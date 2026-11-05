"""Tile-sized city-name refinements for the 200 x 110 world.

Coordinates follow the authored XL map, not a longitude/latitude projection.
Each entry is (reference civilization, x, y, name). Other civilizations inherit
the refinement only where they already use the same regional name. Separate
historical/exonym forms below handle cultures with a different vocabulary.
Keep these patches local: a nearby founding tile may still use the parent city.
"""

SITES = (
    # Nile: distinguish Upper Egyptian centres and the branches of the Delta.
    (0, 112, 51, 'Nubt'),
    (0, 112, 53, 'Nekhen'),
    (0, 111, 55, 'Abdju'),
    (0, 110, 56, 'Khmun'),
    (0, 111, 57, 'Iunu'),
    (0, 108, 59, 'Sau'),
    (0, 109, 59, 'Behdet'),
    (0, 113, 58, 'Djedet'),
    # India and Sri Lanka.
    (1, 145, 50, 'Kozhikode'),
    (1, 147, 51, 'Madurai'),
    (1, 145, 54, 'Mysuru'),
    (1, 148, 53, 'Kanchipuram'),
    (1, 149, 55, 'Nellore'),
    (1, 143, 57, 'Pune'),
    (1, 145, 58, 'Pratishthana'),
    (1, 146, 60, 'Vidisha'),
    (1, 148, 60, 'Nagpur'),
    (1, 143, 61, 'Ajmer'),
    (1, 146, 64, 'Mathura'),
    (1, 147, 65, 'Kannauj'),
    (1, 146, 66, 'Thanesar'),
    (1, 144, 67, 'Amritsar'),
    (1, 150, 62, 'Prayaga'),
    (1, 153, 62, 'Tamralipti'),
    (1, 154, 64, 'Sonargaon'),
    (1, 151, 48, 'Polonnaruwa'),
    # China: opened basins, river valleys and finer northern/southern regions.
    (2, 162, 68, 'Chengdu'),
    (2, 161, 67, 'Leshan'),
    (2, 163, 68, 'Langzhong'),
    (2, 164, 68, 'Nanchong'),
    (2, 163, 69, 'Guangyuan'),
    (2, 161, 70, 'Baoji'),
    (2, 163, 70, 'Xianyang'),
    (2, 164, 70, 'Tongguan'),
    (2, 167, 70, 'Zhengzhou'),
    (2, 168, 72, 'Shangqiu'),
    (2, 170, 72, 'Yangzhou'),
    (2, 171, 71, 'Suzhou'),
    (2, 172, 69, 'Shaoxing'),
    (2, 173, 68, 'Ningbo'),
    (2, 171, 66, 'Quanzhou'),
    (2, 169, 67, 'Jiujiang'),
    (2, 167, 68, 'Yueyang'),
    (2, 168, 68, 'Jingzhou'),
    (2, 161, 64, 'Dali'),
    (2, 169, 64, 'Foshan'),
    (2, 167, 61, 'Sanya'),
    (2, 163, 74, 'Taiyuan'),
    (2, 164, 75, 'Shijiazhuang'),
    (2, 166, 75, 'Tianjin'),
    (2, 167, 77, 'Tangshan'),
    (2, 165, 78, 'Chengde'),
    (2, 170, 78, 'Liaoyang'),
    (2, 173, 78, 'Dandong'),
    (2, 164, 60, 'Haiphong'),
    # Mesopotamia, Iran and Central Asia.
    (3, 125, 61, 'Eridu'),
    (3, 125, 64, 'Larsa'),
    (3, 125, 66, 'Samarra'),
    (3, 122, 69, 'Edessa'),
    (5, 134, 65, 'Pasargada'),
    (5, 133, 66, 'Yazd'),
    (5, 136, 64, 'Karmana'),
    (5, 138, 64, 'Zranka'),
    (5, 130, 65, 'Gundeshapur'),
    (5, 128, 66, 'Nihavand'),
    (5, 131, 69, 'Qumis'),
    (5, 137, 69, 'Ghazni'),
    (5, 133, 75, 'Paykand'),
    (5, 136, 76, 'Panjikent'),
    (5, 139, 75, 'Kunduz'),
    # Greece and the Roman world.
    (4, 108, 69, 'Thebai'),
    (4, 106, 69, 'Amphissa'),
    (4, 107, 72, 'Thessalonike'),
    (4, 109, 71, 'Amphipolis'),
    (4, 114, 69, 'Knidos'),
    (4, 112, 72, 'Abydos'),
    (6, 93, 64, 'Utica'),
    (6, 94, 61, 'Hadrumetum'),
    (6, 90, 61, 'Thamugadi'),
    (6, 91, 64, 'Thabraca'),
    (6, 99, 59, 'Thubactis'),
    (7, 99, 71, 'Tibur'),
    (7, 98, 72, 'Veii'),
    (7, 96, 73, 'Florentia'),
    (7, 96, 75, 'Bononia'),
    (7, 96, 77, 'Brixia'),
    (7, 99, 76, 'Patavium'),
    (7, 101, 80, 'Lauriacum'),
    (7, 96, 80, 'Castra Regina'),
    # Japan.
    (8, 180, 69, 'Saga'),
    (8, 183, 70, 'Takamatsu'),
    (8, 181, 72, 'Okayama'),
    (8, 182, 73, 'Himeji'),
    (8, 184, 71, 'Nara'),
    (8, 186, 73, 'Hamamatsu'),
    (8, 186, 75, 'Matsumoto'),
    (8, 187, 74, 'Kamakura'),
    (8, 187, 77, 'Utsunomiya'),
    (8, 188, 78, 'Fukushima'),
    (8, 186, 80, 'Hirosaki'),
    (8, 188, 83, 'Abashiri'),
    # Ethiopia and the Horn; West African river and trade centres.
    (9, 116, 46, 'Gondar'),
    (9, 115, 45, 'Bahir Dar'),
    (9, 117, 45, 'Dessie'),
    (9, 117, 48, 'Adwa'),
    (9, 116, 51, 'Asmara'),
    (9, 118, 43, 'Harar'),
    (9, 119, 46, 'Zeila'),
    (9, 113, 48, 'Kassala'),
    (20, 85, 48, 'Kangaba'),
    (20, 84, 47, 'Bamako'),
    (20, 83, 48, 'Segou'),
    (20, 87, 49, 'Mopti'),
    (20, 88, 46, 'Tenkodogo'),
    (20, 90, 46, 'Bono'),
    # Maya and central Mexico.
    (10, 35, 59, 'Calakmul'),
    (10, 37, 58, 'Caracol'),
    (10, 35, 58, 'Yaxchilan'),
    (10, 34, 58, 'Tonina'),
    (10, 35, 60, 'Uxmal'),
    (10, 38, 60, 'Tulum'),
    (10, 37, 55, 'Quirigua'),
    (10, 36, 54, 'Kaminaljuyu'),
    (24, 30, 60, 'Texcoco'),
    (24, 28, 61, 'Tollan'),
    (24, 30, 64, 'Zacateco'),
    (24, 31, 64, 'Tamtoc'),
    # Scandinavia.
    (11, 96, 89, 'Ribe'),
    (11, 101, 90, 'Lund'),
    (11, 101, 92, 'V&#228;xj&#246;'),
    (11, 93, 95, 'Haugesund'),
    (11, 95, 96, 'Hamar'),
    (11, 99, 94, 'V&#228;nersborg'),
    (11, 100, 97, '&#214;rebro'),
    (11, 102, 96, 'Sigtuna'),
    (11, 101, 99, 'Hudiksvall'),
    (11, 104, 101, 'Skellefte&#229;'),
    (11, 100, 103, 'Steinkjer'),
    # Arabia and mainland/island Southeast Asia.
    (12, 120, 55, 'Jiddah'),
    (12, 122, 55, "At-Ta'if"),
    (12, 120, 59, 'Khaybar'),
    (12, 124, 51, 'Shibam'),
    (12, 125, 56, 'Diriyah'),
    (12, 128, 57, 'Al-Hufuf'),
    (12, 120, 61, 'Madaba'),
    (12, 120, 64, 'Bosra'),
    (13, 163, 54, 'Ayutthaya'),
    (13, 162, 56, 'Si Satchanalai'),
    (13, 164, 57, 'Chiang Rai'),
    (13, 165, 53, 'Sambor Prei Kuk'),
    (13, 164, 59, 'Vinh'),
    (13, 161, 50, 'Melaka'),
    (13, 160, 45, 'Jambi'),
    (13, 170, 48, 'Kota Kinabalu'),
    # Iberia.
    (14, 83, 67, 'Ecija'),
    (14, 84, 68, 'Jaen'),
    (14, 86, 71, 'Cuenca'),
    (14, 83, 72, 'Avila'),
    (14, 88, 72, 'Lleida'),
    (14, 89, 73, 'Girona'),
    (14, 80, 74, 'Lugo'),
    (21, 80, 69, 'Santarem'),
    (21, 81, 71, 'Coimbra'),
    (21, 80, 73, 'Braga'),
    (21, 80, 66, 'Lagos'),
    # France, Britain and Ireland.
    (15, 85, 78, 'Poitiers'),
    (15, 86, 76, 'Agen'),
    (15, 89, 77, 'Albi'),
    (15, 90, 76, 'Valence'),
    (15, 90, 78, 'Macon'),
    (15, 86, 79, 'Nantes'),
    (15, 88, 80, 'Chartres'),
    (15, 87, 81, 'Le Mans'),
    (15, 88, 83, 'Caen'),
    (15, 91, 81, 'Troyes'),
    (15, 91, 83, 'Arras'),
    (16, 85, 88, 'St Albans'),
    (16, 85, 86, 'Winchester'),
    (16, 83, 87, 'Bristol'),
    (16, 82, 89, 'Caernarfon'),
    (16, 83, 90, 'Shrewsbury'),
    (16, 85, 90, 'Lincoln'),
    (16, 84, 92, 'Lancaster'),
    (16, 86, 93, 'Durham'),
    (16, 82, 96, 'Dumbarton'),
    (16, 83, 98, 'Elgin'),
    (16, 79, 92, 'Athlone'),
    (16, 80, 93, 'Drogheda'),
    # Germany, the Low Countries and eastern Europe.
    (17, 99, 84, 'Potsdam'),
    (17, 98, 85, 'Magdeburg'),
    (17, 101, 85, 'Neubrandenburg'),
    (17, 97, 85, 'Braunschweig'),
    (17, 96, 83, 'W&#252;rzburg'),
    (17, 99, 83, 'Halle'),
    (17, 99, 80, 'Passau'),
    (17, 101, 81, 'Olm&#252;tz'),
    (19, 93, 85, 'Utrecht'),
    (19, 95, 85, 'Deventer'),
    (19, 91, 84, 'Middelburg'),
    (18, 116, 89, 'Mozhajsk'),
    (18, 118, 90, 'Dmitrov'),
    (18, 117, 88, 'Kolomna'),
    (18, 112, 85, 'Chernigov'),
    (18, 113, 82, 'Cherkassy'),
    (18, 111, 90, 'Staraja Russa'),
    (18, 114, 91, 'Torzhok'),
    (18, 125, 91, 'Svijazhsk'),
    # Andes: coastal valleys and highland centres beyond the old 12 names.
    (22, 41, 39, 'Caral'),
    (22, 41, 38, 'Huaral'),
    (22, 40, 37, 'Chincha'),
    (22, 44, 35, 'Palpa'),
    (22, 45, 33, 'Vilcashuaman'),
    (22, 47, 31, 'Chuquibamba'),
    (22, 49, 30, 'Chucuito'),
    (22, 49, 28, 'Chuquiapu'),
    (22, 39, 41, 'Pacatnamu'),
    (22, 39, 43, 'Cajamarca'),
    (22, 39, 45, 'Huancabamba'),
    (22, 41, 47, 'Latacunga'),
    # Mongolia and North America.
    (23, 161, 82, 'Tsetserleg'),
    (23, 159, 84, 'Uliastai'),
    (23, 154, 82, 'Olgii'),
    (26, 33, 71, 'Fort Worth'),
    (26, 38, 69, 'Baton Rouge'),
    (26, 41, 69, 'Savannah'),
    (26, 43, 75, 'Charlottesville'),
    (26, 45, 75, 'Alexandria'),
    (26, 46, 77, 'Harrisburg'),
    (26, 40, 75, 'Louisville'),
    (26, 41, 77, 'Fort Wayne'),
    (26, 38, 78, 'Rockford'),
    (26, 35, 80, 'Saint Paul'),
    (26, 35, 76, 'Topeka'),
    (26, 30, 77, 'Boulder'),
    (26, 48, 80, 'Portsmouth'),
)

# Additional names for a culture whose parent label differs at the same tile.
# These are refinements of the *same* site, so conquest can change its exonym.
VARIANTS = {
    'St Albans': {'Londinium': 'Verulamium', 'Londres': 'St Albans'},
    'Winchester': {'Londinium': 'Venta Belgarum', 'Londres': 'Winchester'},
    'Bristol': {'Aquae Sulis': 'Abona'},
    'Caernarfon': {'Deva': 'Segontium'},
    'Lincoln': {'Ratae': 'Lindum'},
    'Dumbarton': {'Glasgow': 'Alt Clut'},
    'Florentia': {'Pisa': 'Firenze', 'Pise': 'Florence'},
    'Bononia': {'Parma': 'Bologna', 'Parme': 'Bologne'},
    'Brixia': {'Milan': 'Brescia', 'Mailand': 'Brescia', 'Milano': 'Brescia'},
    'Patavium': {'Venetia': 'Padova', 'Venedig': 'Padua', 'Venise': 'Padoue'},
    'Castra Regina': {'M&#252;nchen': 'Regensburg', 'Munich': 'Ratisbonne'},
    'Thebai': {'Athenae': 'Thebae', 'Athens': 'Thebes', 'Athena': 'Tebe'},
    'Thessalonike': {'Pella': 'Thessalonica'},
    'Knidos': {'Halicarnassus': 'Cnidus'},
    'Utica': {'Carthago': 'Utica', 'Carthage': 'Utique'},
    'Hadrumetum': {'Carthago': 'Hadrumetum', 'Tunis': 'Sousse'},
    'Abdju': {'Al-Uqsur': 'Abydos', 'Diospolis Megale': 'Abydos'},
    'Khmun': {'Niwt-Rst': 'Khmun', 'Al-Uqsur': 'Al-Ashmunayn'},
    'Iunu': {'Memphis': 'Heliopolis', 'Al-Qahirah': 'Ain Shams'},
    'Texcoco': {'Mexico City': 'Texcoco', 'Ciudad de M&#233;xico': 'Texcoco'},
    'Chuquiapu': {'Tiahuanaco': 'La Paz'},
}


def validate_sites(map_text):
    """Fail generation if terrain changes strand an authored naming site."""
    import re
    plots = {}
    for block in re.findall(r'BeginPlot\s+(.*?)EndPlot', map_text, re.S):
        point = tuple(map(int, re.search(r'x=(\d+),y=(\d+)', block).groups()))
        plots[point] = block
    occupied = set()
    for civilization, x, y, name in SITES:
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
    for reference, x, y, name in SITES:
        if (x, y) in protected:
            raise ValueError('XL city-name refinement overlaps a protected city: %s' % ((x, y),))
        row = 109 - y
        parent = original_planes[reference][row][x]
        current = rows[row][x]
        replacement = None
        if civilization == reference or (parent != '-1' and current == parent):
            replacement = name
        else:
            replacement = VARIANTS.get(name, {}).get(current)
        if replacement is not None and replacement != current:
            result[row][x] = replacement
            changes.append((x, y, replacement))
    return tuple(tuple(row) for row in result), tuple(changes)
