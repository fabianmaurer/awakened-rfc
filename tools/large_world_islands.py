"""XL coastline corrections, applied before resource placement (offline Python 3).

Budgets are deliberately approximate: RFC enlarges Europe and compresses the
Arctic. The original map's land count is always the lower bound. Large islands
already consistent with their neighbouring mainland retain their XL footprint.
"""
from collections import deque
from pathlib import Path


# Reference-map bounding box: (name, XL land budget). None retains the footprint.
# Area comparisons: https://en.wikipedia.org/wiki/List_of_islands_by_area
# Rough regional densities: Europe 6,000 km2/tile; Japan 12,000; other regions
# 20,000. Rounded budgets retain recognizable coastlines and original land floors.
REVIEW = {
    (34, 60, 45, 67): ('Greenland', None),
    (27, 59, 35, 65): ('Baffin Island', 26),
    # Their coastlines encode RFC's enlarged European projection. Eroding them
    # to an area quota removes Scotland, Cornwall and Ireland's west coast.
    (50, 53, 54, 60): ('Great Britain', None),
    (73, 13, 76, 19): ('Madagascar', 30),
    (111, 24, 117, 27): ('New Guinea', None),
    (112, 44, 116, 49): ('Honshu', 20),
    (104, 27, 106, 30): ('Borneo', None),
    (19, 63, 22, 65): ('Victoria Island / western Arctic', 11),
    (120, 5, 122, 8): ('New Zealand South Island', 8),
    (45, 62, 47, 63): ('Iceland main body', None),
    (48, 55, 49, 58): ('Ireland', None),
    (114, 50, 116, 52): ('Hokkaido', 7),
    (19, 67, 23, 67): ('Western Queen Elizabeth Islands', 6),
    (27, 67, 31, 67): ('Ellesmere / northern Arctic', 10),
    (99, 26, 101, 28): ('Southern Sumatra', None),
    (108, 26, 109, 28): ('Sulawesi', 9),
    (108, 33, 109, 36): ('Luzon', 6),
    (76, 64, 77, 66): ('Novaya Zemlya', 4),
    (78, 67, 81, 67): ('Franz Josef Land', 4),
    (103, 25, 106, 25): ('Java', 7),
    (109, 30, 110, 32): ('Mindanao', 5),
    (111, 41, 112, 43): ('Kyushu', 4),
    (114, 7, 116, 8): ('Tasmania', 4),
    (122, 9, 123, 11): ('New Zealand North Island', 6),
    (17, 64, 18, 65): ('Banks Island / western Arctic', 4),
    (26, 38, 28, 38): ('Cuba', 5),
    (36, 53, 37, 54): ('Newfoundland', 5),
    (35, 4, 36, 4): ('Falkland Islands', 2),
    (58, 42, 58, 43): ('Sardinia and Corsica', None),
    (60, 40, 61, 40): ('Sicily', None),
    (65, 40, 66, 40): ('Peloponnese (diagonal mainland connection)', None),
    (68, 39, 69, 39): ('Crete', 2),
    (93, 28, 93, 29): ('Sri Lanka', 5),
    (98, 29, 98, 30): ('Northern Sumatra', None),
    (106, 32, 106, 33): ('Palawan', 2),
    (108, 38, 108, 39): ('Taiwan', 2),
    (113, 55, 113, 56): ('Northern Sakhalin', 4),
    (118, 27, 119, 27): ('New Britain', 2),
    (104, 67, 105, 67): ('Siberian Arctic coast', None),
}

# Single reference cells which represent sizeable islands or a mainland neck.
SINGLE = {
    (10, 51): ('Vancouver Island', 2),
    (10, 56): ('Alexander Archipelago', 1),
    (24, 31): ('Central American mainland neck', None),
    (25, 32): ('Panama mainland neck', None),
    (30, 37): ('Hispaniola', None),
    (27, 36): ('Jamaica', 2),
    (30, 39): ('Nassau / central Bahamas', 1),
    (32, 37): ('Puerto Rico', 1),
    (33, 35): ('St Kitts / Leeward Islands', 1),
    (33, 33): ('Grenada / Windward Islands', 1),
    (32, 3): ('Tierra del Fuego', 2),
    (34, 50): ('Nova Scotia mainland neck', None),
    (35, 51): ('Cape Breton Island', 1),
    (44, 43): ('Azores', 1),
    (44, 64): ('Iceland northwest', None),
    (45, 33): ('Cape Verde', 1),
    (47, 36): ('Canary Islands', 1),
    (47, 38): ('Madeira', 1),
    (54, 16): ('Saint Helena', 1),
    (71, 40): ('Cyprus', None),
    (72, 48): ('Crimea mainland neck', None),
    (79, 22): ('Seychelles', 1),
    (80, 29): ('Socotra', 1),
    (83, 16): ('Mauritius', 1),
    (88, 28): ('Maldives', 1),
    (104, 37): ('Hainan', 2),
    (108, 30): ('Mindanao (Zamboanga peninsula)', 1),
    (108, 32): ('Visayas', 1),
    (110, 40): ('Okinawa', 1),
    (113, 43): ('Shikoku', 2),
    (114, 54): ('Southern Sakhalin', 1),
    (115, 33): ('Mariana Islands', 1),
    (123, 58): ('Chukotka mainland coast', None),
}

# The XL grid has room for distinct one-tile islands and intervening sea lanes.
# Layout reference: https://www.nhc.noaa.gov/pdf/breakpoints_carib.pdf
# point: (island, relief, terrain, reference cell for settlement/war preferences)
ADDITIONS = {
    (183, 78): ('Sado', 1, 'GRASS', (114, 47)),
    (46, 65): ('Grand Bahama', 2, 'PLAINS', (30, 39)),
    (50, 62): ('Exuma', 2, 'PLAINS', (30, 39)),
    (54, 60): ('Virgin Islands', 1, 'PLAINS', (33, 33)),
    (55, 58): ('Antigua', 1, 'PLAINS', (33, 33)),
    (55, 56): ('Guadeloupe', 1, 'GRASS', (33, 33)),
    (55, 54): ('Martinique', 1, 'GRASS', (33, 33)),
    (57, 53): ('Barbados', 2, 'GRASS', (33, 33)),
    (56, 51): ('Trinidad', 2, 'GRASS', (33, 33)),
    (48, 59): ('Hispaniola', 1, 'GRASS', (30, 37)),
    (49, 59): ('Hispaniola', 2, 'GRASS', (30, 37)),
}

CARIBBEAN_NAMES = {
    (46, 65): 'Freeport', (48, 63): 'Nassau', (50, 62): 'George Town',
    (48, 60): 'Cap-Haitien', (49, 60): 'Santiago de los Caballeros',
    (48, 59): 'Port-au-Prince', (49, 59): 'Santo Domingo',
    (52, 60): 'San Juan', (54, 60): 'Road Town', (53, 57): 'Basseterre',
    (55, 58): "St. John's", (55, 56): 'Basse-Terre',
    (55, 54): 'Fort-de-France', (53, 53): "St. George's",
    (57, 53): 'Bridgetown', (56, 51): 'Port of Spain',
}

# At very small tile counts, symmetrical erosion can turn a long island across
# its axis. Retain recognizable silhouettes and their existing historical sites.
SMALL_SHAPES = {
    'Taiwan': {(174, 62), (174, 63)},
    'Crete': {(111, 63), (112, 63)},
    'Sri Lanka': {(150, 48), (151, 48), (150, 47), (151, 47), (151, 46)},
    'Tasmania': {(185, 13), (186, 13), (187, 13), (186, 12)},
}

# Retain the original diagonal crossings and the adjoining narrow approaches.
# Individual island silhouettes must not erase Japan's existing walking route.
JAPAN_CONNECTIONS = {(182, 73), (181, 72), (181, 71), (182, 70),
                     (186, 79), (185, 80), (184, 81), (185, 82), (186, 82)}


def refine_grids(rows, plane, city_names, civilization, refinements):
    """Give new land the adjacent archipelago's AI values and actual town names."""
    result = [list(row) for row in rows]
    for (x, y), (island, relief, terrain, reference) in ADDITIONS.items():
        if not city_names:
            sx, sy = reference
            result[109-y][x] = plane[67-sy][sx]
    if city_names:
        for (x, y), name in CARIBBEAN_NAMES.items():
            result[109-y][x] = name
            if refinements is not None:
                refinements.setdefault((x, y), {})[civilization] = name
    return tuple(tuple(row) for row in result)


def components(points, width, diagonal=False):
    remaining = set(points)
    steps = ((-1, 0), (1, 0), (0, -1), (0, 1))
    if diagonal:
        steps += ((-1, -1), (-1, 1), (1, -1), (1, 1))
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        found, queue = {seed}, deque([seed])
        while queue:
            x, y = queue.popleft()
            for dx, dy in steps:
                point = ((x + dx) % width, y + dy)
                if point in remaining:
                    remaining.remove(point)
                    found.add(point)
                    queue.append(point)
        yield found


def refine(plots, source, origins, protected, naming_sites, report_path):
    """Erode excess coastal cells without flooding starts or splitting islands.

    Four-neighbour source components separate the Japanese islands, which touch
    diagonally in RFC. Continental fragments at those same diagonal necks are
    explicitly retained. The report accounts for every source land component.
    """
    # Preserve physical necks and the original traversable Japanese crossings.
    protected = (set(protected) | set(naming_sites) | set().union(*SMALL_SHAPES.values()) | set(CARIBBEAN_NAMES) |
                 {(175, 49), (176, 50), (183, 89), (184, 88)} | JAPAN_CONNECTIONS)
    land = {point for point, fields in source.items() if 'PlotType=3' not in fields}
    rows, islands = [], {}
    removed = set()
    for original in components(land, 124):
        box = (min(x for x, y in original), min(y for x, y in original),
               max(x for x, y in original), max(y for x, y in original))
        if len(original) > 100:
            name, budget = 'Continental mainland', None
        elif box[1] <= 1:
            name, budget = 'Antarctic coastline', None
        elif len(original) == 1:
            point = next(iter(original))
            name, budget = SINGLE.get(point, ('Small island at %d,%d' % point, 1))
        elif box in REVIEW:
            name, budget = REVIEW[box]
        elif box == (27, 59, 28, 59):
            name, budget = 'Baffin coastal fragment', len(original)
        elif box[1] >= 59:
            name, budget = 'Arctic island group', len(original)
        elif box in ((3, 57, 4, 57), (5, 35, 5, 36), (21, 26, 21, 27)):
            name, budget = 'Small island group', len(original)
        else:
            raise ValueError('Unreviewed reference island: %s' % (box,))
        footprint = {p for p, origin in origins.items()
                     if origin in original and 'PlotType=3' not in plots[p]}
        if name == 'Cyprus':
            # The authored lowland extends into a reference water cell.
            footprint.add((114, 65))
        before = len(footprint)
        if before < len(original):
            raise ValueError('Coast refinement violates the non-XL island floor: ' + name)
        target = before if budget is None else min(before, max(len(original), budget))
        kept = set(footprint)
        fixed = protected & kept
        # At least one habitable cell survives wherever the enlarged island has
        # one; a tiny island must not become an isolated uninhabitable peak.
        usable = {p for p in kept if any(t in plots[p] for t in ('PlotType=1', 'PlotType=2'))
                  and not any('_IMPASSABLE' in f or 'FEATURE_ICE' in f for f in plots[p])}
        if usable and not (fixed & usable):
            fixed.add(min(usable, key=lambda p: (p not in naming_sites, p)))
        target = max(target, len(fixed))
        if target < before:
            # Preserve the outline at a smaller area. Prefer coastal cells far
            # from a contracted silhouette, retaining authored names on ties.
            cx = sum(x for x, y in kept) / before
            cy = sum(y for x, y in kept) / before
            ratio = (target / before) ** .5
            silhouette = {(round(cx + (x - cx) * ratio), round(cy + (y - cy) * ratio))
                          for x, y in kept}
            def removal_rank(p):
                distance = min((p[0]-x)**2 + (p[1]-y)**2 for x, y in silhouette)
                coast = sum(((p[0]+dx) % 200, p[1]+dy) not in kept
                            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)))
                return (-distance, p in naming_sites, -coast, p)
            while len(kept) > target:
                for point in sorted(kept - fixed, key=removal_rank):
                    if not any(((point[0]+dx) % 200, point[1]+dy) not in kept
                               for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))):
                        continue
                    candidate = kept - {point}
                    if len(list(components(candidate, 200))) != 1:
                        continue
                    kept.remove(point)
                    removed.add(point)
                    break
                else:
                    # Area budgets are approximate. Keep the remaining outline
                    # when further erosion would strand names or split land.
                    print('%s retains %d tiles to preserve its outline (area budget %d)' %
                          (name, len(kept), target))
                    break
            for point in footprint - kept:
                plots[point] = ['TerrainType=TERRAIN_COAST', 'PlotType=3']
        if len(original) <= 100 and box[1] > 1 and budget is not None:
            for point in original:
                islands[point] = kept
        rows.append((name, ','.join(map(str, box)), len(original), before, len(kept)))
    for point, (name, relief, terrain, reference) in ADDITIONS.items():
        if 'PlotType=3' not in plots[point]:
            raise ValueError('New island overlaps existing land: %s' % (point,))
        if name != 'Hispaniola' and any(
                'PlotType=3' not in plots.get((point[0]+dx, point[1]+dy), ['PlotType=3'])
                for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy):
            raise ValueError('New island closes a sea lane: ' + name)
        plots[point] = ['TerrainType=TERRAIN_' + terrain, 'PlotType=%d' % relief,
                         'FeatureType=FEATURE_FOREST, FeatureVariety=0']
        if name == 'Hispaniola':
            islands.setdefault((30, 37), set()).add(point)
        else:
            islands[origins[point]] = {point}
            rows.append((name, 'new at %d,%d' % point, 0, 0, 1))
    # Hispaniola is much larger than the reference's single cell: four XL cells
    # put it in proportion to five-cell Cuba, while retaining a separate strait.
    islands[30, 37].update(((48, 60), (49, 60)))
    rows = [row[:4] + (4,) if row[0] == 'Hispaniola' else row for row in rows]
    if any('PlotType=3' in plots[point] for point in CARIBBEAN_NAMES):
        raise ValueError('Caribbean town name lies on water')
    connected = list(components(
        {p for p, fields in plots.items() if 'PlotType=3' not in fields}, 200, diagonal=True))
    for neck in ({(175, 49), (176, 50)}, {(183, 89), (184, 88)}):
        if not any(neck <= group for group in connected):
            raise ValueError('Island correction severs a physical island neck')
    walkable = {p for p, fields in plots.items() if 'PlotType=3' not in fields
                and 'PlotType=0' not in fields
                and not any('_IMPASSABLE' in f or 'FEATURE_ICE' in f for f in fields)}
    if not any(JAPAN_CONNECTIONS <= group for group in components(walkable, 200, diagonal=True)):
        raise ValueError('Island correction severs the Japanese walking route')
    from large_world_coasts import normalize_shores
    river_edges = normalize_shores(plots, removed | set(ADDITIONS))
    print('Shoreline river segments removed:', river_edges)
    Path(report_path).write_text(
        'Region\tReference bounds\tNon-XL tiles\tUncorrected XL tiles\tCorrected XL tiles\n' +
        ''.join('\t'.join(map(str, row)) + '\n' for row in rows), encoding='utf-8')
    changed = [row for row in rows if row[3] > row[4]]
    print('Island review: %d reference land components; %d reduced; %d excess tiles removed; %d tiles added' %
          (len(rows) - sum(row[2] == 0 for row in rows), len(changed), len(removed), len(ADDITIONS)))
    return islands, removed
