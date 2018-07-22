
from __future__ import print_function

import sys
import os.path

import model_reader.model_reader as mdl
import trace_generators.inverse_boring_dissassemble_trace_generator as gen
import serialize_trace.serializer as ser

if len(sys.argv) < 3:
    print("Usage: make_inverse_boring_trace.py some.mdl some.nbt [-f]", file = sys.stderr)
    sys.exit(1)

if (len(sys.argv) >= 4 and sys.argv[3] != '-f') and os.path.exists(sys.argv[2]):
    print("%s already exists" % sys.argv[2], file = sys.stderr)
    sys.exit(1)

model = mdl.read(sys.argv[1])
trace = gen.build_inverse_dissassemble_boring_trace(model)

with open(sys.argv[2], "w") as f:
    ser.serialize(trace, f)
