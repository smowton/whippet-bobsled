
def l1norm(coord):
    assert len(coord) == 3
    return sum(map(abs, coord))

def chess_dist(coord):
    return max(map(abs, coord))

def is_near_difference(coord):
    return l1norm(coord) <= 2 and chess_dist(coord) == 1

def is_linear_difference(coord):
    # At most one coordinate is nonzero:
    return sum(map(lambda c: c == 0, coord) <= 1)

def is_short_linear_difference(coord):
    return is_linear_difference(coord) and l1norm(coord) <= 5

def is_long_linear_difference(coord):
    return is_linear_difference(coord) and l1norm(coord) <= 15

class Trace:

    class Halt:
        def __init__(self):
            pass

    class Wait:
        def __init__(self):
            pass

    class Flip:
        def __init__(self):
            pass

    class SMove:
        def __init__(self, distance):
            self.distance = distance
            assert is_long_linear_difference(distance)

    class LMove:
        def __init__(self, distance1, distance2):
            self.distance1 = distance1
            self.distance2 = distance2
            assert is_short_linear_distance(distance1)
            assert is_short_linear_distance(distance2)

    class FusionP:
        def __init__(self, distance):
            self.distance = distance
            assert is_near_difference(distance)

    class FusionS:
        def __init__(self, distance):
            self.distance = distance
            assert is_near_difference(distance)

    class Fission:
        def __init__(self, distance, seeds_kept):
            self.distance = distance
            self.seeds_kept = seeds_kept
            assert is_near_difference(distance)

    class Fill:
        def __init__(self, distance):
            self.distance = distance
            assert is_near_difference(distance)
