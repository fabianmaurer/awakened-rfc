#ifndef OBSERVER_PERFORMANCE_H
#define OBSERVER_PERFORMANCE_H

// Process-local instrumentation, enabled only by authenticated observer autoplay.
extern bool g_observerPerformance;
void observerPerformanceStart();
void observerPerformanceFlush();
class ObserverPerformanceScope
{
public:
    ObserverPerformanceScope(const char* name);
    ~ObserverPerformanceScope();
private:
    const char* m_name;
    int m_turn;
    __int64 m_start;
    double m_children;
    ObserverPerformanceScope* m_parent;
};
#define OBSERVER_PERFORMANCE(name) ObserverPerformanceScope observerPerformanceScope(name)
#endif
