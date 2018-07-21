import bot_locomotion.pathfinding as pathfinding
import model_reader.model_reader as model_reader

grid = model_reader.read('./data/problems/LA001_tgt.mdl')

start = [0, 0, 0]
goal = [7, 4, 19]
path = pathfinding.search(start, goal, grid)
model_reader.dump_slices(grid, path)

lines = pathfinding.path_lines(path)
commands = pathfinding.path_commands(lines)
print "Lines (distance and direction):"
print lines
print "Commands (type, distance and direction):"
print commands
