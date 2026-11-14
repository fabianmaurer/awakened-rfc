# Rhye's and Fall of Civilization - Religions management

from CvPythonExtensions import *
import ScenarioGeography as geo
import CvUtil
import PyHelpers       
import Popup
import cPickle as pickle     	
import Consts as con
import RFCUtils

# globals
gc = CyGlobalContext()
PyPlayer = PyHelpers.PyPlayer
utils = RFCUtils.RFCUtils()

### Constants ###

iArabia = con.iArabia
iNumPlayers = con.iNumPlayers
iBarbarian = con.iBarbarian
iIndependent = con.iIndependent
iIndependent2 = con.iIndependent2
iCeltia = con.iCeltia

geo.bindTime(globals(), 'i2250BC', con._timeValues['i2250BC'])
geo.bindTime(globals(), 'i2085BC', con._timeValues['i2085BC'])
geo.bindTime(globals(), 'i1800BC', con._timeValues['i1800BC'])
geo.bindTime(globals(), 'i600BC', con._timeValues['i600BC'])
geo.bindTime(globals(), 'i483BC', con._timeValues['i483BC'])
geo.bindTime(globals(), 'i479BC', con._timeValues['i479BC'])
geo.bindTime(globals(), 'i33AD', con._timeValues['i33AD'])
geo.bindTime(globals(), 'i622AD', con._timeValues['i622AD'])



# initialise religion variables to religion indices from XML
iJudaism = con.iJudaism 
iChristianity = con.iChristianity
iIslam = con.iIslam
iHinduism = con.iHinduism
iBuddhism = con.iBuddhism
iConfucianism = con.iConfucianism
iTaoism = con.iTaoism

iMissionary_Jewish = con.iJewishMissionary
iMissionary_Christian = con.iChristianMissionary
iMissionary_Islamic = con.iIslamicMissionary
iMissionary_Hindu = con.iHinduMissionary
iMissionary_Buddhist = con.iBuddhistMissionary
iMissionary_Confucian = con.iConfucianMissionary
iMissionary_Taoist = con.iTaoistMissionary


# initialise coordinates

geo.bind(globals(), 'tJerusalem', 'Religions.tJerusalem')
geo.bind(globals(), 'tJewishTL', 'Religions.tJewishTL')
geo.bind(globals(), 'tJewishBR', 'Religions.tJewishBR')
geo.bind(globals(), 'tLevantTL', 'Religions.tLevantTL')
geo.bind(globals(), 'tLevantBR', 'Religions.tLevantBR')
geo.bind(globals(), 'tArabiaTL', 'Religions.tArabiaTL')
geo.bind(globals(), 'tArabiaBR', 'Religions.tArabiaBR')
geo.bind(globals(), 'tNorthIndiaTL', 'Religions.tNorthIndiaTL')
geo.bind(globals(), 'tNorthIndiaBR', 'Religions.tNorthIndiaBR')
geo.bind(globals(), 'tChinaTL', 'Religions.tChinaTL')
geo.bind(globals(), 'tChinaBR', 'Religions.tChinaBR')
geo.bind(globals(), 'tVaranasiTL', 'Religions.tVaranasiTL')
geo.bind(globals(), 'tVaranasiBR', 'Religions.tVaranasiBR')
geo.bind(globals(), 'tBodhgayaTL', 'Religions.tBodhgayaTL')
geo.bind(globals(), 'tBodhgayaBR', 'Religions.tBodhgayaBR')
geo.bind(globals(), 'tBuddhistTL', 'Religions.tBuddhistTL')
geo.bind(globals(), 'tBuddhistBR', 'Religions.tBuddhistBR')
geo.bind(globals(), 'tHenanTL', 'Religions.tHenanTL')
geo.bind(globals(), 'tHenanBR', 'Religions.tHenanBR')
geo.bind(globals(), 'tSEAsiaTL', 'Religions.tSEAsiaTL')
geo.bind(globals(), 'tSEAsiaBR', 'Religions.tSEAsiaBR')
geo.bind(globals(), 'tAsiaTL', 'Religions.tAsiaTL')
geo.bind(globals(), 'tAsiaBR', 'Religions.tAsiaBR')
geo.bind(globals(), 'tEuropeTL', 'Religions.tEuropeTL')
geo.bind(globals(), 'tEuropeBR', 'Religions.tEuropeBR')
geo.bind(globals(), 'tQufuTL', 'Religions.tQufuTL')
geo.bind(globals(), 'tQufuBR', 'Religions.tQufuBR')
geo.bind(globals(), 'tMecca', 'Religions.tMecca')



class Religions:

##################################################
### Secure storage & retrieval of script data ###
################################################
		
        def getSeed( self ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['iSeed']

        def setSeed( self ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['iSeed'] = utils.getFakeRandNum(100, 'Seed for random delay')
                gc.getGame().setScriptData( pickle.dumps(scriptDict) )        


#######################################
### Main methods (Event-Triggered) ###
#####################################  

        def setup(self):
                self.setSeed()
                scriptDict = pickle.loads(gc.getGame().getScriptData())
                scriptDict['bFirstTempleGranted'] = False
                gc.getGame().setScriptData(pickle.dumps(scriptDict))
                self.grantFirstTemple()
                

       	
        def grantFirstTemple(self):
                # Traditional completion of Solomon's Temple, c. 957 BC.
                # Later scenarios receive the grant at setup; no rebuilt reward.
                game = gc.getGame()
                if game.getGameTurnYear() < -957:
                        return
                scriptDict = pickle.loads(game.getScriptData())
                if scriptDict.get('bFirstTempleGranted', False):
                        return
                iShrine = gc.getInfoTypeForString("BUILDING_JEWISH_SHRINE")
                iClass = gc.getBuildingInfo(iShrine).getBuildingClassType()
                if game.getBuildingClassCreatedCount(iClass) > 0:
                        scriptDict['bFirstTempleGranted'] = True
                        game.setScriptData(pickle.dumps(scriptDict))
                        return
                city = gc.getMap().plot(tJerusalem[0], tJerusalem[1]).getPlotCity()
                if city.isNone() or not city.isHasReligion(iJudaism):
                        return
                scriptDict['bFirstTempleGranted'] = True
                game.setScriptData(pickle.dumps(scriptDict))
                city.setNumRealBuilding(iShrine, 1)

        def checkTurn(self, iGameTurn):
                self.grantFirstTemple()
                self.checkRegionalFounding()

        def checkRegionalFounding(self):
                game = gc.getGame()
                year = game.getGameTurnYear()
                # Religion, earliest year, fallback year, technology, region, preferred area, other holy city.
                rules = (
                        (iJudaism, -1500, -1000, "TECH_MONOTHEISM", tLevantTL, tLevantBR, tJerusalem, tJerusalem, -1),
                        (iChristianity, 33, 200, "TECH_THEOLOGY", tLevantTL, tLevantBR, tJerusalem, tJerusalem, -1),
                        (iIslam, 622, 650, "TECH_DIVINE_RIGHT", tArabiaTL, tArabiaBR, tMecca, tMecca, -1),
                        (iHinduism, -1500, -1000, "TECH_MEDITATION", tNorthIndiaTL, tNorthIndiaBR, tVaranasiTL, tVaranasiBR, -1),
                        (iBuddhism, -500, -200, "TECH_PRIESTHOOD", tNorthIndiaTL, tNorthIndiaBR, tBodhgayaTL, tBodhgayaBR, iHinduism),
                        (iConfucianism, -500, -200, "TECH_MATHEMATICS", tChinaTL, tChinaBR, tHenanTL, tHenanBR, -1),
                        (iTaoism, -400, -200, "TECH_CALENDAR", tChinaTL, tChinaBR, tHenanTL, tHenanBR, iConfucianism),
                )
                for religion, start, fallback, techName, lower, upper, preferredLower, preferredUpper, other in rules:
                        if year < start or game.isReligionFounded(religion):
                                continue
                        tech = gc.getInfoTypeForString(techName)
                        bestCity = None
                        bestRank = None
                        for x in range(lower[0], upper[0] + 1):
                                for y in range(lower[1], upper[1] + 1):
                                        city = gc.getMap().plot(x, y).getPlotCity()
                                        if city.isNone():
                                                continue
                                        player = gc.getPlayer(city.getOwner())
                                        if year < fallback and not gc.getTeam(player.getTeam()).isHasTech(tech):
                                                continue
                                        if religion == iChristianity and year < fallback and (x, y) != tJerusalem and not city.isHasReligion(iJudaism):
                                                continue
                                        distinct = other < 0 or not city.isHolyCityByType(other)
                                        preferred = preferredLower[0] <= x <= preferredUpper[0] and preferredLower[1] <= y <= preferredUpper[1]
                                        jewish = religion == iChristianity and city.isHasReligion(iJudaism)
                                        rank = (distinct, preferred, jewish, city.getPopulation())
                                        if bestRank is None or rank > bestRank:
                                                bestRank = rank
                                                bestCity = city
                        if bestCity is not None:
                                game.setHolyCity(religion, bestCity, True)
                                coords = (bestCity.getX(), bestCity.getY())
                                if religion == iChristianity:
                                        self.spreadReligion(coords, 3, iMissionary_Christian)
                                elif religion == iIslam and bestCity.getOwner() == iArabia and not gc.getPlayer(iArabia).isHuman():
                                        self.spreadReligion(coords, 4, iMissionary_Islamic)

        def foundReligion(self, tPlot, iReligion):
                if (tPlot != False):
                        plot = gc.getMap().plot( tPlot[0], tPlot[1] )                
                        if (not plot.getPlotCity().isNone()):
                                #if (gc.getPlayer(city.getOwner()).isHuman() == 0):
                                #if (not gc.getGame().isReligionFounded(iReligion)):
                                gc.getGame().setHolyCity(iReligion, plot.getPlotCity(), True)
                                return True
                        else:
                                return False
                            
                return False


        def selectRandomCityCiv(self, iCiv):
                if (gc.getPlayer(iCiv).isAlive()):
                        cityList = []
                        for pyCity in PyPlayer(iCiv).getCityList():
                                cityList.append(pyCity.GetCy())
                        iCity = utils.getFakeRandNum(len(cityList), 'random city')
                        city = cityList[iCity]
                        return (city.getX(), city.getY())
                return False
            

        def selectRandomCityArea(self, tTopLeft, tBottomRight):
                cityList = []
                for x in range(tTopLeft[0], tBottomRight[0]+1):
                        for y in range(tTopLeft[1], tBottomRight[1]+1):
                                pCurrent = gc.getMap().plot( x, y )
                                if ( pCurrent.isCity()):
                                        cityList.append(pCurrent.getPlotCity())
                if (cityList):
                        iCity = utils.getFakeRandNum(len(cityList), 'random city')
                        city = cityList[iCity]
                        return (city.getX(), city.getY())
                else:
                        return False


        def selectRandomCityAreaCiv(self, tTopLeft, tBottomRight, iCiv):
                cityList = []
                for x in range(tTopLeft[0], tBottomRight[0]+1):
                        for y in range(tTopLeft[1], tBottomRight[1]+1):
                                pCurrent = gc.getMap().plot( x, y )
                                if ( pCurrent.isCity()):
                                        if (pCurrent.getPlotCity().getOwner() == iCiv):
                                                cityList.append(pCurrent.getPlotCity())
                if (cityList):
                        iCity = utils.getFakeRandNum(len(cityList), 'random city')
                        city = cityList[iCity]
                        return (city.getX(), city.getY())
                else:
                        return False



        def selectRandomCityReligion(self, iReligion):
                if (gc.getGame().isReligionFounded(iReligion)):
                        cityList = []
                        for iPlayer in range(iNumPlayers):
                                for pyCity in PyPlayer(iPlayer).getCityList():
                                        if pyCity.GetCy().isHasReligion(iReligion):
                                                cityList.append(pyCity.GetCy())                                        
                        iCity = utils.getFakeRandNum(len(cityList), 'random city')
                        city = cityList[iCity]
                        return (city.getX(), city.getY())
                return False


        def selectRandomCityReligionCiv(self, iReligion, iCiv):
                if (gc.getGame().isReligionFounded(iReligion)):
                        cityList = []
                        for iPlayer in range(iNumPlayers):
                                for pyCity in PyPlayer(iPlayer).getCityList():
                                        if pyCity.GetCy().isHasReligion(iReligion):
                                                if (pyCity.GetCy().getOwner() == iCiv):                            
                                                        cityList.append(pyCity.GetCy())
                        if (cityList):
                                iCity = utils.getFakeRandNum(len(cityList), 'random city')
                                city = cityList[iCity]
                                return (city.getX(), city.getY())
                return False


        def spreadReligion(self, tCoords, iNum, iMissionary):
                city = gc.getMap().plot( tCoords[0], tCoords[1] ).getPlotCity()
                #print city
                #print city.getOwner()
                utils.makeUnit(iMissionary, city.getOwner(), tCoords, iNum)


                    
