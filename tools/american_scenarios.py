"""Author Maya starts and the dedicated Mississippian player in RFC maps."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / 'Awakened RFC/PublicMaps'
MISSISSIPPIANS = 31
EARLY_TECHS = ('AGRICULTURE', 'THE_WHEEL', 'POTTERY', 'HUNTING', 'MYSTICISM')
CLASSICAL_TECHS = EARLY_TECHS + ('FISHING', 'ARCHERY', 'MINING', 'MASONRY',
                                'WRITING', 'POLYTHEISM', 'PRIESTHOOD', 'CALENDAR',
                                'MONARCHY', 'MATHEMATICS', 'CONSTRUCTION')
MISSISSIPPIAN_TECHS = EARLY_TECHS + ('FISHING', 'ARCHERY', 'MINING', 'MASONRY')


def field(block, key, value):
    line = '\t' + key + '=' + str(value)
    pattern = r'^[ \t]*' + re.escape(key) + r'=[^\r\n]*'
    if re.search(pattern, block, re.M):
        return re.sub(pattern, lambda _: line, block, count=1, flags=re.M)
    return block.rstrip() + '\n' + line + '\n'


def migrate_slots(text):
    players = re.findall(r'BeginPlayer\b(.*?)EndPlayer', text, re.S)
    if len(players) == 38:
        if 'CIVILIZATION_NATIVE_AMERICA' not in players[31]:
            raise ValueError('Mississippian slot is occupied')
        return text
    if len(players) != 37:
        raise ValueError('Expected the existing 37-player scenario layout')
    scalar = (r'\b(Team|UnitOwner|CityOwner|OriginalOwner|PreviousOwner|Owner|'
              r'ContactWithTeam|AtWar|OpenBordersWithTeam|DefensivePactWithTeam|'
              r'VassalOfTeam|PermanentWarPeace)=(\d+)')
    text = re.sub(scalar, lambda m: m[1] + '=' + str(int(m[2]) + (int(m[2]) >= 31)), text)
    text = re.sub(r'\bPlayer(\d+)Culture', lambda m: 'Player' + str(int(m[1]) + (int(m[1]) >= 31)) + 'Culture', text)
    text = re.sub(r'\bTeamReveal=([^\r\n]*)', lambda m: 'TeamReveal=' + ','.join(
        str(int(n) + (int(n) >= 31)) for n in m[1].split(',') if n.strip()) + ',', text)
    player = ('BeginPlayer\n\tTeam=31\n\tCivType=CIVILIZATION_NATIVE_AMERICA\n'
              '\tLeaderType=LEADER_SITTING_BULL\n\tPlayableCiv=1\n'
              '\tMinorNationStatus=0\n\tHandicap=HANDICAP_PRINCE\nEndPlayer')
    for kind, new in (('Team', 'BeginTeam\nEndTeam'), ('Player', player)):
        matches = list(re.finditer('Begin' + kind + r'\b.*?End' + kind, text, re.S))
        at = matches[31].start()
        text = text[:at] + new + '\n' + text[at:]
    return text


def unit(kind, owner, ai=None):
    lines = ['\tBeginUnit', '\t\tUnitType=UNIT_' + kind + ', UnitOwner=' + str(owner)]
    if ai:
        lines.append('\t\tUnitAIType=UNITAI_' + ai)
    return '\n' + '\n'.join(lines + ['\tEndUnit']) + '\n'


def city(name, owner, population, capital=False):
    buildings = ['GRANARY', 'OBELISK']
    if capital:
        buildings.append('PALACE')
    lines = ['\tBeginCity', '\t\tCityOwner=' + str(owner), '\t\tCityName=' + name,
             '\t\tCityPopulation=' + str(population)]
    lines += ['\t\tBuildingType=BUILDING_' + b for b in buildings]
    lines += ['\t\tPlayer%dCulture=100' % owner, '\tEndCity']
    return '\n' + '\n'.join(lines) + '\n'


def apply_american_starts(text):
    text = migrate_slots(text)
    turn = int(re.search(r'\bGameTurn=(\d+)', text)[1])
    players = iter(range(38))
    def player(match):
        owner = next(players)
        block = match[1]
        if owner == 10 and turn in (87, 181, 211):
            block = field(block, 'PlayableCiv', 1)
            block = field(block, 'MinorNationStatus', 0)
        if owner == MISSISSIPPIANS:
            for key, value in (('PlayableCiv', int(turn != 0)), ('MinorNationStatus', 0),
                               ('CivDesc', 'TXT_KEY_MISS_DESC'),
                               ('CivShortDesc', 'TXT_KEY_MISS'),
                               ('CivAdjective', 'TXT_KEY_MISS_ADJ'),
                               ('LeaderName', 'TXT_KEY_MISS_LEADER'),
                               ('StartingX', 25 if turn == 271 else 23),
                               ('StartingY', 44 if turn == 271 else 45)):
                block = field(block, key, value)
        return 'BeginPlayer' + block + 'EndPlayer'
    text = re.sub(r'BeginPlayer\b(.*?)EndPlayer', player, text, flags=re.S)
    teams = iter(range(38))
    def team(match):
        owner = next(teams)
        block = match[1]
        techs = ()
        if owner == 10 and turn in (87, 181, 211):
            techs = EARLY_TECHS if turn == 87 else CLASSICAL_TECHS
        if owner == MISSISSIPPIANS and turn >= 211:
            techs = MISSISSIPPIAN_TECHS
        for tech in techs:
            if not re.search(r'\bTech=TECH_' + tech + r'\b', block):
                block += '\n\tTech=TECH_' + tech + '\n'
        return 'BeginTeam' + block + 'EndTeam'
    text = re.sub(r'BeginTeam\b(.*?)EndTeam', team, text, flags=re.S)
    settlements = {}
    if turn == 87:
        settlements[(22, 35)] = ('Nakbe', 10, 2, True)
    elif turn == 211:
        settlements[(23, 45)] = ('Cahokia', MISSISSIPPIANS, 2, True)
    elif turn == 271:
        settlements[(25, 44)] = ('Etowah', MISSISSIPPIANS, 4, True)
        settlements[(22, 43)] = ('Natchez', MISSISSIPPIANS, 3, False)
    def plot(match):
        block = match[1]
        pos = tuple(map(int, re.search(r'x=(\d+),y=(\d+)', block).groups()))
        # Transfer the two established Maya settlements and their own garrisons.
        if turn in (181, 211) and ('CityName=Yax Mutal' in block or 'CityName=Chich' in block):
            block = re.sub(r'(CityOwner|UnitOwner)=34\b', r'\g<1>=10', block)
            block = block.replace('Player34Culture=', 'Player10Culture=')
            is_capital = 'CityName=Yax Mutal' in block if turn == 181 else 'CityName=Chich' in block
            if is_capital and 'BuildingType=BUILDING_PALACE' not in block:
                block = block.replace('\tEndCity', '\t\tBuildingType=BUILDING_PALACE\n\tEndCity')
        if pos in settlements:
            name, owner, population, capital = settlements[pos]
            if not re.search(r'PlotType=[12]\b', block):
                raise ValueError('Settlement is not on passable land: ' + str(pos))
            block = re.sub(r'\s*Begin(?:City|Unit)\b.*?End(?:City|Unit)', '', block, flags=re.S)
            block = re.sub(r'^[ \t]*(?:FeatureType|Player\d+Culture)=[^\r\n]*', '', block, flags=re.M)
            block += city(name, owner, population, capital)
            guard = 'WARRIOR' if turn == 87 else 'ARCHER'
            block += unit(guard, owner, 'CITY_DEFENSE') + unit(guard, owner, 'CITY_DEFENSE')
            if capital:
                block += unit('WORKER', owner) + unit('SCOUT', owner, 'EXPLORE')
        return 'BeginPlot' + block + 'EndPlot'
    return re.sub(r'BeginPlot\b(.*?)EndPlot', plot, text, flags=re.S)


def main():
    for path in sorted(MAPS.glob('Start *.CivBeyondSwordWBSave')):
        path.write_text(apply_american_starts(path.read_text(encoding='utf-8-sig')),
                        encoding='utf-8', newline='\r\n')
        print(path.name)
    template = ROOT / 'tools/scenario_templates/1453_ad_base.CivBeyondSwordWBSave'
    template.write_text(migrate_slots(template.read_text(encoding='utf-8-sig')),
                        encoding='utf-8', newline='\r\n')


if __name__ == '__main__':
    main()
