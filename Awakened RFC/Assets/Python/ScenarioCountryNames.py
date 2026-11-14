# Country-name previews for the authored scenario selection screen (Python 2.4).
from CvPythonExtensions import CyGlobalContext, CyTranslator
import Consts as con
import StartingCivics
import IndianCivsData
import ScenarioGeography
import os


def descriptions(description, filename):
    gc = CyGlobalContext()
    names = {}
    # These scenarios use RFC's fixed major-player slots. Other WB maps may not.
    if os.path.basename((filename or "").replace("\\", "/")).lower() not in ScenarioGeography.SCENARIOS:
        return names
    # Menu previews run before the selected geography is activated.
    startTurn = description.gameDesc.gameTurn
    if ScenarioGeography.scenarioSpeed(filename) == "GAMESPEED_XL":
        startTurn = startTurn // 2
    cityCounts = {}
    capitals = {}
    for plot in description.plotDesc or []:
        if plot.cityDesc is not None:
            owner = plot.cityDesc.owner
            cityCounts[owner] = cityCounts.get(owner, 0) + 1
            if 'BUILDING_PALACE' in plot.cityDesc.bldgType:
                capitals[owner] = (plot.iX * 200 // description.mapDesc.iGridW,
                                   plot.iY * 110 // description.mapDesc.iGridH)
    for iPlayer in range(con.iNumMajorPlayers):
        player = description.playersDesc[iPlayer]
        if player.civType == "CIVILIZATION_ADENA":
            names[iPlayer] = CyTranslator().getText("TXT_KEY_ADENA_DESC", ())
            continue
        if iPlayer == con.iEskimos and player.civType == "CIVILIZATION_ESKIMO":
            names[iPlayer] = CyTranslator().getText("TXT_KEY_ESK_TRIBES", ())
            continue
        if startTurn == 211 and (
                (iPlayer == con.iEgypt and player.civType == "CIVILIZATION_EGYPT") or
                (iPlayer == con.iCarthage and player.civType == "CIVILIZATION_CARTHAGE")):
            dynasty = "AGHLABID"
            if iPlayer == con.iEgypt:
                dynasty = "TULUNID"
            names[iPlayer] = CyTranslator().getText("TXT_KEY_RFCMP_900_" + dynasty + "_DESC", ())
            continue
        if player.civType not in StartingCivics.PROFILES or player.isMinorNationCiv:
            continue
        profile = StartingCivics.getProfile(player.civType, startTurn)
        # A menu preview uses the intended starting institutions. In play,
        # StartingCivics.apply also checks which choices technology permits.
        civics = [gc.getInfoTypeForString("CIVIC_" + name) for name in profile]
        religion = -1
        if player.stateReligion:
            religion = gc.getInfoTypeForString(player.stateReligion)
        year = {0: -3000, 87: -800, 181: 600, 211: 900, 271: 1453}[startTurn]
        capital = capitals.get(iPlayer, (-1, -1))
        # Future births preview their authored starting year, capital and faith,
        # rather than treating an unspawned kingdom as a country in 3000 BC.
        for civ, short, birth, birthYear, site, coreTL, coreBR, normalTL, normalBR in IndianCivsData.CIVS:
            if player.civType == 'CIVILIZATION_' + civ and year < birthYear:
                year = birthYear
                capital = site
                religionName = 'RELIGION_HINDUISM'
                if civ in ('DELHI', 'BENGAL'):
                    religionName = 'RELIGION_ISLAM'
                religion = gc.getInfoTypeForString(religionName)
                break
        # WB files do not store resolved cultural borders. Preview the base
        # name until the live map supplies the actual owned land count.
        names[iPlayer] = gc.getCountryNamePreview(
            iPlayer, civics, religion, cityCounts.get(iPlayer, 0),
            year,
            0, gc.getInfoTypeForString(player.civType),
            capital[0], capital[1])
    return names
