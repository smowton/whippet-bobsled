
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
        self.partial_model = numpy.zeros((self.resolution, self.resolution, self.resolution), bool)

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

    def is_grounded(self, coord):

        # Grounded if on the ground!
        if coord[1] == 0:
            return True

        # Grounded if any adjacent filled block is grounded:
        for ax in range(3):
            for offset in (1, -1):
                neighbour = list(coord)
                neighbour[ax] += offset
                neighbour = tuple(neighbour)
                if self.partial_model[neighbour] and not self.ungrounded_blocks[neighbour]:
                    return True

        return False

    def flood_grounded_from(self, coord):
        # coord is a newly filled block and is grounded -- mark anything it's in contact
        # with as grounded too.
        worklist = [coord]

        while len(worklist) != 0:
            flood_from = worklist[-1]
            worklist.pop()

            for ax in range(3):
                for offset in (1, -1):
                    neighbour = list(flood_from)
                    neighbour[ax] += offset
                    neighbour = tuple(neighbour)

                    if self.ungrounded_blocks[neighbour]:
                        self.ungrounded_blocks[neighbour] = False
                        self.num_ungrounded_blocks -= 1
                        worklist.append(neighbour)

    def fill_block_at(self, coord):

        # Check if the new block will be ungrounded:
        new_block_grounded = self.is_grounded(coord)

        to_target = self.difference_to(coord)

        # If anti-grav is currently off we must enable it before filling:
        if (not new_block_grounded) and self.num_ungrounded_blocks == 0:
            self.trace.add(tr.Trace.Flip())

        self.trace.add(tr.Trace.Fill(to_target))
        self.partial_model[coord] = True

        # Register the new block:
        self.ungrounded_blocks[coord] = not new_block_grounded
        if not new_block_grounded:
            self.num_ungrounded_blocks += 1
        elif self.num_ungrounded_blocks != 0:
            # Check if the new block grounds anything:
            self.flood_grounded_from(coord)
            if self.num_ungrounded_blocks == 0:
                # Object newly grounded -- switch anti-grav off.
                self.trace.add(tr.Trace.Flip())

    def make(self):

        # Step through 3x3xz cuboids, building everything we can reach as we go.

        for y in range(1, self.resolution, 3):
            if y % 2 == 1:
                x_range = range(self.resolution - 2, -1, -3)
            else:
                x_range = range(2, self.resolution, 3)

            moved_this_tier = False

            for x in x_range:
                if x % 2 == 1:
                    z_range = range(self.resolution - 1, -1, -1)
                    z_step = -1
                else:
                    z_range = range(self.resolution + 1)
                    z_step = 1
                for z in z_range:

                    moved_this_row = False

                    # Consider building blocks in order: the 3 below us, the 2 either side (x)
                    # and one behind (z), then the 3 above us.
                    neighbour_offsets = \
                        [(-1, -1, 0), (0, -1, 0), (1, -1, 0),
                         (-1, 0, 0), (1, 0, 0), (0, 0, -z_step),
                         (-1, 1, 0), (0, 1, 0), (1, 1, 0)]

                    for neighbour_offset in neighbour_offsets:
                        neighbour = tr.coord_add((x, y, z), neighbour_offset)
                        if any(c >= self.resolution or c < 0 for c in neighbour):
                            continue
                        if self.model[neighbour]:
                            if not moved_this_row:
                                if not moved_this_tier:
                                    moved_this_tier = True
                                    # Make sure to move up first, out of range of any material
                                    # we've built below.
                                    self.move_to((self.pos[0], min(self.pos[1] + 3, self.resolution - 1), self.pos[2]))
                                self.move_to((x, y, z))
                                moved_this_row = True
                            self.fill_block_at(neighbour)

        # Move carefully, over any material placed, then to the top corner, then down.
        self.move_to((self.pos[0], self.resolution - 1, self.pos[2]))
        self.move_to((0, self.resolution - 1, 0))
        self.move_to((0, 0, 0))
        self.trace.add(tr.Trace.Halt())

def build_simple_trace(model):

    builder = SimpleTraceBuilder(model)
    builder.make()
    return builder.trace
