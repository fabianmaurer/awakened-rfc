"""3000 BC XL: an Indus homeland for the Harappan civilization."""
import copy
import Earth200x110 as base

WIDTH, HEIGHT = base.WIDTH, base.HEIGHT
AREA_COUNT, AREAS = base.AREA_COUNT, base.AREAS
VALUES = copy.deepcopy(base.VALUES)
NATIVE = copy.deepcopy(base.NATIVE)

for key, value in (
    ('tCapitals', (141, 64)),
    ('tReserveCapitals', (138, 60)),
    ('tCoreAreasTL', (137, 57)), ('tCoreAreasBR', (144, 66)),
    ('tNormalAreasTL', (135, 55)), ('tNormalAreasBR', (146, 68)),
    ('tBroaderAreasTL', (133, 53)), ('tBroaderAreasBR', (147, 70)),
    ('tNormalAreasSubtract', ()), ('tExceptions', ())):
    table = list(VALUES['Consts.' + key])
    table[1] = value
    VALUES['Consts.' + key] = tuple(table)

# Founding remains geographic. The Indus homeland is outside the eligible belt;
# a Harappan city established in the Ganges can still found either religion.
VALUES['Religions.tNorthIndiaTL'] = (145, 57)
VALUES['Religions.tNorthIndiaBR'] = (155, 69)

# Prefer the Indus/Punjab and Gujarat rather than filling the Ganges and south.
settlers = list(base.SETTLERS)
plane = []
for row in range(HEIGHT):
    y = HEIGHT - 1 - row
    cells = []
    for x in range(WIDTH):
        value = 20
        if 135 <= x <= 146 and 55 <= y <= 68:
            value = 200
        if 137 <= x <= 144 and 57 <= y <= 66:
            value = 400
        cells.append(value)
    plane.append(tuple(cells))
settlers[1] = tuple(plane)
SETTLERS = tuple(settlers)

# Archaeological site names are used as labels; their ancient names are unknown.
names = list(VALUES['CityNameManager.tCityMap'])
plane = [list(row) for row in names[1]]
for x, y, name in ((141, 64, 'Harappa'), (138, 60, 'Mohenjo-daro'),
                   (140, 57, 'Dholavira'), (142, 56, 'Lothal'),
                   (144, 64, 'Rakhigarhi'), (143, 62, 'Kalibangan')):
    plane[HEIGHT - 1 - y][x] = name
names[1] = tuple(tuple(row) for row in plane)
VALUES['CityNameManager.tCityMap'] = tuple(names)
