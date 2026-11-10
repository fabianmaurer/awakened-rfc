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


def chanceText(basisPoints):
    basisPoints += 5
    return (u"%d.%d" % (basisPoints / 100, basisPoints % 100 / 10)).rstrip(u"0").rstrip(u".")


class CvEspionageAdvisor:
    def __init__(self):
        self.SCREEN_NAME = "EspionageAdvisor"
        self.iTargetPlayer = -1
        self.widgets = []
        self.lastRate = -1
        self.lastPercent = -1
        self.previewMode = -1

    def getScreen(self):
        return CyGInterfaceScreen(self.SCREEN_NAME, CvScreenEnums.ESPIONAGE_ADVISOR)

    def name(self):
        name = "IntelWidget%d" % len(self.widgets)
        self.widgets.append(name)
        return name

    def label(self, value, x, y, large=False):
        size = "3b"
        if not large:
            size = "3"
        self.getScreen().setLabel(self.name(), "Background", u"<font=%s><color=230,230,235,255>%s</color></font>" % (size, value),
            CvUtil.FONT_LEFT_JUSTIFY, x, y, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

    def body(self, value, x, y, w, h):
        self.getScreen().addMultilineText(self.name(), u"<font=3>%s</font>" % value,
            x - 4, y, w + 8, h, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

    def panel(self, x, y, w, h):
        name = self.name()
        screen = self.getScreen()
        screen.addPanel(name, u"", u"", True, False, x, y, w, h, PanelStyles.PANEL_STYLE_TECH)
        screen.setPanelColor(name, PANEL_COLOR[0], PANEL_COLOR[1], PANEL_COLOR[2])

    def modeName(self, mode):
        if mode == 2 and gc.getPlayer(self.iActivePlayer).getIntelligenceData(-1, 32):
            return tr("DYNASTIC_MODE")
        return tr("MODE_%d" % mode)

    def interfaceScreen(self):
        screen = self.getScreen()
        if screen.isActive():
            return
        self.iActivePlayer = CyGame().getActivePlayer()
        self.iTargetPlayer = -1
        self.previewMode = -1
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
        self.lastEffective = player.getIntelligenceData(-1, 59)
        self.researchTech, self.researchRate, self.researchContributions = self.researchEffects(player)
        self.label(tr("NETWORKS"), 30, 77, True)
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
        self.panel(20, 108, 302, 608)
        screen.addScrollPanel(scroll, u"", 20, 108, 302, 608, PanelStyles.PANEL_STYLE_EMPTY)
        for row, i in enumerate(known):
            rival = gc.getPlayer(i)
            y = row * 100
            tile = self.name()
            screen.attachPanelAt(scroll, tile, u"", u"", True, False, PanelStyles.PANEL_STYLE_TECH,
                4, y + 3, 274, 90, WidgetTypes.WIDGET_GENERAL, 7100, i)
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
            screen.setLabelAt(civLabel, scroll, u"<font=3b>%s%s</color></font>" % (color, rival.getCivilizationShortDescription(0)),
                CvUtil.FONT_LEFT_JUSTIFY, 70, y + 10, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, 7100, i)
            screen.setHitTest(civLabel, HitTestTypes.HITTEST_NOHIT)
            modeText = self.modeName(active)
            if pending != active:
                modeText += u" *"
            modeLabel = self.name()
            screen.setLabelAt(modeLabel, scroll, u"<font=3>%s</font>" % modeText,
                CvUtil.FONT_LEFT_JUSTIFY, 70, y + 37, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, 7100, i)
            screen.setHitTest(modeLabel, HitTestTypes.HITTEST_NOHIT)
            summaryKeys = ["TECH_SHORT", "MILITARY_SHORT", "POLITICS_CURRENT_SHORT", "ECONOMIC_SHORT", "COOP_SHORT", "NONE_SHORT"]
            if active == 0:
                amount = self.researchContributions.get(i, 0)
            elif active == 1:
                amount = chanceText(player.getIntelligenceData(i, 6))
            elif active == 2:
                amount = -rival.getIntelligenceData(-1, 20)
            elif active == 3:
                amount = chanceText(player.getIntelligenceData(i, 53))
            elif active == 4:
                amount = player.getIntelligenceData(i, 64)
            else:
                amount = 0
            summary = tr(summaryKeys[active], (amount,))
            if active == 2 and player.getIntelligenceData(-1, 32):
                summary = tr("DYNASTIC_STAGE_%d" % player.getIntelligenceData(i, 33))
            effectLabel = self.name()
            screen.setLabelAt(effectLabel, scroll, u"<font=2>%s</font>" % summary,
                CvUtil.FONT_LEFT_JUSTIFY, 70, y + 65, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, 7100, i)
            screen.setHitTest(effectLabel, HitTestTypes.HITTEST_NOHIT)
        if not known:
            self.body(tr("NO_CONTACTS"), 350, 136, 620, 150)
            return
        self.drawTarget(player)

    def drawTarget(self, player):
        screen = self.getScreen()
        i = self.iTargetPlayer
        rival = gc.getPlayer(i)
        active = player.getIntelligenceData(i, 0)
        pending = player.getIntelligenceData(i, 1)
        self.label(rival.getCivilizationShortDescription(0), 356, 77, True)
        self.panel(336, 108, 668, 140)
        self.modeHint = self.name()
        hint = tr("CHOOSE_MODE")
        self.showModeHint(hint)
        # Reuse the exact top-bar glyphs and their native transparent rendering.
        iconStyles = (
            "Button_HUDAdvisorTechnology_Style",
            "Button_HUDAdvisorMilitary_Style",
            "Button_HUDAdvisorVictory_Style",
            "Button_HUDAdvisorFinance_Style",
            "Button_HUDAdvisorCorporation_Style",
            "Button_HUDAdvisorDomestic_Style",
        )
        for slot, mode in enumerate((5, 0, 1, 2, 3, 4)):
            # Highlight only the player's selection; queued timing is shown below.
            state = "Neutral"
            if mode == pending:
                state = "Selected"
            x = 356 + slot * 110
            enabled = mode != 4 or bool(player.getIntelligenceData(i, 62))
            widgetID = 7101
            widgetValue = mode
            if not enabled:
                widgetID = 7102
                widgetValue = i
            frameButton = self.name()
            if enabled:
                screen.setImageButton(frameButton, INTEL_ART + state + ".dds",
                    x, 144, 80, 84, WidgetTypes.WIDGET_GENERAL, widgetID, widgetValue)
            else:
                # A passive background preserves hover help without being a clickable button.
                screen.addDDSGFC(frameButton, INTEL_ART + "Neutral.dds",
                    x, 144, 80, 84, WidgetTypes.WIDGET_GENERAL, widgetID, widgetValue)
            iconButton = self.name()
            # Leave a footer inside each tile for its network buildup percentage.
            if mode == 4:
                # Exact brown briefcase from the Corporations Advisor HUD atlas.
                if enabled:
                    screen.setImageButton(iconButton, INTEL_ART + "Cooperation.dds", x + 12, 150, 56, 56,
                        WidgetTypes.WIDGET_GENERAL, widgetID, widgetValue)
                else:
                    screen.addDDSGFC(iconButton, INTEL_ART + "CooperationDisabled.dds", x + 12, 150, 56, 56,
                        WidgetTypes.WIDGET_GENERAL, widgetID, widgetValue)
            else:
                screen.setImageButton(iconButton, "", x + 12, 150, 56, 56,
                    WidgetTypes.WIDGET_GENERAL, widgetID, widgetValue)
                iconStyle = iconStyles[mode]
                if mode == 2 and player.getIntelligenceData(-1, 32):
                    iconStyle = "Button_HUDAdvisorCivics_Style"
                screen.setStyle(iconButton, iconStyle)
            buildup = self.buildupText(player, mode)
            if not enabled:
                buildup = u"<color=140,140,145,255>%s</color>" % buildup
            screen.setLabel(self.name(), "Background", u"<font=2>%s</font>" % buildup,
                CvUtil.FONT_CENTER_JUSTIFY, x + 40, 212, -0.1, FontTypes.GAME_FONT,
                WidgetTypes.WIDGET_GENERAL, widgetID, widgetValue)
        self.detailWidgetStart = len(self.widgets)
        self.drawModeDetails(player)

    def buildupText(self, player, mode):
        amount = player.getIntelligenceData(self.iTargetPlayer, 100 + mode)
        if amount < 0:
            return u"--"
        return chanceText(amount) + u"%"

    def modeHelp(self, player, mode):
        if mode == 2 and player.getIntelligenceData(-1, 32):
            return tr("DYNASTIC_HELP")
        return tr(("TECH_HELP", "MILITARY_HELP", "POLITICS_HELP", "ECONOMIC_HELP", "COOP_HELP", "NONE_HELP")[mode])

    def refreshModeDetails(self):
        for name in reversed(self.widgets[self.detailWidgetStart:]):
            self.getScreen().deleteWidget(name)
        self.widgets = self.widgets[:self.detailWidgetStart]
        self.drawModeDetails(gc.getPlayer(self.iActivePlayer))

    def drawModeDetails(self, player):
        screen = self.getScreen()
        i = self.iTargetPlayer
        rival = gc.getPlayer(i)
        active = player.getIntelligenceData(i, 0)
        pending = player.getIntelligenceData(i, 1)
        mode = pending
        if self.previewMode >= 0:
            mode = self.previewMode
        self.panel(336, 248, 668, 374)
        backgroundArt = ("TechnologyBackground.dds", "MilitaryBackground.dds",
            "PoliticalBackground.dds", "EconomicBackground.dds", "CooperationBackground.dds", None)[mode]
        if mode == 2 and player.getIntelligenceData(-1, 32):
            backgroundArt = "DynasticBackground.dds"
        if backgroundArt:
            background = self.name()
            screen.addDDSGFC(background, INTEL_ART + backgroundArt,
                338, 250, 664, 354, WidgetTypes.WIDGET_GENERAL, -1, -1)
            screen.setHitTest(background, HitTestTypes.HITTEST_NOHIT)
        self.label(self.modeName(mode), 356, 256, True)
        self.label(tr("BUILDUP_PERCENT", (self.buildupText(player, mode),)), 690, 288)
        if mode != active:
            self.body(self.modeHelp(player, mode), 356, 328, 628, 104)
            if mode == 1:
                strength = player.getIntelligenceData(i, 101)
                self.label(tr("COMBAT_CURRENT_EFFECT", (chanceText(30 * strength / 100), rival.getCivilizationShortDescription(0))), 356, 448)
                self.label(tr("TROOP_COVERAGE", (chanceText(strength),)), 356, 480)
                if gc.getTeam(player.getTeam()).isAtWar(rival.getTeam()):
                    self.label(tr("INFILTRATION_CURRENT_EFFECT", (chanceText(30 * strength / 100),)), 356, 512)
                else:
                    self.label(tr("INFILTRATION_AT_PEACE"), 356, 512)
            elif mode == 4 and not player.getIntelligenceData(i, 62):
                self.label(tr("COOP_LOCKED"), 356, 448)
            elif mode != 5:
                self.body(tr("PREVIEW_BUILDUP_HELP"), 356, 448, 628, 80)
            self.drawModeFooter(player, mode)
            return
        self.label(tr("CURRENT_EFFECT"), 356, 288)
        nation = rival.getCivilizationShortDescription(0)
        y = 328
        if active == 0:
            self.label(tr("TECH_CURRENT_EFFECT", (self.researchContributions.get(i, 0), nation)), 356, y, True)
            self.label(tr("TOTAL_RESEARCH_RATE", (self.researchRate,)), 356, y + 32)
            tech = self.researchTech
            if tech >= 0:
                self.label(tr("PROJECT", (gc.getTechInfo(tech).getDescription(),)), 356, y + 96)
                team = gc.getTeam(player.getTeam())
                progress = team.getResearchProgress(tech)
                cost = max(1, team.getResearchCost(tech))
                name = self.name()
                screen.addStackedBarGFC(name, 356, y + 128, 628, 21, InfoBarTypes.NUM_INFOBAR_TYPES, WidgetTypes.WIDGET_GENERAL, -1, -1)
                screen.setStackedBarColors(name, InfoBarTypes.INFOBAR_STORED, gc.getInfoTypeForString("COLOR_PLAYER_DARK_RED"))
                screen.setStackedBarColors(name, InfoBarTypes.INFOBAR_RATE, gc.getInfoTypeForString("COLOR_PLAYER_VERYDARK_RED_TEXT"))
                screen.setStackedBarColors(name, InfoBarTypes.INFOBAR_EMPTY, gc.getInfoTypeForString("COLOR_EMPTY"))
                screen.setBarPercentage(name, InfoBarTypes.INFOBAR_STORED, min(1.0, float(progress) / cost))
                screen.setBarPercentage(name, InfoBarTypes.INFOBAR_RATE, min(1.0, float(self.researchRate) / max(1, cost - progress)))
                self.label(tr("RESEARCH_PROGRESS", (progress, cost)), 356, y + 160)
            else:
                self.label(tr("NO_ACTIVE_PROJECT"), 356, y + 96)
        elif active == 1:
            self.label(tr("COMBAT_CURRENT_EFFECT", (chanceText(player.getIntelligenceData(i, 6)), nation)), 356, y, True)
            if gc.getTeam(player.getTeam()).isAtWar(rival.getTeam()):
                self.label(tr("INFILTRATION_CURRENT_EFFECT", (chanceText(player.getIntelligenceData(i, 7)),)), 356, y + 32)
            else:
                self.label(tr("INFILTRATION_AT_PEACE"), 356, y + 32)
            self.label(tr("TROOP_COVERAGE", (chanceText(player.getIntelligenceData(i, 30)),)), 356, y + 64)
        elif active == 2:
            if player.getIntelligenceData(-1, 32):
                stage = player.getIntelligenceData(i, 33)
                self.label(tr("DYNASTIC_STAGE_%d" % stage), 356, y, True)
                if stage == 4:
                    if gc.getTeam(rival.getTeam()).isVassal(player.getTeam()):
                        self.label(tr("DYNASTIC_INCORPORATING"), 356, y + 32)
                        self.label(tr("DYNASTIC_PROTECTED"), 356, y + 64)
                    else:
                        self.label(tr("DYNASTIC_INCORPORATION_PAUSED"), 356, y + 32)
                elif not player.getIntelligenceData(i, 36):
                    self.label(tr("DYNASTIC_REQUIRES"), 356, y + 32)
                else:
                    chance = player.getIntelligenceData(i, 35)
                    chanceKey = "DYNASTIC_ADVANCE"
                    if chance < 0:
                        chanceKey = "DYNASTIC_REGRESS"
                    self.label(tr(chanceKey, (chanceText(abs(chance)),)), 356, y + 32)
                self.label(tr("DYNASTIC_RELATIONS", (player.getIntelligenceData(i, 37),)), 356, y + 96)
                if gc.getTeam(player.getTeam()).isAtWar(rival.getTeam()):
                    self.label(tr("DYNASTIC_WAR_PAUSED"), 356, y + 128)
                elif stage == 2 and not player.getIntelligenceData(i, 39):
                    self.label(tr("DYNASTIC_UNION_BLOCKED"), 356, y + 128)
                elif stage < 4:
                    self.label(tr("DYNASTIC_INSTABILITY_HELP"), 356, y + 128)
                if stage >= 2:
                    self.label(tr("DYNASTIC_KIN_WAR_HELP", (player.getIntelligenceData(-1, 45),)), 356, y + 160)
            else:
                penalty = rival.getIntelligenceData(-1, 20)
                anarchy = rival.getIntelligenceData(-1, 25)
                self.label(tr("POLITICAL_RELATIONS", (player.getIntelligenceData(i, 50),)), 356, y, True)
                self.label(tr("POLITICAL_PRESSURE_EFFECT", (-penalty, anarchy)), 356, y + 32)
                self.label(tr("POLITICAL_CIVIC_CHANCE", (chanceText(player.getIntelligenceData(i, 48)),)), 356, y + 64)
                self.label(tr("POLITICAL_CULTURE", (chanceText(player.getIntelligenceData(i, 51)),)), 356, y + 96)
                clientChance = player.getIntelligenceData(i, 49)
                if gc.getTeam(rival.getTeam()).isVassal(player.getTeam()):
                    self.label(tr("POLITICAL_CLIENT_ACTIVE"), 356, y + 128)
                elif clientChance == 0:
                    self.label(tr("POLITICAL_CLIENT_BLOCKED"), 356, y + 128)
                elif clientChance < 5:
                    self.label(tr("POLITICAL_CLIENT_SMALL"), 356, y + 128)
                else:
                    self.label(tr("POLITICAL_CLIENT_CHANCE", (chanceText(clientChance),)), 356, y + 128)
        elif active == 3:
            self.label(tr("ECONOMIC_INFLUENCE", (chanceText(player.getIntelligenceData(i, 53)),)), 356, y, True)
            self.label(tr("ECONOMIC_GOLD", (chanceText(player.getIntelligenceData(i, 54)),)), 356, y + 32)
            self.label(tr("ECONOMIC_FOOD", (chanceText(player.getIntelligenceData(i, 55)),)), 356, y + 64)
            self.label(tr("ECONOMIC_ART", (chanceText(player.getIntelligenceData(i, 56)),)), 356, y + 96)
            self.label(tr("ECONOMIC_SHARED"), 356, y + 128)
            self.label(tr("ECONOMIC_BUDGET"), 356, y + 160)
        elif active == 4:
            self.label(tr("COOP_CONTRIBUTION", (player.getIntelligenceData(i, 64),)), 356, y, True)
            self.label(tr("COOP_INFLUENCE", (chanceText(player.getIntelligenceData(i, 63)),)), 356, y + 32)
            self.body(tr("COOP_HELP"), 356, y + 96, 628, 88)
        else:
            self.body(tr("NONE_HELP"), 356, y, 628, 140)
        self.drawModeFooter(player, mode)

    def drawModeFooter(self, player, mode):
        i = self.iTargetPlayer
        active = player.getIntelligenceData(i, 0)
        pending = player.getIntelligenceData(i, 1)
        if active != pending:
            self.label(tr("QUEUED", (self.modeName(pending),)), 356, 544)
        discovery = chanceText(player.getIntelligenceData(i, 200 + mode))
        risk = tr("RISK_LOW", (discovery,))
        if mode >= 4:
            risk = u"-"
        elif mode == 1:
            risk = tr("RISK_MEDIUM", (discovery,))
        elif mode == 2:
            if player.getIntelligenceData(-1, 32):
                risk = u"-"
            else:
                risk = tr("RISK_HIGH", (discovery,))
        self.label(tr("RISK", (risk,)), 356, 576)
        self.panel(336, 620, 668, 96)
        self.label(tr("ACCESS", (player.getIntelligenceData(i, 2),)), 356, 628)
        self.label(tr("RESISTANCE", (player.getIntelligenceData(i, 13),)), 690, 628)
        embassy = tr("YES")
        if not player.getIntelligenceData(i, 4):
            embassy = tr("NO")
        self.label(tr("CONNECTIONS", (embassy, player.getIntelligenceData(i, 3))), 356, 668)
        self.label(tr("RELATIONS", (player.getIntelligenceData(i, 8),)), 690, 668)

    def showModeHint(self, value):
        self.getScreen().setLabel(self.modeHint, "Background", u"<font=3>%s</font>" % value,
            CvUtil.FONT_LEFT_JUSTIFY, 356, 116, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

    def handleInput(self, inputClass):
        if inputClass.getData1() == 7102:
            # Locked cooperation has hover help only: no preview selection and no network message.
            return 1
        if inputClass.getData1() == 7101:
            if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CURSOR_MOVE_ON:
                mode = inputClass.getData2()
                player = gc.getPlayer(self.iActivePlayer)
                caption = self.modeName(mode)
                if mode == 4 and not player.getIntelligenceData(self.iTargetPlayer, 62):
                    caption = tr("COOP_LOCKED")
                if mode == player.getIntelligenceData(self.iTargetPlayer, 0):
                    caption = tr("CURRENT", (caption,))
                elif mode == player.getIntelligenceData(self.iTargetPlayer, 1):
                    caption = tr("QUEUED", (caption,))
                self.showModeHint(caption)
                self.previewMode = mode
                self.refreshModeDetails()
                return 1
            if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CURSOR_MOVE_OFF:
                hint = tr("CHOOSE_MODE")
                self.showModeHint(hint)
                self.previewMode = -1
                self.refreshModeDetails()
                return 1
        if inputClass.getNotifyCode() != NotifyCode.NOTIFY_CLICKED:
            return 0
        if inputClass.getData1() == 7100:
            self.iTargetPlayer = inputClass.getData2()
            self.previewMode = -1
            self.drawContents()
            return 1
        if inputClass.getData1() == 7101 and self.iTargetPlayer >= 0:
            if inputClass.getData2() == 4 and not gc.getPlayer(self.iActivePlayer).getIntelligenceData(self.iTargetPlayer, 62):
                return 1
            self.previewMode = inputClass.getData2()
            self.refreshModeDetails()
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
        if dirty or self.lastEffective != player.getIntelligenceData(-1, 59) or self.lastRate != player.getCommerceRate(CommerceTypes.COMMERCE_ESPIONAGE) or self.lastPercent != player.getCommercePercent(CommerceTypes.COMMERCE_ESPIONAGE):
            CyInterface().setDirty(InterfaceDirtyBits.Espionage_Advisor_DIRTY_BIT, False)
            self.drawContents()
