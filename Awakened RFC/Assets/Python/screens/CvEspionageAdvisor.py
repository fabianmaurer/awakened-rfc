# Awakened RFC intelligence advisor. Compatible with Civ4 Python 2.4.
from CvPythonExtensions import *
import CvUtil
import CvScreenEnums
import Consts as con

gc = CyGlobalContext()
text = CyTranslator()
art = CyArtFileMgr()

INTEL_ART = "Art/Interface/Buttons/Intelligence/"
PANEL_COLOR = (42, 42, 46)
TILE_COLOR = (55, 55, 60)
SELECTED_COLOR = (158, 0, 0)


def tr(key, args=()):
    return text.getText("TXT_KEY_INTEL_" + key, args)


class CvEspionageAdvisor:
    def __init__(self):
        self.SCREEN_NAME = "EspionageAdvisor"
        self.iTargetPlayer = -1
        self.widgets = []
        self.lastRate = -1
        self.lastPercent = -1

    def getScreen(self):
        return CyGInterfaceScreen(self.SCREEN_NAME, CvScreenEnums.ESPIONAGE_ADVISOR)

    def name(self):
        name = "IntelWidget%d" % len(self.widgets)
        self.widgets.append(name)
        return name

    def label(self, value, x, y, large=False):
        size = "3b"
        if not large:
            size = "2"
        self.getScreen().setLabel(self.name(), "Background", u"<font=%s><color=230,230,235,255>%s</color></font>" % (size, value),
            CvUtil.FONT_LEFT_JUSTIFY, x, y, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

    def body(self, value, x, y, w, h):
        self.getScreen().addMultilineText(self.name(), u"<font=2>%s</font>" % value,
            x, y, w, h, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

    def panel(self, x, y, w, h):
        name = self.name()
        screen = self.getScreen()
        screen.addPanel(name, u"", u"", True, False, x, y, w, h, PanelStyles.PANEL_STYLE_TECH)
        screen.setPanelColor(name, PANEL_COLOR[0], PANEL_COLOR[1], PANEL_COLOR[2])

    def modeName(self, mode):
        return tr("MODE_%d" % mode)

    def interfaceScreen(self):
        screen = self.getScreen()
        if screen.isActive():
            return
        self.iActivePlayer = CyGame().getActivePlayer()
        self.iTargetPlayer = -1
        screen.setRenderInterfaceOnly(True)
        screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
        screen.setDimensions(screen.centerX(0), screen.centerY(0), 1024, 768)
        screen.addDDSGFC("IntelBackground", INTEL_ART + "Background.dds",
            0, 0, 1024, 768, WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.showWindowBackground(False)
        screen.deleteWidget("IntelBottom")
        screen.deleteWidget("IntelBottomRule")
        screen.addPanel("IntelTop", u"", u"", True, False, 0, 0, 1024, 55, PanelStyles.PANEL_STYLE_TECH)
        screen.setPanelColor("IntelTop", 30, 30, 34)
        screen.addDDSGFC("IntelTopRule", INTEL_ART + "Selected.dds", 0, 53, 1024, 2, WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.setLabel("IntelTitle", "Background", u"<font=4b><color=220,120,120,255>%s</color></font>" % tr("TITLE").upper(),
            CvUtil.FONT_CENTER_JUSTIFY, 512, 13, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.setText("IntelExit", "Background", u"<font=4><color=230,230,235,255>%s</color></font>" % text.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()),
            CvUtil.FONT_RIGHT_JUSTIFY, 994, 726, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1)
        self.drawContents()

    def researchEffects(self, player):
        tech = player.getIntelligenceData(-1, 21)
        rate = player.getIntelligenceData(-1, 22)
        if tech >= 0:
            team = gc.getTeam(player.getTeam())
            rate = min(rate, max(0, team.getResearchCost(tech) - team.getResearchProgress(tech)))
        sources = []
        for i in range(con.iNumActivePlayers):
            raw = player.getIntelligenceData(i, 14)
            if raw > 0:
                sources.append((-raw, i))
        sources.sort()
        contributions = {}
        remaining = rate
        for rank, entry in enumerate(sources):
            amount = min(remaining, -entry[0] / (rank + 1))
            contributions[entry[1]] = amount
            remaining -= amount
        return tech, rate, contributions

    def visibleCities(self, rival, team):
        visible, unrest = 0, 0
        city, iterator = rival.firstCity(False)
        while city and not city.isNone():
            if city.getEspionageVisibility(team):
                visible += 1
            if city.getEspionageHappinessCounter() > 0:
                unrest += 1
            city, iterator = rival.nextCity(iterator, False)
        return visible, unrest

    def drawContents(self):
        screen = self.getScreen()
        for name in reversed(self.widgets):
            screen.deleteWidget(name)
        self.widgets = []
        player = gc.getPlayer(self.iActivePlayer)
        team = gc.getTeam(player.getTeam())
        rate = player.getCommerceRate(CommerceTypes.COMMERCE_ESPIONAGE)
        percent = player.getCommercePercent(CommerceTypes.COMMERCE_ESPIONAGE)
        self.lastRate, self.lastPercent = rate, percent
        self.panel(20, 64, 984, 88)
        self.label(tr("OUTPUT", (rate,)), 38, 76, True)
        self.label(tr("SLIDER", (percent,)), 38, 110)
        step = gc.getDefineINT("COMMERCE_PERCENT_CHANGE_INCREMENTS")
        for delta, x, style in [(-step, 255, ButtonStyles.BUTTON_STYLE_CITY_MINUS),
                                 (step, 281, ButtonStyles.BUTTON_STYLE_CITY_PLUS)]:
            button = self.name()
            screen.setButtonGFC(button, u"", "", x, 108, 22, 22, WidgetTypes.WIDGET_CHANGE_PERCENT,
                CommerceTypes.COMMERCE_ESPIONAGE, delta, style)
            screen.enable(button, player.isCommerceFlexible(CommerceTypes.COMMERCE_ESPIONAGE))
        self.researchTech, self.researchRate, self.researchContributions = self.researchEffects(player)
        self.label(tr("TOTAL_RESEARCH_RATE", (self.researchRate,)), 342, 78, True)
        self.label(tr("LAST_RESEARCH", (player.getIntelligenceData(-1, 23),)), 342, 111)
        self.label(tr("NETWORKS"), 30, 163, True)
        known = []
        for i in range(con.iNumActivePlayers):
            rival = gc.getPlayer(i)
            if rival.isAlive() and not rival.isMinorCiv() and rival.getTeam() != player.getTeam() and team.isHasMet(rival.getTeam()):
                known.append(i)
        if self.iTargetPlayer not in known:
            self.iTargetPlayer = -1
            if known:
                self.iTargetPlayer = known[0]
        scroll = self.name()
        self.panel(20, 192, 302, 511)
        screen.addScrollPanel(scroll, u"", 20, 192, 302, 511, PanelStyles.PANEL_STYLE_EMPTY)
        for row, i in enumerate(known):
            rival = gc.getPlayer(i)
            y = row * 84
            tile = self.name()
            screen.attachPanelAt(scroll, tile, u"", u"", True, False, PanelStyles.PANEL_STYLE_TECH,
                4, y + 3, 274, 74, WidgetTypes.WIDGET_GENERAL, 7100, i)
            if i == self.iTargetPlayer:
                screen.setPanelColor(tile, SELECTED_COLOR[0], SELECTED_COLOR[1], SELECTED_COLOR[2])
            else:
                screen.setPanelColor(tile, TILE_COLOR[0], TILE_COLOR[1], TILE_COLOR[2])
            active = player.getIntelligenceData(i, 0)
            pending = player.getIntelligenceData(i, 1)
            color = u"<color=255,235,235,255>"
            if i != self.iTargetPlayer:
                color = u"<color=230,230,230,255>"
            screen.setImageButtonAt(self.name(), scroll, gc.getLeaderHeadInfo(rival.getLeaderType()).getButton(),
                12, y + 14, 48, 48, WidgetTypes.WIDGET_GENERAL, 7100, i)
            civLabel = self.name()
            screen.setLabelAt(civLabel, scroll, u"<font=2b>%s%s</color></font>" % (color, rival.getCivilizationShortDescription(0)),
                CvUtil.FONT_LEFT_JUSTIFY, 70, y + 10, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, 7100, i)
            screen.setHitTest(civLabel, HitTestTypes.HITTEST_NOHIT)
            modeText = self.modeName(active)
            if pending != active:
                modeText += u" *"
            modeLabel = self.name()
            screen.setLabelAt(modeLabel, scroll, u"<font=2>%s</font>" % modeText,
                CvUtil.FONT_LEFT_JUSTIFY, 70, y + 33, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, 7100, i)
            screen.setHitTest(modeLabel, HitTestTypes.HITTEST_NOHIT)
            summaryKeys = ["TECH_SHORT", "MILITARY_SHORT", "POLITICS_CURRENT_SHORT", "MAP_SHORT"]
            if active == 0:
                amount = self.researchContributions.get(i, 0)
            elif active == 1:
                amount = player.getIntelligenceData(i, 6)
            elif active == 2:
                amount = -rival.getIntelligenceData(-1, 20)
            else:
                amount = player.getIntelligenceData(i, 10)
            summary = tr(summaryKeys[active], (amount,))
            effectLabel = self.name()
            screen.setLabelAt(effectLabel, scroll, u"<font=1>%s</font>" % summary,
                CvUtil.FONT_LEFT_JUSTIFY, 70, y + 55, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, 7100, i)
            screen.setHitTest(effectLabel, HitTestTypes.HITTEST_NOHIT)
        if not known:
            self.body(tr("NO_CONTACTS"), 350, 220, 620, 150)
            return
        self.drawTarget(player)

    def drawTarget(self, player):
        screen = self.getScreen()
        i = self.iTargetPlayer
        rival = gc.getPlayer(i)
        active = player.getIntelligenceData(i, 0)
        pending = player.getIntelligenceData(i, 1)
        self.label(rival.getCivilizationShortDescription(0), 342, 163, True)
        self.panel(336, 192, 668, 120)
        self.modeHint = self.name()
        self.showModeHint(tr("CHOOSE_MODE"))
        # Reuse the exact top-bar glyphs and their native transparent rendering.
        iconStyles = (
            "Button_HUDAdvisorTechnology_Style",
            "Button_HUDAdvisorMilitary_Style",
            "Button_HUDAdvisorVictory_Style",
            "Button_HUDAdvisorForeign_Style",
        )
        for mode in range(4):
            # Highlight only the player's selection; queued timing is shown below.
            state = "Neutral"
            if mode == pending:
                state = "Selected"
            x = 390 + mode * 160
            screen.setImageButton(self.name(), INTEL_ART + state + ".dds",
                x, 224, 80, 80, WidgetTypes.WIDGET_GENERAL, 7101, mode)
            iconButton = self.name()
            # Restore the original, smoothly rendered top-bar icons at native scale.
            screen.setImageButton(iconButton, "", x + 8, 232, 64, 64,
                WidgetTypes.WIDGET_GENERAL, 7101, mode)
            screen.setStyle(iconButton, iconStyles[mode])
        self.panel(336, 320, 668, 310)
        self.label(self.modeName(active), 352, 333, True)
        self.label(tr("CURRENT_EFFECT"), 352, 367)
        nation = rival.getCivilizationShortDescription(0)
        visible, unrest = self.visibleCities(rival, player.getTeam())
        y = 397
        if active == 0:
            self.label(tr("TECH_CURRENT_EFFECT", (self.researchContributions.get(i, 0), nation)), 352, y, True)
            self.label(tr("TOTAL_RESEARCH_RATE", (self.researchRate,)), 352, y + 32)
            self.label(tr("LAST_RESEARCH", (player.getIntelligenceData(-1, 23),)), 352, y + 64)
            tech = self.researchTech
            if tech >= 0:
                self.label(tr("PROJECT", (gc.getTechInfo(tech).getDescription(),)), 352, y + 96)
                team = gc.getTeam(player.getTeam())
                progress = team.getResearchProgress(tech)
                cost = max(1, team.getResearchCost(tech))
                name = self.name()
                screen.addStackedBarGFC(name, 352, y + 124, 630, 21, InfoBarTypes.NUM_INFOBAR_TYPES, WidgetTypes.WIDGET_GENERAL, -1, -1)
                screen.setStackedBarColors(name, InfoBarTypes.INFOBAR_STORED, gc.getInfoTypeForString("COLOR_PLAYER_DARK_RED"))
                screen.setStackedBarColors(name, InfoBarTypes.INFOBAR_RATE, gc.getInfoTypeForString("COLOR_PLAYER_VERYDARK_RED_TEXT"))
                screen.setStackedBarColors(name, InfoBarTypes.INFOBAR_EMPTY, gc.getInfoTypeForString("COLOR_EMPTY"))
                screen.setBarPercentage(name, InfoBarTypes.INFOBAR_STORED, min(1.0, float(progress) / cost))
                screen.setBarPercentage(name, InfoBarTypes.INFOBAR_RATE, min(1.0, float(self.researchRate) / max(1, cost - progress)))
                self.label(tr("RESEARCH_PROGRESS", (progress, cost)), 352, y + 152)
            else:
                self.label(tr("NO_ACTIVE_PROJECT"), 352, y + 96)
        elif active == 1:
            self.label(tr("COMBAT_CURRENT_EFFECT", (player.getIntelligenceData(i, 6), nation)), 352, y, True)
            if gc.getTeam(player.getTeam()).isAtWar(rival.getTeam()):
                self.label(tr("INFILTRATION_CURRENT_EFFECT", (player.getIntelligenceData(i, 7),)), 352, y + 32)
            else:
                self.label(tr("INFILTRATION_AT_PEACE"), 352, y + 32)
            self.label(tr("VISIBLE_CITIES", (visible,)), 352, y + 64)
        elif active == 2:
            penalty = rival.getIntelligenceData(-1, 20)
            anarchy = penalty / 3
            if rival.getMaxAnarchyTurns() == 0:
                anarchy = 0
            self.label(tr("STABILITY_CURRENT_EFFECT", (-penalty, nation)), 352, y, True)
            self.label(tr("ANARCHY_CURRENT_EFFECT", (anarchy,)), 352, y + 32)
            self.label(tr("UNREST_CURRENT_EFFECT", (unrest,)), 352, y + 64)
            self.label(tr("COMBINED_MEDDLING"), 352, y + 104)
        else:
            self.label(tr("MAP_CURRENT_EFFECT", (player.getIntelligenceData(i, 10),)), 352, y, True)
            self.label(tr("VISIBLE_CITIES", (visible,)), 352, y + 32)
            turns = player.getIntelligenceData(i, 11)
            if visible == 0:
                turns = 0
            self.label(tr("REPORT_DURATION", (turns,)), 352, y + 64)
        if active != pending:
            self.label(tr("QUEUED", (self.modeName(pending),)), 352, 578)
        risk = tr("RISK_LOW")
        if active == 1:
            risk = tr("RISK_MEDIUM")
        elif active == 2:
            risk = tr("RISK_HIGH")
        self.label(tr("RISK", (risk,)), 352, 607)
        self.panel(336, 638, 668, 65)
        self.label(tr("ACCESS", (player.getIntelligenceData(i, 2),)), 352, 649)
        self.label(tr("RESISTANCE", (player.getIntelligenceData(i, 13),)), 690, 649)
        embassy = tr("YES")
        if not player.getIntelligenceData(i, 4):
            embassy = tr("NO")
        self.label(tr("CONNECTIONS", (embassy, player.getIntelligenceData(i, 3))), 352, 677)
        self.label(tr("RELATIONS", (player.getIntelligenceData(i, 8),)), 780, 677)

    def showModeHint(self, value):
        self.getScreen().setLabel(self.modeHint, "Background", u"<font=2>%s</font>" % value,
            CvUtil.FONT_LEFT_JUSTIFY, 351, 204, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

    def handleInput(self, inputClass):
        if inputClass.getData1() == 7101:
            if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CURSOR_MOVE_ON:
                mode = inputClass.getData2()
                player = gc.getPlayer(self.iActivePlayer)
                caption = self.modeName(mode)
                if mode == player.getIntelligenceData(self.iTargetPlayer, 0):
                    caption = tr("CURRENT", (caption,))
                elif mode == player.getIntelligenceData(self.iTargetPlayer, 1):
                    caption = tr("QUEUED", (caption,))
                self.showModeHint(caption)
                return 1
            if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CURSOR_MOVE_OFF:
                self.showModeHint(tr("CHOOSE_MODE"))
                return 1
        if inputClass.getNotifyCode() != NotifyCode.NOTIFY_CLICKED:
            return 0
        if inputClass.getData1() == 7100:
            self.iTargetPlayer = inputClass.getData2()
            self.drawContents()
            return 1
        if inputClass.getData1() == 7101 and self.iTargetPlayer >= 0:
            # Never change game state locally. The DLL commits this player's queued mode.
            CyMessageControl().sendEspionageSpendingWeightChange(gc.getPlayer(self.iTargetPlayer).getTeam(), 100 + inputClass.getData2())
            return 1
        return 0

    def update(self, fDelta):
        player = gc.getPlayer(self.iActivePlayer)
        if CyGame().getActivePlayer() != self.iActivePlayer:
            self.getScreen().hideScreen()
            return
        dirty = CyInterface().isDirty(InterfaceDirtyBits.Espionage_Advisor_DIRTY_BIT)
        if dirty or self.lastRate != player.getCommerceRate(CommerceTypes.COMMERCE_ESPIONAGE) or self.lastPercent != player.getCommercePercent(CommerceTypes.COMMERCE_ESPIONAGE):
            CyInterface().setDirty(InterfaceDirtyBits.Espionage_Advisor_DIRTY_BIT, False)
            self.drawContents()
