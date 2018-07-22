from copy import deepcopy

import numpy


class Voxel_position:
    def __init__(self, x=0, y=0, z=0):
        if isinstance(x, Voxel_position):
            self.x = x.x
            self.y = x.y
            self.z = x.z
        elif isinstance(x, tuple):
            self.x = x[0]
            self.y = x[1]
            self.z = x[2]
        else:
            self.x = x
            self.y = y
            self.z = z

    def add_offset(self, other):
        if isinstance(other, tuple):
            return self.add_offset(Voxel_position(other))
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self


class Bot:
    def __init__(self):
        self.position = Voxel_position()
        self.seeds = 0


class Execution_state:
    def __init__(self, dimension):
        self.dimension = dimension
        self.bots = [Bot()]
        self.current_bot_index = 0
        self.current_model = numpy.zeros((dimension, dimension, dimension), bool)
        self.antigrav = False
        self.volatiles = []

    @property
    def current_bot(self):
        return self.bots[self.current_bot_index]

    def position_in_bounds(self, position):
        return position.x >= 0 and \
               position.y >= 0 and \
               position.z >= 0 and \
               position.x < self.dimension and \
               position.y < self.dimension and \
               position.z < self.dimension

    def contents_of_position(self, position):
        if self.current_model[position.x, position.y, position.z]:
            return "is filled"
        if position in map(lambda bot: bot.position, self.bots):
            return "contains a bot"
        if position in self.volatiles:
            return "is volatile"
        if not self.position_in_bounds(position):
            return "is out of bounds"
        return ""

    def select_next_bot(self):
        self.current_bot_index += 1
        if self.current_bot_index >= len(self.bots):
            self.current_bot_index = 0
            self.volatiles = []

    def add_volatile(self, volatile):
        self.volatiles.append(deepcopy(volatile))