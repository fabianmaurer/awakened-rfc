# Fantastical Eskimo homeland and persistent polar wildlife. Python 2.4.
from CvPythonExtensions import CyGlobalContext, UnitAITypes, DirectionTypes, GameOptionTypes, plotXY
import ScenarioGeography as geo
import Consts as con
import StartingCivics
import cPickle as pickle


def cityNameMap():
    anchors = geo.value('Arctic.cityNameMap.anchors_1')
    result = [["-1" for x in range(geo.width())] for y in range(geo.height())]
    for x in range(geo.width()):
        for y in range(*geo.value('Arctic.range_13')):
            if not (geo.value('Arctic.bound_7') <= x <= geo.value('Arctic.bound_1') or geo.value('Arctic.bound_8') <= x <= geo.value('Arctic.bound_2')):
                continue
            best, distance = anchors[0], 100000
            for anchor in anchors:
                value = (x-anchor[0])**2 + (y-anchor[1])**2
                if value < distance:
                    best, distance = anchor, value
            result[(geo.height() - 1) - y][x] = best[2]
    return tuple(tuple(row) for row in result)


def setup():
    gc = CyGlobalContext()
    player = gc.getPlayer(con.iEskimos)
    if player.getCivilizationType() != gc.getInfoTypeForString("CIVILIZATION_ESKIMO"):
        return
    StartingCivics.apply(con.iEskimos)
    # This fantasy civilization uses the ordinary victory conditions.
    data = pickle.loads(gc.getGame().getScriptData())
    data['lBirthTurnModifier'][con.iEskimos] = 0
    data['lGoals'][con.iEskimos] = [0, 0, 0]
    gc.getGame().setScriptData(pickle.dumps(data))


def spawn(turn):
    gc = CyGlobalContext()
    player = gc.getPlayer(con.iEskimos)
    if (gc.getGame().getStartTurn() != 0 or turn != con.tBirth[con.iEskimos] or
        player.isAlive() or player.getCivilizationType() != gc.getInfoTypeForString("CIVILIZATION_ESKIMO")):
        return
    # Find an empty, legal cold founding site near the authored homeland.
    candidates = []
    cold = (gc.getInfoTypeForString("TERRAIN_SNOW"), gc.getInfoTypeForString("TERRAIN_TUNDRA"))
    capital = con.tCapitals[con.iEskimos]
    for x in range(*geo.value('Arctic.range_14')):
        for y in range(*geo.value('Arctic.range_15')):
            plot = gc.getMap().plot(x, y)
            if (plot.getTerrainType() in cold and plot.getNumUnits() == 0 and
                player.canFound(x, y) and plot.getFortGarrisonOwner() in (-1, con.iEskimos)):
                candidates.append(((x-capital[0])**2 + (y-capital[1])**2, x, y))
    if not candidates:
        return
    candidates.sort()
    distance, x, y = candidates[0]
    player.initUnit(gc.getInfoTypeForString("UNIT_SETTLER"), x, y,
                    UnitAITypes.UNITAI_SETTLE, DirectionTypes.DIRECTION_SOUTH)
    for role in (UnitAITypes.UNITAI_WORKER, UnitAITypes.UNITAI_CITY_DEFENSE, UnitAITypes.UNITAI_RESERVE):
        player.initUnit(gc.getInfoTypeForString("UNIT_ARCTIC_HUNTER"), x, y,
                        role, DirectionTypes.DIRECTION_SOUTH)
    StartingCivics.apply(con.iEskimos)


def wildlife(turn):
    gc = CyGlobalContext()
    game = gc.getGame()
    if game.isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
        return
    if (turn - game.getStartTurn()) % 6:
        return
    bear = gc.getInfoTypeForString("UNIT_ICE_BEAR")
    snow = gc.getInfoTypeForString("TERRAIN_SNOW")
    tundra = gc.getInfoTypeForString("TERRAIN_TUNDRA")
    world = gc.getMap()
    # One bear per 18 cold land tiles, capped globally. Fixed iteration and
    # game RNG keep spawning identical on every multiplayer peer.
    candidates, homeland, cold, count, localCount = [], [], 0, 0, 0
    for index in range(world.numPlots()):
        plot = world.plotByIndex(index)
        for i in range(plot.getNumUnits()):
            if plot.getUnit(i).getUnitType() == bear:
                count += 1
                if geo.value('Arctic.bound_9') <= plot.getX() <= geo.value('Arctic.bound_3') and geo.value('Arctic.bound_10') <= plot.getY() <= geo.value('Arctic.bound_4'):
                    localCount += 1
        if plot.isWater() or plot.isImpassable() or plot.getTerrainType() not in (snow, tundra):
            continue
        cold += 1
        if plot.isCity() or plot.getNumUnits():
            continue
        # Visible land is eligible, but keep a one-tile buffer from all borders.
        nearOwned = False
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nearby = plotXY(plot.getX(), plot.getY(), dx, dy)
                if nearby is not None and not nearby.isNone() and nearby.isOwned():
                    nearOwned = True
                    break
            if nearOwned:
                break
        if nearOwned:
            continue
        candidates.append(index)
        if geo.value('Arctic.bound_11') <= plot.getX() <= geo.value('Arctic.bound_5') and geo.value('Arctic.bound_12') <= plot.getY() <= geo.value('Arctic.bound_6'):
            homeland.append(index)
    target = min(48, cold // 18)
    for i in range(min(4, max(0, target-count))):
        if not candidates:
            break
        choices = candidates
        if localCount < 6 and homeland:
            choices = homeland
        index = choices[game.getSorenRandNum(len(choices), "Arctic ice bear")]
        candidates.remove(index)
        if index in homeland:
            homeland.remove(index)
            localCount += 1
        plot = world.plotByIndex(index)
        gc.getPlayer(con.iBarbarian).initUnit(bear, plot.getX(), plot.getY(),
            UnitAITypes.UNITAI_ANIMAL, DirectionTypes.DIRECTION_SOUTH)
