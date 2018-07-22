
import numpy
import datatypes.trace as tr
import simple_move

class PrintFromAboveTraceBuilder:

    def __init__(self, model, make_complete_trace = True, lockstep = False):
        self.pos = (0, 0, 0)
        self.trace = tr.Trace()
        self.model = model
        self.region_size = (len(self.model), len(self.model[0]), len(self.model[0, 0]))
        self.make_complete_trace = make_complete_trace
        self.lockstep = lockstep

    # No clipping yet, as the bot is always above all filled cells.
    def move_to(self, new_pos):
        needed = self.difference_to(new_pos)
        simple_move.move(needed, self.trace)
        self.pos = new_pos

    def difference_to(self, target):
        return tr.coord_subtract(target, self.pos)

    def make(self):

        if self.make_complete_trace:
            self.trace.add(tr.Trace.Flip())

        for y in range(self.region_size[1]):
            if y % 2 == 1:
                x_range = range(self.region_size[0] - 1, -1, -1)
            else:
                x_range = range(self.region_size[0])
            for x in x_range:
                if x % 2 == 1:
                    z_range = range(self.region_size[2] - 1, -1, -1)
                else:
                    z_range = range(self.region_size[2])
                for z in z_range:

                    if not self.model[x, y, z]:
                        continue

                    to_target = self.difference_to((x, y, z))

                    # Never draw material on the same level as this bot, as that
                    # introduces a collision hazard.
                    if self.pos[1] != y + 1 or not tr.is_near_difference(to_target):
                        self.move_to((x, y + 1, z))
                        to_target = self.difference_to((x, y, z))

                    self.trace.add(tr.Trace.Fill(to_target, (x, y, z)))

            if self.lockstep:
                self.trace.add(tr.Trace.Barrier())

        if self.make_complete_trace:
            self.move_to((0, 0, 0))
            self.trace.add(tr.Trace.Flip())
            self.trace.add(tr.Trace.Halt())

def build_simple_trace(model):

    builder = PrintFromAboveTraceBuilder(model)
    builder.make()
    return builder.trace
