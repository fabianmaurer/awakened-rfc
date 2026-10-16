# Post-Constantinople world start. Compatible with Civ4's Python 2.4.
from CvPythonExtensions import CyGlobalContext
import Consts as con
import StartingCivics
from Scenario1453Data import START_TURN, START_YEAR, ACTIVE_PLAYERS, CAPITALS
import cPickle as pickle


def isScenario():
    return CyGlobalContext().getGame().getStartTurn() == START_TURN


def setup(riseAndFall):
    # Technologies, cities, forces, religions and diplomacy are authored in WB.
    # Never replay the ancient or medieval civilization spawns here.
    gc = CyGlobalContext()
    palace = gc.getInfoTypeForString("BUILDING_PALACE")
    for iPlayer in ACTIVE_PLAYERS:
        player = gc.getPlayer(iPlayer)
        StartingCivics.apply(iPlayer)
        city, iterator = player.firstCity(False)
        while city and not city.isNone():
            isCapital = (city.getX(), city.getY()) == CAPITALS[iPlayer]
            city.setNumRealBuilding(palace, int(isCapital))
            city, iterator = player.nextCity(iterator, False)

    data = pickle.loads(gc.getGame().getScriptData())
    for iPlayer in range(con.iNumTotalPlayers):
        player = gc.getPlayer(iPlayer)
        if player.isAlive():
            data['lLastTurnAlive'][iPlayer] = START_TURN
            data['lNumCities'][iPlayer] = player.getNumCities()
            if iPlayer < con.iNumMajorPlayers:
                data['lStability'][iPlayer] = 10
    # These ancient victories already missed indispensable early objectives.
    for iPlayer in (con.iEgypt, con.iIndia, con.iBabylonia, con.iGreece,
                    con.iPersia, con.iCarthage, con.iRome, con.iEthiopia, con.iMaya):
        data['lGoals'][iPlayer] = [0, 0, 0]
    gc.getGame().setScriptData(pickle.dumps(data))
