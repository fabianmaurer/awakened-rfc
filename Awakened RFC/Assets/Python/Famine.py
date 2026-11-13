"""Population-loss stability and local famine secession. Python 2.4."""
from CvPythonExtensions import *
import cPickle as pickle
import Consts as con
import RFCUtils
import ScenarioGeography as geo

gc = CyGlobalContext()
utils = RFCUtils.RFCUtils()
seceding = False


def populationLossPenalty(iPlayer):
    return pickle.loads(gc.getGame().getScriptData())['lPopulationLossPenalty'][iPlayer]


def recordPopulationLoss(iPlayer, iCity, losses, capital, starvation, population):
    """Record losses on every peer; return whether persistent starvation ends the city."""
    if iPlayer < 0 or losses <= 0:
        return 0
    game = gc.getGame()
    if not game.getScriptData():
        return 0
    data = pickle.loads(game.getScriptData())
    turn = game.getGameTurn()
    cityKey = tuple(iCity)
    # All cities count actual loss turns, including independent/barbarian cities.
    # A transfer keeps this history; founding a new city creates a different key.
    # Retain dates: a city's lookback can grow if immigration restores population.
    recent = data['cityStarvationLossTurns']
    abandon = False
    if starvation:
        # Clear a ruined predecessor when a new city is founded at the same site.
        for city in recent.keys():
            if city[:2] == cityKey[:2] and city != cityKey:
                del recent[city]
        turns = recent.setdefault(cityKey, [])
        if not turns or turns[-1] != turn:
            turns.append(turn)
        window = max(5, population + 2)
        required = max(3, (7 * population + 9) // 10)
        abandon = sum([1 for lostTurn in turns if turn - lostTurn < window]) >= required
    data['cityStarvationLossTurns'] = recent
    if iPlayer < con.iNumMajorPlayers:
        window = max(1, geo.turns(10))
        history = [entry for entry in data['lPopulationLossHistory'][iPlayer]
                   if turn - entry[0] < window]
        active = sum([1 for lostTurn, points, city, hunger in history
                      if city == cityKey and hunger])
        base = 1
        if capital:
            base = 4
        for loss in range(losses):
            points = base
            if starvation:
                points *= 1 + 2 * active
                active += 1
            history.append((turn, points, cityKey, bool(starvation)))
        data['lPopulationLossHistory'][iPlayer] = history
    game.setScriptData(pickle.dumps(data))
    return int(abandon)


def updatePenalty(iPlayer):
    """Sum independent linear decay curves; round only the combined penalty."""
    game = gc.getGame()
    turn = game.getGameTurn()
    data = pickle.loads(game.getScriptData())
    old = data['lPopulationLossPenalty'][iPlayer]
    window = max(1, geo.turns(10))
    history = [entry for entry in data['lPopulationLossHistory'][iPlayer]
               if turn - entry[0] < window]
    weighted = sum([points * (window - (turn - lostTurn))
                    for lostTurn, points, city, starvation in history])
    value = -((weighted + window - 1) // window)
    data['lPopulationLossPenalty'][iPlayer] = value
    data['lPopulationLossHistory'][iPlayer] = history
    game.setScriptData(pickle.dumps(data))
    return value - old


def checkPlayerTurn(iPlayer):
    global seceding
    if iPlayer < 0 or iPlayer >= con.iNumMajorPlayers:
        return 0
    player = gc.getPlayer(iPlayer)
    if not player.isAlive():
        return 0
    delta = updatePenalty(iPlayer)
    # Snapshot coordinates: a flip replaces the underlying native city object.
    sites = []
    city, iterator = player.firstCity(False)
    while city and not city.isNone():
        sites.append((city.getX(), city.getY()))
        city, iterator = player.nextCity(iterator, False)
    for x, y in sites:
        city = gc.getMap().plot(x, y).getPlotCity()
        if city.isNone() or city.getOwner() != iPlayer or city.isCapital() or city.isOccupation():
            continue
        if city.getPopulation() <= 1 or city.getFamineTurns() < 3:
            continue
        if city.getFood() > 0 or city.foodDifference(False) + city.getFoodTradeExports() >= 0:
            continue
        # Famine anger alone cannot cause secession. Political discontent or a
        # foreign cultural majority must already exist independently of hunger.
        political = city.unhappyLevel(0) - city.getFamineUnhappiness() > city.happyLevel()
        foreign = city.plot().countTotalCulture() > 0 and city.plot().calculateCulturePercent(iPlayer) < 50
        if not political and not foreign:
            continue
        recipients = [(gc.getPlayer(i).getNumCities(), i) for i in
            (con.iIndependent, con.iIndependent2) if not gc.getPlayer(i).isHuman()]
        if not recipients:
            continue
        recipients.sort()
        iNew = recipients[0][1]
        name = city.getName()
        seceding = True
        try:
            utils.cultureManager((x, y), 50, iNew, iPlayer, False, False, False)
            utils.flipUnitsInCityBefore((x, y), iNew, iPlayer)
            utils.flipCity((x, y), 0, 0, iNew, [iPlayer])
            utils.flipUnitsInCityAfter((x, y), iNew)
        finally:
            seceding = False
        CyInterface().addMessage(iPlayer, True, con.iDuration,
            CyTranslator().getText('TXT_KEY_FAMINE_INDEPENDENT', (name,)), '', 0, '',
            ColorTypes(con.iOrange), x, y, True, True)
    return delta
