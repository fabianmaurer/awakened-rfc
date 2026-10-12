"""Write complete five-language production conversion text, using ASCII XML."""
from pathlib import Path
from xml.sax.saxutils import escape

ENTRIES = [
    ('BASIC_WEALTH', 'Basic Wealth', 'Einfache Geldkonvertierung'),
    ('BASIC_WEALTH_STRATEGY',
     'Converts 25% of production into gold. Available from the beginning; Currency replaces it with Wealth at 50% efficiency.',
     'Wandelt 25% der Produktion in Gold um. Von Beginn an verfügbar; Währung ersetzt diese Konvertierung durch die Geldkonvertierung mit 50% Effektivität.'),
    ('WEALTH_STRATEGY', 'Converts 50% of production into gold. Requires Currency.',
     'Wandelt 50% der Produktion in Gold um. Benötigt Währung.'),
    ('RESEARCH_STRATEGY', 'Converts 25% of production into research. Requires Alphabet.',
     'Wandelt 25% der Produktion in Forschung um. Benötigt Alphabet.'),
    ('CULTURE_STRATEGY', 'Converts 50% of production into culture. Requires Music.',
     'Wandelt 50% der Produktion in Kultur um. Benötigt Musik.'),
]

def main():
    lines=['<?xml version="1.0" encoding="UTF-8"?>','<Civ4GameText xmlns="http://www.firaxis.com">']
    for suffix,english,german in ENTRIES:
        lines += ['  <TEXT>','    <Tag>TXT_KEY_RFCMP_PROCESS_'+suffix+'</Tag>']
        for lang in ('English','French','German','Italian','Spanish'):
            lines.append('    <'+lang+'>'+escape(german if lang=='German' else english)+'</'+lang+'>')
        lines.append('  </TEXT>')
    lines.append('</Civ4GameText>')
    path=Path(__file__).resolve().parents[1]/'RFC MP Plus/Assets/XML/Text/CIV4GameText_ProductionConversions.xml'
    path.write_bytes(('\n'.join(lines)+'\n').encode('ascii','xmlcharrefreplace'))

if __name__=='__main__': main()
