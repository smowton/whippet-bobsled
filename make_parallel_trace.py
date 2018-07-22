
from __future__ import print_function

import sys
import os.path

import model_reader.model_reader as mdl
import trace_generators.parallel_trace_generator as gen
import serialize_trace.serializer as ser

if len(sys.argv) < 3:
    print("Usage: make_parallel_trace.py some.mdl some.nbt [-f] [--lockstep]", file = sys.stderr)
    sys.exit(1)

lockstep = "--lockstep" in sys.argv
overwrite = "-f" in sys.argv

if os.path.exists(sys.argv[2]) and not overwrite:
    print("%s already exists" % sys.argv[2], file = sys.stderr)
    sys.exit(1)

model = mdl.read(sys.argv[1])
trace = gen.build_parallel_trace(model, lockstep)

with open(sys.argv[2], "w") as f:
    ser.serialize(trace, f)
