"""Directed floodplain reaches and stationary fertility weights. Python 2.4."""

NORMAL, WEAK, DROUGHT, STRONG, EXTREME = range(5)
PRIORITY = (0, 2, 3, 1, 4)
MIN_REACH, MAX_REACH = 6, 12
INITIAL_PROTECTION = 40
RECOVERY_PROTECTION = 12
CHANCE_PER_EDGE = .005
# Event starts, not time shares: drought:weak and extreme:strong are both 1:2.
KINDS = (WEAK, WEAK, DROUGHT, STRONG, STRONG, EXTREME)


def templates(ends, anchors, rand):
    incoming, outgoing = {}, {}
    for edge in sorted(ends.keys()):
        start, end = ends[edge]
        outgoing.setdefault(start, []).append(edge)
        incoming.setdefault(end, []).append(edge)
    result = []
    rounds = max(4, (64 + len(anchors) - 1) // len(anchors))
    for repeat in range(rounds):
        for anchor in anchors:
            used = set([anchor])
            upstream, downstream = [], []

            def extend(path, count, reverse):
                current = anchor
                if path: current = path[-1]
                for step in range(count):
                    if current not in ends: break
                    start, end = ends[current]
                    choices = outgoing.get(end, [])
                    if reverse: choices = incoming.get(start, [])
                    choices = [e for e in choices if e not in used]
                    if not choices: break
                    chosen = choices[0]
                    if len(choices) > 1:
                        chosen = choices[rand(len(choices), 'Floodplain river branch')]
                    used.add(chosen)
                    path.append(chosen)
                    current = chosen

            size = MIN_REACH + rand(MAX_REACH - MIN_REACH + 1, 'Floodplain reach length')
            extend(upstream, rand(size, 'Floodplain reach position'), True)
            extend(downstream, size - 1 - len(upstream), False)
            extend(upstream, size - 1 - len(upstream) - len(downstream), True)
            path = list(reversed(upstream)) + [anchor] + downstream
            count = 2 + rand(2, 'Floodplain core length')
            first = max(0, min(len(path) - count, len(upstream) - count // 2))
            core = path[first:first + count]
            result.append({'core': sorted(core), 'reach': sorted(used)})
    return result


def initiationChance(length):
    if not length: return 0
    return min(2500, int(max(3, length) * CHANCE_PER_EDGE * 10000 + .5))


def stationaryWeights(chance, fullCoverage, coreCoverage):
    """Renewal weights for one river's uniform saved reach catalogue.

    Initial phases average five turns. Severe events add five recovery turns,
    one warning turn, and twelve protected turns after recovery. An expired
    event can roll immediately, so normal waiting time is (1-p)/p.
    Historical events and the opening grace period are excluded.
    """
    if not chance: return [1., 0., 0., 0., 0.]
    probability = chance / 10000.
    cycle = (1. - probability) / probability + 7. + RECOVERY_PROTECTION / 3.
    mild = 5. * fullCoverage / (2. * cycle)
    severe = 5. * coreCoverage / (6. * cycle)
    return [1. - 2. * mild - 2. * severe, mild, severe, mild, severe]


def combineWeights(left, right):
    """Independent rivers sharing a tile use the more disruptive state."""
    result = [0.] * 5
    for a in range(5):
        for b in range(5):
            state = a
            if PRIORITY[b] > PRIORITY[a]: state = b
            result[state] += left[a] * right[b]
    return result
