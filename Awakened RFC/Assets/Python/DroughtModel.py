"""Directed drought reaches and analytical food calibration. Python 2.4.

No game imports: the runtime supplies geometry and synchronized random draws.
"""

MIN_REACH, MAX_REACH = 6, 12
MIN_MARGIN, MAX_MARGIN = 2, 4
TARGET_FOOD = 3.5
ORDINARY_DRY = (1., 1., 1., 1., .75, .5, .25)


def templates(ends, anchors, rand):
    """Sample a saved, equally likely catalogue using the game's seeded RNG."""
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
                # Each direction follows only its channel: it never fans out.
                current = anchor
                if path: current = path[-1]
                for step in range(count):
                    if current not in ends: break
                    start, end = ends[current]
                    candidates = outgoing.get(end, [])
                    if reverse: candidates = incoming.get(start, [])
                    choices = [edge for edge in candidates if edge not in used]
                    if not choices: break
                    chosen = choices[0]
                    if len(choices) > 1:
                        chosen = choices[rand(len(choices), 'Drought river branch')]
                    used.add(chosen)
                    path.append(chosen)
                    current = chosen

            size = MIN_REACH + rand(MAX_REACH - MIN_REACH + 1, 'Drought reach length')
            before = rand(size, 'Drought reach position')
            extend(upstream, before, True)
            extend(downstream, size - 1 - len(upstream), False)
            # If the mouth is close, try to use the remaining length upstream.
            extend(upstream, size - 1 - len(upstream) - len(downstream), True)
            core = sorted(used)
            extend(upstream, MIN_MARGIN + rand(MAX_MARGIN - MIN_MARGIN + 1,
                'Drought upstream margin'), True)
            extend(downstream, MIN_MARGIN + rand(MAX_MARGIN - MIN_MARGIN + 1,
                'Drought downstream margin'), False)
            result.append({'core': core, 'margin': sorted(used.difference(set(core)))})
    return result


def initiationWeight(length):
    if length == 0: return 0
    return max(3, length)


def calibrationRows(floodBanks, regions):
    """Inclusion-exclusion keeps healthy second rivers in the food estimate."""
    catalogues = []
    for region in regions:
        catalogue = [set(shape['core']) for shape in region['templates']]
        catalogueEdges = set(region['edges'])
        catalogues.append((catalogueEdges, catalogue, initiationWeight(len(region['floodEdges']))))
    rows = []
    for banks in floodBanks:
        tileRows = []
        for mask in range(1, 1 << len(banks)):
            selected = set([banks[i] for i in range(len(banks)) if mask & (1 << i)])
            sign = 1
            if len(selected) % 2: sign = -1
            dry = []
            for catalogueEdges, catalogue, weight in catalogues:
                if not selected.intersection(catalogueEdges): continue
                core = sum([1 for c in catalogue if selected.intersection(c)]) / float(len(catalogue))
                for age in range(7):
                    dry.append((core * ORDINARY_DRY[age], weight))
            tileRows.append((sign, dry))
        rows.append(tileRows)
    return rows


def expectedFood(rows, probability):
    if not rows: return 4.
    total = 0.
    for tileRows in rows:
        allDry = 1.
        for sign, dry in tileRows:
            noDry = 1.
            for coverage, weight in dry:
                # Match the runtime's integer roll and minimum river length.
                chance = min(10000, int(probability * weight * 10000. + .5)) / 10000.
                noDry *= 1. - chance * coverage
            allDry += sign * noDry
        # A floodplain without bordering edges cannot suffer river drought.
        if not tileRows: allDry = 0.
        total += 4. - 2. * allDry
    return total / len(rows)


def calibrate(floodBanks, regions):
    rows = calibrationRows(floodBanks, regions)
    if not rows: return 0, 4.
    # One shared rate per weighted river segment; no river exceeds 100%.
    low, high = 0., 1. / max([initiationWeight(len(region['floodEdges'])) for region in regions])
    for step in range(24):
        middle = (low + high) / 2.
        if expectedFood(rows, middle) > TARGET_FOOD: low = middle
        else: high = middle
    chance = high * 10000.
    return chance, expectedFood(rows, chance / 10000.)
