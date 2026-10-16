# Observer scenario setup, compatible with Civ4's Python 2.4.
# Called by the WB loader before GameStart; normal launches return immediately.
import os


def configure_players(description, filename):
    path = os.environ.get('AWAKENED_RFC_OBSERVER_CONFIG')
    token = os.environ.get('AWAKENED_RFC_OBSERVER_TOKEN')
    if not path or not token:
        return
    import ConfigParser
    parser = ConfigParser.RawConfigParser()
    parser.read(path)
    if (parser.get('Observer', 'Token') != token or
            parser.getint('Observer', 'ProcessId') != os.getpid()):
        return
    if (not parser.has_option('Observer', 'Unattended') or
            not parser.getboolean('Observer', 'Unattended')):
        return
    scenario = '3000bc'
    if parser.has_option('Observer', 'Scenario'):
        scenario = parser.get('Observer', 'Scenario')
    expected = {'3000bc': ('start 1 - 3000 bc.civbeyondswordwbsave', 0, 26, 'CIVILIZATION_AMERICA'),
                '800bc': ('start 2 - 800 bc.civbeyondswordwbsave', 87, 26, 'CIVILIZATION_AMERICA'),
                '600ad': ('start 3 - 600 ad.civbeyondswordwbsave', 181, 2, 'CIVILIZATION_CHINA')}
    if scenario not in expected:
        raise ValueError('Unsupported observer scenario/mode')
    name, turn, active, civ = expected[scenario]
    if os.path.basename(str(filename)).lower() != name:
        raise ValueError('Unattended observer loaded an unexpected scenario')
    if description.gameDesc.gameTurn != turn or description.gameDesc.iStartYear != -3000:
        raise ValueError('Unattended observer scenario turn/year mismatch')
    players = description.playersDesc
    if players[active].civType != civ:
        raise ValueError('Unattended observer civilization slot mismatch')
    # Restrict the setup selector, not civilization participation in the game.
    # Every other civilization remains present and follows its ordinary spawn.
    for i in range(len(players)):
        players[i].isPlayableCiv = int(i == active)
    players[active].handicap = 'HANDICAP_PRINCE'
    description.gameDesc.speedType = 'GAMESPEED_NORMAL'
    output = parser.get('Observer', 'OutputDirectory')
    marker = os.path.join(output, 'setup-ready.json')
    if not os.path.exists(marker):
        temporary = marker + '.tmp'
        handle = open(temporary, 'wb')
        try:
            handle.write('{"phase":"scenario_setup","pid":%d}' % os.getpid())
        finally:
            handle.close()
        os.rename(temporary, marker)
