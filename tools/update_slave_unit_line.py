"""Maintain the sword and post-musket slave tiers without rewriting other XML."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / 'Awakened RFC/Assets/XML'
NEW_TIERS = (
    ('SLAVE_RIFLEMAN', 'TECH_RIFLING', 10, 'RIFLEMAN',
     'Slave Rifleman', 'Sklavensch&#252;tze'),
    ('SLAVE_INFANTRY', 'TECH_ASSEMBLY_LINE', 14, 'INFANTRY',
     'Slave Infantry', 'Sklaveninfanterie'),
    ('SLAVE_MODERN_INFANTRY', 'TECH_ROBOTICS', 20, 'MARINE',
     'Modern Slave Infantry', 'Moderne Sklaveninfanterie'),
)


def upgrade(next_tier):
    if next_tier is None:
        return '<UnitClassUpgrades/>'
    return ('<UnitClassUpgrades>\n\t\t\t\t<UnitClassUpgrade>\n'
            '\t\t\t\t\t<UnitClassUpgradeType>UNITCLASS_' + next_tier + '</UnitClassUpgradeType>\n'
            '\t\t\t\t\t<bUnitClassUpgrade>1</bUnitClassUpgrade>\n'
            '\t\t\t\t</UnitClassUpgrade>\n\t\t\t</UnitClassUpgrades>')


def main():
    unit_path = ROOT / 'Units/CIV4UnitInfos.xml'
    classes_path = ROOT / 'Units/CIV4UnitClassInfos.xml'
    text_path = ROOT / 'Text/CIV4GameText_RFCMPSlavery.xml'
    units = unit_path.read_text(encoding='utf-8').replace('SLAVE_SPEARMAN', 'SLAVE_SWORDSMAN')
    classes = classes_path.read_text(encoding='utf-8').replace('SLAVE_SPEARMAN', 'SLAVE_SWORDSMAN')
    text = text_path.read_text(encoding='utf-8').replace('SLAVE_SPEARMAN', 'SLAVE_SWORDSMAN')

    def patch_sword(match):
        b = match.group(0)
        unit_type = re.search(r'<Type>([^<]+)</Type>', b).group(1)
        if unit_type == 'UNIT_ARMED_SLAVE' or unit_type.startswith('UNIT_SLAVE'):
            b = re.sub(r'<iCityDefense>[^<]+</iCityDefense>', '<iCityDefense>0</iCityDefense>', b)
        if unit_type != 'UNIT_SLAVE' and (unit_type == 'UNIT_ARMED_SLAVE' or unit_type.startswith('UNIT_SLAVE')):
            b = re.sub(r'<GreatPeoples\s*/>',
                '<GreatPeoples><GreatPeople><GreatPeopleType>SPECIALIST_SLAVE</GreatPeopleType>'
                '<bGreatPeople>1</bGreatPeople></GreatPeople></GreatPeoples>', b)
        early_strengths = {'UNIT_ARMED_SLAVE': 3, 'UNIT_SLAVE_SWORDSMAN': 4,
                           'UNIT_SLAVE_MACEMAN': 5}
        if unit_type in early_strengths:
            for field in ('iCombat', 'iPower'):
                b = re.sub('<' + field + r'>[^<]+</' + field + '>',
                           '<' + field + '>' + str(early_strengths[unit_type]) + '</' + field + '>', b)
        if '<Type>UNIT_SLAVE_SWORDSMAN</Type>' in b:
            b = b.replace('ART_DEF_UNIT_SPEARMAN', 'ART_DEF_UNIT_SWORDSMAN')
        return b

    units = re.sub(r'<UnitInfo>.*?</UnitInfo>', patch_sword, units, flags=re.S)
    blocks = re.findall(r'<UnitInfo>.*?</UnitInfo>', units, re.S)
    template = next(b for b in blocks if '<Type>UNIT_SLAVE_MUSKETMAN</Type>' in b)
    for index, (tier, tech, strength, art, english, german) in enumerate(NEW_TIERS):
        b = template.replace('SLAVE_MUSKETMAN', tier)
        b = re.sub(r'<PrereqTech>.*?</PrereqTech>', '<PrereqTech>' + tech + '</PrereqTech>', b)
        for field in ('iCombat', 'iPower'):
            b = re.sub('<' + field + r'>.*?</' + field + '>',
                       '<' + field + '>' + str(strength) + '</' + field + '>', b)
        b = b.replace('ART_DEF_UNIT_MUSKETMAN', 'ART_DEF_UNIT_' + art)
        next_tier = NEW_TIERS[index + 1][0] if index + 1 < len(NEW_TIERS) else None
        b = re.sub(r'<UnitClassUpgrades(?:\s*/>|>.*?</UnitClassUpgrades>)', upgrade(next_tier), b, flags=re.S)
        existing = next((old for old in blocks if '<Type>UNIT_' + tier + '</Type>' in old), None)
        if existing:
            units = units.replace(existing, b, 1)
        else:
            units = units.replace('</UnitInfos>', '\t\t' + b + '\n\t</UnitInfos>', 1)

        class_block = '''<UnitClassInfo>
            <Type>UNITCLASS_%s</Type>
            <Description>TXT_KEY_RFCMP_UNIT_%s</Description>
            <iMaxGlobalInstances>-1</iMaxGlobalInstances>
            <iMaxTeamInstances>-1</iMaxTeamInstances>
            <iMaxPlayerInstances>-1</iMaxPlayerInstances>
            <iInstanceCostModifier>0</iInstanceCostModifier>
            <DefaultUnit>UNIT_%s</DefaultUnit>
        </UnitClassInfo>''' % (tier, tier, tier)
        if '<Type>UNITCLASS_' + tier + '</Type>' not in classes:
            classes = classes.replace('</UnitClassInfos>', '\t\t' + class_block + '\n\t</UnitClassInfos>', 1)
        key = 'TXT_KEY_RFCMP_UNIT_' + tier
        if '<Tag>' + key + '</Tag>' not in text:
            entry = '<TEXT><Tag>' + key + '</Tag>'
            for language in ('English', 'French', 'German', 'Italian', 'Spanish'):
                entry += '<' + language + '>' + (german if language == 'German' else english) + '</' + language + '>'
            text = text.replace('</Civ4GameText>', '  ' + entry + '</TEXT>\n</Civ4GameText>', 1)

    # Extend the former endpoint only after deriving the new units from it.
    patched = re.sub(r'<UnitClassUpgrades(?:\s*/>|>.*?</UnitClassUpgrades>)',
                     upgrade(NEW_TIERS[0][0]), template, flags=re.S)
    units = units.replace(template, patched, 1)
    text = text.replace('Slave Spearman', 'Slave Swordsman').replace(
        'Sklavenspeertr&#228;ger', 'Sklavenschwertk&#228;mpfer')
    for path, contents in ((unit_path, units), (classes_path, classes), (text_path, text)):
        path.write_text(contents, encoding='utf-8')
    # Preserve custom visuals when regenerating the gameplay unit definitions.
    art_path = ROOT / 'Art/CIV4ArtDefines_Unit.xml'
    if 'ART_DEF_UNIT_SLAVE_A' in art_path.read_text(encoding='utf-8'):
        from build_slave_art import apply_unit_visuals
        apply_unit_visuals()
    print('Updated slave sword tier and added rifle, infantry and modern infantry tiers.')


if __name__ == '__main__':
    main()
