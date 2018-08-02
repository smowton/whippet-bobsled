
import datatypes.trace as tr
import trace_generators.parallel_trace_generator as gen

def build_trace(model, lockstep, sort_tiers):
    trace = gen.build_parallel_trace(model, lockstep, sort_tiers)

    bots = {0: 39}
    active_bots = [0]
    steps = []
    step = []

    for command in trace.instructions:
        fusion_seeds = None

        if isinstance(command, tr.Trace.FusionP):
            fusion_seeds = bots[command.target_bot]
            bots[command.primary_bot] += bots[command.target_bot] + 1
            del bots[command.target_bot]
        elif isinstance(command, tr.Trace.Fission):
            bots[command.new_bot_id] = command.seeds_given
            bots[command.bot_id] -= command.seeds_given + 1

        step.append((command, active_bots[len(step)], fusion_seeds))
        if len(step) == len(active_bots):
            active_bots = bots.keys()
            active_bots.sort()
            steps.append(step)
            step = []

    steps.reverse()

    new_steps = []
    for step in steps:
        new_step = []
        for item in step:
            command = item[0]
            bot_id = item[1]
            if isinstance(command, tr.Trace.Fill):
                new_step.append((bot_id, tr.Trace.Void(command.distance)))
            elif isinstance(command, tr.Trace.Void):
                new_step.append((bot_id, tr.Trace.Fill(command.distance)))
            elif isinstance(command, tr.Trace.Wait):
                new_step.append((bot_id, command))
            elif isinstance(command, tr.Trace.Flip):
                new_step.append((bot_id, command))
            elif isinstance(command, tr.Trace.SMove):
                new_step.append((bot_id, tr.Trace.SMove((-command.distance[0], -command.distance[1], -command.distance[2]))))
            elif isinstance(command, tr.Trace.LMove):
                new_step.append((bot_id, tr.Trace.LMove(
                    (-command.distance2[0], -command.distance2[1], -command.distance2[2]),
                    (-command.distance1[0], -command.distance1[1], -command.distance1[2])
                )))
            elif isinstance(command, tr.Trace.FusionP):
                fission_seeds = item[2]
                new_step.append((bot_id, tr.Trace.Fission(command.distance, fission_seeds, bot_id, command.target_bot)))
            elif isinstance(command, tr.Trace.Fission):
                new_step.append((bot_id, tr.Trace.FusionP(command.distance, bot_id, command.new_bot_id)))
                new_step.append((command.new_bot_id, tr.Trace.FusionS(tr.coord_scalar_multiply(command.distance, -1), bot_id)))

        if len(new_step) > 0:
            new_steps.append(new_step)

    bot_mapping = {}
    bot_mapping[new_steps[0][0][0]] = (0, range(1, 40))
    for step in new_steps:
        for item in step:
            bot_id = item[0]
            command = item[1]
            if isinstance(command, tr.Trace.FusionP):
                bot_mapping[bot_id] = (bot_mapping[bot_id][0], bot_mapping[bot_id][1] + bot_mapping[command.target_bot][1] + [bot_mapping[command.target_bot][0]])
                bot_mapping[bot_id][1].sort()
                bot_mapping[command.target_bot] = (bot_mapping[command.target_bot][0], [])
            elif isinstance(command, tr.Trace.Fission):
                bot_mapping[command.new_bot_id] = (bot_mapping[bot_id][1][0], bot_mapping[bot_id][1][1:command.seeds_given + 1])
                bot_mapping[bot_id] = (bot_mapping[bot_id][0], bot_mapping[bot_id][1][command.seeds_given + 1:])

    sorted_steps = []
    for step in new_steps:
        sorted_step = []
        for item in step:
           new_bot_id = bot_mapping[item[0]][0]
           sorted_step.append((new_bot_id, item[1]))

        sorted_step.sort()
        sorted_steps.append(sorted_step)

    new_instructions = [item[1] for step in sorted_steps for item in step]
    new_instructions.append(tr.Trace.Halt())
    trace.instructions = new_instructions

    return trace
