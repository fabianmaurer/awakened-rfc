# -*- coding: latin-1 -*-
"""Synchronized slavery, uprising and slave-war rules for RFC MP Plus."""

from CvPythonExtensions import *
import Popup

gc = CyGlobalContext()

SLAVE_REVOLT_POPUP = 7624

class Slavery:

	def __init__(self):
		self.pending = (-1, -1)

	def _info(self, name):
		return gc.getInfoTypeForString(name)

	def _slaveSpecialist(self):
		return self._info("SPECIALIST_SLAVE")

	def _slaveryCivic(self):
		return self._info("CIVIC_SLAVERY")

	def _hasSlavery(self, player):
		return player.getCivics(self._info("CIVICOPTION_LABOR")) == self._slaveryCivic()

	def _slaveCount(self, city):
		return city.getFreeSpecialistCount(self._slaveSpecialist())

	def _garrisonStrength(self, city, owner):
		plot = city.plot()
		strength = 0
		for i in range(plot.getNumUnits()):
			unit = plot.getUnit(i)
			if unit.getOwner() == owner and unit.canDefend():
				strength += unit.baseCombatStr()
		return strength

	def _slavePower(self, city, owner):
		# Rebels use the strongest slave weapons the owner has unlocked.  This
		# keeps obsolete garrisons from permanently securing a late-era slave city.
		unitType = self._latestRebelUnit(owner)
		return self._slaveCount(city) * gc.getUnitInfo(unitType).getCombat()

	def revoltChance(self, city, owner):
		# An unguarded slave contributes five percentage points, capped at 40%.
		# Garrison strength reduces this proportionally; matching the prospective
		# rebel force prevents a revolt entirely.
		slavePower = self._slavePower(city, owner)
		if slavePower <= 0: return 0
		unguardedPower = max(0, slavePower - self._garrisonStrength(city, owner))
		return max(0, min(40, self._slaveCount(city) * 5 * unguardedPower / slavePower))

	def checkPlayerTurn(self, iPlayer):
		player = gc.getPlayer(iPlayer)
		if not player.isAlive() or not self._hasSlavery(player):
			return
		for city in player.cities():
			chance = self.revoltChance(city, iPlayer)
			if chance > 0 and gc.getGame().getSorenRandNum(100, "Slave revolt") < chance:
				self._startRevolt(iPlayer, city)
				return # one decision per player turn

	def _startRevolt(self, iPlayer, city):
		self.pending = (iPlayer, city.getID())
		if gc.getPlayer(iPlayer).isHuman():
			popup = Popup.PyPopup(SLAVE_REVOLT_POPUP, EventContextTypes.EVENTCONTEXT_ALL)
			popup.setHeaderString(CyTranslator().getText("TXT_KEY_RFCMP_SLAVE_REVOLT_TITLE", ()))
			popup.setBodyString(CyTranslator().getText("TXT_KEY_RFCMP_SLAVE_REVOLT_TEXT", (city.getName(), self._slaveCount(city))))
			popup.addButton(CyTranslator().getText("TXT_KEY_RFCMP_SLAVE_REVOLT_FREE", ()))
			popup.addButton(CyTranslator().getText("TXT_KEY_RFCMP_SLAVE_REVOLT_SUPPRESS", ()))
			popup.launch(False)
		else:
			# AI suppresses only where it can plausibly contain the immediate revolt.
			if self._garrisonStrength(city, iPlayer) >= self._slavePower(city, iPlayer):
				self._suppress(iPlayer, city, True)
			else:
				self._free(city)

	def eventApply(self, popupReturn):
		iPlayer, iCity = self.pending
		self.pending = (-1, -1)
		if iPlayer < 0: return
		player = gc.getPlayer(iPlayer)
		if not player.isAlive(): return
		city = player.getCity(iCity)
		if self._slaveCount(city) <= 0: return
		if popupReturn.getButtonClicked() == 0:
			self._free(city)
		else:
			self._suppress(iPlayer, city, True)

	def _free(self, city):
		slaves = self._slaveCount(city)
		loss = max(1, (slaves + 2) / 3)
		city.changePopulation(-min(max(0, city.getPopulation() - 1), loss))
		city.changeHurryAngerTimer(slaves * 3)
		city.emancipateSlaveSpecialists()
		CyInterface().addMessage(city.getOwner(), True, 14,
			CyTranslator().getText("TXT_KEY_RFCMP_SLAVE_REVOLT_FREED", (city.getName(),)), "", 0, "", ColorTypes(8), city.getX(), city.getY(), True, True)

	def _latestRebelUnit(self, iPlayer):
		team = gc.getTeam(gc.getPlayer(iPlayer).getTeam())
		for name, techName in [("UNIT_SLAVE_MUSKETMAN", "TECH_GUNPOWDER"), ("UNIT_SLAVE_MACEMAN", "TECH_MACHINERY"), ("UNIT_SLAVE_SPEARMAN", "TECH_IRON_WORKING"), ("UNIT_ARMED_SLAVE", "TECH_BRONZE_WORKING")]:
			unit = self._info(name)
			if unit >= 0 and team.isHasTech(self._info(techName)): return unit
		return self._info("UNIT_SLAVE")

	def _spawnPlot(self, city):
		for radius in range(1, 4):
			for dx in range(-radius, radius + 1):
				for dy in range(-radius, radius + 1):
					if max(abs(dx), abs(dy)) != radius: continue
					plot = gc.getMap().plot(city.getX() + dx, city.getY() + dy)
					if not plot.isNone() and not plot.isWater() and not plot.isPeak() and not plot.isCity():
						return plot
		return city.plot()

	def _promoteRebel(self, unit):
		choices = [self._info("PROMOTION_COMBAT1"), self._info("PROMOTION_CITY_RAIDER1"), self._info("PROMOTION_COVER"), self._info("PROMOTION_SHOCK")]
		for n in range(1 + gc.getGame().getSorenRandNum(2, "Slave rebel promotion count")):
			available = [p for p in choices if p >= 0 and not unit.isHasPromotion(p)]
			if not available: break
			unit.setHasPromotion(available[gc.getGame().getSorenRandNum(len(available), "Slave rebel promotion")], True)

	def _suppress(self, iPlayer, city, bChain):
		slaves = self._slaveCount(city)
		loss = max(1, (slaves + 3) / 4)
		city.changePopulation(-min(max(0, city.getPopulation() - 1), loss))
		spawned = []
		barb = gc.getPlayer(gc.getBARBARIAN_PLAYER())
		plot = self._spawnPlot(city)
		for i in range(max(1, (slaves + 1) / 2)):
			unit = barb.initUnit(self._latestRebelUnit(iPlayer), plot.getX(), plot.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
			self._promoteRebel(unit)
			spawned.append(unit)
		CyInterface().addMessage(iPlayer, True, 14,
			CyTranslator().getText("TXT_KEY_RFCMP_SLAVE_REVOLT_SUPPRESSED", (city.getName(), len(spawned))), "AS2D_REVOLT", 0, "", ColorTypes(7), city.getX(), city.getY(), True, True)
		if bChain:
			spawned += self._slaveWarChain(iPlayer, city)
		if len(spawned) >= 8:
			general = barb.initUnit(self._info("UNIT_GREAT_GENERAL"), plot.getX(), plot.getY(), UnitAITypes.UNITAI_GENERAL, DirectionTypes.DIRECTION_SOUTH)
			if len(spawned) and general.canLead(plot, spawned[0].getID()):
				general.lead(spawned[0].getID())
		return spawned

	def _slaveWarChain(self, iPlayer, origin):
		player = gc.getPlayer(iPlayer)
		originArea = origin.plot().getArea()
		candidates = []
		for city in player.cities():
			if city.getID() != origin.getID() and city.plot().getArea() == originArea:
				chance = self.revoltChance(city, iPlayer)
				if chance > 0: candidates.append((chance, city))
		candidates.sort(reverse=True, key=lambda x: x[0])
		allSpawned = []
		for chance, city in candidates:
			if gc.getGame().getSorenRandNum(100, "Slave war spread") < min(100, chance * 2 + 25):
				allSpawned += self._suppress(iPlayer, city, False)
			else:
				break
		return allSpawned

slavery = Slavery()
