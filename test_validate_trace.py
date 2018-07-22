import model_reader.model_reader as model_reader
import trace_generators.simple_trace_generator as generator
import datatypes.trace as trace
import model_reader.model_reader as model_reader

target_model = model_reader.read('./data/problems/LA001_tgt.mdl')
output_trace = generator.build_simple_trace(target_model)
(state, result) = output_trace.validate(target_model)
print(result)
model_reader.dump_slices(state.current_model)
