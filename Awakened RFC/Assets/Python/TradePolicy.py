# -*- coding: ascii -*-
"""Embargo UI requests change game state only through synchronized net messages.

19001: actor player, target player, explicit embargo state, reserved field.
Compatible with the game's embedded Python 2.4.
"""
from CvPythonExtensions import *

gc = CyGlobalContext()
EMBARGO_MESSAGE = 19001


def validTarget(iActor, iTarget):
    if iActor < 0 or iActor >= gc.getMAX_PLAYERS() or iTarget < 0 or iTarget >= gc.getMAX_PLAYERS():
        return False
    actor = gc.getPlayer(iActor)
    target = gc.getPlayer(iTarget)
    if not actor.isAlive() or not target.isAlive() or target.isBarbarian():
        return False
    if actor.getTeam() == target.getTeam():
        return False
    return gc.getTeam(actor.getTeam()).isHasMet(target.getTeam())


def requestEmbargo(iActor, iTarget):
    if iActor != CyGame().getActivePlayer() or not validTarget(iActor, iTarget):
        return
    team = gc.getTeam(gc.getPlayer(iActor).getTeam())
    eTarget = gc.getPlayer(iTarget).getTeam()
    bNew = not team.isTradeEmbargo(eTarget)
    if bNew and not team.isHasTech(gc.getInfoTypeForString("TECH_CURRENCY")):
        return
    CyMessageControl().sendModNetMessage(EMBARGO_MESSAGE, iActor, iTarget, int(bNew), 0)


def applyEmbargo(iActor, iTarget, iNewState):
    if iNewState not in (0, 1) or not validTarget(iActor, iTarget):
        return
    team = gc.getTeam(gc.getPlayer(iActor).getTeam())
    team.setTradeEmbargo(gc.getPlayer(iTarget).getTeam(), bool(iNewState))
    CyInterface().setDirty(InterfaceDirtyBits.Foreign_Screen_DIRTY_BIT, True)
