import bot_locomotion.pathfinding as pathfinding
import model_reader.model_reader as model_reader

grid = model_reader.read('./data/problems/LA001_tgt.mdl')

start = [0, 0, 0]
goal = [19, 4, 19]
path = pathfinding.search(start, goal, grid)
model_reader.dump_slices(grid, path)
