"""Maintain Korea's authored starts and compact peninsula in all RFC scenarios.

Also called by the 900/1453 generators so regeneration preserves Korea.
Never launches the game. Requires Python 3 for authoring, not for gameplay.
"""
from pathlib import Path
import ast
import re

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'Awakened RFC'
KOREA = 30


def field(block, key, value):
    pattern = r'^[ \t]*' + re.escape(key) + r'=[^\r\n]*'
    line = '\t' + key + '=' + str(value)
    if re.search(pattern, block, re.M):
        return re.sub(pattern, lambda _: line, block, flags=re.M)
    return block.rstrip() + '\n' + line + '\n'


def ensure_papal_slot(text):
    """Reserve the Papal player; its Palace is founded by the Rome event only."""
    text = re.sub(r'^\s*BuildingType=BUILDING_APOSTOLIC_PALACE[^\r\n]*\r?\n', '', text, flags=re.M)
    players = re.findall(r'BeginPlayer\b(.*?)EndPlayer', text, re.S)
    if len(players) == 37:
        if 'CivType=NONE' not in players[36] or 'Team=36' not in players[36]:
            raise ValueError('Reserved Papal State slot is occupied')
        return text
    if len(players) != 36:
        raise ValueError('Expected the reserved Crusader slot before Papal reservation')
    scalar = (r'\b(Team|UnitOwner|CityOwner|OriginalOwner|PreviousOwner|'
              r'ContactWithTeam|AtWar|OpenBordersWithTeam|DefensivePactWithTeam|'
              r'VassalOfTeam|PermanentWarPeace)=(\d+)')
    text = re.sub(scalar, lambda m: m[1] + '=' + str(int(m[2]) + (int(m[2]) >= 36)), text)
    text = re.sub(r'\bPlayer36Culture', 'Player37Culture', text)
    text = re.sub(r'\bTeamReveal=([^\r\n]*)', lambda m: 'TeamReveal=' + ','.join(
        str(int(n) + (int(n) >= 36)) for n in m[1].split(',') if n.strip()) + ',', text)
    for kind, new in [('Team', 'BeginTeam\nEndTeam'),
                      ('Player', 'BeginPlayer\n\tTeam=36\n\tCivType=NONE\n'
                       '\tLeaderType=NONE\n\tPlayableCiv=0\n\tMinorNationStatus=0\nEndPlayer')]:
        matches = list(re.finditer('Begin' + kind + r'\b.*?End' + kind, text, re.S))
        at = matches[-1].end()
        text = text[:at] + '\n' + new + text[at:]
    return text


def ensure_crusader_slot(text):
    """Reserve player/team 35 and move the engine's barbarian identity to 36."""
    players = re.findall(r'BeginPlayer\b(.*?)EndPlayer', text, re.S)
    if len(players) in (36, 37):
        if 'CivType=NONE' not in players[35] or 'Team=35' not in players[35]:
            raise ValueError('Reserved Crusader state slot is occupied')
        return ensure_papal_slot(text)
    if len(players) != 35:
        raise ValueError('Expected 35 historical players before Crusader reservation')
    scalar = (r'\b(Team|UnitOwner|CityOwner|OriginalOwner|PreviousOwner|'
              r'ContactWithTeam|AtWar|OpenBordersWithTeam|DefensivePactWithTeam|'
              r'VassalOfTeam|PermanentWarPeace)=(\d+)')
    text = re.sub(scalar, lambda m: m[1] + '=' + str(int(m[2]) + (int(m[2]) >= 35)), text)
    text = re.sub(r'\bPlayer35Culture', 'Player36Culture', text)
    text = re.sub(r'\bTeamReveal=([^\r\n]*)', lambda m: 'TeamReveal=' + ','.join(
        str(int(n) + (int(n) >= 35)) for n in m[1].split(',') if n.strip()) + ',', text)
    for kind, new in [('Team', 'BeginTeam\nEndTeam'),
                      ('Player', 'BeginPlayer\n\tTeam=35\n\tCivType=NONE\n'
                       '\tLeaderType=NONE\n\tPlayableCiv=0\n\tMinorNationStatus=1\nEndPlayer')]:
        matches = list(re.finditer('Begin' + kind + r'\b.*?End' + kind, text, re.S))
        at = matches[-1].end()
        text = text[:at] + '\n' + new + text[at:]
    return ensure_papal_slot(text)


def migrate_slots(text):
    """Insert Korea before minor players, once. Existing major IDs stay fixed."""
    players = re.findall(r'BeginPlayer\b(.*?)EndPlayer', text, re.S)
    if len(players) == 38:
        if 'CIVILIZATION_KOREA' not in players[30] or 'CIVILIZATION_NATIVE_AMERICA' not in players[31]:
            raise ValueError('Unexpected major-player layout')
        return text
    if len(players) in (35, 36, 37):
        if 'CIVILIZATION_KOREA' not in players[KOREA]:
            raise ValueError('Player 30 is occupied by a different civilization')
        return ensure_crusader_slot(text)
    if len(players) != 34:
        raise ValueError('Unexpected scenario player count')
    # Player and team IDs occur in these scalar WB fields; map coordinates,
    # technology IDs and the civilization XML order are independent of slots.
    scalar = (r'\b(Team|UnitOwner|CityOwner|OriginalOwner|PreviousOwner|'
              r'ContactWithTeam|AtWar|OpenBordersWithTeam|DefensivePactWithTeam|'
              r'VassalOfTeam|PermanentWarPeace)=(\d+)')
    text = re.sub(scalar, lambda m: m[1] + '=' + str(int(m[2]) + (int(m[2]) >= 30)), text)
    text = re.sub(r'\bPlayer(\d+)Culture',
                  lambda m: 'Player%dCulture' % (int(m[1]) + (int(m[1]) >= 30)), text)
    text = re.sub(r'\bTeamReveal=([^\r\n]*)', lambda m: 'TeamReveal=' + ','.join(
        str(int(n) + (int(n) >= 30)) for n in m[1].split(',') if n.strip()) + ',', text)
    for kind, new in [('Team', 'BeginTeam\nEndTeam'),
                      ('Player', 'BeginPlayer\n\tCivType=CIVILIZATION_KOREA\n'
                       '\tLeaderType=LEADER_WANGKON\n\tTeam=30\n'
                       '\tPlayableCiv=1\n\tHandicap=HANDICAP_PRINCE\nEndPlayer')]:
        matches = list(re.finditer('Begin' + kind + r'\b.*?End' + kind, text, re.S))
        at = matches[30].start()
        text = text[:at] + new + '\n' + text[at:]
    return ensure_crusader_slot(text)


def korea_tables():
    source = (MOD / 'Assets/Python/Korea.py').read_text(encoding='utf-8')
    return {n.targets[0].id: ast.literal_eval(n.value)
            for n in ast.parse(source).body if isinstance(n, ast.Assign)}


def techs(turn):
    tables = korea_tables()
    result = list(tables['EARLY_TECHS'])
    for threshold, name in [(181, 'CLASSICAL_TECHS'), (211, 'MEDIEVAL_TECHS'),
                            (271, 'RENAISSANCE_TECHS')]:
        if turn >= threshold:
            result.extend(tables[name])
    return result


def unit(kind, ai=None):
    text = '\n\tBeginUnit\n\t\tUnitType=UNIT_%s, UnitOwner=30\n' % kind
    if ai:
        text += '\t\tUnitAIType=UNITAI_' + ai + '\n'
    return text + '\tEndUnit\n'


def city(name, population, buildings, religion=None):
    lines = ['\tBeginCity', '\t\tCityOwner=30', '\t\tCityName=' + name,
             '\t\tCityPopulation=' + str(population)]
    lines += ['\t\tBuildingType=BUILDING_' + b for b in buildings]
    if religion:
        lines.append('\t\tReligionType=RELIGION_' + religion)
    lines += ['\t\tPlayer30Culture=100', '\tEndCity']
    return '\n' + '\n'.join(lines) + '\n'


def apply_korea(text):
    text = migrate_slots(text)
    turn = int(re.search(r'\bGameTurn=(\d+)', text)[1])
    if turn not in (0, 87, 181, 211, 271):
        raise ValueError('Unsupported scenario date')
    capital = (109, 46) if turn == 271 else (110, 45) if turn == 211 else (109, 48)
    names = {(x, y): name for x, y, name in korea_tables()['CITY_NAMES']}
    players = iter(range(len(re.findall(r'BeginPlayer\b', text))))

    def player(match):
        owner = next(players)
        if owner != KOREA:
            return match[0]
        block = match[1]
        for key, value in [('CivType', 'CIVILIZATION_KOREA'), ('LeaderType', 'LEADER_WANGKON'),
                           ('Team', 30), ('PlayableCiv', int(turn != 0)), ('MinorNationStatus', 0),
                           ('LeaderName', 'TXT_KEY_KOREA_LEADER_' + str(turn)),
                           ('StartingX', capital[0]), ('StartingY', capital[1]),
                           ('StartingGold', 80 if turn <= 87 else 200 if turn < 271 else 400)]:
            block = field(block, key, value)
        if turn >= 181:
            block = field(block, 'StateReligion', 'RELIGION_' +
                          ('CONFUCIANISM' if turn == 271 else 'BUDDHISM'))
        return 'BeginPlayer' + block + 'EndPlayer'

    text = re.sub(r'BeginPlayer\b(.*?)EndPlayer', player, text, flags=re.S)
    teams = iter(range(len(re.findall(r'BeginTeam\b', text))))

    def team(match):
        owner = next(teams)
        if owner != KOREA:
            return match[0]
        lines = ['BeginTeam']
        if turn:
            lines += ['\tTech=TECH_' + t for t in techs(turn)]
            lines += ['\tContactWithTeam=2', '\tContactWithTeam=8']
        return '\n'.join(lines + ['EndTeam'])

    text = re.sub(r'BeginTeam\b(.*?)EndTeam', team, text, flags=re.S)
    additions = {}
    if turn == 87:
        additions[capital] = unit('WORKER') + unit('SETTLER')
        additions[capital] += unit('ARCHER', 'CITY_DEFENSE') * 3 + unit('SPEARMAN', 'COUNTER') * 2
        additions[(110, 48)] = unit('WORKBOAT', 'WORKER_SEA')
    elif turn in (181, 211):
        for pos in ((109, 48), (110, 45)):
            buildings = ['GRANARY', 'BARRACKS', 'WALLS', 'LIBRARY']
            if pos == capital:
                buildings.append('PALACE')
            if turn == 211:
                buildings += ['FORGE', 'MARKET', 'BUDDHIST_TEMPLE']
            additions[pos] = city(names[pos], 4 if turn == 181 else 5, buildings, 'BUDDHISM')
            defender = 'ARCHER' if turn == 181 else 'LONGBOWMAN'
            additions[pos] += unit(defender, 'CITY_DEFENSE') * 2
            additions[pos] += unit('SPEARMAN', 'COUNTER')
        additions[capital] += unit('WORKER') * 2 + unit('SWORDSMAN', 'ATTACK') * 2
        additions[(111, 46)] = unit('GALLEY', 'ASSAULT_SEA') + unit('WORKBOAT', 'WORKER_SEA')
    elif turn == 271:
        for pos, pop in [(capital, 7), ((108, 49), 4)]:
            buildings = ['GRANARY', 'BARRACKS', 'WALLS', 'LIBRARY', 'FORGE', 'MARKET',
                         'CONFUCIAN_TEMPLE']
            if pos == capital:
                buildings += ['PALACE', 'KOREAN_SEOWON']
            additions[pos] = city(names[pos], pop, buildings, 'CONFUCIANISM')
            additions[pos] += unit('LONGBOWMAN', 'CITY_DEFENSE') * 2
            additions[pos] += unit('PIKEMAN', 'COUNTER')
        additions[capital] += unit('WORKER') * 2 + unit('KOREAN_HWACHA', 'ATTACK_CITY') * 2
        additions[(111, 46)] = unit('CARAVEL', 'EXPLORE_SEA') + unit('GALLEY', 'ASSAULT_SEA')

    def plot(match):
        block = match[1]
        pos = tuple(map(int, re.search(r'x=(\d+),y=(\d+)', block).groups()))
        # Replace the original independent Hanseong and previous generated starts.
        if 108 <= pos[0] <= 110 and 45 <= pos[1] <= 49:
            block = re.sub(r'\s*BeginCity\b.*?EndCity', '', block, flags=re.S)
            block = re.sub(r'\s*BeginUnit\b.*?EndUnit', '', block, flags=re.S)
            block = re.sub(r'^[ \t]*Player\d+Culture=[^\r\n]*', '', block, flags=re.M)
        else:
            block = re.sub(r'\s*BeginUnit\b(?:(?!EndUnit).)*UnitOwner=30\b.*?EndUnit', '', block, flags=re.S)
        # No coastline expansion: food and an accessible metal support two cities.
        for location, bonus in [((109, 46), 'WHEAT'), ((110, 47), 'COPPER'), ((111, 47), 'FISH')]:
            if pos == location:
                block = field(block, 'BonusType', 'BONUS_' + bonus)
        if turn >= 181 and 108 <= pos[0] <= 110 and 45 <= pos[1] <= 49:
            if 'PlotType=3' not in block and 'PlotType=0' not in block:
                block = field(block, 'RouteType', 'ROUTE_ROAD')
        block += additions.get(pos, '')
        return 'BeginPlot' + block + 'EndPlot'

    return re.sub(r'BeginPlot\b(.*?)EndPlot', plot, text, flags=re.S)


def main():
    paths = sorted((MOD / 'PublicMaps').glob('*.CivBeyondSwordWBSave'))
    paths.append(ROOT / 'tools/scenario_templates/1453_ad_base.CivBeyondSwordWBSave')
    for path in paths:
        text = path.read_text(encoding='utf-8-sig')
        # Keep the generator's historical base on the same slot/resource layout.
        from american_scenarios import apply_american_starts
        result = apply_american_starts(apply_korea(text))
        path.write_text(result, encoding='utf-8', newline='\r\n')
        print(path.relative_to(ROOT))


if __name__ == '__main__':
    main()
