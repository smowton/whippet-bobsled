import sys

import model_reader.model_reader as model_reader
import model_reader.model_functions as model_functions
import trace_generators.layer_floodfill_generator as layer_floodfill_generator
import serialize_trace.serializer as serializer
import bot_locomotion.pathfinding as pathfinding

model = model_reader.read('./data/problems/FA047_tgt.mdl')

commands = layer_floodfill_generator.build_trace(model)

with open(sys.argv[1], "w") as f:
    serializer.serialize(commands, f)
