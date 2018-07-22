
import numpy
import datatypes.trace as tr
import simple_move

class SortingPrintFromAboveTraceBuilder:

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

    def compute_tier_order(self, y):
        tier = numpy.zeros((self.region_size[0], self.region_size[2]), int)
        # Initialise the tier with -1 for not-to-be-filled, 9999 for not visited,
        # 1 for underpinned by the layer below.

        worklist = []
        for x in range(self.region_size[0]):
            for z in range(self.region_size[2]):
                if not self.model[x, y, z]:
                    tier[x, z] = -1
                elif y == 0 or self.model[x, y - 1, z]:
                    tier[x, z] = 1
                    worklist.append((x, z))
                else:
                    tier[x, z] = 9999

        def neighbours(x, z):
            return [(x + dx, z + dz) for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1))
                                     if x + dx >= 0 and \
                                     x + dx < self.region_size[0] and \
                                     z + dz >= 0 and \
                                     z + dz < self.region_size[2]]

        while len(worklist) != 0:
            nextlist = []
            for (x, z) in worklist:
                ns = neighbours(x, z)
                for neighbour in neighbours(x, z):
                    if tier[neighbour] == 9999:
                        tier[neighbour] = tier[x, z] + 1
                        nextlist.append(neighbour)
            worklist = nextlist

        return tier

    def make(self):

        if self.make_complete_trace:
            self.trace.add(tr.Trace.Flip())

        for y in range(self.region_size[1]):

            # This fills 0 cells in with their minimum distance from underpinned voxels.
            tier = self.compute_tier_order(y)

            visit_order = [(x, z) for x in range(self.region_size[0]) for z in range(self.region_size[2]) if self.model[x, y, z]]
            visit_order = sorted(visit_order, key = lambda xz: (tier[xz], xz))

            print visit_order

            for (x, z) in visit_order:

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
