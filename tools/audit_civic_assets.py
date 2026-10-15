"""Read-only audit of civic XML, localization completeness and DLL civic keys."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'Awakened RFC/Assets'
LANGUAGES = {'English', 'French', 'German', 'Italian', 'Spanish'}

def local(tag):
    return tag.rsplit('}', 1)[-1]

def fields(element):
    return {local(child.tag): child for child in element}

def audit():
    errors = []
    keys = set()
    count = 0
    text_files = list((ASSETS / 'XML/Text').rglob('*.xml'))
    for path in text_files:
        for text in ET.parse(path).getroot().iter():
            if local(text.tag) != 'TEXT':
                continue
            count += 1
            values = fields(text)
            key = values['Tag'].text
            keys.add(key)
            missing = LANGUAGES - values.keys()
            if missing:
                errors.append(f'{path.name}: {key}: missing {sorted(missing)}')

    civic_root = ET.parse(ASSETS / 'XML/GameInfo/CIV4CivicInfos.xml').getroot()
    civics = [fields(x) for x in civic_root.iter() if local(x.tag) == 'CivicInfo']
    names = {c['Type'].text for c in civics}
    assert len(civics) == 25
    for civic in civics:
        for field in ('Description', 'Help'):
            key = civic.get(field)
            if key is not None and key.text and key.text not in keys:
                errors.append(f'{civic["Type"].text}: missing {field} key {key.text}')

    for file in ('CvCity.cpp', 'CvPlayer.cpp', 'CvUnit.cpp', 'CvGameTextMgr.cpp'):
        code = (ROOT / 'Awakened RFC/CvGameCoreDLL' / file).read_bytes().decode('latin1')
        references = set(re.findall(r'getInfoTypeForString\("(CIVIC_[A-Z_]+)"\)', code))
        for unknown in references - names:
            errors.append(f'{file}: unknown civic {unknown}')

    for path in (ASSETS / 'XML').rglob('*.xml'):
        for element in ET.parse(path).getroot().iter():
            value = (element.text or '').strip()
            if value.startswith('CIVIC_') and value not in names:
                errors.append(f'{path.name}: unknown civic {value}')

    print(f'Localization: {len(text_files)} files, {count} entries, all five languages.')
    print(f'Civics: {len(civics)} definitions; localized descriptions/help, XML references and C++ civic keys audited.')
    for error in errors:
        print('ERROR:', error)
    if errors:
        raise SystemExit(1)

if __name__ == '__main__':
    audit()
