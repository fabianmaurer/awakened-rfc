"""Generate conquest relocation text with all five Civ4 language elements."""
from pathlib import Path
from xml.sax.saxutils import escape

ENTRIES=[
    ('RELOCATE_CITY','Relocate (receive a settler)','Umsiedeln (Siedler erhalten)'),
    ('CITY_RELOCATED','%s1_City has been dismantled. Its inhabitants provide a settler.',
     '%s1_City wurde aufgelöst. Aus der Bevölkerung entsteht ein Siedler.'),
]

def main():
    lines=['<?xml version="1.0" encoding="UTF-8"?>','<Civ4GameText xmlns="http://www.firaxis.com">']
    for key,en,de in ENTRIES:
        lines.extend(['  <TEXT>','    <Tag>TXT_KEY_RFCMP_'+key+'</Tag>'])
        for language in ('English','French','German','Italian','Spanish'):
            lines.append('    <'+language+'>'+escape(de if language=='German' else en)+'</'+language+'>')
        lines.append('  </TEXT>')
    lines.append('</Civ4GameText>')
    target=Path(__file__).resolve().parents[1]/'Awakened RFC/Assets/XML/Text/CIV4GameText_CityRelocation.xml'
    target.write_bytes(('\n'.join(lines)+'\n').encode('ascii','xmlcharrefreplace'))

if __name__=='__main__': main()
