"""Generate military mastery techs, DLL data, localized help and the design table.

Run after generators which change units/technologies. Appends infos without moving
existing IDs. Does not build the DLL or launch the game.
"""
from pathlib import Path
import copy
import re
import struct
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'Awakened RFC'
XML = MOD / 'Assets/XML'
LANGS = ('English', 'French', 'German', 'Italian', 'Spanish')
# The basic Warrior has no unlocking technology.
MASTERY_NO_TECH_BASE_COST = 100

# Each tuple is an incremental reward. Earlier rewards remain active.
# Explicit tracks keep rewards specific to the unit, including unique units.
TRACKS = {
    'SCOUT': [('VISIBILITY', 1), ('FOREST_DOUBLE', 1, 'JUNGLE_DOUBLE', 1), ('HEAL', 15, 'FIRST_IMMUNE', 1)],
    'EXPLORER': [('MOVES', 1), ('SAME_TILE_HEAL', 15), ('IGNORE_TERRAIN', 1, 'HEAL', 15)],
    'WARRIOR': [('CITY_DEFENSE', 30), ('MELEE', 30), ('HEAL', 15, 'ALWAYS_HEAL', 1)],
    'SWORDSMAN': [('CITY_ATTACK', 30), ('FIRST_IMMUNE', 1), ('BLITZ', 1, 'MOVES', 1)],
    'AXEMAN': [('MELEE', 35), ('FOREST_ATTACK', 40), ('COLLATERAL', 30, 'COLLATERAL_TARGETS', 3, 'COLLATERAL_LIMIT', 40)],
    'MACEMAN': [('CITY_ATTACK', 30), ('ARMOR', 25, 'GUN', 25), ('FIRST_STRIKES', 2)],
    'SPEARMAN': [('MOUNTED', 50), ('HILLS_DEFENSE', 40), ('FIRST_STRIKES', 2)],
    'PIKEMAN': [('MOUNTED', 50), ('MELEE', 30), ('FIRST_IMMUNE', 1, 'HEAL', 15)],
    'MUSKETMAN': [('CITY_DEFENSE', 30), ('FIRST_STRIKES', 2), ('AMPHIB', 1, 'RIVER', 1)],
    'RIFLEMAN': [('GUN', 25), ('HILLS_DEFENSE', 40), ('ALWAYS_HEAL', 1, 'HEAL', 15)],
    'GRENADIER': [('CITY_ATTACK', 35), ('COLLATERAL', 35, 'COLLATERAL_TARGETS', 3, 'COLLATERAL_LIMIT', 50), ('FIRST_IMMUNE', 1)],
    'AT_INFANTRY': [('ARMOR', 50), ('HILLS_DEFENSE', 40), ('WITHDRAWAL', 40)],
    'INFANTRY': [('CITY_ATTACK', 30), ('SAME_TILE_HEAL', 15), ('BLITZ', 1, 'MOVES', 1)],
    'MARINE': [('CITY_ATTACK', 35), ('FIRST_STRIKES', 2), ('ALWAYS_HEAL', 1, 'HEAL', 20)],
    'PARATROOPER': [('HILLS_DEFENSE', 40), ('ENEMY_ROUTE', 1), ('CITY_ATTACK', 35, 'FIRST_IMMUNE', 1)],
    'MECHANIZED_INFANTRY': [('ARMOR', 35), ('SAME_TILE_HEAL', 20), ('MOVES', 1, 'ENEMY_ROUTE', 1)],
    'ARCHER': [('CITY_DEFENSE', 40), ('HILLS_DEFENSE', 40), ('FIRST_STRIKES', 2)],
    'LONGBOWMAN': [('CITY_DEFENSE', 40), ('FIRST_STRIKES', 2), ('SAME_TILE_HEAL', 15, 'HEAL', 15)],
    'CROSSBOWMAN': [('MELEE', 40), ('HILLS_ATTACK', 40), ('FIRST_STRIKES', 2)],
    'CHARIOT': [('WITHDRAWAL', 30), ('ARCHER', 40), ('MOVES', 1, 'RIVER', 1)],
    'HORSE_ARCHER': [('WITHDRAWAL', 30), ('FIRST_STRIKES', 2), ('ENEMY_ROUTE', 1)],
    'KNIGHT': [('CITY_ATTACK', 30), ('WITHDRAWAL', 30), ('BLITZ', 1, 'MOVES', 1)],
    'CUIRASSIER': [('GUN', 30), ('WITHDRAWAL', 35), ('MOVES', 1, 'FIRST_IMMUNE', 1)],
    'CAVALRY': [('SIEGE', 50), ('ENEMY_ROUTE', 1), ('BLITZ', 1, 'MOVES', 1)],
    'WAR_ELEPHANT': [('MELEE', 35), ('CITY_ATTACK', 35), ('COLLATERAL', 40, 'COLLATERAL_TARGETS', 4, 'COLLATERAL_LIMIT', 50)],
    'TANK': [('CITY_ATTACK', 35), ('WITHDRAWAL', 35), ('MOVES', 1, 'ENEMY_ROUTE', 1)],
    'MODERN_ARMOR': [('ARMOR', 35), ('FIRST_IMMUNE', 1), ('MOVES', 1, 'ALWAYS_HEAL', 1)],
    'CATAPULT': [('BOMBARD', 20), ('COLLATERAL_TARGETS', 3), ('WITHDRAWAL', 40)],
    'TREBUCHET': [('CITY_ATTACK', 50), ('BOMBARD', 25), ('COLLATERAL_LIMIT', 20, 'COLLATERAL_TARGETS', 2)],
    'CANNON': [('COLLATERAL', 30), ('BOMBARD', 30), ('WITHDRAWAL', 40)],
    'MACHINE_GUN': [('GUN', 35), ('FIRST_STRIKES', 3), ('SAME_TILE_HEAL', 20)],
    'ARTILLERY': [('COLLATERAL_TARGETS', 4), ('COLLATERAL_LIMIT', 20), ('MOVES', 1)],
    'MOBILE_ARTILLERY': [('BOMBARD', 40), ('COLLATERAL_TARGETS', 4), ('WITHDRAWAL', 50, 'ENEMY_ROUTE', 1)],
    'GALLEY': [('WITHDRAWAL', 35), ('MOVES', 1), ('ALWAYS_HEAL', 1, 'HEAL', 20)],
    'TRIREME': [('FIRST_STRIKES', 2), ('WITHDRAWAL', 40), ('MOVES', 2)],
    'CARAVEL': [('VISIBILITY', 2), ('MOVES', 2), ('WITHDRAWAL', 50)],
    'GALLEON': [('WITHDRAWAL', 35), ('MOVES', 2), ('HEAL', 25, 'ALWAYS_HEAL', 1)],
    'PRIVATEER': [('WITHDRAWAL', 40), ('MOVES', 2), ('ALWAYS_HEAL', 1, 'HEAL', 25)],
    'FRIGATE': [('BOMBARD', 25), ('FIRST_STRIKES', 2), ('MOVES', 2)],
    'SHIP_OF_THE_LINE': [('FIRST_IMMUNE', 1), ('BOMBARD', 30), ('FIRST_STRIKES', 3)],
    'IRONCLAD': [('BOMBARD', 25, 'HEAL', 15), ('FIRST_IMMUNE', 1), ('MOVES', 2)],
    'DESTROYER': [('VISIBILITY', 2), ('FIRST_STRIKES', 3), ('MOVES', 2, 'WITHDRAWAL', 30)],
    'BATTLESHIP': [('BOMBARD', 40), ('COLLATERAL_TARGETS', 3, 'COLLATERAL_LIMIT', 20), ('BLITZ', 1, 'MOVES', 1)],
    'MISSILE_CRUISER': [('SAME_TILE_HEAL', 20, 'HEAL', 15), ('VISIBILITY', 2), ('BLITZ', 1, 'MOVES', 2)],
    'STEALTH_DESTROYER': [('FIRST_STRIKES', 3), ('WITHDRAWAL', 45), ('MOVES', 2, 'ALWAYS_HEAL', 1)],
    'SUBMARINE': [('WITHDRAWAL', 40), ('FIRST_STRIKES', 3), ('MOVES', 2)],
    'ATTACK_SUBMARINE': [('FIRST_STRIKES', 3), ('FIRST_IMMUNE', 1, 'HEAL', 20), ('MOVES', 2, 'WITHDRAWAL', 30)],
    'AUTONOMOUS_COMBAT_VEHICLE': [('CITY_DEFENSE', 40), ('ALWAYS_HEAL', 1, 'HEAL', 20), ('FIRST_STRIKES', 3)],
    'AUTONOMOUS_TANK': [('CITY_ATTACK', 40), ('ARMOR', 40), ('MOVES', 1, 'ENEMY_ROUTE', 1)],
    'WAR_GALLEY': [('FIRST_STRIKES', 2), ('HEAL', 20, 'ALWAYS_HEAL', 1), ('BLITZ', 1)],
    'ARCTIC_HUNTER': [('VISIBILITY', 1, 'ANIMAL', 50), ('HILLS_DOUBLE', 1), ('FIRST_STRIKES', 2, 'HEAL', 20)],
    # Unique units: deliberate rewards build on their historical/gameplay role.
    'INCAN_QUECHUA': [('ARCHER', 50), ('HILLS_DOUBLE', 1), ('CITY_ATTACK', 40, 'HEAL', 15)],
    'AZTEC_JAGUAR': [('JUNGLE_DOUBLE', 1), ('JUNGLE_ATTACK', 50, 'FOREST_ATTACK', 50), ('ALWAYS_HEAL', 1, 'HEAL', 20)],
    'CELTIC_GALLIC_WARRIOR': [('HILLS_ATTACK', 50), ('HILLS_DOUBLE', 1), ('WITHDRAWAL', 40, 'HILLS_DEFENSE', 30)],
    'ROME_PRAETORIAN': [('CITY_ATTACK', 40), ('SAME_TILE_HEAL', 15), ('IGNORE_BUILDING', 1)],
    'GREEK_PHALANX': [('MOUNTED', 50), ('FIRST_STRIKES', 2), ('MELEE', 40, 'HILLS_DEFENSE', 30)],
    'SUMERIAN_VULTURE': [('MELEE', 40), ('CITY_ATTACK', 40), ('FIRST_IMMUNE', 1, 'HEAL', 15)],
    'NATIVE_AMERICA_DOG_SOLDIER': [('FOREST_DEFENSE', 50), ('FOREST_DOUBLE', 1), ('MELEE', 40, 'SAME_TILE_HEAL', 15)],
    'JAPAN_SAMURAI': [('FIRST_STRIKES', 2), ('CITY_ATTACK', 40), ('BLITZ', 1, 'MOVES', 1)],
    'VIKING_BESERKER': [('CITY_ATTACK', 40), ('RIVER', 1, 'MOVES', 1), ('BLITZ', 1)],
    'ZULU_IMPI': [('WITHDRAWAL', 40), ('ENEMY_ROUTE', 1), ('SAME_TILE_HEAL', 20, 'ALWAYS_HEAL', 1)],
    'MAYA_HOLKAN': [('JUNGLE_DEFENSE', 50), ('JUNGLE_DOUBLE', 1), ('MOUNTED', 50, 'FIRST_STRIKES', 2)],
    'HOLY_ROMAN_LANDSKNECHT': [('MELEE', 50), ('MOUNTED', 50), ('FIRST_STRIKES', 2, 'HEAL', 15)],
    'FRENCH_MUSKETEER': [('WITHDRAWAL', 35), ('ENEMY_ROUTE', 1), ('BLITZ', 1)],
    'OTTOMAN_JANISSARY': [('MELEE', 30, 'ARCHER', 30, 'MOUNTED', 30), ('CITY_ATTACK', 40), ('FIRST_STRIKES', 2)],
    'ETHIOPIAN_OROMO_WARRIOR': [('FIRST_STRIKES', 2), ('HILLS_DEFENSE', 50), ('HILLS_DOUBLE', 1, 'HEAL', 20)],
    'ENGLISH_REDCOAT': [('GUN', 40), ('AMPHIB', 1, 'RIVER', 1), ('FIRST_STRIKES', 2, 'CITY_DEFENSE', 30)],
    'AMERICAN_NAVY_SEAL': [('FIRST_STRIKES', 2), ('ENEMY_ROUTE', 1), ('BLITZ', 1, 'MOVES', 1)],
    'MALI_SKIRMISHER': [('WITHDRAWAL', 40), ('MOVES', 1), ('HILLS_DEFENSE', 50, 'FIRST_STRIKES', 2)],
    'BABYLON_BOWMAN': [('MELEE', 50), ('CITY_DEFENSE', 40), ('FIRST_STRIKES', 2, 'SAME_TILE_HEAL', 15)],
    'CHINA_CHOKONU': [('COLLATERAL_TARGETS', 3), ('COLLATERAL_LIMIT', 20), ('BLITZ', 1, 'MOVES', 1)],
    'EGYPT_WARCHARIOT': [('ARCHER', 50), ('WITHDRAWAL', 40), ('MOVES', 1, 'BLITZ', 1)],
    'PERSIA_IMMORTAL': [('CITY_ATTACK', 40), ('SAME_TILE_HEAL', 15), ('ALWAYS_HEAL', 1, 'HEAL', 25)],
    'CARTHAGE_NUMIDIAN_CAVALRY': [('MELEE', 40), ('WITHDRAWAL', 40), ('ENEMY_ROUTE', 1, 'MOVES', 1)],
    'MONGOL_KESHIK': [('WITHDRAWAL', 40), ('ENEMY_ROUTE', 1), ('BLITZ', 1, 'MOVES', 1)],
    'ARABIA_CAMELARCHER': [('MOUNTED', 40), ('HEAL', 25, 'ALWAYS_HEAL', 1), ('BLITZ', 1, 'MOVES', 1)],
    'BYZANTINE_CATAPHRACT': [('MELEE', 40), ('FIRST_IMMUNE', 1), ('CITY_ATTACK', 40, 'WITHDRAWAL', 35)],
    'SPANISH_CONQUISTADOR': [('GUN', 35), ('AMPHIB', 1, 'RIVER', 1), ('CITY_ATTACK', 40, 'SAME_TILE_HEAL', 15)],
    'RUSSIA_COSSACK': [('MOUNTED', 50), ('WITHDRAWAL', 40), ('BLITZ', 1, 'MOVES', 1)],
    'KHMER_BALLISTA_ELEPHANT': [('MOUNTED', 50), ('COLLATERAL', 40, 'COLLATERAL_TARGETS', 4, 'COLLATERAL_LIMIT', 50), ('FIRST_IMMUNE', 1)],
    'GERMAN_PANZER': [('ARMOR', 50), ('WITHDRAWAL', 40), ('MOVES', 1, 'ENEMY_ROUTE', 1)],
    'KOREAN_HWACHA': [('MELEE', 50), ('COLLATERAL_TARGETS', 4), ('COLLATERAL_LIMIT', 25, 'WITHDRAWAL', 35)],
    'PORTUGAL_CARRACK': [('HEAL', 20, 'ALWAYS_HEAL', 1), ('VISIBILITY', 2), ('MOVES', 2, 'WITHDRAWAL', 35)],
    'NETHERLANDS_OOSTINDIEVAARDER': [('FIRST_STRIKES', 2), ('HEAL', 25, 'ALWAYS_HEAL', 1), ('MOVES', 2)],
    'ADENA_WOODLAND_WARRIOR': [('FOREST_ATTACK', 50, 'FOREST_DEFENSE', 50), ('FOREST_DOUBLE', 1), ('SAME_TILE_HEAL', 15, 'FIRST_STRIKES', 2)],
}

# Armed transports are deliberately excluded: mastery is for fighting units.
EXCLUDED = {'UNIT_GALLEY', 'UNIT_GALLEON', 'UNIT_PORTUGAL_CARRACK',
            'UNIT_NETHERLANDS_OOSTINDIEVAARDER', 'UNIT_TRANSPORT', 'UNIT_COG'}
# Carracks/East Indiamen retain a combat role and their unique mastery tracks.
EXCLUDED -= {'UNIT_PORTUGAL_CARRACK', 'UNIT_NETHERLANDS_OOSTINDIEVAARDER'}

PHRASES = {
    'COMBAT': '+{n}% combat strength', 'MOVES': '+{n} movement',
    'FIRST_STRIKES': '+{n} first strikes', 'WITHDRAWAL': '+{n}% withdrawal chance',
    'COLLATERAL': '+{n}% collateral damage', 'COLLATERAL_LIMIT': '+{n}% collateral damage limit',
    'COLLATERAL_TARGETS': '+{n} collateral targets', 'CITY_ATTACK': '+{n}% city attack',
    'CITY_DEFENSE': '+{n}% city defense', 'HILLS_ATTACK': '+{n}% hills attack',
    'HILLS_DEFENSE': '+{n}% hills defense', 'FOREST_ATTACK': '+{n}% forest attack',
    'FOREST_DEFENSE': '+{n}% forest defense', 'JUNGLE_ATTACK': '+{n}% jungle attack',
    'JUNGLE_DEFENSE': '+{n}% jungle defense', 'MELEE': '+{n}% against melee units',
    'MOUNTED': '+{n}% against mounted units', 'ARCHER': '+{n}% against archery units',
    'GUN': '+{n}% against gunpowder units', 'ARMOR': '+{n}% against armored units',
    'SIEGE': '+{n}% against siege units', 'NAVAL': '+{n}% against naval units',
    'ANIMAL': '+{n}% against animals', 'HEAL': 'Heals {n} extra HP per turn',
    'SAME_TILE_HEAL': 'Units on the same tile heal {n} extra HP per turn',
    'BLITZ': 'Can attack multiple times per turn', 'AMPHIB': 'No amphibious attack penalty',
    'RIVER': 'No river attack penalty', 'ENEMY_ROUTE': 'Can use enemy roads',
    'ALWAYS_HEAL': 'Can heal while moving', 'HILLS_DOUBLE': 'Double movement in hills',
    'FOREST_DOUBLE': 'Double movement in forests', 'JUNGLE_DOUBLE': 'Double movement in jungle',
    'FIRST_IMMUNE': 'Immune to first strikes', 'IGNORE_TERRAIN': 'Ignores terrain movement costs',
    'IGNORE_BUILDING': 'Ignores building defenses', 'BOMBARD': '+{n}% city bombardment',
    'VISIBILITY': '+{n} visibility range',
}

# Reward wording is kept in one place so all 249 text entries stay consistent.
GERMAN = {
    'COMBAT': '+{n}% Kampfstärke', 'MOVES': '+{n} Bewegung',
    'FIRST_STRIKES': '+{n} Erstangriffe', 'WITHDRAWAL': '+{n}% Rückzugschance',
    'COLLATERAL': '+{n}% Kollateralschaden', 'COLLATERAL_LIMIT': '+{n}% Kollateralschadensgrenze',
    'COLLATERAL_TARGETS': '+{n} Kollateralziele', 'CITY_ATTACK': '+{n}% Stadtangriff',
    'CITY_DEFENSE': '+{n}% Stadtverteidigung', 'HILLS_ATTACK': '+{n}% Hügelangriff',
    'HILLS_DEFENSE': '+{n}% Hügelverteidigung', 'FOREST_ATTACK': '+{n}% Waldangriff',
    'FOREST_DEFENSE': '+{n}% Waldverteidigung', 'JUNGLE_ATTACK': '+{n}% Dschungelangriff',
    'JUNGLE_DEFENSE': '+{n}% Dschungelverteidigung', 'MELEE': '+{n}% gegen Nahkampfeinheiten',
    'MOUNTED': '+{n}% gegen berittene Einheiten', 'ARCHER': '+{n}% gegen Bogenschützen',
    'GUN': '+{n}% gegen Schießpulvereinheiten', 'ARMOR': '+{n}% gegen Panzereinheiten',
    'SIEGE': '+{n}% gegen Belagerungseinheiten', 'NAVAL': '+{n}% gegen Marineeinheiten',
    'ANIMAL': '+{n}% gegen Tiere', 'HEAL': 'Heilt {n} zusätzliche TP pro Runde',
    'SAME_TILE_HEAL': 'Einheiten auf demselben Feld heilen {n} zusätzliche TP pro Runde',
    'BLITZ': 'Kann mehrmals pro Runde angreifen', 'AMPHIB': 'Kein Malus bei amphibischen Angriffen',
    'RIVER': 'Kein Angriffsmalus über Flüsse', 'ENEMY_ROUTE': 'Kann feindliche Straßen nutzen',
    'ALWAYS_HEAL': 'Kann während der Bewegung heilen', 'HILLS_DOUBLE': 'Doppelte Bewegung auf Hügeln',
    'FOREST_DOUBLE': 'Doppelte Bewegung im Wald', 'JUNGLE_DOUBLE': 'Doppelte Bewegung im Dschungel',
    'FIRST_IMMUNE': 'Immun gegen Erstangriffe', 'IGNORE_TERRAIN': 'Ignoriert Geländebewegungskosten',
    'IGNORE_BUILDING': 'Ignoriert Gebäudeverteidigung', 'BOMBARD': '+{n}% Stadtbombardierung',
    'VISIBILITY': '+{n} Sichtweite',
}
FRENCH = {
    'COMBAT': '+{n}% de force', 'MOVES': '+{n} mouvement', 'FIRST_STRIKES': '+{n} premières frappes',
    'WITHDRAWAL': '+{n}% de chances de retraite', 'COLLATERAL': '+{n}% de dégâts collatéraux',
    'COLLATERAL_LIMIT': '+{n}% à la limite des dégâts collatéraux', 'COLLATERAL_TARGETS': '+{n} cibles collatérales',
    'CITY_ATTACK': '+{n}% en attaque de ville', 'CITY_DEFENSE': '+{n}% en défense de ville',
    'HILLS_ATTACK': '+{n}% en attaque sur collines', 'HILLS_DEFENSE': '+{n}% en défense sur collines',
    'FOREST_ATTACK': '+{n}% en attaque en forêt', 'FOREST_DEFENSE': '+{n}% en défense en forêt',
    'JUNGLE_ATTACK': '+{n}% en attaque dans la jungle', 'JUNGLE_DEFENSE': '+{n}% en défense dans la jungle',
    'MELEE': '+{n}% contre les unités de mêlée', 'MOUNTED': '+{n}% contre les unités montées',
    'ARCHER': '+{n}% contre les archers', 'GUN': '+{n}% contre les unités à poudre',
    'ARMOR': '+{n}% contre les blindés', 'SIEGE': '+{n}% contre les unités de siège',
    'NAVAL': '+{n}% contre les unités navales', 'ANIMAL': '+{n}% contre les animaux',
    'HEAL': 'Soigne {n} PV supplémentaires par tour',
    'SAME_TILE_HEAL': 'Les unités sur la même case soignent {n} PV supplémentaires par tour',
    'BLITZ': 'Peut attaquer plusieurs fois par tour', 'AMPHIB': "Aucune pénalité d'attaque amphibie",
    'RIVER': "Aucune pénalité d'attaque à travers une rivière", 'ENEMY_ROUTE': 'Peut utiliser les routes ennemies',
    'ALWAYS_HEAL': 'Peut se soigner en mouvement', 'HILLS_DOUBLE': 'Mouvement doublé sur les collines',
    'FOREST_DOUBLE': 'Mouvement doublé en forêt', 'JUNGLE_DOUBLE': 'Mouvement doublé dans la jungle',
    'FIRST_IMMUNE': 'Insensible aux premières frappes', 'IGNORE_TERRAIN': 'Ignore les coûts de mouvement du terrain',
    'IGNORE_BUILDING': 'Ignore les défenses des bâtiments', 'BOMBARD': '+{n}% au bombardement des villes',
    'VISIBILITY': '+{n} portée de vision',
}
ITALIAN = {
    'COMBAT': '+{n}% forza', 'MOVES': '+{n} movimento', 'FIRST_STRIKES': '+{n} primi colpi',
    'WITHDRAWAL': '+{n}% probabilità di ritirata', 'COLLATERAL': '+{n}% danni collaterali',
    'COLLATERAL_LIMIT': '+{n}% al limite dei danni collaterali', 'COLLATERAL_TARGETS': '+{n} bersagli collaterali',
    'CITY_ATTACK': '+{n}% attacco alle città', 'CITY_DEFENSE': '+{n}% difesa delle città',
    'HILLS_ATTACK': '+{n}% attacco sulle colline', 'HILLS_DEFENSE': '+{n}% difesa sulle colline',
    'FOREST_ATTACK': '+{n}% attacco nelle foreste', 'FOREST_DEFENSE': '+{n}% difesa nelle foreste',
    'JUNGLE_ATTACK': '+{n}% attacco nella giungla', 'JUNGLE_DEFENSE': '+{n}% difesa nella giungla',
    'MELEE': '+{n}% contro unità da mischia', 'MOUNTED': '+{n}% contro unità a cavallo',
    'ARCHER': '+{n}% contro arcieri', 'GUN': '+{n}% contro unità con armi da fuoco',
    'ARMOR': '+{n}% contro unità corazzate', 'SIEGE': '+{n}% contro unità da assedio',
    'NAVAL': '+{n}% contro unità navali', 'ANIMAL': '+{n}% contro animali',
    'HEAL': 'Recupera {n} PF aggiuntivi per turno',
    'SAME_TILE_HEAL': 'Le unità sulla stessa casella recuperano {n} PF aggiuntivi per turno',
    'BLITZ': 'Può attaccare più volte per turno', 'AMPHIB': 'Nessuna penalità agli attacchi anfibi',
    'RIVER': 'Nessuna penalità agli attacchi attraverso fiumi', 'ENEMY_ROUTE': 'Può usare le strade nemiche',
    'ALWAYS_HEAL': 'Può curarsi in movimento', 'HILLS_DOUBLE': 'Movimento doppio sulle colline',
    'FOREST_DOUBLE': 'Movimento doppio nelle foreste', 'JUNGLE_DOUBLE': 'Movimento doppio nella giungla',
    'FIRST_IMMUNE': 'Immune ai primi colpi', 'IGNORE_TERRAIN': 'Ignora i costi di movimento del terreno',
    'IGNORE_BUILDING': 'Ignora le difese degli edifici', 'BOMBARD': '+{n}% bombardamento delle città',
    'VISIBILITY': '+{n} raggio visivo',
}
SPANISH = {
    'COMBAT': '+{n}% fuerza', 'MOVES': '+{n} movimiento', 'FIRST_STRIKES': '+{n} primeros ataques',
    'WITHDRAWAL': '+{n}% probabilidad de retirada', 'COLLATERAL': '+{n}% daños colaterales',
    'COLLATERAL_LIMIT': '+{n}% al límite de daños colaterales', 'COLLATERAL_TARGETS': '+{n} objetivos colaterales',
    'CITY_ATTACK': '+{n}% ataque a ciudades', 'CITY_DEFENSE': '+{n}% defensa de ciudades',
    'HILLS_ATTACK': '+{n}% ataque en colinas', 'HILLS_DEFENSE': '+{n}% defensa en colinas',
    'FOREST_ATTACK': '+{n}% ataque en bosques', 'FOREST_DEFENSE': '+{n}% defensa en bosques',
    'JUNGLE_ATTACK': '+{n}% ataque en selva', 'JUNGLE_DEFENSE': '+{n}% defensa en selva',
    'MELEE': '+{n}% contra unidades cuerpo a cuerpo', 'MOUNTED': '+{n}% contra unidades montadas',
    'ARCHER': '+{n}% contra arqueros', 'GUN': '+{n}% contra unidades de pólvora',
    'ARMOR': '+{n}% contra unidades blindadas', 'SIEGE': '+{n}% contra unidades de asedio',
    'NAVAL': '+{n}% contra unidades navales', 'ANIMAL': '+{n}% contra animales',
    'HEAL': 'Recupera {n} PV adicionales por turno',
    'SAME_TILE_HEAL': 'Las unidades en la misma casilla recuperan {n} PV adicionales por turno',
    'BLITZ': 'Puede atacar varias veces por turno', 'AMPHIB': 'Sin penalización por ataque anfibio',
    'RIVER': 'Sin penalización por atacar a través de ríos', 'ENEMY_ROUTE': 'Puede usar caminos enemigos',
    'ALWAYS_HEAL': 'Puede curarse en movimiento', 'HILLS_DOUBLE': 'Movimiento doble en colinas',
    'FOREST_DOUBLE': 'Movimiento doble en bosques', 'JUNGLE_DOUBLE': 'Movimiento doble en selva',
    'FIRST_IMMUNE': 'Inmune a primeros ataques', 'IGNORE_TERRAIN': 'Ignora los costes de movimiento del terreno',
    'IGNORE_BUILDING': 'Ignora las defensas de edificios', 'BOMBARD': '+{n}% bombardeo de ciudades',
    'VISIBILITY': '+{n} alcance visual',
}
LOCAL_PHRASES = dict(zip(LANGS, (PHRASES, FRENCH, GERMAN, ITALIAN, SPANISH)))
RULES = dict(zip(LANGS, (
    'Three levels. Level I uses the base cost of the most expensive required technology, or 100 if none is required. Normal research modifiers apply. Each further level doubles the cost. Ends when a successor is unlocked.',
    "Trois niveaux. Le niveau I utilise le coût de base de la technologie requise la plus chère, ou 100 si aucune n'est requise. Les modificateurs de recherche habituels s'appliquent. Chaque niveau suivant double le coût. Se termine au déblocage d'un successeur.",
    'Drei Stufen. Stufe I nutzt die Basiskosten der teuersten benötigten Technologie, oder 100 ohne benötigte Technologie. Die üblichen Forschungsmodifikatoren gelten. Jede weitere Stufe verdoppelt die Kosten. Endet, sobald ein Nachfolger freigeschaltet ist.',
    'Tre livelli. Il livello I usa il costo base della tecnologia richiesta più costosa, o 100 se non ne è richiesta alcuna. Si applicano i normali modificatori di ricerca. Ogni livello successivo raddoppia il costo. Termina quando si sblocca un successore.',
    'Tres niveles. El nivel I usa el coste base de la tecnología requerida más cara, o 100 si no se requiere ninguna. Se aplican los modificadores de investigación habituales. Cada nivel posterior duplica el coste. Termina al desbloquear un sucesor.',
)))
DETAILS = dict(zip(LANGS, (
    "Benefits are cumulative and apply to existing and newly trained units of this type. Resources and buildings do not affect research access. Upgrading uses the destination unit's mastery; earlier types do not stack. Research is shared by teammates. Obsolete units retain completed benefits.",
    "Les avantages se cumulent et concernent les unités existantes et futures de ce type. Les ressources et bâtiments ne limitent pas la recherche. Une modernisation utilise la maîtrise du nouveau type. Les coéquipiers partagent la recherche. Les unités obsolètes conservent les avantages acquis.",
    'Die Vorteile summieren sich und gelten für bestehende und neu ausgebildete Einheiten dieses Typs. Ressourcen und Gebäude begrenzen den Forschungszugang nicht. Aufgerüstete Einheiten nutzen nur die Meisterschaft des neuen Typs. Teammitglieder teilen die Forschung. Veraltete Einheiten behalten abgeschlossene Vorteile.',
    'I benefici sono cumulativi e valgono per le unità esistenti e future di questo tipo. Risorse ed edifici non limitano la ricerca. Un ammodernamento usa solo la maestria del nuovo tipo. I compagni di squadra condividono la ricerca. Le unità obsolete conservano i benefici acquisiti.',
    'Las ventajas se acumulan y afectan a las unidades existentes y futuras de este tipo. Los recursos y edificios no limitan la investigación. Al modernizarse se usa solo la maestría del nuevo tipo. Los compañeros de equipo comparten la investigación. Las unidades obsoletas conservan las ventajas obtenidas.',
)))
COMBAT_RULE = dict(zip(LANGS, (
    'Each combat advances available mastery research for both combatants, even on defeat or withdrawal.',
    'Chaque combat fait progresser la recherche de maîtrise disponible des deux combattants, même en cas de défaite ou de retraite.',
    'Jeder Kampf bringt beiden Kämpfern Fortschritt bei verfügbarer Meisterschaftsforschung, auch bei Niederlage oder Rückzug.',
    'Ogni combattimento fa avanzare la ricerca di maestria disponibile per entrambi i combattenti, anche in caso di sconfitta o ritirata.',
    'Cada combate hace avanzar la investigación de maestría disponible de ambos combatientes, incluso en caso de derrota o retirada.',
)))


def load(path):
    root = ET.parse(path).getroot()
    for e in root.iter():
        e.tag = e.tag.split('}')[-1]
    return root


def effects(reward):
    return list(zip(reward[::2], reward[1::2]))


def describe(reward, language='English'):
    return '; '.join(LOCAL_PHRASES[language][k].format(n=n) for k, n in effects(reward)) + '.'


def write_mastery_tiles():
    """Small opaque UI backgrounds; native tech panels do not shrink this far."""
    directory = MOD / 'Assets/Art/Interface/Buttons/UnitMastery'
    directory.mkdir(parents=True, exist_ok=True)
    header = struct.pack('<4s31I', b'DDS ', 124, 0x100F, 32, 32, 128, 0, 0,
                         *([0] * 11), 32, 0x41, 0, 32,
                         0xFF0000, 0xFF00, 0xFF, 0xFF000000, 0x1000, 0, 0, 0, 0)
    for name, rgb in (('Complete', (75, 155, 80)), ('Researching', (65, 190, 215)),
                      ('Available', (80, 95, 155)), ('Unavailable', (155, 65, 60))):
        pixels = bytearray()
        for y in range(32):
            for x in range(32):
                delta = 45 if x == 0 or y == 0 else -65 if x == 31 or y == 31 else 0
                red, green, blue = (max(0, min(255, c + delta)) for c in rgb)
                pixels.extend((blue, green, red, 255))
        path = directory / (name + '.dds')
        content = header + pixels
        if not path.exists() or path.read_bytes() != content:
            path.write_bytes(content)


def main():
    write_mastery_tiles()
    units = load(XML / 'Units/CIV4UnitInfos.xml').findall('.//UnitInfo')
    unit_buttons = {art.findtext('Type'): art.findtext('Button')
                    for art in load(XML / 'Art/CIV4ArtDefines_Unit.xml').findall('.//UnitArtInfo')}
    tech_path = XML / 'Technologies/CIV4TechInfos.xml'
    original = tech_path.read_bytes().decode('utf-8')
    techs = {t.findtext('Type'): t for t in load(tech_path).findall('.//TechInfo')}
    unit_text = {}
    for path in (XML / 'Text').glob('*.xml'):
        for t in load(path).findall('.//TEXT'):
            key = t.findtext('Tag')
            if key:
                unit_text[key] = {lang: (t.find(lang).findtext('Text') or t.find(lang).text or '').strip()
                                  for lang in LANGS if t.find(lang) is not None}
    eligible = [u for u in units if int(u.findtext('iCost', '-1')) >= 0
                and int(u.findtext('iCombat', '0')) > 0
                and u.findtext('Type') not in EXCLUDED
                and u.findtext('Domain') != 'DOMAIN_AIR'
                and int(u.findtext('iNukeRange', '-1')) < 0]
    missing = {u.findtext('Type')[5:] for u in eligible} - TRACKS.keys()
    if missing:
        raise ValueError('Design a track for: ' + ', '.join(sorted(missing)))
    # Append in original unit order so reruns preserve all existing tech IDs.
    original = re.sub(r'<TechInfo>\s*<Type>TECH_UNIT_MASTERY_.*?</TechInfo>\s*', '', original, flags=re.S)
    additions, texts, data, table = [], [], [], []
    # Resolve the unit's name at runtime, including base-game translations.
    texts.append(('TXT_KEY_UNIT_MASTERY_NAME', dict(zip(LANGS, (
        '%s1_UnitName Mastery', '%s1_UnitName Maîtrise', '%s1_UnitName Meisterschaft',
        '%s1_UnitName Maestria', '%s1_UnitName Maestría')))))
    max_y = max(int(t.findtext('iGridY', '-1')) for name, t in techs.items()
                if not name.startswith('TECH_UNIT_MASTERY_'))
    max_x = max(int(t.findtext('iGridX', '-1')) for name, t in techs.items()
                if not name.startswith('TECH_UNIT_MASTERY_'))
    columns = {}
    for u in eligible:
        name = u.findtext('Type')
        suffix = name[5:]
        tech_name = 'TECH_UNIT_MASTERY_' + suffix
        key = 'TXT_KEY_' + tech_name
        rewards = TRACKS[suffix]
        assert len(rewards) == 3
        # UnitInfo has no Button field: the engine obtains it from unit art.
        art_type = u.findtext('UnitMeshGroups/UnitMeshGroup/EarlyArtDefineTag')
        button = unit_buttons.get(art_type)
        if not button or not button.strip():
            raise ValueError('Missing mastery research icon for ' + name)
        prereqs = [u.findtext('PrereqTech')] + [t.text for t in u.findall('TechTypes/PrereqTech')]
        prereqs = list(dict.fromkeys(t for t in prereqs if t and t != 'NONE'))
        cost_tech = max(prereqs, key=lambda p: int(techs[p].findtext('iCost'))) if prereqs else None
        base_cost = int(techs[cost_tech].findtext('iCost')) if cost_tech else MASTERY_NO_TECH_BASE_COST
        x = max([1] + [int(techs[t].findtext('iGridX')) for t in prereqs])
        # Keep the section within the existing width and stack collisions.
        x = min(x, max_x)
        row = columns.get(x, 0)
        columns[x] = row + 1
        t = copy.deepcopy(techs['TECH_FUTURE_TECH'])
        values = {'Type': tech_name, 'Description': key, 'Civilopedia': key + '_PEDIA',
                  'Help': key + '_HELP', 'Strategy': key + '_PEDIA', 'iCost': str(base_cost),
                  'bDisable': '0', 'bRepeat': '1', 'bTrade': '0', 'bGoodyTech': '0',
                  'iHealth': '0', 'iHappiness': '0', 'iAsset': '0', 'iPower': '0',
                  'iAIWeight': '0', 'iAdvancedStartCost': '-1', 'iFirstFreeTechs': '0',
                  'iGridX': str(x), 'iGridY': str(max_y + 3 + row * 2),
                  'Era': techs[cost_tech].findtext('Era') if cost_tech else 'ERA_ANCIENT',
                  'Button': button, 'Quote': ''}
        for tag, value in values.items():
            t.find(tag).text = value
        for tag in ('OrPreReqs', 'AndPreReqs', 'Flavors'):
            t.find(tag).clear()
        for p in prereqs:
            ET.SubElement(t.find('AndPreReqs'), 'PrereqTech').text = p
        additions.append('\n'.join(line.rstrip() for line in ET.tostring(t, encoding='unicode').splitlines()).strip())
        names = unit_text.get(u.findtext('Description'), {})
        en = names.get('English', suffix.replace('_', ' ').title())
        labels = ('Mastery', 'Maîtrise', 'Meisterschaft', 'Maestria', 'Maestría')
        texts.append((key, {lang: names.get(lang, en) + ' ' + label
                            for lang, label in zip(LANGS, labels)}))
        help_text = {lang: '[NEWLINE]'.join('%s: %s' % (roman, describe(reward, lang))
                                          for roman, reward in zip(('I', 'II', 'III'), rewards))
                           for lang in LANGS}
        texts.append((key + '_HELP', help_text))
        texts.append((key + '_PEDIA', {lang: help_text[lang] + '[PARAGRAPH:1]' + RULES[lang]
                                    + '[PARAGRAPH:1]' + DETAILS[lang]
                                    + '[PARAGRAPH:1]' + COMBAT_RULE[lang] for lang in LANGS}))
        for level, reward in enumerate(rewards, 1):
            for effect, value in effects(reward):
                data.append('    {"%s", %d, MASTERY_%s, %d},' % (name, level, effect, value))
        table.append('| %s | %s | %s | %s | %s |' % (en, base_cost, *(describe(r) for r in rewards)))
    original = original.replace('</TechInfos>', '\n' + '\n'.join(additions) + '\n</TechInfos>')
    tech_path.write_bytes(original.encode('utf-8'))
    blocks = ['<?xml version="1.0" encoding="UTF-8"?>', '<Civ4GameText xmlns="http://www.firaxis.com">']
    for key, translations in texts:
        blocks.append('  <TEXT><Tag>%s</Tag>%s</TEXT>' % (key, ''.join(
            '<%s>%s</%s>' % (lang, escape(translations[lang]), lang) for lang in LANGS)))
    blocks.append('</Civ4GameText>')
    (XML / 'Text/CIV4GameText_UnitMastery.xml').write_bytes(('\n'.join(blocks) + '\n').encode('ascii', 'xmlcharrefreplace'))
    (MOD / 'CvGameCoreDLL/UnitMasteryData.inc').write_text(
        '// Generated by tools/generate_unit_mastery.py. Edit the generator.\n' + '\n'.join(data) + '\n', encoding='ascii')
    doc = '''# Military unit mastery

Military fighting units have three cumulative, unit-specific mastery levels.
Each level costs twice the previous one: base, 2x base, 4x base. The base is
the base XML research cost of the unit's most expensive required technology.
The mastery uses that technology's era for research cost modifiers. Warriors
require no technology and use a fallback base cost of 100. Normal research
modifiers still apply; technology diffusion discounts do not apply to mastery.
Calendar thresholds do not reprice research. Unit production costs and reward
strength do not change the research cost. Research unlocks with all unit technology
requirements and ends at III or when an upgrade successor is technologically
available, independently of resources/buildings. Unique units use their own
tracks; civilizations cannot research another civilization's replacement.

Each direct combat grants both participants' teams 1% of their exact unit type's
next mastery level's total research cost, whether attacking, defending, losing
or withdrawing. Mastery need not be selected for research, but must currently be
researchable. Collateral victims and civilian captures do not grant progress.
The XML define UNIT_MASTERY_COMBAT_RESEARCH_PERCENT controls the percentage;
0 disables it. Awards round down to whole research points, with a minimum of 1,
and are capped at the current level's remaining cost without research overflow.

Bonuses follow the current owner's team and exact unit type. Existing and new
units benefit; upgrading switches tracks. Surviving obsolete units retain
completed benefits. No promotions are added or transferred. Existing unique
powers and capped global Military Research remain active and stack normally.
Unfinished retired research returns to the acquiring player's research overflow.

Small mastery icons sit below the ordinary tree without arrows, grouped side
by side within their unlocking technology's column. The dialog grows to fit
the row; shorter screens use tighter spacing to avoid vertical scrolling.
Research help lists
all three rewards; the research name shows the next level, such as Archer
Mastery I, II, or III. Completed tracks remain labeled III. General rules are
in the Civilopedia rather than the hover text. The top research bar shows
the research name and turns remaining. Unit tooltips only append (I), (II), or (III) to the name;
unmastered units have no suffix. Visible enemies follow the same display rule.
No map badges or mastery effect explanations are added to unit tooltips.

Civilian/transport units, aircraft and nuclear weapons are excluded. Aircraft
remain disabled by the existing mod rules. Armed exploration and unique
Carrack/East Indiaman combat ships have tracks. No existing-save compatibility
is required. Run `python tools/generate_unit_mastery.py` after changing tracks
or unit/tech prerequisites, then rebuild with the legacy VC7.1 toolchain.
Research names, reward descriptions and rules include all five languages.

Gameplay and multiplayer validation are user-operated and remain unverified.

| Unit | Base cost | I | II | III |
| --- | ---: | --- | --- | --- |
'''
    (ROOT / 'docs/UnitMastery.md').write_text(doc + '\n'.join(table) + '\n', encoding='utf-8')
    print('Generated %d military mastery tracks.' % len(eligible))


if __name__ == '__main__':
    main()
