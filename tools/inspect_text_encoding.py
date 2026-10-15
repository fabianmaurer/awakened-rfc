"""Read-only report of suspicious characters in localized XML text."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MODS = Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Mods")

def inspect(folder):
    count = 0
    for path in folder.glob('*.xml'):
        try:
            tree = ET.parse(path)
        except (ET.ParseError, ValueError) as error:
            print(path.name, 'XML ERROR:', error)
            continue
        for entry in tree.getroot().iter():
            if entry.tag.rsplit('}', 1)[-1] != 'TEXT':
                continue
            children = {x.tag.rsplit('}', 1)[-1]: x for x in entry}
            key = children.get('Tag')
            german = children.get('German')
            if german is None:
                continue
            value = ''.join(german.itertext())
            # Query strings such as php?f=204 are valid, not damaged umlauts.
            value = re.sub(r'https?://\S+', '', value)
            bad = re.search(r'[A-Za-z]\?[A-Za-z]|\ufffd|\u00ef\u00bf\u00bd|\u00c3[\u0080-\u00bf]', value)
            if bad:
                count += 1
                start = max(0, bad.start() - 35)
                sample = value[start:bad.end()+80]
                print(path.name, key.text if key is not None else '', repr(sample).encode('ascii', 'backslashreplace').decode())
    print('Suspicious German entries:', count)

if __name__ == '__main__':
    for label, folder in (
        ('Workspace', ROOT/'Awakened RFC/Assets/XML/Text'),
        ('Original RFC MP', MODS/"Rhye's and Fall MP/Assets/XML/Text"),
    ):
        print('\n' + label)
        inspect(folder)
