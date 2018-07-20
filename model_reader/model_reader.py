import sys
import numpy

if len(sys.argv) != 2:
    print('Usage - model_reader.py <model file>')
    exit()

input_file_name = sys.argv[1]
print('Reading file "' + input_file_name + '"')
input_file = open(input_file_name, 'rb')
try:
    resolution_bytes = input_file.read(1)
    resolution = int(resolution_bytes[0])
    print('Resolution is ' + str(resolution))
    bit_queue = []
    grid = numpy.empty((resolution, resolution, resolution), bool)
    for z in range(0, resolution):
        for y in range(0, resolution):
            for x in range(0, resolution):
                if len(bit_queue) == 0:
                    byte = int(input_file.read(1)[0])
                    for i in range(0,8):
                        bit_queue.append((byte >> i) & 1)
                bit = bit_queue.pop(0)
                grid[x, y, z] = bit
finally:
    input_file.close()


def dump_grid(grid):
    for z in range(0, resolution):
        for y in range(0, resolution):
            for x in range(0, resolution):
                print("x:"+str(x) + " y:"+str(y)+ " z:"+str(z), grid[x,y,z])


dump_grid(grid)
