
import datatypes.trace as tr

def decode_long_linear_difference(ax, mag):
    result = [0, 0, 0]
    result[ax - 1] += (mag - 15)
    result = tuple(result)
    assert tr.is_long_linear_difference(result)
    return result

def decode_short_linear_difference(ax, mag):
    result = [0, 0, 0]
    result[ax - 1] += (mag - 5)
    result = tuple(result)
    assert tr.is_short_linear_difference(result)
    return result

def decode_near_difference(encoded):
    result = [-1, -1, -1]
    while encoded >= 9:
        result[0] += 1
        encoded -= 9
    while encoded >= 3:
        result[1] += 1
        encoded -= 3
    result[2] = encoded - 1
    result = tuple(result)
    assert tr.is_near_difference(result)
    return result

def read_trace(stream):

    trace = tr.Trace()

    while True:

        byte = ord(stream.read(1))
        long_opcode = byte & 0b1111
        short_opcode = byte & 0b111

        if byte == 0b11111111:
            trace.add(tr.Trace.Halt())
            break
        elif byte == 0b11111110:
            trace.add(tr.Trace.Wait())
        elif byte == 0b11111101:
            trace.add(tr.Trace.Flip())
        elif long_opcode == 0b0100:
            trace.add(tr.Trace.SMove(decode_long_linear_difference(byte >> 4, ord(stream.read(1)))))
            pass
        elif long_opcode == 0b1100:
            next_byte = ord(stream.read(1))
            dist1 = decode_short_linear_difference((byte >> 4) & 0b11, next_byte & 0b1111)
            dist2 = decode_short_linear_difference(byte >> 6, next_byte >> 4)
            trace.add(tr.Trace.LMove(dist1, dist2))
            pass
        elif short_opcode == 0b111:
            trace.add(tr.Trace.FusionP(decode_near_difference(byte >> 3)))
            pass
        elif short_opcode == 0b110:
            trace.add(tr.Trace.FusionS(decode_near_difference(byte >> 3)))
            pass
        elif short_opcode == 0b101:
            trace.add(tr.Trace.Fission(decode_near_difference(byte >> 3)))
            pass
        elif short_opcode == 0b011:
            trace.add(tr.Trace.Fill(decode_near_difference(byte >> 3)))
            pass

    junk_bytes = stream.read()

    if len(junk_bytes) != 0:
        raise Exception("Junk at end of stream: %s" % junk_bytes)

    return trace
