import numpy as np
import datatypes.trace as trace

add = trace.coord_add
subtract = trace.coord_subtract
scalar_multiply = trace.coord_scalar_multiply

directions = [
    (0, 1, 0),
    (0, -1, 0),
    (1, 0, 0),
    (-1, 0, 0),
    (0, 0, 1),
    (0, 0, -1)
]
step_cost = 1

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
            new_vectors.append(add(vectors[i], vectors[i + 1]))
            i += 2
        else:
            new_vectors.append(vectors[i])
            i += 1
    return new_vectors

def within_bounds(position, bounds):
    if position[0] >= 0 and position[0] < bounds[0]:
        if position[1] >=0 and position[1] < bounds[1]:
            if position[2] >=0 and position[2] < bounds[2]:
                return True
    return False

# All possible orders of the 3 axes of direction
orders = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]

def quick_search(start, goal, is_occupied):
    diff = subtract(goal, start)
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
                position = add(position, direction)
                if is_occupied(position):
                    failed = True
                    break
            if failed:
                break
        if not failed:
            return lines
    return None

def quick_around_search(start, goal, is_occupied):
    diff = subtract(goal, start)
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
                    scalar_multiply(direction, distance),
                    components[order[0]],
                    components[order[1]],
                    components[order[2]],
                    scalar_multiply(direction, -distance)
                ])
                lines = [line for line in lines if trace.l1norm(line) > 0]
                for line in lines:
                    move_direction = trace.direction_vector(line)
                    for i in range(trace.l1norm(line)):
                        position = add(position, move_direction)
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

    offset_start = subtract(bounded_start, bounds[0])
    offset_goal = subtract(bounded_goal, bounds[0])

    bounded_dimensions = add(subtract(bounds[1], bounds[0]), (1, 1, 1))
    is_occupied_offset = lambda location: is_occupied(add(location, bounds[0]))

    search_path = search(offset_start, offset_goal, bounded_dimensions, is_occupied_offset)

    if path_start == None or search_path == None or path_end == None:
        return None

    return path_start + search_path + path_end

def search(start, goal, dimensions, is_occupied):
    if start == goal:
        return []

    closed_set = set(start)
    actions = dict()

    open_set = [(heuristic(start, goal), 0, start, -1)]

    found = False
    while not found:
        if len(open_set) == 0:
            return None
        else:
            open_set.sort(reverse=True)
            total_cost, path_cost, location, prev_direction = open_set.pop()

            if location == goal:
                found = True
            else:
                for direction in directions:
                    new_location = add(location, direction)
                    if within_bounds(new_location, dimensions):
                        if not new_location in closed_set and not is_occupied(new_location):
                            continuation = direction == prev_direction
                            new_path_cost = path_cost + step_cost
                            total_cost = new_path_cost + heuristic(new_location, goal) + (0 if continuation else 1)
                            open_set.append((total_cost, new_path_cost, new_location, direction))
                            closed_set.add(new_location)
                            actions[new_location] = direction

    path=[]
    path.append(goal)
    while location != start:
        location = add(location, scalar_multiply(actions[location], -1))
        path.append(location)

    path.reverse()
    return search_path_lines(path)

def heuristic(position, goal):
    return abs(position[0] - goal[0]) + abs(position[1] - goal[1]) + abs(position[2] - goal[2])

def search_path_lines(path):
    if len(path) < 2:
        return []
    lines = []
    direction = subtract(path[1], path[0])
    lines.append((0, direction))
    index = 1
    while index < len(path):
        new_direction = subtract(path[index], path[index - 1])
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
