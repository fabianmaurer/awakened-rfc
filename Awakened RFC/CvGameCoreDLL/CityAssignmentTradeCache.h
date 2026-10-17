#ifndef CITY_ASSIGNMENT_TRADE_CACHE_H
#define CITY_ASSIGNMENT_TRADE_CACHE_H

#include <map>
class CvCity;

// Infrastructure is invariant while one city reassigns citizens. Cache only
// connectivity/efficiency, never food amounts: export caps change with yields.
// A stack lifetime prevents stale results across any game-state changes.
class CityAssignmentTradeCache
{
public:
    CityAssignmentTradeCache();
    ~CityAssignmentTradeCache();
private:
    friend class CvCity;
    typedef std::pair<const CvCity*, const CvCity*> Route;
    typedef std::map<Route, int> Efficiencies;
    Efficiencies m_efficiencies;
    CityAssignmentTradeCache* m_previous;
    static CityAssignmentTradeCache* s_active;
    CityAssignmentTradeCache(const CityAssignmentTradeCache&);
    CityAssignmentTradeCache& operator=(const CityAssignmentTradeCache&);
};
#endif
