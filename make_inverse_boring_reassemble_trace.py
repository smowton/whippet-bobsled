
from __future__ import print_function

import sys
import os.path

import model_reader.model_reader as mdl
import trace_generators.inverse_boring_dissassemble_trace_generator as dis_gen
import trace_generators.inverse_boring_trace_generator as ass_gen
import serialize_trace.serializer as ser

if len(sys.argv) < 4:
    print("Usage: make_inverse_boring_reassemble_trace.py source.mdl target.mdl some.nbt [-f]", file = sys.stderr)
    sys.exit(1)

if (len(sys.argv) >= 5 and sys.argv[4] != '-f') and os.path.exists(sys.argv[3]):
    print("%s already exists" % sys.argv[3], file = sys.stderr)
    sys.exit(1)

source_model = mdl.read(sys.argv[1])
target_model = mdl.read(sys.argv[2])

disassemble_trace = dis_gen.build_inverse_dissassemble_boring_trace(source_model)
assemble_trace = ass_gen.build_inverse_boring_trace(target_model)

disassemble_trace.instructions.pop() # Remove halt

with open(sys.argv[3], "w") as f:
    ser.serialize(disassemble_trace, f)
    ser.serialize(assemble_trace, f)
