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
    tuple = (x_slices_populated.index(False), rindex(x_slices_populated, False),
             y_slices_populated.index(False), rindex(y_slices_populated, False),
             z_slices_populated.index(False), rindex(z_slices_populated, False) )
    return tuple
