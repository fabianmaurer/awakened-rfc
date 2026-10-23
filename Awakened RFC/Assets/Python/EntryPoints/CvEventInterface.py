from Reporting import ENABLED as REPORTING_ENABLED
# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005
#
# CvEventInterface.py
#
# These functions are App Entry Points from C++
# WARNING: These function names should not be changed
# WARNING: These functions can not be placed into a class
#
# No other modules should import this
#
import CvUtil
import CvRFCEventManager
from CvPythonExtensions import *

normalEventManager = CvRFCEventManager.CvRFCEventManager()

def getEventManager():
	return normalEventManager

def onEvent(argsList):
	'Called when a game event happens - return 1 if the event was consumed'
	return getEventManager().handleEvent(argsList)

def applyEvent(argsList):
	context, playerID, netUserData, popupReturn = argsList
	return getEventManager().applyEvent(argsList)

def beginEvent(context, argsList=-1):
	return getEventManager().beginEvent(context, argsList)


# Native mod callbacks must enter through an engine-visible EntryPoints module.
# Resolve ordinary helper modules with Python imports, not native module lookup.
def canRomanCampaign(argsList):
    iPlayer = argsList[0]
    import RomanEmpire
    return RomanEmpire.canCampaign(iPlayer)


def recordLaborEvaluation(argsList):
    if REPORTING_ENABLED:
        player, current, best, flat_scores = argsList
        import GameObserver
        GameObserver.record_labor_evaluation(player, current, best, flat_scores)


def showCaliphateChoice(argsList):
    iPlayer = argsList[0]
    import Caliphate
    Caliphate.showChoice(iPlayer)


def onCaliphatePartition(argsList):
    if REPORTING_ENABLED: CvUtil.pyPrint('Caliphate: native callback entered')
    import Caliphate
    Caliphate.onPartition()


def recordApostolicMechanic(argsList):
    if REPORTING_ENABLED:
        import GameObserver
        GameObserver.record_apostolic_mechanic(*argsList)


def recordApostolicState(argsList):
    if REPORTING_ENABLED:
        import GameObserver
        GameObserver.record_apostolic_state(*argsList)
