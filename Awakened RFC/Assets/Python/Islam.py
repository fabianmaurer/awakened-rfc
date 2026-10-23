from CvPythonExtensions import *
import Popup

POPUP_ID = 7626
shown = None


def beginChoice():
    pass


def showChoice(iPlayer):
    global shown
    gc = CyGlobalContext()
    player = gc.getPlayer(iPlayer)
    decision = player.getIslamFoundingDecision()
    if decision < 0 or not player.isHuman(): return
    if gc.getGame().getActivePlayer() != iPlayer: return
    if shown == (iPlayer, decision): return
    shown = (iPlayer, decision)
    popup = Popup.PyPopup(POPUP_ID, EventContextTypes.EVENTCONTEXT_ALL)
    popup.setUserData((iPlayer, decision))
    popup.setHeaderString(CyTranslator().getText("TXT_KEY_RFCMP_ISLAM_CHOICE_TITLE", ()))
    popup.setBodyString(CyTranslator().getText("TXT_KEY_RFCMP_ISLAM_CHOICE_BODY", ()))
    popup.addButton(CyTranslator().getText("TXT_KEY_RFCMP_ISLAM_JOIN", ()))
    popup.addButton(CyTranslator().getText("TXT_KEY_RFCMP_ISLAM_SUPPRESS", ()))
    popup.launch(False, PopupStates.POPUPSTATE_IMMEDIATE)


def applyChoice(playerID, netUserData, popupReturn):
    if not isinstance(netUserData, (tuple, list)) or len(netUserData) != 2: return
    owner, decision = netUserData
    if playerID != owner or owner < 0 or owner >= CyGlobalContext().getMAX_PLAYERS(): return
    button = popupReturn.getButtonClicked()
    if button not in (0, 1): return
    # EVENTCONTEXT_ALL applies on every peer. The native saved decision ID
    # validates the owner-scoped choice and consumes it before any effects.
    CyGlobalContext().getPlayer(owner).resolveIslamFounding(decision, button == 0)


def onBeginPlayerTurn(argsList):
    showChoice(argsList[1])


def onLoadGame(argsList):
    global shown
    shown = None
    iPlayer = CyGlobalContext().getGame().getActivePlayer()
    if iPlayer >= 0: showChoice(iPlayer)
