"""Generate the election announcements, retaining all five Civ4 languages."""
from pathlib import Path
from military_civic_text import ENTRIES
from xml.sax.saxutils import escape

ANNOUNCEMENTS = {
    'DESPOTISM': (
        'The electorate has entrusted its freedom to one exceptionally trustworthy individual. Further elections may confirm this assessment.',
        'Die Wähler haben ihre Freiheit einem außergewöhnlich vertrauenswürdigen Einzelnen anvertraut. Weitere Wahlen werden dies womöglich bestätigen.'),
    'THEOCRATIC_LEGITIMACY': (
        'The election results have been certified by the highest authority. Requests for a recount should be submitted through prayer.',
        'Das Wahlergebnis wurde von höchster Stelle bestätigt. Anträge auf Neuauszählung sind als Gebet einzureichen.'),
    'PLUTOCRACY': (
        'Every citizen had a voice. Some citizens also had a printing press, three banks, and the candidates’ home addresses.',
        'Jeder Bürger hatte eine Stimme. Einige besaßen außerdem eine Druckerei, drei Banken und die Privatadressen der Kandidaten.'),
    'NATIONALISM': (
        'The nation has voted to put the nation first. Other nations are invited to admire the decision from a respectful distance.',
        'Die Nation hat entschieden, die Nation an erste Stelle zu setzen. Andere Nationen dürfen diese Entscheidung aus respektvollem Abstand bewundern.'),
    'RULE_OF_LAW': (
        'The people demand equal treatment before the law. A committee will now determine precisely how many forms this requires.',
        'Das Volk verlangt Gleichheit vor dem Gesetz. Ein Ausschuss wird nun ermitteln, wie viele Formulare dafür erforderlich sind.'),
    'SELF_SUFFICIENCY': (
        'The voters have rejected economic complexity. Everyone will grow their own dinner; the economists have been issued hoes.',
        'Die Wähler haben wirtschaftliche Komplexität abgelehnt. Jeder baut sein eigenes Abendessen an; die Ökonomen haben Hacken erhalten.'),
    'SLAVERY': (
        'The electorate has voted for cheaper labor. The people expected to provide it were conspicuously absent from the electoral register.',
        'Die Wähler haben sich für billigere Arbeitskräfte entschieden. Die dafür vorgesehenen Menschen fehlten auffällig im Wählerverzeichnis.'),
    'SERFDOM': (
        'The countryside has voted for stability. To prevent unnecessary movement, the winning party has attached the voters to the countryside.',
        'Das Land hat für Beständigkeit gestimmt. Um unnötige Bewegung zu verhindern, hat die Siegerpartei die Wähler an das Land gebunden.'),
    'PLANNED_ECONOMY': (
        'The people have approved the Five-Year Plan. Production targets are ambitious; the supply of celebratory posters is already exceeding expectations.',
        'Das Volk hat den Fünfjahresplan gebilligt. Die Produktionsziele sind ehrgeizig; bei Jubelplakaten wird der Plan bereits übererfüllt.'),
    'CORPORATE_ECONOMY': (
        'The electorate has chosen enterprise and competition. Several companies immediately offered to sponsor the announcement.',
        'Die Wähler haben Unternehmergeist und Wettbewerb gewählt. Mehrere Firmen haben sofort angeboten, die Bekanntmachung zu sponsern.'),
    'WARRIOR_SOCIETY': (
        'The voters demand a return to traditional values: courage, strength, and settling policy disagreements with a club.',
        'Die Wähler verlangen traditionelle Werte: Mut, Stärke und die Klärung politischer Meinungsverschiedenheiten mit einer Keule.'),
    'NAVAL_WARFARE': (ENTRIES['TXT_KEY_RFCMP_ELECTION_NAVAL_WARFARE']['English'],
        ENTRIES['TXT_KEY_RFCMP_ELECTION_NAVAL_WARFARE']['German']),
    'FEUDAL_RETINUES': (ENTRIES['TXT_KEY_RFCMP_ELECTION_FEUDAL_RETINUES']['English'],
        ENTRIES['TXT_KEY_RFCMP_ELECTION_FEUDAL_RETINUES']['German']),
    'PROFESSIONAL_ARMY': (
        'National defense will be entrusted to trained professionals. The public is relieved; the payroll department is less enthusiastic.',
        'Die Landesverteidigung wird ausgebildeten Profis anvertraut. Die Bevölkerung ist erleichtert; die Besoldungsstelle zeigt weniger Begeisterung.'),
    'CONSCRIPTION': (
        'The voters demand a larger army. Recruitment officials are delighted to explain that the voters themselves constitute the larger army.',
        'Die Wähler verlangen ein größeres Heer. Die Rekrutierungsbeamten erklären erfreut, dass die Wähler selbst dieses größere Heer bilden.'),
    'ANCESTOR_CULT': (
        'The electorate has sought guidance from its ancestors. Their silence has been interpreted as unanimous approval.',
        'Die Wähler haben ihre Ahnen um Rat gefragt. Deren Schweigen wurde als einstimmige Zustimmung gewertet.'),
    'STATE_RELIGION': (
        'The nation has elected an official faith. The government assures everyone that this will simplify matters considerably.',
        'Die Nation hat einen amtlichen Glauben gewählt. Die Regierung versichert, dass dies alles erheblich vereinfachen wird.'),
    'GOD_STATE': (
        'The voters have chosen a holy mission for the nation. The distinction between cabinet meetings and religious services is becoming ceremonial.',
        'Die Wähler haben eine heilige Mission für die Nation gewählt. Der Unterschied zwischen Kabinettssitzung und Gottesdienst wird zunehmend zeremoniell.'),
    'TOLERANCE': (
        'The electorate has agreed that everyone may worship as they please. Agreement on anything else remains entirely optional.',
        'Die Wähler sind sich einig, dass jeder glauben darf, was er möchte. Einigkeit in allen anderen Fragen bleibt freiwillig.'),
    'STATE_ATHEISM': (
        'The people have voted to separate religion from public life. The government intends to accomplish this with considerable enthusiasm.',
        'Das Volk will Religion vom öffentlichen Leben trennen. Die Regierung beabsichtigt, dies mit beträchtlichem Eifer umzusetzen.'),
}


def main():
    entries = [('TXT_KEY_RFCMP_ELECTION_TITLE', 'Election result', 'Wahlergebnis'),
               ('TXT_KEY_RFCMP_ELECTION_ADOPT', 'Adopt %s1_civic', '%s1_civic annehmen')]
    entries += [('TXT_KEY_RFCMP_ELECTION_' + civic, en, de)
                for civic, (en, de) in sorted(ANNOUNCEMENTS.items())]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<Civ4GameText xmlns="http://www.firaxis.com">']
    for key, en, de in entries:
        lines += ['  <TEXT>', '    <Tag>' + key + '</Tag>']
        for lang in ('English', 'French', 'German', 'Italian', 'Spanish'):
            value = ENTRIES.get(key, {}).get(lang, de if lang == 'German' else en)
            value = escape(value).encode('ascii', 'xmlcharrefreplace').decode('ascii')
            lines.append('    <' + lang + '>' + value + '</' + lang + '>')
        lines.append('  </TEXT>')
    lines.append('</Civ4GameText>')
    target = Path(__file__).resolve().parents[1] / 'Awakened RFC/Assets/XML/Text/CIV4GameText_Elections.xml'
    target.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
