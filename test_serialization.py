
import datatypes.trace as tr
import serialize_trace.serializer as ser
import sys

# Make a trace exercising each instruction:

trace = []
trace.append(tr.Trace.Wait())
trace.append(tr.Trace.Flip())
trace.append(tr.Trace.SMove((1, 0, 0)))
trace.append(tr.Trace.SMove((0, 1, 0)))
trace.append(tr.Trace.LMove((-1, 0, 0), (0, -1, 0)))
trace.append(tr.Trace.Fill((0, 0, 1)))
trace.append(tr.Trace.Fission((1, 0, 0), 5))
trace.append(tr.Trace.FusionP((1, 0, 0))) # executed by bot 1
trace.append(tr.Trace.FusionS((-1, 0, 0))) # executed by bot 2
trace.append(tr.Trace.Flip())
trace.append(tr.Trace.Halt())

ser.serialize(trace, sys.stdout)
