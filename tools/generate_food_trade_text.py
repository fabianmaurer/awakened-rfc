"""Generate complete Civ4 localization for food transfers (EN/DE translations)."""
from pathlib import Path
import xml.etree.ElementTree as ET

ENTRIES = [
    ('TXT_KEY_RFCMP_FOOD_TRADE_TOTAL',
     'Food trade: +%d1_Imports[ICON_FOOD] imported, -%d2_Exports[ICON_FOOD] exported per turn',
     'Nahrungshandel: +%d1_Imports[ICON_FOOD] importiert, -%d2_Exports[ICON_FOOD] exportiert pro Runde'),
    ('TXT_KEY_RFCMP_FOOD_TRADE_ROUTE',
     'Food exchange with this city: %D1_Food[ICON_FOOD] per turn',
     'Nahrungsaustausch mit dieser Stadt: %D1_Food[ICON_FOOD] pro Runde'),
    ('TXT_KEY_RFCMP_TECH_GROWTH',
     'Growth penalty: %s1_Penalty%%; growth per turn: %s2_Growth[ICON_FOOD]',
     'Wachstumsmalus: %s1_Penalty%%; Wachstum pro Runde: %s2_Growth[ICON_FOOD]'),
]

root = ET.Element('Civ4GameText', {'xmlns': 'http://www.firaxis.com'})
for key, english, german in ENTRIES:
    entry = ET.SubElement(root, 'TEXT')
    ET.SubElement(entry, 'Tag').text = key
    for language in ('English', 'French', 'German', 'Italian', 'Spanish'):
        ET.SubElement(entry, language).text = german if language == 'German' else english
ET.indent(root, space='    ')
output = Path(__file__).resolve().parents[1] / 'Awakened RFC/Assets/XML/Text/CIV4GameText_FoodTrade.xml'
output.write_bytes(b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding='ascii', xml_declaration=False) + b'\n')
