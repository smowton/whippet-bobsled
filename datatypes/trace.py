from copy import deepcopy

import serialize_trace.serializer as ser
import numpy
import datatypes.execution_state as execution_state

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

def direction_vector(v):
    assert is_linear_difference(v)
    return (
        v[0] if v[0] == 0 else (1 if v[0] > 0 else -1),
        v[1] if v[1] == 0 else (1 if v[1] > 0 else -1),
        v[2] if v[2] == 0 else (1 if v[2] > 0 else -1),
    )

class Trace:
    class Instruction:
        def execute(self, state):
            return ""

    class Halt(Instruction):
        def __init__(self):
            pass
        def serialize(self, stream):
            stream.write(chr(0b11111111))
        def cost(self):
            return 0

    class Wait(Instruction):
        def __init__(self):
            pass
        def serialize(self, stream):
            stream.write(chr(0b11111110))
        def cost(self):
            return 0

    class Flip(Instruction):
        def __init__(self):
            pass
        def serialize(self, stream):
            stream.write(chr(0b11111101))
        def cost(self):
            return 0
        def execute(self, state):
            state.antigrav = not state.antigrav
            return ""

    class SMove(Instruction):
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

        def execute(self, state):
            state.add_volatile(state.current_bot.position)
            new_position = deepcopy(state.current_bot.position).add_offset(self.distance)
            existing_contents = state.contents_of_position(new_position)
            if existing_contents != "":
                return "Attempted to move bot to voxel which " + existing_contents
            state.current_bot.position = new_position
            return ""


    class LMove(Instruction):
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

        def execute(self, state):
            state.add_volatile(state.current_bot.position)
            new_position = deepcopy(state.current_bot.position).add_offset(self.distance1)
            new_position = new_position.add_offset(self.distance2)
            existing_contents = state.contents_of_position(new_position)
            if existing_contents != "":
                return "Attempted to move bot to voxel which " + existing_contents
            state.current_bot.position = new_position
            return ""

    class FusionP(Instruction):
        def __init__(self, distance, target_bot):
            self.distance = distance
            self.target_bot = target_bot
            assert is_near_difference(distance)
        def serialize(self, stream):
            stream.write(chr(0b00000111 | (ser.get_near_difference_encoding(self.distance) << 3)))
        def cost(self):
            return -24

    class FusionS(Instruction):
        def __init__(self, distance, target_bot):
            self.distance = distance
            self.target_bot = target_bot
            assert is_near_difference(distance)
        def serialize(self, stream):
            stream.write(chr(0b00000110 | (ser.get_near_difference_encoding(self.distance) << 3)))
        def cost(self):
            return 0 # Always grouped with FusionP, which pays the (negative) cost

    class Fission(Instruction):
        def __init__(self, distance, seeds_given, new_bot_id):
            self.distance = distance
            self.seeds_given = seeds_given
            self.new_bot_id = new_bot_id # Not serialized, just useful to know
            assert is_near_difference(distance)
        def serialize(self, stream):
            stream.write(chr(0b00000101 | (ser.get_near_difference_encoding(self.distance) << 3)))
            stream.write(chr(self.seeds_given))
        def cost(self):
            return 24

    class Fill(Instruction):
        def __init__(self, distance):
            self.distance = distance
            assert is_near_difference(distance)

        def serialize(self, stream):
            stream.write(chr(0b00000011 | (ser.get_near_difference_encoding(self.distance) << 3)))

        def cost(self):
            return 12 # Assumes we currently never fill a filled space

        def execute(self, state):
            bot = state.current_bot
            position_to_fill = deepcopy(bot.position).add_offset(self.distance)
            existing_contents = state.contents_of_position(position_to_fill)
            if existing_contents != "":
                return "Attempted to fill to voxel which " + existing_contents
            state.current_model[position_to_fill.x, position_to_fill.y, position_to_fill.z] = True
            return ""

    def __init__(self):
        self.instructions = []

    def add(self, instruction):
        self.instructions.append(instruction)

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

    def validate(self, target_model):
        # Convert instruction list field to local array for speed.
        instructions = numpy.array(self.instructions)
        dimension = target_model.shape[0]
        state = execution_state.Execution_state(dimension)
        state.current_bot.seeds = 39

        for trace_index in range(len(instructions)):
            execution_error = instructions[trace_index].execute(state)
            if execution_error != "":
                print("Error at instruction " + str(trace_index) + ".")
                print(execution_error)
                return state, False
            state.select_next_bot()

        valid = True
        if len(state.bots) != 1:
            print("Final bot count is not 1.")
            valid = False
        elif state.current_bot.position.x != 0 or state.current_bot.position.y != 0 or state.current_bot.position.z != 0:
            print("Final bot positon is not (0,0,0)")
            valid = False
        if not numpy.array_equal(target_model, state.current_model):
            print("Final model does not match target model")
            valid = False

        return state, valid
