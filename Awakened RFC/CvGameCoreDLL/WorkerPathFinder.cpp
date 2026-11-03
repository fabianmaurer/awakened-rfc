#include "CvGameCoreDLL.h"
#include "ObserverPerformance.h"
#include "WorkerPathFinder.h"
#include "CvUnitAI.h"
#include "CvSelectionGroup.h"
#include "CvPlayerAI.h"
#include "CvGameAI.h"
#include "CvPlot.h"
#include "CvInfos.h"
#include "CvGameCoreUtils.h"
#include <queue>

namespace {
    struct WorkerPathNode {
        int cost, moves, turns, parent;
        bool closed;
        WorkerPathNode() : cost(MAX_INT), moves(0), turns(0), parent(-1), closed(false) {}
    };
    struct WorkerPathOpen {
        int cost, index;
        WorkerPathOpen(int c, int i) : cost(c), index(i) {}
        bool operator<(const WorkerPathOpen& other) const {
            // Stable integer ties are independent of addresses and wall time.
            return cost != other.cost ? cost > other.cost : index > other.index;
        }
    };
    int plotIndex(const CvPlot* plot) {
        return GC.getMapINLINE().plotNumINLINE(plot->getX_INLINE(), plot->getY_INLINE());
    }
    void copyNode(FAStarNode& target, const CvPlot* plot, const WorkerPathNode& source) {
        target.m_iX = plot->getX_INLINE();
        target.m_iY = plot->getY_INLINE();
        target.m_iKnownCost = source.cost;
        target.m_iData1 = source.moves;
        target.m_iData2 = source.turns;
    }
}

// Lazy single-source Dijkstra: changing the destination never resets the queue.
// Like the legacy search, keep one movement-state label per plot. This is a
// candidate-ranking approximation, not a claim of optimal time-dependent paths.
class WorkerPathField
{
public:
    int flags;
    std::vector<WorkerPathNode> nodes;
    std::priority_queue<WorkerPathOpen> open;
    explicit WorkerPathField(CvUnitAI* unit, int pathFlags)
        : flags(pathFlags), nodes(GC.getMapINLINE().numPlotsINLINE()) {
        int start = plotIndex(unit->plot());
        nodes[start].cost = 0;
        nodes[start].moves = unit->movesLeft();
        nodes[start].turns = 1;
        open.push(WorkerPathOpen(0, start));
        observerPerformanceCount("count.workerPath.fields");
    }
    bool query(CvUnitAI* unit, const CvPlot* destination, int& expanded) {
        CvSelectionGroup* group = unit->getGroup();
        int goal = plotIndex(destination);
        if (!pathDestValidForFlags(destination->getX_INLINE(), destination->getY_INLINE(), group, flags))
            return false;
        if (nodes[goal].closed) {
            observerPerformanceCount("count.workerPath.cachedTargets");
            return true;
        }
        return search(unit, goal, NULL, MAX_INT, expanded) >= 0;
    }
    int queryAny(CvUnitAI* unit, const std::vector<CvPlot*>& destinations, int maxTurns, int& expanded) {
        std::vector<char> goals(nodes.size(), 0);
        int best = -1;
        bool any = false;
        for (unsigned int i = 0; i < destinations.size(); ++i) {
            CvPlot* plot = destinations[i];
            if (!pathDestValidForFlags(plot->getX_INLINE(), plot->getY_INLINE(), unit->getGroup(), flags)) continue;
            int index = plotIndex(plot);
            goals[index] = 1;
            any = true;
            if (nodes[index].closed && nodes[index].turns <= maxTurns &&
                (best < 0 || nodes[index].cost < nodes[best].cost ||
                 (nodes[index].cost == nodes[best].cost && index < best))) best = index;
        }
        // Closed nodes precede the remaining queue in cost order, including
        // when a previous resource search has already explored these cities.
        if (best >= 0) return best;
        return any ? search(unit, -1, &goals, maxTurns, expanded) : -1;
    }
private:
    int search(CvUnitAI* unit, int goal, const std::vector<char>* goals, int maxTurns, int& expanded) {
        CvSelectionGroup* group = unit->getGroup();
        FAStarNode parent, child;
        while (!open.empty()) {
            WorkerPathOpen next = open.top();
            open.pop();
            WorkerPathNode& current = nodes[next.index];
            if (current.closed || current.cost != next.cost) continue;
            current.closed = true;
            ++expanded;
            CvPlot* from = GC.getMapINLINE().plotByIndexINLINE(next.index);
            copyNode(parent, from, current);
            // Land-worker departure validity is independent of the successor.
            // Check danger and movement permissions once, rather than per edge.
            if (pathValidForFlags(&parent, &parent, group, flags)) {
                for (int d = 0; d < NUM_DIRECTION_TYPES; ++d) {
                    CvPlot* to = plotDirection(from->getX_INLINE(), from->getY_INLINE(), (DirectionTypes)d);
                    if (!to) continue;
                    int index = plotIndex(to);
                    WorkerPathNode& candidate = nodes[index];
                    if (candidate.closed) continue;
                    child.m_iX = to->getX_INLINE();
                    child.m_iY = to->getY_INLINE();
                    // These callbacks need no engine finder for a noncombat
                    // worker and a noninitial node. Retain terrain/road costs,
                    // turn rollover, ownership penalties and feature damage.
                    int edge = pathCost(&parent, &child, 0, group, NULL);
                    if (current.cost > MAX_INT - edge) continue;
                    int cost = current.cost + edge;
                    if (cost >= candidate.cost) continue;
                    pathAdd(&parent, &child, ASNC_NEWADD, group, NULL);
                    candidate.cost = cost;
                    candidate.moves = child.m_iData1;
                    candidate.turns = child.m_iData2;
                    candidate.parent = next.index;
                    open.push(WorkerPathOpen(cost, index));
                }
            }
            // Expand the goal too: later queries may need to pass through it.
            if ((next.index == goal || (goals && (*goals)[next.index])) &&
                current.turns <= maxTurns) return next.index;
        }
        return -1;
    }
};

WorkerPathDecision* WorkerPathDecision::current = NULL;

WorkerPathDecision::WorkerPathDecision(CvUnitAI* unit)
    : m_unit(unit), m_group(unit->getGroup()), m_origin(unit->plot()),
      m_moves(unit->movesLeft()), m_previous(current), m_lastCached(false), m_lastEndTurn(NULL)
#if ARFC_ENABLE_REPORTING
      , m_capture(false), m_recordQueries(false), m_turn(GC.getGameINLINE().getGameTurn()),
      m_owner(unit->getOwnerINLINE()), m_id(unit->getID())
#endif
{
    current = this;
#if ARFC_ENABLE_REPORTING
    if (g_observerPerformance) {
        const char* capture = getenv("AWAKENED_RFC_CAPTURE_WORKER_PATHS");
        m_recordQueries = capture && strcmp(capture, "1") == 0
            && m_turn >= 150 && m_turn <= 350 && m_turn % 25 == 0;
    }
#endif
}

WorkerPathDecision::~WorkerPathDecision()
{
    // The unit may have died or changed groups while pushing its mission.
    // Destruction deliberately never dereferences it.
    for (unsigned int i = 0; i < m_fields.size(); ++i) delete m_fields[i];
    current = m_previous;
}

bool WorkerPathDecision::matches(const CvUnitAI* unit) const
{
    return m_unit == unit && !unit->isHuman() && unit->getDomainType() == DOMAIN_LAND
        && !unit->isCargo() && unit->getGroup() == m_group
        && m_group->getNumUnits() == 1 && !unit->canFight()
        && unit->plot() == m_origin && unit->movesLeft() == m_moves;
}

bool WorkerPathDecision::supports(int flags) const
{
    return (flags & ~(MOVE_SAFE_TERRITORY | MOVE_NO_ENEMY_TERRITORY | MOVE_IGNORE_DANGER)) == 0;
}

WorkerPathField* WorkerPathDecision::fieldForFlags(int flags)
{
    for (unsigned int i = 0; i < m_fields.size(); ++i)
        if (m_fields[i]->flags == flags) return m_fields[i];
    WorkerPathField* field = new WorkerPathField(m_unit, flags);
    m_fields.push_back(field);
    return field;
}

void WorkerPathDecision::setResult(WorkerPathField* field, int index)
{
    m_lastCached = true;
    m_lastEndTurn = NULL;
    if (index < 0) return;
    copyNode(m_lastNode, GC.getMapINLINE().plotByIndexINLINE(index), field->nodes[index]);
    // Match getPathEndTurnPlot without publishing a synthetic engine path.
    int end = index;
    while (field->nodes[end].turns > 1 && field->nodes[end].parent >= 0)
        end = field->nodes[end].parent;
    m_lastEndTurn = GC.getMapINLINE().plotByIndexINLINE(end);
}

CvPlot* WorkerPathDecision::queryAny(const std::vector<CvPlot*>& destinations, int flags, int maxTurns)
{
    OBSERVER_PERFORMANCE("workerPath.retreatQuery");
    WorkerPathField* field = fieldForFlags(flags);
    int expanded = 0;
    int index = field->queryAny(m_unit, destinations, maxTurns, expanded);
    observerPerformanceScope.addWork(expanded);
    setResult(field, index);
    return index >= 0 ? GC.getMapINLINE().plotByIndexINLINE(index) : NULL;
}

bool WorkerPathDecision::query(const CvPlot* destination, int flags, bool reuse, int* turns)
{
    OBSERVER_PERFORMANCE("workerPath.query");
#if ARFC_ENABLE_REPORTING
    LARGE_INTEGER started;
    if (m_recordQueries) QueryPerformanceCounter(&started);
#endif
    WorkerPathField* field = fieldForFlags(flags);
    int expanded = 0;
    bool success = field->query(m_unit, destination, expanded);
    observerPerformanceScope.addWork(expanded);
    setResult(field, success ? plotIndex(destination) : -1);
    if (turns) *turns = MAX_INT;
    if (success) {
        if (turns) *turns = m_lastNode.m_iData2;
    }
#if ARFC_ENABLE_REPORTING
    if (m_recordQueries) {
        LARGE_INTEGER ended, frequency;
        QueryPerformanceCounter(&ended);
        QueryPerformanceFrequency(&frequency);
        Query q;
        static const char* tasks[] = {
            "workerTask.AI_bestCityBuild", "workerTask.AI_improveBonus",
            "workerTask.AI_connectPlot", "workerTask.AI_improveLocalPlot",
            "workerTask.AI_nextCityToImprove", "workerTask.AI_irrigateTerritory",
            "workerTask.AI_fortTerritory", "workerTask.AI_routeTerritory",
            "workerTask.AI_routeCity", "workerTask.AI_improveCity",
            "workerTask.AI_load", "workerTask.AI_retreatToCity", "workerTask.AI_safety"
        };
        q.task = "other";
        for (unsigned int t = 0; t < sizeof(tasks) / sizeof(tasks[0]); ++t)
            if (observerPerformanceInScope(tasks[t])) { q.task = tasks[t]; break; }
        q.x = destination->getX_INLINE(); q.y = destination->getY_INLINE();
        q.flags = flags; q.turns = success ? m_lastNode.m_iData2 : -1;
        q.moves = success ? m_lastNode.m_iData1 : -1;
        q.expanded = expanded; q.success = success; q.reuse = reuse;
        q.seconds = double(ended.QuadPart - started.QuadPart) / double(frequency.QuadPart);
        m_queries.push_back(q);
        captureQueries();
    }
#endif
    return success;
}

#if ARFC_ENABLE_REPORTING
void WorkerPathDecision::captureQueries()
{
    // One nontrivial decision every 25 turns from turn 150. Captures are deliberately
    // separate from ordinary performance runs: exporting and dual execution
    // add substantial overhead to these sampled turns.
    static int capturedTurn = -1;
    static std::string capturedOutput;
    const char* output = getenv("AWAKENED_RFC_PERFORMANCE_OUTPUT");
    if (!output || !*output) return;
    if (capturedOutput != output || m_turn < capturedTurn) {
        capturedOutput = output;
        capturedTurn = -1;
    }
    bool beginning = false;
    if (!m_capture) {
        // Retreat decisions usually contain fewer than 16 queries. A costly
        // first query is representative too; do not require a large batch.
        if (m_turn < 150 || m_turn > 350 || m_turn % 25 || capturedTurn == m_turn) return;
        if (m_queries.size() < 4 && m_queries.back().expanded < 256) return;
        capturedTurn = m_turn;
        m_capture = true;
        beginning = true;
        std::string directory(output);
        directory = directory.substr(0, directory.find_last_of("\\/") + 1);
        char name[100];
        sprintf(name, "worker-path-t%d-p%d-u%d", m_turn, m_owner, m_id);
        m_captureBase = directory + name;
    }
    OBSERVER_PERFORMANCE("workerPath.capture");
    FILE* file = fopen((m_captureBase + "-queries.csv").c_str(), beginning ? "w" : "a");
    if (!file) return;
    if (beginning) fprintf(file, "task,x,y,flags,reuse,native_success,native_turns,native_moves,expanded,native_seconds,legacy_success,legacy_turns,legacy_moves,legacy_seconds\n");
    unsigned int first = beginning ? 0 : m_queries.size() - 1;
    for (unsigned int i = first; i < m_queries.size(); ++i) {
        const Query& q = m_queries[i];
        if (std::find(m_capturedFlags.begin(), m_capturedFlags.end(), q.flags) == m_capturedFlags.end()) {
            captureGraph(q.flags);
            m_capturedFlags.push_back(q.flags);
        }
        LARGE_INTEGER start, end, frequency;
        QueryPerformanceFrequency(&frequency);
        QueryPerformanceCounter(&start);
        int legacyTurns;
        bool success = m_unit->generatePath(GC.getMapINLINE().plotINLINE(q.x, q.y), q.flags, q.reuse, &legacyTurns);
        int moves = success ? m_unit->getPathLastNode()->m_iData1 : -1;
        QueryPerformanceCounter(&end);
        fprintf(file, "%s,%d,%d,%d,%d,%d,%d,%d,%d,%.9f,%d,%d,%d,%.9f\n", q.task, q.x, q.y, q.flags, q.reuse,
            q.success, q.turns, q.moves, q.expanded, q.seconds, success, success ? legacyTurns : -1, moves,
            double(end.QuadPart - start.QuadPart) / double(frequency.QuadPart));
    }
    fclose(file);
}

void WorkerPathDecision::captureGraph(int flags)
{
    char suffix[60];
    sprintf(suffix, "-flags%d.json", flags);
    FILE* file = fopen((m_captureBase + suffix).c_str(), "w");
    if (!file) return;
    CvMap& map = GC.getMapINLINE();
    fprintf(file, "{\"turn\":%d,\"owner\":%d,\"unit\":%d,\"width\":%d,\"height\":%d,\"wrap_x\":%d,\"wrap_y\":%d,\"origin\":%d,\"moves\":%d,\"max_moves\":%d,\"flags\":%d,\"movement_weight\":%d,\"step_weight\":%d,\"straight_weight\":%d,\"nodes\":[\n",
        m_turn, m_owner, m_id, map.getGridWidthINLINE(), map.getGridHeightINLINE(), map.isWrapXINLINE(), map.isWrapYINLINE(),
        plotIndex(m_origin), m_moves, m_unit->maxMoves(), flags, PATH_MOVEMENT_WEIGHT, PATH_STEP_WEIGHT, PATH_STRAIGHT_WEIGHT);
    FAStarNode parent;
    for (int i = 0; i < map.numPlotsINLINE(); ++i) {
        CvPlot* plot = map.plotByIndexINLINE(i);
        parent.m_iX = plot->getX_INLINE(); parent.m_iY = plot->getY_INLINE();
        parent.m_iData1 = 1; parent.m_iData2 = 1;
        bool throughNow = pathValidForFlags(&parent, &parent, m_group, flags) != 0;
        parent.m_iData1 = 0; parent.m_iData2 = 2;
        bool throughLater = pathValidForFlags(&parent, &parent, m_group, flags) != 0;
        bool destination = pathDestValidForFlags(plot->getX_INLINE(), plot->getY_INLINE(), m_group, flags) != 0;
        int penalty = plot->getTeam() != m_unit->getTeam() ? PATH_TERRITORY_WEIGHT : 0;
        if (GC.getPATH_DAMAGE_WEIGHT() != 0) {
            if (plot->getFeatureType() != NO_FEATURE)
                penalty += GC.getPATH_DAMAGE_WEIGHT() * std::max(0, GC.getFeatureInfo(plot->getFeatureType()).getTurnDamage()) / GC.getMAX_HIT_POINTS();
            if (plot->getExtraMovePathCost() > 0) penalty += PATH_MOVEMENT_WEIGHT * plot->getExtraMovePathCost();
        }
        fprintf(file, "%s[%d,%d,%d,%d,[", i ? ",\n" : "", throughNow, throughLater, destination, penalty);
        bool first = true;
        // Omit edges from plots which cannot be traversed in either state.
        if (throughNow || throughLater) for (int d = 0; d < NUM_DIRECTION_TYPES; ++d) {
            CvPlot* to = plotDirection(plot->getX_INLINE(), plot->getY_INLINE(), (DirectionTypes)d);
            if (!to) continue;
            int diagonal = plot->getX_INLINE() != to->getX_INLINE() && plot->getY_INLINE() != to->getY_INLINE();
            fprintf(file, "%s[%d,%d,%d]", first ? "" : ",", plotIndex(to), to->movementCost(m_unit, plot), diagonal);
            first = false;
        }
        fprintf(file, "]]");
    }
    fprintf(file, "\n]}\n");
    fclose(file);
}
#endif
