import model_reader.model_reader as model_reader
import model_reader.model_functions as model_functions

grid = model_reader.read('./data/problems/LA001_tgt.mdl')

slice = grid[:, :, 1]
model_reader.dump_slice(slice)
print( model_functions.slice_is_empty(slice) )

slice = grid[:, :, 19]
model_reader.dump_slice(slice)
print( model_functions.slice_is_empty(slice) )

print(model_functions.bounds(grid))
