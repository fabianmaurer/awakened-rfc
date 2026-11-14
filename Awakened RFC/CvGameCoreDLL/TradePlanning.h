#ifndef TRADE_PLANNING_H
#define TRADE_PLANNING_H
#include <map>
class CvCity;

struct FoodTradeAttraction
{
    int population, wealth, happiness, health;
    FoodTradeAttraction(const CvCity* city, bool cache = true);
    bool operator==(const FoodTradeAttraction& other) const;
};

// One synchronous route update, including its city's nested updates. Never
// reused across a turn, civic transition, city mutation or save/load.
class TradePlanningCache
{
public:
    TradePlanningCache();
    ~TradePlanningCache();
    static TradePlanningCache* current;
    std::map<const CvCity*, bool> harbors;
    std::map<const CvCity*, FoodTradeAttraction> attractions;
private:
    TradePlanningCache* m_previous;
    TradePlanningCache(const TradePlanningCache&);
    TradePlanningCache& operator=(const TradePlanningCache&);
};

#endif
