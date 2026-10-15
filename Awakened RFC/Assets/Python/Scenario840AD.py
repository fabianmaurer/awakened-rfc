# Awakened RFC early medieval start. Civ4 Python 2.4 compatible.
from CvPythonExtensions import CyGlobalContext
import Consts as con
import StartingCivics
import cPickle as pickle

START_TURN = 205
ACTIVE_PLAYERS = (con.iChina, con.iJapan, con.iVikings, con.iArabia,
                  con.iKhmer, con.iSpain, con.iFrance, con.iEngland, con.iGermany)


def isScenario():
    return CyGlobalContext().getGame().getStartTurn() == START_TURN


def setup(riseAndFall):
    # Cities, units, religions and terrain are authored in the WB scenario.
    # Reuse the established tech packages without replaying old spawn events.
    gc = CyGlobalContext()
    riseAndFall.setEarlyLeaders()
    riseAndFall.assign600ADTechs()
    for iPlayer in (con.iKhmer, con.iSpain, con.iFrance, con.iEngland, con.iGermany):
        riseAndFall.assignTechs(iPlayer)
    for iPlayer in range(gc.getMAX_PLAYERS()):
        player = gc.getPlayer(iPlayer)
        if not player.isAlive():
            continue
        StartingCivics.apply(iPlayer)
        if iPlayer in ACTIVE_PLAYERS:
            # WorldBuilder loads cities in plot order and may automatically
            # give the first city a palace before loading the authored capital.
            palace = gc.getInfoTypeForString("BUILDING_PALACE")
            capital = con.tCapitals[iPlayer]
            city, iterator = player.firstCity(False)
            while city and not city.isNone():
                isCapital = (city.getX(), city.getY()) == capital
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
    # Goals already missed before this start must not remain achievable.
    for iPlayer in (con.iEgypt, con.iIndia, con.iBabylonia, con.iGreece,
                    con.iPersia, con.iCarthage, con.iRome, con.iEthiopia, con.iMaya):
        data['lGoals'][iPlayer] = [0, 0, 0]
    gc.getGame().setScriptData(pickle.dumps(data))
