import sys
import numpy

def slice_is_empty(slice):
    resolution = slice.shape[0]
    for x in range(0, resolution):
        for y in range(0, resolution):
            if slice[x, y]:
                return False
    return True

def rindex(list, item):
    size = len(list)
    list.reverse()
    return size - list.index(item) - 1

def bounds(grid):
    resolution = grid.shape[0]
    x_slices_populated = map(lambda i: slice_is_empty(grid[i, :, :]), range(0, resolution))
    y_slices_populated = map(lambda i: slice_is_empty(grid[:, i, :]), range(0, resolution))
    z_slices_populated = map(lambda i: slice_is_empty(grid[:, :, i]), range(0, resolution))
    lower = (x_slices_populated.index(False), y_slices_populated.index(False), z_slices_populated.index(False))
    upper = (rindex(x_slices_populated, False), rindex(y_slices_populated, False), rindex(z_slices_populated, False))
    return (lower, upper)


def grid_diff(grid_a, grid_b):
    resolution = grid_a.shape[0]
    output_grid = numpy.empty((resolution, resolution, resolution), bool)
    for y in range(resolution):
        for z in range(resolution):
            for x in range(resolution):
                output_grid[x, y, z] = grid_a[x, y, z] and not grid_b[x, y, z]
    return output_grid

# Works out which voxels are fillable without anti-gravity.
def fillable(goal_grid, current_grid):
    unfilled_voxels = grid_diff(goal_grid, current_grid)
    resolution = goal_grid.shape[0]
    fillable_voxels = numpy.zeros((resolution, resolution, resolution), bool)
    for y in range(resolution):
        for z in range(resolution):
            for x in range(resolution):
                if unfilled_voxels[x, y, z]:
                    # Ground level is always fill able
                    if y == 0:
                        fillable_voxels[x, y, z] = True
                    # Voxel is fill able if voxel below is filled.
                    elif current_grid[x, y - 1, z]:
                        fillable_voxels[x, y, z] = True
                    # Voxel is fill able if voxel west is filled.
                    elif x>0 and current_grid[x - 1, y, z]:
                        fillable_voxels[x, y, z] = True
                    # Voxel is fill able if voxel east is filled.
                    elif x<resolution-1 and current_grid[x + 1, y, z]:
                        fillable_voxels[x, y, z] = True
                    # Voxel is fill able if voxel north is filled.
                    elif z>0 and current_grid[x, y, z - 1]:
                        fillable_voxels[x, y, z] = True
                    # Voxel is fill able if voxel south is filled.
                    elif z<resolution-1 and current_grid[x, y, z + 1]:
                        fillable_voxels[x, y, z] = True
    return fillable_voxels
