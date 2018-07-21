
import datatypes.trace as tr
import serialize_trace.serializer as ser
import sys

# Make a trace exercising each instruction:

trace = tr.Trace()
trace.add(tr.Trace.Wait())
trace.add(tr.Trace.Flip())
trace.add(tr.Trace.SMove((1, 0, 0)))
trace.add(tr.Trace.SMove((0, 1, 0)))
trace.add(tr.Trace.LMove((-1, 0, 0), (0, -1, 0)))
trace.add(tr.Trace.Fill((0, 0, 1)))
trace.add(tr.Trace.Fission((1, 0, 0), 5))
trace.add(tr.Trace.FusionP((1, 0, 0))) # executed by bot 1
trace.add(tr.Trace.FusionS((-1, 0, 0))) # executed by bot 2
trace.add(tr.Trace.Flip())
trace.add(tr.Trace.Halt())

print >>sys.stderr, "Energy cost:", trace.cost(20) # Assume a 20*20*20 universe

ser.serialize(trace, sys.stdout)
