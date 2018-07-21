import sys
import numpy

def read(input_file_name):
    print('Reading file "' + input_file_name + '"')
    input_file = open(input_file_name, 'rb')
    try:
        resolution =  ord(input_file.read(1))
        print('Resolution is ' + str(resolution))
        bit_queue = []
        grid = numpy.empty((resolution, resolution, resolution), bool)
        for x in range(0, resolution):
            for y in range(0, resolution):
                for z in range(0, resolution):
                    if len(bit_queue) == 0:
                        byte = ord(input_file.read(1))
                        for i in range(0,8):
                            bit_queue.append((byte >> i) & 1)
                    bit = bit_queue.pop(0)
                    grid[x, y, z] = bit
    finally:
        input_file.close()

    return grid

def dump_grid(grid):
    resolution=grid.shape[0]
    for z in range(0, resolution):
        for y in range(0, resolution):
            for x in range(0, resolution):
                print("x:"+str(x) + " y:"+str(y)+ " z:"+str(z), grid[x,y,z])

def dump_slices(grid, path = set()):
    resolution=grid.shape[0]
    for y in range(5): #range(0, resolution):
        print("slice y="+ str(y))
        for z in range(0, resolution):
            for x in range(0, resolution):
                if (grid[x, y, z]):
                    output_char = 'x'
                elif ((x, y, z) in path):
                    output_char = '#'
                else:
                    output_char = '.'
                sys.stdout.write(output_char)
            sys.stdout.write('\n')
        sys.stdout.flush()

# Example usage `dump_slice(grid[:, :, 1])`
def dump_slice(grid):
    resolution = grid.shape[0]
    for y in range(0, resolution):
        for x in range(0, resolution):
            if grid[x, y]:
                output_char = 'x'
            else:
                output_char = '.'
            sys.stdout.write(output_char)
        sys.stdout.write('\n')
    sys.stdout.flush()

