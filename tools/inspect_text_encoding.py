"""Read-only audit of text encoding, damaged characters and language coverage."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MODS = Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Mods")
LANGUAGES = ('English', 'French', 'German', 'Italian', 'Spanish')


def printable(value):
    return ascii(value)

def inspect(folder):
    count = 0
    legacy = 0
    incomplete = 0
    entries = 0
    for path in sorted(folder.rglob('*.xml')):
        try:
            raw = path.read_bytes()
            declaration = re.search(br'encoding=[\"\x27]([^\"\x27]+)', raw)
            encoding = declaration.group(1).decode('ascii') if declaration else 'utf-8'
            source = raw.decode(encoding)
            tree = ET.ElementTree(ET.fromstring(raw))
        except (ET.ParseError, ValueError, LookupError) as error:
            print(path.name, 'XML ERROR:', error)
            continue
        literal_count = sum(ord(char) > 127 for char in source)
        if literal_count and encoding.lower().replace('_', '-') not in ('utf-8', 'utf8'):
            legacy += 1
            print(path.name, 'LEGACY ENCODING:', encoding,
                  'literal non-ASCII characters:', literal_count)
        for entry in tree.getroot().iter():
            if entry.tag.rsplit('}', 1)[-1] != 'TEXT':
                continue
            children = {x.tag.rsplit('}', 1)[-1]: x for x in entry}
            key = children.get('Tag')
            tag = key.text if key is not None else ''
            entries += 1
            missing = [language for language in LANGUAGES if language not in children]
            if missing:
                incomplete += 1
                print(path.name, tag, 'MISSING LANGUAGES:', ', '.join(missing))
            for language in LANGUAGES:
                localized = children.get(language)
                if localized is None:
                    continue
                value = ''.join(localized.itertext())
                # Query strings such as php?f=204 are valid, not damaged umlauts.
                value = re.sub(r'https?://\S+', '', value)
                bad = re.search(r'[A-Za-z]\?[A-Za-z]|\ufffd|\u00ef\u00bf\u00bd|\u00c3[\u0080-\u00bf]|\u00c2[\u0080-\u00bf]|\u00e2\u20ac', value)
                if bad:
                    count += 1
                    start = max(0, bad.start() - 35)
                    sample = value[start:bad.end()+80]
                    print(path.name, tag, language, printable(sample))
    print('Text entries:', entries)
    print('Legacy files with literal non-ASCII:', legacy)
    print('Incomplete language sets:', incomplete)
    print('Suspicious localized entries:', count)

if __name__ == '__main__':
    for label, folder in (
        ('Workspace', ROOT/'Awakened RFC/Assets/XML/Text'),
        ('Original RFC MP', MODS/"Rhye's and Fall MP/Assets/XML/Text"),
    ):
        print('\n' + label)
        inspect(folder)
