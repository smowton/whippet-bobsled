import model_reader.model_reader as model_reader

grid = model_reader.read('./data/problems/LA001_tgt.mdl')

model_reader.dump_slices(grid)
