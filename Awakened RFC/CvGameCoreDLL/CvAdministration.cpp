#include "CvGameCoreDLL.h"
#include "CvAdministration.h"
#include "CvCity.h"
#include "CvPlayer.h"
#include "CvPlayerAI.h"
#include "CvTeam.h"
#include "CvPlot.h"
#include "CvMap.h"
#include "CvGame.h"
#include "CvRhyes.h"
#include "CyArgsList.h"
#include <queue>
#include <functional>

namespace
{
    // Keep the hundredths API: capacity uses whole points, city effort tenths.
    int roundedAdministration100(__int64 numerator, int denominator, int step = 100)
    {
        const __int64 divisor = (__int64)denominator * step;
        return (int)((numerator + divisor - 1) / divisor * step);
    }
    int cityEffort100(int population, int travel, int modifier)
    {
        return roundedAdministration100((__int64)population * (10000 + 5 * travel) *
            std::max(0, 100 + modifier), 10000, 10);
    }
    unsigned int networkRevision = 1;
    struct Network
    {
        unsigned int revision;
        int turn, width, height, proposal;
        std::vector<int> distance, rawDistance, governor;
        std::vector<char> connected;
        Network() : revision(0), turn(-1), width(0), height(0), proposal(-1) {}
    };
    Network networks[MAX_PLAYERS];
    Network seatPlans[MAX_PLAYERS], harborPlans[MAX_PLAYERS], removalPlans[MAX_PLAYERS];
    const int INFINITY_TIME = 100000000;
    typedef std::pair<int, int> Entry;
    typedef std::priority_queue<Entry, std::vector<Entry>, std::greater<Entry> > TravelQueue;
    int residenceClass() { return GC.getInfoTypeForString("BUILDINGCLASS_GREAT_PALACE"); }
    bool residence(const CvCity& city)
    {
        static std::vector<int> types;
        static int infoCount = -1;
        if (infoCount != GC.getNumBuildingInfos())
        {
            types.clear(); infoCount = GC.getNumBuildingInfos();
            for (int b = 0; b < infoCount; ++b)
                if (GC.getBuildingInfo((BuildingTypes)b).getBuildingClassType() == residenceClass()) types.push_back(b);
        }
        for (unsigned int b = 0; b < types.size(); ++b)
            if (city.getNumActiveBuilding((BuildingTypes)types[b]) > 0) return true;
        return false;
    }
    bool permitted(const CvPlot* plot, TeamTypes team)
    {
        if (!plot || plot->isImpassable() || plot->isPeak()) return false;
        TeamTypes owner = plot->getTeam();
        return owner == NO_TEAM || owner == team || GET_TEAM(team).isOpenBorders(owner)
            || GET_TEAM(team).isVassal(owner) || GET_TEAM(owner).isVassal(team);
    }
    bool harbor(const CvPlot* plot)
    {
        CvCity* city = plot->getPlotCity();
        if (!city) return false;
        static std::vector<int> types;
        static int infoCount = -1;
        if (infoCount != GC.getNumBuildingInfos())
        {
            types.clear(); infoCount = GC.getNumBuildingInfos();
            int cls = GC.getInfoTypeForString("BUILDINGCLASS_HARBOR");
            for (int b = 0; b < infoCount; ++b)
                if (GC.getBuildingInfo((BuildingTypes)b).getBuildingClassType() == cls) types.push_back(b);
        }
        for (unsigned int b = 0; b < types.size(); ++b)
            if (city->getNumActiveBuilding((BuildingTypes)types[b]) > 0) return true;
        return false;
    }
    bool oceanAllowed(TeamTypes team, const CvPlot* plot)
    {
        if (plot->getTerrainType() != GC.getInfoTypeForString("TERRAIN_OCEAN")) return true;
        int astronomy = GC.getInfoTypeForString("TECH_ASTRONOMY");
        return astronomy >= 0 && GET_TEAM(team).isHasTech((TechTypes)astronomy);
    }
    int landCost(const CvPlot* from, const CvPlot* to, TeamTypes team)
    {
        int moves = to->getFeatureType() == NO_FEATURE ? GC.getTerrainInfo(to->getTerrainType()).getMovementCost()
            : GC.getFeatureInfo(to->getFeatureType()).getMovementCost();
        if (to->isHills()) moves += GC.getHILLS_EXTRA_MOVEMENT();
        int cost = std::max(1, std::min(2, moves)) * 600;
        if (from->getRouteType() != NO_ROUTE && to->getRouteType() != NO_ROUTE
            && (GET_TEAM(team).isBridgeBuilding() || !from->isRiverCrossing(directionXY(from, to))))
        {
            RouteTypes a = from->getRouteType(), b = to->getRouteType();
            int route = std::max(GC.getRouteInfo(a).getMovementCost() + GET_TEAM(team).getRouteChange(a),
                GC.getRouteInfo(b).getMovementCost() + GET_TEAM(team).getRouteChange(b));
            int flat = std::max(GC.getRouteInfo(a).getFlatMovementCost(), GC.getRouteInfo(b).getFlatMovementCost());
            cost = std::min(cost, std::min(route * 600 / GC.getMOVE_DENOMINATOR(), flat * 1200 / GC.getMOVE_DENOMINATOR()));
        }
        return std::max(1, cost);
    }
    void walkNetwork(const CvPlayer& player, std::vector<int>& distance, std::vector<int>& origins,
        TravelQueue& queue, const std::vector<char>& ports, bool connections)
    {
        CvMap& map = GC.getMapINLINE();
        TeamTypes team = player.getTeam();
        int states = connections ? 7 : 5;
        int limit = connections ? GC.getDefineINT("ARFC_ADMIN_LINK_TURNS") * 1200 : INFINITY_TIME;
        while (!queue.empty())
        {
            Entry entry = queue.top(); queue.pop();
            int time = entry.first, node = entry.second, state = node % states;
            if (time != distance[node] || time >= limit) continue;
            int fromIndex = node / states;
            CvPlot* from = map.plotByIndexINLINE(fromIndex);
            bool land = state == 0 || (connections && state >= 5);
            // Land cities renew land links. A town reached over sea cannot
            // renew a sea link until it has a harbor (land state 6).
            if (connections && land && from->getOwnerINLINE() == player.getID() && from->isCity())
            {
                CvCity* station = from->getPlotCity();
                int stationState = (state >= 5 && !ports[fromIndex] && !station->isCapital()) ? 6 : 0;
                if (time > 0 || stationState != state)
                {
                    int stationNode = fromIndex * states + stationState;
                    if (distance[stationNode] > 0) { distance[stationNode] = 0; queue.push(Entry(0, stationNode)); }
                    continue;
                }
            }
            for (int dir = 0; dir < NUM_DIRECTION_TYPES; ++dir)
            {
                CvPlot* to = plotDirection(from->getX_INLINE(), from->getY_INLINE(), (DirectionTypes)dir);
                if (!permitted(to, team)) continue;
                int index = map.plotNumINLINE(to->getX_INLINE(), to->getY_INLINE());
                int next = -1, value = limit;
                if (land && !to->isWater())
                {
                    int step = landCost(to, from, team);
                    // A continuous owned land corridor has no range limit.
                    if (connections && from->getOwnerINLINE() == player.getID() && to->getOwnerINLINE() == player.getID()) step = 0;
                    next = index * states + state; value = time + step;
                }
                else if (land && state != 6 && to->isWater() && oceanAllowed(team, to))
                {
                    int departure = ports[fromIndex] ? 1 : 0;
                    for (int arrival = 0; arrival < 2; ++arrival)
                    {
                        int sea = 1 + departure * 2 + arrival;
                        int speed = 1 << (departure + arrival);
                        int seaNode = index * states + sea, seaTime = time + 1200 / speed;
                        if (seaTime < distance[seaNode])
                        {
                            distance[seaNode] = seaTime; origins[seaNode] = origins[node]; queue.push(Entry(seaTime, seaNode));
                        }
                    }
                }
                else if (!land && to->isWater() && oceanAllowed(team, to))
                {
                    int flags = state - 1, speed = 1 << ((flags / 2) + (flags % 2));
                    next = index * states + state; value = time + 1200 / speed;
                }
                else if (!land && !to->isWater() && int(ports[index]) == (state - 1) % 2)
                {
                    next = index * states + (connections ? 5 : 0); value = time + 600;
                }
                if (next >= 0 && value < distance[next])
                {
                    distance[next] = value; origins[next] = origins[node]; queue.push(Entry(value, next));
                }
            }
        }
    }
    void buildNetwork(const CvPlayer& player, Network& cache, const CvPlot* extraResidence = NULL,
        const CvPlot* extraHarbor = NULL, const CvPlot* removedResidence = NULL)
    {
        PROFILE("Administration::buildNetwork");
        CvMap& map = GC.getMapINLINE();
        int count = map.numPlotsINLINE(), iterator;
        std::vector<char> ports(count, 0);
        // Cache endpoint harbor flags once instead of looking up buildings per edge.
        for (int owner = 0; owner < MAX_PLAYERS; ++owner)
            for (CvCity* city = GET_PLAYER((PlayerTypes)owner).firstCity(&iterator); city; city = GET_PLAYER((PlayerTypes)owner).nextCity(&iterator))
                if (harbor(city->plot()) || city->plot() == extraHarbor) ports[map.plotNumINLINE(city->getX_INLINE(), city->getY_INLINE())] = 1;
        std::vector<int> distance(count * 5, INFINITY_TIME), origins(count * 5, -1);
        TravelQueue queue;
        CvCity* capital = player.getCapitalCity();
        if (capital)
        {
            int root = map.plotNumINLINE(capital->getX_INLINE(), capital->getY_INLINE()) * 5;
            distance[root] = 0; queue.push(Entry(0, root));
        }
        walkNetwork(player, distance, origins, queue, ports, false);
        cache.rawDistance.resize(count);
        for (int p = 0; p < count; ++p) cache.rawDistance[p] = distance[p * 5];
        // Every discounted source uses its unassisted capital distance. Thus a
        // path can receive exactly one residence discount, never a chain of them.
        for (CvCity* city = player.firstCity(&iterator); city; city = player.nextCity(&iterator))
            if (city->plot() != removedResidence && (residence(*city) || city->plot() == extraResidence))
            {
                int index = map.plotNumINLINE(city->getX_INLINE(), city->getY_INLINE());
                int direct = cache.rawDistance[index] >= INFINITY_TIME ? GC.getDefineINT("ARFC_ADMIN_UNREACHABLE_TRAVEL") * 1200 : cache.rawDistance[index];
                int seed = direct * GC.getDefineINT("ARFC_ADMIN_RESIDENCE_CAPITAL_PERCENT") / 100;
                if (seed < distance[index * 5])
                {
                    distance[index * 5] = seed; origins[index * 5] = city->getID(); queue.push(Entry(seed, index * 5));
                }
            }
        walkNetwork(player, distance, origins, queue, ports, false);
        cache.distance.resize(count); cache.governor.resize(count);
        for (int p = 0; p < count; ++p) { cache.distance[p] = distance[p * 5]; cache.governor[p] = origins[p * 5]; }
        // A residence city must use its own residence, including its own benefit.
        for (CvCity* city = player.firstCity(&iterator); city; city = player.nextCity(&iterator))
            if (city->plot() != removedResidence && (residence(*city) || city->plot() == extraResidence))
            {
                int index = map.plotNumINLINE(city->getX_INLINE(), city->getY_INLINE());
                int direct = cache.rawDistance[index] >= INFINITY_TIME ? GC.getDefineINT("ARFC_ADMIN_UNREACHABLE_TRAVEL") * 1200 : cache.rawDistance[index];
                cache.distance[index] = direct * GC.getDefineINT("ARFC_ADMIN_RESIDENCE_CAPITAL_PERCENT") / 100;
                cache.governor[index] = city->getID();
            }
        // Connectivity is independent of cost distance and residence discounts.
        int limit = GC.getDefineINT("ARFC_ADMIN_LINK_TURNS") * 1200;
        distance.assign(count * 7, limit); origins.assign(count * 7, -1);
        if (capital)
        {
            int root = map.plotNumINLINE(capital->getX_INLINE(), capital->getY_INLINE()) * 7;
            distance[root] = 0; queue.push(Entry(0, root));
        }
        walkNetwork(player, distance, origins, queue, ports, true);
        cache.connected.resize(count);
        for (int p = 0; p < count; ++p) cache.connected[p] = std::min(distance[p * 7], std::min(distance[p * 7 + 5], distance[p * 7 + 6])) < limit;
        cache.revision = networkRevision;
        cache.turn = GC.getGameINLINE().getGameTurn();
        cache.width = map.getGridWidthINLINE(); cache.height = map.getGridHeightINLINE();
    }
    Network& currentNetwork(const CvPlayer& player)
    {
        Network& cache = networks[player.getID()];
        CvMap& map = GC.getMapINLINE();
        if (cache.revision != networkRevision || cache.width != map.getGridWidthINLINE() || cache.height != map.getGridHeightINLINE()) buildNetwork(player, cache);
        return cache;
    }
    int plotIndex(const CvPlot& plot) { return GC.getMapINLINE().plotNumINLINE(plot.getX_INLINE(), plot.getY_INLINE()); }
    int time100(int value) { return value >= INFINITY_TIME ? GC.getDefineINT("ARFC_ADMIN_UNREACHABLE_TRAVEL") * 100 : value / 12; }
    Network& removalNetwork(const CvCity& city)
    {
        const CvPlayer& player = GET_PLAYER(city.getOwnerINLINE());
        Network& cache = removalPlans[player.getID()];
        int proposal = plotIndex(*city.plot());
        if (cache.revision != networkRevision || cache.proposal != proposal)
        {
            buildNetwork(player, cache, NULL, NULL, city.plot()); cache.proposal = proposal;
        }
        return cache;
    }

}

namespace Administration
{
    void invalidateNetwork() { ++networkRevision; }
    bool penaltiesSuspended(const CvPlayer& player)
    {
        // The full jihad event can belong to another civilization as well.
        return player.isArabianJihadActive();
    }
    int travelTime100(const CvCity& city)
    {
        return travelTime100(GET_PLAYER(city.getOwnerINLINE()), *city.plot());
    }
    int travelTime100(const CvPlayer& player, const CvPlot& plot)
    {
        return time100(currentNetwork(player).distance[plotIndex(plot)]);
    }
    int capitalTravelTime100(const CvPlayer& player, const CvPlot& plot)
    {
        return time100(currentNetwork(player).rawDistance[plotIndex(plot)]);
    }
    bool isReachable(const CvPlayer& player, const CvPlot& plot, bool founding)
    {
        Network& cache = currentNetwork(player);
        if (cache.connected[plotIndex(plot)]) return true;
        if (founding && !plot.isWater())
            for (int d = 0; d < NUM_DIRECTION_TYPES; ++d)
            {
                CvPlot* adjacent = plotDirection(plot.getX_INLINE(), plot.getY_INLINE(), (DirectionTypes)d);
                if (adjacent && !adjacent->isWater() && adjacent->getOwnerINLINE() == player.getID() && cache.connected[plotIndex(*adjacent)]) return true;
            }
        return false;
    }
    bool hasResidence(const CvCity& city) { return residence(city); }
    bool isResidenceBuilding(int building) { return GC.getBuildingInfo((BuildingTypes)building).getBuildingClassType() == residenceClass(); }
    int residenceCost100(const CvCity& city) { return residence(city) ? GC.getDefineINT("ARFC_ADMIN_RESIDENCE_GOLD") * 100 : 0; }
    int governingResidence(const CvCity& city) { return currentNetwork(GET_PLAYER(city.getOwnerINLINE())).governor[plotIndex(*city.plot())]; }
    int effortWithoutResidence100(const CvCity& removed)
    {
        const CvPlayer& player = GET_PLAYER(removed.getOwnerINLINE());
        Network& plan = removalNetwork(removed);
        int total = 0, iterator;
        for (CvCity* city = player.firstCity(&iterator); city; city = player.nextCity(&iterator))
            total += cityEffort100(city->getPopulation(), time100(plan.distance[plotIndex(*city->plot())]), localModifier(*city));
        return total;
    }
    int goldChangeWithoutResidence100(const CvCity& removed)
    {
        const CvPlayer& player = GET_PLAYER(removed.getOwnerINLINE());
        int effort = effortWithoutResidence100(removed), capacity = capacity100(player);
        int overload = penaltiesSuspended(player) ? 0 : std::max(0, (int)((__int64)effort * 10000 / capacity) - 10000);
        Network& plan = removalNetwork(removed);
        int upkeep100 = 0, iterator, gold100 = 0, research100 = 0, goldDelta100 = 0, researchDelta100 = 0;
        for (CvCity* city = player.firstCity(&iterator); city; city = player.nextCity(&iterator))
        {
            int cityEffort = cityEffort100(city->getPopulation(), time100(plan.distance[plotIndex(*city->plot())]), localModifier(*city));
            upkeep100 += (int)((__int64)cityEffort * (10000 + 2 * overload) / 20000) + (city == &removed ? 0 : residenceCost100(*city));
            gold100 += city->getCommerceRateTimes100(COMMERCE_GOLD);
            research100 += city->getCommerceRateTimes100(COMMERCE_RESEARCH);
            if (!city->isDisorder())
            {
                int base = city->getBaseYieldRate(YIELD_PRODUCTION) * city->getBaseYieldRateModifier(YIELD_PRODUCTION) / 100;
                int after = (int)((__int64)base * std::max(0, 10000 - overload / 5) / 10000);
                int delta = after - city->getYieldRate(YIELD_PRODUCTION);
                goldDelta100 += delta * city->getProductionToCommerceModifier(COMMERCE_GOLD);
                researchDelta100 += delta * city->getProductionToCommerceModifier(COMMERCE_RESEARCH);
            }
        }
        int afterCosts = player.calculateInflatedCostsWithMaintenance(upkeep100 / 100);
        int goldDelta = (gold100 + goldDelta100) / 100 - gold100 / 100 + player.calculateInflatedCosts() - afterCosts;
        int afterRate = player.calculateGoldRate() + goldDelta;
        if (!player.isCommerceFlexible(COMMERCE_RESEARCH))
        {
            int research = player.getCommerceRate(COMMERCE_RESEARCH) + (research100 + researchDelta100) / 100 - research100 / 100;
            int netResearch = (GC.getDefineINT("BASE_RESEARCH_RATE") + research) * player.calculateResearchModifier(player.getCurrentResearch()) / 100;
            if (player.isHorde()) netResearch = netResearch * 75 / 100;
            afterRate = std::min(0, netResearch + player.calculateBaseNetGold() + goldDelta);
        }
        return (afterRate - player.calculateGoldRate()) * 100;
    }
    int civicModifier(const CvPlayer& player, int civic)
    {
        if (civic < 0 || civic >= GC.getNumCivicInfos()) return 0;
        const CvCivicInfo& info = GC.getCivicInfo((CivicTypes)civic);
        const int civilization = player.getCivilizationType();
        if (info.isPharaonicVariant(civilization)) return GC.getDefineINT("ARFC_ADMIN_PHARAONISM");
        if (info.isDivineKingshipVariant(civilization)) return GC.getDefineINT("ARFC_ADMIN_DIVINE_KINGSHIP");
        if (info.isRomanRepublicVariant(civilization)) return GC.getDefineINT("ARFC_ADMIN_ROMAN_REPUBLIC");
        if (info.isRomanLegionsVariant(civilization)) return GC.getDefineINT("ARFC_ADMIN_ROMAN_LEGIONS");
        if (info.isHordeVariant(civilization)) return GC.getDefineINT("ARFC_ADMIN_HORDE");
        CvString key = "ARFC_ADMIN_"; key += info.getType();
        return GC.getDefineINT(key);
    }
    int wonderModifier(int building)
    {
        CvString type = GC.getBuildingInfo((BuildingTypes)building).getType();
        CvString::size_type suffix = type.find("_ARCTIC_DISPLAY");
        if (suffix != CvString::npos) type.erase(suffix);
        CvString key = "ARFC_ADMIN_"; key += type;
        return GC.getDefineINT(key);
    }
    int modifiedCapacity100(const CvPlayer& player, int extraPercent)
    {
        int base = historicalTurns(1) == 2 ? 50 : 33;
        int percent = 100 + extraPercent;
        for (int c = 0; c < GC.getNumCivicOptionInfos(); ++c) percent += civicModifier(player, player.getCivics((CivicOptionTypes)c));
        const char* wonders[] = { "BUILDING_PYRAMID", "BUILDING_GREAT_LIBRARY", "BUILDING_VERSAILLES" };
        for (int w = 0; w < 3; ++w)
        {
            int b = GC.getInfoTypeForString(wonders[w]);
            if (b >= 0) percent += player.getBuildingClassCount((BuildingClassTypes)GC.getBuildingInfo((BuildingTypes)b).getBuildingClassType()) * wonderModifier(b);
        }
        return roundedAdministration100((__int64)base * (100 + 25 * std::max(0, (int)player.getCurrentEra())) * std::max(1, percent), 100);
    }
    int capacity100(const CvPlayer& player)
    {
        return modifiedCapacity100(player, 0);
    }
    int religionModifier(const CvCity& city, int civic, int state)
    {
        if (civic == GC.getInfoTypeForString("CIVIC_TOLERANCE")) return 0;
        bool atheism = civic == GC.getInfoTypeForString("CIVIC_STATE_ATHEISM");
        if (state == NO_RELIGION && !atheism) return 0;
        int religion = 0;
        for (int r = 0; r < GC.getNumReligionInfos(); ++r)
            if (city.isHasReligion((ReligionTypes)r)) religion += (!atheism && r == state) ? -5 : 10;
        if (civic == GC.getInfoTypeForString("CIVIC_GOD_STATE")) religion *= 2;
        return religion;
    }
    int localModifier(const CvCity& city)
    {
        const CvPlayer& player = GET_PLAYER(city.getOwnerINLINE());
        int option = GC.getInfoTypeForString("CIVICOPTION_RELIGION");
        return city.getMaintenanceModifier() + religionModifier(city,
            player.getCivics((CivicOptionTypes)option), player.getStateReligion());
    }
    int religionEffort100(const CvPlayer& player, int civic, int state)
    {
        int total = 0, iterator;
        for (CvCity* city = player.firstCity(&iterator); city; city = player.nextCity(&iterator))
            total += cityEffort100(city->getPopulation(), travelTime100(*city),
                city->getMaintenanceModifier() + religionModifier(*city, civic, state));
        return total;
    }
    int burdenValue(const CvPlayer& player, int effort, int capacity)
    {
        if (penaltiesSuspended(player)) return 0;
        int overload = std::max(0, (int)((__int64)effort * 10000 / std::max(1, capacity)) - 10000);
        // Empire-wide production, stability and upkeep losses grow together.
        return (int)((__int64)overload * (10 + player.getTotalPopulation()) / 500);
    }
    int expansionWeight(const CvPlayer& player, const CvPlot& plot, int population, int local)
    {
        if (player.getID() >= NUM_MAJOR_PLAYERS || player.getNumCities() == 0 || penaltiesSuspended(player)) return 100;
        int travel = travelTime100(player, plot);
        if (!isReachable(player, plot, true)) return 0;
        int extra = cityEffort100(population, travel, local);
        int capacity = capacity100(player), effort = totalEffort100(player);
        // Reserve a little space for the existing cities' next growth.
        int reserve = std::min(capacity / 10, player.getNumCities() * 100);
        int pressure = std::max(0, (effort + extra + reserve) * 100 / capacity - 100);
        return 10000 / (100 + pressure * 4 + travel / 40);
    }
    int infrastructureValue(const CvCity& city, int building)
    {
        const CvPlayer& player = GET_PLAYER(city.getOwnerINLINE());
        const CvBuildingInfo& info = GC.getBuildingInfo((BuildingTypes)building);
        bool seat = isResidenceBuilding(building) && !hasResidence(city);
        bool port = info.getBuildingClassType() == GC.getInfoTypeForString("BUILDINGCLASS_HARBOR") && !harbor(city.plot());
        if (!seat && !port && wonderModifier(building) == 0) return 0;
        int capacity = capacity100(player), effort = totalEffort100(player);
        int extra = modifiedCapacity100(player, wonderModifier(building)) - capacity;
        int value = extra / 100 + burdenValue(player, effort, capacity) - burdenValue(player, effort, capacity + extra);
        if (!seat && !port) return value;
        // Shortlist one buildable location before running a hypothetical network.
        // Scores here are cheap geographic estimates; the final saving uses real routes.
        const CvCity* best = NULL;
        int bestScore = -1, iterator, otherIterator;
        for (CvCity* candidate = player.firstCity(&iterator); candidate; candidate = player.nextCity(&iterator))
        {
            if (!candidate->canConstruct((BuildingTypes)building, candidate->getProductionBuilding() == building)) continue;
            if (seat && hasResidence(*candidate)) continue;
            if (port && harbor(candidate->plot())) continue;
            int score = 0;
            for (CvCity* other = player.firstCity(&otherIterator); other; other = player.nextCity(&otherIterator))
            {
                int travel = travelTime100(*other);
                if (seat && candidate->area() == other->area())
                {
                    int estimate = plotDistance(candidate->getX_INLINE(), candidate->getY_INLINE(), other->getX_INLINE(), other->getY_INLINE()) * landCost(candidate->plot(), candidate->plot(), player.getTeam()) / 12;
                    int capitalPart = capitalTravelTime100(player, *candidate->plot()) * GC.getDefineINT("ARFC_ADMIN_RESIDENCE_CAPITAL_PERCENT") / 100;
                    score += other->getPopulation() * std::max(0, travel - estimate - capitalPart);
                }
                if (port && (other == candidate || candidate->isGovernmentCenter()) && other->isCoastal(GC.getMIN_WATER_SIZE_FOR_OCEAN()))
                    score += other->getPopulation() * travel;
            }
            if (score > bestScore) { bestScore = score; best = candidate; }
        }
        if (best != &city || bestScore <= 0) return value;
        Network& plan = seat ? seatPlans[player.getID()] : harborPlans[player.getID()];
        int proposal = GC.getMapINLINE().plotNumINLINE(city.getX_INLINE(), city.getY_INLINE());
        if (plan.revision != networkRevision || plan.proposal != proposal)
        {
            buildNetwork(player, plan, seat ? city.plot() : NULL, port ? city.plot() : NULL);
            plan.proposal = proposal;
        }
        int saved = 0, rescued = 0;
        for (CvCity* other = player.firstCity(&iterator); other; other = player.nextCity(&iterator))
        {
            int index = GC.getMapINLINE().plotNumINLINE(other->getX_INLINE(), other->getY_INLINE());
            int oldTime = travelTime100(*other), newTime = time100(plan.distance[index]);
            saved += cityEffort100(other->getPopulation(), oldTime, localModifier(*other)) - cityEffort100(other->getPopulation(), newTime, localModifier(*other));
            if (!isReachable(player, *other->plot()) && plan.connected[index]) rescued += other->getPopulation();
        }
        int reserveDivisor = effort * 100 < capacity * 75 ? 8 : (effort * 100 < capacity * 90 ? 4 : 1);
        return value - (seat ? GC.getDefineINT("ARFC_ADMIN_RESIDENCE_GOLD") * 4 : 0) + saved / (25 * reserveDivisor) + rescued * 20 + burdenValue(player, effort, capacity + extra) - burdenValue(player, std::max(0, effort - saved), capacity + extra);
    }
    int purgeHappinessChange(const CvCity& city, int religion)
    {
        if (religion == NO_RELIGION || !city.isHasReligion((ReligionTypes)religion)) return 0;
        const CvPlayer& player = GET_PLAYER(city.getOwnerINLINE());
        int change = 0;
        bool immune = city.isNoUnhappiness();
        for (int r = 0; r < GC.getNumReligionInfos(); ++r)
            if (r != religion && city.isHasReligion((ReligionTypes)r))
            {
                int happy = city.getReligionHappiness((ReligionTypes)r);
                change -= immune ? std::max(0, happy) : happy;
            }
        for (int b = 0; b < GC.getNumBuildingInfos(); ++b)
        {
            const CvBuildingInfo& info = GC.getBuildingInfo((BuildingTypes)b);
            int r = info.getReligionType() != NO_RELIGION ? info.getReligionType() : info.getPrereqReligion();
            int count = city.getNumActiveBuilding((BuildingTypes)b);
            if (!count || r == NO_RELIGION || r == religion || !city.isHasReligion((ReligionTypes)r) || info.getHolyCity() != NO_RELIGION) continue;
            // Losing immunity is an especially costly purge; avoid optimistic estimates.
            if (info.isNoUnhappiness()) return -2 * city.getPopulation();
            int happy = city.getBuildingHappiness((BuildingTypes)b) + info.getAreaHappiness() + info.getGlobalHappiness();
            for (int bonus = 0; bonus < GC.getNumBonusInfos(); ++bonus)
                if (city.hasBonus((BonusTypes)bonus)) happy += info.getBonusHappinessChanges(bonus);
            change -= count * (immune ? std::max(0, happy) : happy);
        }
        if (!immune)
        {
            int count = 0;
            for (int p = 0; p < MAX_PLAYERS; ++p)
            {
                const CvPlayer& enemy = GET_PLAYER((PlayerTypes)p);
                if (enemy.isAlive() && GET_TEAM(player.getTeam()).isAtWar(enemy.getTeam()) && enemy.getStateReligion() == religion)
                    count += enemy.getHasReligionCount((ReligionTypes)religion);
            }
            int afterReligionAnger = GC.getDefineINT("RELIGION_PERCENT_ANGER") * count / std::max(1, GC.getGameINLINE().getNumCities());
            if (player.isCivic((CivicTypes)GC.getInfoTypeForString("CIVIC_TOLERANCE"))) afterReligionAnger = 0;
            int before = city.getOvercrowdingPercentAnger() + city.getNoMilitaryPercentAnger() + city.getCulturePercentAnger() +
                city.getReligionPercentAnger() + city.getHurryPercentAnger() + city.getConscriptPercentAnger() +
                city.getDefyResolutionPercentAnger() + city.getWarWearinessPercentAnger();
            for (int c = 0; c < GC.getNumCivicInfos(); ++c) before += player.getCivicPercentAnger((CivicTypes)c);
            int after = before - city.getReligionPercentAnger() + afterReligionAnger;
            change += before * city.getPopulation() / GC.getPERCENT_ANGER_DIVISOR() - after * city.getPopulation() / GC.getPERCENT_ANGER_DIVISOR();
        }
        return change;
    }
    int purgeValue(const CvCity& city, int religion)
    {
        const CvPlayerAI& player = GET_PLAYER(city.getOwnerINLINE());
        if (religion == NO_RELIGION || religion != player.getStateReligion() || !city.isHasReligion((ReligionTypes)religion)
            || player.isCivic((CivicTypes)GC.getInfoTypeForString("CIVIC_TOLERANCE"))
            || player.isCivic((CivicTypes)GC.getInfoTypeForString("CIVIC_STATE_ATHEISM"))
            || player.AI_isDoStrategy(AI_STRATEGY_CULTURE2)) return 0;
        int foreign = 0, loss = 0;
        for (int r = 0; r < GC.getNumReligionInfos(); ++r)
            if (r != religion && city.isHasReligion((ReligionTypes)r))
            {
                if (city.isHolyCity((ReligionTypes)r)) return 0;
                ++foreign;
            }
        if (foreign == 0) return 0;
        for (int b = 0; b < GC.getNumBuildingInfos(); ++b)
        {
            const CvBuildingInfo& info = GC.getBuildingInfo((BuildingTypes)b);
            int r = info.getReligionType() != NO_RELIGION ? info.getReligionType() : info.getPrereqReligion();
            if (r != NO_RELIGION && r != religion && city.isHasReligion((ReligionTypes)r) && info.getHolyCity() == NO_RELIGION)
                loss += city.getNumBuilding((BuildingTypes)b) * std::max(0, info.getProductionCost()) / 4;
        }
        int factor = player.isCivic((CivicTypes)GC.getInfoTypeForString("CIVIC_GOD_STATE")) ? 2 : 1;
        int saved = effort100(city) - cityEffort100(city.getPopulation(), travelTime100(city), localModifier(city) - foreign * 10 * factor);
        int effort = totalEffort100(player), capacity = capacity100(player);
        int happyChange = purgeHappinessChange(city, religion);
        int angryBefore = std::max(0, city.unhappyLevel() - city.happyLevel());
        int angryAfter = std::max(0, city.unhappyLevel() - city.happyLevel() - happyChange);
        int value = saved / 10 + 8 * happyChange + 24 * (angryBefore - angryAfter) +
            burdenValue(player, effort, capacity) - burdenValue(player, std::max(0, effort - saved), capacity) - loss;
        return value >= 12 ? value : 0;
    }
    int effort100(const CvCity& city)
    {
        return cityEffort100(city.getPopulation(), travelTime100(city), localModifier(city));
    }
    int totalEffort100(const CvPlayer& player)
    {
        int value = 0, iterator;
        for (CvCity* city = player.firstCity(&iterator); city; city = player.nextCity(&iterator)) value += effort100(*city);
        return value;
    }
    int overload100(const CvPlayer& player)
    {
        if (player.getID() >= NUM_MAJOR_PLAYERS || player.isBarbarian() || player.isMinorCiv() || penaltiesSuspended(player)) return 0;
        int capacity = capacity100(player);
        return std::max(0, (int)((__int64)totalEffort100(player) * 10000 / capacity) - 10000);
    }
    int productionPercent(const CvPlayer& player) { return std::max(0, 10000 - overload100(player) / 5); }
}

// One shared query interface for the advisor, city UI and synchronized Python rules.
int CvPlayer::getAdministrationValue(int kind, int cityID) const
{
    CvCity* city = kind >= 7 && cityID >= 0 ? getCity(cityID) : NULL;
    switch (kind)
    {
    case 0: return Administration::capacity100(*this);
    case 1: return Administration::totalEffort100(*this);
    case 2: return Administration::overload100(*this);
    case 3: return -Administration::overload100(*this) / 250;
    case 4: return 10000 - Administration::productionPercent(*this);
    case 5: return Administration::overload100(*this) * 2;
    case 6: return Administration::civicModifier(*this, cityID);
    case 7: return city ? Administration::travelTime100(*city) : 1000;
    case 8: return city ? Administration::effort100(*city) : 0;
    case 9: return city ? Administration::localModifier(*city) : 0;
    case 10: return Administration::penaltiesSuspended(*this) ? 1 : 0;
    case 11: return city ? Administration::purgeHappinessChange(*city, getStateReligion()) : 0;
    case 12: return city ? Administration::purgeValue(*city, getStateReligion()) : 0;
    case 13: return city ? Administration::capitalTravelTime100(*this, *city->plot()) : 0;
    case 14: return city && Administration::isReachable(*this, *city->plot()) ? 1 : 0;
    case 15: return city ? Administration::governingResidence(*city) : -1;
    case 16: return city ? Administration::residenceCost100(*city) : 0;
    case 17: return city ? Administration::effortWithoutResidence100(*city) : 0;
    case 18: return city ? Administration::goldChangeWithoutResidence100(*city) : 0;
    case 20:
        if (city && Administration::hasResidence(*city))
        {
            int before = Administration::totalEffort100(*this), after = Administration::effortWithoutResidence100(*city), cap = Administration::capacity100(*this);
            int reserveDivisor = after * 100 < cap * 75 ? 8 : (after * 100 < cap * 90 ? 4 : 1);
            return Administration::goldChangeWithoutResidence100(*city) * 4 / 100 - (after - before) / (25 * reserveDivisor) +
                Administration::burdenValue(*this, before, cap) - Administration::burdenValue(*this, after, cap);
        }
        return 0;
    }
    return 0;
}

int CvPlayer::getAdministrationReleaseTarget(int cityID) const
{
    CvCity* city = getCity(cityID);
    if (!city || city->isCapital() || getNumCities() < 2 || isMinorCiv() || isBarbarian()) return -1;
    if (GET_TEAM(getTeam()).isAVassal() || GC.getGameINLINE().isOption(GAMEOPTION_NO_VASSAL_STATES)) return -1;
    // Prefer an existing vassal of this owner. Never recycle a
    // future spawn, a human connection, an occupied team or a reserved event slot.
    for (int p = 0; p < NUM_MAJOR_PLAYERS; ++p)
    {
        const CvPlayer& target = GET_PLAYER((PlayerTypes)p);
        if (target.getID() != getID() && target.isAlive()
            && GET_TEAM(target.getTeam()).isVassal(getTeam())) return p;
    }
    for (int p = 0; p < NUM_MAJOR_PLAYERS; ++p)
    {
        const CvPlayer& target = GET_PLAYER((PlayerTypes)p);
        if (target.getID() != getID() && !target.isAlive() && target.isEverAlive() && !target.isHuman()
            && !GET_TEAM(target.getTeam()).isAlive() && target.getCivilizationType() != NO_CIVILIZATION
            && GC.getGameINLINE().getGameTurn() >= historicalTurns(startingTurn[p]))
        {
            CyArgsList args;
            args.add(p); args.add(city->getX_INLINE()); args.add(city->getY_INLINE());
            long historical = 0;
            gDLL->getPythonIFace()->callFunction(PYScreensModule, "isAdministrationHistoricalCity", args.makeFunctionArgs(), &historical);
            if (historical) return p;
        }
    }
    return -1;
}

bool CvPlayer::releaseAdministrationCity(int cityID, bool independent)
{
    CvCity* city = getCity(cityID);
    if (!city || city->isCapital() || getNumCities() < 2 || isMinorCiv() || isBarbarian()) return false;
    int targetID = independent ? (int)INDEPENDENT : getAdministrationReleaseTarget(cityID);
    if (targetID < 0) return false;
    CvPlayer& target = GET_PLAYER((PlayerTypes)targetID);
    if (!independent && !target.isAlive())
    {
        CvTeam& team = GET_TEAM(target.getTeam());
        for (int other = 0; other < MAX_TEAMS; ++other)
            if (team.isAtWar((TeamTypes)other)) team.makePeace((TeamTypes)other);
        for (int tech = 0; tech < GC.getNumTechInfos(); ++tech)
            team.setHasTech((TechTypes)tech, GET_TEAM(getTeam()).isHasTech((TechTypes)tech), target.getID(), false, false);
        for (int civic = 0; civic < GC.getNumCivicOptionInfos(); ++civic)
            target.setCivics((CivicOptionTypes)civic, getCivics((CivicOptionTypes)civic));
        target.setLastStateReligion(getStateReligion());
        target.setParent(getID());
        target.setGold(0);
        target.changeAnarchyTurns(-target.getAnarchyTurns());
        target.setRevolutionTimer(0);
        target.setConversionTimer(0);
    }
    CvPlot* cityPlot = city->plot();
    target.acquireCity(city, false, true, true);
    // A release establishes a new administration, without inherited city culture.
    CvCity* releasedCity = cityPlot->getPlotCity();
    if (releasedCity && releasedCity->getOwnerINLINE() == targetID)
    {
        for (int p = 0; p < MAX_PLAYERS; ++p)
            releasedCity->setCultureTimes100((PlayerTypes)p, 0, false, true);
    }
    if (!independent)
    {
        if (!target.getCapitalCity()) target.findNewCapital();
        GET_TEAM(target.getTeam()).meet(getTeam(), false);
        if (!GET_TEAM(target.getTeam()).isVassal(getTeam())) GET_TEAM(getTeam()).assignVassal(target.getTeam(), false);
    }
    Administration::invalidateNetwork();
    updateMaintenance();
    target.updateMaintenance();
    return true;
}


bool CvPlayer::removeAdministrationResidence(int cityID)
{
    CvCity* city = getCity(cityID);
    if (!city || !Administration::hasResidence(*city)) return false;
    for (int b = 0; b < GC.getNumBuildingInfos(); ++b)
        if (Administration::isResidenceBuilding(b))
        {
            city->setNumRealBuilding((BuildingTypes)b, 0);
            city->setNumFreeBuilding((BuildingTypes)b, 0);
        }
    Administration::invalidateNetwork();
    updateMaintenance();
    AI_makeAssignWorkDirty();
    city->setInfoDirty(true);
    return true;
}

int CvPlayer::calculateInflatedCostsWithMaintenance(int maintenance) const
{
    int preCosts = calculatePreInflatedCosts() - getTotalMaintenance() + maintenance;
    return (int)std::min((__int64)MAX_INT, (__int64)preCosts * ((__int64)1000000 + m_iMetalInflationTimes10000) / 1000000);
}
