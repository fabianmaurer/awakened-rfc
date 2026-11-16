"""Package the generated fertile-soil decal as Civ4 DDS textures and a NIF.

Run with .venv-art/Scripts/python.exe. The source PNG's colours and transparency
are retained; this only resizes/encodes textures and builds the ground mesh.
"""
from pathlib import Path
from PIL import Image
from build_arctic_art import mesh, NifFormat

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'art/fertile-soil/FertileSoil.png'
FOLDER = ROOT / 'Awakened RFC/Assets/Art/Terrain/Features/FertileSoil'
TEXTURE = 'Art/Terrain/Features/FertileSoil/FertileSoil.dds'


def main():
    FOLDER.mkdir(parents=True, exist_ok=True)
    picture = Image.open(SOURCE).convert('RGBA')
    picture.resize((512, 512), Image.Resampling.LANCZOS).save(
        FOLDER / 'FertileSoil.dds', pixel_format='DXT5')
    picture.resize((64, 64), Image.Resampling.LANCZOS).save(
        FOLDER / 'FertileSoilButton.dds', pixel_format='DXT5')

    # A tile is 180 world units. A small inset and the texture's transparent
    # margin keep the decal off neighbouring plots. Tessellation allows the
    # engine's feature contouring to follow the ground; this is not river art.
    divisions, half_width = 8, 84.
    vertices, uvs, triangles = [], [], []
    for y in range(divisions + 1):
        for x in range(divisions + 1):
            u, v = x / divisions, y / divisions
            vertices.append(((u * 2 - 1) * half_width,
                             (v * 2 - 1) * half_width, .6))
            uvs.append((u, 1 - v))
    for y in range(divisions):
        for x in range(divisions):
            a = y * (divisions + 1) + x
            b, c, d = a + 1, a + divisions + 1, a + divisions + 2
            triangles.extend(((a, b, d), (a, d, c)))
    shape = mesh('Fertile soil', vertices, triangles, (1., 1., 1.), TEXTURE, uvs=uvs)
    for prop in shape.properties:
        if isinstance(prop, NifFormat.NiMaterialProperty):
            prop.name = b'Fertile soil'
            prop.specular_color.r = prop.specular_color.g = prop.specular_color.b = 0
            prop.glossiness = 0
    alpha = NifFormat.NiAlphaProperty()
    alpha.flags = 237  # Source-alpha blending, no hard alpha-test cutoff.
    alpha.threshold = 0
    shape.add_property(alpha)
    depth = NifFormat.NiZBufferProperty()
    depth.flags = 1  # Test against terrain/improvements; do not write depth.
    depth.function = 3  # Less than or equal: improvements remain above the soil.
    shape.add_property(depth)
    # Match the legacy format used by the mod's existing feature models.
    data = NifFormat.Data(version=0x0A020000)
    root = NifFormat.NiNode()
    root.name, root.flags = b'Fertile soil', 14
    root.add_child(shape)
    data.roots = [root]
    with (FOLDER / 'FertileSoil.nif').open('wb') as output:
        data.write(output)
    print('Built fertile-soil mesh, transparent DXT5 texture and feature button.')


if __name__ == '__main__':
    main()
