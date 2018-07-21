
import numpy
import datatypes.trace as tr

class SimpleTraceBuilder:

    def __init__(self, model):
        self.num_ungrounded_blocks = 0
        self.resolution = len(model)
        self.ungrounded_blocks = numpy.zeros((self.resolution, self.resolution, self.resolution), bool)
        self.pos = (0, 0, 0)
        self.trace = tr.Trace()
        self.model = model

    # No clipping yet, as the bot is always above all filled cells.
    def move_to(self, new_pos):

        needed = self.difference_to(new_pos)
        while needed != (0, 0, 0):
            if sum(map(lambda c: c != 0, needed)) == 2 and \
                 all(tr.is_short_linear_difference((c, 0, 0)) for c in needed):
                # LMove can solve it in one:
                dist1 = None
                dist2 = None
                for (ax, c) in enumerate(needed):
                    if c == 0:
                        continue
                    dist = [0, 0, 0]
                    dist[ax] = c
                    if dist1 is None:
                        dist1 = tuple(dist)
                    else:
                        assert dist2 is None
                        dist2 = tuple(dist)
                self.trace.add(tr.Trace.LMove(dist1, dist2))
                needed = (0, 0, 0)
            else:
                # SMove in direction requiring most travel
                largest_ax = max(enumerate(needed), key = lambda pair : abs(pair[1]))
                mv = [0, 0, 0]
                mv[largest_ax[0]] = max(min(largest_ax[1], 15), -15)
                mv = tuple(mv)
                needed = tr.coord_subtract(needed, mv)
                self.trace.add(tr.Trace.SMove(mv))

        self.pos = new_pos

    def difference_to(self, target):
        return tr.coord_subtract(target, self.pos)

    def make(self):

        self.trace.add(tr.Trace.Flip())

        for y in range(self.resolution):
            if y % 2 == 1:
                x_range = range(self.resolution - 1, -1, -1)
            else:
                x_range = range(self.resolution)
            for x in x_range:
                if x % 2 == 1:
                    z_range = range(self.resolution - 1, -1, -1)
                    z_step = -1
                else:
                    z_range = range(self.resolution)
                    z_step = 1
                for z in z_range:

                    if not self.model[x, y, z]:
                        continue

                    to_target = self.difference_to((x, y, z))

                    if not tr.is_near_difference(to_target):

                        # Get one z-step ahead of the required block
                        # (always allowed due to border) to save on moves
                        self.move_to((x, y + 1, z + z_step))
                        to_target = self.difference_to((x, y, z))

                    self.trace.add(tr.Trace.Fill(to_target))

        self.move_to((0, 0, 0))

        self.trace.add(tr.Trace.Flip())
        self.trace.add(tr.Trace.Halt())

def build_simple_trace(model):

    builder = SimpleTraceBuilder(model)
    builder.make()
    return builder.trace
