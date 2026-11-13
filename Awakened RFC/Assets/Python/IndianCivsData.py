"""XL Indian civilizations and portable geography extensions. Python 2.4."""
import copy

# Shared by scenario authoring and the historical drying sequence.
HARAPPAN_CITIES = (
    ('Harappa', (141, 64), 6),
    ('Mohenjo-daro', (140, 62), 4),
    ('Rakhigarhi', (141, 66), 5),
)
# A narrow eastern distributary joins the existing upper and lower Indus.
# (x, y, edge, flow): edge 0 is south, 1 is east; flow uses Civ4 directions.
HARAPPAN_CHANNEL = tuple([(141, y, 1, 2) for y in range(62, 66)] +
    [(x, 62, 0, 3) for x in range(139, 142)])
HARAPPAN_FLOODPLAINS = (
    (140, 61), (140, 62), (141, 62), (141, 63),
    (141, 64), (141, 66), (142, 66),
)
# Only authored extra farmland retreats; the original Indus floodplains stay.
HARAPPAN_DRYING = (
    (-1900, ((141, 63), (141, 66), (142, 66), (140, 62), (141, 62))),
)

FIRST_SLOT = 33
CIVS = (
    ('GANGES', 'GAN', 0, -3000, (150, 65), (148, 62), (152, 67), (146, 60), (154, 68)),
    ('CHOLA', 'CHO', 206, 850, (147, 52), (145, 50), (149, 54), (143, 48), (151, 56)),
    ('DELHI', 'DEL', 241, 1200, (145, 65), (142, 63), (148, 68), (139, 60), (151, 70)),
    ('BENGAL', 'BEN', 256, 1350, (154, 65), (153, 62), (157, 67), (151, 60), (159, 69)),
    ('VIJAYANAGARA', 'VIJ', 256, 1350, (145, 56), (143, 55), (147, 58), (141, 51), (149, 60)),
)
NAMES = (
    ((150,65,'Pataliputra'), (149,64,'Varanasi'), (149,66,'Ayodhya'), (147,65,'Kannauj'), (151,63,'Rajagriha')),
    ((147,52,'Thanjavur'), (148,53,'Kanchipuram'), (147,51,'Madurai'), (148,51,'Nagapattinam'), (151,48,'Polonnaruwa')),
    ((145,65,'Delhi'), (144,67,'Lahore'), (146,64,'Agra'), (143,61,'Ajmer'), (147,65,'Kannauj')),
    ((154,65,'Gaur'), (154,64,'Sonargaon'), (153,62,'Tamralipti'), (156,63,'Chittagong'), (155,66,'Pandua')),
    ((145,56,'Vijayanagara'), (145,54,'Mysuru'), (143,57,'Goa'), (146,55,'Bengaluru'), (147,57,'Warangal')),
)


def extend(profile, name):
    """Keep every geography at DLL capacity; only XL gets Indian homelands."""
    if getattr(profile, '_indianExtended', False): return
    profile.VALUES = copy.deepcopy(profile.VALUES)
    xl = name.startswith('Earth200x110')
    w, h = profile.WIDTH, profile.HEIGHT
    blank = tuple([tuple([0] * w)] * h)
    noNames = tuple([tuple(['-1'] * w)] * h)
    settlers = list(profile.SETTLERS[:FIRST_SLOT])
    names = list(profile.VALUES['CityNameManager.tCityMap'][:FIRST_SLOT])
    wars = list(profile.VALUES['AIWars.tWarsMap'][:FIRST_SLOT])
    keys = ('tCapitals', 'tReserveCapitals', 'tCoreAreasTL', 'tCoreAreasBR',
        'tNormalAreasTL', 'tNormalAreasBR', 'tNormalAreasSubtract',
        'tBroaderAreasTL', 'tBroaderAreasBR', 'tExceptions')
    for key in keys:
        profile.VALUES['Consts.' + key] = list(profile.VALUES['Consts.' + key][:FIRST_SLOT])
    for offset, entry in enumerate(CIVS):
        civ, short, birth, year, capital, coreTL, coreBR, normalTL, normalBR = entry
        if name == 'Earth200x110' and offset == 0: normalTL = (142, 60)
        if not xl: capital, coreTL, coreBR, normalTL, normalBR = [(0, 0)] * 5
        data = (capital, (), coreTL, coreBR, normalTL, normalBR, (), normalTL, normalBR, ())
        for key, value in zip(keys, data): profile.VALUES['Consts.' + key].append(value)
        plane, namePlane, warPlane = blank, noNames, blank
        if xl:
            plane, warPlane = [], []
            for row in range(h):
                y = h - 1 - row
                cells, targets = [], []
                for x in range(w):
                    value = 0
                    if normalTL[0] <= x <= normalBR[0] and normalTL[1] <= y <= normalBR[1]: value = 200
                    if coreTL[0] <= x <= coreBR[0] and coreTL[1] <= y <= coreBR[1]: value = 400
                    if civ == 'CHOLA' and 147 <= x <= 153 and 46 <= y <= 50: value = 150
                    cells.append(value)
                    targets.append(value)
                plane.append(tuple(cells)); warPlane.append(tuple(targets))
            plane, warPlane = tuple(plane), tuple(warPlane)
            # Keep India's established regional vocabulary, then local identities.
            namePlane = [list(row) for row in profile.VALUES['CityNameManager.tCityMap'][1]]
            for x,y,city in NAMES[offset]: namePlane[h - 1 - y][x] = city
            namePlane = tuple([tuple(row) for row in namePlane])
        settlers.append(plane); names.append(namePlane); wars.append(warPlane)
    profile.SETTLERS = tuple(settlers)
    profile.VALUES['CityNameManager.tCityMap'] = tuple(names)
    profile.VALUES['AIWars.tWarsMap'] = tuple(wars)
    if xl:
        profile.VALUES['Religions.tNorthIndiaTL'] = (146, 60)
        profile.VALUES['Religions.tNorthIndiaBR'] = (155, 69)
    profile._indianExtended = True
