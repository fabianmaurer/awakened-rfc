from Reporting import ENABLED as REPORTING_ENABLED
# Rhye's and Fall of Civilization - Barbarian units and cities

from CvPythonExtensions import *
import ScenarioGeography as geo
import CvUtil
import PyHelpers        # LOQ
import Popup
import cPickle as pickle
import RFCUtils
import Consts as con

# globals
gc = CyGlobalContext()
PyPlayer = PyHelpers.PyPlayer	# LOQ
utils = RFCUtils.RFCUtils()


### Constants ###

iIndependent = con.iIndependent
iIndependent2 = con.iIndependent2
iNative = con.iNative
iCeltia = con.iCeltia
pIndependent = gc.getPlayer(iIndependent)
pIndependent2 = gc.getPlayer(iIndependent2)
pNative = gc.getPlayer(iNative)
pCeltia = gc.getPlayer(iCeltia)
teamIndependent = gc.getTeam(pIndependent.getTeam())
teamIndependent2 = gc.getTeam(pIndependent2.getTeam())
teamNative = gc.getTeam(pNative.getTeam())
teamCeltia = gc.getTeam(pCeltia.getTeam())

iBarbarian = con.iBarbarian
pBarbarian = gc.getPlayer(iBarbarian)
teamBarbarian = gc.getTeam(pBarbarian.getTeam())
      

# city coordinates, spawn 1st turn and retries
geo.bind(globals(), 'lUr', 'Barbs.lUr') #3000BC
geo.bind(globals(), 'lJerusalem', 'Barbs.lJerusalem') #3000BC
geo.bind(globals(), 'lBabylon', 'Barbs.lBabylon') #3000BC
geo.bind(globals(), 'lSusa', 'Barbs.lSusa') #3000BC
geo.bind(globals(), 'lTyre', 'Barbs.lTyre') #2700BC #turn10
geo.bind(globals(), 'lKnossos', 'Barbs.lKnossos') #2600BC
geo.bind(globals(), 'lHattusas', 'Barbs.lHattusas') #2000BC
geo.bind(globals(), 'lSamarkand', 'Barbs.lSamarkand') #2000BC
geo.bind(globals(), 'lNineveh', 'Barbs.lNineveh') #1800BC
geo.bind(globals(), 'lGadir', 'Barbs.lGadir') #1100BC
geo.bind(globals(), 'lLepcis', 'Barbs.lLepcis') #1100BC
geo.bind(globals(), 'lCarthage', 'Barbs.lCarthage') #814BC
geo.bind(globals(), 'lGordion', 'Barbs.lGordion') #800BC
geo.bind(globals(), 'lPalermo', 'Barbs.lPalermo') #700BC
geo.bind(globals(), 'lMilan', 'Barbs.lMilan') #700BC
geo.bind(globals(), 'lKaralis', 'Barbs.lKaralis') #Phoenician Sardinia, outside Rome's birth-flip area
geo.bind(globals(), 'lAugsburg', 'Barbs.lAugsburg')
geo.bind(globals(), 'lRusadir', 'Barbs.lRusadir') #650BC
geo.bind(globals(), 'lLyon', 'Barbs.lLyon') #350BC???
#lAxum = [72, 29, 121, 0] #300BC
geo.bind(globals(), 'lBordeaux', 'Barbs.lBordeaux') #300BC
geo.bind(globals(), 'lCartagena', 'Barbs.lCartagena') #230BC
geo.bind(globals(), 'lArtaxata', 'Barbs.lArtaxata') #190BC
geo.bind(globals(), 'lLutetia', 'Barbs.lLutetia') #50BC
geo.bind(globals(), 'lSeoul', 'Barbs.lSeoul') #25BC
#lTikal = [22, 35, 145, 0] #60AD
geo.bind(globals(), 'lSanaa', 'Barbs.lSanaa') #100AD
geo.bind(globals(), 'lPagan', 'Barbs.lPagan') #107AD
geo.bind(globals(), 'lInverness', 'Barbs.lInverness') #400AD
#lChichenItza = [23, 37, 170, 0] #445AD
geo.bind(globals(), 'lBaku', 'Barbs.lBaku') #600AD ca
geo.bind(globals(), 'lLhasa', 'Barbs.lLhasa') #633AD
#lAngkor = [102, 34, 201, 0] #802AD
geo.bind(globals(), 'lHanoi', 'Barbs.lHanoi') #866AD
geo.bind(globals(), 'lTucume', 'Barbs.lTucume') #900AD
geo.bind(globals(), 'lJelling', 'Barbs.lJelling') #980AD
geo.bind(globals(), 'lDublin', 'Barbs.lDublin') #990AD
geo.bind(globals(), 'lNidaros', 'Barbs.lNidaros') #1000AD
geo.bind(globals(), 'lZimbabwe', 'Barbs.lZimbabwe') #1000AD
geo.bind(globals(), 'lQuelimane', 'Barbs.lQuelimane') #1000AD
geo.bind(globals(), 'lUppsala', 'Barbs.lUppsala') #1070AD
geo.bind(globals(), 'lMombasa', 'Barbs.lMombasa') #1100AD
geo.bind(globals(), 'lKazan', 'Barbs.lKazan') #1200AD
geo.bind(globals(), 'lKongo', 'Barbs.lKongo') #1483AD



#handicap level modifier
iHandicapOld = 0



class Barbs:

        def makeUnit(self, iUnit, iPlayer, tCoords, iNum, iForceAttack, sNameKey=None):
                'Makes iNum units for player iPlayer of the type iUnit at tCoords.'
                for i in range(iNum):
                        player = gc.getPlayer(iPlayer)
                        if (iForceAttack == 0):
                                unit = player.initUnit(iUnit, tCoords[0], tCoords[1], UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                        elif (iForceAttack == 1):
                                unit = player.initUnit(iUnit, tCoords[0], tCoords[1], UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
                        elif (iForceAttack == 2):
                                unit = player.initUnit(iUnit, tCoords[0], tCoords[1], UnitAITypes.UNITAI_ATTACK_SEA, DirectionTypes.DIRECTION_SOUTH)
                        elif (iForceAttack == 3):
                                unit = player.initUnit(iUnit, tCoords[0], tCoords[1], UnitAITypes.UNITAI_PILLAGE, DirectionTypes.DIRECTION_SOUTH)
                        if (sNameKey):
                                unit.setName(CyTranslator().getText(sNameKey, ()))


        def checkTurn(self, iGameTurn):
            
                #handicap level modifier
                iHandicap = 0

                #debug
                #if (iGameTurn % 50 == 1):
                #        print ("iHandicap", iHandicap)
                #        print ("iHandicapOld", iHandicapOld)

                if (iGameTurn >= con.i3000BC and iGameTurn <= con.i850BC):
                        if (iHandicap >= 0):
                                self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_1'), geo.value('Barbs.checkTurn.location_2'), con.iWarrior, 1, iGameTurn, 5, 0, utils.outerInvasion, 0)
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_3'), geo.value('Barbs.checkTurn.location_4'), con.iWolf, 1, iGameTurn, 5, 2, utils.outerInvasion, 0)
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_5'), geo.value('Barbs.checkTurn.location_6'), con.iBear, 1, iGameTurn, 5, 4, utils.outerInvasion, 0)
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_7'), geo.value('Barbs.checkTurn.location_8'), con.iLion, 1, iGameTurn, 4, 1, utils.outerInvasion, 0)
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_9'), geo.value('Barbs.checkTurn.location_10'), con.iPanther, 1, iGameTurn, 4, 3, utils.outerInvasion, 0)

                        
                # Small, staggered frontier raids for the 3000 BC Egyptian start.
                # Give the first settlement twelve turns; stop before later armies.
                if (gc.getGame().getStartTurn() == 0 and gc.getPlayer(con.iEgypt).isAlive()
                    and gc.getPlayer(con.iEgypt).getNumCities() > 0
                    and iGameTurn >= 12 and iGameTurn <= con.i850BC):
                        # Nubians approach along the Nile; Libyans enter from the west.
                        # Pillage AI and warriors keep these as light military pressure.
                        self.spawnUnits(iBarbarian, geo.value('Barbs.checkTurn.location_11'), geo.value('Barbs.checkTurn.location_12'), con.iWarrior, 2, iGameTurn, 18, 12, utils.outerInvasion, 3, "TXT_KEY_UNIT_NUBIAN_RAIDERS")
                        self.spawnUnits(iBarbarian, geo.value('Barbs.checkTurn.location_13'), geo.value('Barbs.checkTurn.location_14'), con.iWarrior, 1, iGameTurn, 28, 22, utils.outerInvasion, 3, "TXT_KEY_UNIT_LIBYAN_RAIDERS")

                #celts
                if (iGameTurn >= con.i650BC and iGameTurn <= con.i110BC):
                        self.spawnUnits( iCeltia, geo.value('Barbs.checkTurn.location_15'), geo.value('Barbs.checkTurn.location_16'), con.iCelticGallicWarrior, 1, iGameTurn, 7, 0, utils.outerInvasion, 0)
                        if (iHandicap >= 0):
                                self.spawnUnits( iCeltia, geo.value('Barbs.checkTurn.location_17'), geo.value('Barbs.checkTurn.location_18'), con.iAxeman, 1, iGameTurn, 9, 6, utils.outerInvasion, 0)

                #norse
                if (iGameTurn >= con.i650BC and iGameTurn <= con.i550AD):
                        self.spawnUnits( iCeltia, geo.value('Barbs.checkTurn.location_19'), geo.value('Barbs.checkTurn.location_20'), con.iGalley, 1, iGameTurn, 25, 0, utils.outerSeaSpawn, 2)
                        
                # Northern steppe raids are replaced by the living Xiongnu state.
                if (not gc.getPlayer(con.iXiongnu).isAlive() and iGameTurn >= con.i210BC and iGameTurn < con.i300AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_21'), geo.value('Barbs.checkTurn.location_22'), con.iHorseArcher, 2 + iHandicap*2, iGameTurn, 8, 0, utils.outerInvasion, 0)
                if (not gc.getPlayer(con.iXiongnu).isAlive() and iGameTurn >= con.i300AD and iGameTurn <= con.i900AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_23'), geo.value('Barbs.checkTurn.location_24'), con.iHorseArcher, 3 + iHandicap*2, iGameTurn, 7, 0, utils.outerInvasion, 0)
                if (not gc.getPlayer(con.iXiongnu).isAlive() and iGameTurn > con.i900AD and iGameTurn <= con.i1100AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_25'), geo.value('Barbs.checkTurn.location_26'), con.iHorseArcher, 2 + iHandicap, iGameTurn, 6, 0, utils.outerInvasion, 0)
                        
                #tibet
                if (iGameTurn >= con.i350BC and iGameTurn <= con.i1100AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_27'), geo.value('Barbs.checkTurn.location_28'), con.iSwordsman, 1 + iHandicap, iGameTurn, 10-iHandicap, 3, utils.outerInvasion, 0)

                self.checkHunaInvasion(iGameTurn)

                # Early Indian elephant raids end before the Huna invasion warning.
                if (iGameTurn >= con.i210BC and iGameTurn < con.i450AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_29'), geo.value('Barbs.checkTurn.location_30'), con.iWarElephant, 1, iGameTurn, 6-iHandicap, 4, utils.outerInvasion, 0)
       
                        
                #pirates in Mediterranean
                if (iGameTurn >= con.i210BC and iGameTurn <= con.i50AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_31'), geo.value('Barbs.checkTurn.location_32'), con.iTrireme, 1, iGameTurn, 8, 0, utils.outerSeaSpawn, 2)
                #pirates in Barbary coast
                if (iGameTurn >= con.i50AD and iGameTurn <= con.i700AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_33'), geo.value('Barbs.checkTurn.location_34'), con.iTrireme, 1, iGameTurn, 18, 0, utils.outerCoastSpawn, 2)
                if (iGameTurn >= con.i700AD and iGameTurn <= con.i1400AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_35'), geo.value('Barbs.checkTurn.location_36'), con.iTrireme, 1, iGameTurn, 8, 0, utils.outerCoastSpawn, 2)
                if (iGameTurn >= con.i1400AD and iGameTurn <= con.i1700AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_37'), geo.value('Barbs.checkTurn.location_38'), con.iTrireme, 1, iGameTurn, 12, 0, utils.outerCoastSpawn, 2)
                #pirates in Indian ocean
                if (iGameTurn >= con.i650BC and iGameTurn <= con.i700AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_39'), geo.value('Barbs.checkTurn.location_40'), con.iTrireme, 1, iGameTurn, 18, 0, utils.outerCoastSpawn, 2)
                if (iGameTurn >= con.i700AD and iGameTurn <= con.i1700AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_41'), geo.value('Barbs.checkTurn.location_42'), con.iTrireme, 1, iGameTurn, 8, 0, utils.outerCoastSpawn, 2)


                                                
                #barbarians in europe
                if (iGameTurn >= con.i210BC and iGameTurn <= con.i550AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_43'), geo.value('Barbs.checkTurn.location_44'), con.iAxeman, 3 + iHandicap, iGameTurn, 12, 0, utils.outerInvasion, 0)
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_45'), geo.value('Barbs.checkTurn.location_46'), con.iAxeman, 2 + iHandicap, iGameTurn, 14, 2, utils.outerInvasion, 0)
                if (iGameTurn >= con.i50AD and iGameTurn <= con.i550AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_47'), geo.value('Barbs.checkTurn.location_48'), con.iSwordsman, 3, iGameTurn, 10, 5, utils.outerInvasion, 0)
                if (iGameTurn >= con.i300AD and iGameTurn <= con.i600AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_49'), geo.value('Barbs.checkTurn.location_50'), con.iAxeman, 4 + iHandicap, iGameTurn, 6, 4, utils.outerInvasion, 0)
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_51'), geo.value('Barbs.checkTurn.location_52'), con.iSwordsman, 4 + iHandicap, iGameTurn, 6, 2, utils.outerInvasion, 0)
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_53'), geo.value('Barbs.checkTurn.location_54'), con.iHorseArcher, 3, iGameTurn, 6, 0, utils.outerInvasion, 0)
                if (iGameTurn >= con.i300AD and iGameTurn <= con.i700AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_55'), geo.value('Barbs.checkTurn.location_56'), con.iHorseArcher, 3 + iHandicap, iGameTurn, 4, 2, utils.outerInvasion, 0)

                #last barbarians in east europe and caucasus
                if (iGameTurn >= con.i690AD and iGameTurn <= con.i1100AD):
                        if (not gc.getPlayer(con.iCeltia).getCivilizationType() == 4):  #late start condition (RFCMP)
                                self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_57'), geo.value('Barbs.checkTurn.location_58'), con.iHorseArcher, 3 + iHandicap, iGameTurn, 6, 0, utils.outerInvasion, 0)

                #barbarians in central asia
                if (iGameTurn >= con.i1600BC and iGameTurn < con.i850BC):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_59'), geo.value('Barbs.checkTurn.location_60'), con.iChariot, 2 + iHandicap, iGameTurn, 6-iHandicap, 2, utils.outerInvasion, 0)
                if (iGameTurn >= con.i850BC and iGameTurn < con.i300AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_61'), geo.value('Barbs.checkTurn.location_62'), con.iChariot, 1 + iHandicap, iGameTurn, 7-iHandicap, 2, utils.outerInvasion, 0)
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_63'), geo.value('Barbs.checkTurn.location_64'), con.iHorseArcher, 1 + iHandicap, iGameTurn, 7-iHandicap, 2, utils.outerInvasion, 0)
                if (iGameTurn >= con.i300AD and iGameTurn <= con.i700AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_65'), geo.value('Barbs.checkTurn.location_66'), con.iHorseArcher, 3 + iHandicap, iGameTurn, 8-iHandicap, 2, utils.outerInvasion, 0)
                if (iGameTurn > con.i700AD and iGameTurn <= con.i1400AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_67'), geo.value('Barbs.checkTurn.location_68'), con.iHorseArcher, 2 + iHandicap, iGameTurn, 6-iHandicap, 2, utils.outerInvasion, 0)
                        
                #barbarians in Elam
                if (iGameTurn >= con.i1600BC and iGameTurn < con.i1000BC):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_69'), geo.value('Barbs.checkTurn.location_70'), con.iChariot, 2, iGameTurn, 8-iHandicap, 0, utils.outerInvasion, 0)

                #barbarians in north africa
                # Frontier raids should be containable by a developed coastal state.
                # Do not spawn Guilds-strength camel cavalry throughout antiquity.
                if (iGameTurn >= con.i210BC and iGameTurn < con.i300AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_71'), geo.value('Barbs.checkTurn.location_72'), con.iHorseArcher, 1, iGameTurn, 15, 3, utils.outerInvasion, 0)
                if (iGameTurn >= con.i300AD and iGameTurn < con.i700AD):
                        # Concentrated late-antique pressure in Tripolitania,
                        # with recovery time between two-unit raiding groups.
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_73'), geo.value('Barbs.checkTurn.location_74'), con.iHorseArcher, 2, iGameTurn, 18, 5, utils.outerInvasion, 0)
                if (iGameTurn >= con.i700AD and iGameTurn < con.i900AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_75'), geo.value('Barbs.checkTurn.location_76'), con.iHorseArcher, 1, iGameTurn, 15, 3, utils.outerInvasion, 0)
                if (iGameTurn >= con.i900AD and iGameTurn <= con.i1800AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_77'), geo.value('Barbs.checkTurn.location_78'), con.iCamelArcher, 1, iGameTurn, 8-iHandicap, 4, utils.outerInvasion, 0)
                        
                #camels in arabia
                #if (iGameTurn >= con.i850BC and iGameTurn <= con.i190AD):
                #        self.spawnUnits( iBarbarian, (73, 30), (82, 36), con.iCamelArcher, 1, iGameTurn, 12-iHandicap, 3, utils.outerInvasion, 0)
                if (iGameTurn >= con.i190AD and iGameTurn <= con.i550AD):
                        # Keep late-antique raids near lower Mesopotamia rather than
                        # the short desert approach to independent Jerusalem.
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_79'), geo.value('Barbs.checkTurn.location_80'), con.iCamelArcher, 2, iGameTurn, 9-iHandicap, 7, utils.outerInvasion, 0)

                #African natives
                if (not gc.getPlayer(con.iCeltia).getCivilizationType() == 4):  #late start condition (RFCMP)
                        if (iGameTurn >= con.i50AD and iGameTurn <= con.i690AD):
                                self.spawnUnits( iNative, geo.value('Barbs.checkTurn.location_81'), geo.value('Barbs.checkTurn.location_82'), con.iZuluImpi, 3 + iHandicap, iGameTurn, 6, 4, utils.outerInvasion, 1)
                if (iGameTurn >= con.i450AD and iGameTurn <= con.i1700AD):
                        if (not gc.getPlayer(con.iCeltia).getCivilizationType() == 4):  #late start condition (RFCMP)
                                self.spawnUnits( iNative, geo.value('Barbs.checkTurn.location_83'), geo.value('Barbs.checkTurn.location_84'), con.iZuluImpi, 3 + iHandicap, iGameTurn, 10, 4, utils.outerInvasion, 1)
                        else:
                                self.spawnUnits( iNative, geo.value('Barbs.checkTurn.location_85'), geo.value('Barbs.checkTurn.location_86'), con.iZuluImpi, 3 + iHandicap, iGameTurn, 15, 4, utils.outerInvasion, 1)
                #west africa
                if (iGameTurn >= con.i450AD and iGameTurn <= con.i1700AD):
                        # Regional infantry raiders replace recurring elephant armies.
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_87'), geo.value('Barbs.checkTurn.location_88'), con.iSwordsman, 1, iGameTurn, 16, 4, utils.outerInvasion, 1)
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_89'), geo.value('Barbs.checkTurn.location_90'), con.iZuluImpi, 2, iGameTurn, 16, 10, utils.outerInvasion, 1)

                # Frequent light raids replace the sparse early American armies.
                self.checkAmericanRaids(iGameTurn)

                # Later North American resistance to colonization.
                if (iGameTurn >= con.i1400AD and iGameTurn <= con.i1800AD):
                        self.spawnUnits( iNative, geo.value('Barbs.checkTurn.location_91'), geo.value('Barbs.checkTurn.location_92'), con.iNativeAmericaDogSoldier, 3 + iHandicap, iGameTurn, 8, 0, utils.outerInvasion, 1)
                        self.spawnUnits( iNative, geo.value('Barbs.checkTurn.location_93'), geo.value('Barbs.checkTurn.location_94'), con.iNativeAmericaDogSoldier, 3 + iHandicap, iGameTurn, 8, 4, utils.outerInvasion, 1)
                #pirates in the Caribbean
                if (iGameTurn >= con.i1600AD and iGameTurn <= con.i1800AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_95'), geo.value('Barbs.checkTurn.location_96'), con.iPrivateer, 1, iGameTurn, 5, 0, utils.outerSeaSpawn, 0)
                #pirates in Asia
                if (iGameTurn >= con.i1600AD and iGameTurn <= con.i1900AD):
                        self.spawnUnits( iBarbarian, geo.value('Barbs.checkTurn.location_97'), geo.value('Barbs.checkTurn.location_98'), con.iPrivateer, 1, iGameTurn, 8, 0, utils.outerSeaSpawn, 0)



                #self.foundCity(iIndependent, lUr, "Ur", iGameTurn, 1, con.iWarrior, 1)
                self.foundCity(iIndependent2, lTyre, "Sur", iGameTurn, 1, con.iArcher, 1)
                self.foundCity(iIndependent, lJerusalem, "Yerushalayim", iGameTurn, 2, con.iArcher, 3)                        
                #self.foundCity(lBabylon, "Babel", iGameTurn, 1, con.iArcher, 1)
                self.foundCity(iBarbarian, lSusa, "Shushan", iGameTurn, 1, con.iArcher, 1)
                #self.foundCity(lKnossos, "Knossos", iGameTurn, 1, con.iWarrior, 0)                
                self.foundCity(iBarbarian, lHattusas, "Hattusas", iGameTurn, 1, con.iChariot, 2)
                self.foundCity(iIndependent, lSamarkand, "Afrasiyab", iGameTurn, 1, con.iArcher, 1)
                #self.foundCity(iBarbarian, lNineveh, "Nineveh", iGameTurn, 1, -1, -1)
                if (gc.getGame().getStartTurn() == 0):
                        # An existing Phoenician port to acquire in Iberia.
                        # Outside Carthage's birth flips and shared by all contenders.
                        if (self.foundCity(iIndependent, lGadir, "Gadir", iGameTurn, 2, con.iArcher, 1)):
                                crabPlot = gc.getMap().plot(*geo.value('Barbs.plot_1'))
                                if (crabPlot.getOwner() == -1 or crabPlot.getOwner() == iIndependent):
                                        if (crabPlot.getBonusType(-1) == gc.getInfoTypeForString('BONUS_CRAB') and crabPlot.getImprovementType() == -1):
                                                crabPlot.setImprovementType(gc.getInfoTypeForString('IMPROVEMENT_FISHING_BOATS'))
                #self.foundCity(lLepcis, "Lpqy", iGameTurn, 2, -1, -1)
                #self.foundCity(lCarthage, "Qart-Hadasht", iGameTurn, 2, -1, -1)
                self.foundCity(iBarbarian, lGordion, "Gordion", iGameTurn, 1, con.iChariot, 1)
                #self.foundCity(lPalermo, "Ziz", iGameTurn, 2, con.iArcher, 1)
                if (gc.getGame().getStartTurn() == 0):  #late start 800BC condition (RFCMP)
                        self.foundCity(iCeltia, lMilan, "Melpum", iGameTurn, 2, con.iArcher, 2)
                        # An inhabited island to contest, rather than empty land
                        # for a Roman or Carthaginian settler. Existing ownership
                        # and nearby cities prevent the normal optional founding.
                        if (self.foundCity(iIndependent2, lKaralis, "Karalis", iGameTurn, 2, con.iArcher, 1)):
                                # The small island needs its existing clam bed to
                                # support an inhabited town without mainland imports.
                                clamPlot = gc.getMap().plot(*geo.value('Barbs.plot_2'))
                                if (clamPlot.getOwner() == -1 or clamPlot.getOwner() == iIndependent2):
                                        if (clamPlot.getBonusType(-1) == gc.getInfoTypeForString('BONUS_CLAM') and clamPlot.getImprovementType() == -1):
                                                clamPlot.setImprovementType(gc.getInfoTypeForString('IMPROVEMENT_FISHING_BOATS'))
                #self.foundCity(iBarbarian, lAugsburg, "Damasia", iGameTurn, 1, -1, -1)
                #self.foundCity(lRusadir, "Rusadir", iGameTurn, 2, -1, -1)
                self.foundCity(iCeltia, lLyon, "Lugodunon", iGameTurn, 2, -1, -1)
                #self.foundCity(iIndependent, lAxum, "Axum", iGameTurn, 1, -1, -1)
                self.foundCity(iCeltia, lBordeaux, "Burdigala", iGameTurn, 2, -1, -1)
                #self.foundCity(lCartagena, "Qart Hadasht", iGameTurn, 1, -1, -1)
                self.foundCity(iIndependent, lSeoul, "Hanseong", iGameTurn, 2, -1, -1)
                self.foundCity(iIndependent2, lArtaxata, "Artashat", iGameTurn, 1, -1, -1)
                self.foundCity(iCeltia, lLutetia, "Lutetia", iGameTurn, 2, -1, -1)
                #self.foundCity(iNative, lTikal, "Tikal", iGameTurn, 1, -1, -1)
                self.foundCity(iIndependent, lSanaa, "Sana'a", iGameTurn, 1, -1, -1)
                self.foundCity(iIndependent2, lPagan, "Pagan", iGameTurn, 2, -1, -1)
                self.foundCity(iCeltia, lInverness, "Inbhir Nis", iGameTurn, 2, -1, -1)
                #self.foundCity(iNative, lChichenItza, "Chichen Itza", iGameTurn, 1, -1, -1)
                self.foundCity(iBarbarian, lBaku, "Bak&#252;", iGameTurn, 2, con.iArcher, -1)
                self.foundCity(iBarbarian, lLhasa, "Lasa", iGameTurn, 2, -1, -1)
                #bLhasaResult = self.foundCity(iBarbarian, lLhasa, "Lasa", iGameTurn, 2, -1, -1)
                #if (bLhasaResult == False):
                #        self.foundCity(iBarbarian, (lLhasa[0] - 1, lLhasa[1] - 1, lLhasa[2], lLhasa[3]), "Lhasa", iGameTurn, 2, -1, -1) #try to found it nearby
                #self.foundCity(iIndependent2, lAngkor, "Angkor", iGameTurn, 1, -1, -1)
                self.foundCity(iBarbarian, lHanoi, "Hanoi", iGameTurn, 2, -1, -1)
                self.foundCity(iNative, lTucume, "Tucume", iGameTurn, 1, -1, -1)
                #self.foundCity(lJelling, "Jelling", iGameTurn, 1, -1, -1)
                if (not gc.getPlayer(con.iCeltia).getCivilizationType() == 4):  #late start condition (RFCMP)
                        self.foundCity(iCeltia, lDublin, "&#193;th Cliath", iGameTurn, 1, -1, -1)
                else:
                        self.foundCity(iIndependent, lDublin, "&#193;th Cliath", iGameTurn, 1, -1, -1)
                #self.foundCity(lNidaros, "Nidaros", iGameTurn, 1, -1, -1)
                #self.foundCity(iNative, lZimbabwe, "Zimbabwe", iGameTurn, 1, con.iZuluImpi, 1)
                self.foundCity(iNative, lQuelimane, "Quelimane", iGameTurn, 1, con.iZuluImpi, 1)
                #self.foundCity(lUppsala, "Upsala", iGameTurn, 1, -1, -1)
                self.foundCity(iNative, lMombasa, "Mombasa", iGameTurn, 1, con.iZuluImpi, 1)
                self.foundCity(iBarbarian, lKazan, "Kazan", iGameTurn, 2, con.iHorseArcher, 1)
                self.foundCity(iNative, lKongo, "Mbanza Kongo", iGameTurn, 1, con.iZuluImpi, 1)



        def checkAmericanRaids(self, iGameTurn):
                # Two weak raiders per region every three turns, through 1600.
                # Stagger regions and allow eight turns after a scenario starts.
                if (iGameTurn < gc.getGame().getStartTurn() + 8 or iGameTurn > con.i1600AD):
                        return
                if (gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS)):
                        return
                lRegions = geo.value('Barbs.checkAmericanRaids.lRegions_1')  # Andes and nearby lowlands
                for iRegion in range(len(lRegions)):
                        if (iGameTurn % 3 != iRegion):
                                continue
                        tTL, tBR = lRegions[iRegion]
                        lCities = []
                        lOpen = []
                        iRaiders = 0
                        for x in range(tTL[0], tBR[0] + 1):
                                for y in range(tTL[1], tBR[1] + 1):
                                        plot = gc.getMap().plot(x, y)
                                        for i in range(plot.getNumUnits()):
                                                if (plot.getUnit(i).getOwner() == iBarbarian):
                                                        iRaiders += 1
                                        if (plot.isCity()):
                                                city = plot.getPlotCity()
                                                if (city.getOwner() < con.iNumPlayers
                                                    and city.getGameTurnFounded() <= iGameTurn - 8):
                                                        lCities.append(plot)
                                        elif (not plot.isWater() and not plot.isPeak() and not plot.isImpassable()
                                              and not plot.isUnit()
                                              and (not plot.isOwned() or plot.getOwner() == iBarbarian)):
                                                # Jungle is allowed: these are local raiders.
                                                lOpen.append((x, y, plot.area().getID()))
                        # Keep unattended regions from accumulating huge armies.
                        if (not lCities or iRaiders >= 12):
                                continue
                        lSpawns = []
                        for x, y, iArea in lOpen:
                                iNearest = 1000
                                for cityPlot in lCities:
                                        if (cityPlot.area().getID() == iArea):
                                                iNearest = min(iNearest, plotDistance(x, y, cityPlot.getX(), cityPlot.getY()))
                                if (iNearest >= 3 and iNearest <= 6):
                                        # Also protect new cities and cities beyond the region.
                                        bNearCity = False
                                        for iX in range(x - 2, x + 3):
                                                for iY in range(y - 2, y + 3):
                                                        if (gc.getMap().plot(iX, iY).isCity()):
                                                                bNearCity = True
                                        if (not bNearCity):
                                                lSpawns.append((x, y))
                        if (not lSpawns):
                                continue
                        tSpawn = lSpawns[utils.getFakeRandNum(len(lSpawns), 'American tribal raids')]
                        # Alternate warrior pairs with a warrior and an archer.
                        # Pillage AI emphasizes frontier disruption over city assaults.
                        lUnits = [con.iWarrior, con.iWarrior]
                        if ((iGameTurn // 3) % 2 == 1):
                                lUnits[1] = con.iArcher
                        for iUnit in lUnits[:min(2, 12 - iRaiders)]:
                                self.makeUnit(iUnit, iBarbarian, tSpawn, 1, 3)
                                if REPORTING_ENABLED:
                                    import GameObserver
                                    GameObserver.record_mechanic('scripted_spawn', iBarbarian,
                                            {'unit': iUnit, 'count': 1,
                                             'x': tSpawn[0], 'y': tSpawn[1],
                                             'region': [tTL[0], tTL[1], tBR[0], tBR[1]],
                                             'period': 3})


        def checkHunaInvasion(self, iGameTurn):
                # One finite late-Gupta invasion, separate from China's Xiongnu.
                if (iGameTurn != con.i450AD and iGameTurn != con.i500AD):
                        return
                pIndia = gc.getPlayer(con.iIndia)
                if (not pIndia.isAlive() or pIndia.getNumCities() == 0):
                        return
                if (iGameTurn == con.i450AD):
                        CyInterface().addMessage(con.iIndia, True, con.iDuration,
                                CyTranslator().getText("TXT_KEY_HUNA_INVASION_WARNING", ()),
                                "", 0, "", ColorTypes(con.iOrange), 88, 40, True, True)
                        return

                # Punjab side of the mountains: prefer unclaimed land, then
                # Indian territory, then foreign-controlled approach tiles.
                # Adjacent cities and Indian interior territory do not block
                # entry; the entry tile itself must have no city or units.
                lOpen = []
                lIndian = []
                lForeign = []
                for x in range(*geo.value('Barbs.range_1')):
                        for y in range(*geo.value('Barbs.range_2')):
                                plot = gc.getMap().plot(x, y)
                                if (plot.isWater() or plot.isPeak() or plot.isImpassable()
                                    or plot.isCity() or plot.isUnit()):
                                        continue
                                if (plot.getTerrainType() == con.iMarsh or plot.getFeatureType() == con.iJungle):
                                        continue
                                if (plot.area().getID() != pIndia.getCapitalCity().plot().area().getID()):
                                        continue
                                if (not plot.isOwned() or plot.getOwner() == iBarbarian):
                                        lOpen.append((x, y))
                                elif (plot.getOwner() == con.iIndia):
                                        lIndian.append((x, y))
                                elif (plot.getOwner() != con.iIndia):
                                        lForeign.append((x, y))
                lPlots = lOpen or lIndian or lForeign
                if (not lPlots):
                        return
                tSpawn = lPlots[utils.getFakeRandNum(len(lPlots), 'Huna invasion')]
                # One shared entry point keeps the invasion together. Three
                # cavalry pillage; the rest of the force can assault cities.
                lArmy = ((con.iHorseArcher, 4, UnitAITypes.UNITAI_ATTACK_CITY),
                         (con.iHorseArcher, 3, UnitAITypes.UNITAI_PILLAGE),
                         (con.iSwordsman, 3, UnitAITypes.UNITAI_ATTACK_CITY),
                         (con.iSpearman, 2, UnitAITypes.UNITAI_COUNTER))
                if REPORTING_ENABLED:
                    import GameObserver
                iFlanking1 = gc.getInfoTypeForString("PROMOTION_FLANKING1")
                iFlanking2 = gc.getInfoTypeForString("PROMOTION_FLANKING2")
                for iUnit, iCount, iAI in lArmy:
                        for i in range(iCount):
                                unit = pBarbarian.initUnit(iUnit, tSpawn[0], tSpawn[1], iAI, DirectionTypes.DIRECTION_SOUTH)
                                unit.setScriptData("RFCMP_HUNA_INVASION")
                                if (iUnit == con.iHorseArcher):
                                        unit.setHasPromotion(iFlanking1, True)
                                        unit.setHasPromotion(iFlanking2, True)
                        if REPORTING_ENABLED:
                            GameObserver.record_mechanic('scripted_spawn', iBarbarian,
                                    {'unit': iUnit, 'count': iCount,
                                     'x': tSpawn[0], 'y': tSpawn[1],
                                     'region': geo.value('Barbs.checkHunaInvasion.location_1'), 'period': 0})
                CyInterface().addMessage(con.iIndia, True, con.iDuration,
                        CyTranslator().getText("TXT_KEY_HUNA_INVASION_ARRIVAL", ()),
                        "", 0, "", ColorTypes(con.iOrange), tSpawn[0], tSpawn[1], True, True)


        def getCity(self, tCoords): #by LOQ
                'Returns a city at coordinates tCoords.'
                return CyGlobalContext().getMap().plot(tCoords[0], tCoords[1]).getPlotCity()

        def foundCity(self, iCiv, lCity, name, iTurn, iPopulation, iUnitType, iNumUnits):
                if ((iTurn == lCity[2] + lCity[3]) and (lCity[3]<10)):
                        #print self.checkRegion(tUr)
                        bResult, lCity[3] = self.checkRegion(lCity)
                        if (bResult == True):
                                pCiv = gc.getPlayer(iCiv)
                                pCiv.found(lCity[0], lCity[1])
                                self.getCity((lCity[0], lCity[1])).setName(name, False)
                                if (iPopulation != 1):
                                        self.getCity((lCity[0], lCity[1])).setPopulation(iPopulation)
                                if (iNumUnits > 0):
                                        self.makeUnit(iUnitType, iCiv, (lCity[0], lCity[1]), iNumUnits, 0)
                                return True
                        if (bResult == False) and (lCity[3] == -1):
                                return False
                               

        def checkRegion(self, tCity):
                cityPlot = gc.getMap().plot(tCity[0], tCity[1])
                iNumUnitsInAPlot = cityPlot.getNumUnits()
##                print iNumUnitsInAPlot
                
                #checks if the plot already belongs to someone
                if (cityPlot.isOwned()):
                        if (cityPlot.getOwner() != iBarbarian ):
                                return (False, -1)
                    
##                #checks if there's a unit on the plot
                if (iNumUnitsInAPlot):
                        for i in range(iNumUnitsInAPlot):
                                unit = cityPlot.getUnit(i)
                                iOwner = unit.getOwner()
                                if (iOwner == iBarbarian):
                                        return (False, tCity[3]+1) 
                                #pOwner = gc.getPlayer(iOwner)
                                #if (pOwner.isHuman()):
                                #        return (False, tCity[3]+1)                    

                #checks the surroundings and allows only AI units
                for x in range(tCity[0]-1, tCity[0]+2):
                        for y in range(tCity[1]-1, tCity[1]+2):
                                currentPlot=gc.getMap().plot(x,y)
                                if (currentPlot.isCity()):
                                        return (False, -1)                                
                                iNumUnitsInAPlot = currentPlot.getNumUnits()
                                if (iNumUnitsInAPlot):
                                        for i in range(iNumUnitsInAPlot):
                                                unit = currentPlot.getUnit(i)
                                                iOwner = unit.getOwner()
                                                pOwner = gc.getPlayer(iOwner)
                                                if (pOwner.isHuman()):
                                                        return (False, tCity[3]+1)
                return (True, tCity[3])



        def spawnUnits(self, iCiv, tTopLeft, tBottomRight, iUnitType, iNumUnits, iTurn, iPeriod, iRest, function, iForceAttack, sNameKey=None):
                if (iTurn % iPeriod == iRest):
                        dummy, plotList = utils.squareSearch( tTopLeft, tBottomRight, function, [] )
                        if (len(plotList)):
                                rndNum = utils.getFakeRandNum(len(plotList), 'Spawn units')
                                result = plotList[rndNum]
                                if (result):
                                        self.makeUnit(iUnitType, iCiv, result, iNumUnits, iForceAttack, sNameKey)
                                        # Observe successful scripted groups without another
                                        # spawn search, unit creation or RNG draw.
                                        if REPORTING_ENABLED:
                                            import GameObserver
                                        if REPORTING_ENABLED:
                                            GameObserver.record_mechanic('scripted_spawn', iCiv,
                                                    {'unit': iUnitType, 'count': iNumUnits,
                                                     'x': result[0], 'y': result[1],
                                                     'region': [tTopLeft[0], tTopLeft[1], tBottomRight[0], tBottomRight[1]],
                                                     'period': iPeriod})
                                


	    
        def killNeighbours(self, tCoords):
                'Kills all units in the neigbbouring tiles of plot (as well as plot itself) so late starters have some space.'
                for x in range(tCoords[0]-1, tCoords[0]+2):        # from x-1 to x+1
                        for y in range(tCoords[1]-1, tCoords[1]+2):	# from y-1 to y+1
                                killPlot = CyMap().getPlot(x, y)
                                for i in range(killPlot.getNumUnits()):
                                        unit = killPlot.getUnit(0)	# 0 instead of i because killing units changes the indices
                                        unit.kill(False, iBarbarian)

