
import datatypes.trace as tr
import numpy

class GroundTracker:

    def __init__(self, resolution):
        self.resolution = resolution
        self.ungrounded_blocks = numpy.zeros((self.resolution, self.resolution, self.resolution), bool)
        self.num_ungrounded_blocks = 0
        self.partial_model = numpy.zeros((self.resolution, self.resolution, self.resolution), bool)

    def fill_block_at(self, coord):

        # Check if the new block will be ungrounded:
        new_block_grounded = self.coord_is_grounded(coord)
        self.partial_model[coord] = True

        # Register the new block:
        self.ungrounded_blocks[coord] = not new_block_grounded
        if not new_block_grounded:
            self.num_ungrounded_blocks += 1
        elif self.num_ungrounded_blocks != 0:
            # Check if the new block grounds anything:
            self.flood_grounded_from(coord)

    def coord_is_grounded(self, coord):

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

    def model_is_grounded(self):
        return self.num_ungrounded_blocks == 0

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

def add_flips(trace, resolution):

    result = tr.Trace()
    grounded_tracker = GroundTracker(resolution)

    trace_idx = 0
    active_bots = 1

    while trace_idx < len(trace.instructions):

        frame_size = active_bots
        grounded_before_frame = grounded_tracker.model_is_grounded()

        # Play the next frame to the tracker, and update the active bot count:
        for i in range(trace_idx, trace_idx + frame_size):
            instruction = trace.instructions[i]
            if isinstance(instruction, tr.Trace.Fission):
                active_bots += 1
            elif isinstance(instruction, tr.Trace.FusionP):
                active_bots -= 1
            elif isinstance(instruction, tr.Trace.Fill):
                if instruction.absolute_coord is None:
                    raise Exception("Must annotate fills with absolute coords first")
                grounded_tracker.fill_block_at(instruction.absolute_coord)

        grounded_after_frame = grounded_tracker.model_is_grounded()

        # Enable AG if necessary:
        if grounded_before_frame and not grounded_after_frame:

            result.instructions.append(tr.Trace.Flip())
            ag_enabled = True
            for i in range(frame_size - 1):
                result.instructions.append(tr.Trace.Wait())

        # Copy the frame
        result.instructions.extend(trace.instructions[trace_idx : trace_idx + frame_size])

        # Disable AG if possible:
        if grounded_after_frame and not grounded_before_frame:

            result.instructions.append(tr.Trace.Flip())
            # Note this is a subsequent frame, so the new bot count applies.
            for i in range(active_bots - 1):
                result.instructions.append(tr.Trace.Wait())

        trace_idx += frame_size

    return result
