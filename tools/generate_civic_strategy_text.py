"""Generate current civic unlock summaries and wire their Strategy keys."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'RFC MP Plus/Assets'
SUMMARIES = {
    'TRIBAL_SYSTEM': (
        '+20% unit production, -20% research, +100% distance and city-count maintenance.',
        '+20% Einheitenproduktion, -20% Forschung, +100% entfernungs- und städtezahlabhängiger Unterhalt.'),
    'MONARCHY': (
        '+25% production for world, team and national wonders. Enables inheritance events.',
        '+25% Produktion f\u00fcr Welt-, Team- und nationale Wunder. Erm\u00f6glicht Erbfolgeereignisse.'),
    'REPUBLIC': (
        '+50% Great Person birth rate.',
        '+50% Geburtenrate Großer Persönlichkeiten.'),
    'DICTATORSHIP': (
        '+20% production and no war weariness, but -2 happiness in every city.',
        '+20% Produktion und keine Kriegsmüdigkeit, aber -2 Zufriedenheit in jeder Stadt.'),
    'DEMOCRACY': (
        '+2 happiness in every city. Every ten turns, elections randomly change one other civic column.',
        '+2 Zufriedenheit in jeder Stadt. Wahlen ändern alle zehn Runden zufällig eine andere Staatsformen-Kategorie.'),
    'DESPOTISM': (
        '+1 happiness from palaces and monuments, including unique replacements.',
        '+1 Zufriedenheit durch Paläste und Monumente, einschließlich einzigartiger Ersatzgebäude.'),
    'THEOCRATIC_LEGITIMACY': (
        '+10% combat strength. State-religion buildings give +1 happiness; buildings of other religions give -2 happiness.',
        '+10% Kampfstärke. Gebäude der Staatsreligion geben +1 Zufriedenheit, Gebäude anderer Religionen -2 Zufriedenheit.'),
    'PLUTOCRACY': (
        '+25% gold income and +50% trade-route commerce.',
        '+25% Goldeinnahmen und +50% Wirtschaftspunkte durch Handelsrouten.'),
    'NATIONALISM': (
        '+5 culture per city and +20% production. -5 happiness where another player\'s city-tile culture exceeds the owner\'s.',
        '+5 Kultur je Stadt und +20% Produktion. -5 Zufriedenheit, wenn die Kultur eines anderen Spielers auf dem Stadtfeld größer ist als die des Besitzers.'),
    'RULE_OF_LAW': (
        '+2 happiness in every city and +10% commerce.',
        '+2 Zufriedenheit in jeder Stadt und +10% Wirtschaftspunkte.'),
    'SELF_SUFFICIENCY': (
        '+2 health in every city. Cottage improvements stop growing; assigned specialists are blocked, but free specialists remain.',
        '+2 Gesundheit in jeder Stadt. Hüttenverbesserungen wachsen nicht; zugewiesene Spezialisten sind gesperrt, freie Spezialisten bleiben.'),
    'SLAVERY': (
        'Enables slave specialists. Enslave conquered peoples.',
        'Erm\u00f6glicht Sklavenspezialisten. Versklavt eroberte V\u00f6lker.'),
    'SERFDOM': (
        '+1 food from farms, -1 commerce from villages, workers build improvements 50% faster, and population can rush units.',
        '+1 Nahrung durch Bauernh\u00f6fe, -1 Wirtschaftspunkt durch D\u00f6rfer; Bautrupps errichten Verbesserungen 50% schneller und Bev\u00f6lkerung kann Einheiten beschleunigen.'),
    'PLANNED_ECONOMY': (
        '+1 production from workshops, watermills and windmills; +1 food from farms; -20% commerce. No trade routes with Capitalists.',
        '+1 Produktion durch Werkstätten, Wasser- und Windmühlen; +1 Nahrung durch Bauernhöfe; -20% Wirtschaftspunkte. Keine Handelswege mit Kapitalisten.'),
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
        '+25% mounted-unit production and +10% city attack.',
        '+25% Produktion für berittene Einheiten und +10% Stadtangriff.'),
    'PROFESSIONAL_ARMY': (
        'Units start with +5 experience.',
        'Einheiten starten mit +5 Erfahrung.'),
    'CONSCRIPTION': (
        '+25% unit production. Surplus food is converted into production for military units.',
        '+25% Einheitenproduktion. Nahrungs\u00fcbersch\u00fcsse werden bei Milit\u00e4reinheiten zu Produktion.'),
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
        'Removes unhappiness caused by foreign religions.',
        'Entfernt Unzufriedenheit durch fremde Religionen.'),
    'STATE_ATHEISM': (
        '+10% research. Religious buildings have no effects; religions cannot spread in your cities.',
        '+10% Forschung. Religiöse Gebäude haben keine Effekte; Religionen können sich in den eigenen Städten nicht verbreiten.'),
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
