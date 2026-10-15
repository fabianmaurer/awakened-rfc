"""Civ4 text for marsh drainage, with all five required language entries."""
from pathlib import Path
import xml.etree.ElementTree as ET

entries = [
    ('TXT_KEY_RFCMP_BUILD_DRAIN_MARSH', 'Drain marsh', 'Sumpf trockenlegen'),
    ('TXT_KEY_RFCMP_BUILD_DRAIN_MARSH_HELP',
     'Converts marsh to grassland and removes swamp features. No production is gained. Requires Engineering.',
     'Wandelt Sumpf in Grasland um und entfernt die Sumpfdarstellung. Kein Produktionsgewinn. Erfordert Maschinenbau.'),
]
root = ET.Element('Civ4GameText', {'xmlns': 'http://www.firaxis.com'})
for key, english, german in entries:
    text = ET.SubElement(root, 'TEXT')
    ET.SubElement(text, 'Tag').text = key
    for lang in ('English', 'French', 'German', 'Italian', 'Spanish'):
        ET.SubElement(text, lang).text = german if lang == 'German' else english
ET.indent(root, space='    ')
target = Path(__file__).resolve().parents[1] / 'Awakened RFC/Assets/XML/Text/CIV4GameText_LandReclamation.xml'
target.write_bytes(b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding='ascii', xml_declaration=False) + b'\n')
