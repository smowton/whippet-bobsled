import bot_locomotion.pathfinding as pathfinding
import model_reader.model_reader as model_reader
import model_reader.model_functions as model_functions
import datatypes.trace as trace

grid = model_reader.read('./data/problems/LA001_tgt.mdl')
bounds = model_functions.outer_bounds(grid)

start = (8, 1, 2)
goal = (12, 4, 18)
path = pathfinding.move(start, goal, grid, bounds)

edges = [start]
position = start
for line in path:
    position = trace.coord_add(position,  trace.coord_scalar_multiply(line[1], line[0]))
    edges.append(position)

edges.append(goal)

model_reader.dump_slices(grid, edges)

print path
