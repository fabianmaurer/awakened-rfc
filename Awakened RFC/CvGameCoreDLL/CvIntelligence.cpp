// Automatic intelligence networks. All choices and random rolls run on every peer.
#include "CvGameCoreDLL.h"
#include "ObserverPerformance.h"
#include "CvPlayerAI.h"
#include "CvTeamAI.h"
#include "CvCity.h"
#include "CvUnit.h"
#include "CvPlot.h"
#include "CvMap.h"
#include "CvGameAI.h"
#include "CvGlobals.h"
#include "CvInfos.h"
#include "CvGameCoreUtils.h"
#include "CvRhyes.h"
#include "CvDLLInterfaceIFaceBase.h"

namespace
{
    // Mode IDs are also the values sent by the existing synchronized spending message.
    enum { INTEL_TECHNOLOGY, INTEL_MILITARY, INTEL_POLITICS, INTEL_MAPS };
    int scaledTurns(int iTurns)
    {
        return std::max(1, iTurns * GC.getGameSpeedInfo(GC.getGameINLINE().getGameSpeedType()).getResearchPercent() / 100);
    }
}

bool CvPlayer::canIntelligenceTarget(PlayerTypes eTarget) const
{
    if (eTarget < 0 || eTarget >= NUM_MAJOR_PLAYERS || getID() >= NUM_MAJOR_PLAYERS ||
        GC.getGameINLINE().isOption(GAMEOPTION_NO_ESPIONAGE)) return false;
    const CvPlayer& kTarget = GET_PLAYER(eTarget);
    return isAlive() && !isMinorCiv() && kTarget.isAlive() && !kTarget.isMinorCiv() &&
        kTarget.getTeam() != getTeam() && GET_TEAM(getTeam()).isHasMet(kTarget.getTeam());
}

int CvPlayer::getIntelligenceTradeRoutes(PlayerTypes eTarget) const
{
    int iCount = 0, iLoop;
    for (CvCity* pCity = firstCity(&iLoop); pCity; pCity = nextCity(&iLoop))
        for (int i = 0; i < pCity->getTradeRoutes(); ++i)
        {
            CvCity* pTrade = pCity->getTradeCity(i);
            if (pTrade && pTrade->getOwnerINLINE() == eTarget) ++iCount;
        }
    return iCount;
}

bool CvPlayer::hasIntelligenceEmbassy(PlayerTypes eTarget) const
{
    if (eTarget < 0 || eTarget >= NUM_MAJOR_PLAYERS) return false;
    int iLoop;
    // Communications.py treats an embassy on either side as maintaining contact.
    for (CvCity* pCity = firstCity(&iLoop); pCity; pCity = nextCity(&iLoop))
        if (pCity->hasBuilding((BuildingTypes)(NUM_BUILDINGS_PLAGUE + eTarget))) return true;
    for (CvCity* pOther = GET_PLAYER(eTarget).firstCity(&iLoop); pOther; pOther = GET_PLAYER(eTarget).nextCity(&iLoop))
        if (pOther->hasBuilding((BuildingTypes)(NUM_BUILDINGS_PLAGUE + getID()))) return true;
    return false;
}

int CvPlayer::getIntelligenceAccess(PlayerTypes eTarget) const
{
    if (!canIntelligenceTarget(eTarget)) return 0;
    const CvCity* pOurs = getCapitalCity();
    const CvCity* pTheirs = GET_PLAYER(eTarget).getCapitalCity();
    if (!pOurs || !pTheirs) return 0;
    int iDistance = plotDistance(pOurs->getX_INLINE(), pOurs->getY_INLINE(), pTheirs->getX_INLINE(), pTheirs->getY_INLINE());
    int iDistancePenalty = std::min(60, 120 * iDistance / std::max(1, GC.getMapINLINE().maxPlotDistance()));
    return range(100 - iDistancePenalty + (hasIntelligenceEmbassy(eTarget) ? 20 : 0) +
        5 * std::min(4, getIntelligenceTradeRoutes(eTarget)), 40, 140);
}

int CvPlayer::getIntelligenceDefense(PlayerTypes eTarget) const
{
    // Team-wide generation also protects teammates. There is always some resistance.
    int iDefense = 10;
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
        if (GET_PLAYER((PlayerTypes)i).isAlive() && GET_PLAYER((PlayerTypes)i).getTeam() == GET_PLAYER(eTarget).getTeam())
            iDefense += GET_PLAYER((PlayerTypes)i).getCommerceRate(COMMERCE_ESPIONAGE);
    int iProtection = 0, iPopulation = 0;
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
    {
        const CvPlayer& kPlayer = GET_PLAYER((PlayerTypes)i);
        if (!kPlayer.isAlive() || kPlayer.getTeam() != GET_PLAYER(eTarget).getTeam()) continue;
        int iLoop;
        for (CvCity* pCity = kPlayer.firstCity(&iLoop); pCity; pCity = kPlayer.nextCity(&iLoop))
        {
            iProtection += pCity->getPopulation() * pCity->getEspionageDefenseModifier();
            iPopulation += pCity->getPopulation();
        }
    }
    return iDefense * (100 + iProtection / std::max(1, iPopulation)) / 100;
}

int CvPlayer::getIntelligenceRate(PlayerTypes eTarget) const
{
    if (!canIntelligenceTarget(eTarget)) return 0;
    int iAttack = getCommerceRate(COMMERCE_ESPIONAGE) * getIntelligenceAccess(eTarget) / 100;
    return iAttack * (iAttack + 20) / std::max(1, iAttack + 20 + getIntelligenceDefense(eTarget));
}

int CvPlayer::getIntelligenceMode(TeamTypes eTarget) const
{
    return (eTarget >= 0 && eTarget < MAX_TEAMS) ? m_aiIntelligenceMode[eTarget] : INTEL_TECHNOLOGY;
}

int CvPlayer::getIntelligenceTechCount(PlayerTypes eTarget) const
{
    if (!canIntelligenceTarget(eTarget)) return 0;
    int iCount = 0;
    for (int i = 0; i < GC.getNumTechInfos(); ++i)
        if (GET_TEAM(GET_PLAYER(eTarget).getTeam()).isHasTech((TechTypes)i) &&
            !GET_TEAM(getTeam()).isHasTech((TechTypes)i) && canResearch((TechTypes)i)) ++iCount;
    return iCount;
}

int CvPlayer::getIntelligenceResearchRate(TechTypes eTech) const
{
    if (eTech == NO_TECH || GET_TEAM(getTeam()).isHasTech(eTech) || !canResearch(eTech)) return 0;
    std::vector<int> aRates;
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
    {
        PlayerTypes eTarget = (PlayerTypes)i;
        if (canIntelligenceTarget(eTarget) && getIntelligenceMode(GET_PLAYER(eTarget).getTeam()) == INTEL_TECHNOLOGY &&
            GET_TEAM(GET_PLAYER(eTarget).getTeam()).isHasTech(eTech))
            aRates.push_back(getIntelligenceRate(eTarget) * (100 + 10 * std::min(10, getIntelligenceTechCount(eTarget))) / 100);
    }
    std::sort(aRates.begin(), aRates.end(), std::greater<int>());
    int iTotal = 0;
    for (int j = 0; j < (int)aRates.size(); ++j) iTotal += aRates[j] / (j + 1);
    return std::min(iTotal, 3 * getCommerceRate(COMMERCE_ESPIONAGE));
}

int CvPlayer::getIntelligenceMilitaryBonus(PlayerTypes eTarget) const
{
    if (!canIntelligenceTarget(eTarget) || getIntelligenceMode(GET_PLAYER(eTarget).getTeam()) != INTEL_MILITARY) return 0;
    int iStrength = m_aiIntelligenceStrength[GET_PLAYER(eTarget).getTeam()];
    return std::min(8, iStrength * 8 / (20 + GET_PLAYER(eTarget).getNumMilitaryUnits() / 2));
}

int CvPlayer::getIntelligenceSuppressionChance(PlayerTypes eTarget) const
{
    if (getIntelligenceMilitaryBonus(eTarget) <= 0) return 0;
    return std::min(25, m_aiIntelligenceStrength[GET_PLAYER(eTarget).getTeam()] * 25 /
        (40 + GET_PLAYER(eTarget).getNumMilitaryUnits()));
}

int CvPlayer::getIntelligencePoliticalTarget() const
{
    int iPressure = 0;
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
    {
        const CvPlayer& kOther = GET_PLAYER((PlayerTypes)i);
        if (kOther.canIntelligenceTarget(getID()) && kOther.getIntelligenceMode(getTeam()) == INTEL_POLITICS)
            iPressure += kOther.m_aiIntelligenceStrength[getTeam()] * 1200 / (20 + getTotalPopulation());
    }
    return std::min(600, iPressure);
}

int CvPlayer::getIntelligenceStabilityPenalty() const
{
    return GC.getGameINLINE().isOption(GAMEOPTION_NO_ESPIONAGE) ? 0 : m_iIntelligencePressure / 100;
}

int CvPlayer::getIntelligenceAnarchyExtra() const
{
    return getIntelligenceStabilityPenalty() / 3; // at most two normal-speed turns
}

int CvPlayer::getIntelligenceRelationPenalty(TeamTypes eTarget) const
{
    return (eTarget >= 0 && eTarget < MAX_TEAMS) ? (m_aiIntelligenceExposure[eTarget] + 99) / 100 : 0;
}

bool CvPlayer::hasIntelligenceCityVisibility(const CvCity* pCity) const
{
    PlayerTypes eTarget = pCity->getOwnerINLINE();
    if (!canIntelligenceTarget(eTarget)) return false;
    TeamTypes eTeam = GET_PLAYER(eTarget).getTeam();
    if (m_aiIntelligenceStrength[eTeam] <= 0) return false;
    if (getIntelligenceMode(eTeam) == INTEL_MILITARY && getIntelligenceMilitaryBonus(eTarget) >= 3)
        return pCity->isRevealed(getTeam(), false);
    return getIntelligenceMode(eTeam) == INTEL_MAPS && m_aiIntelligenceReportCity[eTeam] == pCity->getID() &&
        m_aiIntelligenceReportUntil[eTeam] > GC.getGameINLINE().getGameTurn();
}

int CvPlayer::getIntelligenceData(int iTarget, int iField) const
{
    // Read-only advisor API. Foreign secrets are returned only when actually acquired.
    if (iField == 20) return getIntelligenceStabilityPenalty();
    if (iField == 21) return m_eIntelligenceResearch;
    if (iField == 22) return getIntelligenceResearchRate(m_eIntelligenceResearch);
    if (iField == 23) return m_iIntelligenceLastResearch;
    if (iTarget < 0 || iTarget >= NUM_MAJOR_PLAYERS) return 0;
    PlayerTypes eTarget = (PlayerTypes)iTarget;
    TeamTypes eTeam = GET_PLAYER(eTarget).getTeam();
    switch (iField)
    {
    case 0: return getIntelligenceMode(eTeam);
    case 1: return getEspionageSpendingWeightAgainstTeam(eTeam);
    case 2: return getIntelligenceAccess(eTarget);
    case 3: return getIntelligenceTradeRoutes(eTarget);
    case 4: return hasIntelligenceEmbassy(eTarget) ? 1 : 0;
    case 5: return getIntelligenceRate(eTarget);
    case 6: return getIntelligenceMilitaryBonus(eTarget);
    case 7: return getIntelligenceSuppressionChance(eTarget);
    case 8: return getIntelligenceRelationPenalty(eTeam);
    case 9: return getIntelligenceDefense(eTarget);
    case 10: return std::min(25, getIntelligenceRate(eTarget) * 25 / (30 + GET_PLAYER(eTarget).getNumCities() * 3));
    case 11: return m_aiIntelligenceReportUntil[eTeam] > GC.getGameINLINE().getGameTurn() ? m_aiIntelligenceReportUntil[eTeam] - GC.getGameINLINE().getGameTurn() : 0;
    case 14:
        return m_eIntelligenceResearch != NO_TECH && !GET_TEAM(getTeam()).isHasTech(m_eIntelligenceResearch) &&
            canResearch(m_eIntelligenceResearch) && canIntelligenceTarget(eTarget) && getIntelligenceMode(eTeam) == INTEL_TECHNOLOGY &&
            GET_TEAM(eTeam).isHasTech(m_eIntelligenceResearch) ?
            getIntelligenceRate(eTarget) * (100 + 10 * std::min(10, getIntelligenceTechCount(eTarget))) / 100 : 0;
    case 13:
    {
        int iAttack = getCommerceRate(COMMERCE_ESPIONAGE) * getIntelligenceAccess(eTarget) / 100;
        return iAttack > 0 ? 100 - getIntelligenceRate(eTarget) * 100 / iAttack : 0;
    }
    case 12: return canIntelligenceTarget(eTarget) && getIntelligenceMode(eTeam) == INTEL_POLITICS ?
        std::min(600, m_aiIntelligenceStrength[eTeam] * 1200 / (20 + GET_PLAYER(eTarget).getTotalPopulation())) : 0;
    }
    return 0;
}

void CvPlayer::doIntelligencePressure()
{
    int iTarget = getIntelligencePoliticalTarget();
    int iStep = std::max(1, 2000 / GC.getGameSpeedInfo(GC.getGameINLINE().getGameSpeedType()).getResearchPercent());
    if (iTarget > m_iIntelligencePressure) m_iIntelligencePressure = std::min(iTarget, m_iIntelligencePressure + iStep);
    else m_iIntelligencePressure = std::max(iTarget, m_iIntelligencePressure - iStep);
    if (m_iIntelligenceUnrestCooldown > 0) --m_iIntelligenceUnrestCooldown;
    if (getIntelligenceStabilityPenalty() > 0 && m_iIntelligenceUnrestCooldown == 0 &&
        GC.getGameINLINE().getSorenRandNum(100, "Intelligence unrest") < getIntelligenceStabilityPenalty())
    {
        int iLoop;
        CvCity* pCity;
        // City IDs are sparse; use an ordinal rather than relying on their IDs.
        int iOrdinal = GC.getGameINLINE().getSorenRandNum(std::max(1, getNumCities()), "Intelligence unrest selection");
        for (pCity = firstCity(&iLoop); pCity && iOrdinal > 0; pCity = nextCity(&iLoop)) --iOrdinal;
        if (pCity)
        {
            pCity->changeEspionageHappinessCounter(scaledTurns(2));
            gDLL->getInterfaceIFace()->addMessage(getID(), false, GC.getEVENT_MESSAGE_TIME(),
                gDLL->getText("TXT_KEY_INTEL_UNREST", pCity->getNameKey()), NULL, MESSAGE_TYPE_MINOR_EVENT,
                NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_WARNING_TEXT"), pCity->getX_INLINE(), pCity->getY_INLINE(), true, true);
        }
        m_iIntelligenceUnrestCooldown = scaledTurns(8);
    }
}

void CvPlayer::doEspionagePoints()
{
    OBSERVER_PERFORMANCE("CvPlayer::doEspionagePoints");
    m_iIntelligenceLastResearch = 0;
    if (getID() >= NUM_MAJOR_PLAYERS || isMinorCiv()) return;
    // Commit queued choices only at a turn boundary. Strength is fixed for combat.
    for (int t = 0; t < MAX_TEAMS; ++t)
    {
        m_aiIntelligenceMode[t] = m_aiEspionageSpendingWeightAgainstTeam[t];
        m_aiIntelligenceStrength[t] = 0;
        if (m_aiIntelligenceExposure[t] > 0) m_aiIntelligenceExposure[t] = std::max(0, m_aiIntelligenceExposure[t] - 2);
    }
    if (GC.getGameINLINE().isOption(GAMEOPTION_NO_ESPIONAGE)) return;
    int iTurn = GC.getGameINLINE().getGameTurn();
    GET_TEAM(getTeam()).changeEspionagePointsEver(getCommerceRate(COMMERCE_ESPIONAGE));
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
    {
        PlayerTypes eTarget = (PlayerTypes)i;
        if (!canIntelligenceTarget(eTarget))
        {
            int iCityLoop;
            for (CvCity* pCity = GET_PLAYER(eTarget).firstCity(&iCityLoop); pCity; pCity = GET_PLAYER(eTarget).nextCity(&iCityLoop))
                pCity->updateEspionageVisibility(true);
            continue;
        }
        CvPlayer& kTarget = GET_PLAYER(eTarget);
        TeamTypes eTeam = kTarget.getTeam();
        int iStrength = getIntelligenceRate(eTarget);
        m_aiIntelligenceStrength[eTeam] = iStrength;
        if (iStrength > 0)
        {
            int iMode = getIntelligenceMode(eTeam);
            int iSeverity = iMode == INTEL_POLITICS ? 3 : (iMode == INTEL_MILITARY ? 2 : 1);
            int iRisk = iMode == INTEL_POLITICS ? 6 : (iMode == INTEL_MILITARY ? 3 : 1);
            if (GC.getGameINLINE().getSorenRandNum(100, "Intelligence discovery") < iRisk)
            {
                m_aiIntelligenceExposure[eTeam] = std::max(m_aiIntelligenceExposure[eTeam],
                    std::min(iMode == INTEL_POLITICS ? 600 : (iMode == INTEL_MILITARY ? 300 : 100), m_aiIntelligenceExposure[eTeam] + 100 * iSeverity));
                gDLL->getInterfaceIFace()->addMessage(getID(), false, GC.getEVENT_MESSAGE_TIME(),
                    gDLL->getText("TXT_KEY_INTEL_DISCOVERED", kTarget.getCivilizationShortDescriptionKey()), NULL, MESSAGE_TYPE_MINOR_EVENT);
                gDLL->getInterfaceIFace()->addMessage(eTarget, false, GC.getEVENT_MESSAGE_TIME(),
                    gDLL->getText("TXT_KEY_INTEL_DETECTED", getCivilizationShortDescriptionKey()), NULL, MESSAGE_TYPE_MINOR_EVENT);
            }
            if (iMode == INTEL_MILITARY && GET_TEAM(getTeam()).isAtWar(eTeam))
            {
                int iCityLoop;
                for (CvCity* pCity = kTarget.firstCity(&iCityLoop); pCity; pCity = kTarget.nextCity(&iCityLoop))
                {
                    bool bAdjacent = false;
                    for (int d = 0; d < NUM_DIRECTION_TYPES && !bAdjacent; ++d)
                    {
                        CvPlot* pAdjacent = plotDirection(pCity->getX_INLINE(), pCity->getY_INLINE(), (DirectionTypes)d);
                        if (!pAdjacent) continue;
                        CLLNode<IDInfo>* pNode = pAdjacent->headUnitNode();
                        for (; pNode; pNode = pAdjacent->nextUnitNode(pNode))
                        {
                            CvUnit* pUnit = ::getUnit(pNode->m_data);
                            if (pUnit && pUnit->getOwnerINLINE() == getID() && pUnit->canAttack() && pUnit->getDomainType() == DOMAIN_LAND)
                            { bAdjacent = true; break; }
                        }
                    }
                    if (bAdjacent) pCity->rollIntelligenceSuppression(getID(), getIntelligenceSuppressionChance(eTarget));
                }
            }
            if (iMode == INTEL_MAPS && GC.getGameINLINE().getSorenRandNum(100, "Intelligence map report") < getIntelligenceData(i, 10))
            {
                CvCity* pBest = NULL;
                int iBest = -1, iCityLoop;
                for (CvCity* pCity = kTarget.firstCity(&iCityLoop); pCity; pCity = kTarget.nextCity(&iCityLoop))
                {
                    int iUnknown = 0;
                    for (int dx = -3; dx <= 3; ++dx) for (int dy = -3; dy <= 3; ++dy)
                    {
                        CvPlot* pPlot = plotXY(pCity->getX_INLINE(), pCity->getY_INLINE(), dx, dy);
                        if (pPlot && !pPlot->isRevealed(getTeam(), false)) ++iUnknown;
                    }
                    int iScore = iUnknown * 100 + GC.getGameINLINE().getSorenRandNum(100, "Intelligence report city");
                    if (iScore > iBest) { pBest = pCity; iBest = iScore; }
                }
                if (pBest)
                {
                    for (int dx = -3; dx <= 3; ++dx) for (int dy = -3; dy <= 3; ++dy)
                    {
                        CvPlot* pPlot = plotXY(pBest->getX_INLINE(), pBest->getY_INLINE(), dx, dy);
                        if (pPlot) pPlot->setRevealed(getTeam(), true, false, NO_TEAM, true);
                    }
                    m_aiIntelligenceReportCity[eTeam] = pBest->getID();
                    m_aiIntelligenceReportUntil[eTeam] = iTurn + scaledTurns(3);
                    gDLL->getInterfaceIFace()->addMessage(getID(), false, GC.getEVENT_MESSAGE_TIME(),
                        gDLL->getText("TXT_KEY_INTEL_REPORT", pBest->getNameKey()), NULL, MESSAGE_TYPE_MINOR_EVENT,
                        NULL, NO_COLOR, pBest->getX_INLINE(), pBest->getY_INLINE(), true, true);
                }
            }
        }
        int iCityLoop;
        for (CvCity* pCity = kTarget.firstCity(&iCityLoop); pCity; pCity = kTarget.nextCity(&iCityLoop)) pCity->updateEspionageVisibility(true);
    }
    // One shared project prevents several stolen technologies completing at once.
    if (m_eIntelligenceResearch != NO_TECH &&
        (GET_TEAM(getTeam()).isHasTech(m_eIntelligenceResearch) || !canResearch(m_eIntelligenceResearch)))
        m_eIntelligenceResearch = NO_TECH;
    if (m_eIntelligenceResearch != NO_TECH)
    {
        bool bAvailable = false;
        for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
            if (canIntelligenceTarget((PlayerTypes)i) && GET_TEAM(GET_PLAYER((PlayerTypes)i).getTeam()).isHasTech(m_eIntelligenceResearch))
                bAvailable = true;
        if (!bAvailable) m_eIntelligenceResearch = NO_TECH;
    }
    if (m_eIntelligenceResearch == NO_TECH)
    {
        std::vector<TechTypes> aTechs;
        for (int k = 0; k < GC.getNumTechInfos(); ++k)
            if (getIntelligenceResearchRate((TechTypes)k) > 0) aTechs.push_back((TechTypes)k);
        if (!aTechs.empty()) m_eIntelligenceResearch = aTechs[GC.getGameINLINE().getSorenRandNum((int)aTechs.size(), "Intelligence research project")];
    }
    if (m_eIntelligenceResearch != NO_TECH)
    {
        int iLeft = GET_TEAM(getTeam()).getResearchCost(m_eIntelligenceResearch) - GET_TEAM(getTeam()).getResearchProgress(m_eIntelligenceResearch);
        m_iIntelligenceLastResearch = std::min(iLeft, getIntelligenceResearchRate(m_eIntelligenceResearch));
        if (m_iIntelligenceLastResearch > 0)
            GET_TEAM(getTeam()).changeResearchProgress(m_eIntelligenceResearch, m_iIntelligenceLastResearch, getID());
    }
    gDLL->getInterfaceIFace()->setDirty(Espionage_Advisor_DIRTY_BIT, true);
}

int CvPlayer::getIntelligenceChecksum() const
{
    int iValue = (m_eIntelligenceResearch + 1) * 101 + m_iIntelligencePressure * 103 +
        m_iIntelligenceUnrestCooldown * 107 + m_iIntelligenceLastResearch * 109;
    for (int i = 0; i < MAX_TEAMS; ++i)
        iValue += (i + 1) * (m_aiIntelligenceMode[i] * 113 + m_aiEspionageSpendingWeightAgainstTeam[i] * 127 +
            m_aiIntelligenceStrength[i] * 131 + m_aiIntelligenceExposure[i] * 137 +
            (m_aiIntelligenceReportCity[i] + 1) * 139 + (m_aiIntelligenceReportUntil[i] + 1) * 149);
    return iValue;
}
