from Reporting import ENABLED as REPORTING_ENABLED
# Roman administration and campaign safeguards. Civ4 / Python 2.4.
from CvPythonExtensions import CyGlobalContext
import cPickle as pickle
import Consts as con
import PyHelpers
import RFCUtils

gc = CyGlobalContext()
utils = RFCUtils.RFCUtils()


def canCampaign(iPlayer):
    """1 permits preparation; negative codes identify the actual blocking gate."""
    player = gc.getPlayer(iPlayer)
    if (iPlayer != con.iRome or player.isHuman() or not player.isAlive()):
        return -2
    if (utils.getStability(iPlayer) < -10):
        return -3
    if (utils.getPlagueCountdown(iPlayer) > 0):
        return -4
    capital = player.getCapitalCity()
    if (capital.isNone() or capital.getX() != 60 or capital.getY() != 44):
        return -5
    # Preserve Italy before opening another offensive theater.
    for pyCity in PyHelpers.PyPlayer(iPlayer).getCityList():
        city = pyCity.GetCy()
        if (57 <= city.getX() <= 64 and 40 <= city.getY() <= 47):
            if (city.isOccupation() or city.getPopulation() < 1):
                return -6
    return 1


def handleProvincialLoss(iPlayer, reason):
    """Return true when a viable republic handles losses provincially.

    Severe instability and loss of the Italian base retain full collapse.
    At most one peripheral city secedes per ten turns; no troops are granted.
    """
    if (iPlayer != con.iRome):
        return False
    player = gc.getPlayer(iPlayer)
    if (not player.isCivic(gc.getInfoTypeForString("CIVIC_REPUBLIC")) or
        utils.getStability(iPlayer) < -40):
        return False
    cities = [pyCity.GetCy() for pyCity in PyHelpers.PyPlayer(iPlayer).getCityList()]
    italian = [city for city in cities if 57 <= city.getX() <= 64 and 40 <= city.getY() <= 47]
    if (len(italian) < 2 or gc.getMap().plot(60, 44).getOwner() != iPlayer):
        return False
    data = pickle.loads(gc.getGame().getScriptData())
    turn = gc.getGame().getGameTurn()
    if (turn - data['iRomanLastProvincialLossTurn'] < 10):
        return True
    candidate = None
    best = -1
    for city in cities:
        if (city.isCapital() or (57 <= city.getX() <= 64 and 40 <= city.getY() <= 47)):
            continue
        score = abs(city.getX() - 60) + abs(city.getY() - 44)
        if (not city.isConnectedToCapital(iPlayer)):
            score += 100
        if (score > best):
            best = score
            candidate = city
    if (candidate is not None):
        coords = (candidate.getX(), candidate.getY())
        if REPORTING_ENABLED:
            before = player.getNumCities()
            stability = utils.getStability(iPlayer)
        utils.cultureManager(coords, 50, con.iIndependent, iPlayer, False, False, False)
        utils.flipUnitsInCityBefore(coords, con.iIndependent, iPlayer)
        utils.flipCity(coords, 0, 0, con.iIndependent, [iPlayer])
        utils.flipUnitsInCityAfter(coords, con.iIndependent)
        # Flipping invokes event handlers: reload rather than overwrite their data.
        data = pickle.loads(gc.getGame().getScriptData())
        data['iRomanLastProvincialLossTurn'] = turn
        gc.getGame().setScriptData(pickle.dumps(data))
        if REPORTING_ENABLED:
            import GameObserver
        if REPORTING_ENABLED:
            GameObserver.record_mechanic('collapse_trigger', iPlayer,
                {'reason': reason, 'outcome': 'fragmentation', 'partial': True,
                 'stability_before': stability, 'cities_before': before,
                 'cities_after': player.getNumCities(), 'province': list(coords)})
    return True
