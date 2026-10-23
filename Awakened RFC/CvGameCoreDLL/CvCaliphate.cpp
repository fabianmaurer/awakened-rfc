#include "CvGameCoreDLL.h"
#include "CvPlayerAI.h"
#include "CvRhyes.h"
#include "CvTeamAI.h"
#include "CvGameAI.h"
#include "CvMap.h"
#include "CvPlot.h"
#include "CvCity.h"
#include "CvUnit.h"
#include "CvInitCore.h"
#include "CyArgsList.h"
#include "CvDLLPythonIFaceBase.h"
#include "CvDLLInterfaceIFaceBase.h"

namespace
{
const char* realmCivs[] = { "CIVILIZATION_ABBASID", "CIVILIZATION_FATIMID", "CIVILIZATION_UMAYYAD" };
const char* realmLeaders[] = { "LEADER_ABBASID", "LEADER_FATIMID", "LEADER_UMAYYAD" };
const int capitalX[] = { 78, 69, 51 };
const int capitalY[] = { 40, 35, 44 };

#if ARFC_ENABLE_REPORTING
// Keep native partition progress when a crash prevents a Python traceback.
// Numeric player/plot IDs also avoid encoding localized city names in the log.
void logPartitionStage(const char* stage, PlayerTypes player, int subject = -1)
{
    gDLL->logMsg("Caliphate.log", CvString::format("turn=%d player=%d stage=%s subject=%d",
        GC.getGameINLINE().getGameTurn(), (int)player, stage, subject).c_str(), false, true);
}

#endif
#if !ARFC_ENABLE_REPORTING
inline void logPartitionStage(const char*, PlayerTypes, int = -1) {}
#endif

// Realm, west, south, east, north. Keep these anchors in sync with Caliphate.py.
const int realmRegions[][5] = {
    { 0, 76, 37, 85, 46 }, // Iraq/Persia
    { 0, 73, 29, 80, 37 }, // Arabian Peninsula
    { 1, 61, 24, 72, 40 }, // Egypt/eastern North Africa
    { 1, 71, 38, 75, 45 }, // Levant
    { 2, 44, 30, 60, 49 }  // Western North Africa/Iberia
};

int realmAt(int x, int y)
{
    int bestRealm = -1, bestDistance = MAX_INT;
    for (int i = 0; i < sizeof(realmRegions) / sizeof(realmRegions[0]); ++i)
    {
        const int* region = realmRegions[i];
        const int nearestX = std::max(region[1], std::min(x, region[3]));
        const int nearestY = std::max(region[2], std::min(y, region[4]));
        // Test both longitude edges as well as the clamped point so that
        // Civ4's wrapped distance also finds the nearest edge across the seam.
        int distance = plotDistance(x, y, nearestX, nearestY);
        distance = std::min(distance, plotDistance(x, y, region[1], nearestY));
        distance = std::min(distance, plotDistance(x, y, region[3], nearestY));
        if (distance < bestDistance)
        {
            bestDistance = distance;
            bestRealm = region[0];
        }
    }
    return bestRealm;
}

int realmOf(CivilizationTypes eCiv)
{
    for (int r = 0; r < 3; ++r)
        if (eCiv == GC.getInfoTypeForString(realmCivs[r])) return r;
    return -1;
}

struct PartitionCity
{
    int plot;
    int realm;
    int population;
    bool coastal;
};

CvPlot* nearestRealmCity(const std::vector<PartitionCity>& cities, int realm, CvPlot* origin, bool sea)
{
    CvPlot* best = NULL;
    int distance = MAX_INT;
    for (uint i = 0; i < cities.size(); ++i)
    {
        if (cities[i].realm != realm || (sea && !cities[i].coastal)) continue;
        CvPlot* candidate = GC.getMapINLINE().plotByIndexINLINE(cities[i].plot);
        int value = plotDistance(origin->getX_INLINE(), origin->getY_INLINE(), candidate->getX_INLINE(), candidate->getY_INLINE());
        if (value < distance) { distance = value; best = candidate; }
    }
    return best;
}

void transferUnit(CvUnit* unit, PlayerTypes owner, CvPlot* destination)
{
    // Cargo belongs to the same realm as its transport. Convert cargo first,
    // matching the game's existing gift path; preserve transport attachment.
    std::vector<CvUnit*> cargo;
    unit->getCargoUnits(cargo);
    for (uint i = 0; i < cargo.size(); ++i) transferUnit(cargo[i], owner, destination);
    if (unit->getOwnerINLINE() != owner)
    {
        CvUnit* replacement = GET_PLAYER(owner).initUnit(unit->getUnitType(), unit->getX_INLINE(), unit->getY_INLINE(), unit->AI_getUnitAIType());
        FAssert(replacement != NULL);
        if (replacement == NULL) return;
        replacement->convert(unit);
        unit->doDelayedDeath();
        unit = replacement;
    }
    if (!unit->isCargo()) unit->setXY(destination->getX_INLINE(), destination->getY_INLINE(), false, true, false);
    unit->finishMoves();
}
}

int CvPlayer::getCaliphateRealmMask() const
{
    int mask = 0, loop;
    for (CvCity* city = firstCity(&loop); city != NULL; city = nextCity(&loop))
        mask |= 1 << realmAt(city->getX_INLINE(), city->getY_INLINE());
    return mask;
}

void CvPlayer::configureCaliphateSuccessor()
{
    if (getID() >= NUM_MAJOR_PLAYERS) return;
    // Retain the original Arabia map when loading another game in this process.
    static bool copied = false;
    static int originalArabia[EARTH_Y][EARTH_X];
    if (!copied)
    {
        memcpy(originalArabia, settlersMaps[ARABIA], sizeof(originalArabia));
        copied = true;
    }
    const int realm = realmOf(getCivilizationType());
    if (realm < 0)
    {
        if (getID() == ARABIA) memcpy(settlersMaps[ARABIA], originalArabia, sizeof(originalArabia));
        return;
    }
    // The authored 900 AD Umayyad state is still the emirate (caliphate: 929).
    // Apply on initialization and reload, alongside the successor's regional AI.
    const bool bCordoba = realm == 2 && getID() == CALIPHATE_SLOT_1 &&
        GC.getGameINLINE().getStartTurn() == 211;
    setCivDescription(bCordoba ? L"TXT_KEY_RFCMP_900_CORDOBA_DESC" :
        GC.getCivilizationInfo(getCivilizationType()).getTextKeyWide());
    GC.getInitCore().setCivShortDesc(getID(), bCordoba ? L"TXT_KEY_RFCMP_900_CORDOBA_SHORT" :
        GC.getCivilizationInfo(getCivilizationType()).getShortDescriptionKey());
    GC.getInitCore().setCivAdjective(getID(), GC.getCivilizationInfo(getCivilizationType()).getAdjectiveKey());
    for (int y = 0; y < EARTH_Y; ++y)
        for (int x = 0; x < EARTH_X; ++x)
        {
            bool bHomeland = realmAt(x, y) == realm;
            if (GC.getGameINLINE().getStartTurn() == 211)
            {
                if (realm == 0) bHomeland = x >= 74 && x <= 83 && y >= 31 && y <= 46 &&
                    !(x <= 74 && y >= 38); // Tulunid southern Syria is autonomous.
                if (realm == 1) bHomeland = x >= 56 && x <= 74 && y >= 33 && y <= 42;
                if (realm == 2) bHomeland = x >= 49 && x <= 56 && y >= 40 && y <= 46;
            }
            settlersMaps[getID()][EARTH_Y - 1 - y][x] = bHomeland ? 300 : 20;
        }
}

void CvPlayer::resolveCaliphatePartition(int decision, int chosen)
{
    if (decision < 0 || decision != m_iCaliphatePartitionDecision || m_bCaliphatePartitioned || !isAlive() ||
        getCivilizationType() != GC.getInfoTypeForString("CIVILIZATION_ARABIA")) return;
    if (GET_PLAYER((PlayerTypes)CALIPHATE_SLOT_1).isEverAlive() || GET_PLAYER((PlayerTypes)CALIPHATE_SLOT_2).isEverAlive()) return;

    std::vector<PartitionCity> cities;
    int weights[3] = { 0, 0, 0 };
    bool coastal[3] = { false, false, false };
    int loop, total = 0;
    for (CvCity* city = firstCity(&loop); city != NULL; city = nextCity(&loop))
    {
        PartitionCity entry;
        entry.plot = GC.getMapINLINE().plotNum(city->getX_INLINE(), city->getY_INLINE());
        entry.realm = realmAt(city->getX_INLINE(), city->getY_INLINE());
        entry.population = city->getPopulation();
        entry.coastal = city->isCoastal(GC.getMIN_WATER_SIZE_FOR_OCEAN());
        cities.push_back(entry);
        weights[entry.realm] += entry.population;
        coastal[entry.realm] = coastal[entry.realm] || entry.coastal;
        total += entry.population;
    }
    if (total == 0) return;
    if (chosen == -1 && (!isHuman() || GC.getGameINLINE().isObserverAutoPlay()))
    {
        chosen = 0;
        if (!weights[0]) chosen = weights[1] >= weights[2] ? 1 : 2;
    }
    if (chosen < 0 || chosen > 2 || !weights[chosen]) return;
    logPartitionStage("begin", getID(), chosen);

    // Each successor's city limit rewards expansion into multiple regions.
    // Release the most distant cities of realms exceeding their own limit.
    int cityCounts[3] = { 0, 0, 0 };
    int realmCount = 0;
    for (uint i = 0; i < cities.size(); ++i) ++cityCounts[cities[i].realm];
    for (int r = 0; r < 3; ++r) if (cityCounts[r]) ++realmCount;
    const int cityLimit = 2 + 2 * realmCount; // 4, 6 or 8 per successor.
    std::vector<PartitionCity> independentCities;
    while (cityCounts[0] > cityLimit || cityCounts[1] > cityLimit || cityCounts[2] > cityLimit)
    {
        int farthest = -1, distance = -1;
        for (uint i = 0; i < cities.size(); ++i)
        {
            const int realm = cities[i].realm;
            if (cityCounts[realm] <= cityLimit) continue;
            CvPlot* plot = GC.getMapINLINE().plotByIndexINLINE(cities[i].plot);
            int d = plotDistance(plot->getX_INLINE(), plot->getY_INLINE(), capitalX[realm], capitalY[realm]);
            if (d > distance || (d == distance && cities[i].plot > cities[farthest].plot))
            { farthest = i; distance = d; }
        }
        --cityCounts[cities[farthest].realm];
        independentCities.push_back(cities[farthest]);
        cities.erase(cities.begin() + farthest);
    }
    // Treasury, troops and ports follow the cities the successors actually keep.
    total = 0;
    for (int r = 0; r < 3; ++r) { weights[r] = 0; coastal[r] = false; }
    for (uint i = 0; i < cities.size(); ++i)
    {
        weights[cities[i].realm] += cities[i].population;
        coastal[cities[i].realm] = coastal[cities[i].realm] || cities[i].coastal;
        total += cities[i].population;
    }
    // Consume before transfers, Python callbacks, or save opportunities.
    m_iCaliphatePartitionDecision = -1;
    m_bCaliphatePartitioned = true;

    PlayerTypes owners[3] = { NO_PLAYER, NO_PLAYER, NO_PLAYER };
    owners[chosen] = getID();
    int nextSlot = CALIPHATE_SLOT_1;
    const LeaderHeadTypes leader = (LeaderHeadTypes)GC.getInfoTypeForString(realmLeaders[chosen]);
    GC.getGameINLINE().changePlayer(getID(), GC.getInfoTypeForString(realmCivs[chosen]), leader, -1, isHuman(), true);
    configureCaliphateSuccessor();
    for (int r = 0; r < 3; ++r)
    {
        if (!weights[r] || r == chosen) continue;
        owners[r] = (PlayerTypes)nextSlot++;
        GC.getGameINLINE().addPlayer(owners[r], (LeaderHeadTypes)GC.getInfoTypeForString(realmLeaders[r]),
            (CivilizationTypes)GC.getInfoTypeForString(realmCivs[r]));
        CvPlayer& successor = GET_PLAYER(owners[r]);
        successor.setAlive(true);
        successor.m_bCaliphatePartitioned = true;
        successor.m_bArabianJihadTriggered = true;
        successor.configureCaliphateSuccessor();
        for (int c = 0; c < GC.getNumCivicOptionInfos(); ++c)
            successor.setCivics((CivicOptionTypes)c, getCivics((CivicOptionTypes)c));
        successor.setLastStateReligion(getStateReligion());
        for (int tech = 0; tech < GC.getNumTechInfos(); ++tech)
            if (GET_TEAM(getTeam()).isHasTech((TechTypes)tech))
            {
                GET_TEAM(successor.getTeam()).setHasTech((TechTypes)tech, true, owners[r], false, false);
                GET_TEAM(successor.getTeam()).setNoTradeTech((TechTypes)tech, GET_TEAM(getTeam()).isNoTradeTech((TechTypes)tech));
            }
    }
    // Preserve contact, map knowledge and current foreign wars, but no vassalage
    // between successors. They begin at peace with one another.
    for (int r = 0; r < 3; ++r)
    {
        if (owners[r] == NO_PLAYER || owners[r] == getID()) continue;
        CvTeam& team = GET_TEAM(GET_PLAYER(owners[r]).getTeam());
        for (int t = 0; t < MAX_TEAMS; ++t)
        {
            bool sibling = false;
            for (int s = 0; s < 3; ++s)
                if (owners[s] != NO_PLAYER && GET_PLAYER(owners[s]).getTeam() == t) sibling = true;
            if (GET_TEAM(getTeam()).isHasMet((TeamTypes)t) || sibling) team.meet((TeamTypes)t, false);
            if (!sibling && GET_TEAM(getTeam()).isAtWar((TeamTypes)t) && team.canDeclareWar((TeamTypes)t))
                team.declareWar((TeamTypes)t, false, WARPLAN_TOTAL);
        }
        team.meet(getTeam(), false);
    }
    const int treasury = getGold();
    int remainder = treasury;
    for (int r = 0; r < 3; ++r)
        if (owners[r] != NO_PLAYER && r != chosen)
        {
            int share = (int)((__int64)treasury * weights[r] / total);
            GET_PLAYER(owners[r]).setGold(share);
            remainder -= share;
        }
    setGold(remainder);
    logPartitionStage("successors_ready", getID());

    // Divide each unit class by population share using deterministic weighted
    // allocation. Prefer nearby realm cities on ties; transports retain cargo.
    std::vector<int> units;
    for (CvUnit* unit = firstUnit(&loop); unit != NULL; unit = nextUnit(&loop))
        if (!unit->isCargo() && !unit->isDelayedDeath()) units.push_back(unit->getID());
    std::vector<int> assigned(GC.getNumUnitClassInfos() * 3, 0);
    for (uint u = 0; u < units.size(); ++u)
    {
        CvUnit* unit = getUnit(units[u]);
        if (unit == NULL) continue;
        const bool sea = unit->getDomainType() == DOMAIN_SEA;
        int classId = unit->getUnitClassType(), count = 0, eligibleWeight = 0;
        bool hasPort = false;
        for (int r = 0; r < 3; ++r) if (weights[r] && coastal[r]) hasPort = true;
        for (int r = 0; r < 3; ++r)
            if (weights[r] && (!sea || !hasPort || coastal[r]))
            { count += assigned[classId * 3 + r]; eligibleWeight += weights[r]; }
        int best = chosen;
        __int64 bestScore = -((__int64)MAX_INT * MAX_INT);
        for (int r = 0; r < 3; ++r)
        {
            if (!weights[r] || (sea && hasPort && !coastal[r])) continue;
            CvPlot* destination = nearestRealmCity(cities, r, unit->plot(), sea && hasPort);
            int distance = plotDistance(unit->getX_INLINE(), unit->getY_INLINE(), destination->getX_INLINE(), destination->getY_INLINE());
            __int64 score = ((__int64)weights[r] * (count + 1) - (__int64)assigned[classId * 3 + r] * eligibleWeight) * 1000 - distance;
            if (score > bestScore) { bestScore = score; best = r; }
        }
        ++assigned[classId * 3 + best];
        CvPlot* destination = nearestRealmCity(cities, best, unit->plot(), sea && hasPort);
        // A fleet with no remaining home port keeps its legal sea position.
        if (sea && !hasPort) destination = unit->plot();
        transferUnit(unit, owners[best], destination);
    }

    // Political transfer, never conquest: no casualties, recruitment or loot.
    logPartitionStage("units_transferred", getID());
    m_bCaliphatePartitionInProgress = true;
    for (uint i = 0; i < cities.size(); ++i)
    {
        CvPlot* plot = GC.getMapINLINE().plotByIndexINLINE(cities[i].plot);
        PlayerTypes owner = owners[cities[i].realm];
        if (owner == getID()) continue;
        logPartitionStage("acquire_successor_city", owner, cities[i].plot);
        CvCity* city = plot->getPlotCity();
        const int culture = city->getCultureTimes100(getID());
        GET_PLAYER(owner).acquireCity(city, false, true, false);
        city = plot->getPlotCity();
        city->setCultureTimes100(owner, city->getCultureTimes100(owner) + culture, false, false);
        city->setCultureTimes100(getID(), 0, false, false);
        logPartitionStage("successor_city_complete", owner, cities[i].plot);
    }
    m_bCaliphatePartitionInProgress = false;
    logPartitionStage("divide_plot_culture", getID());
    for (int p = 0; p < GC.getMapINLINE().numPlotsINLINE(); ++p)
    {
        CvPlot* plot = GC.getMapINLINE().plotByIndexINLINE(p);
        for (int r = 0; r < 3; ++r)
            if (owners[r] != NO_PLAYER && r != chosen && plot->isRevealed(getTeam(), false))
                plot->setRevealed(GET_PLAYER(owners[r]).getTeam(), true, false, getTeam(), false);
        int realm = realmAt(plot->getX_INLINE(), plot->getY_INLINE());
        if (owners[realm] == NO_PLAYER || owners[realm] == getID()) continue;
        // Partition Arabian culture without taking any third country's culture.
        int culture = plot->getCulture(getID());
        if (culture > 0)
        {
            plot->changeCulture(owners[realm], culture, false);
            plot->setCulture(getID(), 0, false, false);
        }
    }
    // Release surplus cities after regional culture has been divided, so their
    // city plots cannot be reassigned to a successor by that division.
    m_bCaliphatePartitionInProgress = true;
    for (uint i = 0; i < independentCities.size(); ++i)
    {
        CvPlot* plot = GC.getMapINLINE().plotByIndexINLINE(independentCities[i].plot);
        PlayerTypes owner = GET_PLAYER((PlayerTypes)INDEPENDENT).getNumCities() <=
            GET_PLAYER((PlayerTypes)INDEPENDENT2).getNumCities() ? (PlayerTypes)INDEPENDENT : (PlayerTypes)INDEPENDENT2;
        logPartitionStage("acquire_independent_city", owner, independentCities[i].plot);
        CvCity* city = plot->getPlotCity();
        const int culture = city->getCultureTimes100(getID());
        GET_PLAYER(owner).acquireCity(city, false, true, false);
        city = plot->getPlotCity();
        city->setCultureTimes100(owner, city->getCultureTimes100(owner) + culture, false, false);
        city->setCultureTimes100(getID(), 0, false, false);
        PlayerTypes regionalOwner = owners[independentCities[i].realm];
        const int plotCulture = plot->getCulture(regionalOwner);
        plot->changeCulture(owner, plotCulture, false);
        plot->setCulture(regionalOwner, 0, false, false);
        logPartitionStage("independent_city_complete", owner, independentCities[i].plot);
    }
    m_bCaliphatePartitionInProgress = false;
    const BuildingTypes palace = (BuildingTypes)GC.getInfoTypeForString("BUILDING_PALACE");
    for (int r = 0; r < 3; ++r)
    {
        if (owners[r] == NO_PLAYER) continue;
        logPartitionStage("assign_capital", owners[r], r);
        CvPlayer& successor = GET_PLAYER(owners[r]);
        CvCity* best = NULL;
        int distance = MAX_INT;
        for (CvCity* city = successor.firstCity(&loop); city != NULL; city = successor.nextCity(&loop))
        {
            city->setNumRealBuilding(palace, 0);
            int d = plotDistance(city->getX_INLINE(), city->getY_INLINE(), capitalX[r], capitalY[r]);
            if (d < distance) { distance = d; best = city; }
        }
        if (best != NULL) { best->setNumRealBuilding(palace, 1); successor.setCapitalCity(best); }
    }
    logPartitionStage("update_cultural_owners", getID());
    for (int p = 0; p < GC.getMapINLINE().numPlotsINLINE(); ++p)
        GC.getMapINLINE().plotByIndexINLINE(p)->updateCulture(false, false);
    for (int r = 0; r < 3; ++r)
        if (owners[r] != NO_PLAYER)
        {
            logPartitionStage("update_maintenance", owners[r]);
            GET_PLAYER(owners[r]).updateMaintenance();
            logPartitionStage("update_plot_groups", owners[r]);
            GET_PLAYER(owners[r]).updatePlotGroups();
        }
    logPartitionStage("update_visibility", getID());
    GC.getMapINLINE().updateVisibility();
    logPartitionStage("python_partition_callback", getID());
    CyArgsList args;
    // MakeFunctionArgs packages one Python argument list. Do not pass it an
    // empty native array; give this notification its source player explicitly.
    args.add((int)getID());
    gDLL->getPythonIFace()->callFunction("CvEventInterface", "onCaliphatePartition", args.makeFunctionArgs());
    logPartitionStage("announce", getID());
    CvWString message = gDLL->getText("TXT_KEY_CALIPHATE_PARTITION_ANNOUNCE");
    for (int p = 0; p < MAX_CIV_PLAYERS; ++p)
        if (GET_PLAYER((PlayerTypes)p).isAlive() && GET_TEAM(GET_PLAYER((PlayerTypes)p).getTeam()).isHasMet(getTeam()))
            gDLL->getInterfaceIFace()->addMessage((PlayerTypes)p, false, GC.getEVENT_MESSAGE_TIME(), message, "AS2D_REVOLTEND", MESSAGE_TYPE_MAJOR_EVENT, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_HIGHLIGHT_TEXT"));
    logPartitionStage("complete", getID());
}
