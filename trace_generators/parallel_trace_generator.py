
# runs a (fixed) 6x6 grid of bots that each individually build a column of material.
# Currently the sub-planners will make choices about anti-grav-- for now we ignore their
# choices and just run with gravity switched off (TODO-- post-hoc analysis for this).

import simple_move as move
import print_from_above_trace_generator as pfa
import datatypes.trace as tr

class Bot:
    def __init__(self, split_ops_queue, region_origin, region_size, pos, seeds, bots):
        self.trace = tr.Trace()
        self.split_ops_queue = split_ops_queue
        self.region_origin = region_origin
        self.region_size = region_size
        self.pos = pos # Relative to region_origin
        self.seeds = seeds
        self.bots = bots # back-pointer to the all-bots list

    def make_init_trace(self):
        while len(self.split_ops_queue) > 0:

            split = self.split_ops_queue[0]

            # Split in x or z direction?
            if split[0] == "x":
                split_ax = 0
            else:
                split_ax = 2

            # 1:1 or 2:1 ratio?
            if split.endswith("/2"):
                split_point = self.region_size[split_ax] / 2
            else:
                split_point = (2 * self.region_size[split_ax]) / 3

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

            new_bot_region_size = list(self.region_size)
            own_altered_region_size = list(self.region_size)
            new_bot_region_origin = list(self.region_origin)
            own_altered_region_origin = list(self.region_origin)

            if split_sign == 1:
                new_bot_region_size[split_ax] -= split_point
                own_altered_region_size[split_ax] = split_point
                new_bot_region_origin[split_ax] += split_point
            else:
                new_bot_region_size[split_ax] = split_point
                own_altered_region_size[split_ax] -= split_point
                own_altered_region_origin[split_ax] += split_point

            self.region_size = tuple(own_altered_region_size)
            self.region_origin = tuple(own_altered_region_origin)

            new_bot_pos = list(tr.coord_add(self.pos, fission_place))
            # Make the bots' positions own-region-relative:
            if split_sign == 1:
                new_bot_pos[split_ax] -= split_point
            else:
                self.pos[split_ax] -= split_point
            new_bot_seeds = self.seeds[1:(give_seeds + 1)]
            self.seeds = self.seeds[(give_seeds + 1):]

            self.bots[new_bot_id] = \
                Bot(new_bot_split_ops, tuple(new_bot_region_origin), tuple(new_bot_region_size), tuple(new_bot_pos), new_bot_seeds, self.bots)
            self.bots[new_bot_id].make_init_trace()

            self.split_ops_queue = self.split_ops_queue[1:]

        # Finally for simplicity move to the origin of my region:
        move.move(tr.coord_subtract((0, 0, 0), self.pos), self.trace)

def build_parallel_trace(model):

    res = len(model)

    # Make the prelude: repeatedly fission until we have 6x6 bots each in their own region.
    toplevel_split_ops = ["x/2", "z/2", "x2:1", "z2:1", "x/2", "z/2"]

    bots = [None for i in range(40)]
    bots[0] = Bot(toplevel_split_ops, (0, 0, 0), (res, res, res), (0, 0, 0), range(1, 40), bots)
    bots[0].trace.add(tr.Trace.Flip())
    bots[0].make_init_trace()

    bots_by_origin = {b.region_origin: idx for (idx, b) in enumerate(bots) if b is not None}
    bots_by_xlim = {(b.region_origin[0] + b.region_size[0], b.region_origin[1], b.region_origin[2]): idx for (idx, b) in enumerate(bots) if b is not None}
    bots_by_zlim = {(b.region_origin[0], b.region_origin[1], b.region_origin[2] + b.region_size[2]): idx for (idx, b) in enumerate(bots) if b is not None}

    # Have each bot do a simple print-from-above routine:
    for bot in bots:
        if bot is None:
            continue
        submodel = model[bot.region_origin[0] : bot.region_origin[0] + bot.region_size[0], \
                         0 : res, \
                         bot.region_origin[2] : bot.region_origin[2] + bot.region_size[2]]

        # Add build instructions for this region:
        simple_trace_gen = pfa.PrintFromAboveTraceBuilder(submodel, False)
        simple_trace_gen.make()

        # After the usual build process, go to the ceiling:
        simple_trace_gen.move_to((simple_trace_gen.pos[0], res - 1, simple_trace_gen.pos[2]))

        # If this isn't the rightmost bot, go to the edge to pick up the right-hand bot:
        if bot.region_origin[0] + bot.region_size[0] != res:
            simple_trace_gen.move_to((bot.region_size[0] - 1, res - 1, 0))
            target_bot = bots_by_origin[(bot.region_origin[0] + bot.region_size[0], 0, bot.region_origin[2])]
            # This instruction will be properly synchronised later.
            simple_trace_gen.trace.instructions.append(tr.Trace.FusionP((1, 0, 0), target_bot))

        # If this isn't the leftmost bot, go to the back-right corner to get picked up:
        if bot.region_origin[0] != 0:
            simple_trace_gen.move_to((0, res - 1, 0))
            target_bot = bots_by_xlim[bot.region_origin]

            simple_trace_gen.trace.instructions.append(tr.Trace.FusionS((-1, 0, 0), target_bot))

        # If this isn't the backmost bot, go to the edge to pick up the bot behind:
        if bot.region_origin[2] + bot.region_size[2] != res:
            simple_trace_gen.move_to((0, res - 1, bot.region_size[2] - 1))
            target_bot = bots_by_origin[(bot.region_origin[0], 0, bot.region_origin[2] + bot.region_size[2])]
            # This instruction will be properly synchronised later.
            simple_trace_gen.trace.instructions.append(tr.Trace.FusionP((0, 0, 1), target_bot))

        # If this isn't the frontmost bot, go to the front corner to get picked up:
        if bot.region_origin[2] != 0:
            simple_trace_gen.move_to((0, res - 1, 0))
            target_bot = bots_by_zlim[bot.region_origin]

            simple_trace_gen.trace.instructions.append(tr.Trace.FusionS((0, 0, -1), target_bot))

        # The last surviving bot should finally go to the origin:
        if bot.region_origin == (0, 0, 0):
            simple_trace_gen.move_to((0, res - 1, 0))
            simple_trace_gen.move_to((0, 0, 0))

        bot.trace.instructions.extend(simple_trace_gen.trace.instructions)

    # Final shutdown by whichever bot ended up running the origin region:
    bots[bots_by_origin[(0,0,0)]].trace.add(tr.Trace.Flip())
    bots[bots_by_origin[(0,0,0)]].trace.add(tr.Trace.Halt())

    class TraceWalker:
        def __init__(self, idx, bot):
            self.idx = idx
            self.trace = bot.trace
            self.active = False
            self.done = False
            self.trace_index = 0

        def is_stalled(self):
            if self.done:
                return True
            instruction = self.trace.instructions[self.trace_index]
            if isinstance(instruction, tr.Trace.FusionP) or isinstance(instruction, tr.Trace.FusionS):
                target_bot_walker = walkers[instruction.target_bot]
                if not target_bot_walker.active:
                    return True
                if target_bot_walker.done:
                    raise Exception("Waiting for a stopped bot")

                target_bot_instruction = target_bot_walker.trace.instructions[target_bot_walker.trace_index]
                needed_instruction = tr.Trace.FusionS if isinstance(instruction, tr.Trace.FusionP) else tr.Trace.FusionP
                if not isinstance(target_bot_instruction, needed_instruction):
                    return True
                if target_bot_instruction.target_bot != self.idx:
                    return True
            return False

        def activate(self):
            assert not self.active
            self.active = True

        def deactivate(self):
            assert self.active
            self.active = False

        def get_next_instruction(self):
            inst = self.trace.instructions[self.trace_index]
            self.trace_index += 1
            if self.trace_index == len(self.trace.instructions):
                self.done = True
            return inst

    walkers = [TraceWalker(idx, bot) if bot is not None else None for (idx, bot) in enumerate(bots)]
    walkers[0].active = True

    interleaved_trace = tr.Trace()

    while any(walker is not None and walker.active and not walker.done for walker in walkers):

        newly_active = []
        newly_inactive = []

        # Must check this before anyone's program counter moves, otherwise
        # pairing group instructions is tricky
        stalled_walkers = [walker.is_stalled() if walker is not None else False for walker in walkers]

        for (stalled, walker) in zip(stalled_walkers, walkers):
            if walker is not None and walker.active:
                if stalled:
                    instruction = tr.Trace.Wait()
                else:
                    instruction = walker.get_next_instruction()
                interleaved_trace.add(instruction)
                if isinstance(instruction, tr.Trace.Fission):
                    newly_active.append(instruction.new_bot_id)
                elif isinstance(instruction, tr.Trace.FusionS):
                    newly_inactive.append(walker.idx)

        for new_bot in newly_active:
            walkers[new_bot].activate()
        for dead_bot in newly_inactive:
            walkers[dead_bot].deactivate()

    return interleaved_trace
