
import serialize_trace.serializer as ser

def l1norm(coord):
    assert len(coord) == 3
    return sum(map(abs, coord))

def chess_dist(coord):
    return max(map(abs, coord))

def is_near_difference(coord):
    return l1norm(coord) <= 2 and chess_dist(coord) == 1

def is_linear_difference(coord):
    # At most one coordinate is nonzero:
    return sum(map(lambda c: c != 0, coord)) <= 1

def is_short_linear_difference(coord):
    return is_linear_difference(coord) and l1norm(coord) <= 5

def is_long_linear_difference(coord):
    return is_linear_difference(coord) and l1norm(coord) <= 15

class Trace:

    class Halt:
        def __init__(self):
            pass
        def serialize(self, stream):
            stream.write(chr(0b11111111))

    class Wait:
        def __init__(self):
            pass
        def serialize(self, stream):
            stream.write(chr(0b11111110))

    class Flip:
        def __init__(self):
            pass
        def serialize(self, stream):
            stream.write(chr(0b11111101))

    class SMove:
        def __init__(self, distance):
            self.distance = distance
            assert is_long_linear_difference(distance)
        def serialize(self, stream):
            ax = ser.get_linear_axis(self.distance)
            mag = ser.get_long_linear_biased_magnitude(self.distance)
            stream.write(chr(0b00000100 | (ax << 4)))
            stream.write(chr(mag))

    class LMove:
        def __init__(self, distance1, distance2):
            self.distance1 = distance1
            self.distance2 = distance2
            assert is_short_linear_difference(distance1)
            assert is_short_linear_difference(distance2)
        def serialize(self, stream):
            ax1 = ser.get_linear_axis(self.distance1)
            mag1 = ser.get_short_linear_biased_magnitude(self.distance1)
            ax2 = ser.get_linear_axis(self.distance2)
            mag2 = ser.get_short_linear_biased_magnitude(self.distance2)
            stream.write(chr(0b00001100 | (ax2 << 6) | (ax1 << 4)))
            stream.write(chr((mag2 << 4) | mag1))

    class FusionP:
        def __init__(self, distance):
            self.distance = distance
            assert is_near_difference(distance)
        def serialize(self, stream):
            stream.write(chr(0b00000111 | (ser.get_near_difference_encoding(self.distance) << 3)))

    class FusionS:
        def __init__(self, distance):
            self.distance = distance
            assert is_near_difference(distance)
        def serialize(self, stream):
            stream.write(chr(0b00000110 | (ser.get_near_difference_encoding(self.distance) << 3)))

    class Fission:
        def __init__(self, distance, seeds_kept):
            self.distance = distance
            self.seeds_kept = seeds_kept
            assert is_near_difference(distance)
        def serialize(self, stream):
            stream.write(chr(0b00000101 | (ser.get_near_difference_encoding(self.distance) << 3)))
            stream.write(chr(self.seeds_kept))

    class Fill:
        def __init__(self, distance):
            self.distance = distance
            assert is_near_difference(distance)
        def serialize(self, stream):
            stream.write(chr(0b00000011 | (ser.get_near_difference_encoding(self.distance) << 3)))
