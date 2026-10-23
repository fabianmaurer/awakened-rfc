"""Generate current civic unlock summaries and wire their Strategy keys."""
from pathlib import Path
from military_civic_text import ENTRIES
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'Awakened RFC/Assets'
SUMMARIES = {
    'TRIBAL_SYSTEM': (
        '+20% unit production, -20% research, +100% distance and city-count maintenance.',
        '+20% Einheitenproduktion, -20% Forschung, +100% entfernungs- und städtezahlabhängiger Unterhalt.'),
    'MONARCHY': (
        'Capital buildings give +1 culture and +1 commerce each; capital world wonders give +1 happiness empire-wide, capped at +3. Enables inheritance events.',
        'Hauptstadtgeb\xe4ude geben je +1 Kultur und +1 Handel; Weltwunder der Hauptstadt geben reichsweit +1 Zufriedenheit, maximal +3. Erm\xf6glicht Erbfolgeereignisse.'),
    'REPUBLIC': (
        'Assigned specialists except slaves consume 1 less food.',
        'Zugewiesene Spezialisten au\xdfer Sklaven verbrauchen 1 Nahrung weniger.'),
    'DICTATORSHIP': (
        '+20% production and no war weariness, but -2 happiness in every city.',
        '+20% Produktion und keine Kriegsmüdigkeit, aber -2 Zufriedenheit in jeder Stadt.'),
    'DEMOCRACY': (
        '+2 happiness in every city and +1 commerce per specialist. Other civics are decided by elections. No stability penalties from incompatible civics.',
        '+2 Zufriedenheit in jeder Stadt und +1 Handel je Spezialist. Andere Staatsformen werden durch Wahlen entschieden. Keine Stabilit\u00e4tsmali durch unvereinbare Staatsformen.'),
    'DESPOTISM': (
        '+1 happiness from palaces and monuments, including unique replacements.',
        '+1 Zufriedenheit durch Paläste und Monumente, einschließlich einzigartiger Ersatzgebäude.'),
    'THEOCRATIC_LEGITIMACY': (
        '+15% land combat strength against barbarians and countries with a different or no state religion. State-religion buildings give +1 happiness; other religious buildings give -2 happiness.',
        '+15% Kampfst\xe4rke f\xfcr Landeinheiten gegen Barbaren und L\xe4nder mit fremder oder keiner Staatsreligion. Geb\xe4ude der Staatsreligion geben +1 Zufriedenheit, Geb\xe4ude fremder Religionen -2 Zufriedenheit.'),
    'PLUTOCRACY': (
        '+25% gold income and +50% trade-route commerce.',
        '+25% Goldeinnahmen und +50% Wirtschaftspunkte durch Handelsrouten.'),
    'NATIONALISM': (
        '+5 culture per city and +20% production. -5 happiness in cities with a foreign culture plurality.',
        '+5 Kultur je Stadt und +20% Produktion. -5 Zufriedenheit in Städten mit vorherrschender fremder Kultur.'),
    'RULE_OF_LAW': (
        '+2 happiness in every city and +10% commerce.',
        '+2 Zufriedenheit in jeder Stadt und +10% Wirtschaftspunkte.'),
    'SELF_SUFFICIENCY': (
        '+2 health in every city. Cottage improvements do not grow. Cannot assign specialists.',
        '+2 Gesundheit in jeder Stadt. Hüttenverbesserungen wachsen nicht. Kann keine Spezialisten zuweisen.'),
    'SLAVERY': (
        'Enables slave specialists. Enslave conquered peoples.',
        'Schaltet Sklavenspezialisten frei. Versklavt eroberte V\u00f6lker.'),
    'SERFDOM': (
        '+1 food from farms; workers build improvements 50% faster. Can sacrifice population to rush units only, not buildings or projects.',
        '+1 Nahrung durch Bauernh\u00f6fe; Bautrupps errichten Verbesserungen 50% schneller. Kann Bev\u00f6lkerung opfern, um nur Einheiten zu beschleunigen, keine Geb\u00e4ude oder Projekte.'),
    'PLANNED_ECONOMY': (
        '+1 production from workshops, watermills and windmills; +1 food from farms; -10% commerce. No trade routes with Capitalists.',
        '+1 Produktion durch Werkstätten, Wasser- und Windmühlen; +1 Nahrung durch Bauernhöfe; -10% Wirtschaftspunkte. Keine Handelswege mit Kapitalisten.'),
    'CORPORATE_ECONOMY': (
        '+1 free specialist in every city; cottage improvements grow twice as fast. No trade routes with Communists.',
        '+1 freier Spezialist in jeder Stadt; Hüttenverbesserungen wachsen doppelt so schnell. Keine Handelswege mit Kommunisten.'),
    'WARRIOR_SOCIETY': (
        'Melee units start with +2 experience; siege units have -20% combat strength.',
        'Nahkampfeinheiten starten mit +2 Erfahrung; Belagerungseinheiten haben -20% Kampfstärke.'),
    'NAVAL_WARFARE': (ENTRIES['TXT_KEY_RFCMP_CIVIC_NAVAL_WARFARE_STRATEGY']['English'],
        ENTRIES['TXT_KEY_RFCMP_CIVIC_NAVAL_WARFARE_STRATEGY']['German']),
    'FEUDAL_RETINUES': (ENTRIES['TXT_KEY_RFCMP_CIVIC_FEUDAL_RETINUES_STRATEGY']['English'],
        ENTRIES['TXT_KEY_RFCMP_CIVIC_FEUDAL_RETINUES_STRATEGY']['German']),
    'PROFESSIONAL_ARMY': (
        'Units start with +5 experience.',
        'Einheiten starten mit +5 Erfahrung.'),
    'CONSCRIPTION': (
        '+25% unit production. Food surplus contributes to land military unit production.',
        '+25% Einheitenproduktion. Nahrungs\xfcberschuss tr\xe4gt zur Produktion milit\xe4rischer Landeinheiten bei.'),
    'ANCESTOR_CULT': (
        '+1 culture from monuments, including unique replacements.[NEWLINE]+1 unhappiness from state religion.',
        '+1 Kultur durch Monumente, einschlie\u00dflich einzigartiger Ersatzgeb\u00e4ude.[NEWLINE]+1 Unzufriedenheit durch die Staatsreligion.'),
    'STATE_RELIGION': (
        '+1 happiness in cities with the state religion; +100% production for its missionaries and +25% production for its religious buildings.',
        '+1 Zufriedenheit in St\xe4dten mit Staatsreligion; +100% Produktion f\xfcr Missionare und +25% Produktion f\xfcr Geb\xe4ude der Staatsreligion.'),
    'GOD_STATE': (
        '+10% production in cities with the state religion; -1 happiness per non-state religion. Conquered cities are pacified by conversion.',
        '+10% Produktion in St\xe4dten mit Staatsreligion; -1 Zufriedenheit je fremder Religion. Eroberte St\xe4dte werden durch Konvertierung befriedet.'),
    'TOLERANCE': (
        'No unhappiness from non-state religions and no different-religion diplomatic penalties involving your country. +2 relations toward you from countries with a different state religion, except State Atheism. +5 percentage points to incoming religion spread chances through trade routes. Allows training missionaries of any religion.',
        'Keine Unzufriedenheit durch fremde Religionen und keine diplomatischen Religionsmali mit eurem Land. +2 Beziehungen zu euch bei L\xe4ndern mit anderer Staatsreligion, au\xdfer Staatsatheismus. +5 Prozentpunkte auf die Chance der Religionsverbreitung durch Handelswege in eigene St\xe4dte. Erlaubt die Ausbildung von Missionaren aller Religionen.'),
    'STATE_ATHEISM': (
        '+10% research and +10% production; -1 happiness in all cities. Religious buildings have no effects and religions cannot spread.',
        '+10% Forschung und +10% Produktion; -1 Zufriedenheit in allen St\xe4dten. Religi\xf6se Geb\xe4ude wirken nicht und Religionen verbreiten sich nicht.'),
}

def main():
    civic_path = ASSETS / 'XML/GameInfo/CIV4CivicInfos.xml'
    source = civic_path.read_bytes().decode('utf-8')
    infos = re.findall(r'<CivicInfo>.*?</CivicInfo>', source, re.S)
    assert len(infos) == len(SUMMARIES), 'Update summaries for the current civic set'
    for info in infos:
        civic = re.search(r'<Type>CIVIC_(.*?)</Type>', info).group(1)
        assert civic in SUMMARIES, civic
        replacement, count = re.subn(r'<Strategy>.*?</Strategy>',
            '<Strategy>TXT_KEY_RFCMP_CIVIC_' + civic + '_STRATEGY</Strategy>', info, flags=re.S)
        assert count == 1, civic
        source = source.replace(info, replacement, 1)
    civic_path.write_bytes(source.encode('utf-8'))

    output = ASSETS / 'XML/Text/CIV4GameText_CivicStrategies.xml'
    previous = {}
    if output.exists():
        for entry in ET.parse(output).getroot():
            parts = {c.tag.split('}')[-1]: c.text for c in entry}
            previous[parts['Tag']] = parts
    root = ET.Element('Civ4GameText', {'xmlns': 'http://www.firaxis.com'})
    for civic, (english, german) in SUMMARIES.items():
        entry = ET.SubElement(root, 'TEXT')
        ET.SubElement(entry, 'Tag').text = 'TXT_KEY_RFCMP_CIVIC_' + civic + '_STRATEGY'
        for language in ('English', 'French', 'German', 'Italian', 'Spanish'):
            key = 'TXT_KEY_RFCMP_CIVIC_' + civic + '_STRATEGY'
            existing = previous.get(key, {})
            fallback = german if language == 'German' else english
            if language not in ('English', 'German') and existing.get('English') == english:
                fallback = existing.get(language, fallback)
            ET.SubElement(entry, language).text = ENTRIES.get(key, {}).get(language, fallback)
    ET.indent(root, space='    ')
    output = ASSETS / 'XML/Text/CIV4GameText_CivicStrategies.xml'
    output.write_bytes(b'<?xml version="1.0" encoding="UTF-8"?>\n' +
        ET.tostring(root, encoding='ascii', xml_declaration=False) + b'\n')
    print('Updated strategy summaries for', len(SUMMARIES), 'civics')

if __name__ == '__main__':
    main()
