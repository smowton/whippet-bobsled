import sys
import numpy

def slice_is_empty(slice):
    resolution = slice.shape[0]
    for x in range(0, resolution):
        for y in range(0, resolution):
            if slice[x, y]:
                return False
    return True

