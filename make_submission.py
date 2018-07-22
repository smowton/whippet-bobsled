
# Takes a bunch of candidate traces on stdin and makes a zip file with the best ones
# for each problem.

# Arguments: make_submission.py models_directory output.zip
# The models_directory should contain FA001...186_tgt.mdl, and is used only to figure out the
# dimension of the relevant model.

import sys
import os.path
import tempfile
import subprocess
import re
import glob
import shutil

import serialize_trace.deserializer as deser

if len(sys.argv) != 3 or not sys.argv[1].endswith(".zip"):
    print >>sys.stderr, "Usage: make_submission.py output.zip models_dir"
    sys.exit(1)

if os.path.exists(sys.argv[1]):
    print >>sys.stderr, sys.argv[1], "already exists"
    sys.exit(1)

workdir = tempfile.mkdtemp()

best_traces = dict()

for line in sys.stdin:

    line = line.strip()
    if os.path.isdir(line):
        continue

    filename = os.path.basename(line)
    if re.match("F.\d{3}.nbt", filename) is None:
        print >>sys.stderr, "File", line, "not of the expected form F?NNN.nbt"
        sys.exit(1)

    with open(line + ".cost", "r") as f:
        cost = int(f.read().strip())

    print "Trace", line, "solves", filename, "cost", cost
    if filename not in best_traces or best_traces[filename][1] > cost:
        best_traces[filename] = (line, cost)

for modelpath in glob.glob(os.path.join(sys.argv[2], "F*.mdl")):

    expected_nbt = os.path.basename(modelpath).replace("_tgt.mdl", ".nbt").replace("_src.mdl", ".nbt")
    if expected_nbt not in best_traces:
        print >>sys.stderr, "No trace found solving ", modelpath
        sys.exit(1)

for (path, cost) in best_traces.itervalues():
    print "Submitting", path, "with cost", cost
    shutil.copy(path, workdir)

subprocess.call(["zip", "-r", sys.argv[1], "."], cwd = workdir)
