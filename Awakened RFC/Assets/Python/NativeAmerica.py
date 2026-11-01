# Mississippian homeland and authored American starts. Python 2.4 compatible.
from CvPythonExtensions import CyGlobalContext
import ScenarioGeography as geo
import Consts as con
import StartingCivics
import cPickle as pickle

geo.bind(globals(), 'CITY_NAMES', 'NativeAmerica.CITY_NAMES')
geo.bind(globals(), 'ADENA_CITY_NAMES', 'NativeAmerica.ADENA_CITY_NAMES')


def cityNameMap(adena=False):
    names = CITY_NAMES
    if adena:
        names = ADENA_CITY_NAMES
    result = [["-1" for x in range(geo.width())] for y in range(geo.height())]
    for x in range(*geo.value('NativeAmerica.range_1')):
        for y in range(*geo.value('NativeAmerica.range_2')):
            best = names[0]
            distance = 100000
            for anchor in names:
                value = (x-anchor[0])*(x-anchor[0]) + (y-anchor[1])*(y-anchor[1])
                if value < distance:
                    best, distance = anchor, value
            result[(geo.height() - 1) - y][x] = best[2]
    return tuple(tuple(row) for row in result)


def grantTechs():
    gc = CyGlobalContext()
    player = gc.getPlayer(con.iMississippians)
    if player.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ADENA"):
        return # The scenario supplies the smaller Early Woodland technology package.
    team = gc.getTeam(player.getTeam())
    for name in ("AGRICULTURE", "THE_WHEEL", "POTTERY", "HUNTING", "MYSTICISM",
                 "FISHING", "ARCHERY", "MINING", "MASONRY"):
        team.setHasTech(gc.getInfoTypeForString("TECH_" + name), True,
                        con.iMississippians, False, False)


def configureRegions(argsList=None):
    # Restore scenario-specific birth and naming data on both new games and loads.
    gc = CyGlobalContext()
    adena = gc.getPlayer(con.iMississippians).getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ADENA")
    birth = 211
    capital = geo.value('NativeAmerica.configureRegions.capital_1')
    if adena:
        birth = 87
        capital = geo.value('NativeAmerica.configureRegions.capital_2')
    con.tBirth = con.tBirth[:con.iMississippians] + (birth,) + con.tBirth[con.iMississippians+1:]
    import CityNameManager
    CityNameManager.tCityMap = CityNameManager.tCityMap[:31] + (cityNameMap(adena),) + CityNameManager.tCityMap[32:]
    city = gc.getPlayer(con.iMississippians).getCapitalCity()
    if not city.isNone():
        capital = (city.getX(), city.getY())
    con.tCapitals[con.iMississippians] = capital
    con.tReserveCapitals[con.iMississippians] = capital


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
