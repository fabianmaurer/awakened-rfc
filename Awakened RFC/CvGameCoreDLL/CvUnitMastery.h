#ifndef CV_UNIT_MASTERY_H
#define CV_UNIT_MASTERY_H

class CvPlayer;
class CvTeam;
class CvUnit;

// Team research, never per-unit promotions or mutable unit state.
namespace UnitMastery
{
    enum Effect
    {
        MASTERY_COMBAT, MASTERY_MOVES, MASTERY_FIRST_STRIKES,
        MASTERY_WITHDRAWAL, MASTERY_COLLATERAL, MASTERY_COLLATERAL_LIMIT,
        MASTERY_COLLATERAL_TARGETS, MASTERY_CITY_ATTACK, MASTERY_CITY_DEFENSE,
        MASTERY_HILLS_ATTACK, MASTERY_HILLS_DEFENSE, MASTERY_FOREST_ATTACK,
        MASTERY_FOREST_DEFENSE, MASTERY_JUNGLE_ATTACK, MASTERY_JUNGLE_DEFENSE,
        MASTERY_MELEE, MASTERY_MOUNTED, MASTERY_ARCHER, MASTERY_GUN,
        MASTERY_ARMOR, MASTERY_SIEGE, MASTERY_NAVAL, MASTERY_ANIMAL,
        MASTERY_HEAL, MASTERY_SAME_TILE_HEAL, MASTERY_BLITZ, MASTERY_AMPHIB,
        MASTERY_RIVER, MASTERY_ENEMY_ROUTE, MASTERY_ALWAYS_HEAL,
        MASTERY_HILLS_DOUBLE, MASTERY_FOREST_DOUBLE, MASTERY_JUNGLE_DOUBLE,
        MASTERY_FIRST_IMMUNE, MASTERY_IGNORE_TERRAIN, MASTERY_IGNORE_BUILDING,
        MASTERY_BOMBARD, MASTERY_VISIBILITY, NUM_MASTERY_EFFECTS
    };

    TechTypes techForUnit(UnitTypes eUnit);
    UnitTypes unitForTech(TechTypes eTech);
    int level(UnitTypes eUnit, TeamTypes eTeam);
    int modifier(UnitTypes eUnit, TeamTypes eTeam, Effect eEffect);
    bool isAvailable(const CvPlayer& kPlayer, TechTypes eTech);
    CvWString suffix(UnitTypes eUnit, TeamTypes eTeam);
    CvWString tooltipName(const CvUnit& kUnit);
    CvWString researchName(TechTypes eTech, TeamTypes eTeam);
    void updateSight(CvTeam& kTeam, TechTypes eTech, bool bIncrement);
    void refreshResearch(CvTeam& kTeam, PlayerTypes eAcquirer);
}

#endif
