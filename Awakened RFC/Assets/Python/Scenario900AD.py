# Simultaneous European settler start. Keep compatible with Python 2.4.
from CvPythonExtensions import CyGlobalContext
import Consts as con
import StartingCivics
import cPickle as pickle

START_TURN = 211
SPAIN_START = (51, 46)  # Asturias / Oviedo region, not the Madrid-area birth tile.
ACTIVE_PLAYERS = (con.iEgypt, con.iChina, con.iCarthage, con.iJapan, con.iVikings, con.iArabia,
                  con.iKhmer, con.iSpain, con.iFrance, con.iEngland,
                  con.iGermany, con.iRussia, con.iCaliphateSlot1, con.iKorea, con.iMaya, con.iMississippians)


def isScenario():
    return CyGlobalContext().getGame().getStartTurn() == START_TURN


def configureRegions():
    # Apply after Caliphate's default region reset, both at start and on load.
    regions = ((con.iEgypt, (66, 34), (70, 36), (63, 33), (74, 42), (69, 35)),
               (con.iCarthage, (56, 36), (61, 40), (56, 34), (63, 41), (58, 38)),
               (con.iArabia, (75, 37), (81, 43), (74, 31), (83, 46), (78, 40)),
               (con.iCaliphateSlot1, (49, 40), (55, 43), (49, 40), (56, 46), (51, 41)))
    for iPlayer, coreTL, coreBR, normalTL, normalBR, capital in regions:
        con.tCoreAreasTL[iPlayer], con.tCoreAreasBR[iPlayer] = coreTL, coreBR
        con.tNormalAreasTL[iPlayer], con.tNormalAreasBR[iPlayer] = normalTL, normalBR
        con.tBroaderAreasTL[iPlayer], con.tBroaderAreasBR[iPlayer] = normalTL, normalBR
        con.tNormalAreasSubtract[iPlayer] = ()
        con.tExceptions[iPlayer] = ()
        city = CyGlobalContext().getPlayer(iPlayer).getCapitalCity()
        if not city.isNone():
            capital = (city.getX(), city.getY())
        con.tCapitals[iPlayer] = capital
        con.tReserveCapitals[iPlayer] = capital
    capital = SPAIN_START
    city = CyGlobalContext().getPlayer(con.iSpain).getCapitalCity()
    if not city.isNone():
        capital = (city.getX(), city.getY())
    con.tCapitals[con.iSpain] = capital
    con.tReserveCapitals[con.iSpain] = capital
    # The separate Andalusi minor slot owns only the four regional city states.
    iPlayer = con.iCaliphateSlot2
    con.tCoreAreasTL[iPlayer], con.tCoreAreasBR[iPlayer] = (49, 40), (55, 45)
    con.tNormalAreasTL[iPlayer], con.tNormalAreasBR[iPlayer] = (49, 40), (56, 46)
    con.tBroaderAreasTL[iPlayer], con.tBroaderAreasBR[iPlayer] = (49, 40), (56, 46)
    con.tNormalAreasSubtract[iPlayer] = ()
    con.tExceptions[iPlayer] = ()
    capital = (49, 41)
    city = CyGlobalContext().getPlayer(iPlayer).getCapitalCity()
    if not city.isNone():
        capital = (city.getX(), city.getY())
    con.tCapitals[iPlayer] = capital
    con.tReserveCapitals[iPlayer] = capital


def setup(riseAndFall):
    gc = CyGlobalContext()
    riseAndFall.setEarlyLeaders()
    riseAndFall.assign600ADTechs()
    # Give the established Islamic states the existing medieval technology
    # package, without replaying the original Arabian expansion army.
    arabianTeam = gc.getTeam(gc.getPlayer(con.iArabia).getTeam())
    for iPlayer in (con.iEgypt, con.iCarthage, con.iCaliphateSlot1, con.iCaliphateSlot2):
        team = gc.getTeam(gc.getPlayer(iPlayer).getTeam())
        for iTech in range(gc.getNumTechInfos()):
            if arabianTeam.isHasTech(iTech):
                team.setHasTech(iTech, True, iPlayer, False, False)
        gc.getPlayer(iPlayer).changeGold(200)
    # WB plot order must not put the Abbasid palace in Mecca or the Tulunid
    # palace in Alexandria. Use the authored capital in each established state.
    palace = gc.getInfoTypeForString("BUILDING_PALACE")
    for iPlayer, capital in ((con.iEgypt, (69, 35)), (con.iCarthage, (58, 38)),
                             (con.iArabia, (78, 40)), (con.iCaliphateSlot1, (51, 41))):
        player = gc.getPlayer(iPlayer)
        city, iterator = player.firstCity(False)
        while city and not city.isNone():
            city.setNumRealBuilding(palace, int((city.getX(), city.getY()) == capital))
            city, iterator = player.nextCity(iterator, False)
    gc.getPlayer(con.iEgypt).setCivDescription(u"TXT_KEY_RFCMP_900_TULUNID_DESC")
    gc.getPlayer(con.iCarthage).setCivDescription(u"TXT_KEY_RFCMP_900_AGHLABID_DESC")
    gc.getPlayer(con.iCaliphateSlot1).setCivDescription(u"TXT_KEY_RFCMP_900_CORDOBA_DESC")
    configureRegions()
    # Reuse the established medieval forces and technology packages. Vikings
    # already receive their settlers here; do not create them a second time.
    riseAndFall.create600ADstartingUnits(False)
    for iPlayer in (con.iKhmer, con.iSpain, con.iFrance, con.iEngland,
                    con.iGermany, con.iRussia):
        riseAndFall.createStartingUnits(iPlayer, con.tCapitals[iPlayer])
        riseAndFall.createStartingWorkers(iPlayer, con.tCapitals[iPlayer])
    for iPlayer in range(gc.getMAX_PLAYERS()):
        StartingCivics.apply(iPlayer)
    for iPlayer, gold in ((con.iChina, 300), (con.iJapan, 250),
                         (con.iVikings, 150), (con.iArabia, 300),
                         (con.iKhmer, 200), (con.iSpain, 200),
                         (con.iFrance, 150), (con.iEngland, 200),
                         (con.iGermany, 150), (con.iRussia, 200),
                         (con.iNetherlands, 300), (con.iMali, 600),
                         (con.iPortugal, 200), (con.iInca, 700),
                         (con.iMongolia, 250), (con.iAztecs, 600),
                         (con.iTurkey, 300), (con.iAmerica, 1500),
                         (con.iIndependent, 100), (con.iIndependent2, 100),
                         (con.iNative, 300), (con.iCeltia, 500)):
        gc.getPlayer(iPlayer).changeGold(gold)

    data = pickle.loads(gc.getGame().getScriptData())
    for iPlayer in range(con.iNumTotalPlayers):
        player = gc.getPlayer(iPlayer)
        if player.isAlive():
            data['lLastTurnAlive'][iPlayer] = START_TURN
            data['lNumCities'][iPlayer] = player.getNumCities()
            if iPlayer < con.iNumMajorPlayers:
                data['lStability'][iPlayer] = 10
    for iPlayer in (con.iEgypt, con.iIndia, con.iBabylonia, con.iGreece,
                    con.iPersia, con.iCarthage, con.iRome, con.iEthiopia, con.iMaya):
        data['lGoals'][iPlayer] = [0, 0, 0]
    gc.getGame().setScriptData(pickle.dumps(data))
