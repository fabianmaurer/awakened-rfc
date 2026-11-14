"""Build a neutral impassable overlay from Civ4's animated fallout smoke.

Run with .venv-art/Scripts/python.exe. Reads the locally installed game's art
through the existing Assets helper. Derived assets are for use with Civ4.
"""
from pathlib import Path
import io

from build_arctic_art import NifFormat as N
from build_slave_art import Assets

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'Awakened RFC/Assets/Art/Terrain/Features/Wasteland'
SOURCE = 'base:Art/Effects/cities_irradiated/fx_cities_iradiated.nif'
TEXTURE = 'Art/Terrain/Features/Wasteland/FogSmoke.dds'
FOGS = (
    ('ImpassableFog.nif', (.55, .57, .56)),
)


def main():
    assets = Assets()
    source = assets.read(SOURCE)
    OUT.mkdir(parents=True, exist_ok=True)
    # Preserve the shipped smoke alpha mask and its scrolling texture animation.
    (OUT / 'FogSmoke.dds').write_bytes(assets.texture('fx_smokedrift00.dds', SOURCE))
    for filename, tint in FOGS:
        data = N.Data()
        data.read(io.BytesIO(source))
        root = data.roots[0]
        smoke = [node for node in root.children if node.name.startswith(b'smoke')]
        root.num_children = len(smoke)
        root.children.update_size()
        for index, node in enumerate(smoke):
            root.children[index] = node
        # The source spans a city-sized area. Fit its soft cloud layers to a
        # 180-unit plot, with a little overlap between neighbouring fog tiles.
        root.scale = .55
        root.name = filename.removesuffix('.nif').encode('ascii')
        for block in root.tree():
            if isinstance(block, N.NiMaterialProperty):
                block.name = b'Impassable fog'
                block.emissive_color.r, block.emissive_color.g, block.emissive_color.b = tint
                block.specular_color.r = block.specular_color.g = block.specular_color.b = 0
                block.glossiness = 0
            elif isinstance(block, N.NiSourceTexture):
                block.file_name = TEXTURE.encode('ascii')
            elif isinstance(block, N.NiTriShapeData):
                # 35% denser, preserving soft edges and vegetation beneath it.
                for color in block.vertex_colors:
                    color.a = min(1., color.a * 1.35)
        with (OUT / filename).open('wb') as handle:
            data.write(handle)
        print(OUT / filename)


if __name__ == '__main__':
    main()
