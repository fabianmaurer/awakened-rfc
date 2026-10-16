"""Generate current civic unlock summaries and wire their Strategy keys."""
from pathlib import Path
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
        '+15% Kampfst\xe4rke f\xfcr Landeinheiten gegen Barbaren und L\xe4nder mit anderer oder keiner Staatsreligion. Geb\xe4ude der Staatsreligion geben +1 Zufriedenheit, andere religi\xf6se Geb\xe4ude -2 Zufriedenheit.'),
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
        'Erm\u00f6glicht Sklavenspezialisten. Versklavt eroberte V\u00f6lker.'),
    'SERFDOM': (
        '+1 food from farms; workers build improvements 50% faster, and population can rush units.',
        '+1 Nahrung durch Bauernh\u00f6fe; Bautrupps errichten Verbesserungen 50% schneller und Bev\u00f6lkerung kann Einheiten beschleunigen.'),
    'PLANNED_ECONOMY': (
        '+1 production from workshops, watermills and windmills; +1 food from farms; -10% commerce. No trade routes with Capitalists.',
        '+1 Produktion durch Werkstätten, Wasser- und Windmühlen; +1 Nahrung durch Bauernhöfe; -10% Wirtschaftspunkte. Keine Handelswege mit Kapitalisten.'),
    'CORPORATE_ECONOMY': (
        '+1 free specialist in every city; cottage improvements grow twice as fast. No trade routes with Communists.',
        '+1 freier Spezialist in jeder Stadt; Hüttenverbesserungen wachsen doppelt so schnell. Keine Handelswege mit Kommunisten.'),
    'WARRIOR_SOCIETY': (
        'Melee units start with +2 experience; siege units have -20% combat strength.',
        'Nahkampfeinheiten starten mit +2 Erfahrung; Belagerungseinheiten haben -20% Kampfstärke.'),
    'MILITIA': (
        '+30% city defense, but -10% combat strength outside your own territory.',
        '+30% Stadtverteidigung, aber -10% Kampfstärke außerhalb des eigenen Gebiets.'),
    'KNIGHTHOOD': (
        '+6 experience for newly trained mounted units and Samurai; +2 happiness from castles. Called Bushido for Japan.',
        '+6 Erfahrung f\xfcr neu ausgebildete berittene Einheiten und Samurai; +2 Zufriedenheit durch Burgen. Hei\xdft f\xfcr Japan Bushido.'),
    'PROFESSIONAL_ARMY': (
        'Units start with +5 experience.',
        'Einheiten starten mit +5 Erfahrung.'),
    'CONSCRIPTION': (
        '+25% unit production. Food surplus contributes to land military unit production.',
        '+25% Einheitenproduktion. Nahrungs\xfcberschuss tr\xe4gt zur Produktion milit\xe4rischer Landeinheiten bei.'),
    'ANCESTOR_CULT': (
        '+1 culture from monuments, including unique replacements.',
        '+1 Kultur durch Monumente, einschließlich einzigartiger Ersatzgebäude.'),
    'STATE_RELIGION': (
        '+1 happiness in cities with the state religion; +100% production for missionaries of any religion.',
        '+1 Zufriedenheit in Städten mit Staatsreligion; +100% Produktion für Missionare aller Religionen.'),
    'GOD_STATE': (
        'Cities with the state religion gain +2 happiness and +10% production; cities without it get -2 happiness.',
        'Städte mit Staatsreligion erhalten +2 Zufriedenheit und +10% Produktion; Städte ohne sie erhalten -2 Zufriedenheit.'),
    'TOLERANCE': (
        'No unhappiness from non-state religions and no different-religion diplomatic penalties involving your country. +2 relations toward you from countries with a different state religion, except State Atheism.',
        'Keine Unzufriedenheit durch fremde Religionen und keine diplomatischen Religionsmali mit eurem Land. +2 Beziehungen zu euch bei L\xe4ndern mit anderer Staatsreligion, au\xdfer Staatsatheismus.'),
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

    root = ET.Element('Civ4GameText', {'xmlns': 'http://www.firaxis.com'})
    for civic, (english, german) in SUMMARIES.items():
        entry = ET.SubElement(root, 'TEXT')
        ET.SubElement(entry, 'Tag').text = 'TXT_KEY_RFCMP_CIVIC_' + civic + '_STRATEGY'
        for language in ('English', 'French', 'German', 'Italian', 'Spanish'):
            ET.SubElement(entry, language).text = german if language == 'German' else english
    ET.indent(root, space='    ')
    output = ASSETS / 'XML/Text/CIV4GameText_CivicStrategies.xml'
    output.write_bytes(b'<?xml version="1.0" encoding="UTF-8"?>\n' +
        ET.tostring(root, encoding='ascii', xml_declaration=False) + b'\n')
    print('Updated strategy summaries for', len(SUMMARIES), 'civics')

if __name__ == '__main__':
    main()
