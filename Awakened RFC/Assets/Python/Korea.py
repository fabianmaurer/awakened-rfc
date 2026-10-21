# Korean starts and historical objectives. Keep compatible with Python 2.4.
from CvPythonExtensions import CyGlobalContext
import Consts as con
import StartingCivics


# Regional names on RFC's compressed peninsula. Shared with scenario authoring.
CITY_NAMES = ((108, 49, "Uiju"), (109, 50, "Chongjin"),
              (108, 48, "Anju"), (109, 48, "Pyongyang"),
              (108, 47, "Nampo"), (109, 47, "Kaesong"),
              (110, 47, "Chuncheon"), (109, 46, "Hanseong"),
              (110, 46, "Gangneung"), (109, 45, "Jeonju"),
              (110, 45, "Gyeongju"))


# Cover regions around the city anchors, including the western border and
# northern approaches. An adjacent founding tile must not use the generic list.
CITY_NAME_AREA = ((107, 44), (111, 51))
FRONTIER_CITY_NAMES = ((107, 48, "Dalian"), (107, 49, "Dandong"),
                      (107, 50, "Liaoyang"), (108, 51, "Ji'an"),
                      (109, 51, "Hyesan"), (110, 51, "Hoeryong"),
                      (111, 51, "Rason"), (110, 48, "Wonsan"),
                      (109, 49, "Hamhung"))


def cityNameMap(baseMap):
    # Reuse RFC's established geographic vocabulary across China and Manchuria.
    # Extend named regions over gaps, rather than falling back to Seoul or the
    # next unrelated city in Korea's generic civilization list.
    result = [list(row) for row in baseMap]
    areas = (((96, 32), (111, 55)), ((106, 48), (118, 59)))
    for topLeft, bottomRight in areas:
        anchors = []
        for x in range(topLeft[0], bottomRight[0] + 1):
            for y in range(topLeft[1], bottomRight[1] + 1):
                name = baseMap[67-y][x]
                if name != "-1":
                    anchors.append((x, y, name))
        for x in range(topLeft[0], bottomRight[0] + 1):
            for y in range(topLeft[1], bottomRight[1] + 1):
                if result[67-y][x] != "-1":
                    continue
                bestDistance = 100000
                for ax, ay, name in anchors:
                    distance = (x-ax)*(x-ax) + (y-ay)*(y-ay)
                    if distance < bestDistance:
                        bestDistance = distance
                        result[67-y][x] = name
    for x, y, name in regionalCityNames():
        result[67-y][x] = name
    return tuple(tuple(row) for row in result)


def regionalCityNames():
    # Squared tile distance gives each anchor its surrounding region. The
    # explicit anchor order resolves ties identically on every multiplayer peer.
    names = []
    anchors = CITY_NAMES + FRONTIER_CITY_NAMES
    topLeft, bottomRight = CITY_NAME_AREA
    for x in range(topLeft[0], bottomRight[0] + 1):
        for y in range(topLeft[1], bottomRight[1] + 1):
            best = None
            bestDistance = 100000
            for ax, ay, name in anchors:
                distance = (x-ax)*(x-ax) + (y-ay)*(y-ay)
                if distance < bestDistance:
                    bestDistance = distance
                    best = name
            names.append((x, y, best))
    return names


EARLY_TECHS = ("AGRICULTURE", "FISHING", "SAILING", "THE_WHEEL", "POTTERY",
               "HUNTING", "ARCHERY", "MINING", "BRONZE_WORKING")
CLASSICAL_TECHS = ("MYSTICISM", "POLYTHEISM", "MEDITATION", "PRIESTHOOD",
                   "MONARCHY", "MASONRY", "ANIMAL_HUSBANDRY", "IRON_WORKING",
                   "METAL_CASTING", "WRITING", "ALPHABET", "MATHEMATICS",
                   "CALENDAR", "CURRENCY", "CODE_OF_LAWS", "CONSTRUCTION",
                   "HORSEBACK_RIDING")
MEDIEVAL_TECHS = ("CIVIL_SERVICE", "FEUDALISM", "MACHINERY", "COMPASS")
RENAISSANCE_TECHS = ("MONOTHEISM", "THEOLOGY", "PHILOSOPHY", "PAPER",
                     "EDUCATION", "PRINTING_PRESS", "ENGINEERING", "GUILDS",
                     "BANKING", "GUNPOWDER", "OPTICS")


def grantTechs():
    gc = CyGlobalContext()
    player = gc.getPlayer(con.iKorea)
    team = gc.getTeam(player.getTeam())
    year = gc.getGame().getGameTurnYear()
    techs = EARLY_TECHS
    if year >= 600:
        techs += CLASSICAL_TECHS
    if year >= 900:
        techs += MEDIEVAL_TECHS
    if year >= 1453:
        techs += RENAISSANCE_TECHS
    for name in techs:
        team.setHasTech(gc.getInfoTypeForString("TECH_" + name), True,
                        con.iKorea, False, False)


def setup(victory):
    gc = CyGlobalContext()
    if gc.getGame().getStartTurn() == 0:
        return
    grantTechs()
    StartingCivics.apply(con.iKorea)
    player = gc.getPlayer(con.iKorea)
    start = gc.getGame().getStartTurn()
    capital = (109, 48)
    if start == 211:
        capital = (110, 45)
    elif start == 271:
        capital = (109, 46)
    palace = gc.getInfoTypeForString("BUILDING_PALACE")
    city, iterator = player.firstCity(False)
    while city and not city.isNone():
        city.setNumRealBuilding(palace, int((city.getX(), city.getY()) == capital))
        city, iterator = player.nextCity(iterator, False)
    configureRegions()
    # A late scenario cannot retroactively complete the unification deadline.
    if gc.getGame().getGameTurnYear() > 1000:
        victory.setGoal(con.iKorea, 0, 0)


def configureRegions(argsList=None):
    # Restore the live capital after the shared regional reset, including loads.
    city = CyGlobalContext().getPlayer(con.iKorea).getCapitalCity()
    if not city.isNone():
        con.tCapitals[con.iKorea] = (city.getX(), city.getY())


def checkGoals(victory):
    gc = CyGlobalContext()
    player = gc.getPlayer(con.iKorea)
    if not player.isAlive():
        return
    year = gc.getGame().getGameTurnYear()
    coreCities = 0
    universities = 0
    city, iterator = player.firstCity(False)
    seowon = gc.getInfoTypeForString("BUILDING_KOREAN_SEOWON")
    while city and not city.isNone():
        if 108 <= city.getX() <= 110 and 45 <= city.getY() <= 49:
            coreCities += 1
        if city.getNumRealBuilding(seowon) > 0:
            universities += 1
        city, iterator = player.nextCity(iterator, False)
    foreignCoreCity = False
    for x in range(108, 111):
        for y in range(45, 50):
            plot = gc.getMap().plot(x, y)
            if plot.isCity() and plot.getOwner() != con.iKorea:
                foreignCoreCity = True
    if victory.getGoal(con.iKorea, 0) == -1:
        if year <= 1000 and coreCities >= 2 and not foreignCoreCity:
            victory.setGoal(con.iKorea, 0, 1)
        elif year > 1000:
            victory.setGoal(con.iKorea, 0, 0)
    if victory.getGoal(con.iKorea, 1) == -1:
        if year <= 1600 and universities >= 2:
            victory.setGoal(con.iKorea, 1, 1)
        elif year > 1600:
            victory.setGoal(con.iKorea, 1, 0)
    if year >= 1900 and victory.getGoal(con.iKorea, 2) == -1:
        team = gc.getTeam(player.getTeam())
        independent = True
        for iTeam in range(gc.getMAX_CIV_TEAMS()):
            if team.isVassal(iTeam):
                independent = False
        victory.setGoal(con.iKorea, 2, int(independent and coreCities >= 2))
