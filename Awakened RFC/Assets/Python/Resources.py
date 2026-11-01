# Rhye's and Fall of Civilization - Dynamic resources

from CvPythonExtensions import *
import ScenarioGeography as geo
import CvUtil
import PyHelpers  
import Popup
import Consts as con

# globals
gc = CyGlobalContext()
PyPlayer = PyHelpers.PyPlayer

### Constants ###


# initialise bonuses variables

iHorse = con.iHorse
iBanana = con.iBanana
iCorn = con.iCorn
iCow = con.iCow
iPig = con.iPig
iSheep = con.iSheep
iWheat = con.iWheat
iSugar = con.iSugar
iWine = con.iWine
iCotton = con.iCotton
iDye = con.iDye
iRice = con.iRice
iFish = con.iFish
     

class Resources:
       	
        def checkTurn(self, iGameTurn):


                if (iGameTurn == 5): #otherwise it's picked by Portugal at the beginning
                        gc.getMap().plot(*geo.value('Resources.plot_1')).setImprovementType(con.iHut)


                if (iGameTurn == con.i450AD): #(dye added later to prevent Carthaginian UHV exploit)
                        gc.getMap().plot(*geo.value('Resources.plot_2')).setBonusType(iDye) #France
                        gc.getMap().plot(*geo.value('Resources.plot_3')).setBonusType(iDye) #England
                if (gc.getPlayer(con.iCeltia).getCivilizationType() == 4): #late start condition
                        if (iGameTurn == con.i600AD): 
                                gc.getMap().plot(*geo.value('Resources.plot_4')).setBonusType(iDye) #France
                                gc.getMap().plot(*geo.value('Resources.plot_5')).setBonusType(iDye) #England
                    
                if (iGameTurn == con.i1100AD):
                        #gc.getMap().plot(71, 30).setBonusType(iSugar) #Egypt
                        gc.getMap().plot(*geo.value('Resources.plot_7')).setBonusType(iSugar) #East Africa
                        gc.getMap().plot(*geo.value('Resources.plot_8')).setBonusType(iSugar) #Zimbabwe
                        gc.getMap().plot(*geo.value('Resources.plot_9')).setBonusType(iSugar) #South Africa

                        gc.getMap().plot(*geo.value('Resources.plot_10')).setBonusType(iBanana) #Central Africa
                        gc.getMap().plot(*geo.value('Resources.plot_11')).setBonusType(iBanana) #Central Africa

                if (iGameTurn == con.i1250AD):
                        gc.getMap().plot(*geo.value('Resources.plot_12')).setBonusType(iWheat) #Amsterdam
                        
                if (iGameTurn == con.i1600AD):
                        gc.getMap().plot(*geo.value('Resources.plot_13')).setBonusType(iCow) #Washington area
                        gc.getMap().plot(*geo.value('Resources.plot_14')).setBonusType(iCow) #New York area
                        gc.getMap().plot(*geo.value('Resources.plot_15')).setBonusType(iCow) #Lakes
                        gc.getMap().plot(*geo.value('Resources.plot_16')).setBonusType(iCow) #Jacksonville area
                        gc.getMap().plot(*geo.value('Resources.plot_17')).setBonusType(iCow) #Colorado
                        gc.getMap().plot(*geo.value('Resources.plot_18')).setBonusType(iCow) #California
                        gc.getMap().plot(*geo.value('Resources.plot_19')).setBonusType(iCow) #Texas
                        gc.getMap().plot(*geo.value('Resources.plot_20')).setBonusType(iCow) #Argentina
                        gc.getMap().plot(*geo.value('Resources.plot_21')).setBonusType(iCow) #Argentina
                        gc.getMap().plot(*geo.value('Resources.plot_22')).setBonusType(iCow) #Pampas

                        gc.getMap().plot(*geo.value('Resources.plot_23')).setBonusType(iCotton) #near Florida
                        gc.getMap().plot(*geo.value('Resources.plot_24')).setBonusType(iCotton) #Louisiana
                        gc.getMap().plot(*geo.value('Resources.plot_25')).setBonusType(iCotton) #Louisiana
                        gc.getMap().plot(*geo.value('Resources.plot_26')).setBonusType(iCotton) #California
                        
                        gc.getMap().plot(*geo.value('Resources.plot_27')).setBonusType(iPig) #Lakes
                        
                        gc.getMap().plot(*geo.value('Resources.plot_28')).setBonusType(iWheat) #Canadian border
                        gc.getMap().plot(*geo.value('Resources.plot_29')).setBonusType(iWheat) #Midwest

                        gc.getMap().plot(*geo.value('Resources.plot_30')).setBonusType(iBanana) #Guatemala
                        gc.getMap().plot(*geo.value('Resources.plot_31')).setBonusType(iBanana) #Colombia
                        gc.getMap().plot(*geo.value('Resources.plot_32')).setBonusType(iBanana) #Brazil
                        gc.getMap().plot(*geo.value('Resources.plot_33')).setBonusType(iBanana) #Brazil

                        gc.getMap().plot(*geo.value('Resources.plot_34')).setBonusType(iCorn) #Galicia
                        gc.getMap().plot(*geo.value('Resources.plot_35')).setBonusType(iCorn) #France
                        gc.getMap().plot(*geo.value('Resources.plot_36')).setBonusType(iCorn) #Romania

                        gc.getMap().plot(*geo.value('Resources.plot_37')).setBonusType(iCorn) #Manchuria
                       

                if (iGameTurn == con.i1700AD):
                        gc.getMap().plot(*geo.value('Resources.plot_38')).setBonusType(iHorse) #Washington area
                        gc.getMap().plot(*geo.value('Resources.plot_39')).setBonusType(iHorse) #Midwest
                        gc.getMap().plot(*geo.value('Resources.plot_40')).setBonusType(iHorse) #Texas
                        gc.getMap().plot(*geo.value('Resources.plot_41')).setBonusType(iHorse) #Brazil
                        gc.getMap().plot(*geo.value('Resources.plot_42')).setBonusType(iHorse) #Buenos Aires area
                        gc.getMap().plot(*geo.value('Resources.plot_43')).setBonusType(iHorse) #Pampas

                        gc.getMap().plot(*geo.value('Resources.plot_44')).setBonusType(iSugar) #Caribbean
                        gc.getMap().plot(*geo.value('Resources.plot_45')).setBonusType(iSugar) #Brazil
                        gc.getMap().plot(*geo.value('Resources.plot_46')).setBonusType(iSugar) #inner Brazil

                        gc.getMap().plot(*geo.value('Resources.plot_47')).setBonusType(iCorn) #Manchuria
                        gc.getMap().plot(*geo.value('Resources.plot_48')).setBonusType(iCorn) #India

                if (iGameTurn == con.i1850AD):
                        gc.getMap().plot(*geo.value('Resources.plot_49')).setBonusType(iWine) #California
                        gc.getMap().plot(*geo.value('Resources.plot_50')).setBonusType(iWine) #Andes

                        gc.getMap().plot(*geo.value('Resources.plot_51')).setBonusType(iSheep) #Australia
                        gc.getMap().plot(*geo.value('Resources.plot_52')).setBonusType(iSheep) #Australia
                        gc.getMap().plot(*geo.value('Resources.plot_53')).setBonusType(iSheep) #New Zealand

                        gc.getMap().plot(*geo.value('Resources.plot_54')).setBonusType(iHorse) #Mexico

                        gc.getMap().plot(*geo.value('Resources.plot_55')).setBonusType(iRice) #Vercelli
                        gc.getMap().plot(*geo.value('Resources.plot_56')).setBonusType(iRice) #California

                        gc.getMap().plot(*geo.value('Resources.plot_57')).setBonusType(iFish) #California




                
                #setImprovementType(ImprovementType eNewValue)
                #setPlotType(PlotType eNewValue, BOOL bRecalculate, BOOL bRebuildGraphics)
                #setTerrainType(TerrainType eNewValue, BOOL bRecalculate, BOOL bRebuildGraphics)


                        


            




                        
