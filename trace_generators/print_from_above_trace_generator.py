
import numpy
import datatypes.trace as tr
import simple_move

class PrintFromAboveTraceBuilder:

    def __init__(self, model):
        self.pos = (0, 0, 0)
        self.trace = tr.Trace()
        self.model = model
        self.region = (len(self.model), len(self.model[0]), len(self.model[0, 0]))

    # No clipping yet, as the bot is always above all filled cells.
    def move_to(self, new_pos):
        needed = self.difference_to(new_pos)
        simple_move.move(needed, self.trace)
        self.pos = new_pos

    def difference_to(self, target):
        return tr.coord_subtract(target, self.pos)

    def make(self):

        self.trace.add(tr.Trace.Flip())

        for y in range(self.region[1]):
            if y % 2 == 1:
                x_range = range(self.region[0] - 1, -1, -1)
            else:
                x_range = range(self.region[0])
            for x in x_range:
                if x % 2 == 1:
                    z_range = range(self.region[2] - 1, -1, -1)
                    z_step = -1
                else:
                    z_range = range(self.region[2])
                    z_step = 1
                for z in z_range:

                    if not self.model[x, y, z]:
                        continue

                    to_target = self.difference_to((x, y, z))

                    if not tr.is_near_difference(to_target):

                        self.move_to((x, y + 1, z))
                        to_target = self.difference_to((x, y, z))

                    self.trace.add(tr.Trace.Fill(to_target))

        self.move_to((0, 0, 0))

        self.trace.add(tr.Trace.Flip())
        self.trace.add(tr.Trace.Halt())

def build_simple_trace(model):

    builder = PrintFromAboveTraceBuilder(model)
    builder.make()
    return builder.trace
