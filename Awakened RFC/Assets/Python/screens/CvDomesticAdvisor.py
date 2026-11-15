"""Domestic advisor: stability, administration and a compact autonomy list."""
from CvPythonExtensions import *
import CvUtil
import re
import CvScreenEnums
import RFCUtils
import Administration as admin
import CivicNames

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
        self.X_SLIDERS = 20
        self.X_EXPENSES = 721
        self.PANE_WIDTH = 283
        self.Y_STABILITY = 480
        self.H_TREASURY = 50
        self.Y_SPACING = 30
        self.Y_PARAMETERS = 540
        self.TEXT_MARGIN = 15
        self.PARAMETERS_WIDTH = 176
        self.H_PARAMETERS = 160
        self.X_PARAMETERS1 = 20
        self.X_PARAMETERS2 = 222
        self.X_PARAMETERS3 = 424
        self.X_PARAMETERS4 = 626
        self.X_PARAMETERS5 = 828
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
        screen.setHelpTextArea(450, FontTypes.SMALL_FONT, 0, 0, -2.2, True, ArtFileMgr.getInterfaceArtInfo("POPUPS_BACKGROUND_TRANSPARENT").getPath(), True, True, CvUtil.FONT_LEFT_JUSTIFY, 0)
        self.drawContents()

    def label(self, name, content, x, y, size=3):
        self.getScreen().setLabel(name, '', u'<font=%d>%s</font>' % (size, content), CvUtil.FONT_LEFT_JUSTIFY, x, y, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

    def drawContents(self):
        screen = self.getScreen()
        player = gc.getPlayer(self.player)
        self.label('AdminTitle', text.getText('TXT_KEY_ADMIN_ADVISOR', ()), 30, 15, 4)
        effort, capacity = admin.value(self.player, admin.EFFORT), admin.value(self.player, admin.CAPACITY)
        effortText = admin.cost(effort)
        warningColor = '255,165,0,255'
        if effort > capacity:
            if effort * 4 >= capacity * 5:
                warningColor = '255,80,60,255'
            effortText = u'<color=%s>%s</color>' % (warningColor, effortText)
        summary = u'%s %s: %s / %s' % (admin.symbol(), text.getText('TXT_KEY_ADMIN_NAME', ()), effortText, admin.points(capacity))
        paused = admin.value(self.player, admin.PAUSED)
        overload = admin.value(self.player, admin.OVERLOAD)
        overloadText = u''
        effectsText = u''
        if overload > 0:
            overloadText = text.getText('TXT_KEY_ADMIN_OVERLOAD', (admin.number(overload),))
            effectsText = text.getText('TXT_KEY_ADMIN_EFFECTS', (admin.number(admin.value(self.player, admin.UPKEEP)), admin.value(self.player, admin.STABILITY), admin.number(admin.value(self.player, admin.PRODUCTION))))
        campaignText = u''
        if paused:
            campaignText = text.getText('TXT_KEY_ADMIN_PAUSED', ())
        summaryWidth = 300
        summaryHeight = 65
        if paused:
            summaryHeight = 105
        if overload > 0:
            summaryHeight = 150
        screen.addPanel('AdminSummary', '', '', True, True, 20, 65, summaryWidth, summaryHeight, PanelStyles.PANEL_STYLE_MAIN)
        self.label('AdminCapacity', summary, 40, 82, 4)
        # Remove previous labels when an empire returns below capacity.
        screen.deleteWidget('AdminOverload')
        screen.deleteWidget('AdminEffects')
        screen.deleteWidget('AdminCampaign')
        if paused:
            screen.addMultilineText('AdminCampaign', u'<font=2>%s</font>' % campaignText, 40, 120, summaryWidth - 40, 40, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
        if overload > 0:
            for name, content, y, height in [('AdminOverload', overloadText, 120, 30), ('AdminEffects', effectsText, 150, 58)]:
                content = re.sub(r'[-+]?\d+(?:[.,]\d+)?%?', r'<color=%s>\g<0></color>' % warningColor, content)
                screen.addMultilineText(name, u'<font=2>%s</font>' % content, 40, y, summaryWidth - 40, height, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
        self.drawCapacity(65 + summaryHeight + 15, capacity)
        self.drawStability()
        utils = RFCUtils.RFCUtils()
        screen.addPanel('AdminCityListPanel', '', '', True, True, 335, 65, 669, 405, PanelStyles.PANEL_STYLE_MAIN)
        headers = [('TXT_KEY_ADMIN_CITY', 15), ('TXT_KEY_ADMIN_POP', 180), ('TXT_KEY_ADMIN_TRAVEL', 270), ('TXT_KEY_ADMIN_NAME', 345)]
        for i, (key, x) in enumerate(headers):
            self.label('AdminColumn%d' % i, text.getText(key, ()), x + 340, 80, 2)
        screen.deleteWidget('AdminCities')
        screen.addScrollPanel('AdminCities', '', 340, 108, 659, 352, PanelStyles.PANEL_STYLE_EXTERNAL)
        city, iterator = player.firstCity(False)
        row = 0
        self.signature = (gc.getGame().getGameTurn(), effort, capacity, utils.getStability(self.player), player.getNumCities(), paused, tuple(self.capacityRows()))
        while city and not city.isNone():
            cid = city.getID()
            travel = admin.value(self.player, admin.TRAVEL, cid)
            cells = [(city.getName(), 15), (unicode(city.getPopulation()), 180), (admin.number(travel), 270), (admin.cost(admin.value(self.player, admin.CITY_EFFORT, cid)) + u' ' + admin.symbol(), 345)]
            for col, (content, x) in enumerate(cells):
                screen.setLabelAt('AdminCell%d_%d' % (cid, col), 'AdminCities', u'<font=2>%s</font>' % content, CvUtil.FONT_LEFT_JUSTIFY, x, row * 30 + 5, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
            if not city.isCapital() and player.getNumCities() > 1:
                screen.setImageButtonAt('AdminReleaseIcon%d' % cid, 'AdminCities', ArtFileMgr.getInterfaceArtInfo('INTERFACE_TECH_VASSAL').getPath(), 530, row * 30 + 2, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1)
                screen.setTextAt('AdminRelease%d' % cid, 'AdminCities', u'<font=2>%s</font>' % text.getText('TXT_KEY_ADMIN_RELEASE', ()), CvUtil.FONT_LEFT_JUSTIFY, 558, row * 30 + 5, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
            row += 1
            city, iterator = player.nextCity(iterator, False)
        self.drawConfirmation()

    def capacityRows(self):
        player = gc.getPlayer(self.player)
        rows = [text.getText('TXT_KEY_ADMIN_BASE_VALUE', (admin.value(self.player, admin.BASE_CAPACITY),))]
        for name in ('TECH_WRITING', 'TECH_CODE_OF_LAWS', 'TECH_CIVIL_SERVICE',
                'TECH_PRINTING_PRESS', 'TECH_CONSTITUTION', 'TECH_RADIO', 'TECH_COMPUTERS'):
            tech = gc.getInfoTypeForString(name)
            if gc.getTeam(player.getTeam()).isHasTech(tech):
                bonus = admin.value(self.player, admin.TECH_CAPACITY, tech)
                if bonus:
                    rows.append(self.capacityModifier(gc.getTechInfo(tech).getDescription(), bonus))
        modifiers = []
        for option in range(gc.getNumCivicOptionInfos()):
            civic = player.getCivics(option)
            bonus = admin.value(self.player, admin.CIVIC, civic)
            if bonus:
                modifiers.append(self.capacityModifier(CivicNames.description(civic, self.player), bonus, True))
        for name in ('BUILDING_PYRAMID', 'BUILDING_GREAT_LIBRARY', 'BUILDING_VERSAILLES'):
            building = gc.getInfoTypeForString(name)
            bonus = admin.value(self.player, admin.WONDER_CAPACITY, building)
            if bonus:
                buildingClass = gc.getBuildingInfo(building).getBuildingClassType()
                variant = gc.getCivilizationInfo(player.getCivilizationType()).getCivilizationBuildings(buildingClass)
                if variant >= 0:
                    building = variant
                modifiers.append(self.capacityModifier(gc.getBuildingInfo(building).getDescription(), bonus, True))
        return (tuple(rows), tuple(modifiers))

    def capacityModifier(self, name, value, percent=False):
        color = '255,80,60,255'
        if value > 0:
            color = '80,220,100,255'
        amount = u'%+d' % value
        if percent:
            amount += u'%'
        return u'<color=%s>%s: %s</color>' % (color, name, amount)

    def drawCapacity(self, y, capacity):
        screen = self.getScreen()
        height = 470 - y
        screen.addPanel('AdminMaximumPanel', '', '', True, True, 20, y, 300, height, PanelStyles.PANEL_STYLE_MAIN)
        self.label('AdminMaximumTitle', text.getText('TXT_KEY_ADMIN_MAXIMUM_VALUE', (capacity // 100,)), 40, y + 17, 3)
        screen.deleteWidget('AdminCapacityRows')
        screen.addScrollPanel('AdminCapacityRows', '', 30, y + 45, 280, height - 55, PanelStyles.PANEL_STYLE_EXTERNAL)
        baseRows, modifiers = self.capacityRows()
        for row, content in enumerate(baseRows + modifiers):
            screen.setLabelAt('AdminCapacityRow%d' % row, 'AdminCapacityRows', u'<font=2>%s</font>' % content, CvUtil.FONT_LEFT_JUSTIFY, 10, row * 21, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

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
        signature = (gc.getGame().getGameTurn(), admin.value(self.player, admin.EFFORT), admin.value(self.player, admin.CAPACITY), RFCUtils.RFCUtils().getStability(self.player), player.getNumCities(), admin.value(self.player, admin.PAUSED), tuple(self.capacityRows()))
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
        screen.setLabel(self.getNextWidgetName(), szStabilityPanel, u"<font=4>" + text.getText("TXT_KEY_STABILITY_ADVISOR_TITLE", ()).upper() + " " + szTempBuffer + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, (self.X_SLIDERS + self.PANE_WIDTH + self.X_EXPENSES)/2, self.Y_STABILITY + self.H_TREASURY/2 - self.Y_SPACING/2, self.Z_CONTROLS, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, 7105, 0 )

        szParametersPanel1 = self.getNextWidgetName()
        screen.addPanel(szParametersPanel1, u"", "", True, True, self.X_PARAMETERS1, self.Y_PARAMETERS, self.PARAMETERS_WIDTH, self.H_PARAMETERS, PanelStyles.PANEL_STYLE_MAIN )
        screen.setLabel(self.getNextWidgetName(), "Background",  u"<font=3>" + text.getText("TXT_KEY_STABILITY_PARAMETER_CITIES", ()).upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, self.X_PARAMETERS1 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, 7105, 1 )
        iParameter1 = utils.getParCities()
        if (iParameter1 <= -25):
                self.printStars(ePlayer, 1, self.getNextWidgetName(), 1, self.X_PARAMETERS1 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter1 <= -10):
                self.printStars(ePlayer, 1, self.getNextWidgetName(), 2, self.X_PARAMETERS1 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter1 < 10):
                self.printStars(ePlayer, 1, self.getNextWidgetName(), 3, self.X_PARAMETERS1 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter1 < 25):
                self.printStars(ePlayer, 1, self.getNextWidgetName(), 4, self.X_PARAMETERS1 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        else:
                self.printStars(ePlayer, 1, self.getNextWidgetName(), 5, self.X_PARAMETERS1 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        self.printNumber(ePlayer, self.getNextWidgetName(), 1, self.X_PARAMETERS1 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 60, self.Z_CONTROLS + self.DZ)
        self.printArrow(ePlayer, self.getNextWidgetName(), 1, self.X_PARAMETERS1 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 90, self.Z_CONTROLS + self.DZ)

        szParametersPanel2 = self.getNextWidgetName()
        screen.addPanel(szParametersPanel2, u"", "", True, True, self.X_PARAMETERS2, self.Y_PARAMETERS, self.PARAMETERS_WIDTH, self.H_PARAMETERS, PanelStyles.PANEL_STYLE_MAIN )
        screen.setLabel(self.getNextWidgetName(), "Background",  u"<font=3>" + text.getText("TXT_KEY_STABILITY_PARAMETER_CIVICS", ()).upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, self.X_PARAMETERS2 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, 7105, 2 )
        iParameter2 = utils.getParCivics()
        if (iParameter2 <= -30):
                self.printStars(ePlayer, 2, self.getNextWidgetName(), 1, self.X_PARAMETERS2 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter2 <= -15):
                self.printStars(ePlayer, 2, self.getNextWidgetName(), 2, self.X_PARAMETERS2 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter2 <= 4):
                self.printStars(ePlayer, 2, self.getNextWidgetName(), 3, self.X_PARAMETERS2 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter2 <= 10):
                self.printStars(ePlayer, 2, self.getNextWidgetName(), 4, self.X_PARAMETERS2 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        else:
                self.printStars(ePlayer, 2, self.getNextWidgetName(), 5, self.X_PARAMETERS2 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        self.printNumber(ePlayer, self.getNextWidgetName(), 2, self.X_PARAMETERS2 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 60, self.Z_CONTROLS + self.DZ)
        self.printArrow(ePlayer, self.getNextWidgetName(), 2, self.X_PARAMETERS2 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 90, self.Z_CONTROLS + self.DZ)

        szParametersPanel3 = self.getNextWidgetName()
        screen.addPanel(szParametersPanel3, u"", "", True, True, self.X_PARAMETERS3, self.Y_PARAMETERS, self.PARAMETERS_WIDTH, self.H_PARAMETERS, PanelStyles.PANEL_STYLE_MAIN )
        screen.setLabel(self.getNextWidgetName(), "Background",  u"<font=3>" + text.getText("TXT_KEY_STABILITY_PARAMETER_ECONOMY", ()).upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, self.X_PARAMETERS3 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, 7105, 3 )
        iParameter3 = utils.getParEconomy()
        if (iParameter3 <= -40):
                self.printStars(ePlayer, 3, self.getNextWidgetName(), 1, self.X_PARAMETERS3 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter3 <= -15):
                self.printStars(ePlayer, 3, self.getNextWidgetName(), 2, self.X_PARAMETERS3 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter3 < 30):
                self.printStars(ePlayer, 3, self.getNextWidgetName(), 3, self.X_PARAMETERS3 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter3 < 60):
                self.printStars(ePlayer, 3, self.getNextWidgetName(), 4, self.X_PARAMETERS3 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        else:
                self.printStars(ePlayer, 3, self.getNextWidgetName(), 5, self.X_PARAMETERS3 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        self.printNumber(ePlayer, self.getNextWidgetName(), 3, self.X_PARAMETERS3 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 60, self.Z_CONTROLS + self.DZ)
        self.printArrow(ePlayer, self.getNextWidgetName(), 3, self.X_PARAMETERS3 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 90, self.Z_CONTROLS + self.DZ)

        szParametersPanel4 = self.getNextWidgetName()
        screen.addPanel(szParametersPanel4, u"", "", True, True, self.X_PARAMETERS4, self.Y_PARAMETERS, self.PARAMETERS_WIDTH, self.H_PARAMETERS, PanelStyles.PANEL_STYLE_MAIN )
        screen.setLabel(self.getNextWidgetName(), "Background",  u"<font=3>" + text.getText("TXT_KEY_STABILITY_PARAMETER_EXPANSION", ()).upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, self.X_PARAMETERS4 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, 7105, 4 )
        iParameter4 = utils.getParExpansion()
        if (iParameter4 <= -40):
                self.printStars(ePlayer, 4, self.getNextWidgetName(), 1, self.X_PARAMETERS4 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter4 <= -15):
                self.printStars(ePlayer, 4, self.getNextWidgetName(), 2, self.X_PARAMETERS4 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter4 < 15):
                self.printStars(ePlayer, 4, self.getNextWidgetName(), 3, self.X_PARAMETERS4 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter4 < 40):
                self.printStars(ePlayer, 4, self.getNextWidgetName(), 4, self.X_PARAMETERS4 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        else:
                self.printStars(ePlayer, 4, self.getNextWidgetName(), 5, self.X_PARAMETERS4 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        self.printNumber(ePlayer, self.getNextWidgetName(), 4, self.X_PARAMETERS4 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 60, self.Z_CONTROLS + self.DZ)
        self.printArrow(ePlayer, self.getNextWidgetName(), 4, self.X_PARAMETERS4 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 90, self.Z_CONTROLS + self.DZ)

        szParametersPanel5 = self.getNextWidgetName()
        screen.addPanel(szParametersPanel5, u"", "", True, True, self.X_PARAMETERS5, self.Y_PARAMETERS, self.PARAMETERS_WIDTH, self.H_PARAMETERS, PanelStyles.PANEL_STYLE_MAIN )
        screen.setLabel(self.getNextWidgetName(), "Background",  u"<font=3>" + text.getText("TXT_KEY_STABILITY_PARAMETER_FOREIGN", ()).upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, self.X_PARAMETERS5 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, 7105, 5 )
        iParameter5 = utils.getParDiplomacy()
        if (iParameter5 <= -20):
                self.printStars(ePlayer, 5, self.getNextWidgetName(), 1, self.X_PARAMETERS5 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter5 <= -10):
                self.printStars(ePlayer, 5, self.getNextWidgetName(), 2, self.X_PARAMETERS5 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter5 < 8):
                self.printStars(ePlayer, 5, self.getNextWidgetName(), 3, self.X_PARAMETERS5 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        elif (iParameter5 < 16):
                self.printStars(ePlayer, 5, self.getNextWidgetName(), 4, self.X_PARAMETERS5 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        else:
                self.printStars(ePlayer, 5, self.getNextWidgetName(), 5, self.X_PARAMETERS5 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 40, self.Z_CONTROLS + self.DZ)
        self.printNumber(ePlayer, self.getNextWidgetName(), 5, self.X_PARAMETERS5 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 60, self.Z_CONTROLS + self.DZ)
        self.printArrow(ePlayer, self.getNextWidgetName(), 5, self.X_PARAMETERS5 + self.PARAMETERS_WIDTH/2, self.Y_PARAMETERS + self.TEXT_MARGIN + 90, self.Z_CONTROLS + self.DZ)


        #Rhye - end             



    def printStars(self, ePlayer, iParameter, panel, n, x, y, z):
            #RFCMP
            if (not gc.getGame().isHotSeat() and not gc.getGame().isPbem()):
                    totStars = ""
                    for i in range(n):
                        totStars = totStars + unichr(CyGame().getSymbolID(FontSymbols.SILVER_STAR_CHAR))
                    if (gc.getPlayer(ePlayer).isHuman()):
                            self.getScreen().setLabel(panel, "Background",  totStars, CvUtil.FONT_CENTER_JUSTIFY, x, y, z, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, 7105, iParameter )

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
                            self.getScreen().setLabel(panel, "Background",  "(" + number + ")", CvUtil.FONT_CENTER_JUSTIFY, x, y, z, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, 7105, iParameter )

    def printArrow(self, ePlayer, panel, iParameter, x, y, z):
            #RFCMP
            if (not gc.getGame().isHotSeat() and not gc.getGame().isPbem()):
                    if (gc.getPlayer(ePlayer).isHuman()):
                            self.getScreen().setLabel(panel, "Background",  unichr(CyGame().getSymbolID(FontSymbols.POWER_CHAR) + 8 + utils.getArrow(iParameter)), CvUtil.FONT_CENTER_JUSTIFY, x, y, z, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, 7105, iParameter )

    #Rhye - end

