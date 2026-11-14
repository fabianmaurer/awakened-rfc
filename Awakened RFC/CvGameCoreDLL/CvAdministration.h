#ifndef CV_ADMINISTRATION_H
#define CV_ADMINISTRATION_H

class CvCity;
class CvPlayer;
class CvPlot;
namespace Administration
{
    void invalidateNetwork();
    bool penaltiesSuspended(const CvPlayer& player);
    int travelTime100(const CvCity& city);
    int travelTime100(const CvPlayer& player, const CvPlot& plot);
    int capitalTravelTime100(const CvPlayer& player, const CvPlot& plot);
    bool isReachable(const CvPlayer& player, const CvPlot& plot, bool founding = false);
    bool hasResidence(const CvCity& city);
    bool isResidenceBuilding(int building);
    int residenceCost100(const CvCity& city);
    int governingResidence(const CvCity& city);
    int effortWithoutResidence100(const CvCity& city);
    int goldChangeWithoutResidence100(const CvCity& city);
    int localModifier(const CvCity& city);
    int effort100(const CvCity& city);
    int capacity100(const CvPlayer& player);
    int totalEffort100(const CvPlayer& player);
    int overload100(const CvPlayer& player);
    int productionPercent(const CvPlayer& player);
    int civicModifier(const CvPlayer& player, int civic);
    int wonderModifier(int building);
    int religionModifier(const CvCity& city, int civic, int stateReligion);
    int religionEffort100(const CvPlayer& player, int civic, int stateReligion);
    int burdenValue(const CvPlayer& player, int effort, int capacity);
    int expansionWeight(const CvPlayer& player, const CvPlot& plot, int population, int local = 0);
    int infrastructureValue(const CvCity& city, int building);
    int purgeValue(const CvCity& city, int religion);
    int purgeHappinessChange(const CvCity& city, int religion);
}
#endif
