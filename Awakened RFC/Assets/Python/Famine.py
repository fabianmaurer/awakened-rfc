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


def cityIsStarving(cityKey, data, turn):
    episode = data['cityFamineEpisodes'].get(cityKey)
    if episode and episode['lastStarvationTurn'] == turn:
        return True
    city = gc.getMap().plot(cityKey[0], cityKey[1]).getPlotCity()
    if city.isNone() or city.getGameTurnFounded() != cityKey[2]:
        return False
    # Export-only deficits are peaceful emigration, not ongoing famine.
    return city.foodDifference(False) + city.getFoodTradeExports() < 0


def lossTurnsUntilAbandonment(population, turn, previousTurns):
    """Project consecutive losses through the unchanged abandonment rule."""
    turns = list(previousTurns)
    for losses in range(1, population):
        projectedTurn = turn + losses - 1
        turns.append(projectedTurn)
        remaining = population - losses
        window = max(5, remaining + 2)
        required = max(3, (7 * remaining + 9) // 10)
        if sum([1 for lostTurn in turns if projectedTurn - lostTurn < window]) >= required:
            return losses
    # Size-one starvation abandons the city without another ordinary loss.
    return max(1, population - 1)


def famineCollapseBudget(iPlayer, cityKey, beforeLoss, losses, capital, data):
    """Price famine against national size before the crisis, in hundredths."""
    if iPlayer >= con.iNumMajorPlayers:
        return 0
    reference = data['lFamineCrisisReference'][iPlayer]
    if reference is None:
        player = gc.getPlayer(iPlayer)
        # The native callback runs after the current population loss.
        reference = {'population': max(1, player.getTotalPopulation() + losses),
                     'cities': {}}
        city, iterator = player.firstCity(False)
        while city and not city.isNone():
            key = (city.getX(), city.getY(), city.getGameTurnFounded())
            population = city.getPopulation()
            if key == cityKey:
                population += losses
            reference['cities'][key] = population
            city, iterator = player.nextCity(iterator, False)
        data['lFamineCrisisReference'][iPlayer] = reference
    # Cities founded or acquired during a crisis use their first affected size.
    population = reference['cities'].setdefault(cityKey, beforeLoss)
    total = (6000 * population + reference['population'] // 2) // reference['population']
    if capital:
        total += 3000
    return total


def recordCityAbandonment(iPlayer, iCity):
    """Keep famine penalties frozen on the final starvation turn, without a charge."""
    game = gc.getGame()
    data = pickle.loads(game.getScriptData())
    episode = data['cityFamineEpisodes'].setdefault(tuple(iCity),
        {'required': 1, 'lossTurns': 0, 'owner': iPlayer})
    episode['lastStarvationTurn'] = game.getGameTurn()
    game.setScriptData(pickle.dumps(data))


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
    starvationPoints = 0
    if starvation:
        # Clear a ruined predecessor when a new city is founded at the same site.
        for city in recent.keys():
            if city[:2] == cityKey[:2] and city != cityKey:
                del recent[city]
                data['cityFamineEpisodes'].pop(city, None)
        turns = recent.setdefault(cityKey, [])
        if not turns or turns[-1] != turn:
            episodes = data['cityFamineEpisodes']
            episode = episodes.get(cityKey)
            if episode is None:
                beforeLoss = population + losses
                required = lossTurnsUntilAbandonment(beforeLoss, turn, turns)
                episode = {'required': required, 'lossTurns': 0,
                           'lastStarvationTurn': turn, 'owner': iPlayer}
                episodes[cityKey] = episode
            previous = episode['lossTurns']
            episode['lossTurns'] += 1
            episode['lastStarvationTurn'] = turn
            episode['owner'] = iPlayer
            total = famineCollapseBudget(iPlayer, cityKey, population + losses,
                                         losses, capital, data)
            # Spread the population-share budget and capital shock across the
            # expected loss turns; later losses are not capped.
            starvationPoints = (total * episode['lossTurns'] // episode['required'] -
                                total * previous // episode['required'])
            turns.append(turn)
        window = max(5, population + 2)
        required = max(3, (7 * population + 9) // 10)
        abandon = sum([1 for lostTurn in turns if turn - lostTurn < window]) >= required
    data['cityStarvationLossTurns'] = recent
    if iPlayer < con.iNumMajorPlayers:
        # Expiration is handled after paused decay clocks advance in updatePenalty.
        history = data['lPopulationLossHistory'][iPlayer]
        base = 1
        if capital:
            base = 4
        for loss in range(losses):
            points = base
            if starvation:
                hundredths = (starvationPoints * (loss + 1) // losses -
                              starvationPoints * loss // losses)
                points = hundredths / 100.0
            if points:
                history.append((turn, points, cityKey, bool(starvation)))
        data['lPopulationLossHistory'][iPlayer] = history
    game.setScriptData(pickle.dumps(data))
    return int(abandon)


def updatePenalty(iPlayer):
    """Pause famine decay while its city starves; round only the total penalty."""
    game = gc.getGame()
    turn = game.getGameTurn()
    data = pickle.loads(game.getScriptData())
    lastUpdate = data['lPopulationLossLastUpdate'][iPlayer]
    if lastUpdate == turn:
        return 0
    old = data['lPopulationLossPenalty'][iPlayer]
    window = max(1, geo.turns(10))
    elapsed = max(0, turn - lastUpdate)
    starving = {}
    history = []
    for lostTurn, points, city, starvation in data['lPopulationLossHistory'][iPlayer]:
        if starvation:
            if city not in starving:
                starving[city] = cityIsStarving(city, data, turn)
            if starving[city]:
                # Move the effective loss date forward to freeze its age.
                lostTurn = min(turn, lostTurn + elapsed)
        if turn - lostTurn < window:
            history.append((lostTurn, points, city, starvation))
    # Store fractional points, but sum and round decay in integer hundredths.
    weighted = sum([int(round(points * 100)) * (window - (turn - lostTurn))
                    for lostTurn, points, city, starvation in history])
    divisor = window * 100
    value = -((weighted + divisor - 1) // divisor)
    data['lPopulationLossPenalty'][iPlayer] = value
    data['lPopulationLossHistory'][iPlayer] = history
    data['lPopulationLossLastUpdate'][iPlayer] = turn
    if not [entry for entry in history if entry[3]]:
        data['lFamineCrisisReference'][iPlayer] = None
    for city, episode in data['cityFamineEpisodes'].items():
        if episode['owner'] == iPlayer and not cityIsStarving(city, data, turn):
            del data['cityFamineEpisodes'][city]
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
