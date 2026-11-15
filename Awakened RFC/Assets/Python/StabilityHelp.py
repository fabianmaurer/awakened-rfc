"""Read-only stability tooltips and snapshots of the applied base effects (Python 2.4)."""
from CvPythonExtensions import *
import cPickle as pickle
import Consts as con
import RFCUtils

gc = CyGlobalContext()
text = CyTranslator()
PREFIX = 'TXT_KEY_STABILITY_HELP_'
CATEGORIES = ('', 'CITIES', 'CIVICS', 'ECONOMY', 'EXPANSION', 'FOREIGN')
PARAMETERS = ((0, 1, -1), (2, 4, 3), (7, 9, 8), (10, 12, 11), (5, 6, -1))


def add(effects, category, key, value, name=()):
    entry = (category, key, name)
    effects[entry] = effects.get(entry, 0) + value


def store(player, effects, daily=False):
    data = pickle.loads(gc.getGame().getScriptData())
    key = 'stabilityHelpBase'
    if daily:
        key = 'stabilityHelpDaily'
    data.setdefault(key, {})[player] = effects
    gc.getGame().setScriptData(pickle.dumps(data))


def line(label, value):
    color = 'COLOR_POSITIVE_TEXT'
    if value < 0:
        color = 'COLOR_NEGATIVE_TEXT'
    return text.changeTextColor(u'%+d: %s' % (value, label), gc.getInfoTypeForString(color))


def getHelp(category):
    player = gc.getGame().getActivePlayer()
    if player < 0 or player >= con.iNumMajorPlayers or category < 0 or category > 5:
        return u''
    # Legacy category counters belong to the active client and are hidden in
    # hotseat/PBEM by the advisor. Do not expose another player's counters.
    if gc.getGame().isHotSeat() or gc.getGame().isPbem():
        return u''
    utils = RFCUtils.RFCUtils()
    data = pickle.loads(gc.getGame().getScriptData())
    params = data['lStabilityParameters']
    totals = [utils.getParCities(), utils.getParCivics(), utils.getParEconomy(), utils.getParExpansion(), utils.getParDiplomacy()]
    if category == 0:
        lines = []
        for index in range(5):
            lines.append(line(text.getText('TXT_KEY_STABILITY_PARAMETER_' + CATEGORIES[index + 1], ()), totals[index]))
        # The five legacy ratings include event history and era adjustments;
        # they are not an additive decomposition of national stability.
        lines.append(text.getText(PREFIX + 'OVERVIEW', ()))
        return u'\n'.join(lines)
    lines = []
    effects = dict(data.get('stabilityHelpBase', {}).get(player, {}))
    effects.update(data.get('stabilityHelpDaily', {}).get(player, {}))
    # Population losses can change immediately between regular updates.
    import Famine
    effects[(3, 'POPULATION_LOSS', ())] = Famine.populationLossPenalty(player)
    base, events, daily = PARAMETERS[category - 1]
    expected = params[base]
    if daily >= 0:
        expected += params[daily]
    recorded = 0
    for (group, key, name), value in sorted(effects.items()):
        if group == category:
            recorded += value
            if value:
                label = text.getText(PREFIX + key, ())
                if name:
                    label += u': ' + u' / '.join([gc.getCivicInfo(gc.getInfoTypeForString(civic)).getDescription() for civic in name])
                lines.append(line(label, value))
    if expected != recorded:
        lines.append(line(text.getText(PREFIX + 'OTHER_CURRENT', ()), expected - recorded))
    administration = 0
    if category == 4:
        administration = gc.getPlayer(player).getAdministrationValue(3, -1)
        if administration:
            lines.append(line(text.getText('TXT_KEY_ADMIN_NAME', ()), administration))
    if params[events]:
        lines.append(line(text.getText(PREFIX + 'EVENTS', ()), params[events]))
    adjustment = totals[category - 1] - expected - params[events] - administration
    if adjustment:
        lines.append(line(text.getText(PREFIX + 'ERA', ()), adjustment))
    if not lines:
        lines.append(text.getText(PREFIX + 'NONE', ()))
    return u'\n'.join(lines)
