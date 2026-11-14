"""One synchronized human takeover per civilization birth (Python 2.4)."""
from CvPythonExtensions import *
import cPickle as pickle
import Popup
import Consts as con

gc = CyGlobalContext()
POPUP = 7614
_birth = None
_shown = set()


def begin(iNew):
    global _birth
    humans = {}
    for iPlayer in range(con.iNumMajorPlayers):
        player = gc.getPlayer(iPlayer)
        if iPlayer != iNew and player.isHuman() and player.isAlive():
            humans[iPlayer] = player.getNumCities()
    _birth = (iNew, humans, {})
    gc.getGame().beginBirthFlip()


def record(iOld, iNew, city):
    if _birth is None or _birth[0] != iNew or iOld not in _birth[1]:
        return
    losses = _birth[2]
    losses[(city.getX(), city.getY())] = iOld


def finish(bSuccess):
    global _birth
    birth = _birth
    _birth = None
    try:
        if not bSuccess or birth is None:
            return
        iNew, humans, transfers = birth
        losses = {}
        for (x, y), iOld in transfers.items():
            city = gc.getMap().plot(x, y).getPlotCity()
            if not city.isNone() and city.getOwner() == iNew:
                losses[iOld] = losses.get(iOld, 0) + 1
        target = gc.getPlayer(iNew)
        if target.isHuman() or not target.isAlive() or not losses:
            return
        candidates = []
        for iPlayer, count in losses.items():
            player = gc.getPlayer(iPlayer)
            if not player.isHuman():
                continue
            entire = count == humans[iPlayer] and player.getNumCities() == 0
            candidates.append((not entire, -count, iPlayer))
        if not candidates:
            return
        candidates.sort()
        partial, negativeCount, iOwner = candidates[0]
        if not partial:
            gc.getGame().transferBirthControl(iOwner, iNew)
            return
        data = pickle.loads(gc.getGame().getScriptData())
        serial = data['iBirthDecisionSerial']
        data['iBirthDecisionSerial'] = serial + 1
        data['birthDecisions'][serial] = (iOwner, iNew, -negativeCount)
        gc.getGame().setScriptData(pickle.dumps(data))
        showPending()
    finally:
        # Last-city elimination is deferred until automatic succession is done.
        gc.getGame().endBirthFlip()


def showPending(argsList=None):
    game = gc.getGame()
    if not game.getScriptData():
        return
    data = pickle.loads(game.getScriptData())
    for serial in sorted(data['birthDecisions']):
        iOwner, iNew, count = data['birthDecisions'][serial]
        if serial in _shown or game.getActivePlayer() != iOwner:
            continue
        if not gc.getPlayer(iOwner).isHuman() or not gc.getPlayer(iOwner).isAlive():
            continue
        popup = Popup.PyPopup(POPUP, EventContextTypes.EVENTCONTEXT_ALL)
        popup.setUserData((iOwner, serial))
        popup.setHeaderString(CyTranslator().getText('TXT_KEY_BIRTH_SUCCESSION_TITLE', ()))
        popup.setBodyString(CyTranslator().getText('TXT_KEY_BIRTH_SUCCESSION_OFFER',
            (count, gc.getPlayer(iNew).getCivilizationDescription(0))))
        popup.addButton(CyTranslator().getText('TXT_KEY_POPUP_YES', ()))
        popup.addButton(CyTranslator().getText('TXT_KEY_POPUP_NO', ()))
        _shown.add(serial)
        popup.launch(False)


def apply(iPlayer, netUserData, popupReturn):
    if not isinstance(netUserData, (tuple, list)) or len(netUserData) != 2:
        return
    iOwner, serial = netUserData
    data = pickle.loads(gc.getGame().getScriptData())
    decision = data['birthDecisions'].get(serial)
    if decision is None or iPlayer != iOwner or decision[0] != iOwner:
        return
    del data['birthDecisions'][serial]
    gc.getGame().setScriptData(pickle.dumps(data))
    if popupReturn.getButtonClicked() == 0:
        gc.getGame().transferBirthControl(iOwner, decision[1])


def loaded(argsList):
    _shown.clear()
    showPending()

