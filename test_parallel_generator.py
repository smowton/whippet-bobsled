
from __future__ import print_function

import sys
import numpy

import trace_generators.parallel_trace_generator as gen
import serialize_trace.serializer as ser

model = numpy.zeros((50, 50, 50), bool)
trace = gen.build_parallel_trace(model)

ser.serialize(trace, sys.stdout)
