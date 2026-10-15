#ifndef OBSERVER_PERFORMANCE_H
#define OBSERVER_PERFORMANCE_H

// Process-local instrumentation, enabled only by authenticated observer autoplay.
extern bool g_observerPerformance;
void observerPerformanceStart();
void observerPerformanceFlush();
// Event counts and aggregate work, without a clock query for each event.
void observerPerformanceCount(const char* name, unsigned int work = 1);
bool observerPerformanceInScope(const char* name);
class ObserverPerformanceScope
{
public:
    ObserverPerformanceScope(const char* name);
    ~ObserverPerformanceScope();
    void addWork(unsigned int work = 1) { if (m_name) m_work += work; }
private:
    friend bool observerPerformanceInScope(const char* name);
    const char* m_name;
    int m_turn;
    __int64 m_start;
    double m_children;
    unsigned int m_work;
    ObserverPerformanceScope* m_parent;
};
#define OBSERVER_PERFORMANCE(name) ObserverPerformanceScope observerPerformanceScope(name)
#endif
