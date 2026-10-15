"""Build distinct Civ4 slave NIFs and irregular formations from local game art.

Run with .venv-art/Scripts/python.exe; requires PyFFI and setuptools. Source
game/DoC assets are read only. See docs/SlaveUnitArt.md for provenance.
"""
from pathlib import Path
import io
import math
import re
import shutil
import struct
import time

if not hasattr(time, 'clock'):
    time.clock = time.perf_counter  # PyFFI 2.2 compatibility with modern Python.
N = None  # Imported only for the full NIF build, not XML-only regeneration.

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'RFC MP Plus'
GAME = Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization IV Beyond the Sword")
BTS = GAME / 'Beyond the Sword'
DOC = BTS / 'Mods/RFC Dawn of Civilization'
ART = MOD / 'Assets/Art/Units/SlaveUnits'
PACK = GAME / 'Assets/Art0.FPK'

# Unit type, model source, animation source, art-definition template, firearm.
TIERS = (
    ('SLAVE', 'base:Art/Units/Warrior/Warrior.nif', 'Art/Units/Warrior/Warrior.kfm', 'WARRIOR', False),
    ('ARMED_SLAVE', 'bts:Art/Units/Axeman_Middle_East/Axeman_Middle_East.nif', 'Art/Units/Axeman_Middle_East/Axeman_Egyptian.kfm', 'AXEMAN_MIDDLE_EAST', False),
    ('SLAVE_SWORDSMAN', 'base:Art/Units/Swordsman/Swordsman.nif', 'Art/Units/Swordsman/Swordsman.kfm', 'SWORDSMAN', False),
    ('SLAVE_MACEMAN', 'base:Art/Units/Maceman/Maceman.nif', 'Art/Units/Maceman/Maceman.kfm', 'MACEMAN', False),
    ('SLAVE_MUSKETMAN', 'revolution:Art/Units/Militia/Browncoat.nif', 'LOCAL', 'MUSKETMAN', True),
    ('SLAVE_RIFLEMAN', 'doc:Art/Units/Armed Pioneer/davycrockett.nif', 'Art/Units/Unique_Ethiopia_OromoWarrior/Ethiopian_OromoWarrior.kfm', 'RIFLEMAN', True),
    ('SLAVE_INFANTRY', 'base:Art/Units/Infantry/Infantry.nif', 'Art/Units/Infantry/Infantry.kfm', 'INFANTRY', True),
    ('SLAVE_MODERN_INFANTRY', 'base:Art/Units/Marine/Marines.nif', 'Art/Units/Marine/Marines.kfm', 'MARINE', True),
)


class Assets:
    def __init__(self):
        self.packed = {}
        with PACK.open('rb') as f:
            if f.read(9) != b'\x04\x00\x00\x00FPK_\x01':
                raise ValueError('Unsupported Civ4 FPK header')
            count, = struct.unpack('<I', f.read(4))
            for _ in range(count):
                length, = struct.unpack('<I', f.read(4))
                name = bytes((v - 1) % 256 for v in f.read(length)).decode('latin-1').replace('\\', '/').lower()
                f.read((-length) % 4)
                _, _, size, offset = struct.unpack('<IIII', f.read(16))
                self.packed[name] = (offset, size)
        self.roots = {'base': GAME / 'Assets', 'bts': BTS / 'Assets',
                      'warlords': GAME / 'Warlords/Assets',
                      'doc': DOC / 'Assets',
                      'revolution': GAME / 'Mods/American Revolution/Assets'}
        self.by_name = {}
        for prefix in ('base', 'bts', 'warlords', 'doc', 'revolution'):
            for p in self.roots[prefix].rglob('*.dds'):
                self.by_name.setdefault(p.name.lower(), p)

    def read(self, source):
        prefix, relative = source.split(':', 1)
        p = self.roots[prefix] / relative
        if p.is_file():
            return p.read_bytes()
        key = relative.replace('\\', '/').lower()
        if key not in self.packed:
            raise FileNotFoundError(source)
        offset, size = self.packed[key]
        with PACK.open('rb') as f:
            f.seek(offset)
            return f.read(size)

    def texture(self, filename, source):
        filename = filename.replace('\\', '/')
        prefix, relative = source.split(':', 1)
        sibling = self.roots[prefix] / Path(relative).parent / Path(filename).name
        if sibling.is_file():
            return sibling.read_bytes()
        if Path(filename).name.lower() in self.by_name:
            return self.by_name[Path(filename).name.lower()].read_bytes()
        key = filename.lower()
        if key not in self.packed:
            key = next((k for k in self.packed if k.endswith('/' + Path(filename).name.lower())), key)
        return self.read('base:' + key)


def use_slave_body(assets, data, out):
    """Rebind the unarmed slave mesh to the weapon donor's animated rig.

    Bake the donor's rest pose into the body, then rebuild inverse bind
    matrices. Keep bone references (and weights) rather than a rigid body:
    the donor KFM must still animate hands, legs and head independently.
    """
    base = N.Data()
    base_source = TIERS[0][1]
    base.read(io.BytesIO(assets.read(base_source)))
    body = next(b for b in base.blocks if getattr(b, 'name', b'') == b'Warrior_Body')
    root = data.roots[0]
    nodes = [b for b in root.tree() if isinstance(b, N.NiNode)]
    main = next(b for b in data.blocks
                if isinstance(b, (N.NiTriShape, N.NiTriStrips))
                and b.skin_instance and b.name in
                (b'Editable Mesh', b'Editable Mesh@#1', b'Celtic_Warrior_Body', b'Scout_Man:1', b'RedCoat', b'Infantry', b'Marine'))
    preferred = {b.name: b for b in main.skin_instance.bones}
    late = main.name in (b'Infantry', b'Marine')
    mapped = []
    for bone in body.skin_instance.bones:
        name = bone.name.replace(b'BIP ', b'Bip01 ', 1) if late else bone.name
        # The firearm rigs omit clavicles; fold those few weights into the
        # corresponding upper arm, whose animation already drives the shoulder.
        if late and b'Clavicle' in name:
            name = name.replace(b'Clavicle', b'UpperArm')
        target = preferred.get(name)
        if target is None:
            target = next((b for b in nodes if b.name == name), None)
        if target is None and name == b'Bip01 Neck':
            # Marines animate the head directly, without a separate neck node.
            target = preferred[b'Bip01 Head']
        if target is None:
            raise ValueError('Missing animated bone: ' + repr(name))
        mapped.append(target)
    original_bones = list(body.skin_instance.bones)
    rest, normals = body.get_skin_deformation()
    body_to_root = body.get_transform(base.roots[0])
    weights = body.get_vertex_weights()
    transforms = []
    for old, new in zip(original_bones, mapped):
        old_matrix = old.get_transform(base.roots[0])
        new_matrix = new.get_transform(root)
        # Some imported heads have a 0.5 bone scale. Preserve the slave's
        # proportions instead of shrinking its head to the civilian donor's.
        old_scale = old_matrix.get_scale_rotation_translation()[0]
        new_scale = new_matrix.get_scale_rotation_translation()[0]
        compensation = N.Matrix44()
        compensation.set_identity()
        for axis in ('m_11', 'm_22', 'm_33'):
            setattr(compensation, axis, old_scale / new_scale)
        transforms.append(old_matrix.get_inverse() * compensation * new_matrix)
    for i, vertex in enumerate(body.data.vertices):
        source_vertex = rest[i] * body_to_root
        result = N.Vector3()
        for bone_index, weight in weights[i]:
            result += (source_vertex * transforms[bone_index]) * weight
        vertex.x, vertex.y, vertex.z = result.x, result.y, result.z
        normal = N.Vector3()
        source_normal = normals[i] * body_to_root.get_matrix_33()
        for bone_index, weight in weights[i]:
            normal += (source_normal * transforms[bone_index].get_matrix_33()) * weight
        normal.normalize(ignore_error=True)
        body.data.normals[i].x = normal.x
        body.data.normals[i].y = normal.y
        body.data.normals[i].z = normal.z
    identity = N.Matrix44()
    identity.set_identity()
    body.set_transform(identity)
    body.skin_instance.skeleton_root = root
    body.skin_instance.data.set_transform(identity)
    for i, bone in enumerate(mapped):
        body.skin_instance.bones[i] = bone
        body.skin_instance.data.bone_list[i].set_transform(bone.get_transform(root).get_inverse())
    body.data.update_center_radius()
    body.update_skin_center_radius()
    # Import the slave's texture using its own source context, before donor
    # textures are resolved (the meshes have different UV layouts).
    for block in body.tree():
        if isinstance(block, N.NiSourceTexture) and block.file_name:
            filename = block.file_name.decode('latin-1').replace(chr(92), '/')
            if Path(filename).name.lower() == 'teamcolor.bmp':
                continue
            target = out / Path(filename).name
            target.write_bytes(assets.texture(filename, base_source))
            block.file_name = target.relative_to(MOD / 'Assets').as_posix().encode('ascii')
    # Retain skeleton/controller nodes and weapon meshes, discard donor bodies,
    # hats and other clothing. Their names are specific to the source assets.
    weapons = {b'egyptian_AX_Primary', b'egyptian_AX_PSecondary',
               b'BIP R Hand', b'Warrior_Club', b'red_rifle_IK_driver',
               b'Swordsman_Sword', b'Swordsman_Sword01',
               b'Maceman_Mace Handle', b'Maceman_Ball and Chain',
               b'Rifle_Springfield', b'AK47_Marine', b'CLIP_Left_Hand', b'CLIP_rifle',
               b'OromoWarriorGun_Blue', b'OromoWarriorGun_Blue_FALL'}
    for node in nodes:
        for child in list(node.children):
            if isinstance(child, (N.NiTriShape, N.NiTriStrips)):
                # The maceman's chain and ball are themselves skinned; retain
                # their bone weights along with the animated weapon nodes.
                if node.name not in weapons:
                    node.remove_child(child)
    root.add_child(body)


def make_model(assets, unit, source, variant, out):
    data = N.Data()
    data.read(io.BytesIO(assets.read(source)))
    if unit == 'SLAVE':
        for node in data.blocks:
            if isinstance(node, N.NiNode) and node.name == b'Warrior_Club':
                for child in list(node.children):
                    if isinstance(child, (N.NiTriShape, N.NiTriStrips)):
                        node.remove_child(child)
    else:
        use_slave_body(assets, data, out)
    for block in data.roots[0].tree():
        if isinstance(block, N.NiMaterialProperty):
            # Low shine and varied dusty cloth colors, without changing team
            # flags or altering the game's shared textures.
            tint = (0.84, 0.79, 0.70) if variant == 'A' else (0.68, 0.73, 0.65)
            for c, factor in zip(('r', 'g', 'b'), tint):
                setattr(block.diffuse_color, c, getattr(block.diffuse_color, c) * factor)
                setattr(block.specular_color, c, 0.03)
            block.glossiness = 2
        if isinstance(block, N.NiSourceTexture) and block.file_name:
            filename = block.file_name.decode('latin-1').replace('\\', '/')
            if filename.startswith('Art/Units/SlaveUnits/'):
                continue
            if Path(filename).name.lower() == 'teamcolor.bmp':
                continue  # engine-generated texture, never substitute a DDS.
            target = out / Path(filename).name
            if not target.is_file():
                target.write_bytes(assets.texture(filename, source))
            block.file_name = target.relative_to(MOD / 'Assets').as_posix().encode('ascii')
    target = out / ('slave_' + variant.lower() + '.nif')
    with target.open('wb') as f:
        data.write(f)
    return target.relative_to(MOD / 'Assets').as_posix()


def field(block, name, value):
    return re.sub('<' + name + r'(?:\s*/>|>.*?</' + name + '>)',
                  lambda _: '<' + name + '>' + str(value) + '</' + name + '>', block, count=1, flags=re.S)


def apply_unit_visuals():
    p = MOD / 'Assets/XML/Units/CIV4UnitInfos.xml'
    text = p.read_text(encoding='utf-8')
    tier_types = {'UNIT_' + t[0] for t in TIERS}
    def patch(match):
        block = match.group(0)
        unit = re.search(r'<Type>([^<]+)</Type>', block).group(1)
        if unit not in tier_types:
            return block
        groups = '''<UnitMeshGroups>
                <iGroupSize>5</iGroupSize>
                <fMaxSpeed>1.75</fMaxSpeed>
                <fPadTime>1</fPadTime>
                <iMeleeWaveSize>5</iMeleeWaveSize>
                <iRangedWaveSize>0</iRangedWaveSize>
                <UnitMeshGroup><iRequired>3</iRequired><EarlyArtDefineTag>ART_DEF_%s_A</EarlyArtDefineTag></UnitMeshGroup>
                <UnitMeshGroup><iRequired>2</iRequired><EarlyArtDefineTag>ART_DEF_%s_B</EarlyArtDefineTag></UnitMeshGroup>
            </UnitMeshGroups>''' % (unit, unit)
        block = re.sub(r'<UnitMeshGroups>.*?</UnitMeshGroups>', lambda _: groups, block, flags=re.S)
        return field(block, 'FormationType', 'FORMATION_TYPE_SLAVE_IRREGULAR')
    p.write_text(re.sub(r'<UnitInfo>.*?</UnitInfo>', patch, text, flags=re.S), encoding='utf-8')


def main():
    global N
    from pyffi.formats.nif import NifFormat as N
    assets = Assets()
    path = MOD / 'Assets/XML/Art/CIV4ArtDefines_Unit.xml'
    art = path.read_text(encoding='utf-8')
    templates = {re.search(r'<Type>([^<]+)</Type>', b).group(1): b
                 for b in re.findall(r'<UnitArtInfo>.*?</UnitArtInfo>', art, re.S)}
    for unit, source, kfm, template, firearm in TIERS:
        out = ART / unit
        out.mkdir(parents=True, exist_ok=True)
        if kfm == 'LOCAL':
            animation_folder = GAME / 'Mods/American Revolution/Assets/Art/Units/Militia'
            for f in animation_folder.iterdir():
                if f.suffix.lower() in ('.kfm', '.kf'):
                    shutil.copyfile(f, out / f.name)
            kfm = (out / 'Browncoat.kfm').relative_to(MOD / 'Assets').as_posix()
        for variant in ('A', 'B'):
            model = make_model(assets, unit, source, variant, out)
            definition = templates['ART_DEF_UNIT_' + template]
            type_name = 'ART_DEF_UNIT_' + unit + '_' + variant
            definition = field(definition, 'Type', type_name)
            definition = field(definition, 'NIF', model)
            definition = field(definition, 'SHADERNIF', model)
            definition = field(definition, 'KFM', kfm)
            scale = float(re.search(r'<fScale>([^<]+)</fScale>', definition).group(1))
            definition = field(definition, 'fScale', round(scale * (0.96 if variant == 'A' else 1.04), 5))
            definition = field(definition, 'bActAsRanged', int(firearm))
            if type_name in templates:
                art = art.replace(templates[type_name], definition, 1)
            else:
                art = art.replace('</UnitArtInfos>', '\t\t' + definition + '\n\t</UnitArtInfos>', 1)
        if unit == 'SLAVE_MUSKETMAN':
            # KFM's relative reference must also resolve inside the mod.
            shutil.copyfile(out / 'slave_a.nif', out / 'Browncoat.nif')
        print('Built', unit)
    path.write_text(art, encoding='utf-8')
    # Retain all standard formations and add corresponding irregular variants.
    formation_path = MOD / 'Assets/XML/Units/CIV4FormationInfos.xml'
    formations = (BTS / 'Assets/XML/Units/CIV4FormationInfos.xml').read_text()
    additions = []
    for block in re.findall(r'<UnitFormation>.*?</UnitFormation>', formations, re.S):
        if '<FormationType>FORMATION_TYPE_DEFAULT</FormationType>' not in block:
            continue
        block = block.replace('FORMATION_TYPE_DEFAULT', 'FORMATION_TYPE_SLAVE_IRREGULAR')
        block = re.sub(r'<Name>(.*?)</Name>', r'<Name>SLAVE \1</Name>', block)
        position = [0]
        def scatter(match):
            position[0] += 1
            index = position[0]
            b = match.group(0)
            if '<UnitEntryType>UNIT</UnitEntryType>' not in b:
                return b
            for axis, offset in (('x', 0.16 * math.sin(index * 2.3)), ('y', 0.18 * math.cos(index * 1.7))):
                value = float(re.search('<' + axis + r'>([^<]+)</' + axis + '>', b).group(1))
                b = field(b, axis, round(value * 1.12 + offset, 6))
            b = field(b, 'DirVariation', 0.65)
            return b
        block = re.sub(r'<UnitEntry>.*?</UnitEntry>', scatter, block, flags=re.S)
        additions.append(block)
    formations = formations.replace('</UnitFormations>', '\n'.join(additions) + '\n</UnitFormations>')
    formation_path.write_text(formations, encoding='utf-8')
    shutil.copyfile(BTS / 'Assets/XML/Units/Civ4FormationSchema.xml', formation_path.with_name('Civ4FormationSchema.xml'))
    apply_unit_visuals()
    shutil.copyfile(DOC / 'LICENSE.md', ART / 'Dawn-of-Civilization-LICENSE.md')
    shutil.copyfile(DOC / 'Credits.txt', ART / 'Dawn-of-Civilization-Credits.txt')
    (ART / 'NOTICE.txt').write_text('Slave unit art: modified Firaxis Civilization IV / Warlords / Beyond the Sword models, plus the Armed Pioneer from Dawn of Civilization.\nRFC MP Plus rebinds the unarmed slave body to each weapon rig and adds material variants and irregular formations.\nSee the accompanying Dawn of Civilization license and contributor credits.\n', encoding='utf-8')
    print('Updated unit art, mesh groups and', len(additions), 'irregular formation definitions.')
    # Reapply the slave-specific buttons after cloning regular unit templates.
    from build_slave_icons import main as build_icons
    build_icons()


if __name__ == '__main__':
    main()
