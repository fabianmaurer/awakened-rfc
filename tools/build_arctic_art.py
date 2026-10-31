"""Build snowy variants of installed Civ4 art; run with .venv-art Python.

Uses the same read-only local game asset source as build_slave_art.py.
The variants are derivative game assets for use with Civilization IV.
"""
from pathlib import Path
import io
import hashlib
import math
import random
import re
import struct
import sys
import time

if not hasattr(time, 'clock'):
    time.clock = time.perf_counter
from PIL import Image, ImageDraw
from pyffi.formats.nif import NifFormat
from build_slave_art import Assets, MOD


def cold_texture(data, path, blue=False):
    picture = Image.open(io.BytesIO(data)).convert('RGBA')
    pixels = []
    for r, g, b, a in picture.getdata():
        light = (r + g + b) / 3.0
        if light < 24:
            pixels.append((r, g, b, a))
        else:
            pixels.append((int(130 + light*.34), int(175 + light*.26),
                           int(205 + light*.18), a))
    picture.putdata(pixels)
    picture.save(path, pixel_format='DXT5')


def eskimo_banner():
    """Original angular polar seal; white alpha decal uses the player color."""
    path = MOD/'Assets/Art/Interface/TeamColor/FlagDECAL_Eskimo.dds'
    path.parent.mkdir(parents=True, exist_ok=True)
    # Supersampling keeps the thin carved strokes legible on unit flags.
    size = 512
    flag = Image.new('RGBA', (size,size), (255,255,255,0))
    draw = ImageDraw.Draw(flag)
    def line(points, width=4):
        draw.line([(int(x*4),int(y*4)) for x,y in points],
                  fill=(255,255,255,255),width=width*4,joint='curve')
    # Broken octagonal halo and an ascending mountain/gateway rune.
    line([(43,18),(64,9),(85,18)],3)
    line([(101,34),(113,55),(113,74),(101,95)],3)
    line([(85,110),(64,119),(43,110)],3)
    line([(27,95),(15,74),(15,55),(27,34)],3)
    line([(34,88),(64,30),(94,88)],5)
    line([(47,64),(64,76),(81,64)],4)
    line([(64,31),(64,101)],4)
    line([(48,91),(64,101),(80,91)],4)
    for x,y in [(31,25),(97,25),(31,103),(97,103)]:
        line([(x,y-5),(x+4,y),(x,y+5),(x-4,y),(x,y-5)],2)
    flag.resize((128,128),Image.Resampling.LANCZOS).save(path,pixel_format='DXT5')


def icy_building_art(assets):
    """Generate render-only copies of default buildings, with no gameplay changes."""
    import xml.etree.ElementTree as ET
    assets_dir = MOD/'Assets'
    folder = assets_dir/'Art/Arctic/Buildings'
    folder.mkdir(parents=True,exist_ok=True)
    def read(relative):
        p=assets_dir/relative
        if p.is_file(): return p.read_bytes()
        for prefix in ('bts','warlords','base'):
            p=assets.roots[prefix]/relative
            if p.is_file(): return p.read_bytes()
        return assets.read('base:'+relative)
    art_path=assets_dir/'XML/Art/CIV4ArtDefines_Building.xml'
    art_text=art_path.read_text(encoding='utf-8')
    # Regenerate our own entries without rewriting unrelated XML formatting.
    art_text=re.sub(r'<BuildingArtInfo>\s*<Type>ART_DEF_BUILDING_ICY_[^<]*</Type>.*?</BuildingArtInfo>',
                    '',art_text,flags=re.S)
    building_path=assets_dir/'XML/Buildings/CIV4BuildingInfos.xml'
    building_text=building_path.read_text(encoding='utf-8')
    building_text=re.sub(r'<BuildingInfo>(?:(?!</BuildingInfo>).)*?<Type>[^<]*_ARCTIC_DISPLAY</Type>.*?</BuildingInfo>',
                         '',building_text,flags=re.S)
    art_blocks={ET.fromstring(b).findtext('Type'):b for b in
                re.findall(r'<BuildingArtInfo>.*?</BuildingArtInfo>',art_text,re.S)}
    art_entries=[]; building_entries=[]; variants={}; textures={}; missing=[]; unresolved=set()
    for block in re.findall(r'<BuildingInfo>.*?</BuildingInfo>',building_text,re.S):
        info=ET.fromstring(block)
        if info.findtext('BuildingClass')=='BUILDINGCLASS_PALACE': continue
        art_tag=info.findtext('ArtDefineTag')
        if art_tag not in art_blocks: continue
        art=ET.fromstring(art_blocks[art_tag])
        source=art.findtext('NIF') or ''
        # Existing custom Arctic art stays intact.
        if not source.lower().startswith('art/structures/buildings/'): continue
        if art_tag not in variants:
            try: data=read(source)
            except FileNotFoundError:
                missing.append(source); continue
            model_dir=folder/art_tag.removeprefix('ART_DEF_BUILDING_').lower()
            model_dir.mkdir(exist_ok=True)
            # Civ4 NIFs store texture paths as length-prefixed strings. Change
            # those strings directly, preserving every mesh/controller byte.
            # Some shipped legacy meshes cannot be round-tripped by PyFFI.
            replacements=[]
            for match in re.finditer(rb'[ -~]+\.(?:dds|tga|bmp)',data,re.I):
                start,end=match.span()
                if start<4 or struct.unpack('<I',data[start-4:start])[0] != end-start:
                    continue
                original=match[0].decode('ascii').replace('\\','/').lstrip('/')
                if original:
                    content=None
                    for candidate in [(Path(source).parent/Path(original).name).as_posix(),original]:
                        try: content=read(candidate); break
                        except FileNotFoundError: pass
                    if content is None:
                        try: content=assets.texture(original,'base:'+source)
                        except FileNotFoundError:
                            # Retain dangling references already in stock art.
                            unresolved.add((source,original)); continue
                    name=Path(original).name.lower()
                    preserve=any(word in name for word in
                        ('shadow','shad','gloss','normal','bump','smoke','fire','flame','glow'))
                    key=hashlib.sha256(content+bytes([preserve])).hexdigest()[:20]
                    texture_name=key+Path(name).suffix
                    if key not in textures:
                        target=folder/texture_name
                        if preserve: target.write_bytes(content)
                        else: cold_texture(content,target)
                        textures[key]=target
                    target_path=('Art/Arctic/Buildings/'+texture_name).encode('ascii')
                    replacements.append((start-4,end,struct.pack('<I',len(target_path))+target_path))
            if not replacements:
                raise ValueError('No texture references found: '+source)
            for start,end,replacement in reversed(replacements):
                data=data[:start]+replacement+data[end:]
            output=model_dir/Path(source).name
            output.write_bytes(data)
            new_tag=art_tag.replace('ART_DEF_BUILDING_','ART_DEF_BUILDING_ICY_',1)
            entry=art_blocks[art_tag].replace('<Type>'+art_tag+'</Type>',
                                             '<Type>'+new_tag+'</Type>')
            entry=re.sub(r'<NIF>.*?</NIF>',
                         '<NIF>'+output.relative_to(assets_dir).as_posix()+'</NIF>',entry)
            art_entries.append(entry); variants[art_tag]=new_tag
        building_type=info.findtext('Type')
        entry=block.replace('<Type>'+building_type+'</Type>',
                            '<Type>'+building_type+'_ARCTIC_DISPLAY</Type>')
        entry=entry.replace('<ArtDefineTag>'+art_tag+'</ArtDefineTag>',
                            '<ArtDefineTag>'+variants[art_tag]+'</ArtDefineTag>')
        for tag in ('iCost','iAdvancedStartCost'):
            entry=re.sub('<'+tag+r'>.*?</'+tag+'>','<'+tag+'>-1</'+tag+'>',entry)
        building_entries.append(entry)
    if missing: raise FileNotFoundError('Missing building models: '+', '.join(sorted(set(missing))))
    art_text=art_text.replace('</BuildingArtInfos>','\n'.join(art_entries)+'\n</BuildingArtInfos>')
    building_text=building_text.replace('</BuildingInfos>','\n'.join(building_entries)+'\n</BuildingInfos>')
    art_path.write_text(art_text,encoding='utf-8')
    building_path.write_text(building_text,encoding='utf-8')
    print('Icy building art:',len(art_entries),'models,',len(building_entries),'display entries,',len(textures),'textures')
    for source,texture in sorted(unresolved): print('Unchanged stock reference:',source,texture)
    icy_city_walls(assets)


def icy_city_walls(assets):
    """WallBuilder uses segment files independently of building model art."""
    import xml.etree.ElementTree as ET
    folder=MOD/'Assets/Art/Arctic/CityWalls'
    folder.mkdir(parents=True,exist_ok=True)
    sources=sorted(k for k in assets.packed
                   if k.startswith('art/structures/buildings/walls/') and
                   k.endswith('.nif') and not k.endswith('/walls.nif'))
    for source in sources:
        model=model_variant(assets,source,None,'Art/Arctic/CityWalls')
        with (folder/Path(source).name).open('wb') as out: model.write(out)
    path=MOD/'Assets/XML/Buildings/CIV4CityLSystem.xml'
    text=path.read_text(encoding='utf-8')
    pattern=r'<ArtRef Name="building:LSYSTEM_WALLS">.*?</ArtRef>'
    # Remove only the Arctic entries made by this generator.
    text=re.sub(pattern,lambda m:'' if 'Art/Arctic/CityWalls/' in m[0] else m[0],text,flags=re.S)
    template=re.search(pattern,text,re.S)[0]
    root=ET.parse(MOD/'Assets/XML/GlobalTypes.xml').getroot()
    styles=[e.text for e in root.iter() if e.tag.split('}')[-1]=='ArtStyleType'
            and e.text!='ARTSTYLE_ARCTIC']
    assert styles
    ordinary=re.sub(r'\s*<Attribute Class="ArtStyle">.*?</Attribute>','',template,flags=re.S)
    ordinary=ordinary.replace('</ArtRef>',
        '<Attribute Class="ArtStyle">'+','.join(styles)+'</Attribute>\n\t\t</ArtRef>')
    arctic=re.sub(r'\s*<Attribute Class="ArtStyle">.*?</Attribute>','',template,flags=re.S)
    variants=[]
    # WallBuilder's scalar paths go directly to the scene loader rather than
    # through ordinary building-art lookup. Include the mod-relative root.
    wall_root='Mods/Awakened RFC/Assets/Art/Arctic/CityWalls/'
    for era,suffix in [('ERA_ANCIENT,ERA_CLASSICAL','an'),
                       ('ERA_MEDIEVAL,ERA_RENAISSANCE,ERA_INDUSTRIAL,ERA_MODERN,ERA_FUTURE','med')]:
        entry=arctic.replace('</ArtRef>',
            '<Attribute Class="ArtStyle">ARTSTYLE_ARCTIC</Attribute>\n'
            '\t\t\t<Attribute Class="Era">'+era+'</Attribute>\n'
            '\t\t\t<Attribute Class="Scalar">szPostArtFile:'+wall_root+'post01_eu_'+suffix+'.nif</Attribute>\n'
            '\t\t\t<Attribute Class="Scalar">szWallArtFile:'+wall_root+'wall%1_eu_'+suffix+'.nif</Attribute>\n'
            '\t\t</ArtRef>')
        variants.append(entry)
    text=text.replace(template,ordinary+'\n\t\t'+'\n\t\t'.join(variants),1)
    path.write_text(text,encoding='utf-8')
    print('Icy city wall pieces:',len(sources))


def model_variant(assets, source, output, texture_folder, glowing=False, recolor=True):
    model = NifFormat.Data()
    model.read(io.BytesIO(assets.read('base:' + source)))
    target = MOD / 'Assets' / texture_folder
    target.mkdir(parents=True, exist_ok=True)
    for block in model.get_global_iterator():
        if isinstance(block, NifFormat.NiSourceTexture) and block.file_name:
            original = bytes(block.file_name).decode('latin-1').replace('\\', '/')
            name = Path(original).name.lower()
            is_shadow = 'shadow' in name or 'shad' in name
            try:
                # A packed model's sibling texture takes precedence over a
                # same-named loose file (Deer.dds also names a resource button).
                sibling = (Path(source).parent / Path(original).name).as_posix()
                try:
                    content = assets.read('base:' + sibling)
                except FileNotFoundError:
                    content = assets.texture(original, 'base:' + source)
            except FileNotFoundError:
                continue
            # Shadow textures still need local paths in relocated models.
            # Preserve their original alpha and color instead of icing them.
            if recolor and not is_shadow:
                cold_texture(content, target / name)
            else:
                (target / name).write_bytes(content)
            block.file_name = (texture_folder + '/' + name).encode('ascii')
        if glowing and isinstance(block, NifFormat.NiMaterialProperty):
            block.emissive_color.r = .06
            block.emissive_color.g = .22
            block.emissive_color.b = .55
            block.specular_color.r = .3
            block.specular_color.g = .65
            block.specular_color.b = 1.0
            block.glossiness = 45
    return model


def mesh(name, vertices, triangles, color, texture=None, emissive=False, uvs=None):
    N = NifFormat
    shape = N.NiTriShape()
    shape.name = name.encode('ascii')
    shape.flags = 14
    shape.data = N.NiTriShapeData()
    data = shape.data
    data.num_vertices = len(vertices)
    data.has_vertices = True
    data.vertices.update_size()
    for vertex, value in zip(data.vertices, vertices):
        vertex.x, vertex.y, vertex.z = value
    data.set_triangles(triangles)
    data.has_normals = True
    data.normals.update_size()
    normals = [[0.0,0.0,0.0] for _ in vertices]
    for a,b,c in triangles:
        u=[vertices[b][i]-vertices[a][i] for i in range(3)]
        v=[vertices[c][i]-vertices[a][i] for i in range(3)]
        cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        for index in (a,b,c):
            for axis in range(3): normals[index][axis] += cross[axis]
    for target,value in zip(data.normals,normals):
        length=math.sqrt(sum(n*n for n in value)) or 1
        target.x,target.y,target.z=(n/length for n in value)
    data.update_center_radius()
    material = N.NiMaterialProperty()
    material.name = b'Arctic ice'
    material.ambient_color.r, material.ambient_color.g, material.ambient_color.b = color
    material.diffuse_color.r, material.diffuse_color.g, material.diffuse_color.b = color
    material.specular_color.r, material.specular_color.g, material.specular_color.b = (.35, .65, .9)
    material.glossiness = 30
    material.alpha = 1
    if emissive:
        material.emissive_color.r, material.emissive_color.g, material.emissive_color.b = color
    shape.add_property(material)
    if texture:
        data.num_uv_sets = 1
        data.uv_sets.update_size()
        for uv, value in zip(data.uv_sets[0], uvs):
            uv.u, uv.v = value
        prop = N.NiTexturingProperty()
        prop.has_base_texture = True
        prop.base_texture.source = N.NiSourceTexture()
        prop.base_texture.source.use_external = 1
        prop.base_texture.source.file_name = texture.encode('ascii')
        prop.base_texture.clamp_mode = 3
        prop.base_texture.filter_mode = 2
        shape.add_property(prop)
    return shape


def igloo(x, y, radius=19, angle=0):
    N = NifFormat
    house = N.NiNode()
    house.name = b'Igloo'
    house.translation.x, house.translation.y = x, y
    house.flags = 14
    house.rotation.m_11 = house.rotation.m_22 = math.cos(angle)
    house.rotation.m_12 = math.sin(angle)
    house.rotation.m_21 = -math.sin(angle)
    vertices, triangles, uv = [], [], []
    rings, segments = 7, 24
    for row in range(rings+1):
        theta = (math.pi/2) * row/rings
        for col in range(segments+1):
            phi = 2*math.pi*col/segments
            vertices.append((radius*math.cos(theta)*math.cos(phi),
                             radius*math.cos(theta)*math.sin(phi),
                             radius*.85*math.sin(theta)))
            uv.append((col/segments, row/rings))
    for row in range(rings):
        for col in range(segments):
            a = row*(segments+1)+col
            triangles.extend([(a,a+1,a+segments+2),(a,a+segments+2,a+segments+1)])
    house.add_child(mesh('Snow blocks', vertices, triangles, (.85,.91,.97),
        'Art/Structures/Cities/Arctic/igloo_blocks.dds', uvs=uv))
    # Low arched entrance with a dark recess rather than a painted doorway.
    vertices, triangles = [], []
    for depth in (-radius*.65, -radius*1.45):
        for step in range(13):
            angle = math.pi*step/12
            vertices.append((radius*.31*math.cos(angle),depth,radius*.4*math.sin(angle)))
    for i in range(12):
        triangles.extend([(i,i+14,i+13),(i,i+1,i+14)])
    house.add_child(mesh('Entrance arch', vertices, triangles, (.67,.79,.87)))
    opening=[(0,-radius*1.455,0)]+[(radius*.26*math.cos(math.pi*i/12),
                -radius*1.455,radius*.34*math.sin(math.pi*i/12)) for i in range(13)]
    house.add_child(mesh('Entrance shadow',opening,[(0,i+1,i+2) for i in range(12)],(.025,.07,.11)))
    # A thin lower ice course separates the dome from bright terrain snow.
    vertices = []
    for z in (.15,1.25):
        for i in range(segments):
            phi=2*math.pi*i/segments
            vertices.append(((radius+.3)*math.cos(phi),(radius+.3)*math.sin(phi),z))
    triangles=[]
    for i in range(segments):
        j=(i+1)%segments
        triangles.extend([(i,j,j+segments),(i,j+segments,i+segments)])
    house.add_child(mesh('Blue-grey lower ice course',vertices,triangles,(.49,.64,.73)))
    return house


def hunting_grounds_art(assets):
    N = NifFormat
    base = MOD / 'Assets/Art/Arctic'
    # Static resource deer keep their original rig and bind pose. Enlarging the
    # complete scene preserves their proportions relative to the hunting camp.
    camp = model_variant(assets,'art/structures/improvements/camp/camp.nif',None,
                         'Art/Arctic/HuntingGrounds', recolor=False)
    deer = model_variant(assets,'art/terrain/resources/deer/deer.nif',None,
                         'Art/Arctic/HuntingGrounds',recolor=False)
    # Keep the original atlas and alpha; shift brown fur toward a winter
    # grey-beige coat while preserving the dark muzzle, legs and fine details.
    coat_path = base / 'HuntingGrounds/deer.dds'
    coat = Image.open(coat_path).convert('RGBA')
    pixels = []
    for r, g, b, alpha in coat.getdata():
        light = .299*r + .587*g + .114*b
        if alpha and light > 55 and r > g*1.04 and r-b > 12:
            target = (min(255, int(light*.65+80)),
                      min(255, int(light*.66+78)),
                      min(255, int(light*.68+72)))
            r, g, b = target
        pixels.append((r, g, b, alpha))
    coat.putdata(pixels)
    coat.save(coat_path, pixel_format='DXT5')
    # The shed is permanent; wildlife is a separate, worked-tile graphic.
    with (base/'HuntingGrounds/hunting_grounds.nif').open('wb') as out:
        camp.write(out)
    import copy
    animals = []
    names = (b'Deer_Buck01', b'Deer_Buck02', b'Deer_Doe')
    for name in names:
        animal = next(n for n in deer.get_global_iterator()
                      if isinstance(n, N.NiTriShape) and n.name == name)
        transform = animal.get_transform(deer.roots[0])
        vertices, normals = animal.get_skin_deformation()
        rotation = transform.get_matrix_33()
        for target, vertex in zip(animal.data.vertices, vertices):
            point = vertex * transform
            target.x, target.y, target.z = point.x, point.y, point.z
        for target, normal in zip(animal.data.normals, normals):
            point = normal * rotation
            target.x, target.y, target.z = point.x, point.y, point.z
        animal.skin_instance = None
        animal.controller = None
        identity = N.Matrix44()
        identity.set_identity()
        animal.set_transform(identity)
        # Enlarge each animal around its own feet, keeping herd placement fixed.
        center_x = (min(v.x for v in animal.data.vertices) + max(v.x for v in animal.data.vertices)) / 2
        center_y = (min(v.y for v in animal.data.vertices) + max(v.y for v in animal.data.vertices)) / 2
        floor_z = min(v.z for v in animal.data.vertices)
        for vertex in animal.data.vertices:
            vertex.x = center_x + (vertex.x-center_x)*1.4
            vertex.y = center_y + (vertex.y-center_y)*1.4
            vertex.z = floor_z + (vertex.z-floor_z)*1.4
        targets = ((62,-45), (-48,-22), (5,47))
        target_x, target_y = targets[len(animals)]
        animal.translation.x = (target_x-12)/1.6-center_x
        animal.translation.y = (target_y-8)/1.6-center_y
        animal.data.update_center_radius()
        animals.append(animal)
    # Round-trip the baked mesh: PyFFI structs cannot use Python deepcopy.
    deer.roots = [animals[2]]
    buffer = io.BytesIO()
    deer.write(buffer)
    clone = N.Data()
    clone.read(io.BytesIO(buffer.getvalue()))
    fourth = clone.roots[0]
    fourth.name = b'Fourth winter reindeer'
    fourth.translation.x -= 63/1.6
    fourth.translation.y += 18/1.6
    animals.append(fourth)
    for count in range(1,5):
        herd = N.NiNode()
        herd.name = ('Worked hunting herd %d' % count).encode('ascii')
        herd.flags = 14
        herd.scale = 1.6
        herd.translation.x, herd.translation.y = 12,8
        for animal in animals[:count]:
            herd.add_child(animal)
        deer.roots = [herd]
        with (base/('HuntingGrounds/herd%d.nif' % count)).open('wb') as out:
            deer.write(out)
    render_feature_templates([
        ('FEATURE_HUNTING_HERD_%d' % count, 'TXT_KEY_HUNTING_GROUNDS',
         'TXT_KEY_HUNTING_GROUNDS_PEDIA',
         'Art/Arctic/HuntingGrounds/herd%d.nif' % count)
        for count in range(1,5)])


def archive_gate():
    """Carved stone portal, aged metal double doors and luminous inlays."""
    N = NifFormat
    gate = N.NiNode()
    gate.name = b'Ancient advanced civilization bunker doors'
    gate.flags = 14

    def xyz(u, v, z):
        # Stay below the mound's crest and recess the portal into its entrance.
        u *= .8
        v = v*.65 - 2
        z *= .65
        return (-3 + .8*u - .6*v, -9 - .6*u - .8*v, z)

    def gate_mesh(name, vertices, triangles, color, **kwargs):
        # The outward entrance basis is left-handed; reverse face winding.
        return mesh(name, vertices, [(a,c,b) for a,b,c in triangles], color, **kwargs)

    def box(name, u0, u1, v0, v1, z0, z1, color, emissive=False):
        vertices = [xyz(u, v, z) for z in (z0, z1)
                    for v in (v0, v1) for u in (u0, u1)]
        triangles = [(0,2,3),(0,3,1),(4,5,7),(4,7,6),
                     (0,1,5),(0,5,4),(2,6,7),(2,7,3),
                     (0,4,6),(0,6,2),(1,3,7),(1,7,5)]
        gate.add_child(gate_mesh(name, vertices, triangles, color, emissive=emissive))

    stone = (.24, .31, .34)
    metal = (.15, .26, .28)
    brass = (.55, .43, .23)
    blue = (.08, .55, 1.0)
    box('Broad stone threshold', -13,13, -3,5, -.5,1, stone)
    for side in (-1,1):
        center = side*10.5
        for level in range(3):
            shade = tuple(c + level*.025 for c in stone)
            box('Carved stone pier', center-2,center+2, -2,3,
                1+level*7, 7.8+level*7, shade)
        for height in (1.5,8,15,21):
            box('Aged brass pier band',center-2.2,center+2.2, 3,3.35,
                height,height+.45,brass)
        box('Recessed ancient metal door', side*4.15-3.95,side*4.15+3.95,
            -.8,1, 1,21, metal)
        # Nested angular lines resemble inscriptions rather than mine timbers.
        for height in (5,11,17):
            u = side*4.2
            vertices = [xyz(u,1.1,height+1.8),xyz(u+1.5,1.1,height),
                        xyz(u,1.1,height-1.8),xyz(u-1.5,1.1,height),
                        xyz(u,1.1,height+1.25),xyz(u+.95,1.1,height),
                        xyz(u,1.1,height-1.25),xyz(u-.95,1.1,height)]
            triangles = []
            for i in range(4):
                j=(i+1)%4
                triangles.extend([(i,j,4+j),(i,4+j,4+i)])
            gate.add_child(gate_mesh('Luminous angular door inscription',vertices,
                                triangles,blue,emissive=True))
        box('Door bronze edge',side*8.15-.18,side*8.15+.18,
            1.05,1.25, 1,21,brass)
    box('Stepped lintel', -13,13, -2,3, 21,24, stone)
    box('Second ancient lintel course', -10,10, -1.5,2.7, 24,26, stone)
    box('Upper portal keystone', -6,6, -1,2.5, 26,28, stone)
    box('Lintel bronze inlay', -11,11, 3.05,3.4, 22,22.55, brass)
    box('Blue door seam', -.12,.12, 1.05,1.2, 1,21, blue,emissive=True)
    # An eight-sided seal joins both leaves, with a bright blue central diamond.
    vertices = [xyz(math.cos(i*math.pi/4)*2.5,1.5,
                    11+math.sin(i*math.pi/4)*2.5) for i in range(8)]
    gate.add_child(gate_mesh('Ancient octagonal door seal',vertices,
                        [(0,i,i+1) for i in range(1,7)],brass))
    vertices = [xyz(u,1.6,z) for u,z in [(0,12.5),(1.25,11),(0,9.5),(-1.25,11)]]
    gate.add_child(gate_mesh('Luminous door seal core',vertices,
                        [(0,1,2),(0,2,3)],blue,emissive=True))
    return gate


def deep_archive_art(assets):
    N = NifFormat
    base = MOD / 'Assets/Art/Arctic'
    archive = model_variant(assets, 'art/structures/improvements/mine/mine.nif', None,
                            'Art/Arctic/DeepArchive', glowing=True)
    for node in list(archive.get_global_iterator()):
        if isinstance(node, N.NiNode):
            for child in list(node.children):
                # Mine:0 is the complete wooden track/trestle assembly.
                if child is not None and getattr(child, 'name', b'') == b'Mine:0':
                    node.remove_child(child)
        if isinstance(node, N.NiTriShape) and node.name == b'Mine:1':
            cart = set()
            for bone, weights in zip(node.skin_instance.bones,
                                     node.skin_instance.data.bone_list):
                if bone.name == b'bone_mine_cart':
                    cart.update(w.index for w in weights.vertex_weights if w.weight > 0)
            triangles = [t for t in node.data.get_triangles()
                         if not any(v in cart for v in t)]
            # Weld positions across UV seams to separate the chimney and
            # timber entrance from the rock mound, without cutting its surface.
            keys = [tuple(round(getattr(v, axis), 3) for axis in ('x','y','z'))
                    for v in node.data.vertices]
            remaining = set(range(len(triangles)))
            keep = []
            while remaining:
                component = {remaining.pop()}
                points = {keys[v] for v in triangles[next(iter(component))]}
                while True:
                    more = {i for i in remaining
                            if points.intersection(keys[v] for v in triangles[i])}
                    if not more:
                        break
                    for i in more:
                        points.update(keys[v] for v in triangles[i])
                    component.update(more)
                    remaining -= more
                low = [min(v[i] for v in points) for i in range(3)]
                high = [max(v[i] for v in points) for i in range(3)]
                chimney = low[0] < -40 and high[2] > 24
                entrance = (low[0] >= -11 and high[0] <= 5 and
                            low[1] >= -16 and high[1] <= -2 and
                            low[2] >= -1 and 15 < high[2] <= 19)
                if not chimney and not entrance:
                    keep.extend(triangles[i] for i in sorted(component))
            triangles = keep
            # Bake the original bind pose so no stale GPU skin partitions can
            # keep drawing the removed cart. This improvement has no KFM.
            vertices, normals = node.get_skin_deformation()
            for target, source in zip(node.data.vertices, vertices):
                target.x, target.y, target.z = source.x, source.y, source.z
            for target, source in zip(node.data.normals, normals):
                target.x, target.y, target.z = source.x, source.y, source.z
            node.skin_instance = None
            node.data.set_triangles(triangles)
            node.data.update_center_radius()
    archive.roots[0].add_child(archive_gate())
    for x,y,h in [(-42,-52,35),(35,-48,28),(40,30,24)]:
        vertices=[(x-3,y-3,0),(x+3,y-3,0),(x+3,y+3,0),(x-3,y+3,0),(x,y,h)]
        archive.roots[0].add_child(mesh('Archive blue crystal',vertices,
            [(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1),(3,1,0)],(.08,.5,1),emissive=True))
    # Two independent promotion-ready sparkles, offset in time and position.
    # The original particle behavior remains recognizable but more pronounced.
    for layer in range(2):
        glow = model_variant(assets, 'art/effects/unit_promotion/fx_unit_promotion_02.nif',
                             None, 'Art/Arctic/DeepArchive', recolor=False)
        seen = set()
        for block in glow.get_global_iterator():
            if id(block) in seen:
                continue
            seen.add(id(block))
            if isinstance(block, N.NiTimeController):
                block.flags = (int(block.flags) & ~0x86) | 0x08
                block.phase = -layer*.75
            if isinstance(block, N.NiPSysEmitterCtlr):
                block.visibility_interpolator.data = None
                block.visibility_interpolator.bool_value = True
                if block.interpolator.float_value >= 0:
                    block.interpolator.float_value *= 1.35
                if block.interpolator.data:
                    for key in block.interpolator.data.data.keys:
                        key.value *= 1.35
            if isinstance(block, N.NiColorData):
                for key in block.data.keys:
                    key.value.r, key.value.g, key.value.b = .06+layer*.04, .36+layer*.1, 1.0
        glow_root = glow.roots[0]
        glow_root.name = ('Archive looping blue promotion light %d' % layer).encode('ascii')
        glow_root.scale *= .58-layer*.06
        glow_root.translation.x += -5+layer*4
        glow_root.translation.y += -13+layer*2
        glow_root.translation.z += 12
        archive.roots[0].add_child(glow_root)
    with (base/'DeepArchive/deep_archive.nif').open('wb') as out:
        archive.write(out)


def special_art(assets):
    N = NifFormat
    hunting_grounds_art(assets)
    deep_archive_art(assets)
    igloo_art(assets)
    citydir = MOD/'Assets/Art/Structures/Cities'
    for source,target in [('med_eu.nif','arctic_medieval.nif'),('mod_eu.nif','arctic_modern.nif')]:
        city=model_variant(assets,'art/structures/cities/'+source,None,
                           'Art/Structures/Cities/Arctic',glowing=False)
        with (citydir/target).open('wb') as out: city.write(out)
    arctic_settlement_art(assets)


def arctic_settlement_art(assets):
    """Cottages use PlotLSystem, independently of the city's CityLSystem."""
    import xml.etree.ElementTree as ET
    citydir = MOD/'Assets/Art/Structures/Cities'
    city = model_variant(assets, 'art/structures/cities/ren_eu.nif', None,
                         'Art/Structures/Cities/Arctic/Renaissance')
    with (citydir/'arctic_renaissance.nif').open('wb') as out:
        city.write(out)
    variants = {'an_eu.nif': 'arctic_igloos.nif',
                'med_eu.nif': 'arctic_medieval.nif',
                'ren_eu.nif': 'arctic_renaissance.nif',
                'mod_eu.nif': 'arctic_modern.nif'}
    root = ET.parse(MOD/'Assets/XML/GlobalTypes.xml').getroot()
    ordinary_styles = ','.join(e.text for e in root.iter()
        if e.tag.split('}')[-1] == 'ArtStyleType'
        and e.text not in ('ARTSTYLE_ARCTIC', 'ARTSTYLE_ALL'))
    path = MOD/'Assets/XML/Buildings/CIV4PlotLSystem.xml'
    text = path.read_text(encoding='utf-8')
    pattern = r'<ArtRef Name="art:building">.*?</ArtRef>'
    style = r'<Attribute Class="ArtStyle">(.*?)</Attribute>'
    def replace(match):
        entry = match[0]
        source = re.search(r'NIF:Art/Structures/Cities/([^:<]+)\.nif::', entry)
        if source is None or source[1]+'.nif' not in variants:
            return entry
        styles = re.search(style, entry, re.S)
        names = styles[1].split(',') if styles else ['ARTSTYLE_ALL']
        # Repeatable regeneration: recognize the ordinary half of our split.
        if 'ARTSTYLE_ARCTIC' not in names and 'ARTSTYLE_ALL' not in names:
            return entry
        ordinary = [s for s in names if s not in ('ARTSTYLE_ARCTIC', 'ARTSTYLE_ALL')]
        ordinary = ','.join(ordinary) if 'ARTSTYLE_ALL' not in names else ordinary_styles
        arctic = entry.replace(source[1]+'.nif', variants[source[1]+'.nif'])
        # Plot batching shares textures; keep the icy atlas in its own batch.
        arctic = arctic.replace('szBatchGroup:buildings_', 'szBatchGroup:arctic_buildings_')
        if styles:
            entry = re.sub(style, '<Attribute Class="ArtStyle">'+ordinary+'</Attribute>', entry)
            arctic = re.sub(style, '<Attribute Class="ArtStyle">ARTSTYLE_ARCTIC</Attribute>', arctic)
        else:
            entry = entry.replace('</ArtRef>', '<Attribute Class="ArtStyle">'+ordinary+'</Attribute>\n\t\t</ArtRef>')
            arctic = arctic.replace('</ArtRef>', '<Attribute Class="ArtStyle">ARTSTYLE_ARCTIC</Attribute>\n\t\t</ArtRef>')
        return entry+'\n\t\t'+arctic
    path.write_text(re.sub(pattern, replace, text, flags=re.S), encoding='utf-8')


def igloo_art(assets):
    N = NifFormat
    citydir = MOD/'Assets/Art/Structures/Cities'
    (citydir/'Arctic').mkdir(parents=True,exist_ok=True)
    # Blue mortar, slightly varied ice blocks and a bright snowy dome surface.
    blocks=Image.new('RGBA',(256,128),(132,159,178,255))
    draw=ImageDraw.Draw(blocks)
    for row in range(8):
        for col in range(-1,13):
            x=col*24+(12 if row%2 else 0)
            shade=198+(row*5+col*3)%25
            draw.rectangle((x+2,row*16+2,x+22,row*16+14),fill=(shade,shade+10,min(255,shade+20),255))
    blocks.save(citydir/'Arctic/igloo_blocks.dds',pixel_format='DXT5')
    ancient=N.Data()
    ancient.read(io.BytesIO(assets.read('base:art/structures/cities/an_eu.nif')))
    for node in ancient.roots[0].children:
        if not isinstance(node,N.NiNode): continue
        name=bytes(node.name).decode('ascii')
        dimensions=re.match(r'(\d+)[xX](\d+)',name)
        if dimensions is None: continue
        width,height=map(int,dimensions.groups())
        node.num_children=0
        node.children.update_size()
        # Stable local variation keeps regeneration reproducible without a
        # regular grid of identical, equally oriented entrances.
        rng=random.Random(name)
        positions=[(x,y) for x in range(width) for y in range(height)]
        rng.shuffle(positions)
        for x,y in positions[:max(1, (width*height+1)//2)]:
            node.add_child(igloo((x-(width-1)/2)*44+rng.uniform(-3,3),
                                (y-(height-1)/2)*44+rng.uniform(-3,3),
                                radius=rng.uniform(17,19), angle=rng.uniform(0,2*math.pi)))
    with (citydir/'arctic_igloos.nif').open('wb') as out: ancient.write(out)
    palace = N.Data()
    palace.version = ancient.version
    palace.user_version = ancient.user_version
    palace.header.endian_type = ancient.header.endian_type
    hall = N.NiNode()
    hall.name = b'Arctic monumental igloo palace'
    hall.flags = 14
    hall.add_child(igloo(0,0,36))
    hall.add_child(igloo(-35,13,18,angle=-.25))
    hall.add_child(igloo(35,13,18,angle=.25))
    # A smaller raised dome crowns the great hall, giving it a civic silhouette.
    crown = igloo(0,0,9)
    crown.translation.z = 29
    hall.add_child(crown)

    def block(name,x0,x1,y0,y1,z0,z1,color):
        vertices=[(x,y,z) for z in (z0,z1) for y in (y0,y1) for x in (x0,x1)]
        triangles=[(0,2,3),(0,3,1),(4,5,7),(4,7,6),(0,1,5),(0,5,4),
                   (2,6,7),(2,7,3),(0,4,6),(0,6,2),(1,3,7),(1,7,5)]
        hall.add_child(mesh(name,vertices,triangles,color))
    for i in range(3):
        block('Broad carved snow entrance steps',-15+i,15-i,
              -59+i*3,-45, -.1,i*.65+.55,(.58+i*.055,.70+i*.045,.78+i*.035))
    for side in (-1,1):
        block('Tall carved ice entrance pier',side*14-2,side*14+2,
              -42,-36,0,17,(.52,.67,.77))
        block('Snow cap on entrance pier',side*14-2.7,side*14+2.7,
              -42.6,-35.4,17,19,(.79,.87,.93))
    palace.roots=[hall]
    with (citydir/'Arctic/igloo_palace.nif').open('wb') as out:
        palace.write(out)
    arctic_city_lots(assets)
    import xml.etree.ElementTree as ET
    art_path=MOD/'Assets/XML/Art/CIV4ArtDefines_Building.xml'
    text=art_path.read_text(encoding='utf-8')
    template=re.search(r'<BuildingArtInfo>\s*<Type>ART_DEF_BUILDING_PALACE</Type>.*?</BuildingArtInfo>',text,re.S)[0]
    entry=template.replace('ART_DEF_BUILDING_PALACE','ART_DEF_BUILDING_ARCTIC_PALACE')
    entry=re.sub(r'<NIF>.*?</NIF>','<NIF>Art/Structures/Cities/Arctic/igloo_palace.nif</NIF>',entry)
    entry=re.sub(r'<fScale>.*?</fScale>','<fScale>1.0</fScale>',entry)
    pattern=r'<BuildingArtInfo>\s*<Type>ART_DEF_BUILDING_ARCTIC_PALACE</Type>.*?</BuildingArtInfo>'
    if re.search(pattern,text,re.S):
        text=re.sub(pattern,lambda m:entry,text,flags=re.S)
    else:
        text=text.replace('</BuildingArtInfos>',entry+'\n</BuildingArtInfos>')
    art_path.write_text(text,encoding='utf-8')
    # City graphics consume building types directly. Never build this art proxy.
    path=MOD/'Assets/XML/Buildings/CIV4BuildingInfos.xml'
    text=path.read_text(encoding='utf-8')
    template=next(b for b in re.findall(r'<BuildingInfo>.*?</BuildingInfo>',text,re.S)
                  if '<Type>BUILDING_PALACE</Type>' in b)
    entry=template.replace('<Type>BUILDING_PALACE</Type>',
                           '<Type>BUILDING_ARCTIC_PALACE_DISPLAY</Type>')
    entry=entry.replace('ART_DEF_BUILDING_PALACE','ART_DEF_BUILDING_ARCTIC_PALACE')
    entry=re.sub(r'<iCost>.*?</iCost>','<iCost>-1</iCost>',entry)
    entry=re.sub(r'<iAdvancedStartCost>.*?</iAdvancedStartCost>',
                 '<iAdvancedStartCost>-1</iAdvancedStartCost>',entry)
    pattern=r'<BuildingInfo>(?:(?!</BuildingInfo>).)*?<Type>BUILDING_ARCTIC_PALACE_DISPLAY</Type>.*?</BuildingInfo>'
    if re.search(pattern,text,re.S):
        text=re.sub(pattern,lambda m:entry,text,flags=re.S)
    else:
        text=text.replace('</BuildingInfos>',entry+'\n</BuildingInfos>')
    path.write_text(text,encoding='utf-8')



def arctic_city_lots(assets):
    """Only Arctic cities replace their paving with softly translucent snow dust."""
    import xml.etree.ElementTree as ET
    folder=MOD/'Assets/Art/Structures/Cities'
    source=Image.open(io.BytesIO(assets.read('base:art/structures/cities/all_an_lots.dds'))).convert('RGBA')
    rng=random.Random(7341)
    dust=Image.new('RGBA',source.size)
    # Blur the coverage itself: otherwise the original alpha still traces
    # individual cobblestones even after replacing their RGB colors.
    from PIL import ImageFilter
    coverage=source.getchannel('A').filter(ImageFilter.GaussianBlur(10))
    pixels=[]
    for alpha in coverage.getdata():
        noise=rng.uniform(.92,1.08)
        pixels.append((118,132,142,int(alpha*.17*noise)))
    dust.putdata(pixels)
    dust.save(folder/'Arctic/snow_dust.dds',pixel_format='DXT5')
    for key in sorted(assets.packed):
        name=Path(key).name
        if not key.startswith('art/structures/cities/') or not (
                name.startswith('all_city_lot_') or name in ('ren_city_lot.nif','mod_city_lot.nif')) or not name.endswith('.nif'):
            continue
        model=NifFormat.Data()
        model.read(io.BytesIO(assets.read('base:'+key)))
        for node in model.get_global_iterator():
            if isinstance(node,NifFormat.NiSourceTexture):
                node.file_name=b'Art/Structures/Cities/Arctic/snow_dust.dds'
            if isinstance(node,NifFormat.NiAlphaProperty):
                node.flags=(int(node.flags)|1)&~512
                node.threshold=0
        with (folder/('arctic_'+name)).open('wb') as out:
            model.write(out)
    path=MOD/'Assets/XML/Buildings/CIV4CityLSystem.xml'
    text=path.read_text(encoding='utf-8')
    text=re.sub(r'<ArtRef Name="decoration:arctic_[^"]*city_lot[^"]*">.*?</ArtRef>\s*','',text,flags=re.S)
    root=ET.parse(MOD/'Assets/XML/GlobalTypes.xml').getroot()
    styles=[e.text for e in root.iter() if e.tag.split('}')[-1] == 'ArtStyleType' and e.text not in ('ARTSTYLE_ARCTIC','ARTSTYLE_ALL')]
    assert styles, 'Missing non-Arctic city art styles'
    others=','.join(styles)
    pattern=r'<ArtRef Name="decoration:((?:all_city_lot_[^"]+|ren_city_lot|mod_city_lot)\.nif)(::[^"]*)?">.*?</ArtRef>'
    def replace(match):
        old=match[0]
        style=r'<Attribute Class="ArtStyle">.*?</Attribute>'
        if re.search(style,old,re.S):
            old=re.sub(style,'<Attribute Class="ArtStyle">'+others+'</Attribute>',old,flags=re.S)
        else:
            old=old.replace('</ArtRef>','<Attribute Class="ArtStyle">'+others+'</Attribute>\n\t\t</ArtRef>')
        arctic=old.replace('decoration:'+match[1],'decoration:arctic_'+match[1],1)
        arctic=re.sub(style,'<Attribute Class="ArtStyle">ARTSTYLE_ARCTIC</Attribute>',arctic,flags=re.S)
        return old+'\n\t\t'+arctic
    text=re.sub(pattern,replace,text,flags=re.S)
    path.write_text(text,encoding='utf-8')


def snowy_road_art(assets):
    """A render-only road variant; logical map routes stay ordinary roads."""
    folder=MOD/'Assets/Art/Arctic/SnowRoads'
    folder.mkdir(parents=True,exist_ok=True)
    source=assets.read('base:art/terrain/routes/roads/roadprimitive.dds')
    texture=Image.open(io.BytesIO(source)).convert('RGBA')
    pixels=[]
    for r,g,b,a in texture.getdata():
        light=.299*r+.587*g+.114*b
        pixels.append((int(155+light*.24),int(167+light*.24),int(177+light*.24),a))
    texture.putdata(pixels)
    texture.save(folder/'snow_path.dds',pixel_format='DXT5')
    route_path=MOD/'Assets/XML/Misc/CIV4RouteInfos.xml'
    route_text=(route_path.read_text(encoding='utf-8') if route_path.exists() else
                assets.read('bts:XML/Misc/CIV4RouteInfos.xml').decode('utf-8'))
    template=next(b for b in re.findall(r'<RouteInfo>.*?</RouteInfo>',route_text,re.S)
                  if '<Type>ROUTE_ROAD</Type>' in b)
    entry=template.replace('ROUTE_ROAD','ROUTE_SNOW_PATH_DISPLAY')
    pattern=r'<RouteInfo>(?:(?!</RouteInfo>).)*?<Type>ROUTE_SNOW_PATH_DISPLAY</Type>.*?</RouteInfo>'
    if re.search(pattern,route_text,re.S):
        route_text=re.sub(pattern,lambda m:entry,route_text,flags=re.S)
    else:
        route_text=route_text.replace('</RouteInfos>',entry+'\n</RouteInfos>')
    route_path.write_text(route_text,encoding='utf-8')
    model_path=MOD/'Assets/XML/Art/CIV4RouteModelInfos.xml'
    model_text=(model_path.read_text(encoding='utf-8') if model_path.exists() else
                assets.read('bts:XML/Art/CIV4RouteModelInfos.xml').decode('utf-8'))
    model_text=re.sub(r'<RouteModelInfo>(?:(?!</RouteModelInfo>).)*?<RouteType>ROUTE_SNOW_PATH_DISPLAY</RouteType>.*?</RouteModelInfo>','',model_text,flags=re.S)
    entries=[]
    paths=set()
    for block in re.findall(r'<RouteModelInfo>.*?</RouteModelInfo>',model_text,re.S):
        if '<RouteType>ROUTE_ROAD</RouteType>' not in block:
            continue
        entry=block.replace('ROUTE_ROAD','ROUTE_SNOW_PATH_DISPLAY')
        for tag in ('ModelFile','LateModelFile'):
            original=re.search('<'+tag+r'>(.*?)</'+tag+'>',entry)[1]
            paths.add(original)
            target='Art/Arctic/SnowRoads/'+Path(original).name
            entry=entry.replace('<'+tag+'>'+original+'</'+tag+'>',
                                '<'+tag+'>'+target+'</'+tag+'>')
        entries.append(entry)
    model_text=model_text.replace('</RouteModelInfos>','\n'.join(entries)+'\n</RouteModelInfos>')
    model_path.write_text(model_text,encoding='utf-8')
    for original in paths:
        try:
            content=[(original,assets.read('bts:'+original))]
        except FileNotFoundError:
            # Some route paths are stems: the engine selects numbered variants.
            prefix=str(Path(original).with_suffix('')).replace('\\','/').lower()+'-'
            variants=sorted(k for k in assets.packed if k.startswith(prefix) and k.endswith('.nif'))
            if not variants:
                raise
            content=[(name,assets.read('base:'+name)) for name in variants]
        for name,data in content:
            model=NifFormat.Data()
            model.read(io.BytesIO(data))
            for node in model.get_global_iterator():
                if isinstance(node,NifFormat.NiSourceTexture):
                    node.file_name=b'Art/Arctic/SnowRoads/snow_path.dds'
            with (folder/Path(name).name).open('wb') as out:
                model.write(out)


def archive_symbols(assets):
    """Build independent graphic entities for direct archive outputs.

    Never extend the engine's five-symbol yield arrays. The feature entries
    are render-only templates and are never assigned to map terrain.
    """
    import xml.etree.ElementTree as ET
    folder = MOD / 'Assets/Art/Arctic/ArchiveSymbols'
    folder.mkdir(parents=True, exist_ok=True)
    atlas = Image.open(MOD / 'Assets/res/Fonts/GameFont.tga').convert('RGBA')

    def font_icon(row, index):
        # The font atlas separates glyphs with opaque magenta columns.
        # Row 93 holds commerce icons; row 240 holds FontSymbols.
        cells, start = [], 0
        for x in range(atlas.width):
            r, g, b, alpha = atlas.getpixel((x, row))
            if r > 230 and g < 20 and b > 230:
                if x > start:
                    cells.append((start, x))
                start = x + 1
        left, right = cells[index]
        return atlas.crop((left, row, right, row + 20)).resize(
            (64, 64), Image.Resampling.LANCZOS)

    research_icon = font_icon(93, 1)  # COMMERCE_RESEARCH
    great_person_icon = font_icon(240, 12)  # GREAT_PEOPLE_CHAR
    for research, points in ((3, 1), (5, 0)):
        image = Image.new('RGBA', (256, 128))
        # Repeat the game's actual glyphs, as ordinary tile yields do.
        for i in range(research):
            image.alpha_composite(research_icon, (12 + i*30, 44 - i*5))
        if points:
            image.alpha_composite(great_person_icon, (176, 32))
        name = 'Archive%d' % research
        image.save(folder / (name + '.dds'), pixel_format='DXT5')
        model = NifFormat.Data()
        model.read(io.BytesIO(assets.read('base:Art/Interface/Symbols/Commerce/Commerce01.nif')))
        for block in model.get_global_iterator():
            if isinstance(block, NifFormat.NiSourceTexture):
                block.file_name = ('Art/Arctic/ArchiveSymbols/' + name + '.dds').encode('ascii')
            if isinstance(block, NifFormat.NiTriStripsData):
                for vertex in block.vertices:
                    vertex.x *= 2.0
                block.update_center_radius()
        model.roots[0].translation.z += 45.0
        with (folder / (name + '.nif')).open('wb') as out:
            model.write(out)
    # Restore the original file, including exactly five art paths per yield.
    (MOD / 'Assets/XML/Terrain/CIV4YieldInfos.xml').write_bytes(
        assets.read('base:XML/Terrain/CIV4YieldInfos.xml'))
    render_feature_templates([
        ('FEATURE_ARCHIVE_OUTPUT_%d' % research, 'TXT_KEY_DEEP_ARCHIVE',
         'TXT_KEY_DEEP_ARCHIVE_PEDIA',
         'Art/Arctic/ArchiveSymbols/Archive%d.nif' % research)
        for research in (3,5)])


def render_feature_templates(entries):
    """Register render-only models; none are assigned to map terrain."""
    import copy
    import xml.etree.ElementTree as ET
    feature_path = MOD / 'Assets/XML/Terrain/CIV4FeatureInfos.xml'
    art_path = MOD / 'Assets/XML/Art/CIV4ArtDefines_Feature.xml'
    feature_text = feature_path.read_text(encoding='utf-8')
    art_text = art_path.read_text(encoding='utf-8')
    feature_root = ET.fromstring(feature_text)
    art_root = ET.fromstring(art_text)
    for root in (feature_root, art_root):
        for node in root.iter():
            node.tag = node.tag.split('}')[-1]
    feature_template = next(feature_root.iter('FeatureInfo'))
    art_template = next(n for n in art_root.iter('FeatureArtInfo')
                        if n.findtext('Type') == 'ART_DEF_FEATURE_FALLOUT')
    for kind, description, pedia, model_path in entries:
        feature = copy.deepcopy(feature_template)
        for node in feature:
            if node.tag.startswith(('i', 'b')):
                node.text = '0'
        feature.find('Type').text = kind
        feature.find('Description').text = description
        feature.find('Civilopedia').text = pedia
        feature.find('ArtDefineTag').text = 'ART_DEF_' + kind
        for tag in ('YieldChanges', 'RiverYieldChange', 'HillsYieldChange',
                    'TerrainBooleans'):
            feature.find(tag).clear()
        feature.find('iMovement').text = '1'
        art = copy.deepcopy(art_template)
        art.find('Type').text = 'ART_DEF_' + kind
        art.find('bAnimated').text = '0'
        art.find('Button').text = 'Art/Interface/Buttons/Builds/BuildMine.dds'
        variety = art.find('FeatureVariety')
        variety.find('FeatureArtPieces/FeatureArtPiece/ModelFile').text = model_path
        # The engine can read the real plot's forest variety (0, 1 or 2).
        for i in range(2):
            art.append(copy.deepcopy(variety))
        for tag, text, entry in [('FeatureInfo', feature_text, feature),
                                  ('FeatureArtInfo', art_text, art)]:
            entry_text = ET.tostring(entry, encoding='unicode')
            pattern = r'<'+tag+r'>\s*<Type>'+re.escape(entry.findtext('Type'))+r'</Type>.*?</'+tag+'>'
            if re.search(pattern, text, re.S):
                text = re.sub(pattern, lambda m: entry_text, text, flags=re.S)
            else:
                closing = '</FeatureInfos>' if tag == 'FeatureInfo' else '</FeatureArtInfos>'
                text = text.replace(closing, entry_text + '\n' + closing)
            if tag == 'FeatureInfo':
                feature_text = text
            else:
                art_text = text
    feature_path.write_text(feature_text, encoding='utf-8')
    art_path.write_text(art_text, encoding='utf-8')


def main():
    assets = Assets()
    for folder, source in [('Farm', 'art/structures/improvements/farm/'),
                           ('Mine', 'art/structures/improvements/mine/'),
                           ('Bear', 'art/units/bear/'),
                           ('Hunter', 'art/units/scout/')]:
        target = MOD / 'Assets/Art/Arctic' / folder
        target.mkdir(parents=True, exist_ok=True)
        for key in sorted(assets.packed):
            if not key.startswith(source):
                continue
            data = assets.read('base:' + key)
            path = target / Path(key).name
            if path.suffix == '.dds':
                original = Image.open(io.BytesIO(data)).convert('RGBA')
                # Keep eyes, noses, mine openings and shadows dark. Bright
                # surfaces acquire pale blue snow, retaining original detail.
                pixels = []
                for r, g, b, a in original.getdata():
                    light = (r + g + b) // 3
                    if 'shadow' in key or 'spark' in key or light < 28:
                        pixels.append((r, g, b, a))
                    else:
                        strength = .80 if folder == 'Bear' else .72
                        pixels.append((int(r*(1-strength)+(190+light*.22)*strength),
                                       int(g*(1-strength)+(202+light*.18)*strength),
                                       int(b*(1-strength)+(214+light*.14)*strength), a))
                original.putdata(pixels)
                original.save(path, pixel_format='DXT5')
            elif path.suffix == '.nif':
                model = NifFormat.Data()
                model.read(io.BytesIO(data))
                for block in model.get_global_iterator():
                    if isinstance(block, NifFormat.NiSourceTexture) and block.file_name:
                        name = bytes(block.file_name).decode('latin-1').replace('\\', '/')
                        local = Path(name).name.lower()
                        if source + local in assets.packed:
                            block.file_name = ('Art/Arctic/' + folder + '/' + local).encode('ascii')
                with path.open('wb') as output:
                    model.write(output)
            else:
                path.write_bytes(data)
    eskimo_banner()
    special_art(assets)
    archive_symbols(assets)
    snowy_road_art(assets)
    icy_building_art(assets)
    print('Created Arctic units, improvements, igloos and ice city libraries.')


if __name__ == '__main__':
    if '--buildings-only' in sys.argv:
        icy_building_art(Assets())
    elif '--banner-only' in sys.argv:
        eskimo_banner()
    elif '--walls-only' in sys.argv:
        icy_city_walls(Assets())
    elif '--improvements-only' in sys.argv:
        assets = Assets()
        hunting_grounds_art(assets)
        deep_archive_art(assets)
    elif '--city-art-only' in sys.argv:
        igloo_art(Assets())
    elif '--settlements-only' in sys.argv:
        arctic_settlement_art(Assets())
    elif '--snowy-roads-only' in sys.argv:
        snowy_road_art(Assets())
    elif '--archive-symbols-only' in sys.argv:
        archive_symbols(Assets())
    else:
        main()
