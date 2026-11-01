from Reporting import ENABLED as REPORTING_ENABLED
# Roman administration and campaign safeguards. Civ4 / Python 2.4.
from CvPythonExtensions import CyGlobalContext
import ScenarioGeography as geo
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
    if (capital.isNone() or capital.getX() != geo.value('RomanEmpire.bound_1') or capital.getY() != geo.value('RomanEmpire.bound_2')):
        return -5
    # Preserve Italy before opening another offensive theater.
    for pyCity in PyHelpers.PyPlayer(iPlayer).getCityList():
        city = pyCity.GetCy()
        if (geo.value('RomanEmpire.bound_9') <= city.getX() <= geo.value('RomanEmpire.bound_3') and geo.value('RomanEmpire.bound_10') <= city.getY() <= geo.value('RomanEmpire.bound_4')):
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
    italian = [city for city in cities if geo.value('RomanEmpire.bound_11') <= city.getX() <= geo.value('RomanEmpire.bound_5') and geo.value('RomanEmpire.bound_12') <= city.getY() <= geo.value('RomanEmpire.bound_6')]
    if (len(italian) < 2 or gc.getMap().plot(*geo.value('RomanEmpire.plot_1')).getOwner() != iPlayer):
        return False
    data = pickle.loads(gc.getGame().getScriptData())
    turn = gc.getGame().getGameTurn()
    if (turn - data['iRomanLastProvincialLossTurn'] < 10):
        return True
    candidate = None
    best = -1
    for city in cities:
        if (city.isCapital() or (geo.value('RomanEmpire.bound_13') <= city.getX() <= geo.value('RomanEmpire.bound_7') and geo.value('RomanEmpire.bound_14') <= city.getY() <= geo.value('RomanEmpire.bound_8'))):
            continue
        score = abs(city.getX() - geo.value("World.rome")[0]) + abs(city.getY() - geo.value("World.rome")[1])
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
