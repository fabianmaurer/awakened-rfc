# Country-name previews for the authored scenario selection screen (Python 2.4).
from CvPythonExtensions import CyGlobalContext, CyTranslator
import Consts as con
import StartingCivics
import os


def descriptions(description, filename):
    gc = CyGlobalContext()
    names = {}
    # These scenarios use RFC's fixed major-player slots. Other WB maps may not.
    if os.path.basename(filename or "").lower() not in (
            "start 1 - 3000 bc.civbeyondswordwbsave",
            "start 2 - 800 bc.civbeyondswordwbsave",
            "start 3 - 600 ad.civbeyondswordwbsave",
            "start 3b - 900 ad.civbeyondswordwbsave",
            "start 4 - 1453 ad.civbeyondswordwbsave"):
        return names
    cityCounts = {}
    for plot in description.plotDesc or []:
        if plot.cityDesc is not None:
            owner = plot.cityDesc.owner
            cityCounts[owner] = cityCounts.get(owner, 0) + 1
    for iPlayer in range(con.iNumMajorPlayers):
        player = description.playersDesc[iPlayer]
        if iPlayer == con.iEskimos and player.civType == "CIVILIZATION_ESKIMO":
            names[iPlayer] = CyTranslator().getText("TXT_KEY_ESK_TRIBES", ())
            continue
        if description.gameDesc.gameTurn == 211 and (
                (iPlayer == con.iEgypt and player.civType == "CIVILIZATION_EGYPT") or
                (iPlayer == con.iCarthage and player.civType == "CIVILIZATION_CARTHAGE")):
            dynasty = "AGHLABID"
            if iPlayer == con.iEgypt:
                dynasty = "TULUNID"
            names[iPlayer] = CyTranslator().getText("TXT_KEY_RFCMP_900_" + dynasty + "_DESC", ())
            continue
        if player.civType not in StartingCivics.PROFILES or player.isMinorNationCiv:
            continue
        profile = StartingCivics.getProfile(player.civType, description.gameDesc.gameTurn)
        # A menu preview uses the intended starting institutions. In play,
        # StartingCivics.apply also checks which choices technology permits.
        civics = [gc.getInfoTypeForString("CIVIC_" + name) for name in profile]
        religion = -1
        if player.stateReligion:
            religion = gc.getInfoTypeForString(player.stateReligion)
        # WB files do not store resolved cultural borders. Preview the base
        # name until the live map supplies the actual owned land count.
        names[iPlayer] = gc.getCountryNamePreview(
            iPlayer, civics, religion, cityCounts.get(iPlayer, 0),
            {0: -3000, 87: -800, 181: 600, 211: 900, 271: 1453}[description.gameDesc.gameTurn],
            0)
    return names
