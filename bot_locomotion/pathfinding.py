import numpy as np
import datatypes.trace as trace

directions = [[-1, 0, 0],
             [ 0,-1, 0],
             [ 1, 0, 0],
             [ 0, 1, 0],
             [ 0, 0,-1],
             [ 0, 0, 1]]
cost = 1

def move_direction(x, y, z, direction, multiplier = 1):
    x = x + directions[direction][0] * multiplier
    y = y + directions[direction][1] * multiplier
    z = z + directions[direction][2] * multiplier
    return x, y, z

def move(start, goal, grid, bounds = None):
    if start == goal:
        return []

    path = quick_search(start, goal, grid)
    if (path):
        return path

    if not bounds:
        bounds = ((0,0,0), (grid.shape[0] - 1, grid.shape[1] - 1, grid.shape[2] - 1))

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
        path_start = quick_search(start, bounded_start, grid)

    path_end = []
    if goal != bounded_goal:
        path_end = quick_search(bounded_goal, goal, grid)

    search_path = search(bounded_start, bounded_goal, grid, bounds)

    if not search_path:
        return None

    return path_start + search_path + path_end


# All possible orders of the 3 axes of direction
orders = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]

def quick_search(start, goal, grid):
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
        for line in lines:
            direction = trace.direction_vector(line)
            for i in range(trace.l1norm(line)):
                position = trace.coord_add(position, direction)
                if grid[position[0], position[1], position[2]]:
                    failed = True
                    break
            if failed:
                break
        if not failed:
            return [line for line in lines if trace.l1norm(line) > 0]
    return None

def search(start, goal, grid, bounds):
    if start == goal:
        return []

    heuristic = calc_heuristic(grid, goal)

    start = trace.coord_subtract(start, bounds[0])
    goal = trace.coord_subtract(goal, bounds[0])

    xdim=bounds[1][0] - bounds[0][0] + 1
    ydim=bounds[1][1] - bounds[0][1] + 1
    zdim=bounds[1][2] - bounds[0][2] + 1

    x = start[0]
    y = start[1]
    z = start[2]

    closed = np.empty((xdim,ydim,zdim), dtype=np.int8)
    closed[:] = 0
    closed[x,y,z] = 1

    expand = np.empty((xdim,ydim,zdim), dtype=np.int8)
    expand[:] = -1
    action = np.empty((xdim,ydim,zdim), dtype=np.int8)
    action[:] = -1

    g = 0
    h = heuristic[x,y,z]
    f = g+h

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
                        if closed[x2,y2,z2] == 0 and not grid[x2 + bounds[0][0], y2 + bounds[0][1], z2 + bounds[0][2]]:

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

def calc_heuristic(grid, goal):
    xdim=grid.shape[0]
    ydim=grid.shape[1]
    zdim=grid.shape[2]

    heuristic = np.empty((xdim,ydim,zdim), dtype=np.float32)
    heuristic[:] = 0.0

    for z in range(zdim):
        for y in range(ydim):
            for x in range(xdim):
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

def path_to_commands(lines):
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
            commands.append(trace.Trace.LMove(lmove1, lmove2))
            index += 2
            moved = 0
        # The next line is within a long distance
        elif distance <= 15:
            commands.append(trace.Trace.SMove(trace.coord_scalar_multiply(direction, distance)))
            index += 1
            moved = 0
        # The next line longer than a long distance
        else:
            commands.append(trace.Trace.SMove(trace.coord_scalar_multiply(direction, 15)))
            moved += 15
    return commands
