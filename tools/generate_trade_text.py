"""Generate complete EN/DE trade text and rename inherited treaty descriptions.

Pass the base Civ4 installation directory to also refresh inherited wording.
The checked-in XML is sufficient for a checkout on another machine.
"""
from pathlib import Path
from xml.sax.saxutils import escape
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'Awakened RFC/Assets/XML/Text/CIV4GameText_TradePolicy.xml'
LANGS=('English','French','German','Italian','Spanish')
ENTRIES={
 'TXT_KEY_TRADE_OPEN_BORDERS_STRING':('Military access','Militärzugang'),
 'TXT_KEY_MISC_OPEN_BORDERS':('Military access','Militärzugang'),
 'TXT_KEY_VOTE_OPEN_BORDERS':('Military access','Militärzugang'),
 'TXT_KEY_MISC_ENABLES_OPEN_BORDERS':('[ICON_BULLET]Enables Military access agreements','[ICON_BULLET]Ermöglicht Militärzugangsabkommen'),
 'TXT_KEY_RFCMP_EMBARGO_STATUS':('Trade policy: %s1_Country','Handelspolitik: %s1_Country'),
 'TXT_KEY_RFCMP_EMBARGO_BY_PARTNER':('(Their embargo blocks trade.)','(Deren Embargo blockiert den Handel.)'),
 'TXT_KEY_RFCMP_EMBARGO_LIFT':('Lift trade embargo','Handelsembargo aufheben'),
 'TXT_KEY_RFCMP_EMBARGO_IMPOSE':('Impose trade embargo','Handelsembargo verhängen'),
 'TXT_KEY_RFCMP_EMBARGO_REQUIRES_CURRENCY':('Trade embargo requires Currency.','Handelsembargos benötigen Währung.'),
 'TXT_KEY_RFCMP_TRADE_EFFICIENCY':('Infrastructure efficiency: %d1_Percent%% (road or sea connection improves trade)','Infrastruktur-Effektivität: %d1_Percent%% (Straßen- oder Wasserverbindung verbessert den Handel)'),
 'TXT_KEY_RFCMP_TRADE_CULTURE':('Cultural exchange per turn: %s1_Here here, %s2_There in the partner city','Kulturaustausch pro Runde: %s1_Here hier, %s2_There in der Partnerstadt'),
 'TXT_KEY_CONCEPT_RELIGION_PEDIA':(
  '[H1]Religion[\\H1][PARAGRAPH:2]Religions are established through scenario and historical founding rules. Cities can contain several religions. Religious buildings and civics determine their effects.[PARAGRAPH:2][H2]Spread through trade[\\H2][PARAGRAPH:2]Trade routes replace the old automatic proximity-based spread. Each route can spread religions present in either partner city to the other, including domestic routes. Chances increase with route commerce and decrease with the receiving city population. Small chances are rounded down. The owner share of stored city culture reduces the chance linearly from no penalty at 75% to the full maximum chance at 100%, blocking trade spread entirely at 100%. Holy cities subtract another three percentage points for other religions. These penalties do not affect missionaries. State Atheism prevents sending and receiving religions through trade; other restrictions on foreign religions also apply.[PARAGRAPH:2][H2]Missionaries[\\H2][PARAGRAPH:2]Missionaries continue to spread their religion using the Spread Religion action. Foreign territory normally requires Military access. Missionaries cannot spread religion into cities under State Atheism.[PARAGRAPH:2]Existing religions remain present when a civilization adopts State Atheism, but religious buildings lose their effects.',
  '[H1]Religion[\\H1][PARAGRAPH:2]Religionen entstehen durch Szenarien und historische Gründungsregeln. Städte können mehrere Religionen enthalten. Religiöse Gebäude und Staatsformen bestimmen deren Effekte.[PARAGRAPH:2][H2]Verbreitung durch Handel[\\H2][PARAGRAPH:2]Handelsrouten ersetzen die bisherige automatische Verbreitung über räumliche Nähe. Jede Route kann Religionen einer Partnerstadt in die andere verbreiten, auch beim Inlandshandel. Die Chance steigt mit dem Routenwert und sinkt mit der Bevölkerung der empfangenden Stadt. Kleine Chancen werden abgerundet. Der Anteil der Besitzerkultur an der gespeicherten Stadtkultur senkt die Chance linear: kein Abzug bei 75%, die gesamte maximale Chance bei 100%. Bei 100% ist Handelsverbreitung unmöglich. Heilige Städte ziehen weitere drei Prozentpunkte für andere Religionen ab. Diese Abzüge betreffen keine Missionare. Staatsatheismus verhindert das Senden und Empfangen von Religionen durch Handel; andere Verbote fremder Religionen gelten ebenfalls.[PARAGRAPH:2][H2]Missionare[\\H2][PARAGRAPH:2]Missionare verbreiten ihre Religion weiterhin über die Aktion Religion verbreiten. Für fremdes Gebiet wird normalerweise Militärzugang benötigt. In Städten unter Staatsatheismus können Missionare keine Religion verbreiten.[PARAGRAPH:2]Bestehende Religionen bleiben beim Wechsel zu Staatsatheismus erhalten; religiöse Gebäude verlieren ihre Effekte.'),
 'TXT_KEY_CONCEPT_COMMERCE_PEDIA':(
  '[H1]Commerce[\\H1][PARAGRAPH:2]Commerce comes from worked tiles and trade routes and is allocated to gold, research, culture and espionage using the sliders. Gold is distinct from the commerce yield. Buildings and civics can modify these yields.[PARAGRAPH:2]Known cities can trade without roads or Military access. Without infrastructure, route efficiency is capped at 50% through distance 5 and declines linearly to zero at distance 15. Routes at distance 15 or farther require infrastructure. Road connections give 100% efficiency without a distance limit. Water connections require Sailing and are limited to distance 12 until Astronomy removes that limit. Cities on different landmasses require an actual navigable connection; caravan trade cannot bypass this. Water-assisted trade is halved unless both cities have a harbor or its civilization-specific replacement. Continuous road-only connections are unaffected. War and trade embargoes block foreign routes. Trade routes exchange culture and religions in both directions, weakened by the population of the receiving city. Cultural influence is half the route value divided by receiving population, rounded down to one decimal place per route and direction. Contributions below 0.1 disappear; city culture retains tenths and tile culture gains accumulated whole points. Religion chances still round down to whole percentage points.[PARAGRAPH:2]From Currency, trade embargoes can be imposed or lifted for a selected civilization on the Foreign Advisor Relations page.',
  '[H1]Wirtschaftspunkte[\\H1][PARAGRAPH:2]Wirtschaftspunkte stammen aus bearbeiteten Feldern und Handelsrouten. Die Regler verteilen sie auf Gold, Forschung, Kultur und Spionage. Gold ist von den Wirtschaftspunkten zu unterscheiden. Gebäude und Staatsformen können die Erträge verändern.[PARAGRAPH:2]Bekannte Städte handeln auch ohne Straßen oder Militärzugang. Ohne Infrastruktur beträgt die Effektivität höchstens 50% bis Entfernung 5 und sinkt danach linear auf null bei Entfernung 15. Ab Entfernung 15 benötigen Routen Infrastruktur. Straßenverbindungen ermöglichen 100% ohne Entfernungslimit. Wasserverbindungen benötigen Segeln und sind bis Astronomie auf Entfernung 12 begrenzt. Städte auf verschiedenen Landmassen benötigen eine tatsächlich befahrbare Verbindung; Karawanenhandel kann dies nicht umgehen. Wasserhandel wird halbiert, wenn nicht beide Städte einen Hafen oder dessen zivilisationsspezifisches Ersatzgebäude besitzen. Durchgehende reine Straßenverbindungen bleiben unberührt. Krieg und Handelsembargos blockieren fremde Routen. Handelsrouten verbreiten Kultur und Religionen in beide Richtungen, abgeschwächt durch die Bevölkerung der empfangenden Stadt. Der Kultureinfluss beträgt den halben Routenwert geteilt durch die empfangende Bevölkerung, pro Route und Richtung auf eine Nachkommastelle abgerundet. Beiträge unter 0,1 verfallen; Stadtkultur speichert Zehntelpunkte und Feldkultur erhält angesammelte ganze Punkte. Religionschancen bleiben auf ganze Prozentpunkte abgerundet.[PARAGRAPH:2]Ab Währung lassen sich im Außenberater unter Beziehungen Handelsembargos gegen die ausgewählte Zivilisation verhängen oder aufheben.'),
 'TXT_KEY_CONCEPT_BORDERS_PEDIA':(
  '[H1]Borders[\\H1][PARAGRAPH:2]Culture determines territorial borders. Foreign units normally need a Military access treaty to enter peacefully. The treaty remains reciprocal and also permits civilian units such as missionaries and workers. It does not enable trade: known cities can exchange trade routes without military access. War and trade embargoes block foreign trade routes.',
  '[H1]Grenzen[\\H1][PARAGRAPH:2]Kultur bestimmt die territorialen Grenzen. Fremde Einheiten benötigen normalerweise Militärzugang, um friedlich einzureisen. Das Abkommen bleibt gegenseitig und erlaubt auch zivilen Einheiten wie Missionaren und Arbeitern die Einreise. Handel benötigt dieses Abkommen nicht: Bekannte Städte können auch ohne Militärzugang Handelsrouten unterhalten. Krieg und Handelsembargos blockieren fremde Handelsrouten.'),
}


def inherited_text(installation):
    result={}
    for directory in (installation/'Assets/XML/Text', installation/'Beyond the Sword/Assets/XML/Text'):
        for path in sorted(directory.glob('*.xml')):
            for entry in ET.parse(path).getroot().iter():
                if entry.tag.split('}')[-1]!='TEXT': continue
                parts={c.tag.split('}')[-1]:c for c in entry}
                if 'English' not in parts or 'Tag' not in parts: continue
                en=''.join(parts['English'].itertext()).strip()
                if 'open borders' not in en.lower(): continue
                def wording(lang):
                    element=parts.get(lang,parts['English'])
                    # Some Firaxis language elements carry Text/Gender/Plural.
                    text_node=next((c for c in element if c.tag.split('}')[-1]=='Text'),element)
                    return ''.join(text_node.itertext()).strip()
                de=wording('German')
                for before,after in [('Open Borders','Military access'),('open borders','military access')]: en=en.replace(before,after)
                en=en.replace('an Military access','a Military access')
                for before,after in [('Offene Grenzen','Militärzugang'),('offene Grenzen','Militärzugang'),('offenen Grenzen','Militärzugang'),('Offenen Grenzen','Militärzugang')]: de=de.replace(before,after)
                result[parts['Tag'].text]=(en,de)
    return result


def main():
    # Retain inherited override entries when generating without local game files.
    values={}
    if len(sys.argv)>1:
        values.update(inherited_text(Path(sys.argv[1])))
    elif OUTPUT.exists():
        for entry in ET.parse(OUTPUT).getroot():
            parts={c.tag.split('}')[-1]:c.text for c in entry}
            values[parts['Tag']]=(parts['English'],parts['German'])
    values.update(ENTRIES)
    lines=['<?xml version="1.0" encoding="UTF-8"?>','<Civ4GameText xmlns="http://www.firaxis.com">']
    for tag,(en,de) in sorted(values.items()):
        lines.extend(['  <TEXT>','    <Tag>'+tag+'</Tag>'])
        for lang in LANGS:
            lines.append('    <'+lang+'>'+escape(de if lang=='German' else en)+'</'+lang+'>')
        lines.append('  </TEXT>')
    lines.append('</Civ4GameText>')
    OUTPUT.write_bytes(('\n'.join(lines)+'\n').encode('ascii','xmlcharrefreplace'))
    print('Wrote %d complete trade-policy text entries.' % len(values))

if __name__=='__main__': main()
