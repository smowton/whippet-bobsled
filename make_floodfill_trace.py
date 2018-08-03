from __future__ import print_function

import sys
import os.path

import model_reader.model_reader as model_reader
import trace_generators.layer_floodfill_generator as layer_floodfill_generator
import serialize_trace.serializer as serializer

if len(sys.argv) < 3:
    print("Usage: make_floodfill_trace.py some.mdl some.nbt [-f]", file = sys.stderr)
    sys.exit(1)

if (len(sys.argv) >= 4 and sys.argv[3] != '-f') and os.path.exists(sys.argv[2]):
    print("%s already exists" % sys.argv[2], file = sys.stderr)
    sys.exit(1)

model = model_reader.read(sys.argv[1])
commands = layer_floodfill_generator.build_trace(model)

with open(sys.argv[2], "w") as output_file:
    serializer.serialize(commands, output_file)
