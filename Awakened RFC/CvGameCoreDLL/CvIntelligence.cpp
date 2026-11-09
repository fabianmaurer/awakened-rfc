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
    int intelligenceSpeedPercent()
    {
        GameSpeedTypes eNormal = (GameSpeedTypes)GC.getInfoTypeForString("GAMESPEED_NORMAL");
        int iNormal = GC.getGameSpeedInfo(eNormal).getResearchPercent();
        return std::max(1, GC.getGameSpeedInfo(GC.getGameINLINE().getGameSpeedType()).getResearchPercent() * 100 / std::max(1, iNormal));
    }

    int scaledTurns(int iTurns)
    {
        return iTurns <= 0 ? 0 : std::max(1, iTurns * intelligenceSpeedPercent() / 100);
    }

    int scaledChance(int iPercent)
    {
        // Basis points retain half-percent chances on the XL calendar.
        return range(iPercent * 10000 / intelligenceSpeedPercent(), 0, 10000);
    }

    int scaledAnarchyTurns(int iTurns)
    {
        if (iTurns <= 0) return 0;
        GameSpeedTypes eNormal = (GameSpeedTypes)GC.getInfoTypeForString("GAMESPEED_NORMAL");
        return std::max(1, iTurns * GC.getGameSpeedInfo(GC.getGameINLINE().getGameSpeedType()).getAnarchyPercent() /
            std::max(1, GC.getGameSpeedInfo(eNormal).getAnarchyPercent()));
    }

    int mapReportRadius()
    {
        // Scale the reference world's radius 3 with the supported geography widths.
        return std::max(1, (3 * GC.getMapINLINE().getGridWidth() + 62) / 124);
    }

    int decayIntelligenceStock(int iStock)
    {
        const int iDecay = std::min(10000, std::max(1, 50000 / intelligenceSpeedPercent()));
        return iStock - (int)(((__int64)iStock * iDecay + 9999) / 10000);
    }

    int growIntelligenceStock(int iStock, int iRate)
    {
        return (int)std::min((__int64)MAX_INT / 2,
            iStock + (__int64)iRate * 10000 / intelligenceSpeedPercent());
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
    const __int64 iAttack = (__int64)getCommerceRate(COMMERCE_ESPIONAGE) * getIntelligenceAccess(eTarget) / 100;
    return (int)std::min((__int64)MAX_INT, iAttack * (iAttack + 20) /
        std::max((__int64)1, iAttack + 20 + getIntelligenceDefense(eTarget)));
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
    // Basis points preserve marginal gains near the limit in combat as well as in the advisor.
    return 30 * getIntelligenceMilitaryCoverage(eTarget) / 100;
}

int CvPlayer::getIntelligenceMilitaryCoverage(PlayerTypes eTarget) const
{
    if (!canIntelligenceTarget(eTarget) || getIntelligenceMode(GET_PLAYER(eTarget).getTeam()) != INTEL_MILITARY) return 0;
    const int iStock = m_aiIntelligenceMilitaryStock[GET_PLAYER(eTarget).getTeam()];
    // One shared saturation curve: half effect at 20 * (40 + enemy military units).
    // Use 64-bit arithmetic and basis points so very large networks still have diminishing returns.
    const __int64 iHalf = (__int64)2000 * (40 + GET_PLAYER(eTarget).getNumMilitaryUnits());
    return (int)((__int64)10000 * iStock / (iStock + iHalf));
}

int CvPlayer::getIntelligenceSuppressionChance(PlayerTypes eTarget) const
{
    // Basis points, independent of whole-percent combat rounding.
    return 30 * getIntelligenceMilitaryCoverage(eTarget) / 100;
}

void CvPlayer::refreshIntelligenceTracking()
{
    if (getTeam() == NO_TEAM) return;
    for (int i = 0; i < MAX_PLAYERS; ++i)
    {
        int iLoop;
        CvPlayer& kOwner = GET_PLAYER((PlayerTypes)i);
        for (CvUnit* pUnit = kOwner.firstUnit(&iLoop); pUnit; pUnit = kOwner.nextUnit(&iLoop))
            pUnit->updateIntelligenceTracking(getTeam());
    }
}

void CvUnit::updateIntelligenceTracking(TeamTypes eObserver)
{
    if (eObserver < 0 || eObserver >= MAX_CIV_TEAMS) return;
    int iCoverage = 0;
    if (canFight() || canAirAttack())
        for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
        {
            const CvPlayer& kObserver = GET_PLAYER((PlayerTypes)i);
            if (kObserver.isAlive() && kObserver.getTeam() == eObserver)
                iCoverage = std::max(iCoverage, kObserver.getIntelligenceMilitaryCoverage(getOwnerINLINE()));
        }
    // A stable per-unit selection follows the same troops as they move. No UI-local or movement RNG.
    // Unsigned mixing is portable to the legacy compiler; only the synchronized identity is used.
    unsigned int iHash = (unsigned int)getID() ^ ((unsigned int)(getOwnerINLINE() + 1) * 0x9e3779b9U) ^
        ((unsigned int)(eObserver + 1) * 0x85ebca6bU);
    iHash ^= iHash >> 16;
    iHash *= 0x7feb352dU;
    iHash ^= iHash >> 15;
    iHash *= 0x846ca68bU;
    iHash ^= iHash >> 16;
    const bool bTracked = (int)(iHash % 10000) < iCoverage;
    if (m_abIntelligenceTracked[eObserver] == bTracked) return;
    m_abIntelligenceTracked[eObserver] = bTracked;
    if (plot()) plot()->changeVisibilityCount(eObserver, bTracked ? 1 : -1, NO_INVISIBLE, true);
}

void CvUnit::changeIntelligenceSight(CvPlot* pPlot, bool bIncrement, bool bUpdatePlotGroups) const
{
    // Only the occupied tile, with normal invisible-unit rules. No adjacent or recon sight.
    if (!pPlot) return;
    for (int i = 0; i < MAX_CIV_TEAMS; ++i)
        if (m_abIntelligenceTracked[i])
            pPlot->changeVisibilityCount((TeamTypes)i, bIncrement ? 1 : -1, NO_INVISIBLE, bUpdatePlotGroups);
}

int CvUnit::getIntelligenceTrackingChecksum() const
{
    int iValue = 0;
    for (int i = 0; i < MAX_CIV_TEAMS; ++i)
        if (m_abIntelligenceTracked[i]) iValue += (i + 1) * 157;
    return iValue;
}

int CvPlayer::getIntelligencePoliticalTarget() const
{
    int iPressure = 0;
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
    {
        const CvPlayer& kOther = GET_PLAYER((PlayerTypes)i);
        if (!kOther.isDynasticIntelligence() && kOther.canIntelligenceTarget(getID()) && kOther.getIntelligenceMode(getTeam()) == INTEL_POLITICS)
            iPressure += (kOther.getPoliticalInfluence(getID()) * 600 + 5000) / 10000;
    }
    return std::min(600, iPressure);
}

int CvPlayer::getPoliticalInfluence(PlayerTypes eTarget) const
{
    if (isDynasticIntelligence() || !canIntelligenceTarget(eTarget) ||
        getIntelligenceMode(GET_PLAYER(eTarget).getTeam()) != INTEL_POLITICS ||
        GET_PLAYER(eTarget).getNumCities() == 0) return 0;
    const int iStock = m_aiPoliticalStock[GET_PLAYER(eTarget).getTeam()];
    const __int64 iHalf = (__int64)2000 * (20 + GET_PLAYER(eTarget).getTotalPopulation());
    return (int)((__int64)10000 * iStock / (iStock + iHalf));
}

int CvPlayer::getPoliticalRelationBonus(PlayerTypes eTarget) const
{
    if (!canIntelligenceTarget(eTarget) || GET_TEAM(getTeam()).isAtWar(GET_PLAYER(eTarget).getTeam())) return 0;
    const int iInfluence = getPoliticalInfluence(eTarget);
    return iInfluence >= 7500 ? 2 : (iInfluence >= 2500 ? 1 : 0);
}

int CvPlayer::getPoliticalCivicChance(PlayerTypes eTarget) const
{
    const int iInfluence = getPoliticalInfluence(eTarget);
    if (iInfluence == 0 || GET_PLAYER(eTarget).isAnarchy() || GET_PLAYER(eTarget).getRevolutionTimer() > 0) return 0;
    for (int i = 0; i < GC.getNumCivicOptionInfos(); ++i)
    {
        const CivicTypes eCivic = getCivics((CivicOptionTypes)i);
        if (canForceCivics(eTarget, eCivic) &&
            (!GC.getGameINLINE().isForceCivicOption((CivicOptionTypes)i) || GC.getGameINLINE().isForceCivic(eCivic)))
            return 500 * iInfluence / (100 * intelligenceSpeedPercent());
    }
    return 0;
}

int CvPlayer::getPoliticalClientChance(PlayerTypes eTarget) const
{
    int iInfluence = getPoliticalInfluence(eTarget);
    if (iInfluence == 0 || getNumCities() == 0 || GET_TEAM(getTeam()).isAVassal() ||
        GC.getGameINLINE().isOption(GAMEOPTION_NO_VASSAL_STATES)) return 0;
    const TeamTypes eTeam = GET_PLAYER(eTarget).getTeam();
    const CvTeam& kTargetTeam = GET_TEAM(eTeam);
    if (kTargetTeam.isAVassal() || GET_TEAM(getTeam()).isAtWar(eTeam) || kTargetTeam.isArabianJihadWar(getTeam())) return 0;
    const CivicTypes eRepublic = (CivicTypes)GC.getInfoTypeForString("CIVIC_REPUBLIC");
    const CivicTypes eDemocracy = (CivicTypes)GC.getInfoTypeForString("CIVIC_DEMOCRACY");
    int iBaseChance = 100, iInstability = 20;
    // Vassalage affects the whole team: every living member must be vulnerable.
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
    {
        const CvPlayer& kTarget = GET_PLAYER((PlayerTypes)i);
        if (!kTarget.isAlive() || kTarget.getTeam() != eTeam) continue;
        if (kTarget.m_iIntelligenceStability >= -20 || kTarget.getNumCities() == 0) return 0;
        iInstability = std::min(iInstability, range(-kTarget.m_iIntelligenceStability - 20, 0, 20));
        iInfluence = std::min(iInfluence, getPoliticalInfluence((PlayerTypes)i));
        iBaseChance = std::min(iBaseChance, kTarget.isCivic(eDemocracy) ? 100 : (kTarget.isCivic(eRepublic) ? 30 : 10));
    }
    return (int)((__int64)iBaseChance * iInfluence * iInstability * 100 /
        ((__int64)10000 * 20 * intelligenceSpeedPercent()));
}

int CvPlayer::getPoliticalCultureBudget(PlayerTypes eTarget) const
{
    const int iInfluence = getPoliticalInfluence(eTarget);
    if (iInfluence == 0) return 0;
    int iNetworks = 0;
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
        if (getPoliticalInfluence((PlayerTypes)i) > 0) ++iNetworks;
    // A single culture budget across all targets: at most one culture per four EP.
    return (int)std::min((__int64)MAX_INT,
        (__int64)getCommerceRate(COMMERCE_ESPIONAGE) * 25 * iInfluence * 100 /
        ((__int64)10000 * std::max(1, iNetworks) * intelligenceSpeedPercent()));
}

void CvPlayer::doPoliticalIntelligence()
{
    if (isDynasticIntelligence()) return;
    bool abClientRolled[MAX_TEAMS] = {false};
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
    {
        const PlayerTypes eTarget = (PlayerTypes)i;
        if (getPoliticalInfluence(eTarget) == 0) continue;
        CvPlayer& kTarget = GET_PLAYER(eTarget);
        const TeamTypes eTeam = kTarget.getTeam();
        const int iBudget = getPoliticalCultureBudget(eTarget);
        const int iPopulation = std::max(1, kTarget.getTotalPopulation());
        int iCumulative = 0, iApplied = 0, iLoop;
        for (CvCity* pCity = kTarget.firstCity(&iLoop); pCity; pCity = kTarget.nextCity(&iLoop))
        {
            iCumulative += pCity->getPopulation();
            const int iShare = (int)((__int64)iBudget * iCumulative / iPopulation);
            pCity->changeCultureTimes100(getID(), iShare - iApplied, false, true);
            iApplied = iShare;
        }
        const int iCivicChance = getPoliticalCivicChance(eTarget);
        if (iCivicChance > 0 && GC.getGameINLINE().getSorenRandNum(10000, "Political civic adoption") < iCivicChance)
        {
            std::vector<CivicTypes> aCivics;
            for (int j = 0; j < GC.getNumCivicOptionInfos(); ++j)
            {
                const CivicTypes eCivic = getCivics((CivicOptionTypes)j);
                if (canForceCivics(eTarget, eCivic) &&
                    (!GC.getGameINLINE().isForceCivicOption((CivicOptionTypes)j) || GC.getGameINLINE().isForceCivic(eCivic)))
                    aCivics.push_back(eCivic);
            }
            if (!aCivics.empty())
            {
                const CivicTypes eCivic = aCivics[GC.getGameINLINE().getSorenRandNum((int)aCivics.size(), "Political civic selection")];
                const CivicOptionTypes eOption = (CivicOptionTypes)GC.getCivicInfo(eCivic).getCivicOptionType();
                kTarget.setCivics(eOption, eCivic);
                if (kTarget.getCivics(eOption) == eCivic)
                {
                    kTarget.setRevolutionTimer(std::max(kTarget.getRevolutionTimer(), scaledTurns(5)));
                    gDLL->getInterfaceIFace()->addMessage(getID(), false, GC.getEVENT_MESSAGE_TIME(),
                        gDLL->getText("TXT_KEY_INTEL_POLITICAL_REFORM", kTarget.getCivilizationShortDescriptionKey(), GC.getCivicInfo(eCivic).getTextKeyWide()), NULL, MESSAGE_TYPE_MINOR_EVENT);
                    gDLL->getInterfaceIFace()->addMessage(eTarget, false, GC.getEVENT_MESSAGE_TIME(),
                        gDLL->getText("TXT_KEY_INTEL_POLITICAL_REFORM", kTarget.getCivilizationShortDescriptionKey(), GC.getCivicInfo(eCivic).getTextKeyWide()), NULL, MESSAGE_TYPE_MINOR_EVENT);
                }
            }
        }
        if (!abClientRolled[eTeam])
        {
            abClientRolled[eTeam] = true;
            const int iChance = getPoliticalClientChance(eTarget);
            if (iChance > 0 && GC.getGameINLINE().getSorenRandNum(10000, "Political client government") < iChance)
            {
                GET_TEAM(getTeam()).assignVassal(eTeam, false);
                if (GET_TEAM(eTeam).isVassal(getTeam()))
                {
                    const CvWString szMessage = gDLL->getText("TXT_KEY_INTEL_POLITICAL_CLIENT", kTarget.getCivilizationShortDescriptionKey(), getCivilizationShortDescriptionKey());
                    gDLL->getInterfaceIFace()->addMessage(getID(), false, GC.getEVENT_MESSAGE_TIME(), szMessage, NULL, MESSAGE_TYPE_MAJOR_EVENT);
                    for (int j = 0; j < NUM_MAJOR_PLAYERS; ++j)
                        if (GET_PLAYER((PlayerTypes)j).isAlive() && GET_PLAYER((PlayerTypes)j).getTeam() == eTeam)
                            gDLL->getInterfaceIFace()->addMessage((PlayerTypes)j, false, GC.getEVENT_MESSAGE_TIME(), szMessage, NULL, MESSAGE_TYPE_MAJOR_EVENT);
                }
            }
        }
    }
}

int CvPlayer::getIntelligenceStabilityPenalty() const
{
    return GC.getGameINLINE().isOption(GAMEOPTION_NO_ESPIONAGE) || isBeingDynasticallyIncorporated() ? 0 :
        m_iIntelligencePressure / 100 + (m_iDynasticWarTurns > 0 ? 6 : 0);
}

int CvPlayer::getIntelligenceAnarchyExtra() const
{
    return getMaxAnarchyTurns() == 0 || GC.getGameINLINE().isOption(GAMEOPTION_NO_ESPIONAGE) ||
        isBeingDynasticallyIncorporated() ? 0 : scaledAnarchyTurns(m_iIntelligencePressure / 300);
}

bool CvPlayer::isDynasticIntelligence() const
{
    const CivicTypes eMonarchy = (CivicTypes)GC.getInfoTypeForString("CIVIC_MONARCHY");
    return eMonarchy != NO_CIVIC && getCivics((CivicOptionTypes)GC.getCivicInfo(eMonarchy).getCivicOptionType()) == eMonarchy;
}

bool CvPlayer::canDynasticTarget(PlayerTypes eTarget) const
{
    return canIntelligenceTarget(eTarget) && getNumCities() > 0 && GET_PLAYER(eTarget).getNumCities() > 0 &&
        isDynasticIntelligence() && GET_PLAYER(eTarget).isDynasticIntelligence();
}

bool CvPlayer::canFormDynasticUnion(PlayerTypes eTarget) const
{
    if (!canDynasticTarget(eTarget) || GC.getGameINLINE().isOption(GAMEOPTION_NO_VASSAL_STATES)) return false;
    const CvTeam& kOurs = GET_TEAM(getTeam());
    const CvTeam& kTheirs = GET_TEAM(GET_PLAYER(eTarget).getTeam());
    return !kOurs.isAVassal() && !kOurs.isAtWar(kTheirs.getID()) && !kTheirs.isArabianJihadWar(getTeam()) &&
        (!kTheirs.isAVassal() || kTheirs.isVassal(getTeam()));
}

int CvPlayer::getDynasticChance(PlayerTypes eTarget) const
{
    if (!canDynasticTarget(eTarget)) return 0;
    const TeamTypes eTeam = GET_PLAYER(eTarget).getTeam();
    const int iStage = m_aiDynasticStage[eTeam];
    if (iStage >= 4) return 0; // Incorporation is terminal.
    const int iStock = m_aiDynasticStock[eTeam];
    const int iOffset = iStage == 0 ? 0 : (iStage == 1 ? 500 : 1000);
    int iChance = (int)((__int64)2000 * iStock / ((__int64)iStock + 10000)) - iOffset;
    // War blocks advancement, but an unsupported dynasty can still regress.
    if (iChance > 0 && (GET_TEAM(getTeam()).isAtWar(eTeam) ||
        getIntelligenceMode(eTeam) != INTEL_POLITICS || (iStage == 2 && !canFormDynasticUnion(eTarget)))) return 0;
    return range(iChance * 100 / intelligenceSpeedPercent(), -10000, 10000);
}

int CvPlayer::getDynasticRelationBonus(PlayerTypes eTarget) const
{
    if (!canDynasticTarget(eTarget)) return 0;
    int iStage = m_aiDynasticStage[GET_PLAYER(eTarget).getTeam()];
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
    {
        const CvPlayer& kOther = GET_PLAYER((PlayerTypes)i);
        if (kOther.isAlive() && kOther.getTeam() == GET_PLAYER(eTarget).getTeam())
            iStage = std::max(iStage, kOther.m_aiDynasticStage[getTeam()]);
    }
    return std::min(2, iStage);
}

int CvPlayer::getDynasticInheritanceWeight(PlayerTypes eTarget) const
{
    if (eTarget < 0 || eTarget >= NUM_MAJOR_PLAYERS) return 100;
    TeamTypes eTeam = GET_PLAYER(eTarget).getTeam();
    int iStock = m_aiDynasticStock[eTeam];
    return 100 + 100 * m_aiDynasticStage[eTeam] + (int)((__int64)400 * iStock / ((__int64)iStock + 10000));
}

bool CvPlayer::isBeingDynasticallyIncorporated() const
{
    if (!isAlive() || getTeam() == NO_TEAM || GC.getGameINLINE().isOption(GAMEOPTION_NO_ESPIONAGE)) return false;
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
    {
        const CvPlayer& kHeir = GET_PLAYER((PlayerTypes)i);
        if (kHeir.isAlive() && kHeir.m_aiDynasticStage[getTeam()] == 4 &&
            GET_TEAM(getTeam()).isVassal(kHeir.getTeam())) return true;
    }
    return false;
}

void CvPlayer::setIntelligenceStability(int iValue)
{
    m_iIntelligenceStability = iValue;
}

void CvPlayer::onDynasticWar(TeamTypes eTarget)
{
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
        if (GET_PLAYER((PlayerTypes)i).isAlive() && GET_PLAYER((PlayerTypes)i).getTeam() == eTarget &&
            getDynasticRelationBonus((PlayerTypes)i) >= 2)
        {
            m_iDynasticWarTurns = std::max(m_iDynasticWarTurns, scaledTurns(20));
            gDLL->getInterfaceIFace()->addMessage(getID(), false, GC.getEVENT_MESSAGE_TIME(),
                gDLL->getText("TXT_KEY_INTEL_DYNASTIC_WAR", 6, scaledTurns(20)), NULL, MESSAGE_TYPE_MINOR_EVENT);
            break;
        }
}

void CvPlayer::doDynasticIntelligence(PlayerTypes eTarget)
{
    if (!canIntelligenceTarget(eTarget)) return;
    CvPlayer& kTarget = GET_PLAYER(eTarget);
    const TeamTypes eTeam = kTarget.getTeam();
    const int iTurn = GC.getGameINLINE().getGameTurn();
    if (m_aiDynasticLastRoll[eTeam] == iTurn) return;
    m_aiDynasticLastRoll[eTeam] = iTurn;
    if (m_aiDynasticStage[eTeam] == 4)
    {
        incorporateDynasticCity(eTarget);
        return;
    }
    if (!canDynasticTarget(eTarget)) return;
    // Broken personal unions revert to kinship. Completed incorporation never rolls again.
    if (m_aiDynasticStage[eTeam] == 3 && !GET_TEAM(eTeam).isVassal(getTeam()))
    {
        m_aiDynasticStage[eTeam] = 2;
        m_abDynasticUnion[eTeam] = false;
    }
    if (getIntelligenceMode(eTeam) == INTEL_POLITICS && !GET_TEAM(getTeam()).isAtWar(eTeam))
    {
        int iRate = getIntelligenceRate(eTarget);
        // Negative stability helps; positive stability never penalizes the network.
        iRate = (int)std::min((__int64)MAX_INT,
            (__int64)iRate * (100 + 2 * range(-kTarget.m_iIntelligenceStability, 0, 50)) / 100);
        m_aiDynasticStock[eTeam] = growIntelligenceStock(m_aiDynasticStock[eTeam], iRate);
    }
    const int iChance = getDynasticChance(eTarget);
    if (iChance == 0 || GC.getGameINLINE().getSorenRandNum(10000, "Dynastic stage") >= abs(iChance)) return;
    const int iOldStage = m_aiDynasticStage[eTeam];
    const int iNewStage = iOldStage + (iChance > 0 ? 1 : -1);
    if (iNewStage == 3 && iOldStage == 2)
    {
        const bool bAlreadyVassal = GET_TEAM(eTeam).isVassal(getTeam());
        if (!canFormDynasticUnion(eTarget)) return;
        if (!bAlreadyVassal) GET_TEAM(getTeam()).assignVassal(eTeam, false);
        if (!GET_TEAM(eTeam).isVassal(getTeam())) return;
        m_abDynasticUnion[eTeam] = !bAlreadyVassal;
    }
    m_aiDynasticStage[eTeam] = iNewStage;
    if (iOldStage == 3 && iNewStage == 2)
    {
        if (m_abDynasticUnion[eTeam] && GET_TEAM(eTeam).isVassal(getTeam())) GET_TEAM(getTeam()).freeVassal(eTeam);
        m_abDynasticUnion[eTeam] = false;
    }
    CvWString szStage = gDLL->getText(CvString::format("TXT_KEY_INTEL_DYNASTIC_STAGE_%d", iNewStage).c_str());
    gDLL->getInterfaceIFace()->addMessage(getID(), false, GC.getEVENT_MESSAGE_TIME(),
        gDLL->getText("TXT_KEY_INTEL_DYNASTIC_CHANGED", kTarget.getCivilizationShortDescriptionKey(), szStage.GetCString()), NULL, MESSAGE_TYPE_MINOR_EVENT);
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
        if (GET_PLAYER((PlayerTypes)i).isAlive() && GET_PLAYER((PlayerTypes)i).getTeam() == eTeam)
            gDLL->getInterfaceIFace()->addMessage((PlayerTypes)i, false, GC.getEVENT_MESSAGE_TIME(),
                gDLL->getText("TXT_KEY_INTEL_DYNASTIC_CHANGED", getCivilizationShortDescriptionKey(), szStage.GetCString()), NULL, MESSAGE_TYPE_MINOR_EVENT);
    if (iNewStage == 4) incorporateDynasticCity(eTarget);
}

void CvPlayer::incorporateDynasticCity(PlayerTypes eTarget)
{
    const TeamTypes eTeam = GET_PLAYER(eTarget).getTeam();
    if (GET_TEAM(getTeam()).isAtWar(eTeam) || !GET_TEAM(eTeam).isVassal(getTeam())) return;
    const int iTurn = GC.getGameINLINE().getGameTurn();
    CvCity* pBest = NULL;
    int iBestDistance = MAX_INT;
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
    {
        CvPlayer& kOwner = GET_PLAYER((PlayerTypes)i);
        if (kOwner.getTeam() != eTeam) continue;
        if (kOwner.m_iDynasticCityTurn == iTurn) return;
        int iLoop;
        for (CvCity* pCity = kOwner.firstCity(&iLoop); pCity; pCity = kOwner.nextCity(&iLoop))
        {
            int iOurLoop;
            for (CvCity* pOurs = firstCity(&iOurLoop); pOurs; pOurs = nextCity(&iOurLoop))
            {
                const int iDistance = plotDistance(pOurs->getX_INLINE(), pOurs->getY_INLINE(), pCity->getX_INLINE(), pCity->getY_INLINE());
                if (iDistance < iBestDistance) { iBestDistance = iDistance; pBest = pCity; }
            }
        }
    }
    if (!pBest) return;
    // Commit the once-per-game-turn guard before city-acquisition Python callbacks.
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
        if (GET_PLAYER((PlayerTypes)i).getTeam() == eTeam) GET_PLAYER((PlayerTypes)i).m_iDynasticCityTurn = iTurn;
    CvPlayer& kOldOwner = GET_PLAYER(pBest->getOwnerINLINE());
    const PlayerTypes eOldOwner = kOldOwner.getID();
    const CvWString szCityName = pBest->getName();
    // On the final city, preserve the remaining army instead of deleting it on elimination.
    std::vector<IDInfo> aUnits;
    int iLoop;
    for (CvUnit* pUnit = kOldOwner.firstUnit(&iLoop); pUnit; pUnit = kOldOwner.nextUnit(&iLoop))
        if (kOldOwner.getNumCities() == 1 || pUnit->plot() == pBest->plot()) aUnits.push_back(pUnit->getIDInfo());
    for (int i = 0; i < (int)aUnits.size(); ++i)
    {
        CvUnit* pOld = ::getUnit(aUnits[i]);
        if (!pOld) continue;
        CvUnit* pNew = initUnit(pOld->getUnitType(), pOld->getX_INLINE(), pOld->getY_INLINE(), pOld->AI_getUnitAIType());
        pNew->convert(pOld);
        pNew->finishMoves();
    }
    acquireCity(pBest, false, true, true);
    // City acquisition may change IDs; use the copied name for the announcement.
    gDLL->getInterfaceIFace()->addMessage(getID(), false, GC.getEVENT_MESSAGE_TIME(),
        gDLL->getText("TXT_KEY_INTEL_DYNASTIC_CITY", szCityName.GetCString(), getCivilizationShortDescriptionKey()), NULL, MESSAGE_TYPE_MINOR_EVENT);
    gDLL->getInterfaceIFace()->addMessage(eOldOwner, false, GC.getEVENT_MESSAGE_TIME(),
        gDLL->getText("TXT_KEY_INTEL_DYNASTIC_CITY", szCityName.GetCString(), getCivilizationShortDescriptionKey()), NULL, MESSAGE_TYPE_MINOR_EVENT);
}

int CvPlayer::getIntelligenceRelationPenalty(TeamTypes eTarget) const
{
    return (eTarget >= 0 && eTarget < MAX_TEAMS) ? (m_aiIntelligenceExposure[eTarget] + 9999) / 10000 : 0;
}

bool CvPlayer::hasIntelligenceCityVisibility(const CvCity* pCity) const
{
    PlayerTypes eTarget = pCity->getOwnerINLINE();
    if (!canIntelligenceTarget(eTarget)) return false;
    TeamTypes eTeam = GET_PLAYER(eTarget).getTeam();
    if (m_aiIntelligenceStrength[eTeam] <= 0) return false;
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
    if (iField == 25) return getIntelligenceAnarchyExtra();
    if (iField == 26) return scaledAnarchyTurns(2);
    if (iField == 28) return mapReportRadius();
    if (iField == 29) return scaledChance(25);
    if (iField == 32) return isDynasticIntelligence() ? 1 : 0;
    if (iField == 41) return m_iDynasticWarTurns;
    if (iField == 42) return isBeingDynasticallyIncorporated() ? 1 : 0;
    if (iField == 45) return scaledTurns(20);
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
    case 30: return getIntelligenceMilitaryCoverage(eTarget);
    case 31: return m_aiIntelligenceMilitaryStock[eTeam] / 100;
    case 33: return m_aiDynasticStage[eTeam];
    case 34: return m_aiDynasticStock[eTeam] / 100;
    case 35: return getDynasticChance(eTarget);
    case 36: return canDynasticTarget(eTarget) ? 1 : 0;
    case 37: return getDynasticRelationBonus(eTarget);
    case 38: return getDynasticInheritanceWeight(eTarget);
    case 39: return canFormDynasticUnion(eTarget) ? 1 : 0;
    case 46: return m_aiPoliticalStock[eTeam] / 100;
    case 47: return getPoliticalInfluence(eTarget);
    case 48: return getPoliticalCivicChance(eTarget);
    case 49: return getPoliticalClientChance(eTarget);
    case 50: return getPoliticalRelationBonus(eTarget);
    case 51: return getPoliticalCultureBudget(eTarget);
    case 8: return getIntelligenceRelationPenalty(eTeam);
    case 9: return getIntelligenceDefense(eTarget);
    case 10: return getIntelligenceData(iTarget, 24) / 100;
    case 24: return scaledChance(std::min(25, getIntelligenceRate(eTarget) * 25 / (30 + GET_PLAYER(eTarget).getNumCities() * 3)));
    case 27:
        if (isDynasticIntelligence() && getIntelligenceMode(eTeam) == INTEL_POLITICS) return 0;
        return scaledChance(getIntelligenceMode(eTeam) == INTEL_POLITICS ? 6 : (getIntelligenceMode(eTeam) == INTEL_MILITARY ? 3 : 1));
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
    case 12: return !isDynasticIntelligence() && canIntelligenceTarget(eTarget) && getIntelligenceMode(eTeam) == INTEL_POLITICS ?
        (getPoliticalInfluence(eTarget) * 600 + 5000) / 10000 : 0;
    }
    return 0;
}

void CvPlayer::doIntelligencePressure()
{
    if (m_iDynasticWarTurns > 0) --m_iDynasticWarTurns;
    int iTarget = getIntelligencePoliticalTarget();
    int iStep = std::max(1, 2000 / GC.getGameSpeedInfo(GC.getGameINLINE().getGameSpeedType()).getResearchPercent());
    if (iTarget > m_iIntelligencePressure) m_iIntelligencePressure = std::min(iTarget, m_iIntelligencePressure + iStep);
    else m_iIntelligencePressure = std::max(iTarget, m_iIntelligencePressure - iStep);
    if (m_iIntelligenceUnrestCooldown > 0) --m_iIntelligenceUnrestCooldown;
    if (!isBeingDynasticallyIncorporated() && m_iIntelligencePressure >= 100 && m_iIntelligenceUnrestCooldown == 0 &&
        GC.getGameINLINE().getSorenRandNum(10000, "Intelligence unrest") < scaledChance(m_iIntelligencePressure / 100))
    {
        int iLoop;
        CvCity* pCity;
        // City IDs are sparse; use an ordinal rather than relying on their IDs.
        int iOrdinal = GC.getGameINLINE().getSorenRandNum(std::max(1, getNumCities()), "Intelligence unrest selection");
        for (pCity = firstCity(&iLoop); pCity && iOrdinal > 0; pCity = nextCity(&iLoop)) --iOrdinal;
        if (pCity)
        {
            pCity->startIntelligenceUnrest(scaledTurns(2));
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
    // Commit queued choices and update network buildup only at a turn boundary.
    for (int t = 0; t < MAX_TEAMS; ++t)
    {
        m_aiIntelligenceMode[t] = m_aiEspionageSpendingWeightAgainstTeam[t];
        m_aiIntelligenceStrength[t] = 0;
        // Decay even when funding stops or a different operation is selected.
        // Normal: B_next = 0.95 * B + effective output. XL uses half-sized steps.
        m_aiIntelligenceMilitaryStock[t] = decayIntelligenceStock(m_aiIntelligenceMilitaryStock[t]);
        m_aiPoliticalStock[t] = decayIntelligenceStock(m_aiPoliticalStock[t]);
        m_aiDynasticStock[t] = decayIntelligenceStock(m_aiDynasticStock[t]);
        if (m_aiIntelligenceExposure[t] > 0) m_aiIntelligenceExposure[t] = std::max(0, m_aiIntelligenceExposure[t] - std::max(1, 20000 / intelligenceSpeedPercent()));
    }
    if (GC.getGameINLINE().isOption(GAMEOPTION_NO_ESPIONAGE))
    {
        refreshIntelligenceTracking();
        return;
    }
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
        bool bFirst = true;
        for (int j = 0; j < i; ++j)
            if (GET_PLAYER((PlayerTypes)j).getTeam() == eTeam && canIntelligenceTarget((PlayerTypes)j)) bFirst = false;
        if (bFirst) doDynasticIntelligence(eTarget);
        if (bFirst && !isDynasticIntelligence() && getIntelligenceMode(eTeam) == INTEL_POLITICS)
            m_aiPoliticalStock[eTeam] = growIntelligenceStock(m_aiPoliticalStock[eTeam], iStrength);
        if (getIntelligenceMode(eTeam) == INTEL_MILITARY)
        {
            // Count each target team once, including in team games. Leave headroom for arithmetic.
            if (bFirst)
                m_aiIntelligenceMilitaryStock[eTeam] = growIntelligenceStock(m_aiIntelligenceMilitaryStock[eTeam], iStrength);
        }
        if (!(isDynasticIntelligence() && getIntelligenceMode(eTeam) == INTEL_POLITICS) &&
            (iStrength > 0 || (getIntelligenceMode(eTeam) == INTEL_MILITARY && m_aiIntelligenceMilitaryStock[eTeam] > 0) ||
            (getIntelligenceMode(eTeam) == INTEL_POLITICS && m_aiPoliticalStock[eTeam] > 0)))
        {
            int iMode = getIntelligenceMode(eTeam);
            int iSeverity = iMode == INTEL_POLITICS ? 3 : (iMode == INTEL_MILITARY ? 2 : 1);
            int iRisk = iMode == INTEL_POLITICS ? 6 : (iMode == INTEL_MILITARY ? 3 : 1);
            if (GC.getGameINLINE().getSorenRandNum(10000, "Intelligence discovery") < scaledChance(iRisk))
            {
                m_aiIntelligenceExposure[eTeam] = std::max(m_aiIntelligenceExposure[eTeam],
                    std::min(iMode == INTEL_POLITICS ? 60000 : (iMode == INTEL_MILITARY ? 30000 : 10000), m_aiIntelligenceExposure[eTeam] + 10000 * iSeverity));
                gDLL->getInterfaceIFace()->addMessage(getID(), false, GC.getEVENT_MESSAGE_TIME(),
                    gDLL->getText("TXT_KEY_INTEL_DISCOVERED", kTarget.getCivilizationShortDescriptionKey()), NULL, MESSAGE_TYPE_MINOR_EVENT);
                gDLL->getInterfaceIFace()->addMessage(eTarget, false, GC.getEVENT_MESSAGE_TIME(),
                    gDLL->getText("TXT_KEY_INTEL_DETECTED", getCivilizationShortDescriptionKey()), NULL, MESSAGE_TYPE_MINOR_EVENT);
            }
        }
        // A decaying network can still infiltrate after funding is reduced to zero.
        if (getIntelligenceMode(eTeam) == INTEL_MILITARY && GET_TEAM(getTeam()).isAtWar(eTeam))
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
        if (iStrength > 0)
        {
            if (getIntelligenceMode(eTeam) == INTEL_MAPS && GC.getGameINLINE().getSorenRandNum(10000, "Intelligence map report") < getIntelligenceData(i, 24))
            {
                CvCity* pBest = NULL;
                const int iRadius = mapReportRadius();
                int iBest = -1, iCityLoop;
                for (CvCity* pCity = kTarget.firstCity(&iCityLoop); pCity; pCity = kTarget.nextCity(&iCityLoop))
                {
                    int iUnknown = 0;
                    for (int dx = -iRadius; dx <= iRadius; ++dx) for (int dy = -iRadius; dy <= iRadius; ++dy)
                    {
                        CvPlot* pPlot = plotXY(pCity->getX_INLINE(), pCity->getY_INLINE(), dx, dy);
                        if (pPlot && !pPlot->isRevealed(getTeam(), false)) ++iUnknown;
                    }
                    int iScore = iUnknown * 100 + GC.getGameINLINE().getSorenRandNum(100, "Intelligence report city");
                    if (iScore > iBest) { pBest = pCity; iBest = iScore; }
                }
                if (pBest)
                {
                    for (int dx = -iRadius; dx <= iRadius; ++dx) for (int dy = -iRadius; dy <= iRadius; ++dy)
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
    refreshIntelligenceTracking();
    doPoliticalIntelligence();
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
        m_iIntelligenceUnrestCooldown * 107 + m_iIntelligenceLastResearch * 109 +
        m_iIntelligenceStability * 157 + m_iDynasticWarTurns * 163 + (m_iDynasticCityTurn + 1) * 167;
    for (int i = 0; i < MAX_TEAMS; ++i)
        iValue += (i + 1) * (m_aiIntelligenceMode[i] * 113 + m_aiEspionageSpendingWeightAgainstTeam[i] * 127 +
            m_aiIntelligenceStrength[i] * 131 + m_aiIntelligenceExposure[i] * 137 +
            m_aiIntelligenceMilitaryStock[i] * 151 +
            m_aiPoliticalStock[i] * 193 +
            m_aiDynasticStock[i] * 173 + m_aiDynasticStage[i] * 179 +
            (m_aiDynasticLastRoll[i] + 1) * 181 + m_abDynasticUnion[i] * 191 +
            (m_aiIntelligenceReportCity[i] + 1) * 139 + (m_aiIntelligenceReportUntil[i] + 1) * 149);
    int iLoop;
    for (CvUnit* pUnit = firstUnit(&iLoop); pUnit; pUnit = nextUnit(&iLoop))
        iValue += (pUnit->getID() + 1) * pUnit->getIntelligenceTrackingChecksum();
    return iValue;
}
