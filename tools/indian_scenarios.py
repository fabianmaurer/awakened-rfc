"""Maintain XL Indian civilizations and five reserved major-player slots.

Old scenarios receive empty slots only; their existing owners shift with the
DLL's minor-player IDs. Gameplay additions are limited to the two XL starts.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'Awakened RFC'
sys.path.insert(0, str(MOD / 'Assets/Python'))
from IndianCivsData import CIVS, HARAPPAN_CITIES, HARAPPAN_DRYING


def apply_indian_civs(text, xl=False):
    players = re.findall(r'BeginPlayer\b.*?EndPlayer', text, re.S)
    if len(players) == 39:
        scalar = (r'\b(Team|UnitOwner|CityOwner|OriginalOwner|PreviousOwner|Owner|'
            r'ContactWithTeam|AtWar|OpenBordersWithTeam|DefensivePactWithTeam|'
            r'VassalOfTeam|PermanentWarPeace)=(\d+)')
        text = re.sub(scalar, lambda m: m[1] + '=' + str(int(m[2]) + 5 * (int(m[2]) >= 33)), text)
        text = re.sub(r'\bPlayer(\d+)Culture', lambda m: 'Player%dCulture' %
            (int(m[1]) + 5 * (int(m[1]) >= 33)), text)
        text = re.sub(r'\bTeamReveal=([^\r\n]*)', lambda m: 'TeamReveal=' + ','.join(
            str(int(n) + 5 * (int(n) >= 33)) for n in m[1].split(',') if n.strip()) + ',', text)
        for kind in ('Team', 'Player'):
            matches = list(re.finditer('Begin' + kind + r'\b.*?End' + kind, text, re.S))
            if kind == 'Team': blocks = ['BeginTeam\nEndTeam'] * 5
            else: blocks = [empty_player(i) for i in range(33, 38)]
            at = matches[33].start()
            text = text[:at] + '\n'.join(blocks) + '\n' + text[at:]
    elif len(players) != 44:
        raise ValueError('Expected 39 or 44 player slots')
    if not xl: return text
    turn = int(re.search(r'\bGameTurn=(\d+)', text)[1])
    late = turn > 0
    oldPlayers = re.findall(r'BeginPlayer\b.*?EndPlayer', text, re.S)
    oldTeams = re.findall(r'BeginTeam\b.*?EndTeam', text, re.S)
    inheritedTeam = ''
    inheritedPlayer = ''
    if late:
        inheritedSlot = 33
        if 'CivType=CIVILIZATION_INDIA' in oldPlayers[1]: inheritedSlot = 1
        inheritedTeam, inheritedPlayer = oldTeams[inheritedSlot], oldPlayers[inheritedSlot]
        inheritedTeam = '\n'.join(line.rstrip() for line in inheritedTeam.splitlines())
    colors = ('PURPLE', 'DARK_RED', 'DARK_GREEN', 'LIGHT_BLUE', 'YELLOW')
    for offset, entry in enumerate(CIVS):
        civ, short, birth, year, capital, _, _, _, _ = entry
        slot = 33 + offset
        playable = int(turn >= birth * 2)  # XL uses two game turns per reference turn.
        player = ('BeginPlayer\n\tTeam=%d\n\tCivType=CIVILIZATION_%s\n'
            '\tLeaderType=LEADER_%s\n\tLeaderName=TXT_KEY_LEADER_%s\n'
            '\tColor=PLAYERCOLOR_%s\n\tPlayableCiv=%d\n\tMinorNationStatus=0\n'
            '\tHandicap=HANDICAP_PRINCE\n\tStartingX=%d\n\tStartingY=%d\nEndPlayer') % (
            slot, civ, civ, short, colors[offset], playable, capital[0], capital[1])
        if late and offset == 0:
            fields = re.findall(r'^[ \t]*(?:CivicOption=[^\r\n]*|StateReligion=[^\r\n]*|StartingGold=[^\r\n]*)', inheritedPlayer, re.M)
            player = player.replace('EndPlayer', '\n'.join(fields) + '\nEndPlayer')
        text = replace_block(text, 'Player', slot, player)
        techs = ()
        if offset == 0:
            techs = ('AGRICULTURE', 'MYSTICISM')
        team = 'BeginTeam\n' + ''.join('\tTech=TECH_' + t + '\n' for t in techs) + 'EndTeam'
        text = replace_block(text, 'Team', slot, team)
    if late:
        # The 800 BC Gangetic polity inherits the old India cities and troops.
        text = re.sub(r'\b(UnitOwner|CityOwner|OriginalOwner|PreviousOwner)=1\b', r'\g<1>=33', text)
        text = re.sub(r'\bPlayer1Culture', 'Player33Culture', text)
        text = replace_block(text, 'Team', 33, inheritedTeam)
        text = replace_block(text, 'Team', 1, 'BeginTeam\nEndTeam')
        text = replace_block(text, 'Player', 1, empty_player(1))
        text = re.sub(r'\b(ContactWithTeam|AtWar|OpenBordersWithTeam|DefensivePactWithTeam|VassalOfTeam|PermanentWarPeace)=1\b', r'\g<1>=33', text)
        text = re.sub(r'\bTeamReveal=([^\r\n]*)', lambda m: 'TeamReveal=' + ','.join(
            str(33 if int(n) == 1 else int(n)) for n in m[1].split(',') if n.strip()) + ',', text)
        text = re.sub(r'BeginCity\b.*?EndCity', gangetic_palace, text, flags=re.S)
    else:
        text = replace_block(text, 'Team', 1, 'BeginTeam\n\tTech=TECH_AGRICULTURE\nEndTeam')
        text = add_harappa_cities(text)
        text = add_ganges_units(text)
    return text


def empty_player(slot):
    return ('BeginPlayer\n\tTeam=%d\n\tCivType=NONE\n\tLeaderType=NONE\n'
        '\tPlayableCiv=0\n\tMinorNationStatus=0\n\tHandicap=HANDICAP_PRINCE\nEndPlayer') % slot


def replace_block(text, kind, index, block):
    match = list(re.finditer('Begin' + kind + r'\b.*?End' + kind, text, re.S))[index]
    return text[:match.start()] + block + text[match.end():]


def gangetic_palace(match):
    block = match[0]
    if 'CityOwner=33' not in block: return block
    block = re.sub(r'^[ \t]*BuildingType=BUILDING_PALACE[^\n]*\n', '', block, flags=re.M)
    if 'Patliputra' in block or 'Pataliputra' in block:
        block = block.replace('EndCity', '\t\tBuildingType=BUILDING_PALACE, BuildDate=-800\n\tEndCity')
    return block


def add_harappa_cities(text):
    """Author established Indus cities without duplicating them on reruns."""
    cities = {site: (name, population) for name, site, population in HARAPPAN_CITIES}
    def plot(match):
        block = match[1]
        coordinates = re.search(r'\bx=(\d+),y=(\d+)\b', block)
        site = tuple(map(int, coordinates.groups()))
        # Remove retired opening sites before authoring the new city positions.
        if site not in cities:
            for name, position, population in HARAPPAN_CITIES:
                block = re.sub(r'\s*BeginCity\b(?:(?!EndCity).)*\bCityName=' +
                               re.escape(name) + r'\b(?:(?!EndCity).)*EndCity', '', block, flags=re.S)
            return 'BeginPlot' + block + 'EndPlot'
        name, population = cities[site]
        if 'BeginCity' in block:
            block = re.sub(r'\bCityPopulation=\d+', 'CityPopulation=%d' % population, block)
        else:
            palace = '\t\tBuildingType=BUILDING_PALACE\n' if name == 'Harappa' else ''
            block += ('\n\tBeginCity\n\t\tCityOwner=1\n\t\tCityName=%s\n'
                      '\t\tCityPopulation=%d\n%s\tEndCity\n') % (name, population, palace)
        return 'BeginPlot' + block + 'EndPlot'
    return re.sub(r'BeginPlot\b(.*?)EndPlot', plot, text, flags=re.S)


def add_ganges_units(text):
    # Idempotent authoring: opening troops are supplied here, not by a second birth.
    text = re.sub(r'\s*BeginUnit\b(?:(?!EndUnit).)*\bUnitOwner=33\b(?:(?!EndUnit).)*EndUnit', '', text, flags=re.S)
    def plot(match):
        block = match[1]
        if not re.search(r'\bx=150,y=65\b', block): return match[0]
        for unit, ai in (('SETTLER', 'SETTLE'), ('WARRIOR', 'CITY_DEFENSE')):
            block += '\n\tBeginUnit\n\t\tUnitType=UNIT_%s, UnitOwner=33\n\t\tUnitAIType=UNITAI_%s\n\tEndUnit\n' % (unit, ai)
        return 'BeginPlot' + block + 'EndPlot'
    return re.sub(r'BeginPlot\b(.*?)EndPlot', plot, text, flags=re.S)


if __name__ == '__main__':
    for path in sorted((MOD / 'PublicMaps').glob('*.CivBeyondSwordWBSave')):
        text = path.read_text(encoding='utf-8-sig')
        updated = apply_indian_civs(text, ' XL ' in path.name)
        if updated != text: path.write_text(updated, encoding='utf-8', newline='\n')
