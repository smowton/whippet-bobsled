
import datatypes.trace as tr

def move(difference, trace):
    while difference != (0, 0, 0):
        if sum(map(lambda c: c != 0, difference)) == 2 and \
             all(tr.is_short_linear_difference((c, 0, 0)) for c in difference):
            # LMove can solve it in one:
            dist1 = None
            dist2 = None
            for (ax, c) in enumerate(difference):
                if c == 0:
                    continue
                dist = [0, 0, 0]
                dist[ax] = c
                if dist1 is None:
                    dist1 = tuple(dist)
                else:
                    assert dist2 is None
                    dist2 = tuple(dist)
            trace.add(tr.Trace.LMove(dist1, dist2))
            difference = (0, 0, 0)
        else:
            # SMove in direction requiring most travel
            largest_ax = max(enumerate(difference), key = lambda pair : abs(pair[1]))
            mv = [0, 0, 0]
            mv[largest_ax[0]] = max(min(largest_ax[1], 15), -15)
            mv = tuple(mv)
            difference = tr.coord_subtract(difference, mv)
            trace.add(tr.Trace.SMove(mv))
