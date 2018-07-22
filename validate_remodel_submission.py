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
    model_path1 = "./data/problems/" + os.path.splitext(trace_name)[0] + "_src.mdl"
    model_path2 = "./data/problems/" + os.path.splitext(trace_name)[0] + "_tgt.mdl"
    print("Validating trace \"" + trace_path + "\", against model \"" + model_path1 + "\" and model \"" + model_path2 + "\".")
    source_model = model_reader.read(model_path1)
    target_model = model_reader.read(model_path2)
    trace = deserializer.read_trace(open(trace_path, "rb"))
    (state, result) = trace.validate(target_model, source_model)
    if result:
        print("Valid")
    else:
        print("Invalid")

