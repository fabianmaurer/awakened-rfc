"""Author a post-Constantinople 1453 world on RFC's existing Earth terrain.

This creates scenario assets only. It never starts Civilization IV.
"""
from pathlib import Path
from collections import deque
import re
import xml.etree.ElementTree as ET
from generate_840_ad_scenario import set_field, unit

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'Awakened RFC'
TARGET = MOD / 'PublicMaps/Start 5 - 1453 AD.CivBeyondSwordWBSave'
START_TURN = 271
ACTIVE = tuple(i for i in range(26) if i != 3)
CHRISTIAN = 'RELIGION_CHRISTIANITY'
ISLAM = 'RELIGION_ISLAM'
BUDDHISM = 'RELIGION_BUDDHISM'
CONFUCIAN = 'RELIGION_CONFUCIANISM'
RELIGIONS = {0: ISLAM, 1: ISLAM, 2: CONFUCIAN, 4: CHRISTIAN,
             5: ISLAM, 6: ISLAM, 7: CHRISTIAN, 8: BUDDHISM,
             9: CHRISTIAN, 11: CHRISTIAN, 12: ISLAM, 13: BUDDHISM,
             14: CHRISTIAN, 15: CHRISTIAN, 16: CHRISTIAN, 17: CHRISTIAN,
             18: CHRISTIAN, 19: CHRISTIAN, 20: ISLAM, 21: CHRISTIAN}

# First city per major is the capital. Sizes are relative urban weights, not a
# census conversion. The crowded RFC map requires regional aggregations.
CITY_DATA = """
0|69,35|Al-Qahira|10
0|67,36|Al-Iskandariyya|6
0|73,38|Al-Quds|4
0|74,41|Dimashq|7
1|90,40|Delhi|8
28|94,40|Jaunpur|5
28|96,39|Gaur|5
1|88,42|Lahore|4
2|102,47|Beijing|10
2|107,43|Nanjing|10
2|100,44|Xi'an|6
2|104,45|Qufu|5
2|105,39|Guangzhou|8
2|107,41|Hangzhou|9
2|102,41|Guiyang|4
4|67,41|Mistra|3
5|85,47|Samarqand|7
5|83,43|Herat|6
5|83,45|Merv|4
5|85,41|Kandahar|4
6|58,39|Tunis|6
6|60,37|Tarabulus|3
7|60,47|Venezia|7
7|60,44|Roma|5
8|113,45|Kyoto|8
8|115,47|Edo|1
8|111,43|Hakata|4
9|72,29|Aksum|4
9|73,26|Dabra Libanos|3
10|23,37|Mani|3
10|22,35|Tayasal|3
11|61,57|Kobenhavn|4
11|61,62|Nidaros|3
11|65,62|Stockholm|4
12|75,33|Makkah|4
27|76,30|Sana'a|3
13|102,32|Chaktomuk|4
13|102,34|Angkor|3
14|52,43|Toledo|5
14|52,45|Leon|3
14|55,44|Barcelona|6
14|50,41|Sevilla|6
15|55,50|Paris|9
16|53,48|Bordeaux|4
15|57,46|Marseille|5
16|53,54|London|7
16|53,57|York|4
17|62,48|Wien|5
17|59,50|Frankfurt|5
17|62,52|Berlin|3
17|64,51|Praha|6
18|73,54|Moskva|5
18|75,55|Vladimir|3
19|57,53|Brugge|7
20|51,29|Niani|5
29|53,31|Timbuktu|5
29|56,31|Gao|4
20|54,29|Djenne|4
21|49,43|Lisboa|6
21|49,45|Porto|4
22|28,22|Qusqu|7
29|24,25|Chan Chan|6
29|25,23|Cajamarca|4
22|27,24|Huamanga|4
22|30,18|Hatun Qulla|4
29|26,29|Tumipampa|4
29|30,15|Tupiza|3
29|29,11|Copiapo|2
23|99,51|Qaraqorum|4
23|96,53|Qobdo|2
24|18,37|Tenochtitlan|10
24|20,35|Texcoco|4
24|21,33|Oaxaca|4
25|68,45|Konstantiniyye|7
25|72,43|Konya|5
25|70,43|Bursa|5
25|66,46|Edirne|4
25|65,44|Thessaloniki|4
27|52,41|Gharnata|5
27|52,60|Inbhir Nis|3
27|67,53|Krakow|5
27|72,57|Novgorod|5
27|78,40|Baghdad|5
27|82,38|Shiraz|5
27|81,45|Tabriz|6
27|75,44|Trapezous|4
28|98,36|Ava|5
28|100,32|Ayutthaya|6
28|106,33|Thang Long|5
28|109,46|Hanseong|6
28|88,36|Dabhol|4
28|91,33|Vijayanagara|8
28|87,40|Multan|4
29|61,16|Mbanza Kongo|4
29|74,14|Kilwa|5
29|68,15|Great Zimbabwe|4
27|49,56|Dublin|3
28|62,42|Napoli|6
28|60,40|Palermo|5
27|65,49|Buda|5
27|76,46|Tbilisi|3
28|52,37|Fes|6
28|54,38|Tlemcen|4
28|82,34|Masqat|3
28|96,43|Lhasa|3
28|93,29|Colombo|3
28|100,30|Melaka|5
28|106,25|Surabaya|4
"""

# Independent slots group unrelated polities. Their cities need local faiths,
# rather than a shared state religion inherited from the slot.
CITY_RELIGIONS = {
    'Dublin': CHRISTIAN, 'Napoli': CHRISTIAN, 'Palermo': CHRISTIAN,
    'Buda': CHRISTIAN, 'Tbilisi': CHRISTIAN,
    'Fes': ISLAM, 'Tlemcen': ISLAM, 'Masqat': ISLAM, 'Melaka': ISLAM,
    'Lhasa': BUDDHISM, 'Colombo': BUDDHISM,
    'Surabaya': 'RELIGION_HINDUISM',
}

BASE_TECHS = ('MYSTICISM MEDITATION POLYTHEISM PRIESTHOOD MONOTHEISM '
              'MONARCHY LITERATURE CODE_OF_LAWS DRAMA FEUDALISM THEOLOGY '
              'MUSIC CIVIL_SERVICE GUILDS DIVINE_RIGHT FISHING THE_WHEEL '
              'AGRICULTURE POTTERY AESTHETICS SAILING WRITING MATHEMATICS '
              'ALPHABET CALENDAR CURRENCY PHILOSOPHY PAPER BANKING '
              'HUNTING MINING ARCHERY MASONRY ANIMAL_HUSBANDRY '
              'BRONZE_WORKING HORSEBACK_RIDING IRON_WORKING METAL_CASTING '
              'COMPASS CONSTRUCTION MACHINERY ENGINEERING').split()
AMERICAN_TECHS = ('MYSTICISM POLYTHEISM PRIESTHOOD MONARCHY CODE_OF_LAWS '
                  'AGRICULTURE POTTERY WRITING MATHEMATICS CALENDAR '
                  'CURRENCY HUNTING MINING ARCHERY MASONRY BRONZE_WORKING '
                  'CONSTRUCTION FEUDALISM').split()
GUNPOWDER = (0, 1, 2, 5, 8, 11, 14, 15, 16, 17, 18, 19, 21, 25)
OPTICS = (2, 7, 11, 14, 15, 16, 19, 21)
LEADERS = {
    0: ('Inal', 'Inal'), 1: ('Bahlul Lodi', 'Bahlul Lodi'),
    2: ('Jingtai', 'Jingtai'), 4: ('Palaiologan Despots', 'Despoten der Palaiologen'),
    5: ('Timurid Princes', 'Timuridische Fürsten'),
    6: ('Abu Amr Uthman', 'Abu Amr Uthman'),
    7: ('Italian City Councils', 'Italienische Stadträte'),
    8: ('Ashikaga Yoshimasa', 'Ashikaga Yoshimasa'),
    9: ('Zara Yaqob', 'Zara Yaqob'), 10: ('Maya Dynasties', 'Maya-Dynastien'),
    11: ('Scandinavian Crowns', 'Skandinavische Königshäuser'),
    12: ('Sharifs of Mecca', 'Scharifen von Mekka'),
    13: ('Ponhea Yat', 'Ponhea Yat'),
    14: ('Iberian Crowns', 'Iberische Königshäuser'),
    15: ('Charles VII', 'Karl VII.'), 16: ('Henry VI', 'Heinrich VI.'),
    17: ('Frederick III', 'Friedrich III.'), 18: ('Vasily II', 'Wassili II.'),
    19: ('Philip the Good', 'Philipp der Gute'),
    20: ('Mansa of Mali', 'Mansa von Mali'), 21: ('Afonso V', 'Alfons V.'),
    22: ('Pachacuti', 'Pachacuti'), 23: ('Mongol Taishis', 'Mongolische Taischi'),
    24: ('Moctezuma I', 'Moctezuma I.'), 25: ('Mehmed II', 'Mehmed II.'),
}


def records():
    cities = []
    for line in CITY_DATA.strip().splitlines():
        owner, xy, name, size = line.split('|')
        cities.append((int(owner), tuple(map(int, xy.split(','))), name, int(size)))
    return cities


def techs(owner):
    result = list(AMERICAN_TECHS if owner in (10, 22, 24) else BASE_TECHS)
    if owner in GUNPOWDER:
        result.append('GUNPOWDER')
    if owner in OPTICS:
        result.append('OPTICS')
    return result


def text_entries():
    from xml.sax.saxutils import escape
    en = ('1453 AD: After the fall of Constantinople. Every established major '
          'civilization is playable. Regional states are represented by RFC civilization slots; '
          'America appears on its usual schedule.')
    de = ('1453 n. Chr.: Nach dem Fall Konstantinopels. Alle bestehenden großen '
          'Zivilisationen sind spielbar. Regionale Staaten werden durch die RFC-Zivilisationen '
          'abgebildet; Amerika erscheint nach dem gewohnten Zeitplan.')
    entries = [('TXT_KEY_RFCMP_SCENARIO_1453_AD', en, de)]
    entries += [('TXT_KEY_RFCMP_1453_LEADER_' + str(i), *LEADERS[i]) for i in sorted(LEADERS)]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<Civ4GameText xmlns="http://www.firaxis.com">']
    for tag, english, german in entries:
        lines += ['  <TEXT>', '    <Tag>' + tag + '</Tag>']
        for language in ('English', 'French', 'German', 'Italian', 'Spanish'):
            value = german if language == 'German' else english
            lines.append('    <' + language + '>' + escape(value) + '</' + language + '>')
        lines.append('  </TEXT>')
    lines.append('</Civ4GameText>')
    (MOD / 'Assets/XML/Text/CIV4GameText_Scenario1453.xml').write_bytes(
        ('\n'.join(lines) + '\n').encode('ascii', 'xmlcharrefreplace'))


def main():
    text = (MOD / 'PublicMaps/Start 4 - 840 AD.CivBeyondSwordWBSave').read_text(encoding='utf-8')
    text = text.replace('GameTurn=205', 'GameTurn=' + str(START_TURN))
    text = text.replace('TXT_KEY_RFCMP_SCENARIO_840_AD', 'TXT_KEY_RFCMP_SCENARIO_1453_AD')
    cities = records()
    if {owner for owner, _, _, _ in cities if owner < 27} != set(ACTIVE):
        raise ValueError('Every populated major must be selectable, and every selectable major needs a city')
    for index, (_, (x, y), name, _) in enumerate(cities):
        for _, (xx, yy), other, _ in cities[index + 1:]:
            if max(min(abs(x - xx), 124 - abs(x - xx)), abs(y - yy)) < 2:
                raise ValueError('City sites are adjacent: %s / %s' % (name, other))
    capitals = {}
    for owner, pos, _, _ in cities:
        capitals.setdefault(owner, pos)
    capitals[16] = (53, 54)  # London, despite Bordeaux appearing earlier in the data.

    def initial_culture_reaches(pos):
        x, y = pos
        for owner, (cx, cy), _, _ in cities:
            dx = min(abs(x - cx), 124 - abs(x - cx))
            dy = abs(y - cy)
            # CvCity::cultureDistance uses Civ4's plotDistance. The authored
            # 500/200 city culture gives capitals radius 4, other cities 3.
            radius = 4 if capitals[owner] == (cx, cy) else 3
            if max(dx, dy) + min(dx, dy) // 2 <= radius:
                return True
        return False

    player_index = -1

    def player(match):
        nonlocal player_index
        player_index += 1
        owner = player_index
        block = match.group(1)
        block = re.sub(r'^\s*(?:StateReligion|CivDesc|CivShortDesc|CivicOption|StartingGold|LeaderName)=[^\n]*', '', block, flags=re.M)
        block = set_field(block, 'PlayableCiv', int(owner in ACTIVE))
        if owner in ACTIVE:
            block = set_field(block, 'MinorNationStatus', 0)
            block = set_field(block, 'StartingGold', 500 if owner not in (2, 25) else 800)
            block = set_field(block, 'LeaderName', 'TXT_KEY_RFCMP_1453_LEADER_' + str(owner))
        if owner == 26:
            block = set_field(block, 'StartingGold', 1500)
        if owner in RELIGIONS:
            block = set_field(block, 'StateReligion', RELIGIONS[owner])
        if owner in capitals:
            block = set_field(block, 'StartingX', capitals[owner][0])
            block = set_field(block, 'StartingY', capitals[owner][1])
        return 'BeginPlayer' + block + 'EndPlayer'

    text = re.sub(r'BeginPlayer\b(.*?)EndPlayer', player, text, flags=re.S)
    team_index = -1

    def team(match):
        nonlocal team_index
        team_index += 1
        owner = team_index
        lines = ['BeginTeam']
        if owner in capitals:
            lines += ['\tTech=TECH_' + t for t in techs(owner)]
            # Continental diplomacy predates this start; no transatlantic contact.
            for other in capitals:
                if other != owner and ((owner not in (10, 22, 24) and other not in (10, 22, 24))
                                       or (owner in (10, 24) and other in (10, 24))):
                    lines.append('\tContactWithTeam=' + str(other))
        if owner in (15, 16):
            lines.append('\tAtWar=' + str(31 - owner))
        lines.append('EndTeam')
        return '\n'.join(lines)

    text = re.sub(r'BeginTeam\b(.*?)EndTeam', team, text, flags=re.S)
    plots = {}
    for match in re.finditer(r'BeginPlot\b(.*?)EndPlot', text, re.S):
        block = match.group(1)
        pos = tuple(map(int, re.search(r'x=(\d+),y=(\d+)', block).groups()))
        block = re.sub(r'\s*BeginCity\b.*?EndCity', '', block, flags=re.S)
        block = re.sub(r'\s*BeginUnit\b.*?EndUnit', '', block, flags=re.S)
        block = re.sub(r'^\s*(?:Player\d+Culture|TeamReveal)=[^\n]*', '', block, flags=re.M)
        # Culture is applied while WorldBuilder is still creating cities.
        # Claiming an inherited hut calls doGoody with no unit during this
        # incomplete setup (notably at 59,55 when Brugge expands). Keep huts
        # only outside the initial borders, for discovery during normal play.
        if initial_culture_reaches(pos):
            block = re.sub(r'^\s*ImprovementType=IMPROVEMENT_GOODY_HUT[^\n]*', '', block, flags=re.M)
        plots[pos] = block.rstrip() + '\n'

    used = set()
    for owner, pos, name, size in cities:
        block = plots[pos]
        if pos in used or 'PlotType=0' in block or 'PlotType=3' in block:
            raise ValueError('Invalid city site: %s %s' % (name, pos))
        used.add(pos)
        block = re.sub(r'^\s*(?:FeatureType|ImprovementType|RouteType)=[^\n]*', '', block, flags=re.M)
        block += '\tRouteType=ROUTE_ROAD\n\tBeginCity\n'
        block += '\t\tCityOwner=%d\n\t\tCityName=%s\n\t\tCityPopulation=%d\n' % (owner, name, size)
        buildings = ['GRANARY', 'BARRACKS', 'WALLS']
        if size >= 4:
            buildings += ['LIBRARY', 'MARKET']
        if size >= 6:
            buildings += ['AQUEDUCT', 'FORGE']
        if capitals[owner] == pos:
            buildings += ['PALACE']
        if name == 'Al-Qahira':
            buildings.append('PYRAMID')
        if name == 'Konstantiniyye':
            buildings.append('HAGIA_SOPHIA')
        if name == 'Beijing':
            buildings.append('GREAT_WALL')
        block += ''.join('\t\tBuildingType=BUILDING_' + b + '\n' for b in buildings)
        religion = CITY_RELIGIONS.get(name, RELIGIONS.get(owner))
        if religion:
            block += '\t\tReligionType=' + religion + '\n'
        holy = {'Makkah': [ISLAM], 'Al-Quds': [CHRISTIAN, 'RELIGION_JUDAISM'],
                'Jaunpur': ['RELIGION_HINDUISM', BUDDHISM],
                'Qufu': [CONFUCIAN], "Xi'an": ['RELIGION_TAOISM']}.get(name, [])
        for faith in holy:
            if faith != religion:
                block += '\t\tReligionType=' + faith + '\n'
            block += '\t\tHolyCityReligionType=' + faith + '\n'
        block += '\t\tPlayer%dCulture=%d\n\tEndCity\n' % (owner, 500 if capitals[owner] == pos else 200)
        garrison = 'UNIT_ARCHER' if owner in (10, 22, 24) else 'UNIT_LONGBOWMAN'
        block += unit(owner, garrison, 'UNITAI_CITY_DEFENSE') * 2
        if capitals[owner] == pos:
            block += unit(owner, 'UNIT_WORKER', 'UNITAI_WORKER') * (3 if owner in ACTIVE else 1)
            if owner in ACTIVE:
                army = 'UNIT_SPEARMAN' if owner in (10, 22, 24) else 'UNIT_KNIGHT'
                block += unit(owner, army) * 2
        if owner == 25 and capitals[owner] == pos:
            # Bombards are represented by trebuchets; Steel-era cannon are not
            # unlocked merely to depict the siege artillery of 1453.
            block += unit(owner, 'UNIT_OTTOMAN_JANISSARY') * 3
            block += unit(owner, 'UNIT_TREBUCHET') * 2
        plots[pos] = block

    # Develop each city's working radius and give contiguous local culture.
    for owner, (x, y), _, size in cities:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                pos = ((x + dx) % 124, y + dy)
                if pos not in plots or abs(dx) + abs(dy) > 3:
                    continue
                block = plots[pos]
                block += '\tPlayer%dCulture=%d\n' % (owner, 40 if max(abs(dx), abs(dy)) <= 1 else 10)
                if pos not in used and not any(t in block for t in ('PlotType=0', 'PlotType=3', 'ImprovementType=')):
                    improvement = None
                    if re.search(r'BonusType=BONUS_(WHEAT|RICE|CORN)\b', block):
                        improvement = 'FARM'
                    elif re.search(r'BonusType=BONUS_(COW|PIG|SHEEP|HORSE)\b', block):
                        improvement = 'PASTURE'
                    elif re.search(r'BonusType=BONUS_(IRON|COPPER|GOLD|SILVER|GEMS)\b', block):
                        improvement = 'MINE'
                    elif 'BonusType=' not in block and 'PlotType=1' in block:
                        improvement = 'MINE'
                    elif 'BonusType=' not in block and re.search(r'TerrainType=TERRAIN_(GRASS|PLAINS)\b', block):
                        improvement = 'FARM' if 'River' in block else 'HAMLET'
                    if improvement:
                        block = re.sub(r'^\s*FeatureType=FEATURE_(FOREST|JUNGLE)[^\n]*', '', block, flags=re.M)
                        block += '\tImprovementType=IMPROVEMENT_' + improvement + '\n'
                        if 'RouteType=' not in block:
                            block += '\tRouteType=ROUTE_ROAD\n'
                plots[pos] = block

    # Connect each major's cities over land where a route exists.
    for owner in ACTIVE:
        start = capitals[owner]
        for _, goal, _, _ in [c for c in cities if c[0] == owner]:
            pending, previous = deque([start]), {start: None}
            while pending and goal not in previous:
                x, y = pending.popleft()
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    pos = ((x + dx) % 124, y + dy)
                    if pos in previous or pos not in plots or any(t in plots[pos] for t in ('PlotType=0', 'PlotType=3')):
                        continue
                    previous[pos] = (x, y)
                    pending.append(pos)
            if goal in previous:
                pos = goal
                while pos is not None:
                    if 'RouteType=' not in plots[pos]:
                        plots[pos] += '\tRouteType=ROUTE_ROAD\n'
                    pos = previous[pos]

    # Coastal economies start with a small fleet on adjacent sea tiles.
    for owner in (2, 6, 7, 8, 11, 14, 15, 16, 19, 21, 25):
        for _, (x, y), _, _ in [c for c in cities if c[0] == owner]:
            sea = [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                   if 'PlotType=3' in plots.get((x + dx, y + dy), '')
                   and 'FEATURE_ICE' not in plots.get((x + dx, y + dy), '')]
            if sea:
                ship = 'UNIT_CARAVEL' if owner in OPTICS else 'UNIT_GALLEY'
                plots[min(sea)] += unit(owner, ship) + unit(owner, 'UNIT_WORKBOAT')
                break

    for (x, y), block in plots.items():
        revealed = []
        for owner in ACTIVE:
            local = any(max(min(abs(x - cx), 124 - abs(x - cx)), abs(y - cy)) <= 8
                        for o, (cx, cy), _, _ in cities if o == owner)
            old_world = owner not in (10, 22, 24) and 42 <= x <= 118 and 20 <= y <= 65
            if local or old_world:
                revealed.append(str(owner))
        if revealed:
            plots[x, y] += '\tTeamReveal=' + ','.join(revealed) + ',\n'

    def plot(match):
        pos = tuple(map(int, re.search(r'x=(\d+),y=(\d+)', match.group(1)).groups()))
        return 'BeginPlot' + plots[pos] + 'EndPlot'

    text = re.sub(r'BeginPlot\b(.*?)EndPlot', plot, text, flags=re.S)
    # Check generated references against the installed mod's own XML catalogue.
    known = set()
    for path in (MOD / 'Assets/XML').rglob('*.xml'):
        for e in ET.parse(path).getroot().iter():
            if e.tag.rsplit('}', 1)[-1] == 'Type' and e.text:
                known.add(e.text)
    for prefix in ('UnitType', 'BuildingType', 'Tech', 'ReligionType', 'HolyCityReligionType'):
        for value in re.findall(prefix + r'=(\w+)', text):
            if value not in known:
                raise ValueError('Unknown %s: %s' % (prefix, value))
    TARGET.write_text(text, encoding='utf-8')
    data = ('# Generated by tools/generate_1453_ad_scenario.py; Python 2.4.\n'
            'START_TURN = %r\nSTART_YEAR = 1453\nACTIVE_PLAYERS = %r\nCAPITALS = %r\n' %
            (START_TURN, ACTIVE, {i: capitals[i] for i in ACTIVE}))
    (MOD / 'Assets/Python/Scenario1453Data.py').write_text(data, encoding='ascii')
    text_entries()
    print('Created %s: %d cities, %d playable major civilizations.' % (TARGET.name, len(cities), len(ACTIVE)))


if __name__ == '__main__':
    main()
