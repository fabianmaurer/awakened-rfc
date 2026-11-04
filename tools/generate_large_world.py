"""Author the alternative 3000 BC world and its static Python 2.4 geography.

Run with Python 3 from any directory. Never launches Civilization IV.
The original RFC cartography supplies coastlines; this offline conversion also
authors terrain barriers, preserves corridors and emits independent profile data.
"""
from collections import Counter, deque
import argparse
import heapq
import math
from pathlib import Path
import pprint
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'Awakened RFC'
DATA = MOD / 'Assets/Python/ScenarioGeographyData'
sys.path.insert(0, str(DATA))
import Earth124x68 as BASE

WIDTH, HEIGHT = 160, 88
NAME = 'Earth160x88'
# Retain the Large start for authoring without exposing it in the scenario menu.
TARGET = ROOT / 'tools/scenario_templates/disabled/Start 1b - 3000 BC - Large World.CivBeyondSwordWBSave'
DESCRIPTION = 'TXT_KEY_ARFC_LARGE_WORLD_DESC'
ATLAS_NAME = 'LargeWorldResources.tsv'


def resource_free_settlements(profile_values):
    """Keep reviewed XL births and the 800 BC cities free of all dated bonuses."""
    result = {tuple(pos) for key in ('Consts.tCapitals', 'Consts.tReserveCapitals')
              for pos in profile_values[key] if pos}
    result.update(profile_values[key] for key in (
        'NativeAmerica.configureRegions.capital_1', 'NativeAmerica.configureRegions.capital_2',
        'Korea.setup.capital_1', 'Korea.setup.capital_2', 'Korea.setup.capital_3'))
    # Authored 800 BC settlements, including secondary and Independent cities.
    result.update(((36, 57), (95, 76), (108, 67), (110, 59), (111, 54),
                   (118, 62), (118, 65), (123, 65), (124, 69), (128, 65),
                   (137, 77), (142, 62), (145, 65), (150, 65), (165, 76),
                   (166, 70), (172, 71)))
    return result


def axis(n, vertical=False):
    old, new = (68, HEIGHT) if vertical else (124, WIDTH)
    if n == old:  # Exclusive range endpoint.
        return new
    return int((n + .5) * new / old)


def edge(n, vertical=False):
    """First destination cell in a source cell (also exclusive range bounds)."""
    old, new = (68, HEIGHT) if vertical else (124, WIDTH)
    return max(0, min(new, (2 * n * new + old - 1) // (2 * old)))


def footprint(point):
    x, y = point
    return tuple((dx, dy) for dx in range(edge(x), edge(x + 1))
                 for dy in range(edge(y, True), edge(y + 1, True)))


def rectangle(value):
    west, south, east, north = value
    return (edge(west), edge(south, True), edge(east + 1) - 1,
            edge(north + 1, True) - 1)


def corners(value, upper=False):
    if not value:
        return value
    if len(value) == 2 and isinstance(value[0], int):
        return type(value)(edge(n + int(upper), i == 1) - int(upper)
                           for i, n in enumerate(value))
    return type(value)(corners(v, upper) for v in value)


def boxes(value):
    if len(value) == 2 and len(value[0]) == 2 and isinstance(value[0][0], int):
        return (corners(value[0]), corners(value[1], True))
    return tuple(boxes(v) for v in value)


def coordinate(value):
    """Only geographic sequences; turn numbers and weights stay untouched."""
    kind = type(value)
    if not value:
        return value
    if len(value) in (2, 3, 4) and all(isinstance(n, int) for n in value[:2]):
        if len(value) == 3:  # Named city anchor.
            return kind((axis(value[0]), axis(value[1], True), value[2]))
        if len(value) == 4:
            return kind(rectangle(value))
        return kind(axis(n, i % 2 == 1) for i, n in enumerate(value))
    return kind(coordinate(n) for n in value)


# Scalar keys do not encode their axis. Keep this explicit and reviewable.
PY_Y = {
    'Arctic': {4, 6, 10, 12}, 'RiseAndFall': {2},
    'Korea': {2, 4}, 'Victory': {2, 4, 8}, 'Congresses': {3, 4},
    'CvRFCEventHandler': {2}, 'RomanEmpire': set(range(2, 15, 2)),
}
PY_LOWER = {'Arctic': set(range(7, 13)), 'Korea': {3, 4},
            'RomanEmpire': set(range(9, 15)), 'Congresses': {2}}
PY_UPPER = {'Arctic': set(range(1, 7)), 'Korea': {1, 2},
            'RomanEmpire': set(range(3, 9)), 'Congresses': {1, 3, 4}}
RANGE_Y = {'Arctic.range_13', 'Arctic.range_15', 'NativeAmerica.range_2',
           'Korea.range_6', 'RiseAndFall.range_4', 'Barbs.range_2',
           'Stability.range_2', 'CvRFCEventHandler.range_6'}
BOX_KEYS = {'Korea.CITY_NAME_AREA', 'Korea.cityNameMap.areas_1',
            'Caliphate.configureRegions.bounds_1', 'Caliphate.configureRegions.cores_1',
            'Barbs.checkAmericanRaids.lRegions_1', 'RiseAndFall.processAfrica.bounds'}
FOOTPRINT_KEYS = {'RiseAndFall.conquerorFeaturePlots', 'RiseAndFall.conquerorHillPlots',
                  'RiseAndFall.aztecHillPlots', 'RiseAndFall.conquerorBlockedPlots',
                  'Victory.tMediterraneanExceptions'}
NATIVE_Y = {
    'CvCaliphate': {3, 4, 6, 9, 10, 13, 14},
    'CvCity': set(range(2, 19, 2)) | set(range(19, 36)) |
              {38, 39, 41, 44, 45, 48, 49, 52, 53},
    'CvGame': {3, 4, 6},
    'CvPlayer': {n for n in range(1, 33) if (n - 1) % 4 >= 2} |
                {34, 36, 38, 40, 42},
    'CvPlayerAI': {3, 4, 7, 8},
    'CvUnitAI': {2, 4, 6, 8, 10, 12, 13, 15, 16, 18, 20,
                 22, 24, 26, 28, 30, 32, 34},
}
NATIVE_UPPER = {
    'CvCaliphate': {2, 4, 5, 8, 10, 12, 14},
    'CvCity': {35, 37, 39, 41, 43, 45, 47, 49, 51, 53},
    'CvGame': {2, 4},
    'CvPlayer': set(range(2, 33, 2)) | {33, 34},
    'CvPlayerAI': {2, 4, 6, 8, 9},
    'CvUnitAI': {1, 2, 3, 4, 5, 6, 7, 8, 15, 17, 18, 19, 20, 33},
}
NATIVE_LOWER = {
    'CvCaliphate': {1, 3, 6, 7, 9, 11, 13},
    'CvCity': set(range(19, 35)) | {36, 38, 40, 42, 44, 46, 48, 50, 52},
    'CvGame': {1, 3, 5, 6},
    'CvPlayer': set(range(1, 33, 2)),
    'CvPlayerAI': {1, 3, 5, 7},
    'CvUnitAI': {13, 14, 16, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 34},
}


def scalar_bound(n, vertical, number, module, lower, upper):
    if number in upper.get(module, ()):
        return edge(n + 1, vertical) - 1
    if number in lower.get(module, ()):
        return edge(n, vertical)
    return axis(n, vertical)  # Equality against an exact city/plot anchor.


def values():
    result = {}
    for key, value in BASE.VALUES.items():
        if key in ('CityNameManager.tCityMap', 'AIWars.tWarsMap'):
            continue
        module, leaf = key.split('.', 1)
        if key in ('Consts.tPatienceThreshold', 'Consts.tHire'):
            result[key] = value
        elif key in FOOTPRINT_KEYS:
            result[key] = tuple(p for point in value for p in footprint(point))
        elif key in ('Consts.tExceptions', 'Consts.tNormalAreasSubtract'):
            result[key] = tuple(tuple(p for point in ((plane,) if plane and isinstance(plane[0], int) else plane)
                                      for p in footprint(point))
                                for plane in value)
        elif key in BOX_KEYS:
            result[key] = boxes(value)
        elif key == 'UniquePowers.tRussianTopLeft':
            result[key] = corners(value)
        elif key == 'UniquePowers.tRussianBottomRight':
            result[key] = tuple(edge(n, i == 1) for i, n in enumerate(value))
        elif re.search(r'TL(?:_\d+)?$', key):
            result[key] = corners(value)
        elif re.search(r'BR(?:_\d+)?$', key):
            result[key] = corners(value, True)
        elif '.bound_' in key:
            number = int(leaf.split('_')[-1])
            result[key] = scalar_bound(value, number in PY_Y[module], number,
                                       module, PY_LOWER, PY_UPPER)
        elif '.range_' in key:
            # Correct the reference profile's obsolete 168-row loop to this map.
            result[key] = (0, HEIGHT) if key == 'RiseAndFall.range_4' else tuple(
                edge(n, key in RANGE_Y) for n in value)
        elif module == 'Barbs' and leaf.startswith('l') and len(value) == 4 and isinstance(value[0], int):
            result[key] = [axis(value[0]), axis(value[1], True)] + value[2:]
        elif key == 'Caliphate.REGIONS':
            result[key] = tuple((v[0],) + rectangle(v[1:]) for v in value)
        else:
            result[key] = coordinate(value)
    if NAME == 'Earth200x110':
        # Huge-only regional centres. Turns use the existing RFC calendar;
        # the fourth field is mutable founding-retry state, initially zero.
        result.update({
            # The old Libyan rectangle is entirely Saharan wasteland. Use the
            # open coastal approach west of the Nile instead.
            'Barbs.checkTurn.location_13': (104, 59),
            'Barbs.checkTurn.location_14': (110, 60),
            # The reference's early chariot rectangle has reversed x bounds.
            # Share the eastern limit of the following Near Eastern raid phase.
            'Barbs.checkTurn.location_60': (128, 78),
            'Barbs.lMerv': [135, 74, 101, 0],       # 600 BC, river oasis.
            'Barbs.lAnuradhapura': [150, 48, 114, 0],  # 400 BC, northern Sri Lanka.
            'Barbs.lPalembang': [164, 43, 191, 0],  # AD 700, southeast Sumatra.
            'Barbs.lGreatZimbabwe': [111, 27, 231, 0],  # AD 1100, inland cattle/gold belt.
        })
    return result


def native():
    result = {}
    for key, value in BASE.NATIVE.items():
        module, leaf = key.split('.', 1)
        if key == 'Caliphate.realmRegions':
            result[key] = [n for i in range(0, len(value), 5)
                           for n in (value[i],) + rectangle(value[i + 1:i + 5])]
        elif key in ('Crusades.regions', 'Arabia.egypt'):
            result[key] = [n for i in range(0, len(value), 4)
                           for n in rectangle(value[i:i + 4])]
        elif key in ('World.rome', 'World.mecca'):
            result[key] = [axis(n, i % 2 == 1) for i, n in enumerate(value)]
        elif 'iAmericanEdge' in key:
            result[key] = [edge(n + 1) - 1 for n in value]
        elif 'iAsianEdge' in key:
            result[key] = [edge(n) for n in value]
        elif key == 'Caliphate.capitalX':
            result[key] = [axis(n) for n in value]
        elif key == 'Caliphate.capitalY':
            result[key] = [axis(n, True) for n in value]
        else:
            number = int(leaf.split('_')[-1])
            vertical = (leaf.startswith('y_') or
                        (leaf.startswith('bound_') and number in NATIVE_Y[module]) or
                        (leaf.startswith('founding_') and number >= 3))
            if leaf.startswith('bound_'):
                result[key] = [scalar_bound(n, vertical, number, module, NATIVE_LOWER, NATIVE_UPPER)
                               for n in value]
            else:
                result[key] = [axis(n, vertical) for n in value]
    return result


def compact(planes, city_names=False):
    result, shared = [], {}
    xs = [min(123, int((x + .5) * 124 / WIDTH)) for x in range(WIDTH)]
    ys = [min(67, int((y + .5) * 68 / HEIGHT)) for y in range(HEIGHT)]
    for plane in planes:
        rows = tuple(tuple(plane[67 - ys[HEIGHT - 1 - y]][x] for x in xs)
                     for y in range(HEIGHT))
        if NAME == 'Earth200x110':
            # Cyprus gains a lowland beside its original summit cell. Keep
            # naming and AI geography on that land instead of the old sea grid.
            row = list(rows[HEIGHT - 1 - 65])
            for x in (114, 115):
                row[x] = 'Salamis' if city_names else plane[67 - 40][71]
            rows = rows[:HEIGHT - 1 - 65] + (tuple(row),) + rows[HEIGHT - 65:]
        if rows in shared:
            result.append(shared[rows])
            continue
        shared[rows] = len(result)
        default = Counter(n for row in rows for n in row).most_common(1)[0][0]
        spans = {}
        for y, row in enumerate(rows):
            x = 0
            while x < WIDTH:
                end = x
                while end + 1 < WIDTH and row[end + 1] == row[x]:
                    end += 1
                if row[x] != default:
                    spans.setdefault(row[x], []).append((y, x, end))
                x = end + 1
        result.append((default, tuple((n, tuple(runs)) for n, runs in sorted(spans.items()))))
    return tuple(result)


def write_data(path, entries):
    text = '# Generated by tools/generate_large_world.py. Python 2.4.\n'
    for key, value in entries.items():
        text += key + ' = ' + pprint.pformat(value, width=110, sort_dicts=False) + '\n'
    path.write_text(text, encoding='ascii')


# EU4-inspired strategic wastelands in RFC's compressed coordinates. These are
# regional barriers, including sparse/cleared cells inside a forest or desert;
# source vegetation and every minor river must not perforate the interiors.
# See docs/LargeWorld.md for the complete EU4 reference-to-region review.
WILDS = (
    ('Sahara: El Djouf, central and east', 'desert', ((47, 31), (49, 36), (55, 37), (63, 36), (69, 36), (70, 30), (65, 28), (57, 29), (51, 30))),
    ('Central Africa and northern Congo', 'rainforest', ((57, 24), (58, 28), (63, 30), (69, 29), (71, 26), (68, 21), (62, 21), (59, 23))),
    ('Guinea interior', 'rainforest', ((52, 26), (54, 29), (58, 29), (59, 26), (56, 24), (53, 25))),
    ('Imatong', 'rainforest', ((69, 25), (70, 28), (72, 28), (73, 25), (71, 24))),
    ('Urgoma', 'mountain', ((73, 25), (74, 28), (76, 27), (76, 24), (74, 23))),
    ('Namib', 'desert', ((61, 13), (61, 18), (64, 20), (65, 17), (64, 12))),
    ('Kalahari', 'desert', ((64, 14), (64, 19), (67, 21), (70, 19), (69, 15), (67, 13))),
    ('Western and eastern Amazonas', 'rainforest', ((27, 24), (28, 29), (33, 31), (39, 30), (42, 26), (40, 21), (34, 20), (29, 22))),
    ('Guyana interior', 'rainforest', ((34, 29), (35, 32), (39, 33), (42, 30), (40, 27), (37, 27))),
    ('Great Basin', 'desert', ((11, 45), (12, 50), (16, 51), (18, 48), (16, 44), (13, 43))),
    ('Columbia and Rocky Mountains', 'mountain', ((8, 51), (10, 58), (13, 60), (17, 56), (18, 51), (15, 47), (12, 48))),
    ('Alaska', 'boreal', ((3, 59), (5, 65), (10, 66), (14, 63), (12, 58), (7, 57))),
    ('Northwest Territories', 'boreal', ((13, 56), (14, 63), (19, 66), (24, 64), (24, 58), (19, 54))),
    ('Nunavut and Baffin', 'polar', ((23, 59), (25, 65), (31, 67), (39, 67), (38, 62), (31, 58))),
    ('Weagamow', 'boreal', ((21, 52), (22, 58), (28, 59), (30, 55), (27, 51))),
    ('Ungava', 'boreal', ((29, 55), (30, 62), (35, 64), (39, 61), (37, 55), (33, 53))),
    ('Adirondacks', 'mountain', ((28, 49), (28, 51), (30, 52), (31, 50), (30, 49))),
    ('Greenland', 'ice', ((37, 55), (40, 56), (43, 61), (42, 66), (38, 67), (36, 62))),
    ('Scandes', 'mountain', ((59, 57), (59, 62), (62, 65), (65, 63), (64, 58), (62, 56))),
    ('Alps west and east', 'mountain', ((56, 46), (58, 49), (62, 49), (64, 47), (61, 46))),
    ('Carpathians', 'mountain', ((65, 49), (67, 52), (70, 51), (70, 48), (68, 47))),
    ('Caucasus', 'mountain', ((74, 45), (76, 47), (80, 47), (81, 45), (78, 44))),
    ('High Atlas', 'mountain', ((49, 35), (51, 38), (54, 38), (56, 36), (53, 34))),
    ('Hakkari', 'mountain', ((76, 42), (77, 45), (80, 45), (81, 43), (79, 41))),
    ('Syrian desert', 'desert', ((76, 35), (77, 38), (80, 38), (81, 35), (79, 34))),
    ('Rub al Khali', 'desert', ((77, 29), (76, 32), (79, 35), (83, 34), (85, 31), (82, 28))),
    ('Nenets and Yamal', 'boreal', ((69, 61), (72, 66), (84, 67), (88, 63), (84, 59), (77, 59))),
    ('Western Siberia', 'boreal', ((81, 56), (81, 63), (86, 66), (92, 64), (93, 58), (87, 55))),
    ('Central Siberia', 'boreal', ((91, 58), (90, 65), (99, 67), (106, 65), (106, 59), (99, 57))),
    ('Eastern Siberia', 'boreal', ((105, 59), (105, 65), (115, 67), (123, 65), (122, 59), (115, 57))),
    ('Tian Shan', 'mountain', ((85, 47), (87, 51), (93, 51), (95, 48), (90, 46))),
    ('Pamir', 'mountain', ((85, 43), (85, 47), (88, 49), (91, 46), (89, 42))),
    ('Himalaya and Arunachal', 'mountain', ((89, 41), (91, 44), (97, 44), (102, 42), (101, 40), (96, 41), (92, 40))),
    ('Changtang', 'mountain', ((92, 44), (92, 47), (98, 48), (101, 46), (99, 43), (96, 43))),
    ('Qilian', 'mountain', ((96, 47), (97, 51), (100, 52), (103, 49), (102, 46))),
    ('Suleiman Range', 'mountain', ((84, 37), (85, 41), (88, 43), (90, 41), (88, 37), (86, 36))),
    ('Changbai', 'mountain', ((108, 50), (108, 53), (111, 55), (112, 52), (111, 49))),
    ('Arakan', 'mountain', ((96, 34), (97, 38), (99, 40), (100, 37), (98, 33))),
    ('Naga Hills', 'mountain', ((98, 39), (98, 41), (101, 42), (102, 40), (100, 38))),
    ('Gaoligong', 'mountain', ((99, 40), (100, 44), (103, 44), (104, 41), (102, 39))),
    ('Annamite Mountains', 'mountain', ((103, 33), (103, 37), (105, 39), (106, 36), (105, 32))),
    ('Borneo interior', 'rainforest', ((104, 25), (105, 29), (108, 29), (110, 27), (109, 24), (106, 24))),
    ('Papua interior', 'rainforest', ((114, 24), (116, 28), (120, 29), (123, 27), (122, 24), (118, 23))),
    ('Western and central Australia', 'desert', ((102, 13), (103, 20), (108, 23), (115, 22), (118, 17), (116, 11), (108, 10))),
)
# Huge World expands remote interiors, not Europe's settlement belt. These
# supplement the EU4-inspired inventory above; they are geographic abstractions,
# not claims that every tile was historically inaccessible. Coastal fringes,
# birth sites, the Sahel and the named route networks remain protected.
HUGE_WILDS = (
    ('Saharan interior extensions', 'desert', ((48, 32), (50, 37), (58, 37), (66, 37), (68, 31), (63, 29), (54, 29))),
    ('Congo southern interior', 'rainforest', ((60, 22), (62, 26), (68, 26), (70, 23), (68, 20), (63, 20))),
    ('Amazon southern interior', 'rainforest', ((28, 23), (31, 28), (39, 28), (42, 25), (40, 19), (34, 19))),
    ('Patagonian interior', 'desert', ((31, 5), (31, 12), (33, 14), (35, 12), (35, 7), (33, 5))),
    ('Canadian shield interior', 'boreal', ((16, 54), (18, 61), (26, 63), (33, 60), (35, 55), (29, 52), (23, 52))),
    ('Alaskan interior extensions', 'boreal', ((4, 57), (5, 64), (12, 65), (15, 61), (13, 56), (9, 55))),
    ('Siberian taiga interior', 'boreal', ((82, 56), (88, 61), (100, 63), (115, 62), (121, 58), (113, 55), (99, 55), (89, 55))),
    ('Gobi interior', 'desert', ((96, 49), (98, 53), (103, 54), (107, 52), (106, 49), (101, 48))),
    ('Australian interior extensions', 'desert', ((103, 12), (103, 21), (110, 24), (116, 22), (118, 17), (116, 10), (109, 10))),
)
# Open strategic routes through the surrounding barriers. These are traversable
# corridors, not prebuilt roads. Coordinates follow RFC's compressed projection.
CORRIDORS = (
    ((53, 28), (54, 32), .55), ((54, 32), (55, 37), .55), # western oasis route
    ((60, 28), (61, 33), .55), ((61, 33), (60, 37), .55), # Djado/Fezzan route
    ((69, 24), (69, 37), .85),                            # Nile
    ((73, 30), (75, 37), .65), ((75, 37), (77, 41), .65), # western Arabia/Levant
    ((78, 38), (86, 42), .65),                           # Persia
    ((83, 47), (90, 49), .6), ((90, 49), (102, 49), .6), # northern Silk Road
    ((90, 44), (99, 45), .55),                           # southern Tarim rim
    ((86, 41), (90, 40), .6), ((90, 40), (98, 37), .65), # Khyber/Ganges/Bengal
    ((25, 18), (28, 29), .65),                           # Andean approaches
    ((28, 27), (34, 27), .55), ((34, 27), (42, 28), .55),# Amazon trunk
    ((60, 23), (65, 23), .6), ((65, 23), (69, 24), .6), # lower Congo/lakes
    ((11, 48), (31, 48), .7),                            # southern Canada
    ((76, 54), (110, 54), .7),                           # southern Siberia
)

# Named route networks, not a guarantee that every coastline is connected.
# Waypoints use reference-map coordinates. Short mountain passes may be opened
# where the enlarged source peaks otherwise sever a documented land route.
HISTORICAL_ROUTES = (
    ('western trans-Saharan', ((51, 36), (54, 32), (53, 27))),
    ('Fezzan-Kanem', ((60, 38), (61, 33), (62, 28))),
    ('Nile', ((68, 35), (69, 30), (69, 25))),
    ('Arabian incense route', ((77, 31), (76, 34), (75, 37), (76, 41))),
    ('Persia-Bactria', ((79, 41), (83, 42), (86, 45))),
    ('western Alpine pass', ((59, 47), (58, 48), (58, 49))),
    ('Brenner approach', ((60, 47), (61, 48), (62, 49))),
    ('Caucasus northern access', ((76, 45), (77, 47), (77, 49))),
    ('northern Tarim and Hexi', ((86, 45), (90, 48), (95, 48), (99, 47), (102, 47), (106, 46))),
    ('southern Tarim', ((90, 48), (90, 45), (95, 45), (99, 47))),
    ('Khyber and Ganges', ((86, 45), (87, 41), (90, 40), (95, 38))),
    ('Bengal-Burma-Yunnan', ((95, 38), (98, 37), (99, 35), (102, 40))),
    ('mainland Southeast Asia', ((99, 35), (102, 34), (103, 36), (103, 38))),
    ('Congo river and lake approaches', ((60, 23), (64, 25), (67, 24), (70, 23))),
    ('Zambezi', ((64, 20), (68, 19), (72, 19))),
    ('Amazon river', ((28, 27), (34, 27), (39, 27))),
    ('Andean north-south', ((25, 29), (26, 25), (28, 20), (30, 15))),
    ('Canadian southern route', ((10, 52), (16, 50), (22, 50), (30, 48))),
    ('southern Siberia', ((76, 54), (90, 54), (101, 54), (113, 54))),
)
HUGE_ROUTES = (
    ('Tibetan valleys and eastern approaches', ((95, 43), (97, 43), (100, 42), (100, 40))),
    ('Tibet-Nepal-Ganges', ((95, 43), (94, 42), (94, 40), (93, 39))),
    ('southern Andes and central Chile', ((30, 15), (30, 13), (30, 10), (31, 8))),
    ('central Andes crossing to the Pampas', ((30, 13), (32, 13), (35, 12))),
    ('Alberta eastern foothills', ((15, 55), (17, 53), (18, 52))),
    ('Great Basin northern passes', ((13, 48), (15, 49), (16, 50), (18, 49))),
    ('central Andean plateau access', ((28, 23), (31, 22), (33, 20))),
)
ROUTE_STEPS = tuple((dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy)
SHARED_EDGE_ROUTES = False


def open_routes(plots):
    """Protect connected, narrow paths; avoid water and prefer existing passes."""
    protected, opened_peaks = set(), set()
    def is_land(pos):
        return pos in plots and 'PlotType=3' not in plots[pos] and not any('FEATURE_ICE' in f for f in plots[pos])
    def snap(point):
        center = (axis(point[0]), axis(point[1], True))
        choices = [p for p in plots if is_land(p) and max(abs(p[0]-center[0]), abs(p[1]-center[1])) <= 2]
        if not choices:
            raise ValueError('Route waypoint has no nearby land: ' + str(point))
        return min(choices, key=lambda p: ((p[0]-center[0])**2+(p[1]-center[1])**2, 'PlotType=0' in plots[p], p))
    for name, waypoints in HISTORICAL_ROUTES:
        for a, b in zip(waypoints, waypoints[1:]):
            start, end = snap(a), snap(b)
            queue, costs, previous = [(0, start)], {start: 0}, {start: None}
            while queue:
                cost, pos = heapq.heappop(queue)
                if cost != costs[pos]:
                    continue
                if pos == end:
                    break
                x, y = pos
                for dx, dy in ROUTE_STEPS:
                    neighbor = (x + dx, y + dy)
                    if not is_land(neighbor):
                        continue
                    if (SHARED_EDGE_ROUTES and dx and dy and
                            (is_land((x + dx, y)) or is_land((x, y + dy)))):
                        # Follow land around corners. Diagonal-only isthmuses
                        # between water cells still need the normal Civ4 step.
                        continue
                    sx, sy = (neighbor[0]+.5)*124/WIDTH, (neighbor[1]+.5)*68/HEIGHT
                    if line_distance(sx, sy, a, b) > 3:
                        continue
                    step = 12 if 'PlotType=0' in plots[neighbor] else 1
                    score = cost + step
                    if score < costs.get(neighbor, float('inf')):
                        costs[neighbor], previous[neighbor] = score, pos
                        heapq.heappush(queue, (score, neighbor))
            if end not in previous:
                raise ValueError('Disconnected historical route: ' + name)
            pos = end
            while pos is not None:
                protected.add(pos)
                fields = plots[pos]
                if 'PlotType=0' in fields:
                    fields[fields.index('PlotType=0')] = 'PlotType=1'
                    opened_peaks.add(pos)
                pos = previous[pos]
    print('Historical route tiles: %d; mountain pass tiles opened: %d' % (len(protected), len(opened_peaks)))
    return protected


def ocean_ice(plots, origins):
    """Conservative permanent pack ice, not the seasonal winter maximum."""
    added = 0
    for pos, fields in plots.items():
        if 'PlotType=3' not in fields:
            continue
        x, y = origins[pos]
        arctic = y >= 66 or (y >= 64 and (x <= 37 or x >= 72)) or (y >= 62 and 20 <= x <= 38)
        # Tierra del Fuego reaches source row 3 in this compressed projection.
        # Explicitly preserve its southern sea lane rather than treating every
        # low row as equally far south. Only small Weddell/Ross fringes extend.
        cape_horn = 28 <= x <= 36 and 1 <= y <= 4
        antarctic = not cape_horn and (y <= 1 or (y <= 2 and (39 <= x <= 44 or 110 <= x <= 123)))
        if not (arctic or antarctic) or any('FEATURE_ICE' in f for f in fields):
            continue
        fields[:] = [f for f in fields if not f.startswith('FeatureType=')]
        fields.append('FeatureType=FEATURE_ICE, FeatureVariety=0')
        added += 1
    print('Additional permanent ocean ice:', added)


def line_distance(x, y, start, end):
    ax, ay = start
    dx, dy = end[0] - ax, end[1] - ay
    t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
    return ((x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2) ** .5


def in_polygon(x, y, vertices):
    inside = False
    ax, ay = vertices[-1]
    for bx, by in vertices:
        if ((bx - ax) * (y - ay) == (by - ay) * (x - ax) and
                min(ax, bx) <= x <= max(ax, bx) and min(ay, by) <= y <= max(ay, by)):
            return True
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
            inside = not inside
        ax, ay = bx, by
    return inside


def barrier_biome(fields, kind):
    if kind in ('desert', 'rainforest', 'boreal', 'polar', 'ice'):
        return True
    if kind == 'mountain':
        # Retain lowland approaches; existing peaks already form most ranges.
        return 'PlotType=1' in fields or 'TerrainType=TERRAIN_SNOW' in fields
    raise ValueError('Unknown wilderness biome: ' + kind)


# Reviewed off-channel alluvial fringes, in the reference projection. Plains
# represent seasonally watered soils/dry grazing here, not a universal fertile
# halo around rivers. The Nile's narrow valley is already represented by its
# river-adjacent floodplains; its outer copies retain underlying desert.
FLOODPLAIN_FRINGES = {
    (53, 31): 'Niger inland delta', (54, 31): 'Niger inland delta',
    (76, 38): 'Mesopotamian alluvium', (76, 41): 'Upper Mesopotamian steppe',
    (77, 38): 'Mesopotamian alluvium', (77, 39): 'Mesopotamian alluvium',
    (77, 40): 'Mesopotamian alluvium',
    (87, 39): 'Indus alluvial fringe',
}


def correct_floodplains(plots, origins):
    """Remove invalid features; preserve base terrain except reviewed fringes."""
    valleys, corrected = set(), Counter()
    for (x, y), fields in plots.items():
        if not any(f.startswith('FeatureType=FEATURE_FLOOD_PLAINS') for f in fields):
            continue
        valleys.add((x, y))
        river = ('isNOfRiver' in fields or 'isWOfRiver' in fields or
                 'isNOfRiver' in plots.get((x, y + 1), ()) or
                 'isWOfRiver' in plots.get(((x - 1) % WIDTH, y), ()))
        if river and 'PlotType=2' in fields and 'TerrainType=TERRAIN_DESERT' in fields:
            continue
        fields[:] = [f for f in fields if not f.startswith('FeatureType=FEATURE_FLOOD_PLAINS')]
        if ('PlotType=2' in fields and 'TerrainType=TERRAIN_DESERT' in fields
                and origins[x, y] in FLOODPLAIN_FRINGES):
            fields[fields.index('TerrainType=TERRAIN_DESERT')] = 'TerrainType=TERRAIN_PLAINS'
        terrain = next(f.split('=')[1] for f in fields if f.startswith('TerrainType='))
        corrected[terrain] += 1
    print('Off-river/invalid floodplains replaced:', dict(corrected))
    return valleys


def refine_mountains(plots, source):
    """Reconstruct Huge relief instead of multiplying rectangular peak cells.

    Keep a summit in each original peak cell, but give enlarged outer copies
    hill shoulders where the continuous source relief falls away. No new peaks
    or lowland edits: the original range cores and isolated summits survive.
    """
    summits = {point: (axis(point[0]), axis(point[1], True))
               for point, fields in source.items() if 'PlotType=0' in fields}
    cores = set(summits.values())
    # Link adjacent source summits before trimming. This keeps continuous
    # ridges continuous rather than leaving spaced, isolated peak anchors.
    for (sx, sy), (ax, ay) in summits.items():
        for dx, dy in ((1, 0), (0, 1), (1, 1), (-1, 1)):
            end = summits.get((sx + dx, sy + dy))
            if end is None:
                continue
            bx, by = end
            steps = max(abs(bx - ax), abs(by - ay))
            cores.update((round(ax + (bx - ax) * n / steps),
                          round(ay + (by - ay) * n / steps))
                         for n in range(steps + 1))
    shoulders = set()
    for (x, y), fields in plots.items():
        if 'PlotType=0' not in fields:
            continue
        if (x, y) in cores:
            continue
        fx, fy = (x + .5) * 124 / WIDTH - .5, (y + .5) * 68 / HEIGHT - .5
        left, bottom = math.floor(fx), math.floor(fy)
        support = 0.
        for dx in (0, 1):
            for dy in (0, 1):
                point = ((left + dx) % 124, max(0, min(67, bottom + dy)))
                if 'PlotType=0' in source[point]:
                    support += (1 - abs(fx - left - dx)) * (1 - abs(fy - bottom - dy))
        # Trim the outer quarter of the interpolated peak field; summit
        # anchors and their links take precedence over this shoulder threshold.
        if support < .75:
            fields[fields.index('PlotType=0')] = 'PlotType=1'
            shoulders.add((x, y))
    print('Enlarged mountain edge tiles changed to foothills:', len(shoulders))
    return shoulders


def refine_starts(plots, source, profile_values):
    """Keep births beside their source rivers/shores after edge-based scaling."""
    def river(grid, point):
        x, y = point
        return any(flag in grid.get(pos, ()) for pos, flag in (
            (point, 'isNOfRiver'), (point, 'isWOfRiver'),
            ((x, y + 1), 'isNOfRiver'), ((x - 1, y), 'isWOfRiver')))

    def shore(grid, point, width, radius=1):
        x, y = point
        return any('PlotType=3' in grid.get(((x + dx) % width, y + dy), ())
                   for dx in range(-radius, radius + 1) for dy in range(-radius, radius + 1)
                   if dx or dy)

    resolved = {}
    def resolve(point, settlement=False):
        if not point:
            return point
        if point in resolved:
            return resolved[point]
        center = (axis(point[0]), axis(point[1], True))
        needs_river, needs_shore = river(source, point), shore(source, point, 124)
        choices = []
        for pos in footprint(point):
            fields = plots[pos]
            if not ('PlotType=1' in fields or 'PlotType=2' in fields):
                continue
            if any('_IMPASSABLE' in f or 'FEATURE_ICE' in f for f in fields):
                continue
            if needs_river and not river(plots, pos):
                continue
            if needs_shore and not shore(plots, pos, WIDTH):
                # A one-cell estuary can become two cells wide. Historical
                # cities prefer direct coast, but retain their river when the
                # two edges cannot share a tile in this source footprint.
                if not settlement or not shore(plots, pos, WIDTH, radius=2):
                    continue
            choices.append(pos)
        if not choices:
            raise ValueError('No matching river/shore birth tile in source footprint: ' + str(point))
        result = min(choices, key=lambda p: (needs_shore and not shore(plots, p, WIDTH),
                     (p[0] - center[0]) ** 2 + (p[1] - center[1]) ** 2, p))
        resolved[point] = result
        return result

    for key in ('Consts.tCapitals', 'Consts.tReserveCapitals'):
        profile_values[key] = tuple(resolve(point) for point in BASE.VALUES[key])
    # These setup routines can replace the ordinary capital table at runtime.
    for key in ('NativeAmerica.configureRegions.capital_1', 'NativeAmerica.configureRegions.capital_2',
                'Korea.setup.capital_1', 'Korea.setup.capital_2', 'Korea.setup.capital_3'):
        profile_values[key] = resolve(BASE.VALUES[key])
    # Historical city foundations suffer the same edge/center mismatch as
    # civilization births. Preserve their dates and owners while moving locally.
    for key, value in BASE.VALUES.items():
        if key.startswith('Barbs.l') and len(value) == 4 and isinstance(value[0], int):
            profile_values[key] = list(resolve(tuple(value[:2]), settlement=True)) + list(value[2:])
    print('Birth/setup river and shore corrections:',
          {point: pos for point, pos in resolved.items()
           if pos != (axis(point[0]), axis(point[1], True))})


def refine_historic_regions(plots):
    """Small authored lowlands inside overly broad enlarged mountain masks."""
    lowlands = {
        'Sichuan basin': ((161, 67), (162, 67), (162, 68), (163, 68), (164, 68), (165, 68)),
        'Wei and middle Yellow River valleys': ((162, 70), (163, 70), (164, 70), (165, 70)),
        'Red River delta': ((163, 60), (164, 60)),
    }
    protected = set()
    for name, points in lowlands.items():
        for pos in points:
            fields = plots[pos]
            old = next(f for f in fields if f.startswith('PlotType='))
            fields[fields.index(old)] = 'PlotType=2'
            protected.add(pos)
        print(name + ' protected lowland tiles:', len(points))
    # A short distributary joins the existing south-flowing Red River at
    # corner (163,60) to the coast at (165,60). The enlarged delta must not
    # separate its historical city tile from both river and coastal access.
    for pos in ((163, 60), (164, 60)):
        fields = plots[pos]
        fields[:] = [f for f in fields if f != 'isNOfRiver' and not f.startswith('RiverWEDirection=')]
        fields.extend(('isNOfRiver', 'RiverWEDirection=1'))
    # The source reduces Cyprus to one uninhabitable summit, while its copper
    # atlas marker lies on Syria. Retain an upland and add one coastal lowland.
    for pos, relief in (((114, 65), 2), ((115, 65), 1)):
        fields = plots[pos]
        fields[:] = [f for f in fields if not f.startswith(('PlotType=', 'TerrainType=', 'FeatureType='))]
        fields.extend(('TerrainType=TERRAIN_PLAINS', 'PlotType=%d' % relief))
        if relief == 1:
            fields.append('FeatureType=FEATURE_FOREST, FeatureVariety=0')
        protected.add(pos)
    return protected


def make_map(profile_values):
    source = (MOD / 'PublicMaps/Start 1 - 3000 BC.CivBeyondSwordWBSave').read_text(encoding='utf-8-sig')
    header = source.split('BeginPlot', 1)[0]
    blocks, placements = {}, {}
    for block in re.findall(r'BeginPlot\s*\n(.*?)EndPlot', source, re.S):
        x, y = map(int, re.search(r'x=(\d+),y=(\d+)', block).groups())
        payload = [m.group(0).strip() for m in re.finditer(r'Begin(City|Unit)\b.*?End\1', block, re.S)]
        if payload:
            placements[axis(x), axis(y, True)] = payload
        block = re.sub(r'\s*Begin(?:City|Unit)\b.*?End(?:City|Unit)', '', block, flags=re.S)
        fields = [s.strip() for s in block.splitlines() if s.strip()]
        blocks[x, y] = fields[1:]
    def plot_type(fields):
        return int(next(s.split('=')[1] for s in fields if s.startswith('PlotType=')))
    def usable(fields):
        return plot_type(fields) in (1, 2) and not any('FEATURE_ICE' in s for s in fields)
    baseline = sum(usable(fields) for fields in blocks.values())
    plots, origins = {}, {}
    for x in range(WIDTH):
        for y in range(HEIGHT):
            sx, sy = min(123, int((x + .5) * 124 / WIDTH)), min(67, int((y + .5) * 68 / HEIGHT))
            fields = []
            for s in blocks[sx, sy]:
                # Large World resources are authored independently, after all
                # terrain, routes and sea ice. Never inherit a source deposit.
                if s.startswith('BonusType='):
                    continue
                # Improvements are retained once, not multiplied by resizing.
                if s.startswith('ImprovementType=') and (x, y) != (axis(sx), axis(sy, True)):
                    continue
                if s.startswith(('TeamReveal=', 'Player')):
                    continue
                # Rivers run on cell edges: extend their length but never their width.
                # NOfRiver means the plot is NORTH of its south-edge river.
                if (s == 'isNOfRiver' or s.startswith('RiverWEDirection=')) and y != edge(sy, True):
                    continue
                if (s == 'isWOfRiver' or s.startswith('RiverNSDirection=')) and x != edge(sx + 1) - 1:
                    continue
                fields.append(s)
            plots[x, y], origins[x, y] = fields, (sx, sy)

    shoulders = refine_mountains(plots, blocks) if NAME == 'Earth200x110' else set()
    historic_sites = refine_historic_regions(plots) if NAME == 'Earth200x110' else set()
    # The coarse Amazon mask overlapped the Bolivian highlands. Keep this small
    # authored Altiplano belt as open upland terrain, with its source relief;
    # it must not turn Potosi and the plateau valleys into tropical wilderness.
    uplands = set()
    if NAME == 'Earth200x110':
        # Fine relief on the enlarged Greek projection. Keep Athens (108,67)
        # flat, distinguish Attic uplands and one Peloponnesian valley, and
        # give Crete a broken upland spine with three usable lowland tiles.
        for pos, relief in (((109, 68), 1), ((109, 66), 1), ((106, 65), 2),
                            ((110, 63), 1), ((111, 64), 1), ((112, 63), 1)):
            fields = plots[pos]
            old = next(f for f in fields if f.startswith('PlotType='))
            fields[fields.index(old)] = 'PlotType=%d' % relief
        # The source Venice/Aquileia cell is hills, interrupting the eastern
        # lowland. Flatten only its enlarged footprint, below the Alpine belt.
        for pos in footprint((61, 47)):
            fields = plots[pos]
            if 'PlotType=1' in fields:
                fields[fields.index('PlotType=1')] = 'PlotType=2'
        for point in ((31, 22), (32, 22), (32, 21), (33, 21), (32, 20), (33, 20)):
            for pos in footprint(point):
                fields = plots[pos]
                if 'PlotType=3' in fields:
                    continue
                terrain = next(f for f in fields if f.startswith('TerrainType='))
                fields[fields.index(terrain)] = 'TerrainType=TERRAIN_PLAINS'
                fields[:] = [f for f in fields if not f.startswith('FeatureType=FEATURE_JUNGLE')]
                uplands.add(pos)
        print('Andean plateau terrain tiles:', len(uplands))
    route_sites = open_routes(plots)
    ocean_ice(plots, origins)
    if NAME == 'Earth200x110':
        refine_starts(plots, blocks, profile_values)

    anchors = list(profile_values['Consts.tCapitals'])
    for key, value in profile_values.items():
        if key.startswith('Barbs.l') and len(value) == 4 and isinstance(value[0], int):
            anchors.append(tuple(value[:2]))
    candidates = []
    for (x, y), fields in plots.items():
        if not usable(fields):
            continue
        if any(max(abs(x - ax), abs(y - ay)) <= 2 for ax, ay in anchors):
            continue
        sx, sy = origins[x, y]
        if any(line_distance(sx, sy, a, b) <= width for a, b, width in CORRIDORS):
            continue
        # Keep shorelines traversable; do not turn a peninsula into a wall.
        if any(plot_type(plots.get(((x + dx) % WIDTH, y + dy), ['PlotType=3'])) == 3
               for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))):
            continue
        for name, kind, vertices in WILDS:
            # Mountain polygons use destination-cell centers, avoiding another
            # source-sized staircase. Retain the newly authored foothills.
            px, py = sx, sy
            if kind == 'mountain' and NAME == 'Earth200x110':
                if (x, y) in shoulders:
                    continue
                px, py = (x + .5) * 124 / WIDTH - .5, (y + .5) * 68 / HEIGHT - .5
            if in_polygon(px, py, vertices) and barrier_biome(fields, kind):
                candidates.append((x, y, name))
                break
    # Births and historical settlement sites retain access. Villages inside a
    # wasteland move to accessible fringes; resources are authored afterward.
    protected = set(placements) | route_sites | uplands | historic_sites
    for key in FOOTPRINT_KEYS - {'Victory.tMediterraneanExceptions', 'RiseAndFall.conquerorBlockedPlots'}:
        protected.update(profile_values[key])
    event_sites = set(anchors)
    candidate_sites = {(x, y) for x, y, region in candidates}
    safe = {pos for pos, fields in plots.items() if usable(fields) and pos not in candidate_sites and
            any(plot_type(plots.get(((pos[0] + dx) % WIDTH, pos[1] + dy), ['PlotType=3'])) == 3
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)))}
    # Only connected open land is a destination: a protected capital's small
    # clearing inside a wasteland must not count as its own access route.
    queue = deque(safe)
    while queue:
        x, y = queue.popleft()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                neighbor = ((x + dx) % WIDTH, y + dy)
                if (neighbor in plots and neighbor not in safe and neighbor not in candidate_sites
                        and usable(plots[neighbor])):
                    safe.add(neighbor)
                    queue.append(neighbor)
    for site in sorted(event_sites):
        protected.add(site)
        if not usable(plots[site]):
            continue
        queue, previous = deque([site]), {site: None}
        reached = None
        while queue:
            pos = queue.popleft()
            if pos in safe:
                reached = pos
                break
            x, y = pos
            for neighbor in (((x + dx) % WIDTH, y + dy)
                             for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dx or dy):
                if neighbor not in previous and neighbor in plots and usable(plots[neighbor]):
                    previous[neighbor] = pos
                    queue.append(neighbor)
        if reached is None:
            raise ValueError('No land access to historical site at ' + str(site))
        while reached is not None:
            protected.add(reached)
            safe.add(reached)
            reached = previous[reached]
    candidates = [entry for entry in candidates if entry[:2] not in protected]
    barrier_sites = {(x, y) for x, y, region in candidates}
    # Include newly opened historical access paths when relocating resources.
    accessible = safe | protected
    relocations = []
    for pos, fields in plots.items():
        if pos not in barrier_sites:
            continue
        for field in list(fields):
            if not field.startswith('ImprovementType='):
                continue
            prefix = field.split('=')[0] + '='
            destinations = []
            for target, target_fields in plots.items():
                if target not in accessible or target in barrier_sites or target in placements or not usable(target_fields):
                    continue
                if any(s.startswith(prefix) for s in target_fields):
                    continue
                dx, dy = abs(target[0] - pos[0]), abs(target[1] - pos[1])
                distance = min(dx, WIDTH - dx) ** 2 + dy ** 2
                if distance > 22 ** 2:
                    continue
                if (origins[pos][0] < 44) != (origins[target][0] < 44):
                    continue
                destinations.append((distance, target))
            if not destinations:
                raise ValueError('No nearby compatible fringe tile for %s at %s' % (field, pos))
            target = min(destinations)[1]
            target_fields = plots[target]
            target_fields.append(field)
            fields.remove(field)
            relocations.append((field, pos, target))
    before = sum(usable(fields) for fields in plots.values())
    barriers = Counter()
    kinds = dict((name, kind) for name, kind, polygon in WILDS)
    for x, y, region in candidates:
        fields = plots[x, y]
        terrain = next(s for s in fields if s.startswith('TerrainType='))
        kind = kinds[region]
        replacement = {'desert': 'TERRAIN_DESERT', 'ice': 'TERRAIN_SNOW', 'polar': 'TERRAIN_SNOW'}.get(kind, terrain.split('=')[1])
        if kind == 'rainforest' and replacement != 'TERRAIN_MARSH':
            replacement = 'TERRAIN_GRASS'
        fields[fields.index(terrain)] = 'TerrainType=' + replacement + '_IMPASSABLE'
        fields[:] = [s for s in fields if not s.startswith('FeatureType=')]
        if kind == 'mountain':
            fields[fields.index(next(s for s in fields if s.startswith('PlotType=')))] = 'PlotType=0'
        else:
            # Normal vegetation/ice remains the gameplay feature. The DLL adds
            # FEATURE_IMPASSABLE as display-only fog over impassable terrain.
            feature = None
            if replacement == 'TERRAIN_SNOW':
                feature = 'ICE'
            elif replacement == 'TERRAIN_MARSH':
                feature = 'MUD'
            elif kind == 'rainforest':
                feature = 'JUNGLE'
            elif kind == 'boreal':
                feature = 'FOREST'
            if feature:
                fields.append('FeatureType=FEATURE_%s, FeatureVariety=%d' % (feature, int(feature == 'FOREST')))
        barriers[region] += 1
    # Every major birth must remain a legal land start, including future civs.
    for pos in profile_values['Consts.tCapitals']:
        if not usable(plots[pos]) or any('_IMPASSABLE' in s for s in plots[pos]):
            raise ValueError('Invalid civilization start: ' + str(pos))
    # Resource history is a separate final authoring pass. It sees the finished
    # geography, including opened mountain passes and permanent ocean ice.
    review = NAME == 'Earth200x110'
    valleys = correct_floodplains(plots, origins) if review else set()
    from large_world_resources import place_resources
    event_fisheries = ()
    if review:
        # These two founding events install fishing boats on an existing bonus.
        # Reserve their coastal beds before placing the general resource atlas.
        event_fisheries = (
            ('CRAB', 'Gadir crab', profile_values['Barbs.plot_1']),
            ('CLAM', 'Karalis shellfish', profile_values['Barbs.plot_2']),
        )
    place_resources(plots, origins, axis, DATA, NAME, ATLAS_NAME,
                    review=review, protected=protected, valleys=valleys,
                    event_fisheries=event_fisheries,
                    settlements=resource_free_settlements(profile_values) if review else ())
    for old, new in [('grid width=124', 'grid width=%d' % WIDTH), ('grid height=68', 'grid height=%d' % HEIGHT),
                     ('num plots written=8432', 'num plots written=%d' % (WIDTH * HEIGHT)),
                     ('Description=TXT_KEY_RHYES_WB_DESC', 'Description=' + DESCRIPTION)]:
        header = header.replace(old, new)
    # Explicit initial starts; the existing RiseAndFall setup supplies their units.
    if NAME == 'Earth200x110':
        header = re.sub(r'Calendar=CALENDAR_DEFAULT[ \t]*', 'Calendar=CALENDAR_DEFAULT\n\tSpeed=GAMESPEED_XL', header, count=1)
    players = re.findall(r'BeginPlayer\s*\n.*?EndPlayer', header, re.S)
    for i, player in enumerate(players):
        changed = re.sub(r'(StartingX=)(\d+)', lambda m: m[1] + str(axis(int(m[2]))), player)
        changed = re.sub(r'(StartingY=)(\d+)', lambda m: m[1] + str(axis(int(m[2]), True)), changed)
        if i < 4:
            x, y = profile_values['Consts.tCapitals'][i]
            changed = changed.replace('EndPlayer', '\tStartingX=%d\n\tStartingY=%d\nEndPlayer' % (x, y))
        header = header.replace(player, changed, 1)
    output = [header.rstrip() + '\n']
    for (x, y), fields in plots.items():
        output.append('BeginPlot\n\tx=%d,y=%d\n\t%s\nEndPlot\n' %
                      (x, y, '\n\t'.join(fields + placements.get((x, y), []))))
    output.append('BeginSign\nEndSign\n' if 'BeginSign' in source else '')
    TARGET.write_text(''.join(output), encoding='utf-8', newline='\n')
    print('Reference passable land: %d; enlarged before barriers: %d; final: %d (%+.2f%%)' %
          (baseline, before, before - len(candidates), 100 * ((before - len(candidates)) / baseline - 1)))
    print('Impassable additions:', dict(barriers))
    print('Improvements moved to nearby fringes:', len(relocations))
    if relocations:
        print('Longest relocation: %.1f tiles' % max(((a[0]-b[0])**2+(a[1]-b[1])**2)**.5
                                                    for field, a, b in relocations))
    return {s.split('=')[1] for fields in plots.values() for s in fields if s.startswith('TerrainType=') and '_IMPASSABLE' in s}


def terrain_xml(used):
    path = MOD / 'Assets/XML/Terrain/CIV4TerrainInfos.xml'
    text = path.read_text(encoding='utf-8')
    # Keep existing appended terrain IDs stable when a map stops using a biome.
    used = set(used) | set(re.findall(r'<Type>(TERRAIN_[A-Z]+_IMPASSABLE)</Type>', text))
    text = re.sub(r'\s*<TerrainInfo>\s*<Type>TERRAIN_[A-Z]+_IMPASSABLE</Type>.*?</TerrainInfo>', '', text, flags=re.S)
    additions = []
    for name in sorted(used):
        original = name.removesuffix('_IMPASSABLE')
        block = re.search(r'<TerrainInfo>\s*<Type>' + original + r'</Type>.*?</TerrainInfo>', text, re.S)[0]
        block = block.replace('<Type>' + original + '</Type>', '<Type>' + name + '</Type>')
        block = re.sub(r'<Description>.*?</Description>', '<Description>TXT_KEY_ARFC_IMPASSABLE_LAND</Description>', block)
        block = re.sub(r'<Civilopedia>.*?</Civilopedia>', '<Civilopedia>TXT_KEY_ARFC_IMPASSABLE_LAND_PEDIA</Civilopedia>', block)
        block = block.replace('<bImpassable>0', '<bImpassable>1').replace('<bFound>1', '<bFound>0')
        block = block.replace('<bFoundCoast>1', '<bFoundCoast>0').replace('<bFoundFreshWater>1', '<bFoundFreshWater>0')
        block = re.sub(r'<iYield>\d+</iYield>', '<iYield>0</iYield>', block)
        additions.append('\t\t' + block + '\n')
    text = text.replace('\t</TerrainInfos>', ''.join(additions) + '\t</TerrainInfos>')
    path.write_text(text, encoding='utf-8', newline='\n')


def feature_xml():
    """One display-only fog feature; normal plot features remain unchanged."""
    path = MOD / 'Assets/XML/Terrain/CIV4FeatureInfos.xml'
    text = path.read_text(encoding='utf-8')
    retired = 'DEEP_DESERT|DEEP_JUNGLE|REMOTE_FOREST|FROZEN_WILDERNESS|IMPASSABLE'
    text = re.sub(r'\s*<FeatureInfo>\s*<Type>FEATURE_(?:' + retired + r')</Type>.*?</FeatureInfo>', '', text, flags=re.S)
    block = re.search(r'<FeatureInfo>\s*<Type>FEATURE_FALLOUT</Type>.*?</FeatureInfo>', text, re.S)[0]
    for tag, value in (('Type', 'FEATURE_IMPASSABLE'), ('Description', 'TXT_KEY_ARFC_IMPASSABLE_LAND'),
                       ('Civilopedia', 'TXT_KEY_ARFC_IMPASSABLE_LAND_PEDIA'), ('ArtDefineTag', 'ART_DEF_FEATURE_IMPASSABLE')):
        block = re.sub('<' + tag + '>.*?</' + tag + '>', '<' + tag + '>' + value + '</' + tag + '>', block, flags=re.S)
    for tag in ('YieldChanges', 'RiverYieldChange', 'HillsYieldChange', 'FootstepSounds', 'TerrainBooleans'):
        block = re.sub(r'<' + tag + r'(?:\s*/>|>.*?</' + tag + r'>)', '<' + tag + '/>', block, flags=re.S)
    for tag in ('iAppearance', 'iDisappearance', 'iGrowth', 'iTurnDamage', 'iHealthPercent', 'iDefense',
                'bNoCoast', 'bNoRiver', 'bNoAdjacent', 'bRequiresFlatlands', 'bRequiresRiver', 'bAddsFreshWater'):
        block = re.sub('<' + tag + '>.*?</' + tag + '>', '<' + tag + '>0</' + tag + '>', block)
    for tag in ('bImpassable', 'bNoCity', 'bNoImprovement', 'bNukeImmune'):
        block = re.sub('<' + tag + '>.*?</' + tag + '>', '<' + tag + '>1</' + tag + '>', block)
    block = re.sub('<iAdvancedStartRemoveCost>.*?</iAdvancedStartRemoveCost>', '<iAdvancedStartRemoveCost>-1</iAdvancedStartRemoveCost>', block)
    text = re.sub(r'\s*</FeatureInfos>', '\n\t\t' + block + '\n\t</FeatureInfos>', text)
    path.write_text(text, encoding='utf-8', newline='\n')
    path = MOD / 'Assets/XML/Art/CIV4ArtDefines_Feature.xml'
    text = path.read_text(encoding='utf-8')
    text = re.sub(r'\s*<FeatureArtInfo>\s*<Type>ART_DEF_FEATURE_(?:DEEP_DESERT|DEEP_JUNGLE|FROZEN_WILDERNESS|IMPASSABLE)</Type>.*?</FeatureArtInfo>', '', text, flags=re.S)
    block = re.search(r'<FeatureArtInfo>\s*<Type>ART_DEF_FEATURE_FALLOUT</Type>.*?</FeatureArtInfo>', text, re.S)[0]
    block = block.replace('ART_DEF_FEATURE_FALLOUT', 'ART_DEF_FEATURE_IMPASSABLE')
    block = re.sub(r'<ModelFile>.*?</ModelFile>', '<ModelFile>Art/Terrain/Features/Wasteland/ImpassableFog.nif</ModelFile>', block)
    button = ',Art/Interface/Buttons/BaseTerrain/Desert.dds,Art/Interface/Buttons/BaseTerrain_TerrainFeatures_Atlas.dds,2,1'
    for tag in ('Button', 'VarietyButton'):
        block = re.sub('<' + tag + '>.*?</' + tag + '>', '<' + tag + '>' + button + '</' + tag + '>', block)
    # The engine uses the plot's normal feature variety when drawing an
    # additional entity. Support all three forest varieties, like herd overlays.
    variety = re.search(r'<FeatureVariety>.*?</FeatureVariety>', block, re.S)[0]
    block = block.replace(variety, '\n'.join([variety] * 3))
    text = re.sub(r'\s*</FeatureArtInfos>', '\n\t\t' + block + '\n\t</FeatureArtInfos>', text)
    path.write_text(text, encoding='utf-8', newline='\n')


def main():
    global WIDTH, HEIGHT, NAME, TARGET, DESCRIPTION, ATLAS_NAME, WILDS, HISTORICAL_ROUTES, SHARED_EDGE_ROUTES
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--huge', action='store_true', help='Author the additional 200 x 110 Eurocentric world.')
    args = parser.parse_args()
    if args.huge:
        WIDTH, HEIGHT = 200, 110
        NAME = 'Earth200x110'
        TARGET = MOD / 'PublicMaps/Start 1 XL - 3000BC.CivBeyondSwordWBSave'
        DESCRIPTION = 'TXT_KEY_ARFC_HUGE_WORLD_DESC'
        ATLAS_NAME = 'HugeWorldResources.tsv'
        WILDS = WILDS + HUGE_WILDS
        HISTORICAL_ROUTES = HISTORICAL_ROUTES + HUGE_ROUTES
        # Continuous shared-edge paths avoid corner-only gaps through the
        # enlarged peak blocks. Keep passes narrow rather than flattening ranges.
        SHARED_EDGE_ROUTES = True
    v = values()
    used = make_map(v)
    write_data(DATA / (NAME + 'Values.py'), {'VALUES': v})
    write_data(DATA / (NAME + 'Native.py'), {'VALUES': native()})
    write_data(DATA / (NAME + 'Grids.py'), {
        'SETTLEMENTS': compact(BASE.SETTLERS),
        'CITY_NAMES': compact(BASE.VALUES['CityNameManager.tCityMap'], city_names=True),
        'WAR_MAPS': compact(BASE.VALUES['AIWars.tWarsMap'])})
    # Emit continent rectangles using full source-cell extents as well.
    wrapper = ('# Generated by tools/generate_large_world.py. Python 2.4.\n'
               'from {name}Values import VALUES\n'
               'from {name}Native import VALUES as NATIVE\n'
               'from {name}Grids import SETTLEMENTS, CITY_NAMES, WAR_MAPS\n'
               'from SparseGrids import expand\n\n'
               'WIDTH = {width}\nHEIGHT = {height}\nAREA_COUNT = 3\nAREAS = ').format(name=NAME, width=WIDTH, height=HEIGHT)
    areas = [(group,) + rectangle((west, south, east, north))
             for group, west, south, east, north in BASE.AREAS]
    wrapper += pprint.pformat(areas, width=110) + '\n\n'
    wrapper += ("SETTLERS = expand(WIDTH, HEIGHT, SETTLEMENTS)\n"
                "VALUES['CityNameManager.tCityMap'] = expand(WIDTH, HEIGHT, CITY_NAMES)\n"
                "VALUES['AIWars.tWarsMap'] = expand(WIDTH, HEIGHT, WAR_MAPS)\n")
    (DATA / (NAME + '.py')).write_text(wrapper, encoding='ascii')
    terrain_xml(used)
    feature_xml()


if __name__ == '__main__':
    main()
