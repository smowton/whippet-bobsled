
import numpy
import datatypes.trace as tr
import bot_locomotion.pathfinding as pathfinding

class SimpleTraceBuilder:

    def __init__(self, model):
        self.num_ungrounded_blocks = 0
        self.resolution = len(model)
        self.ungrounded_blocks = numpy.zeros((self.resolution, self.resolution, self.resolution), bool)
        self.pos = (0, 0, 0)
        self.trace = tr.Trace()
        self.model = model
        self.partial_model = numpy.zeros((self.resolution, self.resolution, self.resolution), bool)

    def move_to(self, new_pos):
        path = pathfinding.search(self.pos, new_pos, self.partial_model)
        path_lines = pathfinding.path_lines(path)
        path_commands = pathfinding.path_commands(path_lines)
        self.trace.extend(path_commands)
        self.pos = new_pos

    def move_straight_to(self, new_pos):
        while self.pos != new_pos:
            diff = tr.coord_subtract(new_pos, self.pos)
            diff = map(lambda c: min(c, 15), diff)
            self.trace.add(tr.Trace.SMove(diff))
            self.pos = tr.coord_add(self.pos, diff)

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

            for x in x_range:
                if x % 2 == 1:
                    z_range = range(self.resolution - 1, -1, -1)
                    z_step = -1
                else:
                    z_range = range(self.resolution + 1)
                    z_step = 1
                for z in z_range:

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
                            # Optimisation: moving is straightforward if we're already on the
                            # same x, y coordinate (the bot is just moving forwards along its
                            # current track, which must be clear)
                            if self.pos[0] == x and self.pos[1] == y:
                                self.move_straight_to((x, y, z))
                            else:
                                self.move_to((x, y, z))
                            self.fill_block_at(neighbour)

        self.move_to((0, 0, 0))
        self.trace.add(tr.Trace.Halt())

def build_simple_trace(model):

    builder = SimpleTraceBuilder(model)
    builder.make()
    return builder.trace
