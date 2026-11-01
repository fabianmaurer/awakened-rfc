# All existing start dates share this authored world map. Python 2.4.
from Earth124x68Values import VALUES
from SparseGrids import expand
from Earth124x68Grids import SETTLEMENTS, CITY_NAMES, WAR_MAPS
from Earth124x68Native import VALUES as NATIVE

WIDTH = 124
HEIGHT = 68
AREA_COUNT = 3
AREAS = [(0, 24, 23, 25, 29), (0, 26, 3, 34, 32), (0, 35, 10, 43, 29), (1, 49, 40, 56, 52), (1, 59, 40, 68, 45), (1, 57, 46, 78, 65), (1, 79, 52, 83, 63), (1, 84, 54, 91, 65), (1, 92, 57, 123, 65), (2, 61, 10, 72, 22)]

SETTLERS = expand(WIDTH, HEIGHT, SETTLEMENTS)
VALUES['CityNameManager.tCityMap'] = expand(WIDTH, HEIGHT, CITY_NAMES)
# Existing war maps omit the last two slots; absent targets have zero weight.
VALUES['AIWars.tWarsMap'] = expand(WIDTH, HEIGHT, WAR_MAPS + ((0, ()), (0, ())))
