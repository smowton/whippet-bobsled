import model_reader.model_reader as model_reader
import model_reader.model_functions as model_functions
import numpy

grid = model_reader.read('./data/problems/LA001_tgt.mdl')

resolution = grid.shape[0]
minus_grid = numpy.zeros((resolution, resolution, resolution), bool)
minus_grid[12, 0, 8] = True
minus_grid[12, 0, 12] = True
minus_grid[12, 1, 12] = True

print ("Goal grid")
model_reader.dump_slice(grid[:, 1, :])

print ("Minus grid")
model_reader.dump_slice(minus_grid[:, 1, :])

print("grid_diff result")
grid_diff_result = model_functions.grid_diff(grid, minus_grid)
model_reader.dump_slice(grid_diff_result[:, 1, :])

fillable_grid = model_functions.fillable(grid, minus_grid)

print( "Goal ground" )
model_reader.dump_slice(grid[:, 0, :])
print( "Filled ground" )
model_reader.dump_slice(minus_grid[:, 0, :])
print( "Fillable ground" )
model_reader.dump_slice(fillable_grid[:, 0, :])

print( "Goal level 1" )
model_reader.dump_slice(grid[:, 1, :])
print( "Filled level 1" )
model_reader.dump_slice(minus_grid[:, 1, :])
print( "Fillable level 1" )
model_reader.dump_slice(fillable_grid[:, 1, :])

print( "Goal level 2" )
model_reader.dump_slice(grid[:, 2, :])
print( "Filled level 2" )
model_reader.dump_slice(minus_grid[:, 2, :])
print( "Fillable level 2" )
model_reader.dump_slice(fillable_grid[:, 2, :])

print( "Goal level 3" )
model_reader.dump_slice(grid[:, 3, :])
print( "Filled level 3" )
model_reader.dump_slice(minus_grid[:, 3, :])
print( "Fillable level 3" )
model_reader.dump_slice(fillable_grid[:, 3, :])

