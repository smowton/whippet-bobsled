
import datatypes.trace

def get_linear_axis(distance)
    assert types.trace.is_linear_difference(distance)
    return [idx for (idx, coord) in enumerate(distance, 1) if coord != 0][0]

def get_short_linear_biased_magnitude(distance):
    assert types.trace.is_short_linear_difference(distance)
    return [d for d in distance if d != 0][0] + 5

def get_long_linear_biased_magnitude(distance):
    assert types.trace.is_long_linear_difference(distance)
    return [d for d in distance if d != 0][0] + 15

def get_near_difference_encoding(distance):
    assert types.trace.is_near_difference(distance)
    return ((d[0] + 1) * 9) + ((d[1] + 1) * 3) + (d[2] + 1)

# Writes bytes to stream, which should be a file-pointer or similar.
def serialize(trace, stream):

    for instruction in trace:
        instruction.serialize(trace)
