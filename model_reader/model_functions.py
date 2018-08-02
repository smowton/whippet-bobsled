import sys
import numpy
import datatypes.trace as trace

add = trace.coord_add

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

def outer_bounds(grid):
    inner_bounds = bounds(grid)
    return (
        (
            max(inner_bounds[0][0] - 1, 0),
            max(inner_bounds[0][1] - 1, 0),
            max(inner_bounds[0][2] - 1, 0)
        ),
        (
            min(inner_bounds[1][0] + 1, grid.shape[0] - 1),
            min(inner_bounds[1][1] + 1, grid.shape[1] - 1),
            min(inner_bounds[1][2] + 1, grid.shape[2] - 1)
        ),
    )

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

lateral_directions = [
    (0, 0, 1),
    (1, 0, 0),
    (0, 0, -1),
    (-1, 0, 0),
]

directions = lateral_directions + [
    (0, 1, 0),
    (0, -1, 0),
]

def layer_to_set(layer, y):
    layer_set = set()
    for x in range(layer.shape[0]):
        for z in range(layer.shape[1]):
            if layer[x, z]:
                layer_set.add((x, y, z))
    return layer_set

def get_next_layer(grid, layer_height, prev_layer, explored):
    layer_data = grid[:, layer_height, :]
    layer = []

    # Get grounded points that are directly on top of existing points
    for point in prev_layer:
        new_point = (point[0], layer_height, point[2])
        if layer_data[new_point[0], new_point[2]] and new_point not in explored:
            layer.append(new_point)
            explored.add(new_point)

    # Progressively add all points that touch grounded points
    for point in layer:
        for direction in lateral_directions:
            adjacent_point = add(point, direction)
            if layer_data[adjacent_point[0], adjacent_point[2]] and adjacent_point not in explored:
                layer.append(adjacent_point)
                explored.add(adjacent_point)

    return set(layer)

def get_floodfill_layers(grid):
    base_layer = layer_to_set(grid[:, 0, :], 0)
    layers = [(base_layer, 0, [])]
    explored = base_layer.copy()
    open_layers = [0]
    new_layer_index = 1

    for layer_index in open_layers:
        layer_height = layers[layer_index][1]

        upper_layer = get_next_layer(grid, layer_height + 1, layers[layer_index][0], explored)
        if len(upper_layer) > 0:
            layers[layer_index][2].append(new_layer_index)
            layers.append((upper_layer, layer_height + 1, []))
            open_layers.append(new_layer_index)
            new_layer_index += 1

        lower_layer = get_next_layer(grid, layer_height - 1, layers[layer_index][0], explored)
        if len(lower_layer) > 0:
            layers[layer_index][2].append(new_layer_index)
            layers.append((lower_layer, layer_height - 1, []))
            open_layers.append(new_layer_index)
            new_layer_index += 1

    return layers
