
# Computes and saves the cost of a given trace (as filename.nbt.cost)

import sys
import os.path
import serialize_trace.deserializer as deser

if len(sys.argv) != 3:
    print >>sys.stderr, "Usage: cost_trace.py trace_file.nbt model_directory"
    sys.exit(1)

with open(sys.argv[1], "r") as f:
    trace = deser.read_trace(f)

model_path = os.path.join(sys.argv[2], os.path.basename(sys.argv[1]).replace(".nbt", "_tgt.mdl"))
with open(model_path, "r") as f:
    dimension = ord(f.read(1))

with open(sys.argv[1] + ".cost", "w") as f:
    f.write(str(trace.cost(dimension)))
