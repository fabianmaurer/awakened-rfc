"""Author the five XL Indian identities from existing Civ4 art and XML templates.

Keeps XML IDs stable by replacing our own entries in place, or appending them.
Every generated text entry includes all five supported languages.
"""
from pathlib import Path
import copy
import re
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'Awakened RFC/Assets'
sys.path.insert(0, str(ASSETS / 'Python'))
from IndianCivsData import CIVS, NAMES

SPECS = (
    ('Tribes of Magadha', 'Magadha', 'Magadhan', 'Magadhan Council', 'ASOKA', 'YELLOW',
     'Sacred Learning', 'Priests gain +1 research.', 'WAR_ELEPHANT', 'Mahout Elephant',
     'LIBRARY', 'Gurukula', 'Develop the Ganges plain and build a civilization of sacred learning.'),
    ('Chola Empire', 'Chola', 'Chola', 'Vijayalaya', 'SURYAVARMAN', 'DARK_RED',
     'Oceanic Networks', 'Coastal cities gain +1 trade route.', 'GALLEY', 'Kappal',
     'HARBOR', 'Merchant Guild', 'Unite the Tamil country and prosper through Indian Ocean trade.'),
    ('Delhi Sultanate', 'Delhi', 'Delhi', 'Qutb al-Din Aibak', 'MEHMED', 'DARK_GREEN',
     'Mounted Conquest', 'Mounted units gain +25% city attack.', 'KNIGHT', 'Ghulam',
     'COURTHOUSE', 'Diwan', 'Use mounted armies to build a northern Indian sultanate.'),
    ('Bengal Sultanate', 'Bengal', 'Bengali', 'Ilyas Shah', 'SALADIN', 'LIGHT_BLUE',
     'Delta Commerce', 'River tiles gain +1 commerce.', 'CROSSBOWMAN', 'Paik',
     'MARKET', 'Muslin Bazaar', 'Turn the Bengal delta into a wealthy centre of river and overseas commerce.'),
    ('Vijayanagara Empire', 'Vijayanagara', 'Vijayanagaran', 'Harihara I', 'ASOKA', 'PURPLE',
     'Fortified Heartland', 'Cities gain +25% defense.', 'PIKEMAN', 'Nayaka',
     'HINDU_TEMPLE', 'Royal Temple', 'Defend the southern heartland and build a rich temple civilization.'),
)
GOALS = (
    ('Control the Hindu and Buddhist holy cities by 200 BC.', 'Accumulate 2,500 culture by 200 AD.', 'Control six cities in the Ganges region by 600 AD.'),
    ('Control four cities in southern India by 1100 AD.', 'Control a city in Sri Lanka and trade with three foreign civilizations by 1250 AD.', 'Accumulate 3,000 gold by 1300 AD.'),
    ('Control six cities in northern India by 1350 AD.', 'Spread Islam to eight of your cities by 1450 AD.', 'Control Delhi and three cities in the Deccan by 1500 AD.'),
    ('Control six cities on rivers by 1500 AD.', 'Trade with four foreign civilizations by 1600 AD.', 'Accumulate 5,000 gold by 1700 AD.'),
    ('Control four cities in southern India by 1500 AD.', 'Have eight Hindu temples by 1600 AD.', 'Accumulate 50,000 culture by 1650 AD.'),
)
POWER_TRANSLATIONS = (
    ('Les pr\u00eatres gagnent +1 recherche.', 'Priester erhalten +1 Forschung.', 'I sacerdoti ottengono +1 ricerca.', 'Los sacerdotes obtienen +1 de investigaci\u00f3n.'),
    ('Les villes c\u00f4ti\u00e8res gagnent une route commerciale.', 'K\u00fcstenst\u00e4dte erhalten einen zus\u00e4tzlichen Handelsweg.', 'Le citt\u00e0 costiere ottengono una rotta commerciale aggiuntiva.', 'Las ciudades costeras obtienen una ruta comercial adicional.'),
    ('Les unit\u00e9s mont\u00e9es gagnent +25 % en attaque urbaine.', 'Berittene Einheiten erhalten +25 % Stadtangriff.', 'Le unit\u00e0 montate ottengono +25% all\u2019attacco delle citt\u00e0.', 'Las unidades montadas obtienen +25% al atacar ciudades.'),
    ('Les cases riveraines gagnent +1 commerce.', 'Flussfelder erhalten +1 Handel.', 'Le caselle fluviali ottengono +1 commercio.', 'Las casillas de r\u00edo obtienen +1 de comercio.'),
    ('Les villes gagnent +25 % de d\u00e9fense.', 'St\u00e4dte erhalten +25 % Verteidigung.', 'Le citt\u00e0 ottengono +25% alla difesa.', 'Las ciudades obtienen +25% de defensa.'),
)

# Names, descriptions and goals need translations as well as the power effects.
# Proper names without a conventional German form retain their spelling.
GERMAN_SPECS = (
    ('St\u00e4mme von Magadha', 'Magadha', 'Magadhisch', 'Rat von Magadha',
     'Heilige Gelehrsamkeit', 'Mahut-Elefant', 'Gurukula',
     'Erschlie\u00dft die Gangesebene und gr\u00fcndet eine Zivilisation der heiligen Gelehrsamkeit.'),
    ('Chola-Reich', 'Chola', 'cholisch', 'Vijayalaya',
     'Ozeanische Handelsnetze', 'Kappal', 'H\u00e4ndlergilde',
     'Vereint das tamilische Land und gelangt durch den Handel im Indischen Ozean zu Wohlstand.'),
    ('Sultanat von Delhi', 'Delhi', 'delhisch', 'Qutb ad-Din Aibak',
     'Berittene Eroberer', 'Ghulam', 'Diwan',
     'Errichtet mit berittenen Heeren ein Sultanat in Nordindien.'),
    ('Sultanat von Bengalen', 'Bengalen', 'bengalisch', 'Ilyas Schah',
     'Handel im Delta', 'Paik', 'Musselinbasar',
     'Macht das Gangesdelta zu einem wohlhabenden Zentrum des Fluss- und \u00dcberseehandels.'),
    ('Vijayanagara-Reich', 'Vijayanagara', 'vijayanagarisch', 'Harihara I.',
     'Befestigtes Kernland', 'Nayaka', 'K\u00f6niglicher Tempel',
     'Verteidigt das s\u00fcdliche Kernland und errichtet eine reiche Tempelkultur.'),
)
GERMAN_GOALS = (
    ('Kontrolliert bis 200 v. Chr. die heiligen St\u00e4dte des Hinduismus und des Buddhismus.',
     'Sammelt bis 200 n. Chr. 2.500 Kultur an.',
     'Kontrolliert bis 600 n. Chr. sechs St\u00e4dte im Gangesgebiet.'),
    ('Kontrolliert bis 1100 n. Chr. vier St\u00e4dte in S\u00fcdindien.',
     'Kontrolliert bis 1250 n. Chr. eine Stadt auf Sri Lanka und handelt mit drei fremden Zivilisationen.',
     'Sammelt bis 1300 n. Chr. 3.000 Gold an.'),
    ('Kontrolliert bis 1350 n. Chr. sechs St\u00e4dte in Nordindien.',
     'Verbreitet den Islam bis 1450 n. Chr. in acht Eurer St\u00e4dte.',
     'Kontrolliert bis 1500 n. Chr. Delhi und drei St\u00e4dte im Dekkan.'),
    ('Kontrolliert bis 1500 n. Chr. sechs St\u00e4dte an Fl\u00fcssen.',
     'Handelt bis 1600 n. Chr. mit vier fremden Zivilisationen.',
     'Sammelt bis 1700 n. Chr. 5.000 Gold an.'),
    ('Kontrolliert bis 1500 n. Chr. vier St\u00e4dte in S\u00fcdindien.',
     'Besitzt bis 1600 n. Chr. acht hinduistische Tempel.',
     'Sammelt bis 1650 n. Chr. 50.000 Kultur an.'),
)


def block(text, tag, key):
    return next(
        m[0] for m in re.finditer('<' + tag + r'>.*?</' + tag + '>', text, re.S)
        if re.search(r'<Type>' + re.escape(key) + r'</Type>', m[0]))


def install(path, tag, originals, additions):
    text = path.read_text(encoding='utf-8')
    for key, node in additions:
        ET.indent(node, space='\t')
        new = ET.tostring(node, encoding='unicode')
        try: old = block(text, tag, key)
        except StopIteration:
            text = text.replace('</' + originals + '>', '\t\t' + new + '\n\t</' + originals + '>')
        else: text = text.replace(old, new, 1)
    path.write_text(text, encoding='utf-8', newline='\n')


def set_value(node, tag, text):
    child = node.find(tag)
    if child is None: raise ValueError('Missing template field ' + tag)
    child.text = str(text)


def text_key(entries, key, english, translations=None):
    values = [english] * 5
    if translations: values[1:] = translations
    entries[key] = values
    return key


# Country names use complete localized place phrases to preserve grammar.
COUNTRY_PLACES = {
    'HAR': ('of Harappa', 'de Harappa', 'von Harappa', 'di Harappa', 'de Harappa'),
    'GAN': ('of Magadha', 'de Magadha', 'von Magadha', 'di Magadha', 'de Magadha'),
    'CHO': ('of the Chola', 'des Chola', 'der Chola', 'dei Chola', 'de los Chola'),
    'DEL': ('of Delhi', 'de Delhi', 'von Delhi', 'di Delhi', 'de Delhi'),
    'BEN': ('of Bengal', 'du Bengale', 'von Bengalen', 'del Bengala', 'de Bengala'),
    'VIJ': ('of Vijayanagara', 'de Vijayanagara', 'von Vijayanagara', 'di Vijayanagara', 'de Vijayanagara'),
}
COUNTRY_FORMS = {
    'TRIBES': ('Clans %s', 'Clans %s', 'St\xe4mme %s', 'Clan %s', 'Clanes %s'),
    'KINGDOM': ('Kingdom %s', 'Royaume %s', 'K\xf6nigreich %s', 'Regno %s', 'Reino %s'),
    'REPUBLIC': ('Republic %s', 'R\xe9publique %s', 'Republik %s', 'Repubblica %s', 'Rep\xfablica %s'),
    'FEDERATION': ('Federation %s', 'F\xe9d\xe9ration %s', 'F\xf6deration %s', 'Federazione %s', 'Federaci\xf3n %s'),
    'PEOPLE': ("People's Republic %s", 'R\xe9publique populaire %s', 'Volksrepublik %s', 'Repubblica popolare %s', 'Rep\xfablica Popular %s'),
    'STATE': ('State %s', '\xc9tat %s', 'Staat %s', 'Stato %s', 'Estado %s'),
    'SULTANATE': ('Sultanate %s', 'Sultanat %s', 'Sultanat %s', 'Sultanato %s', 'Sultanato %s'),
    'HOLY': ('Sacred Kingdom %s', 'Royaume sacr\xe9 %s', 'Heiliges Reich %s', 'Regno sacro %s', 'Reino sagrado %s'),
    'THEOCRACY': ('Theocracy %s', 'Th\xe9ocratie %s', 'Gottesstaat %s', 'Teocrazia %s', 'Teocracia %s'),
    'LEAGUE': ('Merchant League %s', 'Ligue marchande %s', 'Handelsbund %s', 'Lega mercantile %s', 'Liga mercantil %s'),
}
COUNTRY_OVERRIDES = {
    ('HAR', 'TRIBES'): ('City-States of Harappa', 'Cit\xe9s-\xc9tats de Harappa', 'Stadtstaaten von Harappa', 'Citt\xe0-stato di Harappa', 'Ciudades-Estado de Harappa'),
    ('GAN', 'TRIBES'): ('Tribes of Magadha', 'Tribus de Magadha', 'St\xe4mme von Magadha', 'Trib\xf9 di Magadha', 'Tribus de Magadha'),
    ('CHO', 'KINGDOM'): ('Chola Empire', 'Empire chola', 'Chola-Reich', 'Impero Chola', 'Imperio chola'),
    ('VIJ', 'KINGDOM'): ('Vijayanagara Empire', 'Empire de Vijayanagara', 'Vijayanagara-Reich', 'Impero di Vijayanagara', 'Imperio de Vijayanagara'),
    ('VIJ', 'HOLY'): ('Temple Realm of Vijayanagara', 'Royaume des temples de Vijayanagara', 'Tempelreich von Vijayanagara', 'Regno dei templi di Vijayanagara', 'Reino de los templos de Vijayanagara'),
}


# Historical identities and territorial successors; conditions live in CvPlayer.cpp.
HISTORICAL_COUNTRY_NAMES = {
    'MAGADHA': ('Kingdom of Magadha', 'Royaume du Magadha', 'K\xf6nigreich Magadha', 'Regno di Magadha', 'Reino de Magadha'),
    'NANDA': ('Nanda Empire', 'Empire nanda', 'Nanda-Reich', 'Impero Nanda', 'Imperio nanda'),
    'MAURYA': ('Mauryan Empire', 'Empire maurya', 'Maurya-Reich', 'Impero Maurya', 'Imperio maurya'),
    'SHUNGA': ('Shunga Empire', 'Empire shunga', 'Shunga-Reich', 'Impero Shunga', 'Imperio shunga'),
    'KANVA': ('Kanva Kingdom', 'Royaume kanva', 'Kanva-Reich', 'Regno Kanva', 'Reino kanva'),
    'GUPTA': ('Gupta Empire', 'Empire gupta', 'Gupta-Reich', 'Impero Gupta', 'Imperio gupta'),
    'PALA': ('Pala Empire', 'Empire pala', 'Pala-Reich', 'Impero Pala', 'Imperio pala'),
    'KOSALA': ('Kingdom of Kosala', 'Royaume du Kosala', 'K\xf6nigreich Kosala', 'Regno di Kosala', 'Reino de Kosala'),
    'HARSHA': ("Harsha's Empire", 'Empire de Harsha', 'Reich des Harsha', 'Impero di Harsha', 'Imperio de Harsha'),
    'DELHI': ('Delhi Sultanate', 'Sultanat de Delhi', 'Sultanat von Delhi', 'Sultanato di Delhi', 'Sultanato de Delhi'),
    'SUR': ('Sur Empire', 'Empire sur', 'Sur-Reich', 'Impero Sur', 'Imperio sur'),
    'MUGHAL': ('Mughal Empire', 'Empire moghol', 'Mogulreich', 'Impero moghul', 'Imperio mogol'),
    'BENGAL': ('Bengal Sultanate', 'Sultanat du Bengale', 'Sultanat von Bengalen', 'Sultanato del Bengala', 'Sultanato de Bengala'),
    'BENGAL_NAWAB': ('Nawabate of Bengal', 'Nawabat du Bengale', 'Nawabstaat Bengalen', 'Nawabato del Bengala', 'Nawabato de Bengala'),
    'THANJAVUR_MARATHA': ('Thanjavur Maratha Kingdom', 'Royaume marathe de Thanjavur', 'Marathenreich von Thanjavur', 'Regno maratha di Thanjavur', 'Reino maratha de Thanjavur'),
    'THANJAVUR_NAYAK': ('Thanjavur Nayak Kingdom', 'Royaume nayak de Thanjavur', 'Nayaka-Reich von Thanjavur', 'Regno nayak di Thanjavur', 'Reino nayaka de Thanjavur'),
    'MADURAI_NAYAK': ('Madurai Nayak Kingdom', 'Royaume nayak de Madurai', 'Nayaka-Reich von Madurai', 'Regno nayak di Madurai', 'Reino nayaka de Madurai'),
    'MYSORE': ('Kingdom of Mysore', 'Royaume de Mysore', 'K\xf6nigreich Mysore', 'Regno di Mysore', 'Reino de Mysore'),
    'MADURAI_SULTANATE': ('Madurai Sultanate', 'Sultanat de Madurai', 'Sultanat von Madurai', 'Sultanato di Madurai', 'Sultanato de Madurai'),
    'PANDYA': ('Pandya Kingdom', 'Royaume pandya', 'Pandya-Reich', 'Regno Pandya', 'Reino pandya'),
    'CHOLA': ('Chola Empire', 'Empire chola', 'Chola-Reich', 'Impero Chola', 'Imperio chola'),
    'VIJAYANAGARA': ('Vijayanagara Empire', 'Empire de Vijayanagara', 'Vijayanagara-Reich', 'Impero di Vijayanagara', 'Imperio de Vijayanagara'),
}


def write_country_names():
    result = ['<?xml version="1.0" encoding="UTF-8"?>\n<Civ4GameText xmlns="http://www.firaxis.com">\n']
    for root, places in sorted(COUNTRY_PLACES.items()):
        for form, templates in sorted(COUNTRY_FORMS.items()):
            values = COUNTRY_OVERRIDES.get((root, form), tuple(template % place for template, place in zip(templates, places)))
            result.append('  <TEXT>\n    <Tag>TXT_KEY_CIVIC_' + root + '_' + form + '</Tag>\n')
            for lang, value in zip(('English', 'French', 'German', 'Italian', 'Spanish'), values):
                result.append('    <' + lang + '>' + escape(value) + '</' + lang + '>\n')
            result.append('  </TEXT>\n')
    for name, values in sorted(HISTORICAL_COUNTRY_NAMES.items()):
        result.append('  <TEXT>\n    <Tag>TXT_KEY_HIST_' + name + '</Tag>\n')
        for lang, value in zip(('English', 'French', 'German', 'Italian', 'Spanish'), values):
            result.append('    <' + lang + '>' + escape(value) + '</' + lang + '>\n')
        result.append('  </TEXT>\n')
    result.append('</Civ4GameText>\n')
    (ASSETS / 'XML/Text/CIV4GameText_CivicCountryNames.xml').write_bytes(''.join(result).encode('ascii', 'xmlcharrefreplace'))


def main():
    civPath = ASSETS / 'XML/Civilizations/CIV4CivilizationInfos.xml'
    leaderPath = ASSETS / 'XML/Civilizations/CIV4LeaderHeadInfos.xml'
    unitPath = ASSETS / 'XML/Units/CIV4UnitInfos.xml'
    buildingPath = ASSETS / 'XML/Buildings/CIV4BuildingInfos.xml'
    texts = [p.read_text(encoding='utf-8') for p in (civPath,leaderPath,unitPath,buildingPath)]
    civs, leaders, units, buildings, entries = [], [], [], [], {}
    for offset, (data, spec) in enumerate(zip(CIVS, SPECS)):
        civ, short, birth, year, capital, _, _, _, _ = data
        desc, name, adjective, leaderName, leaderBase, color, power, effect, unitBase, unitName, buildingBase, buildingName, strategy = spec
        prefix = 'TXT_KEY_' + short
        nameTranslations = None
        if civ == 'GANGES':
            nameTranslations = ('Tribus de Magadha', 'St\u00e4mme von Magadha', 'Trib\u00f9 di Magadha', 'Tribus de Magadha')
        text_key(entries, prefix + '_DESC', desc, nameTranslations)
        text_key(entries, prefix + '_SHORT', name)
        text_key(entries, prefix + '_ADJ', adjective, ('Magadhien', 'Magadhisch', 'Magadhano', 'Magadh\u00ed') if civ == 'GANGES' else None)
        text_key(entries, 'TXT_KEY_LEADER_' + short, leaderName, ('Conseil de Magadha', 'Rat von Magadha', 'Consiglio di Magadha', 'Consejo de Magadha') if civ == 'GANGES' else None)
        text_key(entries, 'TXT_KEY_UP_' + short, power)
        text_key(entries, 'TXT_KEY_UP_' + short + '2', effect, POWER_TRANSLATIONS[offset])
        text_key(entries, prefix + '_STRATEGY', strategy)
        text_key(entries, prefix + '_PEDIA', strategy + ' Its unique power is ' + power + ': ' + effect)
        for i, goal in enumerate(GOALS[offset]): text_key(entries, 'TXT_KEY_UHV_' + short + str(i+1), goal)
        node = ET.fromstring(block(texts[0], 'CivilizationInfo', 'CIVILIZATION_INDIA'))
        for tag,value in [('Type','CIVILIZATION_'+civ),('Description',prefix+'_DESC'),('ShortDescription',prefix+'_SHORT'),('Adjective',prefix+'_ADJ'),('Civilopedia',prefix+'_PEDIA'),('DefaultPlayerColor','PLAYERCOLOR_'+color)]: set_value(node,tag,value)
        node.find('Cities').clear()
        for i,(x,y,city) in enumerate(NAMES[offset]):
            ET.SubElement(node.find('Cities'),'City').text = text_key(entries, prefix+'_CITY'+str(i), city)
        for tag,child,itemType,itemValue in [('Units','Unit','UnitClassType','UNITCLASS_'+unitBase),('Buildings','Building','BuildingClassType','BUILDINGCLASS_'+buildingBase)]:
            parent=node.find(tag);parent.clear();item=ET.SubElement(parent,child);ET.SubElement(item,itemType).text=itemValue
            ET.SubElement(item,child+'Type').text=('UNIT_' if tag=='Units' else 'BUILDING_')+short+'_UNIQUE'
        parent=node.find('Leaders');parent.clear();item=ET.SubElement(parent,'Leader');ET.SubElement(item,'LeaderName').text='LEADER_'+civ;ET.SubElement(item,'bLeaderAvailability').text='1'
        parent=node.find('FreeTechs');parent.clear()
        for tech in ('AGRICULTURE','MYSTICISM'):
            item=ET.SubElement(parent,'FreeTech');ET.SubElement(item,'TechType').text='TECH_'+tech;ET.SubElement(item,'bFreeTech').text='1'
        civs.append(('CIVILIZATION_'+civ,node))
        leader=ET.fromstring(block(texts[1],'LeaderHeadInfo','LEADER_'+leaderBase))
        set_value(leader,'Type','LEADER_'+civ);set_value(leader,'Description','TXT_KEY_LEADER_'+short);set_value(leader,'Civilopedia',prefix+'_PEDIA')
        leader.find('Traits').clear()
        religion = 'RELIGION_HINDUISM'
        if offset in (2,3): religion = 'RELIGION_ISLAM'
        set_value(leader, 'FavoriteReligion', religion)
        set_value(leader, 'FavoriteCivic', ('CIVIC_STATE_RELIGION', 'CIVIC_NAVAL_WARFARE',
            'CIVIC_FEUDAL_RETINUES', 'CIVIC_NAVAL_WARFARE', 'CIVIC_STATE_RELIGION')[offset])
        leaders.append(('LEADER_'+civ,leader))
        unit=ET.fromstring(block(texts[2],'UnitInfo','UNIT_'+unitBase))
        for tag,value in [('Type','UNIT_'+short+'_UNIQUE'),('Description',text_key(entries,prefix+'_UNIT',unitName)),('Civilopedia',prefix+'_PEDIA'),('Strategy',prefix+'_STRATEGY')]: set_value(unit,tag,value)
        if offset==0: set_value(unit,'iCombat',9)
        elif offset==1: set_value(unit,'iMoves',3);set_value(unit,'iCargo',3)
        elif offset==2: set_value(unit,'iCombat',11)
        elif offset==3: set_value(unit,'iCityDefense',25)
        else: set_value(unit,'iCombat',7)
        units.append(('UNIT_'+short+'_UNIQUE',unit))
        building=ET.fromstring(block(texts[3],'BuildingInfo','BUILDING_'+buildingBase))
        for tag,value in [('Type','BUILDING_'+short+'_UNIQUE'),('Description',text_key(entries,prefix+'_BUILDING',buildingName)),('Civilopedia',prefix+'_PEDIA'),('Strategy',prefix+'_STRATEGY')]: set_value(building,tag,value)
        if offset==0:
            parent=building.find('SpecialistCounts');parent.clear();item=ET.SubElement(parent,'SpecialistCount');ET.SubElement(item,'SpecialistType').text='SPECIALIST_PRIEST';ET.SubElement(item,'iSpecialistCount').text='2'
        elif offset==1: set_value(building,'iTradeRouteModifier',75)
        elif offset==2: set_value(building,'iMaintenanceModifier',-60)
        elif offset==3:
            building.find('CommerceModifiers')[0].text='35'
        else:
            parent=building.find('YieldChanges');parent.clear()
            for value in (0,2,0):ET.SubElement(parent,'iYield').text=str(value)
        buildings.append(('BUILDING_'+short+'_UNIQUE',building))
        german = GERMAN_SPECS[offset]
        descDE, nameDE, adjDE, leaderDE, powerDE, unitDE, buildingDE, strategyDE = german
        germanEntries = {
            prefix+'_DESC': descDE, prefix+'_SHORT': nameDE, prefix+'_ADJ': adjDE,
            'TXT_KEY_LEADER_'+short: leaderDE, 'TXT_KEY_UP_'+short: powerDE,
            'TXT_KEY_UP_'+short+'2': POWER_TRANSLATIONS[offset][1],
            prefix+'_UNIT': unitDE, prefix+'_BUILDING': buildingDE,
            prefix+'_STRATEGY': strategyDE,
            prefix+'_PEDIA': strategyDE + ' Einzigartige F\u00e4higkeit: ' + powerDE + '. ' + POWER_TRANSLATIONS[offset][1],
        }
        for i, goal in enumerate(GERMAN_GOALS[offset]): germanEntries['TXT_KEY_UHV_'+short+str(i+1)] = goal
        for i, (x, y, city) in enumerate(NAMES[offset]): germanEntries[prefix+'_CITY'+str(i)] = city
        for key, value in germanEntries.items(): entries[key][2] = value
    for path,tag,parent,values in [(civPath,'CivilizationInfo','CivilizationInfos',civs),(leaderPath,'LeaderHeadInfo','LeaderHeadInfos',leaders),(unitPath,'UnitInfo','UnitInfos',units),(buildingPath,'BuildingInfo','BuildingInfos',buildings)]:install(path,tag,parent,values)
    result=['<?xml version="1.0" encoding="UTF-8"?>\n<Civ4GameText xmlns="http://www.firaxis.com">\n']
    for key,values in sorted(entries.items()):
        result.append('  <TEXT>\n    <Tag>'+key+'</Tag>\n')
        for lang,value in zip(('English','French','German','Italian','Spanish'),values):result.append('    <'+lang+'>'+escape(value)+'</'+lang+'>\n')
        result.append('  </TEXT>\n')
    result.append('</Civ4GameText>\n')
    (ASSETS/'XML/Text/CIV4GameText_IndianCivs.xml').write_bytes(''.join(result).encode('ascii','xmlcharrefreplace'))
    print('Authored five civilizations, leaders, unique units, buildings and',len(entries),'localized keys.')


if __name__ == '__main__':
    if '--country-names-only' not in sys.argv:
        main()
    write_country_names()
