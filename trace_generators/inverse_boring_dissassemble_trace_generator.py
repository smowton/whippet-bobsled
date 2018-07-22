
# import numpy
import datatypes.trace as tr
# import simple_move
# import bot_locomotion.pathfinding as pathfinding
# import model_reader.model_functions as model_functions
import trace_generators.inverse_boring_trace_generator as gen

def build_inverse_dissassemble_boring_trace(model):
    trace = gen.build_inverse_boring_trace(model)

    trace.instructions.reverse()
    new_instructions = []
    for command in trace.instructions:
        if isinstance(command, tr.Trace.Fill):
            new_instructions.append(tr.Trace.Void(command.distance))
        elif isinstance(command, tr.Trace.Void):
            new_instructions.append(tr.Trace.Fill(command.distance))
        elif isinstance(command, tr.Trace.Wait):
            new_instructions.append(command)
        elif isinstance(command, tr.Trace.Flip):
            new_instructions.append(command)
        elif isinstance(command, tr.Trace.SMove):
            new_instructions.append(tr.Trace.SMove((-command.distance[0], -command.distance[1], -command.distance[2])))
        elif isinstance(command, tr.Trace.LMove):
            new_instructions.append(tr.Trace.LMove(
                (-command.distance2[0], -command.distance2[1], -command.distance2[2]),
                (-command.distance1[0], -command.distance1[1], -command.distance1[2])
            ))
        elif isinstance(command, tr.Trace.FusionP):
            assert False
        elif isinstance(command, tr.Trace.FusionS):
            assert False
        elif isinstance(command, tr.Trace.Fission):
            assert False

    new_instructions.append(tr.Trace.Halt())
    trace.instructions = new_instructions

    return trace
