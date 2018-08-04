import bot_locomotion.pathfinding as pathfinding
import model_reader.model_reader as model_reader
import model_reader.model_functions as model_functions
import datatypes.trace as trace

grid = model_reader.read('./data/problems/LA100_tgt.mdl')
bounds = model_functions.outer_bounds(grid)

start = (30, 27, 50)
goal = (35, 15, 30)
# goal = (31, 27, 50)
is_occupied = lambda position: grid[position[0], position[1], position[2]]
print is_occupied(start), is_occupied(goal)

path = pathfinding.bounded_search(start, goal, grid.shape, is_occupied)

if path:
    edges = [start]
    position = start
    for line in path:
        position = trace.coord_add(position, line)
        edges.append(position)

    edges.append(goal)

    # model_reader.dump_slices(grid, edges, bounds[1][1])
    print path
