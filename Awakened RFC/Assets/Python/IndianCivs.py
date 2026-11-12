"""XL Indian starts, regional identities and historical objectives. Python 2.4."""
from CvPythonExtensions import *
import ScenarioGeography as geo
import Consts as con
import IndianCivsData as data
import StartingCivics

gc = CyGlobalContext()
SLOTS = range(con.iGanges, con.iVijayanagara + 1)


def enabled():
    return geo.base_profile_name() == 'Earth200x110'


def isIndian(player):
    return enabled() and player in SLOTS and gc.getPlayer(player).getCivilizationType() >= 0


def grantTechs(player):
    team = gc.getTeam(gc.getPlayer(player).getTeam())
    techs = ('AGRICULTURE', 'MYSTICISM')
    if player != con.iGanges or gc.getGame().getStartTurn() > 0:
        techs += ('THE_WHEEL', 'MINING', 'POTTERY', 'ANIMAL_HUSBANDRY', 'HUNTING',
            'ARCHERY', 'BRONZE_WORKING', 'MASONRY', 'WRITING', 'PRIESTHOOD', 'MONARCHY')
    if player != con.iGanges:
        techs += ('FISHING', 'SAILING', 'IRON_WORKING', 'MATHEMATICS', 'ALPHABET',
            'CURRENCY', 'CALENDAR', 'CODE_OF_LAWS', 'LITERATURE', 'CONSTRUCTION',
            'HORSEBACK_RIDING', 'FEUDALISM', 'CIVIL_SERVICE', 'MACHINERY', 'METAL_CASTING')
    if player == con.iChola:
        techs += ('COMPASS',)
    if player in (con.iDelhi, con.iBengal, con.iVijayanagara):
        techs += ('GUILDS', 'ENGINEERING', 'THEOLOGY', 'PHILOSOPHY', 'PAPER')
    for tech in techs:
        index = gc.getInfoTypeForString('TECH_' + tech)
        if index >= 0: team.setHasTech(index, True, player, False, False)


def setup(victory):
    if not enabled(): return
    if gc.getGame().getStartTurn() > 0:
        grantTechs(con.iGanges)
        StartingCivics.apply(con.iGanges)
    # No goal is silently awarded for the unplayed history of a late scenario.
    year = gc.getGame().getGameTurnYear()
    for player in SLOTS:
        for goal, deadline in enumerate(deadlines(player)):
            if deadline < year: victory.setGoal(player, goal, 0)


def unitType(player, unitClass):
    return gc.getCivilizationInfo(gc.getPlayer(player).getCivilizationType()).getCivilizationUnits(
        gc.getInfoTypeForString('UNITCLASS_' + unitClass))


def makeUnits(player, position, unitClass, number, role):
    unit = unitType(player, unitClass)
    for i in range(number):
        gc.getPlayer(player).initUnit(unit, position[0], position[1], role, DirectionTypes.DIRECTION_SOUTH)


def startingUnits(player, position, rise):
    if player == con.iGanges: return # Both XL scenarios author its opening.
    gc.getPlayer(player).changeGold(200)
    makeUnits(player, position, 'WORKER', 2, UnitAITypes.UNITAI_WORKER)
    makeUnits(player, position, 'SETTLER', 2, UnitAITypes.UNITAI_SETTLE)
    makeUnits(player, position, 'LONGBOWMAN', 3, UnitAITypes.UNITAI_CITY_DEFENSE)
    if player == con.iChola:
        makeUnits(player, position, 'SWORDSMAN', 3, UnitAITypes.UNITAI_ATTACK_CITY)
        makeUnits(player, position, 'SPEARMAN', 2, UnitAITypes.UNITAI_COUNTER)
        sea = rise.findSeaPlots(position, 1, player)
        if sea:
            makeUnits(player, sea, 'GALLEY', 2, UnitAITypes.UNITAI_ASSAULT_SEA)
            makeUnits(player, sea, 'WORKBOAT', 1, UnitAITypes.UNITAI_WORKER_SEA)
    elif player == con.iDelhi:
        makeUnits(player, position, 'KNIGHT', 4, UnitAITypes.UNITAI_ATTACK_CITY)
        makeUnits(player, position, 'TREBUCHET', 2, UnitAITypes.UNITAI_ATTACK_CITY)
    elif player == con.iBengal:
        makeUnits(player, position, 'CROSSBOWMAN', 3, UnitAITypes.UNITAI_COUNTER)
        makeUnits(player, position, 'PIKEMAN', 2, UnitAITypes.UNITAI_COUNTER)
    elif player == con.iVijayanagara:
        makeUnits(player, position, 'PIKEMAN', 4, UnitAITypes.UNITAI_COUNTER)
        makeUnits(player, position, 'TREBUCHET', 2, UnitAITypes.UNITAI_ATTACK_CITY)
    religion = con.iHinduism
    if player in (con.iDelhi, con.iBengal): religion = con.iIslam
    if gc.getGame().isReligionFounded(religion):
        gc.getPlayer(player).convert(religion)
        missionary = con.iJewishMissionary + religion
        gc.getPlayer(player).initUnit(missionary, position[0], position[1],
            UnitAITypes.UNITAI_MISSIONARY, DirectionTypes.DIRECTION_SOUTH)


def deadlines(player):
    return {con.iGanges: (-200, 200, 600), con.iChola: (1100, 1250, 1300),
        con.iDelhi: (1350, 1450, 1500), con.iBengal: (1500, 1600, 1700),
        con.iVijayanagara: (1500, 1600, 1650)}[player]


def checkGoals(victory, player):
    cities = []
    civ = gc.getPlayer(player)
    city, iterator = civ.firstCity(False)
    while city and not city.isNone():
        cities.append(city)
        city, iterator = civ.nextCity(iterator, False)

    def count(west, south, east, north):
        return sum([1 for city in cities if west <= city.getX() <= east and south <= city.getY() <= north])

    partners = set()
    for city in cities:
        for route in range(city.getTradeRoutes()):
            other = city.getTradeCity(route)
            if other and not other.isNone() and other.getOwner() != player:
                if gc.getPlayer(other.getOwner()).getTeam() != civ.getTeam(): partners.add(gc.getPlayer(other.getOwner()).getTeam())
    if player == con.iGanges:
        holy = True
        for religion in (con.iHinduism, con.iBuddhism):
            city = gc.getGame().getHolyCity(religion)
            if city.isNone() or city.getOwner() != player: holy = False
        achieved = (holy, civ.countTotalCulture() >= 2500, count(146,60,154,69) >= 6)
    elif player == con.iChola:
        achieved = (count(143,49,150,56) >= 4,
            count(147,46,153,50) >= 1 and len(partners) >= 3, civ.getGold() >= 3000)
    elif player == con.iDelhi:
        islam = sum([1 for city in cities if city.isHasReligion(con.iIslam)])
        achieved = (count(139,60,154,70) >= 6, islam >= 8,
            gc.getMap().plot(145,65).getOwner() == player and count(141,54,150,60) >= 3)
    elif player == con.iBengal:
        riverCities = sum([1 for city in cities if city.plot().isRiver()])
        achieved = (riverCities >= 6, len(partners) >= 4, civ.getGold() >= 5000)
    else:
        temples = 0
        buildingClass = gc.getInfoTypeForString('BUILDINGCLASS_HINDU_TEMPLE')
        for city in cities:
            for building in range(gc.getNumBuildingInfos()):
                if gc.getBuildingInfo(building).getBuildingClassType() == buildingClass:
                    temples += city.getNumRealBuilding(building)
        achieved = (count(140,49,151,60) >= 4, temples >= 8, civ.countTotalCulture() >= 50000)
    year = gc.getGame().getGameTurnYear()
    for goal, deadline in enumerate(deadlines(player)):
        if victory.getGoal(player, goal) != -1: continue
        if achieved[goal] and year <= deadline: victory.setGoal(player, goal, 1)
        elif year >= deadline: victory.setGoal(player, goal, 0)
