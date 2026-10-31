"""Generate country identities with complete Civ4 language coverage.

Edit country_name_catalog.py for authored English/German names. Several civic
families intentionally share the same name. This is a Python 3 development tool.
"""

from pathlib import Path
import csv
import io
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
from country_name_catalog import COUNTRY_NAMES, ALIASES, SPECIAL_NAMES

ROOT = Path(__file__).resolve().parents[1]
# Short geographic names for alternate-history Islamic names where no bespoke
# identity exists. German articles are included where grammatically required.
COUNTRIES = [
    ('EGY', 'Egypt', 'Ägypten'),
    ('IND', 'India', 'Indien'),
    ('CHI', 'China', 'China'),
    ('BAB', 'Babylon', 'Babylon'),
    ('GRE', 'Greece', 'Griechenland'),
    ('PER', 'Persia', 'Persien'),
    ('CAR', 'Carthage', 'Karthago'),
    ('ROM', 'Rome', 'Rom'),
    ('JAP', 'Japan', 'Japan'),
    ('ETH', 'Ethiopia', 'Äthiopien'),
    ('MAY', 'the Maya', 'der Maya'),
    ('VIK', 'Scandinavia', 'Skandinavien'),
    ('ARA', 'Arabia', 'Arabien'),
    ('KHM', 'Cambodia', 'Kambodscha'),
    ('SPA', 'Spain', 'Spanien'),
    ('FRA', 'France', 'Frankreich'),
    ('ENG', 'Britain', 'Großbritannien'),
    ('GER', 'Germany', 'Deutschland'),
    ('RUS', 'Russia', 'Russland'),
    ('NED', 'the Netherlands', 'der Niederlande'),
    ('MAL', 'Mali', 'Mali'),
    ('POR', 'Portugal', 'Portugal'),
    ('INC', 'the Inca', 'der Inka'),
    ('MON', 'Mongolia', 'Mongolei'),
    ('AZT', 'Mexico', 'Mexiko'),
    ('TUR', 'Turkey', 'Türkei'),
    ('AME', 'America', 'Amerika'),
    ('XIO', 'the Huns', 'der Hunnen'),
]
FORMS = (
    'TRIBAL', 'KINGDOM', 'EMPIRE', 'CONSTITUTIONAL', 'REPUBLIC',
    'DEMOCRACY', 'MERCHANT_REPUBLIC', 'SOCIALIST_REPUBLIC',
    'SOCIALIST_DEMOCRACY', 'PEOPLES_STATE', 'DICTATORSHIP', 'MILITARY',
    'NATIONAL_STATE', 'NATIONAL_REPUBLIC', 'THEOCRACY', 'HOLY_KINGDOM',
    'THEOCRATIC_REPUBLIC', 'ISLAMIC_REPUBLIC', 'CALIPHATE', 'SULTANATE',
    'SECULAR_REPUBLIC',
)
ISLAMIC_NAMES = {
    'ISLAMIC_REPUBLIC': ('Islamic Republic of {country}', 'Islamische Republik {country}'),
    'CALIPHATE': ('Caliphate of {country}', 'Kalifat {country}'),
    'SULTANATE': ('Sultanate of {country}', 'Sultanat {country}'),
}


def country_name(code, form, english_country, german_country):
    if (code, form) in SPECIAL_NAMES:
        return SPECIAL_NAMES[code, form]
    if form in ISLAMIC_NAMES:
        english, german = ISLAMIC_NAMES[form]
        return english.format(country=english_country), german.format(country=german_country)
    return COUNTRY_NAMES[code][ALIASES.get(form, form)]


def eskimo_country_rows():
    # These bespoke technology/government names live in their own runtime XML.
    # Read that source so the review CSV cannot drift from the displayed names.
    path = ROOT / 'Awakened RFC/Assets/XML/Text/CIV4GameText_Eskimos.xml'
    entries = {}
    for entry in ET.parse(path).getroot():
        fields = {child.tag.split('}')[-1]: child.text for child in entry}
        entries[fields['Tag']] = fields
    rows = []
    for root in ('ESK', 'HYPERBOREA', 'AGARTHA'):
        for form in ('TRIBES', 'KINGDOM', 'REPUBLIC', 'STATE', 'SUN_THRONE',
                     'IRON_WATCH', 'FROST_CROWN', 'WINTER_COMMUNE',
                     'STAR_COUNCIL', 'SEA_LEAGUE', 'HEARTH_COUNCIL'):
            fields = entries['TXT_KEY_' + root + '_' + form]
            rule = form if root == 'ESK' else root + '_' + form
            rows.append(('ESK', rule,
                         fields['English'], fields['German']))
    return rows


def main():
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<Civ4GameText xmlns="http://www.firaxis.com">']
    rows = []
    for code, english_country, german_country in COUNTRIES:
        for form in FORMS:
            english, german = country_name(code, form, english_country, german_country)
            tag = 'TXT_KEY_DN_' + code + '_' + form
            xml.extend(['  <TEXT>', '    <Tag>' + tag + '</Tag>'])
            for language in ('English', 'French', 'German', 'Italian', 'Spanish'):
                value = german if language == 'German' else english
                xml.append('    <' + language + '>' + escape(value) + '</' + language + '>')
            xml.append('  </TEXT>')
            rows.append((code, form, english, german))
    # Additional titles selected by bespoke civic, religion or period branches.
    for (code, form), (english, german) in SPECIAL_NAMES.items():
        if form in FORMS:
            continue
        tag = 'TXT_KEY_DN_' + code + '_' + form
        xml.extend(['  <TEXT>', '    <Tag>' + tag + '</Tag>'])
        for language in ('English', 'French', 'German', 'Italian', 'Spanish'):
            value = german if language == 'German' else english
            xml.append('    <' + language + '>' + escape(value) + '</' + language + '>')
        xml.append('  </TEXT>')
        rows.append((code, form, english, german))
    xml.append('</Civ4GameText>')
    path = ROOT / 'Awakened RFC/Assets/XML/Text/CIV4GameText_RFCMP_CountryNames.xml'
    path.write_bytes(('\n'.join(xml) + '\n').encode('ascii', 'xmlcharrefreplace'))
    rows.extend(eskimo_country_rows())
    document = io.StringIO(newline='')
    writer = csv.writer(document)
    writer.writerow(('Civilization', 'Naming rule', 'English', 'German'))
    writer.writerows(rows)
    (ROOT / 'docs').mkdir(exist_ok=True)
    (ROOT / 'docs/CountryNames.csv').write_text(document.getvalue(), encoding='utf-8-sig', newline='')
    distinct = len(set((english, german) for _, _, english, german in rows))
    print('Wrote %d naming entries with %d distinct English/German name pairs.' % (len(rows), distinct))


if __name__ == '__main__':
    main()
