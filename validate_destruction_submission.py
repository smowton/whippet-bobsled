import os
import sys

import serialize_trace.deserializer as deserializer
from model_reader import model_reader

if len(sys.argv) != 2:
    print("Usage: validate_destruction_submission.py submission_directory", sys.stderr)
    sys.exit(1)

input_directory = sys.argv[1]

if not os.path.isdir(input_directory):
    print("Input directory \"" + input_directory + "\" does not exist.")
    sys.exit(1)

trace_list = os.listdir(input_directory)
trace_list.sort()
print("Submission contains " + str(len(trace_list)) + " files.")

for trace_name in trace_list:
    trace_path = os.path.join(input_directory, trace_name)
    model_path = "./data/problems/" + os.path.splitext(trace_name)[0] + "_src.mdl"
    print("Validating trace \"" + trace_path + "\", against model \"" + model_path + "\".")
    source_model = model_reader.read(model_path)
    trace = deserializer.read_trace(open(trace_path, "rb"))
    (state, result) = trace.validate(None, source_model)
    if result:
        print("Valid")
    else:
        print("Invalid")

