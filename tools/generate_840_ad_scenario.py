"""Build the 840 AD scenario from RFC's Earth map and late-start city layout."""
from pathlib import Path
from collections import deque
import re

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / 'Awakened RFC/PublicMaps'
ACTIVE = (2, 8, 11, 12, 13, 14, 15, 16, 17)
# Preserve the normal later-spawn treasuries as well as funding existing states.
GOLD = {2: 300, 8: 250, 11: 150, 12: 350, 13: 200, 14: 200,
        15: 150, 16: 200, 17: 150, 18: 200, 19: 300, 20: 600,
        21: 200, 22: 700, 23: 250, 24: 600, 25: 300, 26: 1500,
        27: 100, 28: 100, 29: 300, 30: 500}
# These later-spawning states have only a lightly developed countryside.
YOUNG_STATES = (11, 13, 14, 15, 16, 17)

# Extra units at each capital, beyond city garrisons. Settlers are reserved for
# states with useful nearby settlement space, rather than granted universally.
CAPITAL_UNITS = {
    2: (('WORKER', 3), ('CHINA_CHOKONU', 1), ('SWORDSMAN', 1)),
    8: (('WORKER', 2), ('SWORDSMAN', 2), ('SETTLER', 1)),
    11: (('WORKER', 1), ('SWORDSMAN', 2), ('SETTLER', 1)),
    12: (('WORKER', 3), ('ARABIA_CAMELARCHER', 2)),
    13: (('WORKER', 2), ('SWORDSMAN', 1), ('SPEARMAN', 1), ('SETTLER', 1)),
    14: (('WORKER', 2), ('SWORDSMAN', 1), ('HORSE_ARCHER', 1)),
    15: (('WORKER', 2), ('SWORDSMAN', 1), ('HORSE_ARCHER', 1)),
    16: (('WORKER', 2), ('SWORDSMAN', 2)),
    17: (('WORKER', 2), ('SWORDSMAN', 1), ('HORSE_ARCHER', 1), ('SETTLER', 1)),
}
# Owner, port, nearby sea units. Ships are placed in adjacent water, not inland
# capital tiles. No later-era unique units are granted ahead of their weapons.
NAVAL_UNITS = (
    (2, (105, 39), (('WORKBOAT', 1),)),
    (8, (113, 45), (('GALLEY', 1), ('WORKBOAT', 1))),
    (11, (61, 62), (('GALLEY', 2), ('WORKBOAT', 1))),
    (14, (55, 44), (('WORKBOAT', 1),)),
    (15, (57, 46), (('WORKBOAT', 1),)),
    (16, (53, 54), (('GALLEY', 1), ('WORKBOAT', 1))),
)

CHRISTIAN = 'RELIGION_CHRISTIANITY'
ISLAM = 'RELIGION_ISLAM'

# Location, owner, city name, religion; populations are defined separately.
NEW_CITIES = (
    (102, 47, 2, 'Beijing', 'RELIGION_CONFUCIANISM'),
    (113, 45, 8, 'Kyoto', 'RELIGION_BUDDHISM'),
    (115, 47, 8, 'Edo', 'RELIGION_BUDDHISM'),
    (61, 62, 11, 'Nidaros', None),
    (61, 57, 11, 'Roskilde', None),
    (75, 33, 12, 'Makkah', ISLAM),
    (78, 40, 12, 'Baghdad', ISLAM),
    (102, 34, 13, 'Angkor', 'RELIGION_BUDDHISM'),
    (52, 43, 14, 'Madrid', CHRISTIAN),
    (50, 45, 14, 'Santiago', CHRISTIAN),
    (55, 44, 14, 'Barcelona', CHRISTIAN),
    (51, 40, 28, 'Cordoba', ISLAM),
    (55, 50, 15, 'Paris', CHRISTIAN),
    (53, 54, 16, 'London', CHRISTIAN),
    (53, 57, 16, 'York', CHRISTIAN),
    (62, 52, 17, 'Berlin', CHRISTIAN),
)
CAPITALS = {owner: (x, y) for x, y, owner, *_ in NEW_CITIES
            if owner in ACTIVE}
CAPITALS.update({8: (113, 45), 11: (61, 62), 12: (75, 33),
                 14: (52, 43), 16: (53, 54), 30: (68, 45)})
TRANSFERS = {
    (53, 48): (15, 'Bordeaux'), (57, 46): (15, 'Marseille'),
    (59, 50): (17, 'Frankfurt'),
    (60, 37): (12, 'Tarabulus'), (64, 36): (12, 'Barqa'),
    (67, 36): (12, 'Al-Iskandariyya'), (69, 35): (12, 'Al-Fustat'),
    (73, 38): (12, 'Al-Quds'), (73, 41): (12, 'Iskenderun'),
    (76, 30): (12, "Sana'a"), (82, 38): (12, 'Shiraz'),
    (100, 44): (2, "Xi'an"), (102, 41): (2, 'Guiyang'),
    (104, 45): (2, 'Qufu'), (105, 39): (2, 'Guangzhou'),
    (107, 42): (2, 'Hangzhou'),
}


# Relative ninth-century urban hierarchy, not a literal census conversion.
# All 50 cities have explicit values: inherited 600 AD sizes are not defaults.
# See docs/840ADPopulation.md for sources, rationale and retained map abstractions.
POPULATIONS_840 = {
    # Tang China: Chang'an dominates; Beijing is not yet an imperial metropolis.
    (100, 44): 9,  # Xi'an / Chang'an
    (102, 47): 3,  # Beijing
    (102, 41): 1,  # Guiyang
    (104, 45): 3,  # Qufu
    (105, 39): 5,  # Guangzhou
    (107, 42): 4,  # Hangzhou
    # Heian Japan; Edo remains only a small settlement on the inherited map.
    (113, 45): 5,  # Kyoto
    (115, 47): 1,  # Edo
    # Early Scandinavian settlements, not their later medieval cities.
    (61, 62): 1,   # Nidaros
    (61, 57): 1,   # Roskilde
    # Islamic urban centers: Baghdad and Fustat outweigh smaller desert towns.
    (78, 40): 8,   # Baghdad
    (69, 35): 5,   # Al-Fustat
    (67, 36): 4,   # Al-Iskandariyya
    (75, 33): 3,   # Makkah
    (76, 30): 3,   # Sana'a
    (82, 38): 4,   # Shiraz
    (73, 38): 3,   # Al-Quds
    (73, 41): 2,   # Iskenderun
    (60, 37): 2,   # Tarabulus
    (64, 36): 1,   # Barqa
    (102, 34): 3,  # Angkor: early Khmer state, before its later urban peak.
    # Iberia: Cordoba is the major urban center, not tiny future Madrid.
    (51, 40): 5,   # Cordoba
    (52, 43): 1,   # Madrid: retained RFC capital site, not a mature city.
    (50, 45): 1,   # Santiago
    (55, 44): 2,   # Barcelona
    # Western/northern Europe: modest towns rather than modern capitals.
    (55, 50): 3,   # Paris
    (53, 48): 2,   # Bordeaux
    (57, 46): 2,   # Marseille
    (53, 54): 2,   # London / Lundenwic
    (53, 57): 2,   # York
    (62, 52): 1,   # Berlin: retained RFC site, centuries before its urban rise.
    (59, 50): 3,   # Frankfurt
    # Byzantium's capital has a distinctly greater urban scale than its provinces.
    (68, 45): 7,   # Constantinopolis
    (67, 41): 2,   # Athenae
    (72, 43): 3,   # Iconium
    (75, 44): 3,   # Trapezus
    # Remaining independent/native cities: no blanket growth since 600 AD.
    (52, 60): 1,   # Inbhir Nis
    (60, 47): 3,   # Venetia
    (60, 44): 3,   # Roma
    (72, 29): 2,   # Aksum
    (83, 45): 3,   # Merv
    (85, 47): 4,   # Samarqand
    (85, 41): 3,   # Kandahar
    (88, 36): 1,   # Mumbai: retained map site, not a modern metropolis.
    (90, 40): 3,   # Delhi
    (94, 40): 3,   # Patliputra: no longer the old imperial capital.
    (98, 36): 2,   # Pagan: before its later imperial prominence.
    (109, 46): 3,  # Hanseong: regional center, not the later royal capital.
    (22, 35): 2,   # Yax Mutal: late Classic Maya contraction.
    (23, 37): 3,   # Chich'en Itza
}


def set_field(block, key, value):
    line = '\t\t' + key + '=' + str(value)
    pattern = r'^\s*' + re.escape(key) + r'=[^\n]*'
    if re.search(pattern, block, re.M):
        return re.sub(pattern, lambda _: line, block, count=1, flags=re.M)
    return block.rstrip() + '\n' + line + '\n'


def unit(owner, kind, ai=None):
    result = '\tBeginUnit\n\t\tUnitType=' + kind + ', UnitOwner=' + str(owner) + '\n'
    if ai:
        result += '\t\tUnitAIType=' + ai + '\n'
    return result + '\tEndUnit\n'


def city(x, y, owner, name, population, religion):
    buildings = ['BUILDING_GRANARY', 'BUILDING_BARRACKS']
    if CAPITALS.get(owner) == (x, y):
        buildings += ['BUILDING_PALACE', 'BUILDING_LIBRARY', 'BUILDING_WALLS']
    if owner in (14, 15, 16, 17):
        buildings += ['BUILDING_MONUMENT']
    # RFC calls the monument BUILDING_OBELISK.
    buildings = ['BUILDING_OBELISK' if b == 'BUILDING_MONUMENT' else b for b in buildings]
    lines = ['\tBeginCity', '\t\tCityOwner=' + str(owner), '\t\tCityName=' + name,
             '\t\tCityPopulation=' + str(population)]
    lines += ['\t\tBuildingType=' + b for b in buildings]
    if religion:
        lines.append('\t\tReligionType=' + religion)
    if (x, y) == (75, 33):
        lines += ['\t\tHolyCityReligionType=' + ISLAM, '\t\tBuildingType=BUILDING_ISLAMIC_TEMPLE']
    lines += ['\t\tPlayer' + str(owner) + 'Culture=' + str(200 if CAPITALS.get(owner) == (x, y) else 50), '\tEndCity']
    return '\n'.join(lines) + '\n'


def main():
    text = (MAPS / 'Start 3 - 600 AD.CivBeyondSwordWBSave').read_text(encoding='utf-8')
    text = text.replace('GameTurn=181', 'GameTurn=205').replace('Description=TXT_KEY_RHYES_WB_DESC', 'Description=TXT_KEY_RFCMP_SCENARIO_840_AD')
    religions = {2: 'RELIGION_CONFUCIANISM', 8: 'RELIGION_BUDDHISM', 12: ISLAM,
                 13: 'RELIGION_BUDDHISM', 14: CHRISTIAN, 15: CHRISTIAN, 16: CHRISTIAN, 17: CHRISTIAN}
    player_index = -1

    def player(match):
        nonlocal player_index
        player_index += 1
        block = match.group(1)
        block = set_field(block, 'PlayableCiv', int(player_index in ACTIVE))
        if player_index in GOLD:
            block = set_field(block, 'StartingGold', GOLD[player_index])
        if player_index in religions:
            block = set_field(block, 'StateReligion', religions[player_index])
        return 'BeginPlayer' + block + 'EndPlayer'

    text = re.sub(r'BeginPlayer\b(.*?)EndPlayer', player, text, flags=re.S)
    plots = {}
    for m in re.finditer(r'BeginPlot\b(.*?)EndPlot', text, re.S):
        b = m.group(1)
        xy = re.search(r'x=(\d+),y=(\d+)', b)
        plots[tuple(map(int, xy.groups()))] = b
    for xy, (owner, name) in TRANSFERS.items():
        b = plots[xy]
        old = int(re.search(r'CityOwner=(\d+)', b).group(1))
        b = b.replace('CityOwner=' + str(old), 'CityOwner=' + str(owner))
        b = re.sub(r'CityName=[^\n]*', 'CityName=' + name, b)
        # Some 600 AD cities contain units of both independent factions.
        b = re.sub(r'UnitOwner=\d+', 'UnitOwner=' + str(owner), b)
        b = b.replace('Player' + str(old) + 'Culture', 'Player' + str(owner) + 'Culture')
        if owner == 12 and 'ReligionType=' + ISLAM not in b:
            b = b.replace('EndCity', '\tReligionType=' + ISLAM + '\n\tEndCity')
        plots[xy] = b

    for x, y, owner, name, religion in NEW_CITIES:
        b = plots[x, y]
        if 'PlotType=3' in b or 'PlotType=0' in b or 'BeginCity' in b:
            raise ValueError('Invalid new city site: ' + str((x, y)))
        b = re.sub(r'^\s*(?:FeatureType|ImprovementType|RouteType)=[^\n]*', '', b, flags=re.M)
        b += '\tRouteType=ROUTE_ROAD\n'
        b += city(x, y, owner, name, POPULATIONS_840[x, y], religion)
        b += unit(owner, 'UNIT_LONGBOWMAN' if owner in (11, 12, 14, 15, 16, 17) else 'UNIT_ARCHER')
        b += unit(owner, 'UNIT_SPEARMAN')
        if CAPITALS.get(owner) == (x, y):
            for kind, count in CAPITAL_UNITS[owner]:
                b += unit(owner, 'UNIT_' + kind) * count
        plots[x, y] = b

    # Do not leave transferred cities undefended merely because their 600 AD
    # independent-city template had no unit on the tile.
    for pos, b in plots.items():
        city_owner = re.search(r'CityOwner=(\d+)', b)
        if city_owner and int(city_owner.group(1)) in ACTIVE and 'BeginUnit' not in b:
            plots[pos] = b + unit(int(city_owner.group(1)), 'UNIT_ARCHER')

    for owner, (x, y), package in NAVAL_UNITS:
        candidates = []
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                pos = ((x + dx) % 124, y + dy)
                b = plots.get(pos, '')
                if 'TerrainType=TERRAIN_COAST' in b and 'PlotType=3' in b and 'FEATURE_ICE' not in b:
                    candidates.append((abs(dx) + abs(dy), pos))
        if not candidates:
            raise ValueError('No adjacent coastal ship start for player ' + str(owner))
        _, pos = min(candidates)
        for kind, count in package:
            plots[pos] += unit(owner, 'UNIT_' + kind) * count

    # Explicitly update inherited cities as well as the newly added ones.
    for pos, population in POPULATIONS_840.items():
        if 'BeginCity' not in plots[pos]:
            raise ValueError('Population entry has no city: ' + str(pos))
        plots[pos] = re.sub(r'CityPopulation=\d+',
                           'CityPopulation=' + str(population), plots[pos], count=1)

    # Equip Constantinople's nearby food resources for its larger population.
    for pos, improvement in (((68, 44), 'FISHING_BOATS'),
                             ((70, 46), 'FISHING_BOATS'),
                             ((66, 44), 'PASTURE')):
        b = plots[pos]
        if 'ImprovementType=' not in b:
            plots[pos] = b + '\tImprovementType=IMPROVEMENT_' + improvement + '\n'

    # Short road connections give each established country an internal network.
    city_sites = {}
    for xy, b in plots.items():
        m = re.search(r'CityOwner=(\d+)', b)
        if m:
            city_sites.setdefault(int(m.group(1)), []).append(xy)
    for owner in ACTIVE:
        start = CAPITALS[owner]
        for goal in city_sites.get(owner, []):
            pending, previous = deque([start]), {start: None}
            while pending and goal not in previous:
                x, y = pending.popleft()
                for dx, dy in ((-1, 0), (0, -1), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)):
                    pos = ((x + dx) % 124, y + dy)
                    if pos in previous or pos not in plots:
                        continue
                    b = plots[pos]
                    if 'PlotType=3' in b or 'PlotType=0' in b:
                        continue
                    previous[pos] = (x, y)
                    pending.append(pos)
            if goal in previous:
                pos = goal
                while pos is not None:
                    b = plots[pos]
                    if 'RouteType=' not in b:
                        b += '\tRouteType=ROUTE_ROAD\n'
                    plots[pos] = b
                    pos = previous[pos]

    # Older urban regions receive developed countryside. Later-spawning states
    # get only 1-2 additions per city, including at most one food improvement.
    # Start from the 600 AD terrain so omitted clearances restore their forests.
    young_limits = {(x, y): min(2, POPULATIONS_840[x, y])
                    for owner in YOUNG_STATES for x, y in city_sites[owner]}
    young_counts = {pos: [0, 0] for pos in young_limits}
    for owner in ACTIVE:
        for x, y in city_sites.get(owner, []):
            limited = owner in YOUNG_STATES
            budget = min(2, POPULATIONS_840[x, y]) if limited else 20
            food_budget = 1 if limited else 20
            candidates = []
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if (dx == 0 and dy == 0) or abs(dx) + abs(dy) > 3:
                        continue
                    pos = ((x + dx) % 124, y + dy)
                    b = plots.get(pos, '')
                    if not b or any(tag in b for tag in ('BeginCity', 'ImprovementType=', 'PlotType=0', 'PlotType=3')):
                        continue
                    improvement = None
                    if re.search(r'BonusType=BONUS_(WHEAT|CORN|RICE)\b', b):
                        improvement = 'FARM'
                    elif re.search(r'BonusType=BONUS_(COW|PIG|SHEEP|HORSE)\b', b):
                        improvement = 'PASTURE'
                    elif 'BonusType=' not in b:
                        if 'PlotType=1' in b:
                            improvement = 'MINE'
                        elif re.search(r'TerrainType=TERRAIN_(GRASS|PLAINS)\b', b):
                            improvement = 'FARM' if 'River' in b else ('COTTAGE' if limited else 'HAMLET')
                    if improvement:
                        # Prefer useful resources and nearby tiles, deterministically.
                        candidates.append((0 if 'BonusType=' in b else 1,
                                           max(abs(dx), abs(dy)), abs(dx) + abs(dy),
                                           pos, improvement))
            for _, _, _, pos, improvement in sorted(candidates):
                if budget == 0:
                    break
                food = improvement in ('FARM', 'PASTURE')
                if food and food_budget == 0:
                    continue
                # Shared working radii must not bypass the limits: a farm near
                # York may also feed London, for example.
                affected = []
                for cx, cy in young_limits:
                    dx = min(abs(pos[0] - cx), 124 - abs(pos[0] - cx))
                    dy = abs(pos[1] - cy)
                    if max(dx, dy) <= 2 and dx + dy <= 3:
                        affected.append((cx, cy))
                if any(young_counts[c][0] >= young_limits[c] or
                       (food and young_counts[c][1] >= 1) for c in affected):
                    continue
                b = plots[pos]
                b = re.sub(r'^\s*FeatureType=FEATURE_(FOREST|JUNGLE)[^\n]*', '', b, flags=re.M)
                b += '\tImprovementType=IMPROVEMENT_' + improvement + '\n'
                if 'RouteType=' not in b:
                    b += '\tRouteType=ROUTE_ROAD\n'
                plots[pos] = b
                for c in affected:
                    young_counts[c][0] += 1
                    young_counts[c][1] += int(food)
                budget -= 1
                if food:
                    food_budget -= 1

    def plot(match):
        xy = tuple(map(int, re.search(r'x=(\d+),y=(\d+)', match.group(1)).groups()))
        return 'BeginPlot' + plots[xy] + 'EndPlot'
    text = re.sub(r'BeginPlot\b(.*?)EndPlot', plot, text, flags=re.S)
    target = MAPS / 'Start 4 - 840 AD.CivBeyondSwordWBSave'
    target.write_text(text, encoding='utf-8')
    print('Created', target.name, 'with', len(plots), 'plots and', sum(map(len, city_sites.values())), 'cities')


if __name__ == '__main__':
    main()
