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
    // Calendar scaling is shared by task-force planning and operation effects.
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

    int decayIntelligenceStock(int iStock)
    {
        const int iDecay = std::min(10000, std::max(1, 100000 / intelligenceSpeedPercent()));
        return iStock - (int)(((__int64)iStock * iDecay + 9999) / 10000);
    }
}

int CvPlayer::getIntelligenceForceCount() const
{
    return std::min(MAX_TEAMS, std::max(1, (int)getCurrentEra() + 1));
}

void CvPlayer::setIntelligenceForceMode(int iForce, int iMode)
{
    if (iForce < 0 || iForce >= getIntelligenceForceCount() || iMode < 0 || iMode >= NUM_INTELLIGENCE_MODES) return;
    if (iMode == INTEL_COOPERATION)
    {
        bool bEligible = false;
        for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
            if (canIntelligenceTarget((PlayerTypes)i) && GET_TEAM(getTeam()).isIntelligenceCooperation(GET_PLAYER((PlayerTypes)i).getTeam())) bEligible = true;
        if (!bEligible) return;
    }
    m_aiForcePending[iForce] = iMode;
    gDLL->getInterfaceIFace()->setDirty(Espionage_Advisor_DIRTY_BIT, true);
}

int CvPlayer::getIntelligenceTargetScore(PlayerTypes eTarget, int iMode) const
{
    if (!canIntelligenceTarget(eTarget) || iMode == INTEL_NONE) return 0;
    const CvPlayerAI& kTarget = GET_PLAYER(eTarget);
    const TeamTypes eTeam = kTarget.getTeam();
    if (kTarget.getNumCities() == 0) return 0;
    const bool bWar = GET_TEAM(getTeam()).isAtWar(eTeam);
    const int iAttitude = GET_TEAM(getTeam()).AI_getAttitudeVal(eTeam);
    int iValue = 100;
    switch (iMode)
    {
    case INTEL_TECHNOLOGY:
        if (getIntelligenceTechCount(eTarget) == 0) return 0;
        iValue = 100 + 10 * std::min(10, getIntelligenceTechCount(eTarget));
        if (m_eIntelligenceResearch != NO_TECH && GET_TEAM(eTeam).isHasTech(m_eIntelligenceResearch)) iValue *= 4;
        break;
    case INTEL_MILITARY:
        // War, relations and geographic proximity contribute independently.
        iValue = 30 + (bWar ? 180 : 0) + std::min(100, 10 * std::max(0, -iAttitude)) +
            (GET_TEAM(getTeam()).AI_isLandTarget(eTeam) ? 70 : 0);
        break;
    case INTEL_POLITICS:
        if (isDynasticIntelligence())
        {
            if (bWar || !canDynasticTarget(eTarget) || m_aiDynasticStage[eTeam] >= 4 ||
                (m_aiDynasticStage[eTeam] == 2 && !canFormDynasticUnion(eTarget))) return 0;
            iValue = 100 + 20 * m_aiDynasticStage[eTeam] + 2 * range(-kTarget.m_iIntelligenceStability, 0, 50);
        }
        else iValue = 100 + std::min(100, 4 * std::max(0, -kTarget.m_iIntelligenceStability));
        break;
    case INTEL_ECONOMY:
        iValue = 50 + std::min(200, kTarget.getCommerceRate(COMMERCE_GOLD));
        break;
    case INTEL_COOPERATION:
        if (!GET_TEAM(getTeam()).isIntelligenceCooperation(eTeam)) return 0;
        {
            const int aiTrust[] = {0, 10, 35, 75, 100};
            const int iOurs = isHuman() ? ATTITUDE_FRIENDLY : GET_TEAM(getTeam()).AI_getAttitude(eTeam);
            const int iTheirs = GET_TEAM(eTeam).isHuman() ? ATTITUDE_FRIENDLY : GET_TEAM(eTeam).AI_getAttitude(getTeam());
            int iOutput = 0;
            for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
                if (GET_PLAYER((PlayerTypes)i).isAlive() && GET_PLAYER((PlayerTypes)i).getTeam() == eTeam)
                    iOutput += GET_PLAYER((PlayerTypes)i).getCommerceRate(COMMERCE_ESPIONAGE);
            iValue = iOutput * aiTrust[std::min(iOurs, iTheirs)] / 100;
        }
        break;
    default: return 0;
    }
    const int iAccess = getIntelligenceAccess(eTarget);
    const int iAttack = std::max(1, getCommerceRate(COMMERCE_ESPIONAGE)) * iAccess / 100;
    const int iResistance = iMode == INTEL_COOPERATION ? 100 :
        (int)((__int64)(iAttack + 20) * 100 / (iAttack + 20 + getIntelligenceDefense(eTarget)));
    return (int)std::min((__int64)MAX_INT / 8, (__int64)iValue * iAccess * iResistance / 100);
}

void CvPlayer::updateIntelligenceForces()
{
    const int iTurn = GC.getGameINLINE().getGameTurn();
    for (int f = 0; f < getIntelligenceForceCount(); ++f)
    {
        const bool bChanged = m_aiForceMode[f] != m_aiForcePending[f];
        m_aiForceMode[f] = m_aiForcePending[f];
        if (!bChanged && iTurn < m_aiForceNextTurn[f]) continue;
        m_aiForceNextTurn[f] = iTurn + scaledTurns(5);
        for (int j = 0; j < 3; ++j) m_aiForceTargets[f][j] = NO_PLAYER;
        int aiPlayers[3] = {NO_PLAYER, NO_PLAYER, NO_PLAYER};
        int aiScores[3] = {0, 0, 0};
        bool abTeams[MAX_TEAMS] = {false};
        for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
        {
            const PlayerTypes eTarget = (PlayerTypes)i;
            if (!canIntelligenceTarget(eTarget)) continue;
            const TeamTypes eTeam = GET_PLAYER(eTarget).getTeam();
            if (abTeams[eTeam]) continue;
            abTeams[eTeam] = true;
            int iScore = getIntelligenceTargetScore(eTarget, m_aiForceMode[f]);
            for (int j = 0; j < 3; ++j)
                if (iScore > aiScores[j])
                {
                    for (int k = 2; k > j; --k) { aiScores[k] = aiScores[k-1]; aiPlayers[k] = aiPlayers[k-1]; }
                    aiScores[j] = iScore; aiPlayers[j] = i; break;
                }
        }
        // Compare useful total output: equal targets yield 100%, 140%, 171%.
        const int aiShare[] = {100, 70, 57};
        __int64 iSum = 0, iBest = 0;
        int iCount = 0;
        for (int j = 0; j < 3 && aiScores[j] > 0; ++j)
        {
            iSum += aiScores[j];
            const __int64 iValue = iSum * aiShare[j];
            if (iValue > iBest) { iBest = iValue; iCount = j + 1; }
        }
        for (int j = 0; j < iCount; ++j) m_aiForceTargets[f][j] = aiPlayers[j];
    }
    const int iActive = std::max(1, getIntelligenceActiveForces());
    for (int f = 0; f < getIntelligenceForceCount(); ++f)
    {
        for (int m = 0; m < NUM_INTELLIGENCE_MODES; ++m)
            m_aiForceStock[f][m] = decayIntelligenceStock(m_aiForceStock[f][m]);
        const int iMode = m_aiForceMode[f];
        bool bActive = false;
        for (int j = 0; j < 3; ++j)
            if (m_aiForceTargets[f][j] >= 0 && canIntelligenceTarget((PlayerTypes)m_aiForceTargets[f][j]) &&
                (iMode != INTEL_COOPERATION || GET_TEAM(getTeam()).isIntelligenceCooperation(GET_PLAYER((PlayerTypes)m_aiForceTargets[f][j]).getTeam()))) bActive = true;
        if (iMode == INTEL_NONE || !bActive) continue;
        // Preserve fractions at low EP: output / active forces + 10% of total output.
        m_aiForceStock[f][iMode] = (int)std::min((__int64)MAX_INT / 2,
            (__int64)m_aiForceStock[f][iMode] + (__int64)getCommerceRate(COMMERCE_ESPIONAGE) *
            (10000 + 1000 * iActive) * 2 / (iActive * intelligenceSpeedPercent()));
    }
}

int CvPlayer::getIntelligenceActiveForces() const
{
    int iCount = 0;
    for (int f = 0; f < getIntelligenceForceCount(); ++f)
        if (m_aiForceMode[f] != INTEL_NONE)
            for (int j = 0; j < 3; ++j)
                if (m_aiForceTargets[f][j] >= 0 && canIntelligenceTarget((PlayerTypes)m_aiForceTargets[f][j]) &&
                    (m_aiForceMode[f] != INTEL_COOPERATION || GET_TEAM(getTeam()).isIntelligenceCooperation(GET_PLAYER((PlayerTypes)m_aiForceTargets[f][j]).getTeam())))
                { ++iCount; break; }
    return iCount;
}

int CvPlayer::getIntelligenceAllocation(TeamTypes eTarget, int iMode) const
{
    int iTotal = 0;
    const int iActive = std::max(1, getIntelligenceActiveForces());
    for (int f = 0; f < getIntelligenceForceCount(); ++f)
    {
        if (m_aiForceMode[f] != iMode || iMode == INTEL_NONE) continue;
        int iCount = 0;
        for (int j = 0; j < 3; ++j) if (m_aiForceTargets[f][j] >= 0) ++iCount;
        const int aiShare[] = {0, 100, 70, 57};
        for (int j = 0; j < iCount; ++j)
        {
            const PlayerTypes ePlayer = (PlayerTypes)m_aiForceTargets[f][j];
            if (canIntelligenceTarget(ePlayer) && GET_PLAYER(ePlayer).getTeam() == eTarget &&
                (iMode != INTEL_COOPERATION || GET_TEAM(getTeam()).isIntelligenceCooperation(eTarget)))
                iTotal += (10000 / iActive + 1000) * aiShare[iCount] / 100;
        }
    }
    return iTotal;
}

bool CvPlayer::hasIntelligenceMode(TeamTypes eTarget, int iMode) const
{
    return getIntelligenceAllocation(eTarget, iMode) > 0;
}

int CvPlayer::getIntelligenceModeRate(PlayerTypes eTarget, int iMode) const
{
    if (!canIntelligenceTarget(eTarget)) return 0;
    return (int)((__int64)getIntelligenceRate(eTarget) * getIntelligenceAllocation(GET_PLAYER(eTarget).getTeam(), iMode) / 10000);
}

void CvPlayer::rebuildIntelligenceStocks()
{
    for (int t = 0; t < MAX_TEAMS; ++t)
    {
        m_aiCooperationStock[t] = m_aiTechnologyStock[t] = m_aiIntelligenceMilitaryStock[t] = 0;
        m_aiPoliticalStock[t] = m_aiEconomicStock[t] = m_aiDynasticStock[t] = 0;
    }
    for (int iPass = 0; iPass < 2; ++iPass)
    for (int f = 0; f < getIntelligenceForceCount(); ++f)
    {
        const int iMode = m_aiForceMode[f];
        if ((iMode == INTEL_COOPERATION) != (iPass == 0)) continue;
        int iCount = 0;
        for (int j = 0; j < 3; ++j) if (m_aiForceTargets[f][j] >= 0) ++iCount;
        const int aiShare[] = {0, 100, 70, 57};
        for (int j = 0; j < iCount; ++j)
        {
            const PlayerTypes eTarget = (PlayerTypes)m_aiForceTargets[f][j];
            if (!canIntelligenceTarget(eTarget) || iMode == INTEL_NONE) continue;
            const TeamTypes eTeam = GET_PLAYER(eTarget).getTeam();
            if (iMode == INTEL_COOPERATION && !GET_TEAM(getTeam()).isIntelligenceCooperation(eTeam)) continue;
            const int iBase = std::max(1, getCommerceRate(COMMERCE_ESPIONAGE));
            const int iOutput = iMode == INTEL_COOPERATION || GET_TEAM(getTeam()).isIntelligenceCooperation(eTeam) ? iBase : getEffectiveEspionage();
            const int iAccess = getIntelligenceAccess(eTarget);
            const __int64 iAttack = (__int64)iOutput * iAccess / 100;
            __int64 iStock = (__int64)m_aiForceStock[f][iMode] * aiShare[iCount] / 100 * iAccess / 100;
            if (iMode != INTEL_COOPERATION)
                iStock = iStock * (iAttack + 20) / (iAttack + 20 + getIntelligenceDefense(eTarget)) * std::max(1, iOutput) / iBase;
            int* pStock = NULL;
            switch (iMode)
            {
            case INTEL_TECHNOLOGY: pStock = &m_aiTechnologyStock[eTeam]; break;
            case INTEL_MILITARY: pStock = &m_aiIntelligenceMilitaryStock[eTeam]; break;
            case INTEL_POLITICS:
                pStock = isDynasticIntelligence() ? &m_aiDynasticStock[eTeam] : &m_aiPoliticalStock[eTeam];
                if (isDynasticIntelligence()) iStock = iStock * (100 + 2 * range(-GET_PLAYER(eTarget).m_iIntelligenceStability, 0, 50)) / 100;
                break;
            case INTEL_ECONOMY: pStock = &m_aiEconomicStock[eTeam]; break;
            case INTEL_COOPERATION: pStock = &m_aiCooperationStock[eTeam]; break;
            }
            if (pStock) *pStock = (int)std::min((__int64)MAX_INT / 2, *pStock + iStock);
        }
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

void CvPlayer::cancelIntelligenceCooperation(TeamTypes eTarget)
{
    if (m_aiIntelligenceMode[eTarget] == INTEL_COOPERATION) m_aiIntelligenceMode[eTarget] = INTEL_NONE;
    if (m_aiEspionageSpendingWeightAgainstTeam[eTarget] == INTEL_COOPERATION)
        m_aiEspionageSpendingWeightAgainstTeam[eTarget] = INTEL_NONE;
}

int CvPlayer::getCooperationInfluence(PlayerTypes eTarget) const
{
    if (!canIntelligenceTarget(eTarget) || getCommerceRate(COMMERCE_ESPIONAGE) <= 0) return 0;
    const CvPlayerAI& kPartner = GET_PLAYER(eTarget);
    const TeamTypes eTeam = kPartner.getTeam();
    if (!GET_TEAM(getTeam()).isIntelligenceCooperation(eTeam) || !hasIntelligenceMode(eTeam, INTEL_COOPERATION)) return 0;
    // Human consent comes from the agreement, never a hidden AI attitude toward another human.
    const AttitudeTypes eOurs = isHuman() ? ATTITUDE_FRIENDLY : GET_TEAM(getTeam()).AI_getAttitude(eTeam);
    const AttitudeTypes eTheirs = GET_TEAM(eTeam).isHuman() ? ATTITUDE_FRIENDLY : GET_TEAM(eTeam).AI_getAttitude(getTeam());
    const int aiTrust[] = {0, 10, 35, 75, 100};
    const int iTrust = aiTrust[std::min(eOurs, eTheirs)];
    const __int64 iStock = m_aiCooperationStock[eTeam];
    return (int)(iStock * iTrust * 100 / (iStock + 40000));
}

int CvPlayer::getCooperationContribution(PlayerTypes eTarget) const
{
    const int iInfluence = getCooperationInfluence(eTarget);
    if (iInfluence <= 0) return 0;
    __int64 iBase = 0;
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
        if (GET_PLAYER((PlayerTypes)i).isAlive() && GET_PLAYER((PlayerTypes)i).getTeam() == GET_PLAYER(eTarget).getTeam())
            iBase += GET_PLAYER((PlayerTypes)i).getCommerceRate(COMMERCE_ESPIONAGE);
    // Only the partner's commerce output is shared, never its cooperation bonus.
    return (int)std::min((__int64)MAX_INT / 2, iBase * iInfluence / 10000);
}

int CvPlayer::getCooperationBonus() const
{
    if (GC.getGameINLINE().isOption(GAMEOPTION_NO_ESPIONAGE)) return 0;
    __int64 iBonus = 0;
    bool abCounted[MAX_TEAMS] = {false};
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
    {
        const PlayerTypes ePartner = (PlayerTypes)i;
        if (!canIntelligenceTarget(ePartner)) continue;
        const TeamTypes eTeam = GET_PLAYER(ePartner).getTeam();
        if (abCounted[eTeam]) continue;
        abCounted[eTeam] = true;
        iBonus += getCooperationContribution(ePartner);
    }
    return (int)std::min((__int64)getCommerceRate(COMMERCE_ESPIONAGE), iBonus);
}

int CvPlayer::getEffectiveEspionage() const
{
    return (int)std::min((__int64)MAX_INT / 2, (__int64)getCommerceRate(COMMERCE_ESPIONAGE) + getCooperationBonus());
}

int CvPlayer::getCooperationStability() const
{
    return GC.getGameINLINE().isOption(GAMEOPTION_NO_ESPIONAGE) ? 0 : (m_iCooperationStability + 50) / 100;
}

void CvPlayer::doIntelligenceCooperation()
{
    int iBestInfluence = 0;
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
    {
        const PlayerTypes ePartner = (PlayerTypes)i;
        if (!canIntelligenceTarget(ePartner)) continue;
        iBestInfluence = std::max(iBestInfluence, getCooperationInfluence(ePartner));
        // The strongest incoming OR outgoing partnership benefits both parties.
        iBestInfluence = std::max(iBestInfluence, GET_PLAYER(ePartner).getCooperationInfluence(getID()));
    }
    const int iTarget = 300 * iBestInfluence / 10000;
    if (m_iCooperationStability < iTarget)
        m_iCooperationStability = std::min(iTarget, m_iCooperationStability + std::max(1, 2000 / intelligenceSpeedPercent()));
    else
        m_iCooperationStability = std::max(iTarget, m_iCooperationStability - std::max(1, 2000 / intelligenceSpeedPercent()));
}

int CvPlayer::getIntelligenceRate(PlayerTypes eTarget) const
{
    if (!canIntelligenceTarget(eTarget)) return 0;
    // Cooperation never enhances operations against an agreement partner.
    const int iOutput = GET_TEAM(getTeam()).isIntelligenceCooperation(GET_PLAYER(eTarget).getTeam()) ?
        getCommerceRate(COMMERCE_ESPIONAGE) : getEffectiveEspionage();
    const __int64 iAttack = (__int64)iOutput * getIntelligenceAccess(eTarget) / 100;
    return (int)std::min((__int64)MAX_INT, iAttack * (iAttack + 20) /
        std::max((__int64)1, iAttack + 20 + getIntelligenceDefense(eTarget)));
}

int CvPlayer::getIntelligenceMode(TeamTypes eTarget) const
{
    for (int m = 0; m < INTEL_NONE; ++m)
        if (hasIntelligenceMode(eTarget, m)) return m;
    return INTEL_NONE;
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

int CvPlayer::getIntelligenceTechInfluence(PlayerTypes eTarget) const
{
    if (!canIntelligenceTarget(eTarget)) return 0;
    const int iRate = getIntelligenceModeRate(eTarget, INTEL_TECHNOLOGY);
    if (iRate <= 0) return 0;
    const int iStock = m_aiTechnologyStock[GET_PLAYER(eTarget).getTeam()];
    const __int64 iSteady = (__int64)2000 * iRate;
    if (iStock >= iSteady) return 10000;
    const __int64 iHalf = 2000 * (20 + (__int64)GET_PLAYER(eTarget).getCommerceRate(COMMERCE_RESEARCH));
    // Normalize saturation to the equilibrium at current funding. A mature network
    // approaches the original stealing rate, never exceeds it, and must rebuild after a funding increase.
    // Divide first at millionth precision to keep all intermediate products within 64 bits.
    const __int64 iFraction = (__int64)iStock * 1000000 / iSteady;
    return (int)std::min((__int64)10000, iFraction * (iSteady + iHalf) / (iStock + iHalf) / 100);
}

int CvPlayer::getIntelligenceTechRate(PlayerTypes eTarget) const
{
    if (!canIntelligenceTarget(eTarget) || !hasIntelligenceMode(GET_PLAYER(eTarget).getTeam(), INTEL_TECHNOLOGY)) return 0;
    return (int)std::min((__int64)MAX_INT / 4, (__int64)getIntelligenceModeRate(eTarget, INTEL_TECHNOLOGY) *
        (100 + 10 * std::min(10, getIntelligenceTechCount(eTarget))) * getIntelligenceTechInfluence(eTarget) / 1000000);
}

int CvPlayer::getIntelligenceResearchRate(TechTypes eTech) const
{
    if (eTech == NO_TECH || GET_TEAM(getTeam()).isHasTech(eTech) || !canResearch(eTech)) return 0;
    std::vector<int> aRates;
    bool abCounted[MAX_TEAMS] = {false};
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
    {
        PlayerTypes eTarget = (PlayerTypes)i;
        if (!canIntelligenceTarget(eTarget)) continue;
        const TeamTypes eTeam = GET_PLAYER(eTarget).getTeam();
        if (abCounted[eTeam]) continue;
        abCounted[eTeam] = true;
        if (hasIntelligenceMode(eTeam, INTEL_TECHNOLOGY) && GET_TEAM(eTeam).isHasTech(eTech))
            aRates.push_back(getIntelligenceTechRate(eTarget));
    }
    std::sort(aRates.begin(), aRates.end(), std::greater<int>());
    int iTotal = 0;
    for (int j = 0; j < (int)aRates.size(); ++j) iTotal += aRates[j];
    return (int)std::min((__int64)iTotal, (__int64)3 * getEffectiveEspionage());
}

int CvPlayer::getIntelligenceMilitaryBonus(PlayerTypes eTarget) const
{
    // Basis points preserve marginal gains near the limit in combat as well as in the advisor.
    return 30 * getIntelligenceMilitaryCoverage(eTarget) / 100;
}

int CvPlayer::getIntelligenceMilitaryCoverage(PlayerTypes eTarget) const
{
    if (!canIntelligenceTarget(eTarget) || !hasIntelligenceMode(GET_PLAYER(eTarget).getTeam(), INTEL_MILITARY)) return 0;
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
        if (!kOther.isDynasticIntelligence() && kOther.canIntelligenceTarget(getID()) && kOther.hasIntelligenceMode(getTeam(), INTEL_POLITICS))
            iPressure += (kOther.getPoliticalInfluence(getID()) * 600 + 5000) / 10000;
    }
    return std::min(600, iPressure);
}

int CvPlayer::getPoliticalInfluence(PlayerTypes eTarget) const
{
    if (isDynasticIntelligence() || !canIntelligenceTarget(eTarget) ||
        !hasIntelligenceMode(GET_PLAYER(eTarget).getTeam(), INTEL_POLITICS) ||
        GET_PLAYER(eTarget).getNumCities() == 0) return 0;
    const int iStock = m_aiPoliticalStock[GET_PLAYER(eTarget).getTeam()];
    const __int64 iHalf = 2000 * 20;
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
    // Force allocation already includes the funding split and target concentration.
    return (int)std::min((__int64)MAX_INT,
        (__int64)(GET_TEAM(getTeam()).isIntelligenceCooperation(GET_PLAYER(eTarget).getTeam()) ?
            getCommerceRate(COMMERCE_ESPIONAGE) : getEffectiveEspionage()) * getIntelligenceAllocation(GET_PLAYER(eTarget).getTeam(), INTEL_POLITICS) * 25 * iInfluence / 100 /
        ((__int64)10000 * intelligenceSpeedPercent()));
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
        !hasIntelligenceMode(eTeam, INTEL_POLITICS) || (iStage == 2 && !canFormDynasticUnion(eTarget)))) return 0;
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

int CvPlayer::getIntelligenceDiscoveryChance(PlayerTypes eTarget, int iMode) const
{
    if (!canIntelligenceTarget(eTarget)) return 0;
    const TeamTypes eTeam = GET_PLAYER(eTarget).getTeam();
    if (iMode < 0) iMode = getIntelligenceMode(eTeam);
    if (iMode < INTEL_TECHNOLOGY || iMode > INTEL_ECONOMY ||
        (iMode == INTEL_POLITICS && isDynasticIntelligence())) return 0;
    int iStock = 0;
    switch (iMode)
    {
    case INTEL_TECHNOLOGY: iStock = m_aiTechnologyStock[eTeam]; break;
    case INTEL_MILITARY: iStock = m_aiIntelligenceMilitaryStock[eTeam]; break;
    case INTEL_POLITICS: iStock = m_aiPoliticalStock[eTeam]; break;
    case INTEL_ECONOMY: iStock = m_aiEconomicStock[eTeam]; break;
    }
    // Stock is in hundredths and settles near 20 turns of effective output.
    // Retained networks remain detectable as funding falls, until their stock decays.
    const __int64 iEffort = std::max((__int64)getIntelligenceModeRate(eTarget, iMode) * 100, (__int64)iStock / 20);
    const int iCap = scaledChance(iMode == INTEL_POLITICS ? 6 : (iMode == INTEL_MILITARY ? 3 : 1));
    // Half of the old fixed risk at 50 effective EP, approaching but never exceeding it.
    return (int)(iCap * iEffort / (iEffort + 5000));
}

int CvPlayer::getIntelligenceRelationPenalty(TeamTypes eTarget) const
{
    return (eTarget >= 0 && eTarget < MAX_TEAMS) ? (m_aiIntelligenceExposure[eTarget] + 9999) / 10000 : 0;
}


int CvPlayer::getEconomicInfluence(PlayerTypes eTarget) const
{
    if (!canIntelligenceTarget(eTarget) || getNumCities() == 0 || GET_PLAYER(eTarget).getNumCities() == 0 ||
        !hasIntelligenceMode(GET_PLAYER(eTarget).getTeam(), INTEL_ECONOMY)) return 0;
    const int iStock = m_aiEconomicStock[GET_PLAYER(eTarget).getTeam()];
    const __int64 iHalf = (__int64)2000 * (20 + GET_PLAYER(eTarget).getTotalPopulation());
    return (int)((__int64)10000 * iStock / (iStock + iHalf));
}

int CvPlayer::getEconomicShare(PlayerTypes eTarget) const
{
    const int iInfluence = getEconomicInfluence(eTarget);
    if (iInfluence == 0) return 0;
    int iTotal = 0;
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
        iTotal += GET_PLAYER((PlayerTypes)i).getEconomicInfluence(eTarget);
    // Sum of all attackers' shares never exceeds full influence. XL halves throughput.
    return (int)((__int64)iInfluence * 10000 * 100 /
        ((__int64)std::max(10000, iTotal) * intelligenceSpeedPercent()));
}

int CvPlayer::getEconomicGoldRequest(PlayerTypes eTarget) const
{
    const int iInfluence = getEconomicInfluence(eTarget);
    if (iInfluence == 0) return 0;
    // Hundredths of gold, limited by the funding allocated to this operation.
    const __int64 iBudget = (__int64)(GET_TEAM(getTeam()).isIntelligenceCooperation(GET_PLAYER(eTarget).getTeam()) ?
            getCommerceRate(COMMERCE_ESPIONAGE) : getEffectiveEspionage()) * getIntelligenceAllocation(GET_PLAYER(eTarget).getTeam(), INTEL_ECONOMY) * 50 * iInfluence / 100 /
        ((__int64)10000 * intelligenceSpeedPercent());
    return (int)std::min((__int64)MAX_INT / 2, iBudget);
}

void CvPlayer::recordEconomicGoldTransfer(int iReceived, int iLost)
{
    if (iReceived <= 0 && iLost <= 0) return;
    const int iTurn = GC.getGameINLINE().getGameTurn();
    const int iBucket = iTurn % 2;
    if (m_aiEconomicGoldTurn[iBucket] != iTurn)
    {
        m_aiEconomicGoldTurn[iBucket] = iTurn;
        m_aiEconomicGoldReceived[iBucket] = 0;
        m_aiEconomicGoldLost[iBucket] = 0;
    }
    m_aiEconomicGoldReceived[iBucket] = (int)std::min((__int64)MAX_INT,
        (__int64)m_aiEconomicGoldReceived[iBucket] + iReceived);
    m_aiEconomicGoldLost[iBucket] = (int)std::min((__int64)MAX_INT,
        (__int64)m_aiEconomicGoldLost[iBucket] + iLost);
}

int CvPlayer::getLastEconomicGoldTransfer(bool bReceived) const
{
    // Read-only: opening an advisor must never change synchronized accounting.
    const int iTurn = GC.getGameINLINE().getGameTurn() - 1;
    if (iTurn < 0 || m_aiEconomicGoldTurn[iTurn % 2] != iTurn) return 0;
    return bReceived ? m_aiEconomicGoldReceived[iTurn % 2] : m_aiEconomicGoldLost[iTurn % 2];
}

void CvPlayer::doEconomicSubversion()
{
    // Resolve incoming operations once, on the victim's turn, against one treasury snapshot.
    int aiRequests[NUM_MAJOR_PLAYERS] = {0};
    __int64 iTotal = 0;
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
    {
        aiRequests[i] = GET_PLAYER((PlayerTypes)i).getEconomicGoldRequest(getID());
        iTotal += aiRequests[i];
    }
    // Divide the available treasury among competing requests. Carry fractions of a coin.
    const __int64 iCap = (__int64)std::max(0, getGold()) * 100;
    const __int64 iDivisor = std::max((__int64)1, std::max(iTotal, iCap));
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
    {
        if (aiRequests[i] <= 0 || iCap == 0) continue;
        m_aiEconomicGoldRemainder[i] += (int)((__int64)aiRequests[i] * iCap / iDivisor);
        const int iGold = std::min(getGold(), m_aiEconomicGoldRemainder[i] / 100);
        m_aiEconomicGoldRemainder[i] %= 100;
        changeGold(-iGold);
        GET_PLAYER((PlayerTypes)i).changeGold(iGold);
        recordEconomicGoldTransfer(0, iGold);
        GET_PLAYER((PlayerTypes)i).recordEconomicGoldTransfer(iGold, 0);
    }
    int iArtChance = 0, aiShares[NUM_MAJOR_PLAYERS] = {0};
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
    {
        aiShares[i] = GET_PLAYER((PlayerTypes)i).getEconomicShare(getID());
        iArtChance += aiShares[i];
    }
    // A single shared roll caps art theft at 1% Normal / 0.5% XL for the victim.
    if (iArtChance == 0 || GC.getGameINLINE().getSorenRandNum(10000, "Economic art theft") >= iArtChance / 100) return;
    int iChoice = GC.getGameINLINE().getSorenRandNum(iArtChance, "Economic art recipient");
    PlayerTypes eThief = NO_PLAYER;
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
    {
        iChoice -= aiShares[i];
        if (iChoice < 0) { eThief = (PlayerTypes)i; break; }
    }
    CvCity* pArtCity = NULL;
    int iSeen = 0, iLoop;
    for (CvCity* pCity = firstCity(&iLoop); pCity; pCity = nextCity(&iLoop))
        if (pCity->getCulture(getID()) >= 100 && pCity->getCommerceRate(COMMERCE_CULTURE) > 0 &&
            GC.getGameINLINE().getSorenRandNum(++iSeen, "Economic art city") == 0) pArtCity = pCity;
    if (!pArtCity || eThief == NO_PLAYER) return;
    CvCity* pDestination = GET_PLAYER(eThief).getEconomicDestination(pArtCity);
    if (!pDestination) return;
    const int iCulture = std::min(100, 5 * pArtCity->getCommerceRate(COMMERCE_CULTURE));
    pDestination->changeCultureTimes100(eThief, iCulture * 100, false, true);
    // Brief loss of happiness, without deleting historical culture or changing borders.
    pArtCity->startIntelligenceUnrest(scaledTurns(3));
    gDLL->getInterfaceIFace()->addMessage(eThief, false, GC.getEVENT_MESSAGE_TIME(),
        gDLL->getText("TXT_KEY_INTEL_ECONOMIC_ART_GAIN", pArtCity->getNameKey(), pDestination->getNameKey(), iCulture), NULL, MESSAGE_TYPE_MINOR_EVENT);
    gDLL->getInterfaceIFace()->addMessage(getID(), false, GC.getEVENT_MESSAGE_TIME(),
        gDLL->getText("TXT_KEY_INTEL_ECONOMIC_ART_LOSS", pArtCity->getNameKey()), NULL, MESSAGE_TYPE_MINOR_EVENT);
}

CvCity* CvPlayer::getEconomicDestination(const CvCity* pOrigin) const
{
    CvCity* pBest = NULL;
    int iBest = MAX_INT, iLoop;
    for (CvCity* pCity = firstCity(&iLoop); pCity; pCity = nextCity(&iLoop))
    {
        if (pCity->isDisorder()) continue;
        const int iDistance = plotDistance(pCity->getX_INLINE(), pCity->getY_INLINE(), pOrigin->getX_INLINE(), pOrigin->getY_INLINE());
        if (iDistance < iBest) { pBest = pCity; iBest = iDistance; }
    }
    return pBest;
}

int CvCity::divertEconomicFood(int iSurplus)
{
    if (iSurplus <= 0 || isDisorder() || isFoodProduction()) return iSurplus;
    int aiShares[NUM_MAJOR_PLAYERS] = {0}, iTotal = 0;
    for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
    {
        CvPlayer& kThief = GET_PLAYER((PlayerTypes)i);
        if (kThief.getEconomicInfluence(getOwnerINLINE()) > 0 && kThief.getEconomicDestination(this))
            aiShares[i] = kThief.getEconomicShare(getOwnerINLINE());
        iTotal += aiShares[i];
    }
    if (iTotal == 0) return iSurplus;
    // Fractions accrue per city. Only newly generated growth food can be taken.
    const __int64 iFood = (__int64)iSurplus * iTotal + m_iEconomicFoodRemainder;
    const int iDiverted = std::min(iSurplus, (int)(iFood / 200000));
    m_iEconomicFoodRemainder = (int)(iFood % 200000);
    // Assign each actual shipment proportionally, using synchronized game RNG.
    for (int j = 0; j < iDiverted; ++j)
    {
        int iChoice = GC.getGameINLINE().getSorenRandNum(iTotal, "Economic food recipient");
        for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
        {
            iChoice -= aiShares[i];
            if (iChoice >= 0) continue;
            CvCity* pDestination = GET_PLAYER((PlayerTypes)i).getEconomicDestination(this);
            if (pDestination) pDestination->changeFood(1);
            break;
        }
    }
    return iSurplus - iDiverted;
}

int CvPlayer::getIntelligenceBuildup(PlayerTypes eTarget, int iMode) const
{
    // Read-only strength of the stored network, independent of the selected operation.
    // These are percentages of each mode's full effect, not research-project progress.
    if (iMode == INTEL_NONE) return -1; // No network to build.
    if (!canIntelligenceTarget(eTarget)) return 0;
    const TeamTypes eTeam = GET_PLAYER(eTarget).getTeam();
    if (iMode == INTEL_TECHNOLOGY) return getIntelligenceTechInfluence(eTarget);
    __int64 iStock = 0, iHalf = 1;
    switch (iMode)
    {
    case INTEL_MILITARY:
        iStock = m_aiIntelligenceMilitaryStock[eTeam];
        iHalf = (__int64)2000 * (40 + GET_PLAYER(eTarget).getNumMilitaryUnits());
        break;
    case INTEL_POLITICS:
        if (isDynasticIntelligence())
        {
            iStock = m_aiDynasticStock[eTeam];
            iHalf = 10000;
        }
        else
        {
            iStock = m_aiPoliticalStock[eTeam];
            iHalf = (__int64)2000 * (20 + GET_PLAYER(eTarget).getTotalPopulation());
        }
        break;
    case INTEL_ECONOMY:
        iStock = m_aiEconomicStock[eTeam];
        iHalf = (__int64)2000 * (20 + GET_PLAYER(eTarget).getTotalPopulation());
        break;
    case INTEL_COOPERATION:
        iStock = m_aiCooperationStock[eTeam];
        iHalf = 40000; // Trust modifies cooperation separately from buildup.
        break;
    default: return 0;
    }
    return (int)(10000 * iStock / (iStock + iHalf));
}

int CvPlayer::getIntelligenceData(int iTarget, int iField) const
{
    if (iField == 300) return getIntelligenceForceCount();
    if (iField == 301) return getIntelligenceActiveForces();
    if (iField == 302) return scaledTurns(5);
    if (iField == 303)
    {
        for (int i = 0; i < NUM_MAJOR_PLAYERS; ++i)
            if (canIntelligenceTarget((PlayerTypes)i) && GET_TEAM(getTeam()).isIntelligenceCooperation(GET_PLAYER((PlayerTypes)i).getTeam())) return 1;
        return 0;
    }
    if (iField >= 310 && iField < 340)
    {
        if (iTarget < 0 || iTarget >= getIntelligenceForceCount()) return -1;
        const int f = iTarget;
        if (iField == 310) return m_aiForceMode[f];
        if (iField == 311) return m_aiForcePending[f];
        if (iField == 312) return std::max(0, m_aiForceNextTurn[f] - GC.getGameINLINE().getGameTurn());
        if (iField == 313)
        {
            if (m_aiForceMode[f] == INTEL_NONE) return 0;
            bool bActive = false;
            for (int j = 0; j < 3; ++j)
                if (m_aiForceTargets[f][j] >= 0 && canIntelligenceTarget((PlayerTypes)m_aiForceTargets[f][j]) &&
                    (m_aiForceMode[f] != INTEL_COOPERATION || GET_TEAM(getTeam()).isIntelligenceCooperation(GET_PLAYER((PlayerTypes)m_aiForceTargets[f][j]).getTeam()))) bActive = true;
            return bActive ? 10000 / std::max(1, getIntelligenceActiveForces()) + 1000 : 0;
        }
        if (iField == 314)
        {
            int iCount = 0;
            for (int j = 0; j < 3; ++j) if (m_aiForceTargets[f][j] >= 0) ++iCount;
            const int aiShare[] = {0, 100, 70, 57};
            return aiShare[iCount];
        }
        if (iField >= 320 && iField < 323)
        {
            const int iPlayer = m_aiForceTargets[f][iField-320];
            return iPlayer >= 0 && canIntelligenceTarget((PlayerTypes)iPlayer) &&
                (m_aiForceMode[f] != INTEL_COOPERATION || GET_TEAM(getTeam()).isIntelligenceCooperation(GET_PLAYER((PlayerTypes)iPlayer).getTeam())) ? iPlayer : -1;
        }
        if (iField >= 330 && iField < 330 + NUM_INTELLIGENCE_MODES)
        {
            if (iField == 330 + INTEL_NONE) return -1;
            const __int64 iStock = m_aiForceStock[f][iField-330];
            const __int64 iSteady = (__int64)2000 * getCommerceRate(COMMERCE_ESPIONAGE) *
                (10000 / std::max(1, getIntelligenceActiveForces()) + 1000) / 10000;
            return (int)std::min((__int64)10000, iStock * 10000 / std::max((__int64)1, iSteady));
        }
        return 0;
    }
    // Read-only advisor API. Foreign secrets are returned only when actually acquired.
    if (iField == 66) return getLastEconomicGoldTransfer(true);
    if (iField == 67) return getLastEconomicGoldTransfer(false);
    if (iField == 59) return getEffectiveEspionage();
    if (iField == 60) return getCooperationBonus();
    if (iField == 61) return getCooperationStability();
    if (iField == 20) return getIntelligenceStabilityPenalty();
    if (iField == 21) return m_eIntelligenceResearch;
    if (iField == 22) return getIntelligenceResearchRate(m_eIntelligenceResearch);
    if (iField == 23) return m_iIntelligenceLastResearch;
    if (iField == 25) return getIntelligenceAnarchyExtra();
    if (iField == 26) return scaledAnarchyTurns(2);
    if (iField == 32) return isDynasticIntelligence() ? 1 : 0;
    if (iField == 41) return m_iDynasticWarTurns;
    if (iField == 42) return isBeingDynasticallyIncorporated() ? 1 : 0;
    if (iField == 45) return scaledTurns(20);
    if (iTarget < 0 || iTarget >= NUM_MAJOR_PLAYERS) return 0;
    PlayerTypes eTarget = (PlayerTypes)iTarget;
    TeamTypes eTeam = GET_PLAYER(eTarget).getTeam();
    if (iField >= 200 && iField < 200 + NUM_INTELLIGENCE_MODES)
        return getIntelligenceDiscoveryChance(eTarget, iField - 200);
    if (iField >= 100 && iField < 100 + NUM_INTELLIGENCE_MODES)
        return getIntelligenceBuildup(eTarget, iField - 100);
    switch (iField)
    {
    case 62: return GET_TEAM(getTeam()).isIntelligenceCooperation(eTeam) ? 1 : 0;
    case 63: return getCooperationInfluence(eTarget);
    case 64: return getCooperationContribution(eTarget);
    case 65: return m_aiCooperationStock[eTeam] / 100;
    case 0: return getIntelligenceMode(eTeam);
    case 1: return getIntelligenceMode(eTeam);
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
    case 57: return m_aiTechnologyStock[eTeam] / 100;
    case 58: return getIntelligenceTechInfluence(eTarget);
    case 52: return m_aiEconomicStock[eTeam] / 100;
    case 53: return getEconomicInfluence(eTarget);
    case 54: return getEconomicGoldRequest(eTarget);
    case 55: return getEconomicShare(eTarget) / 20;
    case 56: return getEconomicShare(eTarget) / 100;
    case 27: return getIntelligenceDiscoveryChance(eTarget);
    case 14:
        return m_eIntelligenceResearch != NO_TECH && !GET_TEAM(getTeam()).isHasTech(m_eIntelligenceResearch) &&
            canResearch(m_eIntelligenceResearch) && canIntelligenceTarget(eTarget) && hasIntelligenceMode(eTeam, INTEL_TECHNOLOGY) &&
            GET_TEAM(eTeam).isHasTech(m_eIntelligenceResearch) ?
            getIntelligenceTechRate(eTarget) : 0;
    case 13:
    {
        int iAttack = (GET_TEAM(getTeam()).isIntelligenceCooperation(eTeam) ? getCommerceRate(COMMERCE_ESPIONAGE) :
            getEffectiveEspionage()) * getIntelligenceAccess(eTarget) / 100;
        return iAttack > 0 ? 100 - getIntelligenceRate(eTarget) * 100 / iAttack : 0;
    }
    case 12: return !isDynasticIntelligence() && canIntelligenceTarget(eTarget) && hasIntelligenceMode(eTeam, INTEL_POLITICS) ?
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
    for (int t = 0; t < MAX_TEAMS; ++t)
    {
        m_aiIntelligenceStrength[t] = 0;
        if (m_aiIntelligenceExposure[t] > 0) m_aiIntelligenceExposure[t] = std::max(0, m_aiIntelligenceExposure[t] - std::max(1, 20000 / intelligenceSpeedPercent()));
    }
    if (GC.getGameINLINE().isOption(GAMEOPTION_NO_ESPIONAGE)) { refreshIntelligenceTracking(); return; }
    updateIntelligenceForces();
    rebuildIntelligenceStocks();
    doIntelligenceCooperation();
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
        for (int iMode = INTEL_TECHNOLOGY; iMode <= INTEL_ECONOMY; ++iMode)
        {
            const int iDiscoveryChance = bFirst && hasIntelligenceMode(eTeam, iMode) ? getIntelligenceDiscoveryChance(eTarget, iMode) : 0;
            if (iDiscoveryChance > 0)
            {
                int iSeverity = iMode == INTEL_POLITICS ? 3 : (iMode == INTEL_MILITARY ? 2 : 1);
                if (GC.getGameINLINE().getSorenRandNum(10000, "Intelligence discovery") < iDiscoveryChance)
                {
                    m_aiIntelligenceExposure[eTeam] = std::max(m_aiIntelligenceExposure[eTeam],
                        std::min(iMode == INTEL_POLITICS ? 60000 : (iMode == INTEL_MILITARY ? 30000 : 10000), m_aiIntelligenceExposure[eTeam] + 10000 * iSeverity));
                    gDLL->getInterfaceIFace()->addMessage(getID(), false, GC.getEVENT_MESSAGE_TIME(),
                        gDLL->getText("TXT_KEY_INTEL_DISCOVERED", kTarget.getCivilizationShortDescriptionKey()), NULL, MESSAGE_TYPE_MINOR_EVENT);
                    for (int j = 0; j < NUM_MAJOR_PLAYERS; ++j)
                        if (GET_PLAYER((PlayerTypes)j).isAlive() && GET_PLAYER((PlayerTypes)j).getTeam() == eTeam)
                            gDLL->getInterfaceIFace()->addMessage((PlayerTypes)j, false, GC.getEVENT_MESSAGE_TIME(),
                                gDLL->getText("TXT_KEY_INTEL_DETECTED", getCivilizationShortDescriptionKey()), NULL, MESSAGE_TYPE_MINOR_EVENT);
                }
            }
        }
        // A decaying network can still infiltrate after funding is reduced to zero.
        if (hasIntelligenceMode(eTeam, INTEL_MILITARY) && GET_TEAM(getTeam()).isAtWar(eTeam))
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
        int iCityLoop;
        for (CvCity* pCity = kTarget.firstCity(&iCityLoop); pCity; pCity = kTarget.nextCity(&iCityLoop)) pCity->updateEspionageVisibility(true);
    }
    refreshIntelligenceTracking();
    doPoliticalIntelligence();
    doEconomicSubversion();
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
    gDLL->getInterfaceIFace()->setDirty(GameData_DIRTY_BIT, true);
}

int CvPlayer::getIntelligenceChecksum() const
{
    int iValue = (m_eIntelligenceResearch + 1) * 101 + m_iIntelligencePressure * 103 +
        m_iIntelligenceUnrestCooldown * 107 + m_iIntelligenceLastResearch * 109 +
        m_iIntelligenceStability * 157 + m_iCooperationStability * 223 + m_iDynasticWarTurns * 163 + (m_iDynasticCityTurn + 1) * 167;
    for (int i = 0; i < MAX_TEAMS; ++i)
        iValue += (i + 1) * (GET_TEAM(getTeam()).isIntelligenceCooperation((TeamTypes)i) * 229 + m_aiIntelligenceMode[i] * 113 + m_aiEspionageSpendingWeightAgainstTeam[i] * 127 +
            m_aiIntelligenceStrength[i] * 131 + m_aiIntelligenceExposure[i] * 137 +
            m_aiIntelligenceMilitaryStock[i] * 151 +
            m_aiTechnologyStock[i] * 211 + m_aiCooperationStock[i] * 227 + m_aiPoliticalStock[i] * 193 +
            m_aiDynasticStock[i] * 173 + m_aiDynasticStage[i] * 179 +
            (m_aiDynasticLastRoll[i] + 1) * 181 + m_abDynasticUnion[i] * 191 +
            m_aiEconomicStock[i] * 197);
    for (int j = 0; j < MAX_PLAYERS; ++j)
        iValue += (j + 1) * m_aiEconomicGoldRemainder[j] * 199;
    for (int iBucket = 0; iBucket < 2; ++iBucket)
        iValue += (iBucket + 1) * ((m_aiEconomicGoldTurn[iBucket] + 1) * 233 +
            m_aiEconomicGoldReceived[iBucket] * 239 + m_aiEconomicGoldLost[iBucket] * 241);
    for (int f = 0; f < MAX_TEAMS; ++f)
    {
        iValue += (f + 1) * (m_aiForceMode[f] * 251 + m_aiForcePending[f] * 257 + m_aiForceNextTurn[f] * 263);
        for (int j = 0; j < 3; ++j) iValue += (f + 1) * (j + 1) * (m_aiForceTargets[f][j] + 1) * 269;
        for (int m = 0; m < NUM_INTELLIGENCE_MODES; ++m) iValue += (f + 1) * (m + 1) * m_aiForceStock[f][m] * 271;
    }
    int iLoop;
    for (CvUnit* pUnit = firstUnit(&iLoop); pUnit; pUnit = nextUnit(&iLoop))
        iValue += (pUnit->getID() + 1) * pUnit->getIntelligenceTrackingChecksum();
    return iValue;
}
