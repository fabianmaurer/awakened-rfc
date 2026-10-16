# Country-name previews for the authored scenario selection screen (Python 2.4).
from CvPythonExtensions import CyGlobalContext
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
            "start 4 - 840 ad.civbeyondswordwbsave",
            "start 5 - 1453 ad.civbeyondswordwbsave"):
        return names
    cityCounts = {}
    for plot in description.plotDesc or []:
        if plot.cityDesc is not None:
            owner = plot.cityDesc.owner
            cityCounts[owner] = cityCounts.get(owner, 0) + 1
    for iPlayer in range(con.iNumMajorPlayers):
        player = description.playersDesc[iPlayer]
        if player.civType not in StartingCivics.PROFILES or player.isMinorNationCiv:
            continue
        profile = StartingCivics.getProfile(player.civType, description.gameDesc.gameTurn)
        # A menu preview uses the intended starting institutions. In play,
        # StartingCivics.apply also checks which choices technology permits.
        civics = [gc.getInfoTypeForString("CIVIC_" + name) for name in profile]
        religion = -1
        if player.stateReligion:
            religion = gc.getInfoTypeForString(player.stateReligion)
        names[iPlayer] = gc.getCountryNamePreview(
            iPlayer, civics, religion, cityCounts.get(iPlayer, 0),
            {0: -3000, 87: -800, 181: 600, 205: 840, 271: 1453}[description.gameDesc.gameTurn])
    return names
