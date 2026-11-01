#include "CvGameCoreDLL.h"
#include "CvUnitMastery.h"
#include "CvPlayer.h"
#include "CvTeam.h"
#include "CvUnit.h"
#include "CvPlot.h"
#include "CvInfos.h"
#include "CvDLLInterfaceIFaceBase.h"

namespace UnitMastery
{
    struct Reward
    {
        const char* unit;
        int level;
        Effect effect;
        int value;
    };
    static const Reward rewards[] = {
#include "UnitMasteryData.inc"
    };

    struct Track
    {
        TechTypes tech;
        int bonus[4][NUM_MASTERY_EFFECTS];
        Track() : tech(NO_TECH) { memset(bonus, 0, sizeof(bonus)); }
    };

    // Resolve XML names once; hot combat getters use direct array lookups.
    struct Registry
    {
        std::vector<Track> units;
        std::vector<UnitTypes> techs;
        Registry() : units(GC.getNumUnitInfos()), techs(GC.getNumTechInfos(), NO_UNIT)
        {
            for (int i = 0; i < sizeof(rewards) / sizeof(rewards[0]); ++i)
            {
                const Reward& r = rewards[i];
                const UnitTypes eUnit = (UnitTypes)GC.getInfoTypeForString(r.unit);
                CvString name("TECH_UNIT_MASTERY_");
                name += r.unit + 5;
                const TechTypes eTech = (TechTypes)GC.getInfoTypeForString(name);
                FAssert(eUnit != NO_UNIT && eTech != NO_TECH);
                if (eUnit == NO_UNIT || eTech == NO_TECH) continue;
                units[eUnit].tech = eTech;
                techs[eTech] = eUnit;
                for (int l = r.level; l <= 3; ++l)
                    units[eUnit].bonus[l][r.effect] += r.value;
            }
        }
    };

    static const Registry& registry()
    {
        static Registry data;
        return data;
    }

    TechTypes techForUnit(UnitTypes eUnit)
    {
        return eUnit == NO_UNIT ? NO_TECH : registry().units[eUnit].tech;
    }

    UnitTypes unitForTech(TechTypes eTech)
    {
        return eTech == NO_TECH ? NO_UNIT : registry().techs[eTech];
    }

    int level(UnitTypes eUnit, TeamTypes eTeam)
    {
        TechTypes eTech = techForUnit(eUnit);
        return eTech == NO_TECH || eTeam == NO_TEAM ? 0 : std::min(3, GET_TEAM(eTeam).getTechCount(eTech));
    }

    int modifier(UnitTypes eUnit, TeamTypes eTeam, Effect eEffect)
    {
        return eUnit == NO_UNIT ? 0 : registry().units[eUnit].bonus[level(eUnit, eTeam)][eEffect];
    }

    static bool technologyUnlocked(const CvTeam& kTeam, UnitTypes eUnit)
    {
        const CvUnitInfo& info = GC.getUnitInfo(eUnit);
        if (info.getProductionCost() < 0) return false;
        TechTypes eTech = (TechTypes)info.getPrereqAndTech();
        if (eTech != NO_TECH && (GC.getTechInfo(eTech).isDisable() || !kTeam.isHasTech(eTech))) return false;
        for (int i = 0; i < GC.getNUM_UNIT_AND_TECH_PREREQS(); ++i)
        {
            eTech = (TechTypes)info.getPrereqAndTechs(i);
            if (eTech != NO_TECH && (GC.getTechInfo(eTech).isDisable() || !kTeam.isHasTech(eTech))) return false;
        }
        return true;
    }

    bool isAvailable(const CvPlayer& kPlayer, TechTypes eTech)
    {
        const UnitTypes eUnit = unitForTech(eTech);
        if (eUnit == NO_UNIT) return true;
        if (kPlayer.getCivilizationType() == NO_CIVILIZATION) return false;
        if (level(eUnit, kPlayer.getTeam()) >= 3) return false;
        const CvUnitInfo& info = GC.getUnitInfo(eUnit);
        const CvCivilizationInfo& civ = GC.getCivilizationInfo(kPlayer.getCivilizationType());
        if (civ.getCivilizationUnits(info.getUnitClassType()) != eUnit) return false;
        // Retirement is permanent with technology, not dependent on iron, horses,
        // buildings, coastal cities or temporary production restrictions.
        for (int i = 0; i < GC.getNumUnitClassInfos(); ++i)
        {
            if (!info.getUpgradeUnitClass(i)) continue;
            const UnitTypes eUpgrade = (UnitTypes)civ.getCivilizationUnits(i);
            if (eUpgrade != NO_UNIT && technologyUnlocked(GET_TEAM(kPlayer.getTeam()), eUpgrade))
                return false;
        }
        return true;
    }

    void recordCombat(const CvUnit& kUnit)
    {
        const int percent = GC.getDefineINT("UNIT_MASTERY_COMBAT_RESEARCH_PERCENT");
        const TechTypes eTech = techForUnit(kUnit.getUnitType());
        CvPlayer& player = GET_PLAYER(kUnit.getOwnerINLINE());
        if (percent <= 0 || eTech == NO_TECH || !player.canResearch(eTech)) return;

        CvTeam& team = GET_TEAM(kUnit.getTeam());
        // Award once per battle, including defeat/withdrawal. Cap at this level
        // so combat never creates overflow for unrelated research.
        const int progress = (int)std::min((__int64)team.getResearchLeft(eTech),
            std::max((__int64)1, (__int64)team.getResearchCost(eTech) * percent / 100));
        if (progress > 0) team.changeResearchProgress(eTech, progress, player.getID());
    }

    CvWString suffix(UnitTypes eUnit, TeamTypes eTeam)
    {
        const int l = level(eUnit, eTeam);
        if (l > 0)
        {
            static const wchar* roman[] = {L"", L"I", L"II", L"III"};
            return CvWString::format(L" (%s)", roman[l]);
        }
        return CvWString();
    }

    CvWString tooltipName(const CvUnit& kUnit)
    {
        return kUnit.getName() + suffix(kUnit.getUnitType(), kUnit.getTeam());
    }

    CvWString researchName(TechTypes eTech, TeamTypes eTeam)
    {
        CvWString name = GC.getTechInfo(eTech).getDescription();
        const UnitTypes eUnit = unitForTech(eTech);
        if (eUnit != NO_UNIT)
        {
            static const wchar* roman[] = {L"I", L"II", L"III"};
            const int next = std::min(2, level(eUnit, eTeam));
            name += CvWString::format(L" %s", roman[next]);
        }
        return name;
    }

    void updateSight(CvTeam& kTeam, TechTypes eTech, bool bIncrement)
    {
        const UnitTypes eUnit = unitForTech(eTech);
        if (eUnit == NO_UNIT) return;
        for (int p = 0; p < MAX_PLAYERS; ++p)
        {
            CvPlayer& player = GET_PLAYER((PlayerTypes)p);
            if (player.getTeam() != kTeam.getID()) continue;
            int iLoop;
            for (CvUnit* unit = player.firstUnit(&iLoop); unit != NULL; unit = player.nextUnit(&iLoop))
                if (unit->getUnitType() == eUnit && unit->plot() != NULL)
                {
                    unit->plot()->changeAdjacentSight(kTeam.getID(), unit->visibilityRange(), bIncrement, unit, true);
                    unit->setInfoBarDirty(true);
                }
        }
    }

    void refreshResearch(CvTeam& kTeam, PlayerTypes eAcquirer)
    {
        if (eAcquirer == NO_PLAYER || GET_PLAYER(eAcquirer).getTeam() != kTeam.getID())
            eAcquirer = kTeam.getLeaderID();
        for (int t = 0; t < GC.getNumTechInfos(); ++t)
        {
            const TechTypes eTech = (TechTypes)t;
            if (unitForTech(eTech) == NO_UNIT) continue;
            bool bAnyAvailable = false;
            for (int p = 0; p < MAX_PLAYERS; ++p)
            {
                CvPlayer& player = GET_PLAYER((PlayerTypes)p);
                if (player.getTeam() != kTeam.getID()) continue;
                if (isAvailable(player, eTech)) bAnyAvailable = true;
                else player.popResearch(eTech);
            }
            // Team progress is refunded only once, never once per teammate.
            if (!bAnyAvailable && kTeam.getResearchProgress(eTech) > 0 && eAcquirer != NO_PLAYER)
            {
                CvPlayer& player = GET_PLAYER(eAcquirer);
                const int progress = kTeam.getResearchProgress(eTech);
                const int refund = (int)std::min((__int64)MAX_INT,
                    (__int64)progress * 100 / std::max(1, player.calculateResearchModifier(eTech)));
                player.changeOverflowResearch(refund);
                kTeam.setResearchProgress(eTech, 0, eAcquirer);
            }
        }
        gDLL->getInterfaceIFace()->setDirty(ResearchButtons_DIRTY_BIT, true);
        gDLL->getInterfaceIFace()->setDirty(SelectionButtons_DIRTY_BIT, true);
        gDLL->getInterfaceIFace()->setDirty(InfoPane_DIRTY_BIT, true);
    }
}
