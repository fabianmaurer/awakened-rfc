# Scenario-selected geography shared by Python and the DLL. Python 2.4.
import copy
import os
from CvPythonExtensions import CyMap


# Selection is explicit: a map of the same size need not have the same geography.
SCENARIOS = {
    'start 1 - 3000 bc.civbeyondswordwbsave': 'Earth124x68',
    'start 2 - 800 bc.civbeyondswordwbsave': 'Earth124x68',
    'start 3 - 600 ad.civbeyondswordwbsave': 'Earth124x68',
    'start 3b - 900 ad.civbeyondswordwbsave': 'Earth124x68',
    'start 4 - 1453 ad.civbeyondswordwbsave': 'Earth124x68',
}

_name = 'Earth124x68' # Import-time bootstrap; scenario loading always selects explicitly.
_profiles = {}
_values = {}
_bindings = []
# Missing scripted-event locations abort only the current dispatched callback.
# Naming grids, birth/stability tables and DLL geography remain mandatory.
_eventModules = ('Resources', 'Barbs', 'Religions', 'RiseAndFall', 'Arctic',
                 'CvRFCEventHandler')
_mutable = ('tCapitals', 'tReserveCapitals', 'tCoreAreasTL', 'tCoreAreasBR',
            'tNormalAreasTL', 'tNormalAreasBR', 'tNormalAreasSubtract',
            'tBroaderAreasTL', 'tBroaderAreasBR', 'tExceptions')


def _profile(name=None):
    if name is None: name = _name
    if not name or name.replace('_', '').isalnum() == False:
        raise ValueError('Invalid scenario geography profile name')
    if name not in _profiles:
        # Civ4 discovers Python files recursively but imports them by their flat
        # module names. Its custom importer does not support ordinary packages.
        _profiles[name] = __import__(name)
    return _profiles[name]


def width():
    return _profile().WIDTH


def height():
    return _profile().HEIGHT


def original(key):
    """Unmodified authored data, for restoring successor-civilization regions."""
    return _profile().VALUES[key]


def value(key):
    if _isEventLocation(key) and _profile().VALUES.get(key) is None:
        raise MissingCoordinate(key)
    if key not in _values:
        entry = copy.deepcopy(original(key))
        if key.startswith('Consts.') and key.split('.')[1] in _mutable:
            entry = list(entry)
        _values[key] = entry
    return _values[key]


def bind(namespace, name, key):
    """Refresh module aliases when another scenario is opened in this process."""
    _bindings.append((namespace, name, key))
    namespace[name] = _boundValue(key)


def _boundValue(key):
    if _isEventLocation(key) and _profile().VALUES.get(key) is None:
        return _MissingBoundCoordinate(key)
    return value(key)


def _isEventLocation(key):
    return key.split('.')[0] in _eventModules


class MissingCoordinate(Exception):
    """A deliberately unauthored scripted-event location, not a script error."""
    pass


class _MissingBoundCoordinate:
    """Defer missing module constants until the event actually uses them."""
    def __init__(self, key):
        self.key = key

    def __deepcopy__(self, memo):
        return self

    def _missing(self, *args):
        raise MissingCoordinate(self.key)

    __getitem__ = __iter__ = __len__ = __nonzero__ = __cmp__ = _missing


def _validate(profile):
    w, h = profile.WIDTH, profile.HEIGHT
    if not (0 < w <= 32767 and 0 < h <= 32767):
        raise ValueError('Invalid scenario geography dimensions')
    # Event locations may be omitted or set to None. Never substitute coordinates
    # from the reference map or turn missing locations into valid tile (0, 0).
    base = _profile('Earth124x68')
    for key in base.VALUES:
        if not _isEventLocation(key) and (key not in profile.VALUES or profile.VALUES[key] is None):
            raise ValueError('Missing scenario geography value: ' + key)
    for key, entries in base.NATIVE.items():
        if key not in profile.NATIVE or len(profile.NATIVE[key]) != len(entries):
            raise ValueError('Missing or malformed native geography value: ' + key)
    for grids in (profile.SETTLERS, profile.VALUES['CityNameManager.tCityMap'],
                  profile.VALUES['AIWars.tWarsMap']):
        if len(grids) != 33:
            raise ValueError('Scenario geography needs one map per major civilization')
        for plane in grids:
            if len(plane) != h:
                raise ValueError('Scenario geography grid height mismatch')
            for row in plane:
                if len(row) != w:
                    raise ValueError('Scenario geography grid width mismatch')
    for group, west, south, east, north in profile.AREAS:
        if not (0 <= group < profile.AREA_COUNT and
                0 <= west <= east < w and 0 <= south <= north < h):
            raise ValueError('Invalid scenario continent rectangle')


def _activate(name):
    global _name, _values
    profile = _profile(name)
    _validate(profile)
    _name = name
    _values = {}
    for namespace, variable, key in _bindings:
        namespace[variable] = _boundValue(key)
    return profile


def prepare(filename, mapDescription):
    """Install geography before WorldBuilder creates areas, cities or units."""
    basename = os.path.basename((filename or '').replace('\\', '/')).lower()
    if basename not in SCENARIOS:
        raise ValueError('Register a geography profile for scenario: ' + basename)
    name = SCENARIOS[basename]
    profile = _profile(name)
    _validate(profile)
    if (mapDescription.iGridW, mapDescription.iGridH) != (profile.WIDTH, profile.HEIGHT):
        raise ValueError('Scenario map dimensions do not match its geography profile')
    areas = [n for rectangle in profile.AREAS for n in rectangle]
    settlers = [n for plane in profile.SETTLERS for row in plane for n in row]
    keys = sorted(profile.NATIVE.keys())
    numbers = [list(profile.NATIVE[key]) for key in keys]
    if not CyMap().configureScenarioGeography([name, profile.WIDTH, profile.HEIGHT,
            profile.AREA_COUNT, areas, settlers, keys, numbers]):
        raise ValueError('The DLL rejected the scenario geography profile')
    _activate(name)


def restore():
    """Select saved geography before any load-time civilization callbacks."""
    world = CyMap()
    name = world.getScenarioGeographyName()
    profile = _activate(name)
    if (world.getGridWidth(), world.getGridHeight()) != (profile.WIDTH, profile.HEIGHT):
        raise ValueError('Saved map dimensions do not match its geography profile')
