"""Load and apply the human-editable XL city-name catalog (offline Python 3).

Edit large_world_city_names.json; the game loads only the generated grids.
"""
from functools import lru_cache
import json
from pathlib import Path


CIVILIZATIONS = (
    'Egypt', 'India', 'China', 'Babylonia', 'Greece', 'Persia', 'Carthage',
    'Rome', 'Japan', 'Ethiopia', 'Maya', 'Vikings', 'Arabia', 'Khmer', 'Spain',
    'France', 'England', 'Germany', 'Russia', 'Netherlands', 'Mali', 'Portugal',
    'Inca', 'Mongolia', 'Aztecs', 'Turkey', 'America', 'CaliphateSlot1',
    'CaliphateSlot2', 'Xiongnu', 'Korea', 'Mississippians', 'Eskimos',
)
CATALOG = Path(__file__).with_suffix('.json')


def game_name(name):
    # Authors can type accents normally; retain RFC's ASCII numeric references.
    return name.encode('ascii', 'xmlcharrefreplace').decode('ascii')


@lru_cache(maxsize=1)
def load_sites():
    """Resolve named civilizations and report malformed entries before generation."""
    catalog = json.loads(CATALOG.read_text(encoding='utf-8'))
    if not isinstance(catalog, dict):
        raise ValueError('XL city-name catalog must group entries by region')
    sites = []
    for region, entries in catalog.items():
        if not isinstance(entries, list):
            raise ValueError('XL city-name region must contain a list: ' + region)
        for index, entry in enumerate(entries, 1):
            label = '%s, entry %d' % (region, index)
            required = {'civ', 'x', 'y', 'name'}
            if (not isinstance(entry, dict) or not required.issubset(entry) or
                    set(entry) - (required | {'variants'})):
                raise ValueError('Expected civ, x, y, name and optional variants: ' + label)
            if entry['civ'] not in CIVILIZATIONS:
                raise ValueError('Unknown civilization in ' + label)
            if (type(entry['x']) is not int or type(entry['y']) is not int or
                    not 0 <= entry['x'] < 200 or not 0 <= entry['y'] < 110):
                raise ValueError('XL coordinates must be x=0..199, y=0..109: ' + label)
            variants = entry.get('variants', {})
            if (not isinstance(entry['name'], str) or not entry['name'].strip() or
                    not isinstance(variants, dict) or
                    any(not isinstance(n, str) or not n.strip()
                        for pair in variants.items() for n in pair)):
                raise ValueError('Names and variant pairs must be nonempty text: ' + label)
            sites.append((CIVILIZATIONS.index(entry['civ']), entry['x'], entry['y'],
                          game_name(entry['name']),
                          {game_name(k): game_name(v) for k, v in variants.items()}))
    return tuple(sites)


def validate_sites(map_text):
    """Fail generation if terrain changes strand an authored naming site."""
    import re
    plots = {}
    for block in re.findall(r'BeginPlot\s+(.*?)EndPlot', map_text, re.S):
        point = tuple(map(int, re.search(r'x=(\d+),y=(\d+)', block).groups()))
        plots[point] = block
    occupied = set()
    for civilization, x, y, name, variants in load_sites():
        if (x, y) in occupied:
            raise ValueError('Duplicate XL naming site: %s' % ((x, y),))
        occupied.add((x, y))
        block = plots.get((x, y), '')
        if (not re.search(r'PlotType=([12])\b', block) or
                '_IMPASSABLE' in block or 'FEATURE_ICE' in block):
            raise ValueError('XL naming site is not passable land: ' + name)


def refine(rows, civilization, original_planes, protected):
    """Apply authored tiles; never replace an existing civilization's capital."""
    result = [list(row) for row in rows]
    changes = []
    for reference, x, y, name, variants in load_sites():
        if (x, y) in protected:
            raise ValueError('XL city-name refinement overlaps a protected city: %s' % ((x, y),))
        row = 109 - y
        parent = original_planes[reference][row][x]
        current = rows[row][x]
        replacement = None
        if civilization == reference or (parent != '-1' and current == parent):
            replacement = name
        else:
            replacement = variants.get(current)
        if replacement is not None and replacement != current:
            result[row][x] = replacement
            changes.append((x, y, replacement))
    return tuple(tuple(row) for row in result), tuple(changes)
