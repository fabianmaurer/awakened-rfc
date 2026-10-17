# Civilization-specific civic labels. Compatible with Civ4's Python 2.4.
from CvPythonExtensions import CyGlobalContext


def description(iCivic, iPlayer=-1):
    gc = CyGlobalContext()
    if iPlayer < 0:
        iPlayer = gc.getGame().getActivePlayer()
    iCivilization = -1
    if iPlayer >= 0:
        iCivilization = gc.getPlayer(iPlayer).getCivilizationType()
    return gc.getCivicInfo(iCivic).getCivilizationDescription(iCivilization)


def upkeep(iCivic, iPlayer=-1):
    gc = CyGlobalContext()
    if iPlayer < 0:
        iPlayer = gc.getGame().getActivePlayer()
    iCivilization = -1
    if iPlayer >= 0:
        iCivilization = gc.getPlayer(iPlayer).getCivilizationType()
    return gc.getCivicInfo(iCivic).getCivilizationUpkeep(iCivilization)


def button(iCivic, iPlayer=-1):
    gc = CyGlobalContext()
    if iPlayer < 0:
        iPlayer = gc.getGame().getActivePlayer()
    iCivilization = -1
    if iPlayer >= 0:
        iCivilization = gc.getPlayer(iPlayer).getCivilizationType()
    return gc.getCivicInfo(iCivic).getCivilizationButton(iCivilization)
