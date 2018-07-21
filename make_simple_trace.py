
from __future__ import print_function

import sys
import os.path

import model_reader.model_reader as mdl
import trace_generators.simple_trace_generator as gen
import serialize_trace.serializer as ser

if len(sys.argv) < 3:
    print("Usage: make_simple_trace.py some.mdl some.nbt [-f]", file = sys.stderr)
    sys.exit(1)

if sys.argv[3] != '-f' and os.path.exists(sys.argv[2]):
    print("%s already exists" % sys.argv[2], file = sys.stderr)
    sys.exit(1)

model = mdl.read(sys.argv[1])
trace = gen.build_simple_trace(model)

with open(sys.argv[2], "w") as f:
    ser.serialize(trace, f)
