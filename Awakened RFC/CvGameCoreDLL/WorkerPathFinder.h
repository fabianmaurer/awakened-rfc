#ifndef WORKER_PATH_FINDER_H
#define WORKER_PATH_FINDER_H

#include "Reporting.h"
#include "FAStarNode.h"
#include <string>
#include <vector>

class CvUnitAI;
class CvSelectionGroup;
class CvPlot;
class WorkerPathField;

// Candidate evaluation only. Missions still use the engine's pathfinder.
// A decision owns its fields; nothing survives movement, another unit's turn,
// a save/load, or a nested worker decision.
class WorkerPathDecision
{
public:
    explicit WorkerPathDecision(CvUnitAI* unit);
    ~WorkerPathDecision();
    static WorkerPathDecision* current;
    bool matches(const CvUnitAI* unit) const;
    bool supports(int flags) const;
    bool query(const CvPlot* destination, int flags, bool reuse, int* turns);
    CvPlot* queryAny(const std::vector<CvPlot*>& destinations, int flags, int maxTurns);
    FAStarNode* lastNode() { return m_lastCached ? &m_lastNode : NULL; }
    CvPlot* endTurnPlot() const { return m_lastEndTurn; }
    void useLegacy() { m_lastCached = false; }

private:
    WorkerPathDecision(const WorkerPathDecision&);
    WorkerPathDecision& operator=(const WorkerPathDecision&);
    CvUnitAI* m_unit;
    CvSelectionGroup* m_group;
    CvPlot* m_origin;
    int m_moves;
    WorkerPathDecision* m_previous;
    std::vector<WorkerPathField*> m_fields;
    WorkerPathField* fieldForFlags(int flags);
    void setResult(WorkerPathField* field, int index);
    FAStarNode m_lastNode;
    bool m_lastCached;
    CvPlot* m_lastEndTurn;
#if ARFC_ENABLE_REPORTING
    struct Query {
        const char* task;
        int x, y, flags, turns, moves, expanded;
        bool success, reuse;
        double seconds;
    };
    std::vector<Query> m_queries;
    bool m_capture, m_recordQueries;
    int m_turn, m_owner, m_id;
    std::string m_captureBase;
    std::vector<int> m_capturedFlags;
    void captureQueries();
    void captureGraph(int flags);
#endif
};

#endif
