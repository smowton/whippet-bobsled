
# runs a (fixed) 6x6 grid of bots that each individually build a column of material.
# Currently the sub-planners will make choices about anti-grav-- for now we ignore their
# choices and just run with gravity switched off (TODO-- post-hoc analysis for this).

import simple_trace_generator as simple
import simple_move as move
import datatypes.trace as tr

class Bot:
    def __init__(self, split_ops_queue, region, pos, seeds, bots):
        self.trace = tr.Trace()
        self.split_ops_queue = split_ops_queue
        self.region = region
        self.pos = pos
        self.seeds = seeds
        self.bots = bots # back-pointer to the all-bots list

    def make_trace(self):
        while len(self.split_ops_queue) > 0:

            split = self.split_ops_queue[0]

            # Split in x or z direction?
            if split[0] == "x":
                split_ax = 0
            else:
                split_ax = 2

            # 1:1 or 2:1 ratio?
            if split.endswith("/2"):
                split_point = self.region[split_ax] / 2
            else:
                split_point = (2 * self.region[split_ax]) / 3

            # Are we above or below the line? This points towards the
            # new bot we'll spawn
            split_sign = -1 if self.pos[split_ax] >= split_point else 1

            if split.endswith("/2"):
                give_seeds = len(self.seeds) / 2
            else:
                if split_sign == -1:
                    give_seeds = (2 * len(self.seeds)) / 3
                else:
                    give_seeds = len(self.seeds) / 3

            # Move towards the split line:
            target_coord = list(self.pos)
            target_coord[split_ax] = split_point
            if split_sign == 1:
                target_coord[split_ax] -= 1
            move.move(tr.coord_subtract(target_coord, self.pos), self.trace)
            self.pos = target_coord

            # Fission across the line:
            new_bot_id = self.seeds[0]
            fission_place = [0,0,0]
            fission_place[split_ax] = split_sign
            self.trace.add(tr.Trace.Fission(tuple(fission_place), give_seeds, new_bot_id))

            # Configure the new bot!
            new_bot_split_ops = self.split_ops_queue[1:]
            # In a 2:1 split, the bot in the 1 part shouldn't do the subsequent /2 split in the
            # same dimension.
            if split.endswith("2:1"):
                skip_op = "x/2" if split == "x2:1" else "z/2"
                if split_sign == 1:
                    new_bot_split_ops = [x for x in new_bot_split_ops if x != skip_op]
                else:
                    self.split_ops_queue = \
                        [self.split_ops_queue[0]] + \
                        [x for x in self.split_ops_queue[1:] if x != skip_op]

            new_bot_region = list(self.region)
            own_altered_region = list(self.region)

            if split_sign == 1:
                new_bot_region[split_ax] -= split_point
                own_altered_region[split_ax] = split_point
            else:
                new_bot_region[split_ax] = split_point
                own_altered_region[split_ax] -= split_point

            self.region = tuple(own_altered_region)

            new_bot_pos = list(tr.coord_add(self.pos, fission_place))
            # Make the bots' positions own-region-relative:
            if split_sign == 1:
                new_bot_pos[split_ax] -= split_point
            else:
                self.pos[split_ax] -= split_point
            new_bot_seeds = self.seeds[1:(give_seeds + 1)]
            self.seeds = self.seeds[(give_seeds + 1):]

            self.bots[new_bot_id] = \
                Bot(new_bot_split_ops, tuple(new_bot_region), tuple(new_bot_pos), new_bot_seeds, self.bots)
            self.bots[new_bot_id].make_trace()

            self.split_ops_queue = self.split_ops_queue[1:]

        # Finally for demonstration purposes move to the origin of my region:
        move.move(tr.coord_subtract((0, 0, 0), self.pos), self.trace)

def build_parallel_trace(model):

    res = len(model)

    # Make the prelude: repeatedly fission until we have 6x6 bots each in their own region.
    toplevel_split_ops = ["x/2", "z/2", "x2:1", "z2:1", "x/2", "z/2"]

    bots = [None for i in range(40)]
    # Note the region is given as a 3-coord, but the y coordinate is irrelevant.
    bots[0] = Bot(toplevel_split_ops, (res, 0, res), (0, 0, 0), range(1, 40), bots)
    bots[0].make_trace()

    interleaved_trace = tr.Trace()
    active_bots = [True] + ([False] * 39)
    idle_bots = [False] * 40
    trace_iterators = [iter(b.trace.instructions) if b is not None else None for b in bots]

    while(any(active and not idle for (active, idle) in zip(active_bots, idle_bots))):

        newly_active = []

        for (idx, (active, trace_iter)) in enumerate(zip(active_bots, trace_iterators)):
            if active:
                try:
                    instruction = trace_iter.next()
                except StopIteration:
                    instruction = tr.Trace.Wait()
                    idle_bots[idx] = True
                interleaved_trace.add(instruction)
                if isinstance(instruction, tr.Trace.Fission):
                    newly_active.append(instruction.new_bot_id)

        for new_bot in newly_active:
            active_bots[new_bot] = True

    return interleaved_trace
