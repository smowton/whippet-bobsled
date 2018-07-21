import bot_locomotion.pathfinding as pathfinding
import model_reader.model_reader as model_reader

grid = model_reader.read('./data/problems/LA001_tgt.mdl')

start = [4, 0, 4]
goal = [15, 4, 15]
path = pathfinding.search(start, goal, grid)
model_reader.dump_slices(grid, path)
