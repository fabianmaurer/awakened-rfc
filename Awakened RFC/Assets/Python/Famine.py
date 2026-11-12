"""Capital famine stability and local secession. Python 2.4."""
from CvPythonExtensions import *
import cPickle as pickle
import Consts as con
import RFCUtils

gc = CyGlobalContext()
utils = RFCUtils.RFCUtils()
seceding = False


def capitalPenalty(iPlayer):
    """Temporary current-base penalty; recovery also follows capital relocation."""
    game = gc.getGame()
    data = pickle.loads(game.getScriptData())
    if data['lCapitalFamineTurn'][iPlayer] == game.getGameTurn():
        return data['lCapitalFaminePenalty'][iPlayer]
    penalty = data['lCapitalFaminePenalty'][iPlayer]
    city = gc.getPlayer(iPlayer).getCapitalCity()
    target = 0
    if not city.isNone() and city.getFood() == 0 and city.foodDifference(False) < 0:
        turns = city.getFamineTurns()
        target = -min(20, max(0, turns - 2) * 5)
    if target < penalty:
        penalty = target
    else:
        penalty = min(target, penalty + 2)
    data['lCapitalFaminePenalty'][iPlayer] = penalty
    data['lCapitalFamineTurn'][iPlayer] = game.getGameTurn()
    game.setScriptData(pickle.dumps(data))
    return penalty


def checkPlayerTurn(iPlayer):
    global seceding
    if iPlayer < 0 or iPlayer >= con.iNumMajorPlayers:
        return
    player = gc.getPlayer(iPlayer)
    if not player.isAlive():
        return
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
        if city.getFood() > 0 or city.foodDifference(False) >= 0:
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
