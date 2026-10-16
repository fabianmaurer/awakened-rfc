"""Generate modern-era research, buildings and complete localized text.

Retired infos remain as disabled identifiers because RFC scripts use numeric
unit/technology IDs. This tool does not start the game or run gameplay tests.
"""
from pathlib import Path
import re
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
XML = ROOT / 'Awakened RFC/Assets/XML'
AIR_TECHS = {'TECH_FLIGHT', 'TECH_ADVANCED_FLIGHT', 'TECH_STEALTH'}
RETIRED_UNITS = {'UNIT_CARRIER', 'UNIT_GUNSHIP', 'UNIT_SAM_INFANTRY', 'UNIT_MOBILE_SAM', 'UNIT_ICBM'}
RETIRED_BUILDINGS = {'BUILDING_AIRPORT', 'BUILDING_BOMB_SHELTER'}
RETIRED_PROMOTIONS = {'PROMOTION_RANGE1', 'PROMOTION_RANGE2', 'PROMOTION_INTERCEPTION1', 'PROMOTION_INTERCEPTION2', 'PROMOTION_ACE'}
TECHS = [
    # suffix, English, German, base cost, prerequisites, x, y, repeat, health, happy
    ('ENVIRONMENTAL_PROGRESS', 'Environmental Quality', 'Umwelt- und Lebensqualität', 6000, ['ECOLOGY'], 21, 1, 1, 0, 1),
    ('MEDICAL_PROGRESS', 'Medical Progress', 'Medizinischer Fortschritt', 6500, ['MEDICINE'], 21, 5, 1, 1, 0),
    ('MILITARY_RESEARCH', 'Military Research', 'Militärische Forschung', 8000, ['COMPUTERS'], 21, 9, 1, 0, 0),
    ('DIGITAL_ADMINISTRATION', 'Digital Administration', 'Digitale Verwaltung', 16000, ['COMPUTERS'], 22, 3, 0, 0, 0),
    ('MACHINE_LEARNING', 'Machine Learning', 'Maschinelles Lernen', 24000, ['COMPUTERS', 'FIBER_OPTICS'], 22, 7, 0, 0, 0),
    ('AI_SERVICES', 'AI-Assisted Services', 'KI-gestützte Dienstleistungen', 36000, ['DIGITAL_ADMINISTRATION', 'MACHINE_LEARNING'], 23, 3, 0, 0, 0),
    ('NETWORKED_PRODUCTION', 'Networked Production', 'Vernetzte Produktion', 50000, ['MACHINE_LEARNING', 'ROBOTICS'], 23, 9, 0, 0, 0),
    ('GENERAL_AI', 'General Artificial Intelligence', 'Allgemeine künstliche Intelligenz', 80000, ['AI_SERVICES', 'NETWORKED_PRODUCTION'], 24, 6, 0, 0, 0),
    ('FULL_AUTOMATION', 'Full Automation', 'Vollständige Automatisierung', 140000, ['GENERAL_AI', 'FUSION'], 25, 6, 0, 0, 0),
]
BUILDINGS = [
    # suffix, English, German, tech, cost, gold%, science%, production%, maintenance%, health, happiness
    ('DIGITAL_ADMINISTRATION', 'Digital Administration Centre', 'Digitales Verwaltungszentrum', 'DIGITAL_ADMINISTRATION', 400, 0, 0, 0, -20, 0, 0),
    ('MACHINE_LEARNING', 'Machine Learning Laboratory', 'Labor für maschinelles Lernen', 'MACHINE_LEARNING', 500, 0, 25, 0, 0, 0, 0),
    ('AI_SERVICES', 'AI Services Centre', 'KI-Dienstleistungszentrum', 'AI_SERVICES', 650, 15, 0, 0, 0, 2, 1),
    ('NETWORKED_PRODUCTION', 'Networked Factory', 'Vernetzte Fabrik', 'NETWORKED_PRODUCTION', 850, 0, 0, 25, 0, 0, 0),
    ('GENERAL_AI', 'General AI Research Centre', 'Forschungszentrum für allgemeine KI', 'GENERAL_AI', 1100, 0, 40, 0, 0, 0, 0),
    ('FULL_AUTOMATION', 'Automated Production Complex', 'Vollautomatisierter Produktionskomplex', 'FULL_AUTOMATION', 1800, 25, 0, 50, 0, 0, 0),
]


def field(block, tag, value):
    pattern = r'<' + tag + r'(?:\s*/>|>.*?</' + tag + r'>)'
    result, count = re.subn(pattern, lambda _: '<%s>%s</%s>' % (tag, value, tag), block, count=1, flags=re.S)
    if count != 1:
        raise ValueError('Missing field ' + tag)
    return result


def typename(block):
    return re.search(r'<Type>([^<]+)</Type>', block).group(1)


def read(path):
    return (XML / path).read_bytes().decode('utf-8')


def write(path, text):
    (XML / path).write_bytes(text.encode('utf-8'))


def records(text, tag):
    return re.findall(r'<' + tag + r'>.*?</' + tag + r'>', text, re.S)


def append_records(text, container, additions):
    return text.replace('</' + container + '>', '\n' + '\n'.join(additions) + '\n</' + container + '>')


def main():
    texts = []
    def add(tag, en, de):
        texts.append((tag, en, de))

    path = 'Technologies/CIV4TechInfos.xml'
    text = read(path)
    template = next(b for b in records(text, 'TechInfo') if typename(b) == 'TECH_FUTURE_TECH')
    for old in records(text, 'TechInfo'):
        name = typename(old)
        if name in {'TECH_' + t[0] for t in TECHS}:
            text = text.replace(old, '')
        elif name in AIR_TECHS or name == 'TECH_FUTURE_TECH':
            new = field(field(field(old, 'bDisable', '1'), 'iGridX', '-1'), 'iGridY', '-1')
            text = text.replace(old, new)
        else:
            new = old.replace('TECH_ADVANCED_FLIGHT', 'TECH_COMPUTERS').replace('TECH_FLIGHT', 'TECH_COMBUSTION').replace('TECH_STEALTH', 'TECH_COMPOSITES')
            text = text.replace(old, new)
    additions = []
    for suffix, en, de, cost, prereqs, x, y, repeat, health, happy in TECHS:
        block = re.sub(r'<!--.*?-->', '', template, flags=re.S)
        values = {'Type': 'TECH_' + suffix, 'Description': 'TXT_KEY_TECH_' + suffix,
                  'Civilopedia': 'TXT_KEY_TECH_' + suffix + '_PEDIA', 'Help': 'TXT_KEY_TECH_' + suffix + '_HELP',
                  'Strategy': 'TXT_KEY_TECH_' + suffix + '_PEDIA', 'iCost': cost, 'bDisable': 0,
                  'bRepeat': repeat, 'bTrade': 0, 'iHealth': health, 'iHappiness': happy,
                  'iGridX': x, 'iGridY': y, 'Era': 'ERA_MODERN' if repeat else 'ERA_FUTURE',
                  'iAIWeight': 0, 'iAsset': 32, 'iPower': 0, 'iAdvancedStartCost': -1,
                  'OrPreReqs': '', 'AndPreReqs': ''.join('<PrereqTech>TECH_' + p + '</PrereqTech>' for p in prereqs),
                  'Quote': '', 'Sound': 'AS2D_TECH_FUTURE', 'SoundMP': 'AS2D_TECH_MP_FUTURE'}
        for tag, value in values.items():
            block = field(block, tag, str(value))
        additions.append(block)
        add('TXT_KEY_TECH_' + suffix, en, de)
        if repeat:
            effect_en = '+1 happiness in every city.' if happy else ('+1 health in every city.' if health else '+1 percentage point of combat strength for land and naval units, up to +15%. Research ends at level 15.')
            effect_de = '+1 Zufriedenheit in jeder Stadt.' if happy else ('+1 Gesundheit in jeder Stadt.' if health else '+1 Prozentpunkt Kampfstärke für Land- und Marineeinheiten, höchstens +15 %. Die Forschung endet bei Stufe 15.')
            help_en = effect_en + ' Each completion increases this field\'s cost by 35%; other fields are unaffected. Costs are rounded up; engine safety limit: 2,000,000 research.'
            help_de = effect_de + ' Jeder Abschluss verteuert diese Richtung um 35 %; andere Richtungen bleiben unverändert. Kosten werden aufgerundet; technische Obergrenze: 2.000.000 Forschung.'
        else:
            help_en = 'Expensive long-term research. Unlocks a specialized city building; repeatable research remains an alternative.'
            help_de = 'Sehr teure Langzeitforschung. Schaltet ein spezialisiertes Stadtgebäude frei; Dauerforschung bleibt eine Alternative.'
        add('TXT_KEY_TECH_' + suffix + '_HELP', help_en, help_de)
        add('TXT_KEY_TECH_' + suffix + '_PEDIA', help_en, help_de)
    text = append_records(text, 'TechInfos', additions)
    write(path, text)

    path = 'Buildings/CIV4BuildingInfos.xml'
    text = read(path)
    template = next(b for b in records(text, 'BuildingInfo') if typename(b) == 'BUILDING_LABORATORY')
    if '<YieldModifiers' not in template:
        template = template.replace('<CommerceChanges', '<YieldModifiers/><CommerceChanges', 1)
    for old in records(text, 'BuildingInfo'):
        if typename(old) in {'BUILDING_' + b[0] for b in BUILDINGS}:
            text = text.replace(old, '')
        elif typename(old) in RETIRED_BUILDINGS:
            text = text.replace(old, field(old, 'iCost', '-1'))
    additions = []
    for suffix, en, de, tech, cost, gold, science, production, maintenance, health, happy in BUILDINGS:
        block = re.sub(r'<!--.*?-->', '', template, flags=re.S)
        values = {'Type': 'BUILDING_' + suffix, 'BuildingClass': 'BUILDINGCLASS_' + suffix,
                  'Description': 'TXT_KEY_BUILDING_' + suffix, 'Civilopedia': 'TXT_KEY_BUILDING_' + suffix + '_PEDIA',
                  'Strategy': 'TXT_KEY_BUILDING_' + suffix + '_PEDIA', 'PrereqTech': 'TECH_' + tech,
                  'iCost': cost, 'iHealth': health, 'iHappiness': happy, 'iMaintenanceModifier': maintenance,
                  'iSpaceProductionModifier': 0, 'SpecialistCounts': '', 'BuildingClassNeededs': '',
                  'CommerceModifiers': '<iCommerce>%d</iCommerce><iCommerce>%d</iCommerce><iCommerce>0</iCommerce><iCommerce>0</iCommerce>' % (gold, science),
                  'YieldModifiers': '<iYield>0</iYield><iYield>%d</iYield><iYield>0</iYield>' % production}
        for tag, value in values.items():
            block = field(block, tag, str(value))
        additions.append(block)
        add('TXT_KEY_BUILDING_' + suffix, en, de)
        add('TXT_KEY_BUILDING_' + suffix + '_PEDIA', 'A specialized modernization enabled by advanced AI and automation research.', 'Eine spezialisierte Modernisierung durch fortgeschrittene KI- und Automatisierungsforschung.')
    write(path, append_records(text, 'BuildingInfos', additions))
    path = 'Buildings/CIV4BuildingClassInfos.xml'
    text = read(path)
    additions = []
    for suffix, *_ in BUILDINGS:
        name = 'BUILDINGCLASS_' + suffix
        for old in records(text, 'BuildingClassInfo'):
            if typename(old) == name:
                text = text.replace(old, '')
        additions.append('<BuildingClassInfo><Type>%s</Type><Description>TXT_KEY_BUILDING_%s</Description><iMaxGlobalInstances>-1</iMaxGlobalInstances><iMaxTeamInstances>-1</iMaxTeamInstances><iMaxPlayerInstances>-1</iMaxPlayerInstances><iExtraPlayerInstances>0</iExtraPlayerInstances><bNoLimit>0</bNoLimit><bMonument>0</bMonument><DefaultBuilding>BUILDING_%s</DefaultBuilding><VictoryThresholds/></BuildingClassInfo>' % (name, suffix, suffix))
    write(path, append_records(text, 'BuildingClassInfos', additions))

    path = 'Units/CIV4UnitInfos.xml'
    text = read(path)
    blocks = records(text, 'UnitInfo')
    for b in blocks:
        if '<Domain>DOMAIN_AIR</Domain>' in b:
            RETIRED_UNITS.add(typename(b))
    retired_classes = {re.search(r'<Class>([^<]+)</Class>', b).group(1) for b in blocks if typename(b) in RETIRED_UNITS}
    for old in blocks:
        block = old
        if typename(old) in RETIRED_UNITS:
            block = field(field(block, 'iCost', '-1'), 'iAdvancedStartCost', '-1')
        else:
            for tag in ('iInterceptionProbability', 'iAirRange', 'iAirCombat', 'iAirCombatLimit', 'iEvasionProbability'):
                block = field(block, tag, '0')
            if '<DomainCargo>DOMAIN_AIR</DomainCargo>' in block:
                block = field(field(field(block, 'iCargo', '0'), 'DomainCargo', 'NONE'), 'SpecialCargo', 'NONE')
            for role in re.findall(r'<UnitAI>.*?</UnitAI>', block, re.S):
                if 'UNITAI_MISSILE_CARRIER_SEA' in role or 'UNITAI_CARRIER_SEA' in role:
                    block = block.replace(role, '')
            for tag in ('UnitClassAttackMod', 'UnitClassDefenseMod', 'UnitCombatMod'):
                for modifier in re.findall(r'<' + tag + r'>.*?</' + tag + r'>', block, re.S):
                    if ('UNITCOMBAT_AIR' in modifier or 'UNITCOMBAT_HELICOPTER' in modifier or
                            any('<UnitClassType>' + c + '</UnitClassType>' in modifier for c in retired_classes)):
                        block = block.replace(modifier, '')
            for upgrade in re.findall(r'<UnitClassUpgrade>.*?</UnitClassUpgrade>', block, re.S):
                if any('<UnitClassUpgradeType>' + c + '</UnitClassUpgradeType>' in upgrade for c in retired_classes):
                    block = block.replace(upgrade, '')
            if typename(old) == 'UNIT_CAVALRY':
                block = field(block, 'UnitClassUpgrades', '<UnitClassUpgrade><UnitClassUpgradeType>UNITCLASS_TANK</UnitClassUpgradeType><bUnitClassUpgrade>1</bUnitClassUpgrade></UnitClassUpgrade>')
            block = block.replace('TECH_STEALTH', 'TECH_COMPOSITES')
        text = text.replace(old, block)
    write(path, text)
    path = 'Units/CIV4PromotionInfos.xml'
    text = read(path)
    for old in records(text, 'PromotionInfo'):
        if typename(old) in RETIRED_PROMOTIONS:
            text = text.replace(old, field(old, 'TechPrereq', 'TECH_FLIGHT'))
    write(path, text)
    path = 'GameInfo/CIV4ProjectInfo.xml'
    text = read(path)
    for old in records(text, 'ProjectInfo'):
        if typename(old) in ('PROJECT_MANHATTAN_PROJECT', 'PROJECT_SDI'):
            text = text.replace(old, field(old, 'iCost', '-1'))
    write(path, text)

    # Retired aviation/nuclear events must not grant disabled units or demand
    # production of units/buildings which can no longer be built.
    path = 'Events/CIV4EventTriggerInfos.xml'
    text = read(path)
    for old in records(text, 'EventTriggerInfo'):
        if any(name in old for name in retired_classes | {'BUILDINGCLASS_AIRPORT', 'BUILDINGCLASS_BOMB_SHELTER'}):
            text = text.replace(old, field(old, 'iPercentGamesActive', '0'))
    write(path, text)

    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<Civ4GameText xmlns="http://www.firaxis.com">']
    for tag, english, german in texts:
        lines += ['<TEXT><Tag>' + tag + '</Tag>']
        for language in ('English', 'French', 'German', 'Italian', 'Spanish'):
            lines.append('<%s>%s</%s>' % (language, escape(german if language == 'German' else english), language))
        lines.append('</TEXT>')
    lines.append('</Civ4GameText>')
    (XML / 'Text/CIV4GameText_ModernEra.xml').write_bytes(('\n'.join(lines) + '\n').encode('ascii', 'xmlcharrefreplace'))
    data = ('# Generated modern-era identifiers. Compatible with Python 2.4.\n'
            'RETIRED_UNITS = %r\nRETIRED_PROMOTIONS = %r\n' %
            (tuple(sorted(RETIRED_UNITS)), tuple(sorted(RETIRED_PROMOTIONS))))
    (ROOT / 'Awakened RFC/Assets/Python/ModernEraData.py').write_text(data, encoding='ascii')
    print('Generated 9 technologies, 6 buildings; retired %d units.' % len(RETIRED_UNITS))


if __name__ == '__main__':
    main()
