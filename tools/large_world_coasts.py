"""Refine the XL shoreline without changing RFC's regional projection.

Bilinear coverage rounds replicated source-cell corners; local topology guards
retain narrow peninsulas, channels and islands. Explicit small stencils correct
features whose coarse reference outline cannot be recovered by interpolation.
"""
from collections import Counter, defaultdict, deque
from math import floor
from pathlib import Path

WIDTH, HEIGHT = 200, 110
ORTHOGONAL = ((-1, 0), (1, 0), (0, -1), (0, 1))
NEIGHBOURS = tuple((dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy)

# Iceland's Westfjords join the main body; the eastern/southern coast tapers.
# Reference: Iceland's official mapping service, https://www.natt.is/en/resources/geospatial-data
ICELAND = {(71, 104), (72, 104)} | {
    (x, y) for y, xs in ((103, range(72, 76)), (102, range(72, 77)),
                         (101, range(73, 77)), (100, range(73, 76))) for x in xs}
# Baja runs northwest/southeast, with an open Gulf of California to its east.
# Reference: https://conanp.gob.mx/conanp/dominios/islasgc/igcson/ubicacion.php
BAJA = {(x, y) for y, xs in (
    (70, (20, 21)), (69, (20, 21)), (68, (21, 22)), (67, (21, 22)),
    (66, (22,)), (65, (22,)), (64, (22,)), (63, (22,))) for x in xs}
OUTLINES = (((70, 99, 78, 105), ICELAND), ((19, 63, 23, 70), BAJA))


def near(point, steps=NEIGHBOURS):
    x, y = point
    return [((x+dx) % WIDTH, y+dy) for dx, dy in steps if 0 <= y+dy < HEIGHT]


def connected(points):
    if not points:
        return True
    remaining = set(points)
    queue = [remaining.pop()]
    while queue:
        for point in near(queue.pop(), ORTHOGONAL):
            if point in remaining:
                remaining.remove(point)
                queue.append(point)
    return not remaining


def coverage(source, point):
    x, y = point
    fx, fy = (x+.5)*124/WIDTH-.5, (y+.5)*68/HEIGHT-.5
    sx, sy = floor(fx), floor(fy)
    tx, ty = fx-sx, fy-sy
    return sum(wx*wy for dx, wx in ((0, 1-tx), (1, tx))
               for dy, wy in ((0, 1-ty), (1, ty))
               if 'PlotType=3' not in source[(sx+dx) % 124, max(0, min(67, sy+dy))])


def region(point):
    x, y = point
    if y <= 3:
        return 'Antarctic fringe'
    if 69 <= x <= 79 and y >= 98:
        return 'Iceland / North Atlantic'
    if 32 <= x <= 59 and 49 <= y <= 70:
        return 'Caribbean / Central America'
    if x <= 76:
        if y >= 53:
            return 'North America west / Arctic' if x <= 42 else 'North America east / Greenland'
        return 'South America' if x >= 32 else 'Pacific islands / eastern Pacific'
    if x <= 127:
        return 'Europe / Mediterranean' if y >= 62 else 'Africa / Atlantic'
    if x <= 156:
        return 'West Asia / Indian subcontinent' if y >= 42 else 'Indian Ocean'
    if y >= 61:
        return 'East Asia / northwest Pacific'
    return 'Southeast Asia / New Guinea' if y >= 37 else 'Australia / New Zealand / southwest Pacific'


def normalize_shores(plots, changed, clear_rivers=True):
    """Remove river edges bordering water; update the locally changed sea floor.

    A river mouth ends at a coastal corner. A segment between land and sea is
    a shoreline-parallel river, not an estuary, and must not survive resizing.
    """
    rivers = 0
    for point, fields in plots.items():
        x, y = point
        for other, flag, direction in (((x, y-1), 'isNOfRiver', 'RiverWEDirection='),
                                        (((x+1) % WIDTH, y), 'isWOfRiver', 'RiverNSDirection=')):
            if clear_rivers and flag in fields and (other not in plots or any(
                    'PlotType=3' in plots[p] for p in (point, other))):
                fields[:] = [f for f in fields if f != flag and not f.startswith(direction)]
                rivers += 1
    shores = set(changed)
    for point in changed:
        shores.update(near(point))
    for point in shores:
        if point not in plots or 'PlotType=3' not in plots[point]:
            continue
        coast = any('PlotType=3' not in plots[q] for q in near(point))
        plots[point][:] = [f for f in plots[point] if not f.startswith('TerrainType=')]
        plots[point].append('TerrainType=TERRAIN_' + ('COAST' if coast else 'OCEAN'))
    return rivers


def repair_river_mouths(plots, reference):
    """Extend displaced mouths on land edges, following their original basins.

    Trace removed mouth segments upstream before seeking a short new outlet.
    Only former coastal outlets qualify; inland sources and lake tributaries
    keep their existing flow directions, and no shoreline-parallel edge is added.
    """
    def segments(grid):
        for (x, y), fields in grid.items():
            if 'isNOfRiver' in fields:
                a, b = (x, y), ((x+1) % WIDTH, y)
                yield (a, b) if 'RiverWEDirection=1' in fields else (b, a)
            if 'isWOfRiver' in fields:
                a, b = ((x+1) % WIDTH, y), ((x+1) % WIDTH, y+1)
                yield (a, b) if 'RiverNSDirection=0' in fields else (b, a)

    def coastal(grid, vertex):
        x, y = vertex
        return any('PlotType=3' in grid.get(((x+dx) % WIDTH, y+dy), ())
                   for dx in (-1, 0) for dy in (-1, 0))

    def edge(a, b):
        x, y = a
        nx, ny = b
        if y == ny:
            west = x if nx == (x+1) % WIDTH else nx
            return (west, y), (west, y-1), 'isNOfRiver', 'RiverWEDirection=', 1 if west == x else 3
        south = min(y, ny)
        return ((x-1) % WIDTH, south), (x, south), 'isWOfRiver', 'RiverNSDirection=', 0 if ny > y else 2

    old = list(segments(reference))
    parents, old_out = defaultdict(set), set()
    for a, b in old:
        parents[b].add(a)
        old_out.add(a)
    mouths = sorted(v for v in parents if v not in old_out and coastal(reference, v))
    # A river can enter a lake and continue on the far shore in the reference
    # graph. Clearing those water edges creates an additional upstream outlet,
    # even though it was not a terminal vertex in that graph.
    current = list(segments(plots))
    outgoing = {a for a, b in current}
    mouths.extend(sorted({b for a, b in current} - outgoing - set(mouths)))
    extensions = 0
    for mouth in mouths:
        current = list(segments(plots))
        vertices = {v for pair in current for v in pair}
        outgoing = {a for a, b in current}
        queue, seen, start = deque([(mouth, 0)]), set(), None
        while queue:
            v, distance = queue.popleft()
            if v in seen:
                continue
            seen.add(v)
            if v in vertices:
                if v not in outgoing:
                    start = v
                    break
                continue
            queue.extend((p, distance+1) for p in sorted(parents[v]))
        if start is None or coastal(plots, start):
            continue
        queue, seen, path = deque([(start, [])]), {start}, None
        while queue:
            v, route = queue.popleft()
            if coastal(plots, v):
                path = route
                break
            if len(route) >= 6:
                continue
            x, y = v
            neighbours = [((x+dx) % WIDTH, y+dy) for dx, dy in ORTHOGONAL]
            neighbours.sort(key=lambda p: (abs(p[0]-mouth[0])+abs(p[1]-mouth[1]), p))
            for n in neighbours:
                if n in seen or n in vertices:
                    continue
                p, q, flag, direction, flow = edge(v, n)
                if any(t not in plots or 'PlotType=3' in plots[t] or 'PlotType=0' in plots[t]
                       for t in (p, q)):
                    continue
                seen.add(n)
                queue.append((n, route+[(v, n)]))
        if path is None:
            raise ValueError('No land-edge outlet for displaced river mouth: %s' % (mouth,))
        for a, b in path:
            p, q, flag, direction, flow = edge(a, b)
            plots[p].extend((flag, direction+str(flow)))
            extensions += 1
    print('River mouth extensions:', extensions)
    final = list(segments(plots))
    outgoing = {a for a, b in final}
    stranded = {b for a, b in final if b not in outgoing and not coastal(plots, b)}
    if stranded:
        raise ValueError('River outlets stranded inland: %s' % sorted(stranded))


def refine(plots, origins, source, protected):
    original = {p for p, fields in plots.items() if 'PlotType=3' not in fields}
    land = set(original)
    protected = set(protected)
    protected.update(p for p, fs in plots.items() if any(f.startswith('ImprovementType=') for f in fs))
    fixed_sites = set(protected)
    # Retain the recognizable British outlines rather than another area-based
    # erosion. The island pass also leaves these two complete silhouettes alone.
    protected.update((x, y) for x in range(76, 90) for y in range(85, 100))
    for box, shape in OUTLINES:
        west, south, east, north = box
        protected.update((x, y) for x in range(west, east+1) for y in range(south, north+1))
    candidates = []
    for point in plots:
        if point in protected or point[1] <= 3 or point[1] >= HEIGHT-2:
            continue
        score = coverage(source, point)
        wanted = score >= .5
        if wanted != (point in land):
            candidates.append((-abs(score-.5), point, wanted))
    for confidence, point, wanted in sorted(candidates):
        neighbours = near(point)
        orthogonal = near(point, ORTHOGONAL)
        land_ring = {q for q in neighbours if q in land}
        sea_ring = set(neighbours) - land_ring
        # A local simple-point change cannot sever an isthmus, seal a strait,
        # join islands or create a lake. Thin tips are deliberately retained.
        if (len([q for q in orthogonal if q in land]) not in (2, 3) or
                not connected(land_ring) or not connected(sea_ring)):
            continue
        if wanted:
            land.add(point)
        else:
            land.remove(point)
    for (west, south, east, north), shape in OUTLINES:
        old = {p for p in land if west <= p[0] <= east and south <= p[1] <= north}
        if (old - shape) & fixed_sites:
            raise ValueError('Authored coastline floods a protected site')
        land.difference_update(old)
        land.update(shape)
    added, removed = land-original, original-land
    for point in sorted(added):
        x, y = point
        choices = [q for q in original if min(abs(q[0]-x), WIDTH-abs(q[0]-x)) <= 3 and abs(q[1]-y) <= 3]
        if not choices:
            raise ValueError('New coast has no neighbouring terrain: %s' % (point,))
        parent = min(choices, key=lambda q: (min(abs(q[0]-x), WIDTH-abs(q[0]-x))**2 + (q[1]-y)**2, q))
        # Copy climate and vegetation, never duplicate rivers, development or
        # starts. Parent origins keep island resource regions and area floors valid.
        plots[point] = [f for f in plots[parent] if not f.startswith((
            'BonusType=', 'ImprovementType=', 'RouteType=', 'River', 'isNOfRiver', 'isWOfRiver'))]
        plots[point] = ['PlotType=1' if f == 'PlotType=0' else f for f in plots[point]]
        origins[point] = origins[parent]
    for point in removed:
        plots[point] = ['TerrainType=TERRAIN_COAST', 'PlotType=3']
    # River normalization is deferred until historical starts have been placed
    # and the final island masks are known.
    normalize_shores(plots, added | removed, clear_rivers=False)
    print('Worldwide coast pass: %d land tiles added; %d removed; all shoreline regions reviewed' %
          (len(added), len(removed)))
    return original


def write_review(plots, original, report_path):
    """Report the finished coastline, including island and authored changes."""
    land = {p for p, fields in plots.items() if 'PlotType=3' not in fields}
    added, removed = land-original, original-land
    before, after, gains, losses = (Counter() for i in range(4))
    for mask, counts in ((original, before), (land, after)):
        for p in mask:
            if any(q not in mask for q in near(p)):
                counts[region(p)] += 1
    gains.update(region(p) for p in added)
    losses.update(region(p) for p in removed)
    Path(report_path).write_text(
        'Region\tEnlarged source shore tiles\tFinal shore tiles\tLand added\tLand removed\n' +
        ''.join('%s\t%d\t%d\t%d\t%d\n' % (name, before[name], after[name], gains[name], losses[name])
                for name in sorted(before.keys() | after.keys())), encoding='utf-8')


def grid_sources(map_text):
    """Supply newly exposed land with adjacent land's naming and AI geography.

    Reconstruct from the final map so --city-names-only produces the same grids.
    Explicit Caribbean names/preferences are applied afterwards by the island pass.
    """
    import re
    source_path = Path(__file__).resolve().parents[1] / 'Awakened RFC/PublicMaps/Start 1 - 3000 BC.CivBeyondSwordWBSave'
    source = {}
    for block in re.findall(r'BeginPlot\s*\n(.*?)EndPlot', source_path.read_text(encoding='utf-8-sig'), re.S):
        p = tuple(map(int, re.search(r'x=(\d+),y=(\d+)', block).groups()))
        source[p] = 'PlotType=3' not in block
    result = {}
    for block in re.findall(r'BeginPlot\s*\n(.*?)EndPlot', map_text, re.S):
        if 'PlotType=3' in block:
            continue
        x, y = map(int, re.search(r'x=(\d+),y=(\d+)', block).groups())
        origin = int((x+.5)*124/WIDTH), int((y+.5)*68/HEIGHT)
        if source[origin]:
            continue
        sx, sy = origin
        choices = [((sx+dx) % 124, sy+dy) for dx in range(-2, 3) for dy in range(-2, 3)
                   if 0 <= sy+dy < 68 and source[(sx+dx) % 124, sy+dy]]
        if choices:
            result[x, y] = min(choices, key=lambda p: (min(abs(p[0]-sx), 124-abs(p[0]-sx))**2 + (p[1]-sy)**2, p))
    return result
