
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

def coord_subtract(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

def coord_add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])

def coord_scalar_multiply(c, m):
    return (c[0] * m, c[1] * m, c[2] * m)

class Trace:

    class Halt:
        def __init__(self):
            pass
        def serialize(self, stream):
            stream.write(chr(0b11111111))
        def cost(self):
            return 0

    class Wait:
        def __init__(self):
            pass
        def serialize(self, stream):
            stream.write(chr(0b11111110))
        def cost(self):
            return 0

    class Flip:
        def __init__(self):
            pass
        def serialize(self, stream):
            stream.write(chr(0b11111101))
        def cost(self):
            return 0

    class SMove:
        def __init__(self, distance):
            self.distance = distance
            assert is_long_linear_difference(distance)
        def serialize(self, stream):
            ax = ser.get_linear_axis(self.distance)
            mag = ser.get_long_linear_biased_magnitude(self.distance)
            stream.write(chr(0b00000100 | (ax << 4)))
            stream.write(chr(mag))
        def cost(self):
            return 2 * l1norm(self.distance)

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
        def cost(self):
            return (2 * (l1norm(self.distance1) + l1norm(self.distance2) + 2))

    class FusionP:
        def __init__(self, distance):
            self.distance = distance
            assert is_near_difference(distance)
        def serialize(self, stream):
            stream.write(chr(0b00000111 | (ser.get_near_difference_encoding(self.distance) << 3)))
        def cost(self):
            return -24

    class FusionS:
        def __init__(self, distance):
            self.distance = distance
            assert is_near_difference(distance)
        def serialize(self, stream):
            stream.write(chr(0b00000110 | (ser.get_near_difference_encoding(self.distance) << 3)))
        def cost(self):
            return 0 # Always grouped with FusionP, which pays the (negative) cost

    class Fission:
        def __init__(self, distance, seeds_kept):
            self.distance = distance
            self.seeds_kept = seeds_kept
            assert is_near_difference(distance)
        def serialize(self, stream):
            stream.write(chr(0b00000101 | (ser.get_near_difference_encoding(self.distance) << 3)))
            stream.write(chr(self.seeds_kept))
        def cost(self):
            return 24

    class Fill:
        def __init__(self, distance):
            self.distance = distance
            assert is_near_difference(distance)
        def serialize(self, stream):
            stream.write(chr(0b00000011 | (ser.get_near_difference_encoding(self.distance) << 3)))
        def cost(self):
            return 12 # Assumes we currently never fill a filled space

    def __init__(self):
        self.instructions = []

    def add(self, instruction):
        self.instructions.append(instruction)

    def extend(self, instructions):
        self.instructions.extend(instructions)

    def cost(self, model_dimension):
        fixed_cost = (model_dimension ** 3) * 3 # Cost for a time-step with anti-grav off
        total_cost = sum([i.cost() for i in self.instructions])

        antigrav = False
        bots_active = 1
        traceidx = 0

        while traceidx < len(self.instructions):

            total_cost += (20 * bots_active)
            total_cost += ((10 if antigrav else 1) * fixed_cost)
            old_bots_active = bots_active

            for i in range(bots_active):

                step = self.instructions[traceidx + i]

                if isinstance(step, Trace.Flip):
                    antigrav = not antigrav
                elif isinstance(step, Trace.Fission):
                    bots_active += 1
                elif isinstance(step, Trace.FusionP):
                    bots_active -= 1

            traceidx += old_bots_active

        return total_cost
