"""Shared five-language text for the naval and agricultural military civics."""
from pathlib import Path
import re
from xml.sax.saxutils import escape

LANGUAGES = ('English', 'French', 'German', 'Italian', 'Spanish')


def translations(*values):
    return dict(zip(LANGUAGES, values))


ENTRIES = {
    'TXT_KEY_RFCMP_CIVIC_NAVAL_WARFARE': translations(
        'Naval Warfare', 'Guerre navale', 'Seekriegsführung', 'Guerra navale', 'Guerra naval'),
    'TXT_KEY_RFCMP_CIVIC_FEUDAL_RETINUES': translations(
        'Feudal Retinues', 'Osts féodaux', 'Heeresfolge', 'Seguiti feudali', 'Mesnadas feudales'),
    'TXT_KEY_RFCMP_CIVIC_EFFECT_NAVAL_WARFARE': translations(
        '[ICON_BULLET]+50% production of military ships, including transports[NEWLINE][ICON_BULLET]+2 experience for newly trained military ships',
        '[ICON_BULLET]+50% à la production de navires militaires, transports compris[NEWLINE][ICON_BULLET]+2 points d’expérience pour les nouveaux navires militaires',
        '[ICON_BULLET]+50% Produktion für Schiffe[NEWLINE][ICON_BULLET]+2XP für neu gebaute Schiffe',
        '[ICON_BULLET]+50% alla produzione di navi militari, inclusi i trasporti[NEWLINE][ICON_BULLET]+2 esperienza per le nuove navi militari',
        '[ICON_BULLET]+50% a la producción de barcos militares, incluidos los transportes[NEWLINE][ICON_BULLET]+2 de experiencia para los nuevos barcos militares'),
    'TXT_KEY_RFCMP_CIVIC_EFFECT_FEUDAL_RETINUES': translations(
        '[ICON_BULLET]+5% land military unit production per Farm worked by this city, including siege units',
        '[ICON_BULLET]+5% à la production d’unités militaires terrestres par ferme exploitée par cette ville, unités de siège comprises',
        '[ICON_BULLET]+5% Produktion für militärische Landeinheiten für jeden Bauernhof, den eine Stadt bewirtschaftet',
        '[ICON_BULLET]+5% alla produzione di unità militari terrestri per fattoria lavorata da questa città, incluse le unità d’assedio',
        '[ICON_BULLET]+5% a la producción de unidades militares terrestres por granja trabajada por esta ciudad, incluidas las unidades de asedio'),
    'TXT_KEY_RFCMP_CIVIC_NAVAL_WARFARE_STRATEGY': translations(
        '+50% military ship production and +2 experience for newly trained military ships, including transports. Workboats receive neither bonus. Available to every civilization with Sailing.',
        '+50% à la production de navires militaires et +2 points d’expérience pour les nouveaux navires militaires, transports compris. Les bateaux de pêche ne reçoivent aucun de ces bonus. Accessible à toute civilisation connaissant la voile.',
        '+50% Produktion für Schiffe und +2XP für neu gebaute Schiffe. Mit Segeln für alle Zivilisationen verfügbar.',
        '+50% alla produzione e +2 esperienza per le nuove navi militari, inclusi i trasporti. Le barche da lavoro non ricevono questi bonus. Disponibile per tutte le civiltà con la Vela.',
        '+50% a la producción y +2 de experiencia para los nuevos barcos militares, incluidos los transportes. Los barcos de trabajo no reciben estas bonificaciones. Disponible para todas las civilizaciones con Navegación a vela.'),
    'TXT_KEY_RFCMP_CIVIC_FEUDAL_RETINUES_STRATEGY': translations(
        '+5% land military unit production per Farm actually worked by the producing city. Includes siege units; excludes civilian units and ships. Six worked Farms give +30%.',
        '+5% à la production d’unités militaires terrestres par ferme effectivement exploitée par la ville productrice. Inclut les unités de siège ; exclut les unités civiles et les navires. Six fermes exploitées donnent +30%.',
        '+5% Produktion für militärische Landeinheiten für jeden Bauernhof, den eine Stadt bewirtschaftet.',
        '+5% alla produzione di unità militari terrestri per fattoria effettivamente lavorata dalla città produttrice. Include le unità d’assedio; esclude le unità civili e le navi. Sei fattorie lavorate danno +30%.',
        '+5% a la producción de unidades militares terrestres por granja efectivamente trabajada por la ciudad productora. Incluye las unidades de asedio; excluye las unidades civiles y los barcos. Seis granjas trabajadas otorgan +30%.'),
    'TXT_KEY_RFCMP_CIVIC_NAVAL_WARFARE_PEDIA': translations(
        'Naval Warfare organizes shipyards, crews and transport fleets for war at sea and overseas expeditions. A maritime power can devote more resources to replacing ships and training crews, while another military institution may better serve a continental army.',
        'La guerre navale organise les chantiers, les équipages et les flottes de transport pour le combat en mer et les expéditions outre-mer. Une puissance maritime peut renforcer sa flotte et former ses équipages, tandis qu’une autre institution militaire peut mieux servir une armée continentale.',
        'Seekriegsführung organisiert Werften, Besatzungen und Transportflotten für den Krieg auf See und überseeische Feldzüge. Eine Seemacht kann mehr Mittel in neue Schiffe und ausgebildete Besatzungen investieren, während eine andere Militärordnung einem Landheer besser dienen kann.',
        'La guerra navale organizza cantieri, equipaggi e flotte da trasporto per i combattimenti in mare e le spedizioni oltremare. Una potenza marittima può investire nelle navi e nell’addestramento degli equipaggi, mentre un’altra istituzione militare può servire meglio un esercito continentale.',
        'La guerra naval organiza astilleros, tripulaciones y flotas de transporte para combatir en el mar y realizar expediciones ultramarinas. Una potencia marítima puede invertir en barcos y tripulaciones, mientras que otra institución militar puede servir mejor a un ejército continental.'),
    'TXT_KEY_RFCMP_CIVIC_FEUDAL_RETINUES_PEDIA': translations(
        'Feudal Retinues mobilize military service and provisions through agricultural estates. Worked farms support the producing city’s land forces, making a productive rural base an alternative to the superior training of a Professional Army.',
        'Les osts féodaux mobilisent le service militaire et les provisions des domaines agricoles. Les fermes exploitées soutiennent les forces terrestres de leur ville : une base rurale productive offre ainsi une alternative à l’entraînement supérieur d’une armée professionnelle.',
        'Heeresfolge mobilisiert Kriegsdienste und Versorgung durch landwirtschaftliche Güter. Bewirtschaftete Bauernhöfe unterstützen die Landstreitkräfte ihrer Stadt. Eine leistungsfähige Landwirtschaft bietet so eine Alternative zur besseren Ausbildung einer Berufsarmee.',
        'I seguiti feudali mobilitano il servizio militare e le provviste delle proprietà agricole. Le fattorie lavorate sostengono le forze terrestri della propria città: una base rurale produttiva offre un’alternativa al migliore addestramento di un esercito professionale.',
        'Las mesnadas feudales movilizan el servicio militar y los suministros de las propiedades agrícolas. Las granjas trabajadas sostienen las fuerzas terrestres de su ciudad: una base rural productiva ofrece una alternativa al mejor adiestramiento de un ejército profesional.'),
    'TXT_KEY_RFCMP_ELECTION_NAVAL_WARFARE': translations(
        'The electorate has voted to rule the waves. The shipyards applaud; the admiralty is checking whether anyone remembered to build transports.',
        'Les électeurs ont voté pour dominer les mers. Les chantiers applaudissent ; l’amirauté vérifie si quelqu’un a pensé aux transports.',
        'Die Wähler wollen die Meere beherrschen. Die Werften applaudieren; die Admiralität prüft, ob jemand an Transportschiffe gedacht hat.',
        'Gli elettori hanno votato per dominare i mari. I cantieri applaudono; l’ammiragliato controlla se qualcuno si è ricordato dei trasporti.',
        'El electorado ha votado por dominar los mares. Los astilleros aplauden; el almirantazgo comprueba si alguien se acordó de los transportes.'),
    'TXT_KEY_RFCMP_ELECTION_FEUDAL_RETINUES': translations(
        'The voters have pledged military service from their estates. Every worked farm must support the muster; the turnips have requested an exemption.',
        'Les électeurs ont promis le service militaire de leurs domaines. Chaque ferme exploitée doit soutenir la levée ; les navets ont demandé une exemption.',
        'Die Wähler haben den Kriegsdienst ihrer Güter zugesagt. Jeder bewirtschaftete Bauernhof soll das Aufgebot versorgen; die Rüben beantragen eine Befreiung.',
        'Gli elettori hanno promesso il servizio militare delle loro terre. Ogni fattoria lavorata deve sostenere la leva; le rape hanno chiesto un’esenzione.',
        'Los votantes han comprometido el servicio militar de sus tierras. Cada granja trabajada debe sostener la leva; los nabos han solicitado una exención.'),
    'TXT_KEY_RFCMP_PRODUCTION_MILITARY_CIVIC': translations(
        '+%d1_Modifier% [ICON_PRODUCTION] from %s2_Civic',
        '+%d1_Modifier% [ICON_PRODUCTION] grâce à %s2_Civic',
        '+%d1_Modifier% [ICON_PRODUCTION] durch %s2_Civic',
        '+%d1_Modifier% [ICON_PRODUCTION] da %s2_Civic',
        '+%d1_Modifier% [ICON_PRODUCTION] por %s2_Civic'),
}


def entry_xml(key, values):
    lines = ['    <TEXT>', '        <Tag>' + key + '</Tag>']
    for language in LANGUAGES:
        value = escape(values[language]).encode('ascii', 'xmlcharrefreplace').decode('ascii')
        lines.append('        <' + language + '>' + value + '</' + language + '>')
    return '\n'.join(lines + ['    </TEXT>'])


def update_definitions():
    path = Path(__file__).resolve().parents[1] / 'Awakened RFC/Assets/XML/Text/CIV4GameText_RFCCivics.xml'
    source = path.read_bytes().decode('utf-8')
    for old, new in [('MILITIA', 'NAVAL_WARFARE'), ('KNIGHTHOOD', 'FEUDAL_RETINUES')]:
        source = source.replace('TXT_KEY_RFCMP_CIVIC_' + old, 'TXT_KEY_RFCMP_CIVIC_' + new)
        source = source.replace('TXT_KEY_RFCMP_CIVIC_EFFECT_' + old, 'TXT_KEY_RFCMP_CIVIC_EFFECT_' + new)
    for key, values in ENTRIES.items():
        if '_STRATEGY' in key or '_ELECTION_' in key:
            continue
        block = entry_xml(key, values)
        pattern = r'[ \t]*<TEXT>\s*<Tag>' + re.escape(key) + r'</Tag>.*?</TEXT>'
        if re.search(pattern, source, re.S):
            source = re.sub(pattern, lambda match: block, source, flags=re.S)
        else:
            source = source.replace('</Civ4GameText>', block + '\n</Civ4GameText>')
    path.write_bytes(source.encode('utf-8'))


if __name__ == '__main__':
    update_definitions()
