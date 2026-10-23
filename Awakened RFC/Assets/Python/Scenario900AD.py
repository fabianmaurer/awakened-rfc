# Simultaneous European settler start. Keep compatible with Python 2.4.
from CvPythonExtensions import CyGlobalContext, UnitAITypes, DirectionTypes
import Consts as con
import StartingCivics
import cPickle as pickle

START_TURN = 211
SPAIN_START = (51, 46)  # Asturias / Oviedo region, not the Madrid-area birth tile.
ACTIVE_PLAYERS = (con.iEgypt, con.iChina, con.iJapan, con.iVikings, con.iArabia,
                  con.iKhmer, con.iSpain, con.iFrance, con.iEngland,
                  con.iGermany, con.iRussia, con.iCaliphateSlot1, con.iKorea, con.iMaya, con.iMississippians)

# Inclusive map rectangles: home regions and nearby routes, not world maps.
# Keep the American and Old World knowledge areas separate.
STARTING_MAP_KNOWLEDGE = {
    con.iEgypt: ((47, 32, 81, 46), (69, 24, 81, 37)),
    con.iChina: ((91, 30, 114, 52), (83, 39, 98, 48), (100, 24, 110, 35)),
    con.iJapan: ((105, 34, 119, 51),),
    con.iMaya: ((17, 29, 28, 40),),
    con.iVikings: ((50, 51, 72, 65), (48, 48, 59, 61)),
    con.iArabia: ((65, 28, 90, 48), (79, 23, 93, 35)),
    con.iKhmer: ((94, 18, 111, 35), (85, 25, 101, 35)),
    con.iSpain: ((46, 35, 61, 49), (58, 38, 68, 44)),
    con.iFrance: ((48, 42, 64, 55), (49, 37, 69, 44)),
    con.iEngland: ((48, 50, 58, 61), (49, 45, 63, 55)),
    con.iGermany: ((53, 43, 72, 57), (57, 37, 66, 45)),
    con.iRussia: ((63, 46, 82, 61), (66, 40, 79, 49)),
    con.iCaliphateSlot1: ((46, 32, 67, 50),),
    con.iCaliphateSlot2: ((46, 35, 61, 49),),
    con.iKorea: ((101, 40, 117, 53),),
    con.iMississippians: ((17, 38, 31, 50),),
    con.iCeltia: ((55, 34, 83, 50),),  # Byzantium in this scenario.
}


def _revealRectangle(gameMap, iTeam, bounds):
    west, south, east, north = bounds
    for x in range(max(0, west), min(gameMap.getGridWidth() - 1, east) + 1):
        for y in range(max(0, south), min(gameMap.getGridHeight() - 1, north) + 1):
            # Ordinary explored map data; this does not grant live visibility.
            gameMap.plot(x, y).setRevealed(iTeam, True, False, -1)


def revealStartingMap():
    gc = CyGlobalContext()
    gameMap = gc.getMap()
    for iPlayer in range(con.iNumTotalPlayers):
        player = gc.getPlayer(iPlayer)
        if not player.isAlive() or player.isBarbarian():
            continue
        iTeam = player.getTeam()
        for bounds in STARTING_MAP_KNOWLEDGE.get(iPlayer, ()):
            _revealRectangle(gameMap, iTeam, bounds)
        # Also cover each actual settlement and its immediate hinterland.
        # This gives the dispersed Independent cities local knowledge too.
        city, iterator = player.firstCity(False)
        while city and not city.isNone():
            x, y = city.getX(), city.getY()
            _revealRectangle(gameMap, iTeam, (x - 4, y - 4, x + 4, y + 4))
            city, iterator = player.nextCity(iterator, False)


def isScenario():
    return CyGlobalContext().getGame().getStartTurn() == START_TURN


def configureRegions():
    # Apply after Caliphate's default region reset, both at start and on load.
    regions = ((con.iEgypt, (56, 34), (74, 42), (56, 33), (74, 42), (69, 35)),
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
    for iPlayer in (con.iEgypt, con.iCaliphateSlot1, con.iCaliphateSlot2):
        team = gc.getTeam(gc.getPlayer(iPlayer).getTeam())
        for iTech in range(gc.getNumTechInfos()):
            if arabianTeam.isHasTech(iTech):
                team.setHasTech(iTech, True, iPlayer, False, False)
        gc.getPlayer(iPlayer).changeGold(200)
    gc.getPlayer(con.iEgypt).changeGold(200)  # Combined Egyptian/Ifriqiyan treasury.
    # WB plot order must not put the Abbasid palace in Mecca or the Fatimid
    # palace in Alexandria. Use the authored capital in each established state.
    palace = gc.getInfoTypeForString("BUILDING_PALACE")
    for iPlayer, capital in ((con.iEgypt, (69, 35)),
                             (con.iArabia, (78, 40)), (con.iCaliphateSlot1, (51, 41))):
        player = gc.getPlayer(iPlayer)
        city, iterator = player.firstCity(False)
        while city and not city.isNone():
            city.setNumRealBuilding(palace, int((city.getX(), city.getY()) == capital))
            city, iterator = player.nextCity(iterator, False)
    gc.getPlayer(con.iCaliphateSlot1).setCivDescription(u"TXT_KEY_RFCMP_900_CORDOBA_DESC")
    configureRegions()
    # Reuse the established medieval forces and technology packages. Vikings
    # already receive their settlers here; do not create them a second time.
    riseAndFall.create600ADstartingUnits(False)
    for iPlayer in (con.iKhmer, con.iSpain, con.iFrance, con.iEngland,
                    con.iGermany, con.iRussia):
        riseAndFall.createStartingUnits(iPlayer, con.tCapitals[iPlayer])
        riseAndFall.createStartingWorkers(iPlayer, con.tCapitals[iPlayer])
    # These cityless kingdoms were already Christian in 900; Rus' and the
    # Viking kingdoms converted later. Let the missionary serve the first city.
    for iPlayer in (con.iSpain, con.iFrance, con.iEngland, con.iGermany):
        player = gc.getPlayer(iPlayer)
        if player.getNumCities() == 0:
            x, y = con.tCapitals[iPlayer]
            player.initUnit(con.iChristianMissionary, x, y,
                            UnitAITypes.UNITAI_MISSIONARY, DirectionTypes.DIRECTION_SOUTH)
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
    revealStartingMap()
