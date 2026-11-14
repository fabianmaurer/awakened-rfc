"""Domestic advisor: stability, administration and a compact autonomy list."""
from CvPythonExtensions import *
import CvUtil
import re
import CvScreenEnums
import RFCUtils
import Administration as admin
import ScenarioGeography as geo

gc = CyGlobalContext()
text = CyTranslator()
utils = RFCUtils.RFCUtils()
ArtFileMgr = CyArtFileMgr()


class CvDomesticAdvisor:
    def __init__(self):
        self.player = -1
        self.pending = None
        self.elapsed = 0
        self.signature = None
        self.stabilityWidgets = 0
        self.X_SLIDERS = 50
        self.X_EXPENSES = 696
        self.PANE_WIDTH = 283
        self.Y_STABILITY = 225
        self.H_TREASURY = 50
        self.Y_SPACING = 30
        self.Y_PARAMETERS = 285
        self.TEXT_MARGIN = 15
        self.PARAMETERS_WIDTH = 170
        self.H_PARAMETERS = 140
        self.X_PARAMETERS1 = 50
        self.X_PARAMETERS2 = 240
        self.X_PARAMETERS3 = 430
        self.X_PARAMETERS4 = 620
        self.X_PARAMETERS5 = 810
        self.Z_CONTROLS = -2.3
        self.DZ = -0.2

    def getScreen(self):
        return CyGInterfaceScreen('DomesticAdvisor', CvScreenEnums.DOMESTIC_ADVISOR)

    def interfaceScreen(self):
        self.player = gc.getGame().getActivePlayer()
        if self.player < 0:
            return
        self.pending = None
        screen = self.getScreen()
        if screen.isActive():
            return
        screen.setRenderInterfaceOnly(True)
        screen.setDimensions(screen.centerX(0), screen.centerY(0), 1024, 768)
        screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
        screen.addDDSGFC('AdminBackground', ArtFileMgr.getInterfaceArtInfo('MAINMENU_SLIDESHOW_LOAD').getPath(), 0, 0, 1024, 768, WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.showWindowBackground(False)
        screen.addPanel('AdminTop', '', '', True, False, 0, 0, 1024, 55, PanelStyles.PANEL_STYLE_TOPBAR)
        screen.addPanel('AdminBottom', '', '', True, False, 0, 713, 1024, 55, PanelStyles.PANEL_STYLE_BOTTOMBAR)
        screen.setText('AdminExit', '', text.getText('TXT_KEY_PEDIA_SCREEN_EXIT', ()), CvUtil.FONT_RIGHT_JUSTIFY, 994, 730, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1)
        self.drawContents()

    def label(self, name, content, x, y, size=3):
        self.getScreen().setLabel(name, '', u'<font=%d>%s</font>' % (size, content), CvUtil.FONT_LEFT_JUSTIFY, x, y, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

    def drawContents(self):
        screen = self.getScreen()
        player = gc.getPlayer(self.player)
        self.label('AdminTitle', text.getText('TXT_KEY_ADMIN_ADVISOR', ()), 30, 15, 4)
        screen.addPanel('AdminSummary', '', '', True, True, 20, 65, 984, 150, PanelStyles.PANEL_STYLE_MAIN)
        effort, capacity = admin.value(self.player, admin.EFFORT), admin.value(self.player, admin.CAPACITY)
        effortText = admin.cost(effort)
        warningColor = '255,165,0,255'
        if effort > capacity:
            if effort * 4 >= capacity * 5:
                warningColor = '255,80,60,255'
            effortText = u'<color=%s>%s</color>' % (warningColor, effortText)
        summary = u'%s %s: %s / %s' % (admin.symbol(), text.getText('TXT_KEY_ADMIN_NAME', ()), effortText, admin.points(capacity))
        self.label('AdminCapacity', summary, 40, 82, 4)
        # Remove previous labels when an empire returns below capacity.
        screen.deleteWidget('AdminOverload')
        screen.deleteWidget('AdminEffects')
        screen.deleteWidget('AdminCampaign')
        paused = admin.value(self.player, admin.PAUSED)
        if paused:
            self.label('AdminCampaign', text.getText('TXT_KEY_ADMIN_PAUSED', ()), 40, 125, 2)
        overload = admin.value(self.player, admin.OVERLOAD)
        if overload > 0:
            overloadText = text.getText('TXT_KEY_ADMIN_OVERLOAD', (admin.number(overload),))
            effectsText = text.getText('TXT_KEY_ADMIN_EFFECTS', (admin.number(admin.value(self.player, admin.UPKEEP)), admin.value(self.player, admin.STABILITY), admin.number(admin.value(self.player, admin.PRODUCTION))))
            for name, content, y in [('AdminOverload', overloadText, 125), ('AdminEffects', effectsText, 165)]:
                content = re.sub(r'[-+]?\d+(?:[.,]\d+)?%?', r'<color=%s>\g<0></color>' % warningColor, content)
                self.label(name, content, 40, y)
        self.drawStability()
        utils = RFCUtils.RFCUtils()
        screen.addPanel('AdminCityListPanel', '', '', True, True, 20, 435, 984, 265, PanelStyles.PANEL_STYLE_MAIN)
        headers = [('TXT_KEY_ADMIN_CITY', 15), ('TXT_KEY_ADMIN_POP', 245), ('TXT_KEY_ADMIN_TRAVEL', 345), ('TXT_KEY_ADMIN_NAME', 455), ('TXT_KEY_ADMIN_CONTROL', 610)]
        for i, (key, x) in enumerate(headers):
            self.label('AdminColumn%d' % i, text.getText(key, ()), x + 25, 445, 2)
        screen.deleteWidget('AdminCities')
        screen.addScrollPanel('AdminCities', '', 25, 473, 974, 222, PanelStyles.PANEL_STYLE_EXTERNAL)
        city, iterator = player.firstCity(False)
        row = 0
        self.signature = (gc.getGame().getGameTurn(), effort, capacity, utils.getStability(self.player), player.getNumCities(), paused)
        while city and not city.isNone():
            cid = city.getID()
            travel = admin.value(self.player, admin.TRAVEL, cid)
            limit = 5
            if geo.turns(1) == 2:
                limit = 10
            left = limit - admin.isolation(city)
            status = u'-'
            if not admin.value(self.player, admin.CONNECTED, cid):
                status = text.getText('TXT_KEY_ADMIN_CONTROL_LOST_IN', (max(0, left),))
                if paused:
                    status = text.getText('TXT_KEY_ADMIN_CONTROL_PAUSED', ())
            cells = [(city.getName(), 15), (unicode(city.getPopulation()), 245), (admin.number(travel), 345), (admin.cost(admin.value(self.player, admin.CITY_EFFORT, cid)) + u' ' + admin.symbol(), 455), (status, 610)]
            for col, (content, x) in enumerate(cells):
                screen.setLabelAt('AdminCell%d_%d' % (cid, col), 'AdminCities', u'<font=2>%s</font>' % content, CvUtil.FONT_LEFT_JUSTIFY, x, row * 30 + 5, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
            if not city.isCapital() and player.getNumCities() > 1:
                screen.setImageButtonAt('AdminReleaseIcon%d' % cid, 'AdminCities', ArtFileMgr.getInterfaceArtInfo('INTERFACE_TECH_VASSAL').getPath(), 770, row * 30 + 2, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1)
                screen.setTextAt('AdminRelease%d' % cid, 'AdminCities', u'<font=2>%s</font>' % text.getText('TXT_KEY_ADMIN_RELEASE', ()), CvUtil.FONT_LEFT_JUSTIFY, 803, row * 30 + 5, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
            row += 1
            city, iterator = player.nextCity(iterator, False)
        self.drawConfirmation()

    def drawConfirmation(self):
        screen = self.getScreen()
        for widget in ['AdminConfirmPanel', 'AdminConfirmTitle', 'AdminConfirmVassal', 'AdminConfirmIndependent', 'AdminConfirmCancel']:
            screen.deleteWidget(widget)
        if self.pending is None:
            return
        city = gc.getPlayer(self.player).getCity(self.pending)
        if city.isNone():
            self.pending = None
            return
        screen.addPanel('AdminConfirmPanel', '', '', True, True, 130, 280, 764, 160, PanelStyles.PANEL_STYLE_MAIN)
        self.label('AdminConfirmTitle', text.getText('TXT_KEY_ADMIN_RELEASE_CONFIRM', (city.getName(),)), 155, 300, 3)
        target = gc.getPlayer(self.player).getAdministrationReleaseTarget(city.getID())
        if target >= 0:
            screen.setText('AdminConfirmVassal', '', text.getText('TXT_KEY_ADMIN_RELEASE_VASSAL', (gc.getPlayer(target).getCivilizationShortDescription(0),)), CvUtil.FONT_LEFT_JUSTIFY, 155, 345, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.setText('AdminConfirmIndependent', '', text.getText('TXT_KEY_ADMIN_RELEASE_INDEPENDENT', ()), CvUtil.FONT_LEFT_JUSTIFY, 155, 380, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.setText('AdminConfirmCancel', '', text.getText('TXT_KEY_SCREEN_CANCEL', ()), CvUtil.FONT_RIGHT_JUSTIFY, 860, 405, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

    def handleInput(self, event):
        if event.getNotifyCode() != NotifyCode.NOTIFY_CLICKED:
            return 0
        name = event.getFunctionName()
        if name in ('AdminRelease', 'AdminReleaseIcon'):
            self.pending = event.getID()
            self.drawConfirmation()
        elif name == 'AdminConfirmCancel':
            self.pending = None
            self.drawConfirmation()
        elif name in ('AdminConfirmVassal', 'AdminConfirmIndependent') and self.pending is not None:
            player = gc.getPlayer(self.player)
            city = player.getCity(self.pending)
            if not city.isNone():
                target = player.getAdministrationReleaseTarget(city.getID())
                if name == 'AdminConfirmIndependent':
                    target = -2
                if target == -2 or target >= 0:
                    admin.requestRelease(city, target)
            self.pending = None
            self.drawConfirmation()
        return 0

    def update(self, delta):
        self.elapsed += delta
        if self.elapsed < 0.5 or self.player < 0:
            return
        self.elapsed = 0
        if gc.getGame().getActivePlayer() != self.player:
            self.getScreen().hideScreen()
            return
        player = gc.getPlayer(self.player)
        signature = (gc.getGame().getGameTurn(), admin.value(self.player, admin.EFFORT), admin.value(self.player, admin.CAPACITY), RFCUtils.RFCUtils().getStability(self.player), player.getNumCities(), admin.value(self.player, admin.PAUSED))
        if signature != self.signature:
            self.drawContents()

    def getNextWidgetName(self):
        name = 'AdminStabilityWidget%d' % self.stabilityWidgets
        self.stabilityWidgets += 1
        return name

    def drawStability(self):
        screen = self.getScreen()
        for i in range(self.stabilityWidgets):
            screen.deleteWidget('AdminStabilityWidget%d' % i)
        self.stabilityWidgets = 0
        ePlayer = self.player #Rhye
        #Rhye - start
        iStability = utils.getStability(ePlayer)
        if (iStability < -40):
                szTempBuffer = text.getText("TXT_KEY_STABILITY_COLLAPSING", ())
        elif (iStability >= -40 and iStability < -20):
                szTempBuffer = text.getText("TXT_KEY_STABILITY_UNSTABLE", ())
        elif (iStability >= -20 and iStability < 0):
                szTempBuffer = text.getText("TXT_KEY_STABILITY_SHAKY", ())
        elif (iStability >= 0 and iStability < 20):
                szTempBuffer = text.getText("TXT_KEY_STABILITY_STABLE", ())
        elif (iStability >= 20 and iStability < 40):
                szTempBuffer = text.getText("TXT_KEY_STABILITY_SOLID", ())
        elif (iStability >= 40):
                szTempBuffer = text.getText("TXT_KEY_STABILITY_VERYSOLID", ())

        #RFCMP
        if (gc.getPlayer(ePlayer).isHuman()):
                if (not gc.getGame().isHotSeat() and not gc.getGame().isPbem()):
                        number = str(iStability)
                        if (iStability > 0):
                                number = '+' + number
                        szTempBuffer = szTempBuffer + " (" + number + ") " + unichr(CyGame().getSymbolID(FontSymbols.POWER_CHAR) + 8 + utils.getArrow(0))
                else:
                        number = str(iStability)
                        if (iStability > 0):
                                number = '+' + number
                        szTempBuffer = szTempBuffer + " (" + number + ") "


        #Rhye - end

        #Rhye - start
        szStabilityPanel = self.getNextWidgetName()
        screen.addPanel(szStabilityPanel, u"", "", True, True, self.X_SLIDERS, self.Y_STABILITY, self.X_EXPENSES + self.PANE_WIDTH - self.X_SLIDERS, self.H_TREASURY, PanelStyles.PANEL_STYLE_MAIN )
        screen.setLabel(self.getNextWidgetName(), szStabilityPanel, u"<font=4>" + text.getText("TXT_KEY_STABILITY_ADVISOR_TITLE", ()).upper() + " " + szTempBuffer + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, (self.X_SLIDERS + self.PANE_WIDTH + self.X_EXPENSES)/2, self.Y_STABILITY + self.H_TREASURY/2 - self.Y_SPACING/2, self.Z_CONTROLS, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

        szParametersPanel1 = self.getNextWidgetName()
        screen.addPanel(szParametersPanel1, u"", "", True, True, self.X_PARAMETERS1, self.Y_PARAMETERS, self.PARAMETERS_WIDTH, self.H_PARAMETERS, PanelStyles.PANEL_STYLE_MAIN )
        screen.setLabel(self.getNextWidgetName(), "Background",  u"<font=3>" + text.getText("TXT_KEY_STABILITY_PARAMETER_CITIES", ()).upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, self.X_PARAMETERS1 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
        iParameter1 = utils.getParCities()
        if (iParameter1 <= -25):
                self.printStars(ePlayer, self.getNextWidgetName(), 1, self.X_PARAMETERS1 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter1 <= -10):
                self.printStars(ePlayer, self.getNextWidgetName(), 2, self.X_PARAMETERS1 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter1 < 10):
                self.printStars(ePlayer, self.getNextWidgetName(), 3, self.X_PARAMETERS1 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter1 < 25):
                self.printStars(ePlayer, self.getNextWidgetName(), 4, self.X_PARAMETERS1 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        else:
                self.printStars(ePlayer, self.getNextWidgetName(), 5, self.X_PARAMETERS1 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        self.printNumber(ePlayer, self.getNextWidgetName(), 1, self.X_PARAMETERS1 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 60, self.Z_CONTROLS + self.DZ)
        self.printArrow(ePlayer, self.getNextWidgetName(), 1, self.X_PARAMETERS1 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 90, self.Z_CONTROLS + self.DZ)

        szParametersPanel2 = self.getNextWidgetName()
        screen.addPanel(szParametersPanel2, u"", "", True, True, self.X_PARAMETERS2, self.Y_PARAMETERS, self.PARAMETERS_WIDTH, self.H_PARAMETERS, PanelStyles.PANEL_STYLE_MAIN )
        screen.setLabel(self.getNextWidgetName(), "Background",  u"<font=3>" + text.getText("TXT_KEY_STABILITY_PARAMETER_CIVICS", ()).upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, self.X_PARAMETERS2 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
        iParameter2 = utils.getParCivics()
        if (iParameter2 <= -30):
                self.printStars(ePlayer, self.getNextWidgetName(), 1, self.X_PARAMETERS2 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter2 <= -15):
                self.printStars(ePlayer, self.getNextWidgetName(), 2, self.X_PARAMETERS2 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter2 <= 4):
                self.printStars(ePlayer, self.getNextWidgetName(), 3, self.X_PARAMETERS2 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter2 <= 10):
                self.printStars(ePlayer, self.getNextWidgetName(), 4, self.X_PARAMETERS2 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        else:
                self.printStars(ePlayer, self.getNextWidgetName(), 5, self.X_PARAMETERS2 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        self.printNumber(ePlayer, self.getNextWidgetName(), 2, self.X_PARAMETERS2 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 60, self.Z_CONTROLS + self.DZ)
        self.printArrow(ePlayer, self.getNextWidgetName(), 2, self.X_PARAMETERS2 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 90, self.Z_CONTROLS + self.DZ)

        szParametersPanel3 = self.getNextWidgetName()
        screen.addPanel(szParametersPanel3, u"", "", True, True, self.X_PARAMETERS3, self.Y_PARAMETERS, self.PARAMETERS_WIDTH, self.H_PARAMETERS, PanelStyles.PANEL_STYLE_MAIN )
        screen.setLabel(self.getNextWidgetName(), "Background",  u"<font=3>" + text.getText("TXT_KEY_STABILITY_PARAMETER_ECONOMY", ()).upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, self.X_PARAMETERS3 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
        iParameter3 = utils.getParEconomy()
        if (iParameter3 <= -40):
                self.printStars(ePlayer, self.getNextWidgetName(), 1, self.X_PARAMETERS3 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter3 <= -15):
                self.printStars(ePlayer, self.getNextWidgetName(), 2, self.X_PARAMETERS3 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter3 < 30):
                self.printStars(ePlayer, self.getNextWidgetName(), 3, self.X_PARAMETERS3 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter3 < 60):
                self.printStars(ePlayer, self.getNextWidgetName(), 4, self.X_PARAMETERS3 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        else:
                self.printStars(ePlayer, self.getNextWidgetName(), 5, self.X_PARAMETERS3 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        self.printNumber(ePlayer, self.getNextWidgetName(), 3, self.X_PARAMETERS3 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 60, self.Z_CONTROLS + self.DZ)
        self.printArrow(ePlayer, self.getNextWidgetName(), 3, self.X_PARAMETERS3 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 90, self.Z_CONTROLS + self.DZ)

        szParametersPanel4 = self.getNextWidgetName()
        screen.addPanel(szParametersPanel4, u"", "", True, True, self.X_PARAMETERS4, self.Y_PARAMETERS, self.PARAMETERS_WIDTH, self.H_PARAMETERS, PanelStyles.PANEL_STYLE_MAIN )
        screen.setLabel(self.getNextWidgetName(), "Background",  u"<font=3>" + text.getText("TXT_KEY_STABILITY_PARAMETER_EXPANSION", ()).upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, self.X_PARAMETERS4 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
        iParameter4 = utils.getParExpansion()
        if (iParameter4 <= -40):
                self.printStars(ePlayer, self.getNextWidgetName(), 1, self.X_PARAMETERS4 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter4 <= -15):
                self.printStars(ePlayer, self.getNextWidgetName(), 2, self.X_PARAMETERS4 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter4 < 15):
                self.printStars(ePlayer, self.getNextWidgetName(), 3, self.X_PARAMETERS4 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter4 < 40):
                self.printStars(ePlayer, self.getNextWidgetName(), 4, self.X_PARAMETERS4 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        else:
                self.printStars(ePlayer, self.getNextWidgetName(), 5, self.X_PARAMETERS4 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        self.printNumber(ePlayer, self.getNextWidgetName(), 4, self.X_PARAMETERS4 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 60, self.Z_CONTROLS + self.DZ)
        self.printArrow(ePlayer, self.getNextWidgetName(), 4, self.X_PARAMETERS4 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 90, self.Z_CONTROLS + self.DZ)

        szParametersPanel5 = self.getNextWidgetName()
        screen.addPanel(szParametersPanel5, u"", "", True, True, self.X_PARAMETERS5, self.Y_PARAMETERS, self.PARAMETERS_WIDTH, self.H_PARAMETERS, PanelStyles.PANEL_STYLE_MAIN )
        screen.setLabel(self.getNextWidgetName(), "Background",  u"<font=3>" + text.getText("TXT_KEY_STABILITY_PARAMETER_FOREIGN", ()).upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, self.X_PARAMETERS5 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
        iParameter5 = utils.getParDiplomacy()
        if (iParameter5 <= -20):
                self.printStars(ePlayer, self.getNextWidgetName(), 1, self.X_PARAMETERS5 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter5 <= -10):
                self.printStars(ePlayer, self.getNextWidgetName(), 2, self.X_PARAMETERS5 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter5 < 8):
                self.printStars(ePlayer, self.getNextWidgetName(), 3, self.X_PARAMETERS5 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter5 < 16):
                self.printStars(ePlayer, self.getNextWidgetName(), 4, self.X_PARAMETERS5 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        else:
                self.printStars(ePlayer, self.getNextWidgetName(), 5, self.X_PARAMETERS5 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        self.printNumber(ePlayer, self.getNextWidgetName(), 5, self.X_PARAMETERS5 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 60, self.Z_CONTROLS + self.DZ)
        self.printArrow(ePlayer, self.getNextWidgetName(), 5, self.X_PARAMETERS5 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 90, self.Z_CONTROLS + self.DZ)


        #Rhye - end             



    def printStars(self, ePlayer, panel, n, x, y, z):
            #RFCMP
            if (not gc.getGame().isHotSeat() and not gc.getGame().isPbem()):
                    totStars = ""
                    for i in range(n):
                        totStars = totStars + unichr(CyGame().getSymbolID(FontSymbols.SILVER_STAR_CHAR))
                    if (gc.getPlayer(ePlayer).isHuman()):
                            self.getScreen().setLabel(panel, "Background",  totStars, CvUtil.FONT_CENTER_JUSTIFY, x, y, z, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

    def printNumber(self, ePlayer, panel, iParameter, x, y, z):
            if (not gc.getGame().isHotSeat() and not gc.getGame().isPbem()):
                    if (gc.getPlayer(ePlayer).isHuman()):
                            if (iParameter == 1):
                                    iNewValue = utils.getParCities()
                            elif (iParameter == 2):
                                    iNewValue = utils.getParCivics()
                            elif (iParameter == 3):
                                    iNewValue = utils.getParEconomy()
                            elif (iParameter == 4):
                                    iNewValue = utils.getParExpansion()
                            elif (iParameter == 5):
                                    iNewValue = utils.getParDiplomacy()
                            number = str(iNewValue)
                            if (iNewValue > 0):
                                    number = '+' + number
                            self.getScreen().setLabel(panel, "Background",  "(" + number + ")", CvUtil.FONT_CENTER_JUSTIFY, x, y, z, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

    def printArrow(self, ePlayer, panel, iParameter, x, y, z):
            #RFCMP
            if (not gc.getGame().isHotSeat() and not gc.getGame().isPbem()):
                    if (gc.getPlayer(ePlayer).isHuman()):
                            self.getScreen().setLabel(panel, "Background",  unichr(CyGame().getSymbolID(FontSymbols.POWER_CHAR) + 8 + utils.getArrow(iParameter)), CvUtil.FONT_CENTER_JUSTIFY, x, y, z, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

    #Rhye - end

