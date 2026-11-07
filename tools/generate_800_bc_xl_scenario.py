"""Adapt the standard 800 BC start to the authored XL world; never launches Civ4.

Run after regenerating Start 1 XL so this start inherits its latest geography
and initial resource atlas. Python supplies the usual 800 BC starting armies.
"""
from pathlib import Path
import re
import sys

import generate_large_world as world

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'Awakened RFC'
MAPS = MOD / 'PublicMaps'
sys.path.insert(0, str(MOD / 'Assets/Python/ScenarioGeographyData'))
import Earth124x68 as reference
import Earth200x110 as geography
from Earth200x110Resources import ADDITIONS

TARGET = MAPS / 'Start 2 XL - 800BC.CivBeyondSwordWBSave'
DESCRIPTION = 'TXT_KEY_ARFC_800_BC_XL_DESC'
PAYLOAD = re.compile(r'Begin(City|Unit)\b.*?End\1', re.S)

# Scaling old coordinates can put workers and development beyond their cities'
# unchanged starting culture radii. Keep these sites inside their owner's borders.
WORKER_START_SITES = {1: (145, 65), 3: (123, 65), 4: world.XL_CAPITAL_OVERRIDES[4]}
STARTING_DEVELOPMENT_SITES = {
    (75, 42): (124, 67),  # sheep pasture inside Babili's second culture ring
    (76, 42): (123, 68),  # mine southwest of Ninua
    (88, 40): (144, 65),  # wheat farm west of Delhi
    (89, 40): (142, 65),  # sheep pasture inside Delhi's third culture ring
    (90, 38): (145, 64),  # farm south of Delhi
    (91, 39): (151, 65),  # farm east of Patliputra
    (92, 39): (150, 64),  # rice farm south of Patliputra
}


def read_map(path):
    text = path.read_text(encoding='utf-8-sig')
    plots = {}
    for block in re.findall(r'BeginPlot\b(.*?)EndPlot', text, re.S):
        pos = tuple(map(int, re.search(r'x=(\d+),y=(\d+)', block).groups()))
        plots[pos] = block
    return text.split('BeginPlot', 1)[0], plots


def fields(block):
    return [s.strip() for s in PAYLOAD.sub('', block).splitlines()
            if s.strip() and not s.strip().startswith('x=')]


def value(lines, key):
    return next((s.split('=', 1)[1] for s in lines if s.startswith(key + '=')), None)


def put(lines, key, entry):
    lines[:] = [s for s in lines if not s.startswith(key + '=')]
    if entry is not None:
        lines.append(key + '=' + entry)


def land(lines):
    return (value(lines, 'PlotType') in ('1', '2') and
            not any('_IMPASSABLE' in s or 'FEATURE_ICE' in s for s in lines))


def river(grid, pos):
    x, y = pos
    return any(flag in grid.get(p, ()) for p, flag in (
        (pos, 'isNOfRiver'), (pos, 'isWOfRiver'),
        ((x, y + 1), 'isNOfRiver'), ((x - 1, y), 'isWOfRiver')))


def shore(grid, pos):
    x, y = pos
    return any(value(grid.get(((x + dx) % geography.WIDTH, y + dy), ()), 'PlotType') == '3'
               for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy)


def main():
    world.WIDTH, world.HEIGHT = geography.WIDTH, geography.HEIGHT
    header, original = read_map(MAPS / 'Start 2 - 800 BC.CivBeyondSwordWBSave')
    xl_header, xl = read_map(MAPS / 'Start 1 XL - 3000BC.CivBeyondSwordWBSave')
    source = {pos: fields(block) for pos, block in original.items()}
    plots = {pos: fields(block) for pos, block in xl.items()}
    for lines in plots.values():
        # Starting development comes from 800 BC, resources/relief from XL.
        lines[:] = [s for s in lines if not s.startswith(('ImprovementType=', 'RouteType=', 'TeamReveal='))
                    and not re.match(r'Player\d+Culture=', s)]
    introduced = 0
    for year, bonus, pos in ADDITIONS:
        if year <= -800:
            if not land(plots[pos]) or value(plots[pos], 'BonusType') is not None:
                raise ValueError('Unavailable historical resource site: ' + str(pos))
            put(plots[pos], 'BonusType', bonus)
            if bonus in ('BONUS_WHEAT', 'BONUS_RICE', 'BONUS_CORN', 'BONUS_COW',
                         'BONUS_SHEEP', 'BONUS_PIG', 'BONUS_HORSE', 'BONUS_COTTON',
                         'BONUS_SUGAR', 'BONUS_DYE', 'BONUS_WINE'):
                feature = value(plots[pos], 'FeatureType') or ''
                if feature.startswith(('FEATURE_FOREST', 'FEATURE_JUNGLE')):
                    put(plots[pos], 'FeatureType', None)
            introduced += 1

    # Reuse reviewed birth, native setup and historical-city anchors.
    anchors = {}
    for key in ('Consts.tCapitals', 'Consts.tReserveCapitals'):
        for old, new in zip(reference.VALUES[key], geography.VALUES[key]):
            if old:
                anchors.setdefault(tuple(old), tuple(new))
    for key, old in reference.VALUES.items():
        if key.startswith('Barbs.l') and len(old) == 4:
            anchors.setdefault(tuple(old[:2]), tuple(geography.VALUES[key][:2]))
    for key in ('NativeAmerica.configureRegions.capital_1', 'NativeAmerica.configureRegions.capital_2',
                'Korea.setup.capital_1', 'Korea.setup.capital_2', 'Korea.setup.capital_3'):
        anchors[reference.VALUES[key]] = geography.VALUES[key]
    resolved = {}

    def resolve(pos):
        if pos in resolved:
            return resolved[pos]
        center = (world.axis(pos[0]), world.axis(pos[1], True))
        water = value(source[pos], 'PlotType') == '3'
        def legal(p):
            return (p in plots and (land(plots[p]) if not water else
                    value(plots[p], 'PlotType') == '3' and
                    not any('FEATURE_ICE' in s for s in plots[p])))
        if pos in anchors and legal(anchors[pos]):
            result = anchors[pos]
        else:
            choices = [p for p in world.footprint(pos) if legal(p)]
            if not choices:
                choices = [(x, y) for x in range(center[0] - 2, center[0] + 3)
                           for y in range(center[1] - 2, center[1] + 3) if legal((x, y))]
            if not choices:
                raise ValueError('No local legal placement for ' + str(pos))
            needs_river = river(source, pos)
            # Shore coordinates in the source wrap at 124, not 200.
            needs_shore = any(value(source.get(((pos[0] + dx) % 124, pos[1] + dy), ()), 'PlotType') == '3'
                              for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy)
            result = min(choices, key=lambda p: (
                needs_river and not river(plots, p),
                not water and needs_shore and not shore(plots, p),
                (p[0] - center[0]) ** 2 + (p[1] - center[1]) ** 2, p))
        resolved[pos] = result
        return result

    payloads, city_sites = {}, set()
    for pos, block in original.items():
        entries = [m[0] for m in PAYLOAD.finditer(block)]
        if not entries:
            continue
        for entry in entries[:]:
            worker = re.search(r'UnitType=UNIT_(?:INDIAN_FAST_)?WORKER, UnitOwner=(\d+)', entry)
            if worker and int(worker[1]) in WORKER_START_SITES:
                dest = WORKER_START_SITES[int(worker[1])]
                payloads.setdefault(dest, []).append(entry)
                entries.remove(entry)
        if not entries:
            continue
        dest = resolve(pos)
        if 'BeginCity' in block:
            if dest in city_sites or not land(plots[dest]):
                raise ValueError('Invalid or duplicate city site: ' + str(dest))
            city_sites.add(dest)
            if value(plots[dest], 'BonusType') is not None:
                raise ValueError('Resource under XL city: ' + str(dest))
            put(plots[dest], 'FeatureType', None)
        payloads.setdefault(dest, []).extend(entries)

    # Expand roads across source footprints to keep the enlarged network joined.
    for pos, lines in source.items():
        route = value(lines, 'RouteType')
        if route:
            for dest in world.footprint(pos):
                if land(plots[dest]):
                    put(plots[dest], 'RouteType', route)
            dest = resolve(pos)
            if land(plots[dest]):
                put(plots[dest], 'RouteType', route)

    improved, omitted = 0, []
    bonus_improvements = {
        'IMPROVEMENT_PASTURE': ('BONUS_COW', 'BONUS_SHEEP', 'BONUS_PIG', 'BONUS_HORSE'),
        'IMPROVEMENT_QUARRY': ('BONUS_STONE', 'BONUS_MARBLE'),
        'IMPROVEMENT_CAMP': ('BONUS_DEER', 'BONUS_FUR', 'BONUS_IVORY'),
        'IMPROVEMENT_PLANTATION': ('BONUS_BANANA', 'BONUS_SUGAR', 'BONUS_DYE', 'BONUS_SILK',
                                 'BONUS_SPICES', 'BONUS_INCENSE', 'BONUS_COTTON'),
        'IMPROVEMENT_FISHING_BOATS': ('BONUS_FISH', 'BONUS_CLAM', 'BONUS_CRAB', 'BONUS_WHALE'),
        'IMPROVEMENT_FARM': ('BONUS_WHEAT', 'BONUS_RICE', 'BONUS_CORN'),
        'IMPROVEMENT_MINE': ('BONUS_COPPER', 'BONUS_IRON', 'BONUS_GOLD', 'BONUS_SILVER',
                            'BONUS_GEMS', 'BONUS_COAL', 'BONUS_URANIUM', 'BONUS_ALUMINUM'),
    }
    for pos, lines in source.items():
        improvement = value(lines, 'ImprovementType')
        if improvement is None:
            continue
        if pos == (72, 39) and improvement == 'IMPROVEMENT_FISHING_BOATS':
            # XL's nearest fish is outside both Sur's and Jerusalem's borders;
            # there is no suitable owned fishery for this inherited improvement.
            omitted.append((pos, improvement))
            continue
        try:
            dest = resolve(pos)
        except ValueError:
            if improvement != 'IMPROVEMENT_GOODY_HUT':
                raise
            omitted.append((pos, improvement))
            continue
        if improvement != 'IMPROVEMENT_GOODY_HUT':
            # Development must fit XL's independent resource atlas, rather than
            # leaving pastures on wheat or quarries on empty desert.
            def suitable(p):
                fs = plots[p]
                if p in city_sites or value(fs, 'ImprovementType') is not None:
                    return False
                bonus = value(fs, 'BonusType')
                if improvement == 'IMPROVEMENT_FISHING_BOATS':
                    return value(fs, 'PlotType') == '3' and bonus in bonus_improvements[improvement]
                if not land(fs):
                    return False
                if bonus in bonus_improvements.get(improvement, ()):
                    return True
                if bonus is not None:
                    return False
                if improvement == 'IMPROVEMENT_MINE':
                    return value(fs, 'PlotType') == '1'
                if improvement in ('IMPROVEMENT_FARM', 'IMPROVEMENT_COTTAGE'):
                    return value(fs, 'PlotType') == '2' and value(fs, 'TerrainType') in ('TERRAIN_GRASS', 'TERRAIN_PLAINS')
                return False
            choices = [p for p in plots if abs(p[0] - dest[0]) <= 3 and abs(p[1] - dest[1]) <= 3
                       and suitable(p)]
            if not choices:
                omitted.append((pos, improvement))
                continue
            dest = min(choices, key=lambda p: (value(plots[p], 'BonusType') not in bonus_improvements.get(improvement, ()),
                                             value(plots[p], 'BonusType') != value(lines, 'BonusType'),
                                             improvement == 'IMPROVEMENT_FARM' and not river(plots, p),
                                             (p[0] - dest[0]) ** 2 + (p[1] - dest[1]) ** 2, p))
            if pos in STARTING_DEVELOPMENT_SITES:
                dest = STARTING_DEVELOPMENT_SITES[pos]
                if not suitable(dest):
                    raise ValueError('Invalid authored development site: ' + str(dest))
        if dest in city_sites or value(plots[dest], 'ImprovementType') is not None:
            raise ValueError('Development placement collision: ' + str(pos))
        put(plots[dest], 'ImprovementType', improvement)
        if improvement not in ('IMPROVEMENT_GOODY_HUT', 'IMPROVEMENT_CAMP', 'IMPROVEMENT_FISHING_BOATS'):
            if (value(plots[dest], 'FeatureType') or '').startswith(('FEATURE_FOREST', 'FEATURE_JUNGLE')):
                put(plots[dest], 'FeatureType', None)
        improved += 1

    header = re.sub(r'BeginMap\b.*?EndMap', lambda _: re.search(r'BeginMap\b.*?EndMap', xl_header, re.S)[0], header, flags=re.S)
    header = re.sub(r'Description=[^\r\n]*', 'Description=' + DESCRIPTION, header, count=1)
    header = re.sub(r'GameTurn=87[ \t]*', 'GameTurn=174', header, count=1)
    header = re.sub(r'Calendar=CALENDAR_DEFAULT[ \t]*', 'Calendar=CALENDAR_DEFAULT\n\tSpeed=GAMESPEED_XL', header, count=1)
    player_id = iter(range(39))
    def player(match):
        owner = next(player_id)
        block = match[0]
        x, y = re.search(r'StartingX=(\d+)', block), re.search(r'StartingY=(\d+)', block)
        if x and y:
            dest = resolve((int(x[1]), int(y[1])))
        elif re.search(r'PlayableCiv=1\b', block):
            dest = geography.VALUES['Consts.tCapitals'][owner]
        else:
            return block
        block = re.sub(r'^[ \t]*Starting[XY]=[^\r\n]*\n?', '', block, flags=re.M)
        return block.replace('EndPlayer', '\tStartingX=%d\n\tStartingY=%d\nEndPlayer' % dest)
    header = re.sub(r'BeginPlayer\b.*?EndPlayer', player, header, flags=re.S)
    output = [header.rstrip() + '\n']
    for (x, y), lines in plots.items():
        output.append('BeginPlot\n\tx=%d,y=%d\n\t%s\n%sEndPlot\n' %
                      (x, y, '\n\t'.join(lines), '\n'.join(payloads.get((x, y), ())) + '\n'))
    TARGET.write_text(''.join(output), encoding='utf-8', newline='\n')
    print('Created', TARGET.name)
    print('%d cities, %d placed units, %d improvements, %d historical resource introductions.' %
          (len(city_sites), sum(entry.startswith('BeginUnit') for entries in payloads.values() for entry in entries), improved, introduced))
    if omitted:
        print('Development omitted without a suitable local XL site:', omitted)


if __name__ == '__main__':
    main()
