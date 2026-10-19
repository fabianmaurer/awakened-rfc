from CvPythonExtensions import *
import Popup
import Consts as con
import copy

POPUP_ID = 7627
REALMS = ("ABBASID", "FATIMID", "UMAYYAD")
# Realm, west, south, east, north; mirrored by CvCaliphate.cpp.
REGIONS = ((0, 76, 37, 85, 46), (0, 73, 29, 80, 37),
           (1, 61, 24, 72, 40), (1, 71, 38, 75, 45),
           (2, 44, 30, 60, 49))
shown = None
tables = ("tCapitals", "tReserveCapitals", "tCoreAreasTL", "tCoreAreasBR",
          "tNormalAreasTL", "tNormalAreasBR", "tNormalAreasSubtract",
          "tBroaderAreasTL", "tBroaderAreasBR", "tExceptions", "tGoals")
defaults = dict((name, copy.deepcopy(getattr(con, name))) for name in tables)


def realmOf(iPlayer):
    gc = CyGlobalContext()
    civ = gc.getPlayer(iPlayer).getCivilizationType()
    for realm in range(3):
        if civ == gc.getInfoTypeForString("CIVILIZATION_" + REALMS[realm]):
            return realm
    return -1


def realmAt(x, y):
    bestRealm, bestDistance = -1, None
    for realm, west, south, east, north in REGIONS:
        nearestX = max(west, min(x, east))
        nearestY = max(south, min(y, north))
        distance = min(plotDistance(x, y, nearestX, nearestY),
                       plotDistance(x, y, west, nearestY),
                       plotDistance(x, y, east, nearestY))
        if bestDistance is None or distance < bestDistance:
            bestRealm, bestDistance = realm, distance
    return bestRealm


def configureRegions():
    gc = CyGlobalContext()
    bounds = (((73, 24), (104, 50)), ((61, 24), (75, 45)), ((44, 30), (60, 49)))
    cores = (((73, 30), (84, 45)), ((66, 30), (75, 43)), ((47, 33), (59, 47)))
    for iPlayer in (con.iArabia, con.iCaliphateSlot1, con.iCaliphateSlot2):
        for name in tables:
            getattr(con, name)[iPlayer] = copy.deepcopy(defaults[name][iPlayer])
        realm = realmOf(iPlayer)
        if realm < 0: continue
        tl, br = bounds[realm]
        con.tCoreAreasTL[iPlayer], con.tCoreAreasBR[iPlayer] = cores[realm]
        con.tNormalAreasTL[iPlayer], con.tNormalAreasBR[iPlayer] = tl, br
        con.tBroaderAreasTL[iPlayer], con.tBroaderAreasBR[iPlayer] = tl, br
        con.tNormalAreasSubtract[iPlayer] = tuple((x, y) for x in range(tl[0], br[0] + 1)
                                                 for y in range(tl[1], br[1] + 1)
                                                 if realmAt(x, y) != realm)
        con.tExceptions[iPlayer] = ()
        con.tGoals[iPlayer] = ("TXT_KEY_UHV_CAL1", "TXT_KEY_UHV_CAL2", "TXT_KEY_UHV_CAL3")
        capital = gc.getPlayer(iPlayer).getCapitalCity()
        if not capital.isNone():
            con.tCapitals[iPlayer] = (capital.getX(), capital.getY())
            con.tReserveCapitals[iPlayer] = con.tCapitals[iPlayer]


def beginChoice():
    pass


def showChoice(iPlayer):
    global shown
    gc = CyGlobalContext()
    player = gc.getPlayer(iPlayer)
    decision = player.getCaliphatePartitionDecision()
    if decision < 0 or not player.isHuman(): return
    if gc.getGame().getActivePlayer() != iPlayer: return
    mask = player.getCaliphateRealmMask()
    if shown == (iPlayer, decision, mask): return
    shown = (iPlayer, decision, mask)
    realms = tuple(r for r in range(3) if mask & (1 << r))
    popup = Popup.PyPopup(POPUP_ID, EventContextTypes.EVENTCONTEXT_ALL)
    popup.setUserData((iPlayer, decision, realms))
    popup.setHeaderString(CyTranslator().getText("TXT_KEY_CALIPHATE_PARTITION_TITLE", ()))
    popup.setBodyString(CyTranslator().getText("TXT_KEY_CALIPHATE_PARTITION_BODY", ()))
    for realm in realms:
        popup.addButton(CyTranslator().getText("TXT_KEY_CIV_" + REALMS[realm] + "_DESC", ()))
    popup.launch(False, PopupStates.POPUPSTATE_IMMEDIATE)


def applyChoice(playerID, netUserData, popupReturn):
    if not isinstance(netUserData, (tuple, list)) or len(netUserData) != 3: return
    owner, decision, realms = netUserData
    gc = CyGlobalContext()
    if owner != playerID or owner < 0 or owner >= gc.getMAX_PLAYERS(): return
    button = popupReturn.getButtonClicked()
    if button < 0 or button >= len(realms): return
    # All peers resolve the native owner-scoped, saved, single-use decision.
    gc.getPlayer(owner).resolveCaliphatePartition(decision, realms[button])


def onBeginPlayerTurn(argsList):
    showChoice(argsList[1])


def onLoadGame(argsList):
    global shown
    shown = None
    configureRegions()
    iPlayer = CyGlobalContext().getGame().getActivePlayer()
    if iPlayer >= 0: showChoice(iPlayer)


def onPartition():
    import RFCUtils
    import cPickle as pickle
    gc = CyGlobalContext()
    configureRegions()
    utils = RFCUtils.RFCUtils()
    # The canonical transfer is not an economic collapse or a lost war.
    data = pickle.loads(gc.getGame().getScriptData())
    players = [p for p in (con.iArabia, con.iCaliphateSlot1, con.iCaliphateSlot2) if realmOf(p) >= 0]
    for p in players:
        for name in ("lGNPold", "lGNPnew", "lCombatResultTempModifier", "lPartialBaseStability"):
            data[name][p] = 0
        # These caches count foreign land and missing homeland cities, not
        # total holdings. Start neutral until the next six-turn recount.
        data["lOwnedPlotsLastTurn"][p] = 0
        data["lOwnedCitiesLastTurn"][p] = 0
        data["lNumCities"][p] = gc.getPlayer(p).getNumCities()
        data["lGoals"][p] = [-1, -1, -1]
        data["l2OutOf3"][p] = False
    gc.getGame().setScriptData(pickle.dumps(data))
    for p in players:
        utils.setStability(p, 5)
        utils.setBaseStabilityLastTurn(p, 5)

    import GameObserver
    GameObserver.record_mechanic("caliphate_partition", con.iArabia,
                                {"realms": [{"player": p, "civilization": REALMS[realmOf(p)],
                                             "cities": gc.getPlayer(p).getNumCities(),
                                             "population": gc.getPlayer(p).getTotalPopulation(),
                                             "units": gc.getPlayer(p).getNumUnits()} for p in players]})
