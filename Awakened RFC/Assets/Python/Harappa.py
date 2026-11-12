"""Harappan identity and early urban/trade historical goals. Python 2.4."""
from CvPythonExtensions import *
import Consts as con

gc = CyGlobalContext()


def isHarappan(iPlayer):
    return gc.getPlayer(iPlayer).getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_HARAPPA')


def goalKeys(iPlayer):
    if isHarappan(iPlayer):
        return ('TXT_KEY_UHV_HAR1', 'TXT_KEY_UHV_HAR2', 'TXT_KEY_UHV_HAR3')
    return con.tGoals[iPlayer]


def checkGoals(victory, iPlayer):
    player = gc.getPlayer(iPlayer)
    year = gc.getGame().getGameTurnYear()
    cities = []
    city, iterator = player.firstCity(False)
    while city and not city.isNone():
        cities.append(city)
        city, iterator = player.nextCity(iterator, False)
    urban = sum([1 for city in cities if city.getPopulation() >= 5 and
        135 <= city.getX() <= 146 and 55 <= city.getY() <= 68]) >= 3
    partners = set()
    for city in cities:
        for index in range(city.getTradeRoutes()):
            other = city.getTradeCity(index)
            if other and not other.isNone() and other.getOwner() != iPlayer:
                if gc.getPlayer(other.getOwner()).getTeam() != player.getTeam():
                    partners.add(other.getOwner())
    for goal, deadline, achieved in ((0, -2000, urban),
            (1, -1500, len(partners) >= 2), (2, -1000, player.getGold() >= 500)):
        if victory.getGoal(iPlayer, goal) != -1:
            continue
        if year <= deadline and achieved:
            victory.setGoal(iPlayer, goal, 1)
        elif year >= deadline:
            victory.setGoal(iPlayer, goal, 0)
