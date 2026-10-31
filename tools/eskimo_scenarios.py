"""Maintain the fantastical Eskimo slot and Arctic starts in authored maps."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / 'Awakened RFC/PublicMaps'
ESKIMOS = 32
START = (122, 61)
# Sparse Arctic food, pelts and mineral deposits; never replace authored bonuses.
ARCTIC_RESOURCES = {
    (119, 59): 'DEER', (115, 63): 'DEER', (118, 60): 'FISH',
    (118, 62): 'SILVER', (111, 64): 'FUR', (100, 63): 'FUR',
    (94, 64): 'DEER', (76, 61): 'FUR', (73, 63): 'FISH',
    (18, 61): 'DEER', (24, 61): 'FUR', (122, 62): 'SILVER',
}


def apply_arctic_resources(text):
    def plot(match):
        block = match[1]
        xy = tuple(map(int, re.search(r'x=(\d+),y=(\d+)', block).groups()))
        bonus = ARCTIC_RESOURCES.get(xy)
        if bonus and 'BonusType=' not in block and 'BeginCity' not in block:
            block = block.rstrip() + '\n\tBonusType=BONUS_' + bonus + '\n'
        return 'BeginPlot' + block + 'EndPlot'
    return re.sub(r'BeginPlot\b(.*?)EndPlot', plot, text, flags=re.S)


def apply_eskimos(text):
    text = apply_arctic_resources(text)
    players = re.findall(r'BeginPlayer\b(.*?)EndPlayer', text, re.S)
    if len(players) == 39:
        if not re.search(r'\bCivType=(?:CIVILIZATION_ESKIMO|NONE)\b', players[ESKIMOS]):
            raise ValueError('Eskimo slot is occupied')
        return apply_availability(text)
    if len(players) != 38:
        raise ValueError('Expected the 38-player pre-Eskimo layout')
    scalar = (r'\b(Team|UnitOwner|CityOwner|OriginalOwner|PreviousOwner|Owner|'
              r'ContactWithTeam|AtWar|OpenBordersWithTeam|DefensivePactWithTeam|'
              r'VassalOfTeam|PermanentWarPeace)=(\d+)')
    text = re.sub(scalar, lambda m: m[1] + '=' + str(int(m[2]) + (int(m[2]) >= 32)), text)
    text = re.sub(r'\bPlayer(\d+)Culture', lambda m: 'Player%dCulture' %
                  (int(m[1]) + (int(m[1]) >= 32)), text)
    text = re.sub(r'\bTeamReveal=([^\r\n]*)', lambda m: 'TeamReveal=' + ','.join(
        str(int(n) + (int(n) >= 32)) for n in m[1].split(',') if n.strip()) + ',', text)
    team = 'BeginTeam\n' + ''.join('\tTech=TECH_' + t + '\n' for t in
        ('FISHING', 'HUNTING')) + 'EndTeam'
    player = ('BeginPlayer\n\tTeam=32\n\tCivType=CIVILIZATION_ESKIMO\n'
              '\tLeaderType=LEADER_ESKIMO\n\tLeaderName=TXT_KEY_ESK_LEADER\n'
              '\tPlayableCiv=1\n\tMinorNationStatus=0\n\tHandicap=HANDICAP_PRINCE\n'
              '\tStartingX=122\n\tStartingY=61\n\tStartingGold=80\nEndPlayer')
    for kind, new in (('Team', team), ('Player', player)):
        matches = list(re.finditer('Begin' + kind + r'\b.*?End' + kind, text, re.S))
        at = matches[32].start()
        text = text[:at] + new + '\n' + text[at:]
    return apply_availability(text)



def apply_availability(text):
    turn = int(re.search(r'\bGameTurn=(\d+)', text)[1])
    players = list(re.finditer(r'BeginPlayer\b.*?EndPlayer', text, re.S))
    player = players[ESKIMOS]
    if turn > 87:
        block = ('BeginPlayer\n\tTeam=32\n\tCivType=NONE\n\tLeaderType=NONE\n'
                 '\tPlayableCiv=0\n\tMinorNationStatus=0\n\tHandicap=HANDICAP_PRINCE\nEndPlayer')
    else:
        block = re.sub(r'PlayableCiv=\d+', 'PlayableCiv=' + str(int(turn == 87)), player[0])
        block = re.sub(r'StartingX=\d+', 'StartingX=%d' % START[0], block)
        block = re.sub(r'StartingY=\d+', 'StartingY=%d' % START[1], block)
    text = text[:player.start()] + block + text[player.end():]
    if turn == 87:
        return apply_starting_units(apply_starting_techs(text))
    text = re.sub(r'\s*BeginUnit\b(?:(?!EndUnit).)*\bUnitOwner=32\b(?:(?!EndUnit).)*EndUnit', '', text, flags=re.S)
    if turn == 0:
        return apply_starting_techs(text)
    teams = list(re.finditer(r'BeginTeam\b.*?EndTeam', text, re.S))
    team = teams[ESKIMOS]
    return text[:team.start()] + 'BeginTeam\nEndTeam' + text[team.end():]


def apply_starting_techs(text):
    if int(re.search(r'\bGameTurn=(\d+)', text)[1]) not in (0, 87):
        return text
    teams = list(re.finditer(r'BeginTeam\b.*?EndTeam', text, re.S))
    team = teams[ESKIMOS]
    block = re.sub(r'^[ \t]*Tech=[^\r\n]*\r?\n', '', team[0], flags=re.M)
    block = block.replace('EndTeam', '\tTech=TECH_FISHING\n\tTech=TECH_HUNTING\nEndTeam')
    return text[:team.start()] + block + text[team.end():]


def apply_starting_units(text):
    text = re.sub(r'\s*BeginUnit\b(?:(?!EndUnit).)*\bUnitOwner=32\b(?:(?!EndUnit).)*EndUnit', '', text, flags=re.S)
    def plot(match):
        block = match[1]
        if not re.search(r'\bx=%d,y=%d\b' % START, block):
            return match[0]
        block = re.sub(r'\s*BeginUnit\b(?:(?!EndUnit).)*\bUnitOwner=32\b(?:(?!EndUnit).)*EndUnit', '', block, flags=re.S)
        if 'BeginCity' in block or 'BeginUnit' in block:
            raise ValueError('Eskimo starting tile is occupied')
        for unit, ai in (('SETTLER', 'SETTLE'), ('ARCTIC_HUNTER', 'WORKER'),
                         ('ARCTIC_HUNTER', 'CITY_DEFENSE'),
                         ('ARCTIC_HUNTER', 'RESERVE')):
            block += ('\n\tBeginUnit\n\t\tUnitType=UNIT_' + unit + ', UnitOwner=32\n'
                      '\t\tUnitAIType=UNITAI_' + ai + '\n\tEndUnit\n')
        return 'BeginPlot' + block + 'EndPlot'
    return re.sub(r'BeginPlot\b(.*?)EndPlot', plot, text, flags=re.S)


if __name__ == '__main__':
    for path in MAPS.glob('*.CivBeyondSwordWBSave'):
        text = path.read_text(encoding='utf-8-sig')
        path.write_text(apply_eskimos(text), encoding='utf-8', newline='\r\n')
