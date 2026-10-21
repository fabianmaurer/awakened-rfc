"""Generate the simultaneous European settler start; never launches Civ4."""
from pathlib import Path
import re
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / 'Awakened RFC/PublicMaps'
TARGET = MAPS / 'Start 3b - 900 AD.CivBeyondSwordWBSave'
ACTIVE = (0, 2, 6, 8, 11, 12, 13, 14, 15, 16, 17, 18, 27, 30)
# English, French, German, Italian, Spanish. Contemporary representatives of
# aggregated RFC slots, not claims to rule every region represented by a slot.
LEADERS = {
    28: ('Local Andalusi rulers', 'Seigneurs andalous locaux', 'Andalusische Regionalherren', 'Signori andalusi locali', 'Se\u00f1ores andalus\u00edes locales'),
    0: ('Harun ibn Khumarawayh',) * 5,
    6: ('Ibrahim II ibn Ahmad',) * 5,
    27: ('Abd Allah ibn Muhammad',) * 5,
    2: ('Tang Zhaozong',) * 5,
    8: ('Daigo',) * 5,
    11: ('Harald Fairhair', 'Harald \u00e0 la Belle Chevelure', 'Harald Sch\u00f6nhaar', 'Harald Bellachioma', 'Harald Cabellera Hermosa'),
    12: ("al-Mu'tadid",) * 5,
    13: ('Yasovarman I', 'Yasovarman Ier', 'Yasovarman I.', 'Yasovarman I', 'Yasovarman I'),
    14: ('Alfonso III of Asturias', "Alphonse III des Asturies", 'Alfons III. von Asturien', 'Alfonso III delle Asturie', 'Alfonso III de Asturias'),
    15: ('Charles III the Simple', 'Charles III le Simple', 'Karl III. der Einf\u00e4ltige', 'Carlo III il Semplice', 'Carlos III el Simple'),
    16: ('Edward the Elder', "\u00c9douard l'Ancien", 'Eduard der \u00c4ltere', 'Edoardo il Vecchio', 'Eduardo el Viejo'),
    17: ('Louis the Child', "Louis l'Enfant", 'Ludwig das Kind', 'Ludovico il Fanciullo', 'Luis el Ni\u00f1o'),
    18: ('Oleg of Kiev', 'Oleg de Kiev', 'Oleg von Kiew', 'Oleg di Kiev', 'Oleg de Kiev'),
    34: ('Leo VI the Wise', 'L\u00e9on VI le Sage', 'Leo VI. der Weise', 'Leone VI il Saggio', 'Le\u00f3n VI el Sabio'),
}
CORDOBA = (51, 41)
CORDOBA_OWNER = 27  # Reserved successor slot, selectable in this scenario.
CORDOBA_TEXT = {
    'TXT_KEY_RFCMP_900_ANDALUSI_DESC': ('Independent Andalusi rulers', 'Seigneurs andalous ind\u00e9pendants', 'Unabh\u00e4ngige andalusische Herrschaften', 'Signorie andaluse indipendenti', 'Se\u00f1or\u00edos andalus\u00edes independientes'),
    'TXT_KEY_RFCMP_900_ANDALUSI_SHORT': ('Andalusi cities', 'Cit\u00e9s andalouses', 'Andalusische St\u00e4dte', 'Citt\u00e0 andaluse', 'Ciudades andalus\u00edes'),
    'TXT_KEY_RFCMP_900_ANDALUSI_ADJ': ('Andalusi', 'andalou', 'andalusisch', 'andaluso', 'andalus\u00ed'),
    'TXT_KEY_RFCMP_900_CORDOBA_DESC': ('Emirate of C\u00f3rdoba', '\u00c9mirat de Cordoue', 'Emirat C\u00f3rdoba', 'Emirato di Cordova', 'Emirato de C\u00f3rdoba'),
    'TXT_KEY_RFCMP_900_CORDOBA_SHORT': ('C\u00f3rdoba', 'Cordoue', 'C\u00f3rdoba', 'Cordova', 'C\u00f3rdoba'),
    'TXT_KEY_RFCMP_900_TULUNID_DESC': ('Tulunid Emirate', '\u00c9mirat toulounide', 'Tulunidenemirat', 'Emirato tulunide', 'Emirato tulun\u00ed'),
    'TXT_KEY_RFCMP_900_TULUNID_SHORT': ('Tulunids', 'Toulounides', 'Tuluniden', 'Tulunidi', 'Tulun\u00edes'),
    'TXT_KEY_RFCMP_900_AGHLABID_DESC': ('Aghlabid Emirate', '\u00c9mirat aghlabide', 'Aghlabidenemirat', 'Emirato aghlabide', 'Emirato aglab\u00ed'),
    'TXT_KEY_RFCMP_900_AGHLABID_SHORT': ('Aghlabids', 'Aghlabides', 'Aghlabiden', 'Aghlabidi', 'Aglab\u00edes'),
    'TXT_KEY_RFCMP_900_TULUNID_ADJ': ('Tulunid', 'toulounide', 'tulunidisch', 'tulunide', 'tulun\u00ed'),
    'TXT_KEY_RFCMP_900_AGHLABID_ADJ': ('Aghlabid', 'aghlabide', 'aghlabidisch', 'aghlabide', 'aglab\u00ed'),
}
# Coordinates follow RFC's compressed terrain. The capital is listed explicitly;
# do not let plot traversal choose Alexandria or Mecca as a new state's capital.
CAPITALS = {0: (69, 35), 6: (58, 38), 12: (78, 40), 27: CORDOBA}
CITIES = {
    (69, 35): (0, "Al-Qata'i", 7),
    (67, 36): (0, 'Al-Iskandariyya', 5),
    (64, 36): (0, 'Barqa', 3),
    (73, 38): (0, 'Al-Quds', 4),
    (73, 41): (0, 'Dimashq', 5),
    (58, 38): (6, 'Raqqada', 6),
    (60, 37): (6, 'Tarabulus', 4),
    (60, 40): (6, 'Balarm', 5),
    (78, 40): (12, 'Baghdad', 9),
    (76, 42): (12, 'Al-Raqqa', 4),
    (79, 43): (12, 'Al-Mawsil', 4),
    (78, 37): (12, 'Al-Basra', 5),
    (75, 33): (12, 'Makkah', 4),
    CORDOBA: (27, 'Cordoba', 6),
    (49, 41): (28, 'Ishbiliyya', 5),      # Seville: Banu Hajjaj
    (50, 43): (28, 'Batalyaws', 4),       # Badajoz: Marwanid local dynasty
    (52, 43): (28, 'Tulaytula', 5),       # Autonomous Toledo
    (54, 45): (28, 'Saraqusta', 5),       # Zaragoza: Tujibid governors
    (52, 37): (31, 'Fes', 4),             # Idrisid Morocco
    (55, 37): (32, 'Tahert', 4),          # Rustamid central Maghreb
    (79, 35): (31, 'Al-Ahsa', 3),         # Qarmatian base, not later Hajar
    (76, 30): (32, "San'a", 3),          # Local Yemeni rule, not direct Abbasid rule
}
INTRODUCTIONS = {
    0: ("900 AD: Harun ibn Khumarawayh rules the autonomous Tulunid emirate from Al-Qata'i. Egypt and southern Syria sustain your state, while the Abbasid caliph has recovered the northern frontier. Preserve your army and treasury; recognition of the caliph does not make your lands directly governed from Baghdad.",
        "900 n. Chr.: Harun ibn Khumarawayh regiert das autonome Tulunidenemirat von Al-Qata'i aus. \u00c4gypten und S\u00fcdsyrien tragen euren Staat, w\u00e4hrend der Abbasidenkalif die n\u00f6rdlichen Grenzgebiete zur\u00fcckgewonnen hat. Sichert Heer und Schatzkammer; die Anerkennung des Kalifen bedeutet keine direkte Herrschaft Bagdads \u00fcber euer Land."),
    6: ("900 AD: Ibrahim II rules Aghlabid Ifriqiya from the Kairouan region. Your holdings include Tripoli and Palermo, but the conquest of Byzantine Sicily is unfinished. Defend your African cities and use your fleet to sustain the island campaign. The Fatimid caliphate has not yet been founded.",
        "900 n. Chr.: Ibrahim II. regiert das aghlabidische Ifriqiya aus der Region Kairouan. Zu eurem Reich geh\u00f6ren Tripolis und Palermo, doch die Eroberung des byzantinischen Sizilien ist noch nicht abgeschlossen. Verteidigt eure afrikanischen St\u00e4dte und sichert den Inselkrieg mit eurer Flotte. Das Fatimidenkalifat ist noch nicht gegr\u00fcndet."),
    12: ("900 AD: Al-Mu'tadid governs the Abbasid caliphate from Baghdad. Iraq and the northern Syrian frontier form your direct power base. The Tulunids and Aghlabids govern autonomously; Iran and Arabia contain other local powers. Restore influence through diplomacy or conquest rather than assuming direct rule over all former provinces.",
         "900 n. Chr.: Al-Mu'tadid regiert das Abbasidenkalifat von Bagdad aus. Der Irak und die nordsyrischen Grenzgebiete bilden eure unmittelbare Machtbasis. Tuluniden und Aghlabiden regieren autonom; auch Iran und Arabien haben eigene Regionalm\u00e4chte. Gewinnt Einfluss durch Diplomatie oder Eroberung zur\u00fcck."),
    27: ("900 AD: Abd Allah rules the Umayyad emirate from Cordoba. Provincial rivals weaken central authority, and Christian rulers remain in northern Iberia. Rebuild your position from the southern core. Cordoba is still an emirate: the historical proclamation of its caliphate lies in 929.",
         "900 n. Chr.: Abd Allah regiert das Umayyadenemirat von Cordoba aus. Provinzrivalen schw\u00e4chen die Zentralgewalt, und im Norden Iberiens bestehen christliche Reiche. Festigt eure Stellung vom s\u00fcdlichen Kernland aus. Cordoba ist noch ein Emirat; die historische Ausrufung des Kalifats liegt im Jahr 929."),
}


def city_and_units(pos, owner, name, population):
    capital = CAPITALS.get(owner) == pos
    lines = ['\tBeginCity', '\t\tCityOwner=' + str(owner),
             '\t\tCityName=' + name, '\t\tCityPopulation=' + str(population)]
    buildings = ['WALLS', 'GRANARY', 'MARKET']
    if capital:
        buildings += ['PALACE', 'LIBRARY']
    for building in buildings:
        lines.append('\t\tBuildingType=BUILDING_' + building)
    lines.append('\t\tReligionType=RELIGION_ISLAM')
    if pos == (73, 38):
        lines += ['\t\tReligionType=RELIGION_JUDAISM',
                  '\t\tHolyCityReligionType=RELIGION_JUDAISM']
    if owner == 0:
        lines.append('\t\tReligionType=RELIGION_CHRISTIANITY')
    if pos == (75, 33):
        lines.append('\t\tHolyCityReligionType=RELIGION_ISLAM')
    lines += ['\t\tPlayer' + str(owner) + 'Culture=1', '\tEndCity']
    forces = [('LONGBOWMAN', 3 if capital else 2, 'CITY_DEFENSE')]
    if capital:
        forces += [('SPEARMAN', 1, 'CITY_DEFENSE'), ('HORSE_ARCHER', 2, 'ATTACK'),
                   ('SWORDSMAN', 2, 'ATTACK_CITY'), ('WORKER', 2, 'WORKER')]
    for kind, count, role in forces:
        for _ in range(count):
            lines += ['\tBeginUnit', '\t\tUnitType=UNIT_' + kind + ', UnitOwner=' + str(owner),
                      '\t\tUnitAIType=UNITAI_' + role, '\tEndUnit']
    return '\n' + '\n'.join(lines) + '\n'


def write_leader_text():
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<Civ4GameText xmlns="http://www.firaxis.com">']
    entries = [('TXT_KEY_RFCMP_900_LEADER_' + str(owner), names)
               for owner, names in sorted(LEADERS.items())] + list(CORDOBA_TEXT.items())
    for owner, (english, german) in INTRODUCTIONS.items():
        entries.append(('TXT_KEY_RFCMP_900_INTRO_' + str(owner),
                        (english, english, german, english, english)))
    for key, names in entries:
        lines += ['  <TEXT>', '    <Tag>' + key + '</Tag>']
        for language, name in zip(('English', 'French', 'German', 'Italian', 'Spanish'), names):
            lines.append('    <' + language + '>' + escape(name) + '</' + language + '>')
        lines.append('  </TEXT>')
    lines.append('</Civ4GameText>')
    target = ROOT / 'Awakened RFC/Assets/XML/Text/CIV4GameText_Scenario900Leaders.xml'
    target.write_bytes(('\n'.join(lines) + '\n').encode('ascii', 'xmlcharrefreplace'))


def field(block, key, value):
    line = '\t' + key + '=' + str(value)
    # WB block markers must occupy their own line. Do not consume the newline
    # before a block's first field when replacing it (notably LeaderType).
    pattern = r'^[ \t]*' + re.escape(key) + r'=[^\n]*'
    if re.search(pattern, block, re.M):
        return re.sub(pattern, lambda _: line, block, count=1, flags=re.M)
    return block.rstrip() + '\n' + line + '\n'


def main():
    text = (MAPS / 'Start 3 - 600 AD.CivBeyondSwordWBSave').read_text(encoding='utf-8')
    text = re.sub(r'GameTurn=181\b', 'GameTurn=211', text)
    text = text.replace('Description=TXT_KEY_RHYES_WB_DESC',
                        'Description=TXT_KEY_RFCMP_900_DESC')
    players = iter(range(35))

    def player(match):
        owner = next(players)
        block = field(match[1], 'PlayableCiv', int(owner in ACTIVE))
        if owner in LEADERS:
            block = field(block, 'LeaderName', 'TXT_KEY_RFCMP_900_LEADER_' + str(owner))
        if owner in CAPITALS:
            block = field(block, 'StateReligion', 'RELIGION_ISLAM')
        if owner == 12:
            block = field(block, 'CivType', 'CIVILIZATION_ABBASID')
            block = field(block, 'LeaderType', 'LEADER_ABBASID')
        if owner in (0, 6):
            dynasty = 'TULUNID' if owner == 0 else 'AGHLABID'
            block = field(block, 'CivDesc', 'TXT_KEY_RFCMP_900_' + dynasty + '_DESC')
            block = field(block, 'CivShortDesc', 'TXT_KEY_RFCMP_900_' + dynasty + '_SHORT')
            block = field(block, 'CivAdjective', 'TXT_KEY_RFCMP_900_' + dynasty + '_ADJ')
        if owner == CORDOBA_OWNER:
            for key, value in (('CivType', 'CIVILIZATION_UMAYYAD'),
                               ('LeaderType', 'LEADER_UMAYYAD'),
                               ('StateReligion', 'RELIGION_ISLAM'),
                               ('CivDesc', 'TXT_KEY_RFCMP_900_CORDOBA_DESC'),
                               ('CivShortDesc', 'TXT_KEY_RFCMP_900_CORDOBA_SHORT'),
                               ('CivAdjective', 'TXT_KEY_CIV_UMAYYAD_ADJECTIVE')):
                block = field(block, key, value)
        if owner == 28:
            # A dedicated minor player scopes Spain's initial war to Andalusia,
            # rather than every unrelated city in the global independent slots.
            for key, value in (('CivType', 'CIVILIZATION_INDEPENDENT2'),
                               ('LeaderType', 'LEADER_INDEPENDENT'),
                               ('MinorNationStatus', 1),
                               ('StateReligion', 'RELIGION_ISLAM'),
                               ('CivDesc', 'TXT_KEY_RFCMP_900_ANDALUSI_DESC'),
                               ('CivShortDesc', 'TXT_KEY_RFCMP_900_ANDALUSI_SHORT'),
                               ('CivAdjective', 'TXT_KEY_RFCMP_900_ANDALUSI_ADJ')):
                block = field(block, key, value)
        return 'BeginPlayer' + block + 'EndPlayer'

    text = re.sub(r'BeginPlayer\b(.*?)EndPlayer', player, text, flags=re.S)
    teams = iter(range(35))

    def team(match):
        owner = next(teams)
        block = match[1]
        # Autonomous emirs recognized Abbasid authority; no Civ4 vassal lock.
        if owner in CAPITALS:
            for other in CAPITALS:
                if other != owner:
                    block += '\n\tContactWithTeam=' + str(other) + '\n'
        # The Aghlabid conquest of Sicily was still in progress in 900.
        if owner in (6, 34):
            block += '\n\tAtWar=' + str(34 if owner == 6 else 6) + '\n'
        if owner in (14, 28):
            other = 28 if owner == 14 else 14
            block += '\n\tContactWithTeam=' + str(other) + '\n\tAtWar=' + str(other) + '\n'
        return 'BeginTeam' + block + 'EndTeam'

    text = re.sub(r'BeginTeam\b(.*?)EndTeam', team, text, flags=re.S)

    def plot(match):
        block = match[1]
        x, y = map(int, re.search(r'x=(\d+),y=(\d+)', block).groups())
        # Leave Italy and Byzantium settled; free the six European homelands.
        europe = (49 <= x <= 58 and 42 <= y <= 65 or
                  59 <= x <= 74 and 48 <= y <= 65)
        if europe:
            block = re.sub(r'\s*Begin(?:City|Unit)\b.*?End(?:City|Unit)', '', block, flags=re.S)
            block = re.sub(r'^\s*(?:Player\d+Culture|Culture|TeamReveal|Owner|ImprovementType|RouteType)=[^\n]*', '', block, flags=re.M)
        # Carry forward China's settled core. The Islamic states are authored
        # individually below, rather than giving Egypt and Syria to Arabia.
        owner = None
        if 99 <= x <= 107 and 37 <= y <= 47:
            owner = 2
        if owner is not None:
            block = re.sub(r'(CityOwner|UnitOwner)=\d+', lambda m: m[1] + '=' + str(owner), block)
            block = re.sub(r'Player\d+Culture=', 'Player' + str(owner) + 'Culture=', block)
        if any(max(abs(x - cx), abs(y - cy)) <= 1 for cx, cy in CITIES):
            # Remove inherited Byzantine/minor culture around replaced cities.
            block = re.sub(r'^[ \t]*Player\d+Culture=[^\n]*', '', block, flags=re.M)
        if (x, y) in CITIES:
            if not re.search(r'PlotType=[12]\b', block):
                raise ValueError('Authored city must be on passable land: ' + str((x, y)))
            block = re.sub(r'\s*Begin(?:City|Unit)\b.*?End(?:City|Unit)', '', block, flags=re.S)
            block = re.sub(r'^[ \t]*(?:Player\d+Culture|Owner|ImprovementType)=[^\n]*', '', block, flags=re.M)
            block += city_and_units((x, y), *CITIES[(x, y)])
        # Local initial borders and roads, preserving the six settler starts.
        if re.search(r'PlotType=[12]\b', block):
            for (cx, cy), (cityOwner, _, _) in CITIES.items():
                if max(abs(x - cx), abs(y - cy)) <= 1:
                    block += '\n\tPlayer' + str(cityOwner) + 'Culture=10\n'
                    block = field(block, 'RouteType', 'ROUTE_ROAD')
                    break
        if (x, y) == (59, 39):
            for kind in ('GALLEY', 'GALLEY', 'TRIREME'):
                block += ('\n\tBeginUnit\n\t\tUnitType=UNIT_' + kind + ', UnitOwner=6\n'
                          '\t\tUnitAIType=UNITAI_' + ('ASSAULT_SEA' if kind == 'GALLEY' else 'ESCORT_SEA') + '\n\tEndUnit\n')
        return 'BeginPlot' + block + 'EndPlot'

    text = re.sub(r'BeginPlot\b(.*?)EndPlot', plot, text, flags=re.S)
    for line in text.splitlines():
        if re.match(r'^\s*(?:Begin|End)(?:Game|Team|Player|Map|Plot|City|Unit)\b', line):
            if not re.fullmatch(r'\s*(?:Begin|End)(?:Game|Team|Player|Map|Plot|City|Unit)\s*', line):
                raise ValueError('WB block marker must be on its own line: ' + line)
    from korea_scenarios import apply_korea
    text = apply_korea(text)
    TARGET.write_text(text, encoding='utf-8')
    write_leader_text()
    print(TARGET.relative_to(ROOT))


if __name__ == '__main__':
    main()
