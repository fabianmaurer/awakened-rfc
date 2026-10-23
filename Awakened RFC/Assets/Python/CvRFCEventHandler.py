from CvPythonExtensions import *
import CvUtil
import CvEventManager #Mercenaries
import sys #Mercenaries
import PyHelpers 
import CvMainInterface #Mercenaries
#import CvConfigParser #Mercenaries #Rhye
import Popup as PyPopup 

import StoredData
import RiseAndFall        
import Barbs                
import Religions        
import Resources        
import CityNameManager  
import UniquePowers     
import AIWars           
import Congresses
import Consts as con
import Scenario1453AD
import Scenario900AD
import RFCUtils
utils = RFCUtils.RFCUtils()
import CvScreenEnums #Mercenaries, Rhye
import Victory
import Stability
import Plague
import Communications
import Slavery
        
gc = CyGlobalContext()        
#iBetrayalCheaters = 15


#Rhye - start
iEgypt = con.iEgypt
iIndia = con.iIndia
iChina = con.iChina
iBabylonia = con.iBabylonia
iGreece = con.iGreece
iPersia = con.iPersia
iCarthage = con.iCarthage
iRome = con.iRome
iJapan = con.iJapan
iEthiopia = con.iEthiopia
iMaya = con.iMaya
iVikings = con.iVikings
iArabia = con.iArabia
iKhmer = con.iKhmer
iSpain = con.iSpain
iFrance = con.iFrance
iEngland = con.iEngland
iGermany = con.iGermany
iRussia = con.iRussia
iNetherlands = con.iNetherlands
iHolland = con.iHolland
iMali = con.iMali
iPortugal = con.iPortugal
iInca = con.iInca
iMongolia = con.iMongolia
iAztecs = con.iAztecs
iTurkey = con.iTurkey
iAmerica = con.iAmerica
iNumPlayers = con.iNumPlayers
iNumMajorPlayers = con.iNumMajorPlayers
iNumActivePlayers = con.iNumActivePlayers
iIndependent = con.iIndependent
iIndependent2 = con.iIndependent2
iNative = con.iNative
iCeltia = con.iCeltia
iBarbarian = con.iBarbarian
iNumTotalPlayers = con.iNumTotalPlayers
#Rhye - end












###################################################
class CvRFCEventHandler:




        def __init__(self, eventManager):

                self.EventKeyDown=6 #Mercenaries

                # initialize base class
                eventManager.addEventHandler("GameStart", self.onGameStart) #Stability
                eventManager.addEventHandler("BeginGameTurn", self.onBeginGameTurn) #Stability
                eventManager.addEventHandler("cityAcquired", self.onCityAcquired) #Stability
                eventManager.addEventHandler("cityRazed", self.onCityRazed) #Stability
                eventManager.addEventHandler("cityBuilt", self.onCityBuilt) #Stability
                eventManager.addEventHandler("combatResult", self.onCombatResult) #Stability
                #eventManager.addEventHandler("changeWar", self.onChangeWar)
                eventManager.addEventHandler("religionFounded",self.onReligionFounded) #Victory
                eventManager.addEventHandler("buildingBuilt",self.onBuildingBuilt) #Victory
                eventManager.addEventHandler("projectBuilt",self.onProjectBuilt) #Victory
                eventManager.addEventHandler("BeginPlayerTurn", self.onBeginPlayerTurn) 
                eventManager.addEventHandler("EndPlayerTurn", self.onEndPlayerTurn)
                eventManager.addEventHandler("EndGameTurn", self.onEndGameTurn) #Stability
                eventManager.addEventHandler("kbdEvent",self.onKbdEvent) 
                eventManager.addEventHandler("techAcquired",self.onTechAcquired) #Stability
                #eventManager.addEventHandler("improvementDestroyed",self.onImprovementDestroyed) #Stability
                eventManager.addEventHandler("religionSpread",self.onReligionSpread) #Stability
                eventManager.addEventHandler("firstContact",self.onFirstContact)
                eventManager.addEventHandler("corporationFounded",self.onCorporationFounded) #Stability
             


               
                self.eventManager = eventManager

                self.data = StoredData.StoredData()
                self.rnf = RiseAndFall.RiseAndFall()
                self.barb = Barbs.Barbs()
                self.rel = Religions.Religions()
                self.res = Resources.Resources()
                self.cnm = CityNameManager.CityNameManager()
                self.up = UniquePowers.UniquePowers()
                self.aiw = AIWars.AIWars()
                self.cong = Congresses.Congresses()
                self.vic = Victory.Victory()
                self.sta = Stability.Stability()
                self.pla = Plague.Plague()
                self.com = Communications.Communications()
                self.slave = Slavery.slavery
                
     

        def onGameStart(self, argsList):
                'Called at the start of the game'
                self.data.setupScriptData()
                self.rnf.setup()
                import Korea
                Korea.setup(self.vic)
                import NativeAmerica
                NativeAmerica.setup()
                self.rel.setup()
                self.pla.setup()
                self.sta.setup()
                self.aiw.setup()
                self.rnf.warOnSpawn()

                
                return 0


        def onCityAcquired(self, argsList):
                #'City Acquired'
                owner,playerType,city,bConquest,bTrade = argsList
                #CvUtil.pyPrint('City Acquired Event: %s' %(city.getName()))
                self.slave.onCityAcquired(owner, playerType, city, bConquest, bTrade)
                self.cnm.renameCities(city, playerType)
                
                if (playerType == con.iTurkey):
                        self.up.turkishUP(city)

                if (playerType < iNumMajorPlayers):
                         utils.spreadMajorCulture(playerType, city.getX(), city.getY())

                self.sta.onCityAcquired(owner,playerType,city,bConquest,bTrade)

                # Voluntary cession to the Pope is not a Byzantine military collapse.
                #kill byzantium
                if (gc.getPlayer(con.iCeltia).getCivilizationType() == 4 and
                    not (bTrade and not bConquest and gc.getGame().isPapalState(playerType))):  #late start condition (RFCMP)
                        if (owner == iCeltia and gc.getPlayer(iCeltia).isAlive()):
                                if ((city.getX() == 68 and city.getY() == 45) or gc.getPlayer(iCeltia).getNumCities() <= 2): #constantinopolis captured or empire size <=2
                                        print ("killed Byzantium")
                                        utils.killAndFragmentCiv(iCeltia, iIndependent, iIndependent2, -1, False)

#RFCMP                
##                if (bConquest):
##                        #self.rnf.collapseCapitals(owner, city, playerType)
##                        if (owner == utils.getHumanID() and playerType != con.iBarbarian):
##                                self.rnf.collapseHuman(owner, city, playerType)
##                        #print ("exile data:", self.rnf.getExileData(0), city.getX(), self.rnf.getExileData(1), city.getY(), self.rnf.getExileData(2))
##                        if (self.rnf.getExileData(0) == city.getX() and self.rnf.getExileData(1) == city.getY()):
##                                if (playerType == utils.getHumanID() and self.rnf.getExileData(2) != -1):
##                                        self.rnf.escape(city)
                if (bTrade):
                        for i in range (con.iScotlandYard +1 - con.iHeroicEpic):
                                iNationalWonder = i + con.iHeroicEpic
                                if (city.hasBuilding(iNationalWonder)):
                                        city.setHasRealBuilding((iNationalWonder), False)

                self.pla.onCityAcquired(owner,playerType,city) #Plague

                self.com.onCityAcquired(city) #Communications

                self.vic.onCityAcquired(owner, playerType, bConquest) #Victory
                
                return 0

        def onCityRazed(self, argsList):
                #'City Razed'
                city, iPlayer = argsList

                self.sta.onCityRazed(city.getOwner(),iPlayer,city)
		
                if (iPlayer == con.iMongolia):
                        self.up.setLatestRazeData(0, gc.getGame().getGameTurn())
                        owner = city.getOwner()
                        if (city.getOwner() == iPlayer):
                                if (city.getPreviousOwner() != -1):
                                        owner = city.getPreviousOwner()                        
                        self.up.setLatestRazeData(1, owner)
                        self.up.setLatestRazeData(2, city.getPopulation())
                        self.up.setLatestRazeData(3, city.getX())
                        self.up.setLatestRazeData(4, city.getY())
                        print ("city.getPopulation()", city.getPopulation())
                        print ("prev", city.getPreviousOwner(), "curr", city.getOwner())
                        self.up.setMongolAI()

                self.pla.onCityRazed(city,iPlayer) #Plague
                        
                if (iPlayer == con.iMongolia):
                        self.vic.onCityRazed(iPlayer) #Victory



        def onCityBuilt(self, argsList):
                'City Built'
                city = argsList[0]
                
                iOwner = city.getOwner()
                
                if (iOwner < con.iNumActivePlayers): 
                        self.cnm.assignName(city)


                #Rhye - delete culture of barbs and minor civs to prevent weird unhappiness
                pCurrent = gc.getMap().plot( city.getX(), city.getY() )
                for i in range(con.iNumTotalPlayers - con.iNumActivePlayers):
                        iMinorCiv = i + con.iNumActivePlayers
                        pCurrent.setCulture(iMinorCiv, 0, True)
                pCurrent.setCulture(con.iBarbarian, 0, True)

                if (iOwner < iNumMajorPlayers):
                        utils.spreadMajorCulture(iOwner, city.getX(), city.getY())


                if (iOwner == con.iTurkey):
                        self.up.turkishUP(city)


                if (self.vic.getNewWorld(0) == -1):
                        if (iOwner not in con.lCivGroups[5] and iOwner < iNumActivePlayers):
                                if (city.getX() >= con.tAmericasTL[0] and city.getX() <= con.tAmericasBR[0] and city.getY() >= con.tAmericasTL[1] and city.getY() <= con.tAmericasBR[1]):
                                        self.vic.setNewWorld(0, iOwner)
                                        if (iOwner != iVikings):
                                                self.vic.setGoal(iVikings, 2, 0)
                                        if (iOwner != iSpain):
                                                self.vic.setGoal(iSpain, 0, 0) 

                if (iOwner == con.iRussia or \
                    iOwner == con.iFrance or \
                    iOwner == con.iEngland or \
                    iOwner == con.iSpain or \
                    #iOwner == con.iCarthage or \
                    iOwner == con.iVikings or \
                    iOwner == con.iPortugal or \
                    iOwner == con.iNetherlands):    
                        self.vic.onCityBuilt(city, iOwner) #Victory

                if (iOwner < con.iNumPlayers):
                        self.sta.onCityBuilt(iOwner, city.getX(), city.getY() )

        def onCombatResult(self, argsList):
                self.up.aztecUP(argsList)
                self.vic.onCombatResult(argsList)
                self.sta.onCombatResult(argsList)
                self.rnf.immuneMode(argsList)



##        def onChangeWar(self, argsList):
##                print ("No cheaters1")
##                if (bIsWar):
##                        print ("No cheaters2")
##                        if (argsList[1] == utils.getHumanID() and gc.getGame().getGameTurn() <= con.tBirth[argsList[1]] + iBetrayalCheaters):
##                                print ("No cheaters3")
##                                self.rnf.setNewCivFlip(argsList[1])
##                                self.rnf.setTempTopLeft(rnf.tCoreAreasTL[argsList[1]])
##                                self.rnf.setTempBottomRight(rnf.tCoreAreasBR[argsList[1]])
##                                self.rnf.setBetrayalTurns(rnf.iBetrayalPeriod)
##                                self.rnf.initBetrayal()



        def onReligionFounded(self, argsList):
                'Religion Founded'
                iReligion, iFounder = argsList

                if (gc.getGame().getStartTurn() != 0 and (gc.getGame().getGameTurn() == 181 or gc.getGame().getGameTurn() == 87 or (Scenario1453AD.isScenario() and gc.getGame().getGameTurn() == Scenario1453AD.START_TURN) or (Scenario900AD.isScenario() and gc.getGame().getGameTurn() == Scenario900AD.START_TURN))): #late start condition (RFCMP)
                        return
        
                self.vic.onReligionFounded(iReligion, iFounder)
        
                if (iFounder < con.iNumPlayers):
                        self.sta.onReligionFounded(iFounder)


	def onCorporationFounded(self, argsList):
		'Corporation Founded'
		iCorporation, iFounder = argsList
		#player = PyPlayer(iFounder)
		
                if (iFounder < con.iNumPlayers):
                        self.sta.onCorporationFounded(iFounder)


                        

        def onBuildingBuilt(self, argsList):
                city, iBuildingType = argsList
                self.vic.onBuildingBuilt(city.getOwner(), iBuildingType)
                if (city.getOwner() < con.iNumPlayers):
                        self.sta.onBuildingBuilt(city.getOwner(), iBuildingType, city)
                        self.com.onBuildingBuilt(city.getOwner(), iBuildingType, city)

        def onProjectBuilt(self, argsList):
                city, iProjectType = argsList
                self.vic.onProjectBuilt(city.getOwner(), iProjectType)
                if (city.getOwner() < con.iNumPlayers):
                        self.sta.onProjectBuilt(city.getOwner(), iProjectType)

        def onImprovementDestroyed(self, argsList):
                pass
                #iImprovement, iOwner, iX, iY = argsList
                #if (iOwner < con.iNumPlayers):
                #        self.sta.onImprovementDestroyed(iOwner)           
                
        def onBeginGameTurn(self, argsList):
                iGameTurn = argsList[0]

                print ("iGameTurn", iGameTurn)
                #self.printDebug(iGameTurn) #RFCMP

                #debug - stop autoplay
                #utils.makeUnit(con.iAxeman, con.iAmerica, (0,0), 1)

                
                self.rnf.checkTurn(iGameTurn)
                self.barb.checkTurn(iGameTurn)
                self.rel.checkTurn(iGameTurn)
                self.res.checkTurn(iGameTurn)
                self.up.checkTurn(iGameTurn)
                self.aiw.checkTurn(iGameTurn)
                #self.cong.checkTurn(iGameTurn)
                self.pla.checkTurn(iGameTurn)
                self.vic.checkTurn(iGameTurn)
                self.sta.checkTurn(iGameTurn)
                self.com.checkTurn(iGameTurn)
     
                return 0



        def onBeginPlayerTurn(self, argsList):        
                iGameTurn, iPlayer = argsList

                # Democracy holds an election every ten turns. The synchronized game RNG
                # selects one non-government civic column and one available replacement.
                pPlayer = gc.getPlayer(iPlayer)
                iDemocracy = CvUtil.findInfoTypeNum(gc.getCivicInfo, gc.getNumCivicInfos(), 'CIVIC_DEMOCRACY')
                if (pPlayer.isAlive() and iGameTurn > 0 and iGameTurn % 10 == 0 and pPlayer.getCivics(0) == iDemocracy):
                        lEligibleColumns = []
                        for iOption in range(1, gc.getNumCivicOptionInfos()):
                                lAvailableCivics = []
                                for iCivic in range(gc.getNumCivicInfos()):
                                        if (gc.getCivicInfo(iCivic).getCivicOptionType() == iOption and iCivic != pPlayer.getCivics(iOption) and pPlayer.canDoCivics(iCivic)):
                                                lAvailableCivics.append(iCivic)
                                if (len(lAvailableCivics) > 0):
                                        lEligibleColumns.append((iOption, lAvailableCivics))
                        if (len(lEligibleColumns) > 0):
                                iColumn = gc.getGame().getSorenRandNum(len(lEligibleColumns), "Democracy election civic column")
                                iCivicOption, lAvailableCivics = lEligibleColumns[iColumn]
                                iNewCivic = lAvailableCivics[gc.getGame().getSorenRandNum(len(lAvailableCivics), "Democracy election civic result")]
                                pPlayer.setCivics(iCivicOption, iNewCivic)
                                if (pPlayer.isHuman()):
                                        szMessage = CyTranslator().getText("TXT_KEY_RFCMP_DEMOCRACY_ELECTION", (gc.getCivicOptionInfo(iCivicOption).getDescription(), gc.getCivicInfo(iNewCivic).getDescription()))
                                        CyInterface().addMessage(iPlayer, True, con.iDuration, szMessage, "", 0, "", ColorTypes(con.iWhite), -1, -1, True, True)
                                        # The election already applies in synchronized state. This
                                        # one-button announcement only acknowledges its result.
                                        civicInfo = gc.getCivicInfo(iNewCivic)
                                        popup = CyPopupInfo()
                                        popup.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                                        popup.setData1(iNewCivic)
                                        popup.setData3(7626)
                                        popup.setText(CyTranslator().getText("TXT_KEY_RFCMP_ELECTION_" + civicInfo.getType().replace("CIVIC_", ""), ()))
                                        popup.addPythonButton(CyTranslator().getText("TXT_KEY_RFCMP_ELECTION_ADOPT", (civicInfo.getDescription(),)), civicInfo.getButton())
                                        popup.addPopup(iPlayer)
                
                #print ("PLAYER", iPlayer)
                #if (iPlayer == con.iMongolia):
                #        if (iGameTurn == self.up.getLatestRazeData(0) +1):
                #                self.up.setMongolAI()
                
                #debug - stop autoplay
                #utils.makeUnit(con.iAxeman, iAmerica, (0,0), 1)

                if (self.rnf.getDeleteMode(0) != -1):
                        self.rnf.deleteMode(iPlayer)
                        
                self.pla.checkPlayerTurn(iGameTurn, iPlayer)

                if (gc.getPlayer(iPlayer).isAlive()):
                        self.vic.checkPlayerTurn(iGameTurn, iPlayer)


                if (gc.getPlayer(iPlayer).isAlive() and iPlayer < con.iNumPlayers and gc.getPlayer(iPlayer).getNumCities() > 0):
                        self.sta.updateBaseStability(iGameTurn, iPlayer)

                if (gc.getPlayer(iPlayer).isAlive() and iPlayer < con.iNumPlayers and not gc.getPlayer(iPlayer).isHuman()):
                        self.rnf.checkPlayerTurn(iGameTurn, iPlayer) #for leaders switch

        
        
        def onEndPlayerTurn(self, argsList):

                iGameTurn, iPlayer = argsList
                # CvPlayer.doTurn fires this after city updates, before input
                # resumes. Expired slaves must not create a stale decision.
                self.slave.checkPlayerTurn(iPlayer)


        def onEndGameTurn(self, argsList):
            
                iGameTurn = argsList[0]
                self.sta.checkImplosion(iGameTurn)


        def onReligionSpread(self, argsList):
            
                iReligion, iOwner, pSpreadCity = argsList
                self.sta.onReligionSpread(iReligion, iOwner)             

        def onFirstContact(self, argsList):
                # WorldBuilder can establish contacts while placing cities,
                # before onGameStart initializes RFC's pickled script data.
                # Check initialization state rather than a scenario's date.
                game = gc.getGame()
                if not game.isFinalInitialized() or not game.getScriptData():
                        return

                iTeamX,iHasMetTeamY = argsList
                self.rnf.onFirstContact(iTeamX, iHasMetTeamY)
                self.pla.onFirstContact(iTeamX, iHasMetTeamY)

        #Rhye - start
        def onTechAcquired(self, argsList):

                #print ("onTechAcquired", argsList)
                iPlayer = argsList[2]
                
                if (gc.getGame().getStartTurn() != 0 and (gc.getGame().getGameTurn() == 181 or gc.getGame().getGameTurn() == 87 or (Scenario1453AD.isScenario() and gc.getGame().getGameTurn() == Scenario1453AD.START_TURN) or (Scenario900AD.isScenario() and gc.getGame().getGameTurn() == Scenario900AD.START_TURN))): #late start condition (RFCMP)
                        return
                
                if (gc.getGame().getGameTurn() > con.tBirth[iPlayer]):                    
                        if (iPlayer == con.iGreece or \
                            iPlayer == con.iJapan or \
                            iPlayer == con.iMaya or \
                            iPlayer == con.iEngland or \
                            iPlayer == con.iGermany or \
                            iPlayer == con.iAztecs or \
                            iPlayer == con.iBabylonia):                            
                                self.vic.onTechAcquired(argsList[0], argsList[2])
                        self.cnm.onTechAcquired(argsList[2])
                
                if (gc.getPlayer(iPlayer).isAlive() and gc.getGame().getGameTurn() > con.tBirth[iPlayer] and iPlayer < con.iNumPlayers):
                        self.sta.onTechAcquired(argsList[0], argsList[2])

                        if (gc.getGame().getGameTurn() > con.i1700AD):
                                self.aiw.forgetMemory(argsList[0], argsList[2])

                if (argsList[0] == con.iAstronomy):
                        if (iPlayer == con.iSpain or \
                            iPlayer == con.iFrance or \
                            iPlayer == con.iEngland or \
                            iPlayer == con.iGermany or \
                            iPlayer == con.iVikings or \
                            iPlayer == con.iNetherlands or \
                            iPlayer == con.iPortugal):  
                                self.rnf.setAstronomyTurn(iPlayer, gc.getGame().getGameTurn())
                if (argsList[0] == con.iCompass):
                        if (iPlayer == con.iVikings):
                                gc.getMap().plot(49, 62).setTerrainType(con.iCoast, True, True)
                if (argsList[0] == con.iMedicine):
                        self.pla.onTechAcquired(argsList[0], argsList[2])

                                
        #Rhye - end
                
                


        # This method handles the key input and will bring up the mercenary manager screen if the 
        # player has at least one city and presses the 'M' key.
        def onKbdEvent(self, argsList):
                'keypress handler - return 1 if the event was consumed'


                #Rhye - start debug
                eventType,key,mx,my,px,py = argsList
                        
                theKey=int(key)

                if ( eventType == self.EventKeyDown and theKey == int(InputTypes.KB_B) and self.eventManager.bAlt):


                        iHuman = utils.getHumanID()

##                        gc.getMap().plot(27, 30).setFeatureType(-1, 0)
##                        gc.getMap().plot(28, 31).setFeatureType(-1, 0)
##                        gc.getMap().plot(31, 13).setPlotType(PlotTypes.PLOT_HILLS, True, True)

                        #self.com.decay(con.iGermany)                
                        #gc.getGame().setActivePlayer(con.iEngland, False)
                        #gc.getGame().setActivePlayer(con.iRussia, False)
                        #self.data.setupScriptData()
                        #gc.getGame().setWinner(con.iEgypt, 0)
                        #if (len(lLeaders[iDeadCiv]) > 1):
                        #gc.getTeam(gc.getPlayer(con.iIndia).getTeam()).signOpenBorders(con.iChina)
                        #print ("CC1", gc.getTeam(gc.getPlayer(con.iIndia).getTeam()).canContact(con.iEgypt))
                        #print ("ME1", gc.getTeam(gc.getPlayer(con.iIndia).getTeam()).isHasMet(con.iEgypt))
                        #gc.getTeam(gc.getPlayer(con.iRome).getTeam()).cutContact(con.iRussia)
                        #gc.getTeam(gc.getPlayer(con.iIndia).getTeam()).cutContact(con.iChina)
                        #print ("CC2", gc.getTeam(gc.getPlayer(con.iIndia).getTeam()).canContact(con.iEgypt))
                        #print ("ME2", gc.getTeam(gc.getPlayer(con.iIndia).getTeam()).isHasMet(con.iEgypt))
                        #for i in range (con.iNumPlayers):
                        #        gc.getTeam(gc.getPlayer(con.iInca).getTeam()).cutContact(i)
                        #gc.getTeam(gc.getPlayer(con.iChina).getTeam()).setVassal(con.iJapan, True, True)
                        #gc.getGame().changePlayer(con.iChina, 0, 22, con.iChina, False, True)
                        #gc.getPlayer(con.iBabylonia).setLeader(24)
                        #gc.getPlayer(con.iEgypt).changeGold(3000)
                        #gc.getMap().plot(72, 32).getPlotCity().changeBuildingProduction(con.iBroadway,639)
                        #print ("CC2", gc.getTeam(gc.getPlayer(con.iEgypt).getTeam()).canContact(con.iNative))
                        #newCivDesc = CyTranslator().getText("TXT_KEY_NAM_CHI1", ())
##                        newCivDesc = "TXT_KEY_NAM_CHI1"
##                        newDesc = newCivDesc.encode('latin-1')
##                        gc.getPlayer(con.iChina).setCivDescription(newDesc)
##                        print (gc.getPlayer(con.iChina).getCivilizationDescription(0), gc.getPlayer(con.iChina).getCivilizationDescriptionKey(), gc.getPlayer(con.iChina).getCivilizationAdjective(0), gc.getPlayer(con.iChina).getCivilizationAdjectiveKey())
##                        print (gc.getPlayer(con.iIndia).getCivilizationDescription(0), gc.getPlayer(con.iIndia).getCivilizationDescriptionKey(), gc.getPlayer(con.iIndia).getCivilizationAdjective(0), gc.getPlayer(con.iIndia).getCivilizationAdjectiveKey())
##                        self.rnf.showPopup(7614, CyTranslator().getText("TXT_KEY_NEWCIV_TITLE", ()), CyTranslator().getText("TXT_KEY_NEWCIV_MESSAGE", (gc.getPlayer(con.iChina).getCivilizationDescriptionKey(),)), (CyTranslator().getText("TXT_KEY_POPUP_YES", ()), CyTranslator().getText("TXT_KEY_POPUP_NO", ())))

                        #gc.getTeam(gc.getPlayer(con.iChina).getTeam()).setVassal(con.iArabia, True, True)

                        
                        #invasion attempt
                        #if (iGameTurn == 100):
                        #        utils.makeUnit(con.iAxeman, iGermany, con.tCapitals[iGermany], 3)
                        #        utils.makeUnit(con.iSwordsman, iGermany, con.tCapitals[iGermany], 3)
                        
                        #for iCiv in range(iNumPlayers):
                        #        for pyCity in PyPlayer(iCiv).getCityList():
                        #                print (pyCity.GetCy().getName())

                        #debug - kills every unit
                        #for x in range(40, 123):
                        #        for y in range(0, 67):
                        #                pCurrent = gc.getMap().plot( x, y )
                        #                if (pCurrent.getNumUnits() > 0):
                        #                        for i in range (pCurrent.getNumUnits()):
                        #                                unit = pCurrent.getUnit(0)
                        #                                unit.kill(False, con.iBarbarian)


##                        if (gc.getPlayer(utils.getHumanID()).getNumCities() > 1):
##                                CyInterface().addImmediateMessage(CyTranslator().getText("TXT_KEY_STABILITY_CIVILWAR_HUMAN", ()), "")
##                                utils.killAndFragmentCiv(utils.getHumanID(), True)
##                                utils.setStability(utils.getHumanID(), -15)


                        #self.pla.setGenericPlagueDates(0, 96)
                        #self.pla.spreadPlague(con.iJapan)
                        #self.pla.stopPlague(con.iJapan)
                        #self.pla.infectCity(utils.getRandomCity(con.iJapan))
                        #print ("Countdown", self.pla.getPlagueCountdown( con.iJapan ))
                    
                        
                        #utils.killAndFragmentCiv(con.iEngland, iIndependent, iIndependent2, -1, False)
                        #self.rnf.resurrection(302)
                        
                        #utils.killAndFragmentCiv(con.iRome, iIndependent, iIndependent2, -1, True)
                        #gc.getGame().setActivePlayer(con.iEgypt, False)
                        #teamEgypt.changeResearchProgress(con.iNationalism, 3299, iEgypt)
                        #teamAztecs.changeResearchProgress(con.iSteel, 3399, iAztecs)
                        
                        #self.sta.normalization(200)
                        #gc.getGame().setActivePlayer(con.iNetherlands, False)
                        #gc.getPlayer(con.iPortugal).changeGold(200)
                        
                        #CyInterface().addImmediateMessage(CyTranslator().getText("TXT_KEY_PLAGUE_SPREAD_CITY", ()), "")
                        #CyInterface().addMessage(utils.getHumanID(), False, con.iDuration, CyTranslator().getText("TXT_KEY_EMBASSY_ESTABLISHED", (gc.getPlayer(con.iRussia).getCivilizationAdjectiveKey(),)) + " " + "Citta di prova", "", 0, "", ColorTypes(con.iWhite), -1, -1, True, True)

                        #CyInterface().addMessage(utils.getHumanID(), True, 5, CyTranslator().getText("TXT_KEY_CONGRESS_NOTIFY_YES2", ()), "", 0, "", ColorTypes(100), -1, -1, True, True)
##                        for i in range(128):
##                                CyInterface().addMessage(utils.getHumanID(), True, 1, "i", "", 0, "", ColorTypes(i), -1, -1, False, True)
##                                if (i % 10 == 0):
##                                         CyInterface().addMessage(utils.getHumanID(), True, 1, "10", "", 0, "", ColorTypes(0), -1, -1, False, True)
                        #print ("vic", self.vic.getNumSinks())

                        #dummy, plotList = utils.squareSearch( (29,28), (31,31), utils.outerInvasion, [])
                        #print (plotList)
                        #utils.setStability(con.iChina, -25)
                        
                        #city = gc.getMap().plot( 79, 40 ).getPlotCity() 
                        #self.pla.infectCity(city)
                        #self.pla.spreadPlague(con.iPersia)
                        #self.pla.processPlague(con.iPersia)

                        #city = gc.getMap().plot( 90, 40 ).getPlotCity()
                        #print ("9040", city.getCulture(con.iIndia), 4000 + 2000*gc.getPlayer(con.iIndia).getCurrentEra())

                        
                        #CyInterface().DoSoundtrack("AS2D_R_F_C")
                        #if (gc.getPlayer(con.iNetherlands).countOwnedBonuses(con.iSpices) + gc.getPlayer(con.iNetherlands).getBonusImport(con.iSpices) >= 5):
                        #        self.vic.setGoal(iNetherlands, 2, 0)

                        #utils.setLastRecordedStabilityStuff(2, 0)
                        #utils.setLastRecordedStabilityStuff(1, 40)

##                        #print (CyGame().getCurrentLanguage())
##                        popup = PyPopup.PyPopup()
##                        popup.setHeaderString(CyTranslator().getText("TXT_KEY_EXILE_TITLE", ()))          
##                        popup.setBodyString( CyTranslator().getText("TXT_KEY_EXILE_TEXT", (gc.getPlayer(con.iGermany).getCivilizationAdjectiveKey(), gc.getPlayer(con.iSpain).getCivilizationShortDescription(0))))
####                        popup.setHeaderString(CyTranslator().getText("TXT_KEY_ESCAPE_TITLE", ()))          
####                        popup.setBodyString( CyTranslator().getText("TXT_KEY_ESCAPE_TEXT", (gc.getPlayer(con.iGermany).getCivilizationAdjectiveKey(),)))
##                        popup.launch()
##
##                        CyInterface().addMessage(utils.getHumanID(), True, con.iDuration/2, ("XXX" + " " + \
##                                                                                   CyTranslator().getText("TXT_KEY_CONGRESS_NOTIFY_YES", (gc.getPlayer(con.iSpain).getCivilizationAdjectiveKey(),))), \
##                                                                                   "", 0, "", ColorTypes(con.iCyan), -1, -1, True, True)
##                        self.rnf.newCivPopup(con.iSpain)
##
##                        self.rnf.showPopup(7622, CyTranslator().getText("TXT_KEY_REBELLION_TITLE", ()), \
##                               CyTranslator().getText("TXT_KEY_REBELLION_TEXT", (gc.getPlayer(con.iGermany).getCivilizationAdjectiveKey(),)), \
##                               (CyTranslator().getText("TXT_KEY_POPUP_YES", ()), \
##                                CyTranslator().getText("TXT_KEY_POPUP_NO", ())))
##
##                        CyInterface().addMessage(utils.getHumanID(), False, con.iDuration, \
##                                                                                 CyTranslator().getText("TXT_KEY_STABILITY_GREAT_DEPRESSION_INFLUENCE", (gc.getPlayer(con.iSpain).getCivilizationDescription(0),)), \
##                                                                                 "", 0, "", ColorTypes(con.iOrange), -1, -1, True, True)
##
####                        CyInterface().addMessage(utils.getHumanID(), True, con.iDuration, \
####                                                        (CyTranslator().getText("TXT_KEY_INDEPENDENCE_TEXT", (gc.getPlayer(con.iGermany).getCivilizationAdjectiveKey(),))), "", 0, "", ColorTypes(con.iGreen), -1, -1, True, True)
##                                
                        #print ("ERA", gc.getInfoTypeForString("ERA_CLASSICAL"))
##                        for iEuroCiv in range(iNumPlayers):
##                                if (iEuroCiv in con.lCivGroups[0]):
##                                        if (not self.vic.checkNotOwnedArea_Skip(iEuroCiv, (24, 3), (43, 32), (32,14), (43,30))):
##                                                CyInterface().addImmediateMessage(CyTranslator().getText("TXT_KEY_STABILITY_CIVILWAR_HUMAN", ()), "")


                        
                        pass
                        print ("SEED:", gc.getGame().getSorenRand().getSeed())

                if ( eventType == self.EventKeyDown and theKey == int(InputTypes.KB_N) and self.eventManager.bAlt):

                        print("ALT-N")
                        #RFCMP
                        #self.printEmbassyDebug()
                        self.printPlotsDebug()
                        self.printStabilityDebug()

                #Rhye - end debug
        
        #Mercenaries - end



        #Rhye - start
        def printDebug(self, iGameTurn):

                #RFCMP
##                if (iGameTurn %10 == 1):
##                        self.printEmbassyDebug()

##                if (iGameTurn %5 == 0):
##                        self.printPlotsDebug()

##                if (iGameTurn %5 == 0): 
##                        self.printStabilityDebug()
                pass


                        
        def printPlotsDebug(self):

##                for i in range(124):
##                        for j in range(68):
##                                print (i, j, gc.getMap().plot(i,j).getArea())
            
                #countTotalUnits
                iTotal = 0
                iTotalCities = 0
##                lType = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
##                lOwner = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                
                #lOwnerLongbow = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
                #         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
                #         0, 0, 0, 0, 0, 0, 0]
                #lOwnerCannon = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
                #         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
                #         0, 0, 0, 0, 0, 0, 0]
##                lPlotOwner = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                              0, 0]
                #lPlotOwner2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
                #              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
                #              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
                #              0, 0]
##                lCityOwner2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
##                              0, 0]
                #lCityOwner_sb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
                #              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
                #              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
                #              0, 0]
                for x in range(0, 123):
                        for y in range(0, 67):
                                pCurrent = gc.getMap().plot( x, y )
                                iTotal += pCurrent.getNumUnits()
##                                if (pCurrent.getNumUnits() > 0):
##                                        for i in range (pCurrent.getNumUnits()):
##                                                unit = pCurrent.getUnit(i)
##                                                lType[unit.getUnitType()] += 1
##                                                lOwner[unit.getOwner()] += 1
                                                #if (unit.getUnitType() == con.iLongbowman):
                                                #       lOwnerLongbow[unit.getOwner()] += 1
                                                #if (unit.getUnitType() == con.iCannon):
                                                #       lOwnerCannon[unit.getOwner()] += 1

                                if ( pCurrent.isCity()):
                                        iTotalCities += 1
                                        
                print ("TOTAL UNITS", iTotal)  
                print ("TOTAL CITIES", iTotalCities)
                #for i in range (len(lPlotOwner)):
                for i in range(con.iNumPlayers):
                        print (gc.getPlayer(i).getCivilizationShortDescription(0), "PLOT OWNERSHIP ABROAD:", self.sta.getOwnedPlotsLastTurn(i), "CITY OWNERSHIP LOST:", self.sta.getOwnedCitiesLastTurn(i) )

##                print ("Unit types")
##                for i in range (len(lType)):
##                        print (i, lType[i])
##                print ("Unit owners")
##                for i in range (len(lOwner)):
##                        print (i, lOwner[i])
                #print ("LB owners")
                #for j in range (len(lOwnerLongbow)):
                #        print (j, lOwnerLongbow[j])               
                #print ("Cannon owners")
                #for j in range (len(lOwnerCannon)):
                #        print (j, lOwnerCannon[j])               
        
                pass

        def printEmbassyDebug(self):
                for i in range(con.iNumPlayers):
                        if (gc.getPlayer(i).isAlive()):
                                apCityList = PyPlayer(i).getCityList()
                                print (gc.getPlayer(i).getCivilizationShortDescription(0), gc.getTeam(gc.getPlayer(i).getTeam()).isHasTech(con.iCivilService), gc.getTeam(gc.getPlayer(i).getTeam()).isHasTech(con.iPaper))                                                                                     
                                for j in range(con.iNumPlayers):
                                        if (gc.getTeam(gc.getPlayer(i).getTeam()).canContact(j)):   
                                                bEmb = False
                                                for pCity in apCityList:
                                                        city = pCity.GetCy()
                                                        if (city.hasBuilding(con.iNumBuildingsPlague+j)):
                                                                print (city.getName(), "HAS EMBASSY", gc.getPlayer(j).getCivilizationAdjective(0))
                                                                bEmb = True
                                                                break
                                                if (bEmb == False):
                                                        print ("NO EMBASSY", gc.getPlayer(j).getCivilizationAdjective(0))


        def printStabilityDebug(self):
                print ("Stability")
                for iCiv in range(con.iNumPlayers):
                        if (gc.getPlayer(iCiv).isAlive()):
                                print ("Base:", utils.getBaseStabilityLastTurn(iCiv), "Modifier:", utils.getStability(iCiv)-utils.getBaseStabilityLastTurn(iCiv), "Total:", utils.getStability(iCiv), "civic", gc.getPlayer(iCiv).getCivics(0), gc.getPlayer(iCiv).getCivilizationShortDescription(0))
                        else:
                                print ("dead", iCiv)
                for i in range(con.iNumStabilityParameters):
                        print("Parameter", i, utils.getStabilityParameters(i))
