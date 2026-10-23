# Mississippian homeland and authored American starts. Python 2.4 compatible.
from CvPythonExtensions import CyGlobalContext
import Consts as con
import StartingCivics
import cPickle as pickle

CITY_NAMES = ((23, 45, "Cahokia"), (25, 44, "Etowah"), (22, 43, "Natchez"),
              (21, 45, "Spiro"), (24, 44, "Moundville"), (25, 43, "Ocmulgee"),
              (24, 47, "Angel Mounds"), (23, 44, "Kincaid"))


def cityNameMap():
    result = [["-1" for x in range(124)] for y in range(68)]
    for x in range(18, 30):
        for y in range(40, 51):
            best = CITY_NAMES[0]
            distance = 100000
            for anchor in CITY_NAMES:
                value = (x-anchor[0])*(x-anchor[0]) + (y-anchor[1])*(y-anchor[1])
                if value < distance:
                    best, distance = anchor, value
            result[67-y][x] = best[2]
    return tuple(tuple(row) for row in result)


def grantTechs():
    gc = CyGlobalContext()
    player = gc.getPlayer(con.iMississippians)
    team = gc.getTeam(player.getTeam())
    for name in ("AGRICULTURE", "THE_WHEEL", "POTTERY", "HUNTING", "MYSTICISM",
                 "FISHING", "ARCHERY", "MINING", "MASONRY"):
        team.setHasTech(gc.getInfoTypeForString("TECH_" + name), True,
                        con.iMississippians, False, False)


def configureRegions(argsList=None):
    # The 1453 capital is southeastern; earlier games begin around Cahokia.
    gc = CyGlobalContext()
    city = gc.getPlayer(con.iMississippians).getCapitalCity()
    if not city.isNone():
        con.tCapitals[con.iMississippians] = (city.getX(), city.getY())
        con.tReserveCapitals[con.iMississippians] = con.tCapitals[con.iMississippians]


def setup():
    gc = CyGlobalContext()
    turn = gc.getGame().getStartTurn()
    configureRegions()
    player = gc.getPlayer(con.iMississippians)
    if player.isAlive():
        grantTechs()
        StartingCivics.apply(con.iMississippians)
    # These civilizations use standard victories when earlier historical
    # objectives are unavailable. Do not inherit another slot's goals.
    data = pickle.loads(gc.getGame().getScriptData())
    data['lBirthTurnModifier'][con.iMississippians] = 0
    data['lGoals'][con.iMississippians] = [0, 0, 0]
    if turn in (87, 181, 211):
        maya = gc.getPlayer(con.iMaya)
        if maya.isAlive():
            StartingCivics.apply(con.iMaya)
            if turn >= 181:
                data['lGoals'][con.iMaya] = [0, 0, 0]
    gc.getGame().setScriptData(pickle.dumps(data))
