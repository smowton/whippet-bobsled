import numpy as np
import datatypes.trace as trace

directions = [
    (0, 1, 0),
    (0, -1, 0),
    (1, 0, 0),
    (-1, 0, 0),
    (0, 0, 1),
    (0, 0, -1)
]
cost = 1

def move_direction(x, y, z, direction, multiplier = 1):
    x = x + directions[direction][0] * multiplier
    y = y + directions[direction][1] * multiplier
    z = z + directions[direction][2] * multiplier
    return x, y, z

def simplify_vectors(vectors):
    i = 0
    new_vectors = []
    while i < len(vectors):
        if i < len(vectors) - 1 and trace.direction_vector(vectors[i]) == trace.direction_vector(vectors[i + 1]):
            new_vectors.append(trace.coord_add(vectors[i], vectors[i + 1]))
            i += 2
        else:
            new_vectors.append(vectors[i])
            i += 1
    return new_vectors

def move(start, goal, dimensions, is_occupied, bounds = None):
    if start == goal:
        return []

    path = quick_search(start, goal, is_occupied)
    if (path):
        return path

    if not bounds:
        bounds = ((0,0,0), (dimensions[0] - 1, dimensions[1] - 1, dimensions[2] - 1))

    bounded_start = (
        min(max(start[0], bounds[0][0]), bounds[1][0]),
        min(max(start[1], bounds[0][1]), bounds[1][1]),
        min(max(start[2], bounds[0][2]), bounds[1][2]),
    )

    bounded_goal = (
        min(max(goal[0], bounds[0][0]), bounds[1][0]),
        min(max(goal[1], bounds[0][1]), bounds[1][1]),
        min(max(goal[2], bounds[0][2]), bounds[1][2]),
    )

    path_start = []
    if start != bounded_start:
        path_start = quick_search(start, bounded_start, is_occupied)

    path_end = []
    if goal != bounded_goal:
        path_end = quick_search(bounded_goal, goal, is_occupied)

    search_path = search(bounded_start, bounded_goal, dimensions, is_occupied, bounds)

    if not search_path:
        return None

    return path_start + search_path + path_end


# All possible orders of the 3 axes of direction
orders = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]

def quick_search(start, goal, is_occupied):
    diff = trace.coord_subtract(goal, start)
    components = [
        (diff[0], 0, 0),
        (0, diff[1], 0),
        (0, 0, diff[2])
    ]
    for order in orders:
        failed = False
        position = start
        lines = [components[order[0]], components[order[1]], components[order[2]]]
        lines = [line for line in lines if trace.l1norm(line) > 0]
        for line in lines:
            direction = trace.direction_vector(line)
            for i in range(trace.l1norm(line)):
                position = trace.coord_add(position, direction)
                if is_occupied(position):
                    failed = True
                    break
            if failed:
                break
        if not failed:
            return lines
    return None

def quick_around_search(start, goal, is_occupied):
    diff = trace.coord_subtract(goal, start)
    components = [
        (diff[0], 0, 0),
        (0, diff[1], 0),
        (0, 0, diff[2])
    ]
    for direction in directions:
        for distance in range(10):
            for order in orders:
                position = start
                failed = False

                lines = simplify_vectors([
                    trace.coord_scalar_multiply(direction, distance),
                    components[order[0]],
                    components[order[1]],
                    components[order[2]],
                    trace.coord_scalar_multiply(direction, -distance)
                ])
                lines = [line for line in lines if trace.l1norm(line) > 0]
                for line in lines:
                    move_direction = trace.direction_vector(line)
                    for i in range(trace.l1norm(line)):
                        position = trace.coord_add(position, move_direction)
                        if is_occupied(position):
                            failed = True
                            break
                    if failed:
                        break
                if not failed:
                    return lines
    return None

def bounded_search(start, goal, dimensions, is_occupied, bounds = None):
    if start == goal:
        return []

    if not bounds:
        bounds = ((0,0,0), (dimensions[0] - 1, dimensions[1] - 1, dimensions[2] - 1))

    bounded_start = (
        min(max(start[0], bounds[0][0]), bounds[1][0]),
        min(max(start[1], bounds[0][1]), bounds[1][1]),
        min(max(start[2], bounds[0][2]), bounds[1][2]),
    )

    bounded_goal = (
        min(max(goal[0], bounds[0][0]), bounds[1][0]),
        min(max(goal[1], bounds[0][1]), bounds[1][1]),
        min(max(goal[2], bounds[0][2]), bounds[1][2]),
    )

    path_start = []
    if start != bounded_start:
        path_start = quick_search(start, bounded_start, is_occupied)

    path_end = []
    if goal != bounded_goal:
        path_end = quick_search(bounded_goal, goal, is_occupied)

    search_path = search(bounded_start, bounded_goal, dimensions, is_occupied, bounds)

    if path_start == None or search_path == None or path_end == None:
        return None

    return path_start + search_path + path_end

def search(start, goal, dimensions, is_occupied, bounds):
    if start == goal:
        return []

    heuristic = calc_heuristic(dimensions, goal)

    start = trace.coord_subtract(start, bounds[0])
    goal = trace.coord_subtract(goal, bounds[0])

    xdim = bounds[1][0] - bounds[0][0] + 1
    ydim = bounds[1][1] - bounds[0][1] + 1
    zdim = bounds[1][2] - bounds[0][2] + 1

    x = start[0]
    y = start[1]
    z = start[2]

    closed = np.empty((xdim, ydim, zdim), dtype = np.int8)
    closed[:] = 0
    closed[x, y, z] = 1

    expand = np.empty((xdim, ydim, zdim), dtype = np.int8)
    expand[:] = -1
    action = np.empty((xdim, ydim, zdim), dtype = np.int8)
    action[:] = -1

    g = 0
    h = heuristic[x, y, z]
    f = g + h

    openl = [[f, g, x, y, z]]

    found = False  # flag that is set when search is complete
    resign = False # flag set if we can't find expand
    count = 0

    while not found and not resign and count < 1e6:
        if len(openl) == 0:
            resign = True
            return None
        else:
            openl.sort(reverse=True)
            nextl = openl.pop()

            x = nextl[2]
            y = nextl[3]
            z = nextl[4]
            g = nextl[1]
            f = nextl[0]
            expand[x,y,z] = count
            count += 1

            if x == goal[0] and y == goal[1] and z == goal[2]:
                found = True
            else:
                for i in range(len(directions)):
                    x2, y2, z2 = move_direction(x, y, z, i)

                    if z2 >= 0 and z2 < zdim and y2 >=0 and y2 < ydim and x2 >=0 and x2 < xdim:
                        if closed[x2,y2,z2] == 0 and not is_occupied((x2 + bounds[0][0], y2 + bounds[0][1], z2 + bounds[0][2])):

                            continuation = False
                            for j in range(len(directions)):
                                x3, y3, z3 = move_direction(x2, y2, z2, j)
                                if (x3 >= 0 and x3 < xdim and y3 >= 0 and y3 < ydim and z3 >= 0 and z3 < zdim):
                                    x4, y4, z4 = move_direction(x2, y2, z2, action[x3, y3, z3])
                                    if x2 == x4 and y2 == y4 and z2 == z4:
                                        continuation = True

                            g2 = g + cost
                            f2 = g2 + heuristic[x2,y2,z2] + (0 if continuation else 10)
                            openl.append([f2, g2, x2, y2, z2])
                            closed[x2,y2,z2] = 1
                            action[x2,y2,z2] = i
                    else:
                        pass

    path=[]
    path.append((goal[0], goal[1], goal[2]))

    while x != start[0] or y != start[1] or z != start[2]:
        x, y, z = move_direction(x, y, z, action[x, y, z], -1)
        path.append((x, y, z))

    path.reverse()
    return search_path_lines(path)

def calc_heuristic(dimensions, goal):
    heuristic = np.empty(dimensions, dtype=np.float32)
    heuristic[:] = 0.0

    for z in range(dimensions[2]):
        for y in range(dimensions[1]):
            for x in range(dimensions[0]):
                heuristic[x, y, z] = (x - goal[0]) + (y - goal[1]) + (z - goal[2])
    return heuristic

def search_path_lines(path):
    if len(path) < 2:
        return []
    lines = []
    direction = trace.coord_subtract(path[1], path[0])
    lines.append((0, direction))
    index = 1
    while index < len(path):
        new_direction = trace.coord_subtract(path[index], path[index - 1])
        if direction != new_direction:
            direction = new_direction
            lines.append((1, direction))
        else:
            lines[-1] = (lines[-1][0] + 1, direction)
        index += 1
    return [trace.coord_scalar_multiply(line[1], line[0]) for line in lines]

def path_to_commands(lines, bot_id = None):
    commands = []
    index = 0
    moved = 0
    while index < len(lines):
        direction = trace.direction_vector(lines[index])
        distance = trace.l1norm(lines[index]) - moved
        # Not the last line, and the next two lines are a short distance
        if index < len(lines) - 1 and distance <= 5 and trace.l1norm(lines[index + 1]) <= 5:
            lmove1 = trace.coord_scalar_multiply(direction, distance)
            lmove2 = lines[index + 1]
            commands.append(trace.Trace.LMove(lmove1, lmove2, bot_id))
            index += 2
            moved = 0
        # The next line is within a long distance
        elif distance <= 15:
            commands.append(trace.Trace.SMove(trace.coord_scalar_multiply(direction, distance), bot_id))
            index += 1
            moved = 0
        # The next line longer than a long distance
        else:
            commands.append(trace.Trace.SMove(trace.coord_scalar_multiply(direction, 15), bot_id))
            moved += 15
    return commands
