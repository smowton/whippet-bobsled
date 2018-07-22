import model_reader.model_reader as model_reader
from serialize_trace import deserializer

target_model = model_reader.read('./data/problems/LA001_tgt.mdl')
trace = deserializer.read_trace(open('./data/LA001_parallel.nbt', "rb"))
(state, result) = trace.validate(target_model)
print(result)
model_reader.dump_slices(state.current_model)
