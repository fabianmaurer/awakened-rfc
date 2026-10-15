"""Render a static textured NIF contact sheet; the game supplies animations."""
from pathlib import Path
import time
if not hasattr(time, 'clock'):
    time.clock = time.perf_counter
import numpy as np
from PIL import Image, ImageDraw
from pyffi.formats.nif import NifFormat as N
from build_slave_art import MOD, ART, TIERS


def render(path):
    d = N.Data()
    with path.open('rb') as f:
        d.read(f)
    parents = {c: p for p in d.blocks if isinstance(p, N.NiNode) for c in p.children if c}
    faces = []
    all_points = []
    for mesh in d.blocks:
        if not isinstance(mesh, (N.NiTriShape, N.NiTriStrips)):
            continue
        node, hidden = mesh, False
        while node:
            if node.flags & 1 or getattr(node, 'name', b'').endswith(b'_FALL'):
                hidden = True
            node = parents.get(node)
        if hidden:
            continue
        try:
            vertices = mesh.get_skin_deformation()[0] if mesh.skin_instance else mesh.data.vertices
        except ValueError:
            # Some shipped regional meshes use a skin root outside PyFFI's
            # expected ancestor chain. Preview their bind pose instead.
            vertices = mesh.data.vertices
        points = np.array([[v.x, v.y, v.z, 1] for v in vertices])
        points = points @ np.array(mesh.get_transform(d.roots[0]).as_list())
        points = points[:, :3]
        # Oblique front view, with Z up. A wider angle also exposes the
        # Infantry/Marine rifles, which face the camera in their bind poses.
        angle = -0.65
        horizontal = points[:, 0] * np.cos(angle) + points[:, 1] * np.sin(angle)
        depth = points[:, 1] * np.cos(angle) - points[:, 0] * np.sin(angle)
        projected = np.column_stack((horizontal, -points[:, 2], depth))
        all_points.extend(projected)
        texture = None
        tint = np.ones(3)
        for prop in mesh.properties:
            if isinstance(prop, N.NiMaterialProperty):
                tint = np.array([prop.diffuse_color.r, prop.diffuse_color.g, prop.diffuse_color.b])
            if isinstance(prop, N.NiTexturingProperty):
                for name in ('base_texture', 'decal_0_texture'):
                    desc = getattr(prop, name)
                    source = desc.source
                    if source and source.file_name.lower().endswith(b'.dds'):
                        p = MOD / 'Assets' / source.file_name.decode('ascii')
                        if p.exists():
                            texture = np.array(Image.open(p).convert('RGB'))
        uvs = None
        if len(mesh.data.uv_sets):
            uvs = np.array([[v.u, v.v] for v in mesh.data.uv_sets[0]])
        for tri in mesh.data.get_triangles():
            ids = list(tri)
            faces.append((projected[ids], uvs[ids] if uvs is not None else None, texture, tint))
    all_points = np.array(all_points)
    low, high = all_points[:, :2].min(axis=0), all_points[:, :2].max(axis=0)
    scale = min(245 / max(1, high[0] - low[0]), 265 / max(1, high[1] - low[1]))
    offset = np.array([140, 155]) - (low + high) * scale / 2
    pixels = np.full((310, 280, 3), (31, 29, 27), dtype=np.uint8)
    zbuffer = np.full((310, 280), np.inf)
    for points, uv, texture, tint in faces:
        p = points[:, :2] * scale + offset
        lo = np.maximum(0, np.floor(p.min(axis=0)).astype(int))
        hi = np.minimum([279, 309], np.ceil(p.max(axis=0)).astype(int))
        if np.any(hi < lo):
            continue
        x, y = np.meshgrid(np.arange(lo[0], hi[0] + 1), np.arange(lo[1], hi[1] + 1))
        a, b, c = p
        det = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(det) < 0.00001:
            continue
        w1 = ((b[1] - c[1]) * (x - c[0]) + (c[0] - b[0]) * (y - c[1])) / det
        w2 = ((c[1] - a[1]) * (x - c[0]) + (a[0] - c[0]) * (y - c[1])) / det
        w3 = 1 - w1 - w2
        z = w1 * points[0, 2] + w2 * points[1, 2] + w3 * points[2, 2]
        mask = (w1 >= 0) & (w2 >= 0) & (w3 >= 0) & (z < zbuffer[y, x])
        if texture is not None and uv is not None:
            coords = w1[..., None] * uv[0] + w2[..., None] * uv[1] + w3[..., None] * uv[2]
            tx = (coords[..., 0] % 1 * (texture.shape[1] - 1)).astype(int)
            ty = (coords[..., 1] % 1 * (texture.shape[0] - 1)).astype(int)
            color = texture[ty, tx].astype(float) * tint
        else:
            color = np.broadcast_to(tint * 155, (*x.shape, 3))
        pixels[y[mask], x[mask]] = np.clip(color[mask], 0, 255).astype(np.uint8)
        zbuffer[y[mask], x[mask]] = z[mask]
    return Image.fromarray(pixels)


if __name__ == '__main__':
    sheet = Image.new('RGB', (1120, 680), (31, 29, 27))
    draw = ImageDraw.Draw(sheet)
    for i, (unit, *_rest) in enumerate(TIERS):
        x, y = i % 4 * 280, i // 4 * 340
        sheet.paste(render(ART / unit / 'slave_a.nif'), (x, y))
        draw.text((x + 12, y + 315), unit.replace('SLAVE_', '').replace('_', ' ').title(), fill=(220, 211, 190))
    target = Path(__file__).resolve().parents[1] / 'art/slaves/preview.png'
    target.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(target)
    print(target)
