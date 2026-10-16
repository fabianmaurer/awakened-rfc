"""Author a post-Constantinople 1453 world on RFC's existing Earth terrain.

This creates scenario assets only. It never starts Civilization IV.
"""
from pathlib import Path
from collections import deque
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'Awakened RFC'
TARGET = MOD / 'PublicMaps/Start 4 - 1453 AD.CivBeyondSwordWBSave'
START_TURN = 271
ACTIVE = tuple(i for i in range(26) if i != 3)
CHRISTIAN = 'RELIGION_CHRISTIANITY'
ISLAM = 'RELIGION_ISLAM'
BUDDHISM = 'RELIGION_BUDDHISM'
CONFUCIAN = 'RELIGION_CONFUCIANISM'
RELIGIONS = {0: ISLAM, 1: ISLAM, 2: CONFUCIAN, 4: CHRISTIAN,
             5: ISLAM, 6: ISLAM, 7: CHRISTIAN, 8: BUDDHISM,
             9: CHRISTIAN, 11: CHRISTIAN, 12: ISLAM, 13: BUDDHISM,
             14: CHRISTIAN, 15: CHRISTIAN, 16: CHRISTIAN, 17: CHRISTIAN,
             18: CHRISTIAN, 19: CHRISTIAN, 20: ISLAM, 21: CHRISTIAN,
             25: ISLAM}

# First city per major is the capital. Sizes are relative urban weights, not a
# census conversion. The crowded RFC map requires regional aggregations.
CITY_DATA = """
0|69,35|Al-Qahira|10
0|67,36|Al-Iskandariyya|6
0|73,38|Al-Quds|4
0|74,41|Dimashq|7
1|90,40|Delhi|8
28|94,40|Jaunpur|5
28|96,39|Gaur|5
1|88,42|Lahore|4
2|102,47|Beijing|10
2|107,43|Nanjing|10
2|100,44|Xi'an|6
2|104,45|Qufu|5
2|105,39|Guangzhou|8
2|107,41|Hangzhou|9
2|102,41|Guiyang|4
4|67,41|Mistra|3
5|85,47|Samarqand|7
5|83,43|Herat|6
5|83,45|Merv|4
5|85,41|Kandahar|4
6|58,39|Tunis|6
6|60,37|Tarabulus|3
7|60,47|Venezia|7
7|60,44|Roma|5
8|113,45|Kyoto|8
8|115,47|Edo|1
8|111,43|Hakata|4
9|72,29|Aksum|4
9|73,26|Dabra Libanos|3
10|23,37|Mani|3
10|22,35|Tayasal|3
11|61,57|Kobenhavn|4
11|61,62|Nidaros|3
11|65,62|Stockholm|4
12|75,33|Makkah|4
27|76,30|Sana'a|3
13|102,32|Chaktomuk|4
13|102,34|Angkor|3
14|52,43|Toledo|5
14|52,45|Leon|3
14|55,44|Barcelona|6
14|50,41|Sevilla|6
15|55,50|Paris|9
16|53,48|Bordeaux|4
15|57,46|Marseille|5
16|53,54|London|7
16|53,57|York|4
17|62,48|Wien|5
17|59,50|Frankfurt|5
17|62,52|Berlin|3
17|64,51|Praha|6
18|73,54|Moskva|5
18|75,55|Vladimir|3
19|57,53|Brugge|7
20|51,29|Niani|5
29|53,31|Timbuktu|5
29|56,31|Gao|4
20|54,29|Djenne|4
21|49,43|Lisboa|6
21|49,45|Porto|4
22|28,22|Qusqu|7
29|24,25|Chan Chan|6
29|25,23|Cajamarca|4
22|27,24|Huamanga|4
22|30,18|Hatun Qulla|4
29|26,29|Tumipampa|4
29|30,15|Tupiza|3
29|29,11|Copiapo|2
23|99,51|Qaraqorum|4
23|96,53|Qobdo|2
24|18,37|Tenochtitlan|10
24|20,35|Texcoco|4
24|21,33|Oaxaca|4
25|68,45|Konstantiniyye|7
25|72,43|Konya|5
25|70,43|Bursa|5
25|66,46|Edirne|4
25|65,44|Thessaloniki|4
27|52,41|Gharnata|5
27|52,60|Inbhir Nis|3
27|67,53|Krakow|5
27|72,57|Novgorod|5
27|78,40|Baghdad|5
27|82,38|Shiraz|5
27|81,45|Tabriz|6
27|75,44|Trapezous|4
28|98,36|Ava|5
28|100,32|Ayutthaya|6
28|106,33|Thang Long|5
28|109,46|Hanseong|6
28|88,36|Dabhol|4
28|91,33|Vijayanagara|8
28|87,40|Multan|4
29|61,16|Mbanza Kongo|4
29|74,14|Kilwa|5
29|68,15|Great Zimbabwe|4
27|49,56|Dublin|3
28|62,42|Napoli|6
28|60,40|Palermo|5
27|65,49|Buda|5
27|76,46|Tbilisi|3
28|52,37|Fes|6
28|54,38|Tlemcen|4
28|82,34|Masqat|3
28|96,43|Lhasa|3
28|93,29|Colombo|3
28|100,30|Melaka|5
28|106,25|Surabaya|4
"""

# Independent slots group unrelated polities. Their cities need local faiths,
# rather than a shared state religion inherited from the slot.
CITY_RELIGIONS = {
    'Dublin': CHRISTIAN, 'Napoli': CHRISTIAN, 'Palermo': CHRISTIAN,
    'Buda': CHRISTIAN, 'Tbilisi': CHRISTIAN,
    'Fes': ISLAM, 'Tlemcen': ISLAM, 'Masqat': ISLAM, 'Melaka': ISLAM,
    'Lhasa': BUDDHISM, 'Colombo': BUDDHISM,
    'Surabaya': 'RELIGION_HINDUISM',
    "Sana'a": ISLAM, 'Gharnata': ISLAM,
    'Baghdad': ISLAM, 'Shiraz': ISLAM, 'Tabriz': ISLAM,
    'Jaunpur': ISLAM, 'Gaur': ISLAM, 'Dabhol': ISLAM, 'Multan': ISLAM,
    'Timbuktu': ISLAM, 'Gao': ISLAM, 'Kilwa': ISLAM,
    'Inbhir Nis': CHRISTIAN, 'Krakow': CHRISTIAN,
    'Novgorod': CHRISTIAN, 'Trapezous': CHRISTIAN,
    'Thessaloniki': CHRISTIAN,
    'Ava': BUDDHISM, 'Ayutthaya': BUDDHISM, 'Thang Long': BUDDHISM,
    'Hanseong': CONFUCIAN,
    'Vijayanagara': 'RELIGION_HINDUISM',
}

# Local American, African and Mongolian traditions are not among Civ4's seven
# religions. Name these exceptions explicitly so missing assignments elsewhere
# cannot silently create more cities without an authored religion.
NO_GAME_RELIGION_CITIES = frozenset((
    'Mani', 'Tayasal', 'Qusqu', 'Chan Chan', 'Cajamarca', 'Huamanga',
    'Hatun Qulla', 'Tumipampa', 'Tupiza', 'Copiapo',
    'Qaraqorum', 'Qobdo', 'Tenochtitlan', 'Texcoco', 'Oaxaca',
    'Mbanza Kongo', 'Great Zimbabwe',
))

BASE_TECHS = ('MYSTICISM MEDITATION POLYTHEISM PRIESTHOOD MONOTHEISM '
              'MONARCHY LITERATURE CODE_OF_LAWS DRAMA FEUDALISM THEOLOGY '
              'MUSIC CIVIL_SERVICE GUILDS DIVINE_RIGHT FISHING THE_WHEEL '
              'AGRICULTURE POTTERY AESTHETICS SAILING WRITING MATHEMATICS '
              'ALPHABET CALENDAR CURRENCY PHILOSOPHY PAPER BANKING '
              'HUNTING MINING ARCHERY MASONRY ANIMAL_HUSBANDRY '
              'BRONZE_WORKING HORSEBACK_RIDING IRON_WORKING METAL_CASTING '
              'COMPASS CONSTRUCTION MACHINERY ENGINEERING').split()
AMERICAN_TECHS = ('MYSTICISM POLYTHEISM PRIESTHOOD MONARCHY CODE_OF_LAWS '
                  'AGRICULTURE POTTERY WRITING MATHEMATICS CALENDAR '
                  'CURRENCY HUNTING MINING ARCHERY MASONRY BRONZE_WORKING '
                  'CONSTRUCTION FEUDALISM').split()
GUNPOWDER = (0, 1, 2, 5, 8, 11, 14, 15, 16, 17, 18, 19, 21, 25)
OPTICS = (2, 7, 11, 14, 15, 16, 19, 21)
LEADERS = {
    0: ('Inal', 'Inal'), 1: ('Bahlul Lodi', 'Bahlul Lodi'),
    2: ('Jingtai', 'Jingtai'), 4: ('Demetrios Palaiologos', 'Demetrios Palaiologos'),
    5: ("Abu Sa'id Mirza", "Abu Sa'id Mirza"),
    6: ('Abu Amr Uthman', 'Abu Amr Uthman'),
    7: ('Francesco Foscari', 'Francesco Foscari'),
    8: ('Ashikaga Yoshimasa', 'Ashikaga Yoshimasa'),
    9: ('Zara Yaqob', 'Zara Yaqob'), 10: ('Ah Xupan Xiu', 'Ah Xupan Xiu'),
    11: ('Christian I', 'Christian I.'),
    12: ('Barakat ibn Hasan', 'Barakat ibn Hasan'),
    13: ('Ponhea Yat', 'Ponhea Yat'),
    14: ('John II of Castile', 'Johann II. von Kastilien'),
    15: ('Charles VII', 'Karl VII.'), 16: ('Henry VI', 'Heinrich VI.'),
    17: ('Frederick III', 'Friedrich III.'), 18: ('Vasily II', 'Wassili II.'),
    19: ('Philip the Good', 'Philipp der Gute'),
    20: ('Uli II', 'Uli II.'), 21: ('Afonso V', 'Alfons V.'),
    22: ('Pachacuti', 'Pachacuti'), 23: ('Esen Taishi', 'Esen Taishi'),
    24: ('Moctezuma I', 'Moctezuma I.'), 25: ('Mehmed II', 'Mehmed II.'),
}


# Briefings describe the authored position, including aggregated regional states.
# Keep them short enough for the existing Dawn of Man panel.
INTRODUCTIONS = {
    0: (
        '1453: From Cairo, the Mamluk sultanate holds Egypt and the Levant. The Nile sustains your cities, while Mediterranean and Red Sea connections bring wealth. The Ottomans have taken Constantinople. Secure your northern frontier and preserve the strength of your sultanate.',
        '1453: Von Kairo aus beherrscht das Mamlukensultanat Ägypten und die Levante. Der Nil ernährt eure Städte, Verbindungen zum Mittelmeer und Roten Meer bringen Wohlstand. Die Osmanen haben Konstantinopel erobert. Sichert die Nordgrenze und bewahrt die Stärke eures Sultanats.'),
    1: (
        '1453: Delhi and Lahore form the heart of your sultanate under Bahlul Lodi. Jaunpur, Bengal and the Deccan follow their own rulers; Vijayanagara stands strong in the south. Consolidate your northern possessions before seeking a wider dominion in India.',
        '1453: Delhi und Lahore bilden unter Bahlul Lodi den Kern eures Sultanats. Jaunpur, Bengalen und der Dekkan folgen eigenen Herrschern; im Süden steht Vijayanagara. Festigt eure nordindischen Besitzungen, bevor ihr nach einer größeren Herrschaft in Indien strebt.'),
    2: (
        '1453: The Ming court rules from Beijing over populous cities and rich farmland. Beyond the northern frontier, Mongol powers remain a threat. Confucian learning, Buddhist temples and Daoist traditions shape your realm. Protect the frontier and turn the strength of your cities into lasting security.',
        '1453: Der Ming-Hof regiert von Beijing aus über bevölkerungsreiche Städte und fruchtbares Land. Jenseits der Nordgrenze bleiben mongolische Mächte eine Gefahr. Konfuzianische Bildung, buddhistische Tempel und daoistische Traditionen prägen euer Reich. Sichert die Grenze und nutzt die Stärke eurer Städte.'),
    4: (
        '1453: Constantinople has fallen, but the Greek despotate in the Morea survives around Mistra. Your small realm faces an Ottoman power established on both sides of the straits. Preserve your independence through careful diplomacy, defensible borders and the resources of your remaining city.',
        '1453: Konstantinopel ist gefallen, doch das griechische Despotat in der Morea besteht um Mistra fort. Euer kleines Reich steht einer osmanischen Macht gegenüber, die beide Seiten der Meerengen beherrscht. Bewahrt eure Unabhängigkeit durch kluge Diplomatie, sichere Grenzen und die Kräfte eurer verbliebenen Stadt.'),
    5: (
        '1453: Timur\'s legacy is divided among competing princes. Your cities stretch from Samarqand through Merv and Herat to Kandahar, while other Iranian rulers hold Tabriz and Shiraz. Guard the routes between your scattered centers and build a durable realm from a contested inheritance.',
        '1453: Timurs Erbe ist unter rivalisierenden Fürsten geteilt. Eure Städte reichen von Samarqand über Merv und Herat bis Kandahar; andere iranische Herrscher halten Tabriz und Shiraz. Schützt die Wege zwischen euren verstreuten Zentren und formt aus dem umkämpften Erbe eine dauerhafte Herrschaft.'),
    6: (
        '1453: Tunis anchors your Hafsid realm on the North African coast, with Tripoli to the east. Fes and Tlemcen remain separate centers of power to the west. Strengthen your ports and inland defenses, and balance Mediterranean opportunities against the ambitions of neighboring states.',
        '1453: Tunis ist das Zentrum eures Hafsidenreichs an Nordafrikas Küste, Tripolis sein östlicher Stützpunkt. Fès und Tlemcen bleiben eigenständige Machtzentren im Westen. Stärkt Häfen und Landesverteidigung und wägt die Chancen des Mittelmeers gegen die Ansprüche eurer Nachbarn ab.'),
    7: (
        '1453: Your Italian cities unite the maritime reach of Venice with the prestige of Rome. Naples and Sicily remain outside your rule, and powerful neighbors watch the Alpine approaches. Develop your wealthy urban centers and secure a place in the struggle for influence across Italy and the Mediterranean.',
        '1453: Eure italienischen Städte verbinden Venedigs maritime Reichweite mit dem Ansehen Roms. Neapel und Sizilien stehen außerhalb eurer Herrschaft; mächtige Nachbarn wachen über die Alpenzugänge. Entwickelt eure reichen Städte und sichert euren Einfluss in Italien und im Mittelmeer.'),
    8: (
        '1453: The Ashikaga shogunate governs from Kyoto, but regional warrior houses limit its authority. Hakata connects your islands to overseas exchange, while Edo is still a small settlement. Strengthen your cities and defenses, and give a divided country a stable center of power.',
        '1453: Das Ashikaga-Shogunat regiert von Kyoto aus, doch regionale Kriegerhäuser begrenzen seine Macht. Hakata verbindet eure Inseln mit dem überseeischen Handel, während Edo noch eine kleine Siedlung ist. Stärkt Städte und Verteidigung und gebt dem geteilten Land ein beständiges Machtzentrum.'),
    9: (
        '1453: Your Christian highland kingdom draws strength from the royal traditions of Aksum and the religious center of Dabra Libanos. Muslim powers surround the approaches to the Red Sea and the northern trade routes. Develop the highlands, defend their passes and preserve your kingdom\'s independence.',
        '1453: Euer christliches Hochlandreich schöpft Kraft aus Aksums königlicher Tradition und dem religiösen Zentrum Dabra Libanos. Muslimische Mächte prägen die Zugänge zum Roten Meer und die nördlichen Handelswege. Entwickelt das Hochland, schützt seine Pässe und bewahrt eure Unabhängigkeit.'),
    10: (
        '1453: Maya lands are divided among regional dynasties. Mani and Tayasal sustain your realm, while the Aztec powers lie to the west. Build on local agriculture and exchange, defend your communities and seek a stronger position among the competing states of Mesoamerica.',
        '1453: Die Länder der Maya sind unter regionalen Dynastien geteilt. Mani und Tayasal tragen eure Herrschaft, westlich liegen die Mächte der Azteken. Stützt euch auf Landwirtschaft und Austausch, schützt eure Gemeinden und festigt eure Stellung unter den rivalisierenden Staaten Mesoamerikas.'),
    11: (
        '1453: Copenhagen, Nidaros and Stockholm represent the Scandinavian crowns under your command. The northern kingdoms share maritime ties, but their interests often diverge. Secure the sea lanes of the Baltic and North Atlantic, develop your ports and hold your scattered lands together.',
        '1453: Kopenhagen, Nidaros und Stockholm vertreten die skandinavischen Kronen unter eurer Führung. Seeverbindungen vereinen die nördlichen Königreiche, doch ihre Interessen gehen oft auseinander. Sichert die Wege über Ostsee und Nordatlantik, entwickelt eure Häfen und haltet die verstreuten Länder zusammen.'),
    12: (
        '1453: Mecca is the heart of your sharifate and a holy city of Islam. Mamluk Egypt lies to the northwest, while Yemen and the ports of Oman remain outside your rule. Safeguard the pilgrimage routes and build the resources and diplomacy needed to preserve your position in the Hejaz.',
        '1453: Mekka ist das Herz eures Scharifats und eine heilige Stadt des Islam. Im Nordwesten liegt das mamlukische Ägypten; Jemen und die Häfen Omans stehen außerhalb eurer Herrschaft. Schützt die Pilgerwege und sichert durch Wohlstand und Diplomatie eure Stellung im Hedschas.'),
    13: (
        '1453: Cambodia\'s court is centered on Chaktomuk, while Angkor preserves the legacy of a greater empire. Ayutthaya to the west and the Vietnamese realm to the east stand apart. Restore the strength of your cities and protect the river lands on which your kingdom depends.',
        '1453: Kambodschas Hof hat sein Zentrum in Chaktomuk, während Angkor das Erbe eines größeren Reiches bewahrt. Ayutthaya im Westen und das vietnamesische Reich im Osten stehen eigenständig daneben. Stärkt eure Städte und schützt die Flusslandschaften, von denen euer Königreich lebt.'),
    14: (
        '1453: Your Christian Iberian realms span the Castilian interior and Barcelona\'s Mediterranean coast. Portugal and Muslim Granada remain outside your rule. Develop the peninsula\'s cities, secure the southern frontier and choose between continental ambitions and opportunities at sea.',
        '1453: Eure christlichen Reiche Iberiens umfassen das kastilische Binnenland und Barcelonas Mittelmeerküste. Portugal und das muslimische Granada stehen außerhalb eurer Herrschaft. Entwickelt die Städte der Halbinsel, sichert die Südgrenze und wägt Ziele auf dem Festland gegen Chancen zur See ab.'),
    15: (
        '1453: France is still at war with England. Paris and Marseille anchor your kingdom, but Bordeaux remains in English hands. Reclaim your southwestern foothold, strengthen royal power and rebuild the prosperity of a realm shaped by a long struggle for its crown.',
        '1453: Frankreich liegt noch im Krieg mit England. Paris und Marseille tragen euer Königreich, doch Bordeaux ist weiterhin englisch. Gewinnt den Stützpunkt im Südwesten zurück, festigt die königliche Macht und erneuert den Wohlstand eines Landes, das lange um seine Krone gekämpft hat.'),
    16: (
        '1453: London and York sustain your English kingdom, while Bordeaux remains your foothold in a war-torn France. Scotland and Ireland lie beyond your direct rule. Decide how much strength to commit across the Channel while securing the island and the resources of the crown.',
        '1453: London und York tragen euer englisches Königreich; Bordeaux bleibt euer Stützpunkt im umkämpften Frankreich. Schottland und Irland stehen außerhalb eurer direkten Herrschaft. Entscheidet, wie viel Kraft ihr jenseits des Ärmelkanals einsetzen könnt, und sichert zugleich Insel und Krone.'),
    17: (
        '1453: Your imperial lands stretch from Frankfurt and Berlin to Prague and Vienna. The Holy Roman Empire is a mosaic of cities and princely interests, with Burgundy to the west and Hungary to the southeast. Connect your centers, strengthen their defenses and turn imperial prestige into practical power.',
        '1453: Eure Reichsgebiete reichen von Frankfurt und Berlin bis Prag und Wien. Das Heilige Römische Reich ist ein Geflecht städtischer und fürstlicher Interessen, mit Burgund im Westen und Ungarn im Südosten. Verbindet eure Zentren, stärkt ihre Verteidigung und verleiht dem kaiserlichen Ansehen Gewicht.'),
    18: (
        '1453: Moscow and Vladimir form the core of your principality. Novgorod remains independent to the northwest, and the wider Russian lands are divided among rival powers. Consolidate your cities, defend the approaches to Moscow and build the strength to extend your influence.',
        '1453: Moskau und Wladimir bilden den Kern eures Fürstentums. Im Nordwesten bleibt Nowgorod unabhängig, und die weiteren russischen Länder sind unter rivalisierenden Mächten geteilt. Festigt eure Städte, schützt die Zugänge zu Moskau und schafft die Grundlage für wachsenden Einfluss.'),
    19: (
        '1453: Bruges anchors your Burgundian Low Countries, a wealthy urban region between France, England and the Empire. Prosperity attracts powerful neighbors as well as distant commerce. Protect your compact territory and use its wealth and diplomacy to preserve room for your own ambitions.',
        '1453: Brügge ist das Zentrum eurer burgundischen Niederlande, einer reichen Städtelandschaft zwischen Frankreich, England und dem Reich. Wohlstand zieht mächtige Nachbarn ebenso an wie fernen Handel. Schützt euer kleines Gebiet und nutzt seine Mittel für eine eigenständige Politik.'),
    20: (
        '1453: Niani and Djenne sustain your Malian realm, but Timbuktu and Gao lie outside your authority. Gold and trans-Saharan exchange offer wealth amid competing powers along the Niger. Consolidate the lands you hold and rebuild your influence over the region\'s important routes and cities.',
        '1453: Niani und Djenne tragen euer Malireich, doch Timbuktu und Gao stehen außerhalb eurer Herrschaft. Gold und der Austausch durch die Sahara versprechen Wohlstand zwischen rivalisierenden Mächten am Niger. Festigt eure Länder und erneuert euren Einfluss auf die Wege und Städte der Region.'),
    21: (
        '1453: Lisbon and Porto face the Atlantic from Portugal\'s narrow western shore. Your Iberian neighbors are strong, while the coasts of Africa offer routes for exploration and exchange. Develop your fleet and ports, safeguard the homeland and choose how far to pursue opportunities overseas.',
        '1453: Lissabon und Porto blicken von Portugals schmaler Westküste auf den Atlantik. Eure iberischen Nachbarn sind stark, während Afrikas Küsten Wege für Erkundung und Austausch eröffnen. Entwickelt Flotte und Häfen, schützt das Kernland und bestimmt die Reichweite eurer überseeischen Ziele.'),
    22: (
        '1453: Pachacuti\'s realm is growing from Cusco into the Andean highlands. Chan Chan, Cajamarca and other regional centers are still independent. Strengthen the connections between your mountain cities and decide where diplomacy or conquest can extend the land of the four quarters.',
        '1453: Pachacutis Reich wächst von Cusco aus in das Andenhochland. Chan Chan, Cajamarca und weitere regionale Zentren bleiben unabhängig. Stärkt die Verbindungen zwischen euren Bergstädten und entscheidet, wo Diplomatie oder Eroberung das Land der vier Weltgegenden erweitern können.'),
    23: (
        '1453: The Northern Yuan preserve a Mongol power beyond the Ming frontier. Qaraqorum and Qobdo anchor your scattered settlements, while China commands much larger cities to the south. Use the space of the steppe, protect your centers and seek opportunities without exhausting your limited urban base.',
        '1453: Die Nördlichen Yuan bewahren eine mongolische Macht jenseits der Ming-Grenze. Qaraqorum und Qobdo tragen eure verstreuten Siedlungen, während China im Süden weit größere Städte besitzt. Nutzt den Raum der Steppe, schützt eure Zentren und schont die Kräfte eurer kleinen städtischen Basis.'),
    24: (
        '1453: Tenochtitlan is the heart of the Aztec Triple Alliance under Moctezuma I. Texcoco and Oaxaca extend your reach, while Maya states endure to the east. Sustain your populous capital, strengthen your armies and bring neighboring lands within your sphere of influence.',
        '1453: Tenochtitlan ist unter Moctezuma I. das Herz des aztekischen Dreibunds. Texcoco und Oaxaca erweitern euren Einfluss, während im Osten die Staaten der Maya bestehen. Versorgt eure bevölkerungsreiche Hauptstadt, stärkt eure Heere und gewinnt Einfluss auf die umliegenden Länder.'),
    25: (
        '1453: Constantinople is yours. Your Ottoman lands now link the Balkans with western and central Anatolia, but Morea, Trebizond and the Mamluk realm remain separate. Secure the straits, rebuild your new capital and decide where the sultanate\'s next frontier should lie.',
        '1453: Konstantinopel gehört euch. Eure osmanischen Länder verbinden nun den Balkan mit West- und Zentralanatolien, doch Morea, Trapezunt und das Mamlukenreich bestehen fort. Sichert die Meerengen, baut eure neue Hauptstadt aus und entscheidet, wo die nächste Grenze des Sultanats liegen soll.'),
}


def records():
    cities = []
    for line in CITY_DATA.strip().splitlines():
        owner, xy, name, size = line.split('|')
        cities.append((int(owner), tuple(map(int, xy.split(','))), name, int(size)))
    return cities


def techs(owner):
    result = list(AMERICAN_TECHS if owner in (10, 22, 24) else BASE_TECHS)
    if owner in GUNPOWDER:
        result.append('GUNPOWDER')
    if owner in OPTICS:
        result.append('OPTICS')
    return result


def text_entries():
    from xml.sax.saxutils import escape
    en = ('1453 AD: After the fall of Constantinople. Every established major '
          'civilization is playable. Regional states are represented by RFC civilization slots; '
          'America appears on its usual schedule.')
    de = ('1453 n. Chr.: Nach dem Fall Konstantinopels. Alle bestehenden großen '
          'Zivilisationen sind spielbar. Regionale Staaten werden durch die RFC-Zivilisationen '
          'abgebildet; Amerika erscheint nach dem gewohnten Zeitplan.')
    entries = [('TXT_KEY_RFCMP_SCENARIO_1453_AD', en, de)]
    title_translations = {
        'English': 'The World in 1453', 'French': 'Le monde en 1453',
        'German': 'Die Welt im Jahr 1453', 'Italian': 'Il mondo nel 1453',
        'Spanish': 'El mundo en 1453',
    }
    entries.append(('TXT_KEY_RFCMP_1453_INTRO_TITLE', title_translations['English'], title_translations['German']))
    entries += [('TXT_KEY_RFCMP_1453_LEADER_' + str(i), *LEADERS[i]) for i in sorted(LEADERS)]
    if set(INTRODUCTIONS) != set(ACTIVE):
        raise ValueError('Every starting civilization needs its own introduction')
    entries += [('TXT_KEY_RFCMP_1453_INTRO_' + str(i), *INTRODUCTIONS[i]) for i in ACTIVE]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<Civ4GameText xmlns="http://www.firaxis.com">']
    for tag, english, german in entries:
        lines += ['  <TEXT>', '    <Tag>' + tag + '</Tag>']
        for language in ('English', 'French', 'German', 'Italian', 'Spanish'):
            value = german if language == 'German' else english
            if tag == 'TXT_KEY_RFCMP_1453_INTRO_TITLE':
                value = title_translations[language]
            lines.append('    <' + language + '>' + escape(value) + '</' + language + '>')
        lines.append('  </TEXT>')
    lines.append('</Civ4GameText>')
    (MOD / 'Assets/XML/Text/CIV4GameText_Scenario1453.xml').write_bytes(
        ('\n'.join(lines) + '\n').encode('ascii', 'xmlcharrefreplace'))


def set_field(block, key, value):
    line = '\t\t' + key + '=' + str(value)
    pattern = r'^\s*' + re.escape(key) + r'=[^\n]*'
    if re.search(pattern, block, re.M):
        return re.sub(pattern, lambda _: line, block, count=1, flags=re.M)
    return block.rstrip() + '\n' + line + '\n'


def unit(owner, kind, ai=None):
    result = '\tBeginUnit\n\t\tUnitType=' + kind + ', UnitOwner=' + str(owner) + '\n'
    if ai:
        result += '\t\tUnitAIType=' + ai + '\n'
    return result + '\tEndUnit\n'


def main():
    text = (ROOT / 'tools/scenario_templates/1453_ad_base.CivBeyondSwordWBSave').read_text(encoding='utf-8')
    cities = records()
    for owner, _, name, _ in cities:
        if name not in CITY_RELIGIONS and owner not in RELIGIONS and name not in NO_GAME_RELIGION_CITIES:
            raise ValueError('Missing city religion assignment: ' + name)
    if {owner for owner, _, _, _ in cities if owner < 27} != set(ACTIVE):
        raise ValueError('Every populated major must be selectable, and every selectable major needs a city')
    for index, (_, (x, y), name, _) in enumerate(cities):
        for _, (xx, yy), other, _ in cities[index + 1:]:
            if max(min(abs(x - xx), 124 - abs(x - xx)), abs(y - yy)) < 2:
                raise ValueError('City sites are adjacent: %s / %s' % (name, other))
    capitals = {}
    for owner, pos, _, _ in cities:
        capitals.setdefault(owner, pos)
    capitals[16] = (53, 54)  # London, despite Bordeaux appearing earlier in the data.

    def initial_culture_reaches(pos):
        x, y = pos
        for owner, (cx, cy), _, _ in cities:
            dx = min(abs(x - cx), 124 - abs(x - cx))
            dy = abs(y - cy)
            # CvCity::cultureDistance uses Civ4's plotDistance. The authored
            # 500/200 city culture gives capitals radius 4, other cities 3.
            radius = 4 if capitals[owner] == (cx, cy) else 3
            if max(dx, dy) + min(dx, dy) // 2 <= radius:
                return True
        return False

    player_index = -1

    def player(match):
        nonlocal player_index
        player_index += 1
        owner = player_index
        block = match.group(1)
        block = re.sub(r'^\s*(?:StateReligion|CivDesc|CivShortDesc|CivicOption|StartingGold|LeaderName)=[^\n]*', '', block, flags=re.M)
        block = set_field(block, 'PlayableCiv', int(owner in ACTIVE))
        if owner in ACTIVE:
            block = set_field(block, 'MinorNationStatus', 0)
            block = set_field(block, 'StartingGold', 500 if owner not in (2, 25) else 800)
            block = set_field(block, 'LeaderName', 'TXT_KEY_RFCMP_1453_LEADER_' + str(owner))
        if owner == 26:
            block = set_field(block, 'StartingGold', 1500)
        if owner in RELIGIONS:
            block = set_field(block, 'StateReligion', RELIGIONS[owner])
        if owner in capitals:
            block = set_field(block, 'StartingX', capitals[owner][0])
            block = set_field(block, 'StartingY', capitals[owner][1])
        return 'BeginPlayer' + block + 'EndPlayer'

    text = re.sub(r'BeginPlayer\b(.*?)EndPlayer', player, text, flags=re.S)
    team_index = -1

    def team(match):
        nonlocal team_index
        team_index += 1
        owner = team_index
        lines = ['BeginTeam']
        if owner in capitals:
            lines += ['\tTech=TECH_' + t for t in techs(owner)]
            # Continental diplomacy predates this start; no transatlantic contact.
            for other in capitals:
                if other != owner and ((owner not in (10, 22, 24) and other not in (10, 22, 24))
                                       or (owner in (10, 24) and other in (10, 24))):
                    lines.append('\tContactWithTeam=' + str(other))
        if owner in (15, 16):
            lines.append('\tAtWar=' + str(31 - owner))
        lines.append('EndTeam')
        return '\n'.join(lines)

    text = re.sub(r'BeginTeam\b(.*?)EndTeam', team, text, flags=re.S)
    plots = {}
    for match in re.finditer(r'BeginPlot\b(.*?)EndPlot', text, re.S):
        block = match.group(1)
        pos = tuple(map(int, re.search(r'x=(\d+),y=(\d+)', block).groups()))
        block = re.sub(r'\s*BeginCity\b.*?EndCity', '', block, flags=re.S)
        block = re.sub(r'\s*BeginUnit\b.*?EndUnit', '', block, flags=re.S)
        block = re.sub(r'^\s*(?:Player\d+Culture|TeamReveal)=[^\n]*', '', block, flags=re.M)
        # Culture is applied while WorldBuilder is still creating cities.
        # Claiming an inherited hut calls doGoody with no unit during this
        # incomplete setup (notably at 59,55 when Brugge expands). Keep huts
        # only outside the initial borders, for discovery during normal play.
        if initial_culture_reaches(pos):
            block = re.sub(r'^\s*ImprovementType=IMPROVEMENT_GOODY_HUT[^\n]*', '', block, flags=re.M)
        plots[pos] = block.rstrip() + '\n'

    used = set()
    for owner, pos, name, size in cities:
        block = plots[pos]
        if pos in used or 'PlotType=0' in block or 'PlotType=3' in block:
            raise ValueError('Invalid city site: %s %s' % (name, pos))
        used.add(pos)
        block = re.sub(r'^\s*(?:FeatureType|ImprovementType|RouteType)=[^\n]*', '', block, flags=re.M)
        block += '\tRouteType=ROUTE_ROAD\n\tBeginCity\n'
        block += '\t\tCityOwner=%d\n\t\tCityName=%s\n\t\tCityPopulation=%d\n' % (owner, name, size)
        buildings = ['GRANARY', 'BARRACKS', 'WALLS']
        if size >= 4:
            buildings += ['LIBRARY', 'MARKET']
        if size >= 6:
            buildings += ['AQUEDUCT', 'FORGE']
        if capitals[owner] == pos:
            buildings += ['PALACE']
        if name == 'Al-Qahira':
            buildings.append('PYRAMID')
        if name == 'Konstantiniyye':
            buildings.append('HAGIA_SOPHIA')
        if name == 'Beijing':
            buildings.append('GREAT_WALL')
        block += ''.join('\t\tBuildingType=BUILDING_' + b + '\n' for b in buildings)
        religion = CITY_RELIGIONS.get(name, RELIGIONS.get(owner))
        if religion:
            block += '\t\tReligionType=' + religion + '\n'
        holy = {'Makkah': [ISLAM], 'Al-Quds': [CHRISTIAN, 'RELIGION_JUDAISM'],
                'Jaunpur': ['RELIGION_HINDUISM', BUDDHISM],
                'Qufu': [CONFUCIAN], "Xi'an": ['RELIGION_TAOISM']}.get(name, [])
        for faith in holy:
            if faith != religion:
                block += '\t\tReligionType=' + faith + '\n'
            block += '\t\tHolyCityReligionType=' + faith + '\n'
        block += '\t\tPlayer%dCulture=%d\n\tEndCity\n' % (owner, 500 if capitals[owner] == pos else 200)
        garrison = 'UNIT_ARCHER' if owner in (10, 22, 24) else 'UNIT_LONGBOWMAN'
        block += unit(owner, garrison, 'UNITAI_CITY_DEFENSE') * 2
        if capitals[owner] == pos:
            block += unit(owner, 'UNIT_WORKER', 'UNITAI_WORKER') * (3 if owner in ACTIVE else 1)
            if owner in ACTIVE:
                army = 'UNIT_SPEARMAN' if owner in (10, 22, 24) else 'UNIT_KNIGHT'
                if owner == 8:
                    army = 'UNIT_JAPAN_SAMURAI'
                block += unit(owner, army) * 2
        if owner == 25 and capitals[owner] == pos:
            # Bombards are represented by trebuchets; Steel-era cannon are not
            # unlocked merely to depict the siege artillery of 1453.
            block += unit(owner, 'UNIT_OTTOMAN_JANISSARY') * 3
            block += unit(owner, 'UNIT_TREBUCHET') * 2
        plots[pos] = block

    # Develop each city's working radius and give contiguous local culture.
    for owner, (x, y), _, size in cities:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                pos = ((x + dx) % 124, y + dy)
                if pos not in plots or abs(dx) + abs(dy) > 3:
                    continue
                block = plots[pos]
                block += '\tPlayer%dCulture=%d\n' % (owner, 40 if max(abs(dx), abs(dy)) <= 1 else 10)
                if pos not in used and not any(t in block for t in ('PlotType=0', 'PlotType=3', 'ImprovementType=')):
                    improvement = None
                    if re.search(r'BonusType=BONUS_(WHEAT|RICE|CORN)\b', block):
                        improvement = 'FARM'
                    elif re.search(r'BonusType=BONUS_(COW|PIG|SHEEP|HORSE)\b', block):
                        improvement = 'PASTURE'
                    elif re.search(r'BonusType=BONUS_(IRON|COPPER|GOLD|SILVER|GEMS)\b', block):
                        improvement = 'MINE'
                    elif 'BonusType=' not in block and 'PlotType=1' in block:
                        improvement = 'MINE'
                    elif 'BonusType=' not in block and re.search(r'TerrainType=TERRAIN_(GRASS|PLAINS)\b', block):
                        improvement = 'FARM' if 'River' in block else 'HAMLET'
                    if improvement:
                        block = re.sub(r'^\s*FeatureType=FEATURE_(FOREST|JUNGLE)[^\n]*', '', block, flags=re.M)
                        block += '\tImprovementType=IMPROVEMENT_' + improvement + '\n'
                        if 'RouteType=' not in block:
                            block += '\tRouteType=ROUTE_ROAD\n'
                plots[pos] = block

    # Connect each major's cities over land where a route exists.
    for owner in ACTIVE:
        start = capitals[owner]
        for _, goal, _, _ in [c for c in cities if c[0] == owner]:
            pending, previous = deque([start]), {start: None}
            while pending and goal not in previous:
                x, y = pending.popleft()
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    pos = ((x + dx) % 124, y + dy)
                    if pos in previous or pos not in plots or any(t in plots[pos] for t in ('PlotType=0', 'PlotType=3')):
                        continue
                    previous[pos] = (x, y)
                    pending.append(pos)
            if goal in previous:
                pos = goal
                while pos is not None:
                    if 'RouteType=' not in plots[pos]:
                        plots[pos] += '\tRouteType=ROUTE_ROAD\n'
                    pos = previous[pos]

    # Coastal economies start with a small fleet on adjacent sea tiles.
    for owner in (2, 6, 7, 8, 11, 14, 15, 16, 19, 21, 25):
        for _, (x, y), _, _ in [c for c in cities if c[0] == owner]:
            sea = [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                   if 'PlotType=3' in plots.get((x + dx, y + dy), '')
                   and 'FEATURE_ICE' not in plots.get((x + dx, y + dy), '')]
            if sea:
                ship = 'UNIT_CARAVEL' if owner in OPTICS else 'UNIT_GALLEY'
                plots[min(sea)] += unit(owner, ship) + unit(owner, 'UNIT_WORKBOAT')
                break

    for (x, y), block in plots.items():
        revealed = []
        for owner in ACTIVE:
            local = any(max(min(abs(x - cx), 124 - abs(x - cx)), abs(y - cy)) <= 8
                        for o, (cx, cy), _, _ in cities if o == owner)
            old_world = owner not in (10, 22, 24) and 42 <= x <= 118 and 20 <= y <= 65
            if local or old_world:
                revealed.append(str(owner))
        if revealed:
            plots[x, y] += '\tTeamReveal=' + ','.join(revealed) + ',\n'

    def plot(match):
        pos = tuple(map(int, re.search(r'x=(\d+),y=(\d+)', match.group(1)).groups()))
        return 'BeginPlot' + plots[pos] + 'EndPlot'

    text = re.sub(r'BeginPlot\b(.*?)EndPlot', plot, text, flags=re.S)
    # Check generated references against the installed mod's own XML catalogue.
    known = set()
    for path in (MOD / 'Assets/XML').rglob('*.xml'):
        for e in ET.parse(path).getroot().iter():
            if e.tag.rsplit('}', 1)[-1] == 'Type' and e.text:
                known.add(e.text)
    for prefix in ('UnitType', 'BuildingType', 'Tech', 'ReligionType', 'HolyCityReligionType'):
        for value in re.findall(prefix + r'=(\w+)', text):
            if value not in known:
                raise ValueError('Unknown %s: %s' % (prefix, value))
    # Inspect the emitted flags as well as the source roster: non-playable
    # majors (Babylon and the future American spawn) must stay out of setup.
    playable = set()
    for owner, block in enumerate(re.findall(r'BeginPlayer\b(.*?)EndPlayer', text, re.S)):
        flags = re.findall(r'^\s*PlayableCiv=(\d+)\s*$', block, re.M)
        if len(flags) != 1 or flags[0] not in ('0', '1'):
            raise ValueError('Invalid playable flag for player %d' % owner)
        if flags[0] == '1':
            playable.add(owner)
    if playable != set(ACTIVE):
        raise ValueError('Generated selectable players do not match the 1453 starting roster')
    TARGET.write_text(text, encoding='utf-8')
    data = ('# Generated by tools/generate_1453_ad_scenario.py; Python 2.4.\n'
            'START_TURN = %r\nSTART_YEAR = 1453\nACTIVE_PLAYERS = %r\nCAPITALS = %r\n' %
            (START_TURN, ACTIVE, {i: capitals[i] for i in ACTIVE}))
    (MOD / 'Assets/Python/Scenario1453Data.py').write_text(data, encoding='ascii')
    text_entries()
    print('Created %s: %d cities, %d playable major civilizations.' % (TARGET.name, len(cities), len(ACTIVE)))


if __name__ == '__main__':
    main()
