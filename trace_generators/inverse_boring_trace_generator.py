
import numpy
import datatypes.trace as tr
import simple_move
import bot_locomotion.pathfinding as pathfinding
import model_reader.model_functions as model_functions

class InverseBoringTraceBuilder:

    def __init__(self, model):
        self.num_ungrounded_blocks = 0
        self.resolution = len(model)
        self.ungrounded_blocks = numpy.zeros((self.resolution, self.resolution, self.resolution), bool)
        self.pos = (0, 0, 0)
        self.trace = tr.Trace()
        self.model = model
        self.bounds = model_functions.outer_bounds(model)
        self.partial_model = numpy.zeros((self.resolution, self.resolution, self.resolution), bool)

    def simple_move_to(self, new_pos):
        needed = self.difference_to(new_pos)
        simple_move.move(needed, self.trace)

        self.pos = new_pos

    def move_to(self, new_pos):
        commands = pathfinding.path_to_commands(pathfinding.move(self.pos, new_pos, self.model, self.bounds))
        for command in commands:
            self.trace.add(command)
        total = (0, 0, 0)
        for cmd in commands:
            if (isinstance(cmd, tr.Trace.SMove)):
                total = tr.coord_add(total, cmd.distance)
            if (isinstance(cmd, tr.Trace.LMove)):
                total = tr.coord_add(total, cmd.distance1)
                total = tr.coord_add(total, cmd.distance2)

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
        last_used_z_step = None

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
                                if (x != self.pos[0] or y != self.pos[1]) and last_used_z_step is not None:
                                    # The bot may still be in a ring of material from a previous
                                    # row -- make sure it moves out of it (i.e. either +1z or -1z
                                    # depending on the direction it was working in) before coming
                                    # across:
                                    # (Not necessary if already in the fringe):
                                    if self.pos[2] != 0 and self.pos[2] != (self.resolution - 1):
                                        self.move_to((self.pos[0], self.pos[1], self.pos[2] + last_used_z_step))
                                    # Do the y move (if any) first, since we might have doubled
                                    # back in the x direction, meaning there could be material
                                    # in the way in the x direction we came from.
                                    self.simple_move_to((self.pos[0], y, self.pos[2]))
                                    self.simple_move_to((x, self.pos[1], self.pos[2]))

                                self.simple_move_to((x, y, z))
                                last_used_z_step = z_step
                                moved_this_row = True
                            self.fill_block_at(neighbour)

        # Move carefully, over any material placed, then to the top corner, then down.
        self.move_to((self.pos[0], self.resolution - 1, self.pos[2]))
        self.move_to((0, self.resolution - 1, 0))
        self.move_to((0, 0, 0))
        self.trace.add(tr.Trace.Halt())

def build_inverse_boring_trace(model):

    builder = InverseBoringTraceBuilder(model)
    builder.make()
    return builder.trace
