"""Historical resource atlas for Large World (offline Python 3 authoring).

Independent of every source-map bonus. Coordinates locate named regions in
RFC's reference projection, NOT longitude/latitude. Each site yields one map
deposit within a small local envelope; there are no civilization quotas.
Years describe regional establishment, not exact first archaeological finds.
Minerals exist initially and retain the game's technology reveal requirements.
See docs/LargeWorld.md for evidence, abstractions and introduction policy.
"""
from collections import Counter
from pathlib import Path
import pprint

# Existing XL deposits at a delta shore and a wilderness margin. Keep their
# original usable cells when refining the coast and applying inland barriers.
XL_RESOURCE_REFUGES = {(64, 43), (167, 23)}  # Carajas iron; Yilgarn iron.


# Commodity | first year (-3000 = initial) | region: reference x,y; ...
# Coarse regional markers, not claims that an entire region grew a crop in one
# year. Game bonuses represent productive local supply, not traded imports.
ATLAS = """
COPPER|-3000|Cyprus:73,41; Sinai:70,34; Timna:72,36; Faynan:73,36; Anatolia:74,44; Balkans:65,46; Rudna Glava:65,48; Mitterberg:61,48; Iberian pyrite belt:51,42; Rio Tinto:50,41; Great Orme:51,54; Ross Island:49,55; Falun:62,60; Urals:81,54; Caucasus:77,46; Iranian plateau:82,41; Oman:82,33; Khetri:89,38; Singhbhum:94,37; Yunnan:100,40; Jiangxi:104,42; Tonglushan:103,44; Japan:115,45; Altai:91,52; Balkhash:89,51; Katanga:66,22; Zambia copperbelt:67,20; Namibia:63,17; Namaqualand:63,13; Atlas:51,37; Akjoujt:50,32; Arizona:15,43; Butte:15,50; Great Lakes:23,50; British Columbia:11,54; Alaska:8,61; Sonora:15,40; Michoacan:17,36; Peru Andes:28,23; Atacama:31,17; central Chile:30,13; Carajas:39,25; Bougainville:122,26; Mount Isa:113,20; South Australia:110,13
IRON|-3000|Weald:53,53; Cumbria:51,56; Lorraine:57,50; Normandy:54,50; Asturias:51,45; Moncayo:54,44; Elba:59,44; Noricum:62,48; Etruria:60,45; Thrace:67,45; Dacia:67,48; Anatolia:75,43; Lebanon:73,39; Nubia:69,30; Meroe:69,28; Algeria:55,38; Morocco:50,36; Sweden Bergslagen:63,60; Kiruna:64,64; Krivyi Rih:71,50; Kursk:72,53; Urals:81,55; central Kazakhstan:88,52; Altai:93,52; Angara:99,54; Liaoning:108,49; Hebei:103,47; Shanxi:101,46; middle Yangtze:104,43; Shandong:106,46; Yunnan:100,41; Karnataka:90,33; Odisha:95,37; Chota Nagpur:94,38; Deccan:90,36; Iran:82,41; Afghanistan:86,43; Korea:110,48; Japan Chugoku:113,44; Nigeria:59,28; Senegal:50,29; Guinea:52,27; Gabon:61,25; Congo:65,23; Zimbabwe:68,17; South Africa:66,13; Minas Gerais:39,20; Carajas:39,25; Marcona:28,21; Labrador:33,55; Mesabi:21,49; Michigan:23,49; Quebec:29,53; Alabama:24,43; Missouri:21,46; California:12,46; Pilbara:104,19; Yilgarn:105,14; South Australia:111,13
GOLD|-3000|Nubia eastern desert:70,30; Egyptian eastern desert:70,33; Ghana Akan:54,26; Bambuk:51,29; Bure:53,28; Lobi:55,28; Zimbabwe:68,17; Witwatersrand:67,13; Tanzania:70,22; Ethiopian highlands:74,28; Dacia:67,48; Thrace:67,45; Lydia:70,43; Armenia:78,44; Asturias:51,45; Wales:51,54; Irish gold:49,55; Urals:81,55; Altai:92,52; Kolyma:116,61; Transbaikal:102,53; Karnataka Kolar:91,33; Hutti:91,35; Shandong:106,46; Yunnan:100,40; Japan Sado:114,47; Sumatra:100,27; Borneo:106,27; New Guinea:119,26; Victoria:114,11; Kalgoorlie:106,13; Ghanaian rivers:55,27; Alaska Yukon:9,61; Klondike:12,59; California Sierra:12,46; Nevada:14,47; Black Hills:18,49; Colorado:17,46; Mexico:18,39; Colombia:27,29; Ecuador:26,26; Peru:28,23; Bolivia:32,21; Minas Gerais:39,20
SILVER|-3000|Laurion:67,42; Siphnos:68,41; Iberian southeast:54,42; Rio Tinto:51,41; Sardinia:58,43; Harz:60,52; Bohemia:62,51; Erzgebirge:61,51; Norway Kongsberg:60,60; Anatolia:73,44; Armenia:78,45; Iran:82,42; Japan Iwami:113,44; Japan Sado:114,47; Korea:110,49; Yunnan:100,40; Mongolia:103,51; Nevada Comstock:13,47; Idaho:14,50; Colorado:17,46; Zacatecas:18,40; Guanajuato:18,38; Taxco:18,36; Potosi:33,20; Peru Pasco:28,23; Peru Huancavelica:28,22; Chile Norte Chico:30,15; Broken Hill:112,13
GEMS|-3000|Golconda:92,35; Panna:92,38; Sri Lanka:93,29; Myanmar Mogok:98,38; Afghanistan Badakhshan:87,44; Sinai turquoise:70,34; Egypt emeralds:70,32; Colombia emeralds:28,28; Brazil Minas Gerais:39,20; Urals:81,55; Altai:93,52; Myanmar jade:98,40; Kashmir:89,42; Thailand Cambodia:102,34; Vietnam rubies:101,38; South Africa Kimberley:65,13; Namibia diamonds:62,15; Angola diamonds:64,21; Congo diamonds:65,23; Tanzania:70,22; Madagascar:75,17; Mozambique:71,17; Australia Argyle:110,21; Brazil Bahia:40,22
COAL|-3000|Northumberland:53,57; Yorkshire:53,55; South Wales:51,53; Scotland:52,58; Ruhr:58,52; Saar:57,50; Wallonia:56,51; Silesia:64,51; Bohemia:62,51; Asturias:51,45; Donbas:73,50; Pechora:78,60; Kuzbass:94,53; Karaganda:88,52; Shanxi:101,46; Shaanxi:100,45; Fushun:108,49; Henan:103,45; Sichuan:100,42; Jharkhand:94,38; Bengal:95,38; central India:92,36; Kyushu:112,42; Hokkaido:114,52; Korea:110,49; Appalachian north:28,47; Appalachian south:26,45; Illinois basin:23,47; Powder River:17,50; Alberta:14,53; Nova Scotia:33,51; Colombia:28,31; South Africa:67,14; Zimbabwe:68,17; New South Wales:117,13; Queensland:117,18; New Zealand South Island:123,9; Kalimantan:107,27; Sumatra:100,27
ALUMINUM|-3000|Guinea bauxite:52,28; Ghana bauxite:55,27; Cameroon:61,27; Jamaica:27,36; Hispaniola:29,37; Guyana:36,30; Suriname:38,29; Brazil Para:39,26; Brazil Minas Gerais:39,20; Arkansas:21,45; Provence:57,47; Hungary:64,49; Dalmatia:64,46; Greece:67,43; Anatolia:73,43; Urals:81,55; India Odisha:95,37; India Gujarat:88,37; China Guizhou:101,41; China Guangxi:103,40; China Henan:103,45; Vietnam central highlands:103,35; Bintan:102,28; Western Australia Darling:104,13; Queensland Weipa:116,22; Northern Territory Gove:111,23
OIL|-3000|Mesopotamia Kirkuk:78,41; Khuzestan:80,39; Persian Gulf offshore:81,36; Kuwait:79,37; eastern Arabia:80,35; Oman:82,33; Baku:79,46; Caspian northeast:81,49; Volga Urals:79,54; West Siberian basin:87,57; Timan Pechora:78,60; Sakhalin:116,53; Daqing:110,52; Shengli:106,46; Tarim:94,47; Assam:97,39; Gujarat:88,37; Punjab Potwar:88,41; Sumatra:100,28; Borneo:107,28; north Java:104,25; Brunei offshore:107,30; Venezuela Maracaibo:29,31; Venezuela Orinoco:33,30; Trinidad:35,32; Mexico Gulf:20,38; Texas:19,43; Oklahoma:20,45; Louisiana offshore:23,41; California:11,45; Alberta:14,54; Alaska north slope:8,64; North Sea west offshore:56,58; North Sea east offshore:59,59; Libya:62,35; Algeria:56,35; Nigeria delta offshore:59,24; Angola offshore:60,20; Gabon offshore:60,24; Egypt Suez:70,35; Sudan:69,28; Kazakhstan:83,50; Norway offshore:57,61; Brazil Santos offshore:40,17; Argentina Patagonia:32,8; Bass Strait offshore:115,9; Northwest Australia offshore:104,22
URANIUM|-3000|Athabasca:19,55; Elliot Lake:25,49; Colorado plateau:16,46; New Mexico:17,43; Niger Arlit:58,32; Namibia Rossing:62,16; South Africa:66,13; Congo Shinkolobwe:66,22; Kazakhstan Chu Sarysu:88,50; Uzbekistan Kyzylkum:84,49; Ukraine:71,51; Czech Bohemia:62,51; France Limousin:55,48; Australia Ranger:110,22; Australia Olympic Dam:110,14; Australia Yeelirrie:106,16; India Jaduguda:94,38; China Jiangxi:104,42; Brazil Bahia:40,22
STONE|-3000|Nile limestone:69,35; Aswan granite:69,32; Sinai:70,34; Levant limestone:73,39; Mesopotamian uplands:78,43; Anatolia:73,44; Aegean:67,43; Malta:61,38; Sicily:61,40; Latium tuff:60,44; Po foothills:60,47; Armorica granite:52,50; Wessex chalk:52,53; Wales slate:51,54; Irish limestone:49,55; Iberian granite:51,43; Portugal limestone:49,43; German sandstone:60,51; Bohemian sandstone:62,51; Scandinavian granite:63,59; Ukrainian granite:70,51; Iranian limestone:81,42; Rajasthan sandstone:89,38; Deccan basalt:90,35; Ganges sandstone:93,39; China central plains:103,45; Fujian granite:107,42; Sichuan sandstone:100,42; Korea granite:110,48; Japan granite:114,45; Angkor sandstone:102,34; Zimbabwe granite:68,17; Ethiopian basalt:74,28; Andean stone:28,23; Yucatan limestone:23,37; central Mexico basalt:18,37; New England granite:31,50; Australia sandstone:117,13
MARBLE|-3000|Carrara:59,46; Pentelikon:67,42; Paros:68,41; Proconnesus:70,44; Dokimeion:72,43; Thasos:68,44; Macedonia:66,45; Pyrenees:54,46; Iberian Estremoz:50,42; Irish Connemara:49,56; Belgian marble:56,51; Norwegian Fauske:62,63; Urals:81,55; Makrana:89,38; Afghanistan:86,43; Yunnan Dali:99,41; Hunan:103,42; Vermont:30,50; Georgia:25,44; British Columbia:11,54
WHEAT|-3000|Lower Nile:68,35; Upper Nile:69,33; Mesopotamia south:77,40; Mesopotamia north:77,42; Levant:73,39; Anatolia:73,44; Iranian plateau:82,41; Indus Punjab:88,41; Indus Sindh:87,38; Ganges northwest:90,40; Bactria:85,45; Sogdia:84,48; Greece:67,43; Thrace:68,45; Danube:65,49; Ukraine:70,51; Italian south:62,42; Sicily:61,40; Po valley:60,47; Tunisia:58,38; Algeria:55,38; Morocco:51,36; Iberian interior:52,44; Guadalquivir:51,42; southern Gaul:55,47; Paris basin:55,50; Rhineland:59,51; British south:53,53; Ireland east:50,55; Jutland:60,55; southern Sweden:63,57
WHEAT|-2000|Tarim oases:93,46; Gansu Hexi:98,47; north China:102,46; Shandong:106,46
WHEAT|-1000|Ethiopian highlands:74,28; eastern Ganges:94,39
WHEAT|1600|central Mexico:18,37; Chile central:30,13
WHEAT|1750|Pennsylvania:29,47; Virginia:28,46; New England:30,49; Argentina Pampas:34,12
WHEAT|1850|US Great Plains north:19,49; US Great Plains south:19,45; Canadian prairie:18,52; Australia southwest:104,13; Australia southeast:115,12; New Zealand Canterbury:123,10
RICE|-3000|lower Yangtze:106,44; middle Yangtze:103,43; Hunan:103,42; south China:105,41
RICE|-2000|middle Ganges:93,39; Bengal:95,38; Assam:97,39; Odisha:95,37; Yunnan:100,41
RICE|-1500|Red River:101,38; Mekong:103,34; central Thailand:101,34; lower Burma:98,35; south India:92,33
RICE|-500|Niger inland delta African rice:54,30; upper Guinea African rice:52,28; Sri Lanka:93,29; Korea:110,48; Japan Kyushu:111,42; Java:104,25; Sumatra:100,27; Luzon:109,34
RICE|900|Iberian Valencia:54,43; Sicily:61,40
RICE|1500|Po valley:60,47
RICE|1750|Carolina lowcountry:28,44; Brazil Maranhao:40,25
RICE|1850|Louisiana:23,43; California Sacramento:12,47
CORN|-3000|Balsas valley:17,36; Oaxaca:19,35; Gulf Mexico lowlands:21,37; Guatemala:22,35; north Peru coast:26,24; Ecuador coastal:25,27
CORN|-1500|Yucatan:23,37; Colombian valleys:28,28; Peru highland valleys:28,23; Bolivia valleys:33,21; Chile central:30,13
CORN|500|Mississippi middle:23,46; Ohio valley:26,47; southwest pueblos:16,43
CORN|1000|Mississippi lower:23,44; Great Lakes south:24,48; Iroquois country:29,49; southeastern US:27,44; southern Brazil:38,17
CORN|1600|Iberian north:51,45; Po valley:61,47; Balkans:66,47; western Africa:55,28; Congo:64,24; India west:89,36; Sichuan:100,42; Yunnan:100,40
CORN|1750|US Corn Belt:23,47; China northeast:108,50; South Africa:67,14
COW|-3000|Nile delta:68,35; Nubia:69,30; Levant:73,39; Mesopotamia:77,41; Anatolia:73,44; Indus Punjab:88,41; Gujarat zebu:88,37; Ganges:92,39; Deccan zebu:91,35; Danube:65,49; Po valley:60,47; Gaul:55,49; Britain:52,54; Ireland:49,56; Denmark:60,55; Sahel west:52,30; Sahel east:59,29; Ethiopian highlands:74,28
COW|-1000|east Africa:70,23; southern Africa:68,16; north China:103,47
COW|1600|Mexico central:18,37; Caribbean Cuba:26,38; Colombia:28,29; Brazil northeast:41,24; Argentina Pampas:35,12
COW|1750|Texas:19,43; US east:28,46; Brazil south:38,17; California:12,45
COW|1850|Australia Queensland:117,18; Australia southeast:116,12; New Zealand North Island:123,12
SHEEP|-3000|Anatolia:74,44; Zagros:80,41; Levant:73,39; Mesopotamia:77,41; Iran:83,42; Indus:88,40; Bactria:85,45; Caucasus:77,46; Balkans:66,47; Greece:67,43; Italy Apennines:61,44; Sardinia:58,43; Iberian meseta:52,44; Gaul uplands:55,48; Britain:52,55; Ireland:49,56; Atlas:51,36; Nile:69,34
SHEEP|-1500|Central Asian steppe:88,52; Mongolia:101,52; north China:103,48
SHEEP|1600|Mexico uplands:18,39; Peru highlands:28,23; Argentina Patagonia:32,9
SHEEP|1800|Australia southwest:104,13; Australia southeast:115,12; Tasmania:115,8
SHEEP|1850|New Zealand South Island:123,10
PIG|-3000|Yangtze:104,43; Yellow River:103,46; Sichuan:100,42; Levant:73,39; Anatolia:73,44; Danube:65,49; Gaul woodland farms:55,49; Rhineland:59,52; southern Britain:53,53; Po valley:60,47; Ganges:93,39; south China:105,41
PIG|-1000|Southeast Asia:101,35; Java:104,25; New Guinea:119,26; Korea:110,48; Japan:114,45
PIG|1600|Mexico:18,37; Cuba:26,38; US southeast:27,44; Brazil:39,20
HORSE|-2200|lower Volga Don:76,51; Pontic steppe:72,50; Kazakhstan steppe:88,52
HORSE|-1500|Anatolia:74,44; Mesopotamia:77,42; Iran:83,42; Indus northwest:88,41; north China:103,48; Mongolia:101,52; Balkans:66,47; Central Europe:62,51; Ukraine:70,51
HORSE|-500|Iberia:52,43; Gaul:55,49; Britain:53,54; Arabia north:76,37; Numidia:55,38; Central Asian oases:85,48
HORSE|1600|Mexico north:17,40; Argentina Pampas:35,12; Chile:30,13
HORSE|1750|US Great Plains:19,47; US Texas:19,43; Canada prairie:18,52; Brazil south:38,17
HORSE|1850|Australia southeast:116,12
BANANA|-3000|New Guinea early cultivation:116,25
BANANA|-1500|Malaysia:101,29; Sumatra:100,27; Java:104,25; Philippines:109,33; south India:92,33; Sri Lanka:93,29
BANANA|500|East African lakes:69,24; coastal East Africa:71,21; Congo southern fringe:65,23
BANANA|1000|Guinea:53,27
BANANA|1600|Caribbean:29,37; Brazil coastal:42,24; Central America:24,33
COTTON|-3000|Indus Sindh:87,38; Gujarat:88,37; Peru north coast:26,24; Peru central coast:27,22
COTTON|-1500|Mesoamerica Gulf:21,37; Maya lowlands:23,36
COTTON|500|Deccan:91,35; Ganges:93,39; Nubia:69,30; Central Asia:84,47
COTTON|1000|Egypt:68,35; Syria:74,40; Iberian south:52,41; Bengal:95,38; south China:105,41
COTTON|1800|US Mississippi:23,44; US Alabama:25,44; US Texas:20,43; Brazil northeast:41,24; Egypt delta expansion:69,35
SUGAR|-3000|New Guinea:119,26
SUGAR|-1000|Ganges:93,39; Bengal:95,38; south India:92,33
SUGAR|500|south China:105,41; Java:104,25
SUGAR|1000|Khuzestan:80,39; Egypt:68,35; Sicily:61,40; Iberian south:52,41
SUGAR|1500|Madeira:47,38; Canaries:46,34
SUGAR|1600|Cuba:26,38; Hispaniola:29,37; Jamaica:27,36; Brazil Pernambuco:43,24; Brazil Bahia:41,22
SUGAR|1750|Louisiana:23,43; Mauritius:79,17
DYE|-3000|Indus indigo:88,38; Indian Deccan indigo:91,35; Bengal indigo:95,38; Levant madder:73,39; Anatolian madder:73,44; European woad:55,49; Britain woad:53,54; China indigo:105,42; Maya indigo:23,36; Peru cochineal:27,23; Mexico cochineal:19,35
DYE|1600|Carolina indigo:28,44; Caribbean indigo:29,37
SILK|-3000|lower Yellow River:104,46; lower Yangtze:106,44; Sichuan:100,42
SILK|200|Korea:110,48; Japan:114,45; India Assam:97,39
SILK|600|Sogdia:84,48; Iran:82,42; Byzantine Anatolia:71,44
SILK|1200|Sicily:61,40; Italy Lucca:59,46; Iberian Valencia:54,43
SPICES|-3000|Malabar pepper:90,32; Sri Lanka cinnamon:93,29; Moluccas cloves:115,27; Banda nutmeg:115,25; Sumatra pepper:100,27; Java spices:104,25; southwest China ginger:100,40; Bengal ginger:95,38; Guinea grains of paradise:52,27
SPICES|1750|Zanzibar cloves:72,21
WINE|-3000|Georgia:78,46; Armenia:78,44; Zagros:80,42; Levant:73,39; Anatolia:72,43; Aegean:67,42; Nile delta:68,35
WINE|-1000|Italy Campania:61,43; Etruria:60,45; Sicily:61,40; Iberian south:52,41; Tunisia:58,38; Greece north:67,44
WINE|-500|Gaul Mediterranean:56,47; Iberian interior:53,44
WINE|200|Bordeaux:53,48; Burgundy:56,49; Rhine:59,51; Moselle:58,51
WINE|1700|Chile central:30,13; Argentina Mendoza:32,13; South Africa Cape:65,10
WINE|1850|California:12,46; Australia south:112,12
INCENSE|-3000|Hadramaut frankincense:79,31; Dhofar frankincense:81,32; Yemen myrrh:76,32; Somalia myrrh:76,25; Ethiopia myrrh:74,27
IVORY|-3000|Guinea elephants:53,27; Akan forest elephants:55,27; Nigeria elephants:59,27; Congo forest elephants:64,25; Cameroon elephants:61,27; Sudan elephants:69,28; Ethiopian lowlands:73,27; East Africa elephants:70,23; Zambezi elephants:69,19; southern Africa elephants:67,14; India Assam elephants:97,39; India eastern elephants:94,37; Sri Lanka elephants:93,29; Myanmar elephants:98,37; Thailand elephants:101,35; Sumatra elephants:100,27; Borneo elephants:107,28
DEER|-3000|Scotland red deer:52,58; Britain woodland:52,55; Gaul red deer:55,49; central Europe red deer:61,52; Poland woodland:65,53; Scandinavia reindeer:64,63; Finland reindeer:68,62; Russia forest:74,57; Urals reindeer:81,60; Siberia west:89,56; Siberia central:99,55; Amur deer:112,54; Japan deer:114,45; Manchuria deer:108,51; Korea deer:110,49; Alaska caribou:8,60; Yukon caribou:12,59; Canada prairie edge:18,53; Quebec caribou:30,54; Great Lakes deer:24,49; Appalachians deer:28,46; Pacific northwest deer:11,51; Patagonia deer:31,10
FUR|-3000|Scotland:52,58; Scandinavia:63,61; Finland:68,61; Novgorod:69,56; Volga forests:76,56; Urals:81,58; Ob basin:87,56; Yenisei:95,56; Baikal:99,54; Amur:112,54; Kamchatka:121,57; Hokkaido:114,52; Alaska:8,60; Yukon:12,59; Mackenzie:17,57; Hudson Bay south:24,53; Quebec:30,54; Great Lakes:24,49; New England:30,50; Pacific northwest:11,52
FISH|-3000|Grand Banks:35,52; Gulf St Lawrence:32,52; Georges Bank:32,49; Chesapeake:30,46; Gulf Maine:32,50; Alaska salmon:7,59; British Columbia salmon:9,54; California current:10,47; Gulf California:14,41; Peru upwelling north:24,25; Peru upwelling south:26,22; Chile upwelling:28,15; Patagonia shelf:36,8; Brazil shelf:44,24; North Sea:57,56; Iceland south:47,63; Norwegian coast:57,61; Barents fringe:67,64; British Atlantic:49,55; Biscay:50,47; Baltic:65,57; Mediterranean west:56,42; Adriatic:63,45; Aegean:68,41; Black Sea:72,47; Morocco upwelling:48,36; Senegal upwelling:47,31; Benguela:61,16; Cape:65,9; Mozambique channel:73,20; Red Sea:72,32; Arabian Sea:85,36; Bay Bengal:96,35; Sri Lanka:95,30; Vietnam coast:104,36; south China coast:108,40; Yellow Sea:108,47; East China Sea:111,43; Japan Pacific:117,45; Hokkaido:118,49; Sea Okhotsk:118,54; Bering Sea:122,59; Java Sea:105,26; Malacca strait:100,29; Philippines:110,33; New Guinea coast:120,28; southeast Australia:119,13; southwest Australia:102,12; New Zealand:122,11
CLAM|-3000|New England shellfish:31,49; Chesapeake shellfish:30,46; Florida Gulf:26,42; California shellfish:11,45; British Columbia shellfish:10,54; Peru coast:25,24; Chile coast:29,13; Brazil south:40,16; Brittany oysters:51,50; Channel oysters:53,52; Ireland shellfish:48,56; Portugal shellfish:48,43; Mediterranean shellfish:60,41; Aegean shellfish:68,42; West Africa estuaries:51,27; East Africa shellfish:72,21; Persian Gulf shellfish:81,35; Bengal estuary:96,37; Vietnam shellfish:103,37; China southeast shellfish:108,42; Korea shellfish:109,48; Japan shellfish:115,44; Thailand Gulf shellfish:102,32; Australia southeast shellfish:118,12; New Zealand shellfish:123,11
CRAB|-3000|Alaska king crab:6,59; Bering king crab:122,60; British Columbia crab:10,54; California Dungeness:11,47; Chesapeake blue crab:30,46; Gulf Mexico blue crab:23,41; Patagonia crab:33,6; Norway crab:58,61; North Sea crab:57,56; Ireland crab:48,55; Iberia crab:49,44; Japan snow crab:114,47; Korea crab:109,48; China coast crab:108,44; Vietnam crab:104,35; Bengal crab:96,37; Java mangrove crab:105,26; Australia north mud crab:111,24; Madagascar mangrove crab:74,19
WHALE|-3000|Bering whales:122,61; Alaska whales:5,59; North Pacific whales:119,52; Japan whales:117,44; North Atlantic whales:41,58; Iceland whales:47,62; Norway whales:57,62; Biscay right whales:49,47; Azores whales:42,45; Newfoundland whales:36,52; California whales:9,45; Peru whales:24,23; Chile whales:27,14; Patagonia whales:36,7; South Africa whales:64,8; Indian Ocean whales:78,18; Australia south whales:110,9; New Zealand whales:121,8
"""

MINERALS = set('COPPER IRON GOLD SILVER GEMS COAL ALUMINUM OIL URANIUM STONE MARBLE'.split())
SEA = set('FISH CLAM CRAB WHALE'.split())
FIELDS = set('WHEAT RICE CORN COW SHEEP PIG HORSE COTTON SUGAR DYE WINE'.split())

# Additional coastal districts for Huge World's longer shores. These mark
# productive shelves, estuaries and upwelling coasts, not uniform ocean density
# or present-day catch quotas. Each anchor still receives at most one deposit.
MARINE_EXTENSIONS = """
FISH|-3000|Newfoundland east banks:36,54; Labrador shelf:35,57; Nova Scotia shelf:33,51; New England outer shelf:32,48; Carolina shelf:30,44; Florida Atlantic:29,41; Louisiana shelf:23,41; Yucatan shelf:24,38; Cuba north shelf:27,39; Guianas shelf:39,31; Brazil northeast shelf:44,26; Brazil southeast shelf:42,20; Rio de la Plata shelf:38,13; Patagonia northern shelf:37,10
FISH|-3000|Alaska Gulf east:9,58; Vancouver outer coast:10,52; Oregon upwelling:10,49; Baja Pacific:12,42; Gulf California north:14,43; Ecuador upwelling:24,28; Peru central upwelling:25,24; Chile northern upwelling:28,19; Chile central upwelling:28,13
FISH|-3000|Iceland west shelf:44,64; Faroes shelf:51,61; Scottish east shelf:55,58; North Sea south banks:57,54; Skagerrak:61,57; Norway central shelf:59,63; Baltic south coast:65,54; Bay Biscay south:51,46; Portuguese upwelling:48,44; Alboran Sea:54,40; Gulf Lion:57,46; Tyrrhenian Sea:59,43; Sicily channel:60,39; Ionian Sea:64,41; Levantine coast:72,39; Black Sea east shelf:76,47
FISH|-3000|Morocco northern shelf:48,38; Mauritania upwelling:47,33; Guinea shelf:50,27; Nigeria shelf:59,25; Angola upwelling:60,20; Namibia upwelling:60,14; Somali upwelling:78,26; Gulf Aden:77,29; Oman upwelling:84,32; Malabar shelf:89,32; Gujarat shelf:87,37; Coromandel shelf:94,33; Bengal outer shelf:96,36
FISH|-3000|Myanmar shelf:98,34; Gulf Thailand:102,33; Mekong shelf:105,34; Gulf Tonkin:105,38; Taiwan Strait:109,41; Shandong shelf:108,46; Korean east shelf:112,48; Japan Seto coast:113,44; Japan Tohoku shelf:117,48; Sakhalin shelf:116,54; Kamchatka shelf:122,56; Sumatra west shelf:99,28; Sunda shelf:103,28; Java south shelf:104,24; Makassar Strait:110,27; Philippines central shelf:110,31; Arafura shelf:116,23; Queensland shelf:119,19; Bass Strait fisheries:115,10; New Zealand east shelf:123,12
CLAM|-3000|Nova Scotia shellfish:33,51; Carolina estuaries:29,44; Gulf Mexico oysters:24,42; Guianas mangrove shellfish:37,31; Brazil northeast estuaries:43,25; Danish shellfish:60,55; Dutch Wadden shellfish:58,53; Galician shellfish:49,46; Tunisia shellfish:59,38; Senegal estuary shellfish:49,30; Mozambique estuary shellfish:72,19; Malabar estuary shellfish:90,32; Guangdong estuary shellfish:107,40; Philippines mangrove shellfish:109,32; Sumatra estuary shellfish:101,28; New Guinea estuary shellfish:119,27
CRAB|-3000|Labrador crab:35,56; Nova Scotia crab:33,50; Oregon crab:10,49; Chile southern crab:30,9; Barents coast crab:68,64; Scottish crab:52,59; Brittany crab:51,49; Oman coast crab:83,33; Myanmar mangrove crab:98,35; Japan Hokkaido crab:116,51; Queensland mud crab:118,20; New Zealand coastal crab:122,10
"""

# Only named rocky districts receive a hard relief requirement. Alluvial gold,
# sedimentary coal/oil basins, bauxite plateaus and ordinary quarries elsewhere
# may legitimately remain flat. Move to an existing local hill first; author a
# small hill/outcrop only if the scaled relief provides no suitable one.
ROCKY_DISTRICTS = {
    'COPPER': {'Sinai', 'Timna', 'Faynan', 'Oman', 'Iranian plateau', 'Atacama', 'central Chile', 'Sonora', 'Arizona', 'Namaqualand'},
    'GOLD': {'Egyptian eastern desert', 'Nubia eastern desert', 'Urals', 'Altai', 'Kalgoorlie'},
    'GEMS': {'Egypt emeralds', 'Sinai turquoise', 'Afghanistan Badakhshan', 'Kashmir', 'Myanmar Mogok'},
    'IRON': {'Nubia', 'Anatolia', 'Urals', 'Altai', 'Yunnan', 'Carajas', 'Pilbara'},
    'SILVER': {'Laurion', 'Harz', 'Bohemia', 'Erzgebirge', 'Urals', 'Nevada Comstock', 'Colorado', 'Zacatecas', 'Guanajuato', 'Taxco', 'Potosi', 'Peru Pasco', 'Peru Huancavelica', 'Chile Norte Chico'},
    'COAL': {'Appalachian north', 'Appalachian south', 'South Wales'},
    'MARBLE': {'Carrara', 'Pentelikon', 'Pyrenees', 'Norwegian Fauske', 'Afghanistan'},
    'STONE': {'Aswan granite', 'Sinai', 'Ethiopian basalt', 'Andean stone'},
}


XL_SITES = """
SHEEP|-3000|Crete uplands:68,39
WINE|-3000|Crete vineyards:69,39
FISH|-3000|Crete coastal fish:68,38
FISH|-3000|Bahamas banks:29,40; Puerto Rico shelf:33,37; Leeward Islands shelf:34,35; Windward Islands shelf:34,33; Trinidad shelf:35,32
SUGAR|1600|Guadeloupe:34,34; Barbados:35,33
FISH|-3000|Egyptian Mediterranean coast:68,36; Cyrenaican coast:65,37; Tripolitanian coast:61,37; Algerian coast:55,40
WHEAT|-3000|Cyrenaican farmland:65,36
WHEAT|-3000|Eurotas valley cereals:66,40
SHEEP|-3000|Marmarican pasture:67,36; Tripolitanian pasture:60,36
WINE|-3000|Cyrenaican vineyards:64,36
HORSE|-1600|Eastern Nile delta:69,35
"""

# Exact XL placements from the precious-metal review. Apply after the general
# atlas so new deposits do not displace unrelated crops or future introductions.
# These retain the atlas's existing turn-zero mineral availability.
XL_METAL_SITES = (
    ('GOLD', 'Witwatersrand West Rand', (106, 20)),
    ('GOLD', 'Witwatersrand Orange Free State', (107, 19)),
    ('GOLD', 'Minas Gerais Mariana', (61, 30)),
    ('GOLD', 'Victoria Bendigo', (181, 19)),
    ('GOLD', 'Alaska interior', (15, 95)),
    ('GOLD', 'Klondike', (16, 95)),
    ('GOLD', 'Timmins Abitibi', (42, 82)),
    ('GOLD', 'Muruntau Kyzylkum', (138, 78)),
    ('GOLD', 'Benguet Luzon', (175, 58)),
    ('GOLD', 'Japan Sado', (183, 78)),
    ('SILVER', 'Potosi western lodes', (53, 33)),
    ('SILVER', 'Potosi southern lodes', (54, 32)),
    ('SILVER', 'Fresnillo Zacatecas', (30, 65)),
    ('SILVER', 'Guanajuato La Luz', (27, 62)),
    ('SILVER', 'Banska Stiavnica', (102, 81)),
    ('SILVER', 'Japan Ikuno', (181, 73)),
)
XL_METAL_REPLACED = {
    ('GOLD', 'Japan Sado'), ('GOLD', 'Alaska Yukon'), ('GOLD', 'Klondike'),
    ('SILVER', 'Japan Sado'), ('SILVER', 'Peru Huancavelica'),
}


def review_xl_metals(plots, catalog, reserved, settlements):
    """Retain other atlas sites; represent giant provinces with several tiles."""
    for bonus, year, label, pos in catalog[:]:
        if (bonus, label) in XL_METAL_REPLACED:
            plots[pos][:] = [f for f in plots[pos] if not f.startswith('BonusType=')]
            reserved.remove(pos)
            catalog.remove((bonus, year, label, pos))
    # One Yukon foothill and Luzon's northern pass make the deposits accessible.
    for pos in ((16, 95), (175, 57)):
        fields = plots[pos]
        fields[fields.index('PlotType=0')] = 'PlotType=1'
    for bonus, label, pos in XL_METAL_SITES:
        fields = plots[pos]
        if (pos in reserved or pos in settlements or 'PlotType=3' in fields
                or 'PlotType=0' in fields
                or any('_IMPASSABLE' in f or 'FEATURE_ICE' in f for f in fields)):
            raise ValueError('Invalid XL metal deposit: %s %s %s' %
                             (label, fields, [site for site in catalog if site[3] == pos]))
        fields.append('BonusType=BONUS_' + bonus)
        reserved.add(pos)
        catalog.append((bonus, -3000, label, pos))

# XL availability review: allow early local exploitation rather than waiting
# for widespread cultivation or commercial prominence. These are generous
# gameplay milestones, not claims of proven cultivation at every atlas site.
# Apply after site selection so date changes cannot displace other resources.
XL_EARLIER_YEARS = {
    ('WINE', 'Greece north'): -3000,
    ('WINE', 'Sicily'): -3000,
    ('WINE', 'Italy Campania'): -2000,
    ('WINE', 'Etruria'): -2000,
    ('WINE', 'Iberian south'): -1500,
    ('WINE', 'Tunisia'): -1500,
    ('WINE', 'Gaul Mediterranean'): -1000,
    ('WINE', 'Iberian interior'): -1000,
    ('WINE', 'Bordeaux'): -500,
    ('WINE', 'Burgundy'): -500,
    ('WINE', 'Rhine'): -500,
    ('WINE', 'Moselle'): -500,
    ('COTTON', 'Mesoamerica Gulf'): -3000,
    ('COTTON', 'Maya lowlands'): -3000,
    ('COTTON', 'Deccan'): -2000,
    ('COTTON', 'Ganges'): -2000,
    ('COTTON', 'Bengal'): -2000,
    ('COTTON', 'Nubia'): -500,
    ('COTTON', 'Central Asia'): -500,
    ('COTTON', 'Brazil northeast'): -3000,
    ('COTTON', 'US Mississippi'): 1000,
    ('COTTON', 'US Alabama'): 1000,
    ('COTTON', 'US Texas'): 1000,
    ('COTTON', 'Egypt delta expansion'): 1000,
    ('CORN', 'Yucatan'): -3000,
    ('CORN', 'Colombian valleys'): -3000,
    ('CORN', 'Peru highland valleys'): -2500,
    ('CORN', 'Bolivia valleys'): -2500,
    ('CORN', 'Chile central'): -2000,
    ('CORN', 'southwest pueblos'): -2200,
    ('CORN', 'Mississippi middle'): -500,
    ('CORN', 'Ohio valley'): -500,
    ('CORN', 'Mississippi lower'): 0,
    ('CORN', 'Great Lakes south'): 0,
    ('CORN', 'Iroquois country'): 0,
    ('CORN', 'southeastern US'): 0,
    ('CORN', 'southern Brazil'): -1000,
    ('CORN', 'US Corn Belt'): 500,
    ('COW', 'east Africa'): -3000,
    ('COW', 'north China'): -2500,
    ('SHEEP', 'Central Asian steppe'): -3000,
    ('SHEEP', 'Mongolia'): -2500,
    ('SHEEP', 'north China'): -2500,
    ('PIG', 'Southeast Asia'): -3000,
    ('PIG', 'Java'): -3000,
    ('PIG', 'Korea'): -2000,
    ('PIG', 'New Guinea'): -1500,
    ('WHEAT', 'north China'): -2500,
    ('WHEAT', 'Shandong'): -2500,
    ('RICE', 'middle Ganges'): -3000,
    ('RICE', 'Niger inland delta African rice'): -1000,
    ('RICE', 'upper Guinea African rice'): -1000,
}


def sites(review=False):
    atlas = ATLAS + (MARINE_EXTENSIONS + XL_SITES if review else '')
    for line in atlas.strip().splitlines():
        if not line.strip():
            continue
        bonus, year, regions = line.split('|')
        for region in regions.split(';'):
            label, xy = region.strip().rsplit(':', 1)
            x, y = map(int, xy.split(','))
            if review and label == 'Cyprus':
                x, y = 71, 40  # The island, not the original Syrian atlas anchor.
            if review:
                # The old approximate anchors were east of New Guinea and on
                # New Zealand's opposite island. Narrower shores expose this
                # drift; keep each named supply on its intended island.
                if label == 'New Guinea':
                    x, y = 116, 26
                elif label in ('New Zealand South Island', 'New Zealand Canterbury'):
                    x, y = 121, 7
                elif label == 'New Zealand North Island':
                    x, y = 122, 10
                elif label in ('Hispaniola', 'Caribbean', 'Caribbean indigo'):
                    x, y = 30, 37
                elif label == 'Trinidad':
                    x, y = 35, 31
                elif label == 'Sakhalin':
                    x, y = 114, 54
            yield bonus, int(year), label, (x, y)


def place_resources(plots, origins, axis, data_dir, profile='Earth160x88', atlas_name='LargeWorldResources.tsv',
                    review=False, protected=(), valleys=(), event_fisheries=(), settlements=(),
                    island_regions=None):
    """Replace all bonuses after geography; reserve later sites from turn zero.

    Random-map BonusInfo climate restrictions (e.g. silver only on tundra)
    would falsify historical geology. Authored deposits instead respect land/
    water, relief, local climate for crops and existing physical barriers.
    Huge World's reviewed rocky districts may gain small hills. Peaks,
    impassability, protected routes/starts and alluvial valley tiles are retained.
    """
    for fields in plots.values():
        fields[:] = [f for f in fields if not f.startswith('BonusType=')]
    reserved, additions, catalog, omitted, relief_edits = set(), [], [], [], []
    settlements = set(settlements)
    crete_land = {pos for pos, origin in origins.items()
                  if origin in ((68, 39), (69, 39)) and 'PlotType=3' not in plots[pos]} if review else set()
    width = max(x for x, y in plots) + 1
    city_radius = tuple((dx, dy) for dx in range(-2, 3) for dy in range(-2, 3)
                        if (dx or dy) and not (abs(dx) == 2 and abs(dy) == 2))
    def open_water(pos):
        fs = plots.get(pos, ())
        return 'PlotType=3' in fs and not any('FEATURE_ICE' in f for f in fs)
    ocean = set()
    if review:
        # This Earth projection puts the central Pacific on the wrap seam.
        # Lake shores must not count as coastal city sites for marine deposits.
        pacific = (0, (max(y for x, y in plots) + 1) // 2)
        if not open_water(pacific):
            raise ValueError('Expected an open Pacific seed for coastal resource authoring')
        queue = [pacific]
        ocean.add(pacific)
        while queue:
            x, y = queue.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    q = ((x + dx) % width, y + dy)
                    if q not in ocean and open_water(q):
                        ocean.add(q)
                        queue.append(q)
    city_sites = set()
    if review:
        for (x, y), fs in plots.items():
            if not ('PlotType=1' in fs or 'PlotType=2' in fs) or any('_IMPASSABLE' in f or 'FEATURE_ICE' in f for f in fs):
                continue
            if any(f in fs for f in ('TerrainType=TERRAIN_SNOW', 'TerrainType=TERRAIN_MARSH')):
                continue
            if any(((x + dx) % width, y + dy) in ocean for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy):
                city_sites.add((x, y))
    accessible_land = set()
    if review:
        # Relief refinement can expose small enclosed foothill pockets. Place
        # economic deposits only on land connected to the coastal network.
        queue = list(city_sites)
        accessible_land.update(queue)
        while queue:
            x, y = queue.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    q = ((x + dx) % width, y + dy)
                    fs = plots.get(q, ())
                    if (q not in accessible_land and ('PlotType=1' in fs or 'PlotType=2' in fs)
                            and not any('_IMPASSABLE' in f or 'FEATURE_ICE' in f for f in fs)):
                        accessible_land.add(q)
                        queue.append(q)
    def workable(pos):
        return any(((pos[0] + dx) % width, pos[1] + dy) in city_sites for dx, dy in city_radius)
    for bonus, label, pos in event_fisheries:
        if (pos not in ocean or 'TerrainType=TERRAIN_COAST' not in plots[pos]
                or not workable(pos) or pos in reserved):
            raise ValueError('Invalid founding-event fishery: ' + label)
        reserved.add(pos)
        plots[pos].append('BonusType=BONUS_' + bonus)
        catalog.append((bonus, -3000, label, pos))
    def priority(site):
        bonus, year, label, origin = site
        # Productive agriculture and characteristic island exports take
        # precedence over ubiquitous quarry stone at this coarse resolution.
        signature = ('Sri Lanka cinnamon', 'New Guinea', 'New Guinea early cultivation', 'Moluccas cloves', 'Banda nutmeg')
        island_sugar = bonus == 'SUGAR' and label in ('Cuba', 'Hispaniola', 'Jamaica', 'Guadeloupe', 'Barbados', 'Sicily', 'Canaries', 'Mauritius', 'Madeira')
        island_gems = review and bonus == 'GEMS' and label == 'Sri Lanka'
        rank = 0 if label in signature or island_sugar or island_gems else 1 if bonus in FIELDS else 2 if bonus not in MINERALS else 4 if bonus in ('STONE', 'MARBLE') else 3
        return rank, year, bonus, label
    for bonus, year, label, origin in sorted(sites(review), key=priority):
        center = axis(origin[0]), axis(origin[1], True)
        rocky = review and label in ROCKY_DISTRICTS.get(bonus, ())
        choices = []
        for pos, fields in plots.items():
            dx, dy = pos[0]-center[0], pos[1]-center[1]
            # A narrowed island must not export its dated land resources across
            # the newly opened strait onto a neighbouring island or mainland.
            if (island_regions and origin in island_regions and bonus not in SEA
                    and not (bonus == 'OIL' and 'offshore' in label.lower())
                    and pos not in island_regions[origin]):
                continue
            if review and label == 'Cyprus' and pos not in ((114, 65), (115, 65)):
                continue
            if review and label.startswith('Crete '):
                # Keep the island's named supplies on Crete and its immediate
                # shore, rather than drifting north into the Aegean network.
                if bonus in SEA:
                    if not any(max(abs(pos[0] - x), abs(pos[1] - y)) <= 1 for x, y in crete_land):
                        continue
                elif pos not in crete_land:
                    continue
            # No long-distance relocation; each coordinate describes a local
            # regional envelope within 3.2 enlarged tiles of the anchor.
            if (abs(dx) > 3 or abs(dy) > 3 or dx*dx+dy*dy > 10
                    or pos in reserved or pos in settlements):
                continue
            if any('_IMPASSABLE' in f or 'FEATURE_ICE' in f for f in fields) or 'PlotType=0' in fields:
                continue
            water = 'PlotType=3' in fields
            if review and not water and pos not in accessible_land:
                continue
            if water != (bonus in SEA or (bonus == 'OIL' and 'offshore' in label.lower())):
                continue
            if review and water and (pos not in ocean or not workable(pos)):
                continue
            terrain = next(f.split('=')[1] for f in fields if f.startswith('TerrainType='))
            feature = next((f.split('=')[1].split(',')[0] for f in fields if f.startswith('FeatureType=')), None)
            if bonus in SEA:
                if bonus in ('CLAM', 'CRAB') and terrain != 'TERRAIN_COAST':
                    continue
                if bonus == 'WHALE' and not review and terrain != 'TERRAIN_OCEAN':
                    continue
            elif bonus not in MINERALS:
                if terrain in ('TERRAIN_SNOW', 'TERRAIN_MARSH'):
                    continue
                watered_desert = bonus in FIELDS and feature in ('FEATURE_FLOOD_PLAINS', 'FEATURE_OASIS')
                if bonus in FIELDS | {'BANANA', 'SILK', 'SPICES', 'IVORY'} and terrain not in ('TERRAIN_GRASS', 'TERRAIN_PLAINS') and not watered_desert:
                    continue
                if bonus == 'INCENSE' and terrain not in ('TERRAIN_DESERT', 'TERRAIN_PLAINS'):
                    continue
            elif terrain == 'TERRAIN_MARSH':
                continue
            if review and bonus in MINERALS and pos in valleys:
                continue
            if rocky and 'PlotType=2' in fields:
                river = ('isNOfRiver' in fields or 'isWOfRiver' in fields or
                         'isNOfRiver' in plots.get((pos[0], pos[1] + 1), ()) or
                         'isWOfRiver' in plots.get(((pos[0] - 1) % width, pos[1]), ()))
                if ((pos in protected and pos not in XL_RESOURCE_REFUGES) or river or any(f.startswith('ImprovementType=') for f in fields)
                        or feature in ('FEATURE_FLOOD_PLAINS', 'FEATURE_OASIS', 'FEATURE_MUD')):
                    continue
            # Prefer existing relief/vegetation, then proximity. No displaced
            # bonus may jump across water to another island or coastal region.
            penalty = 0
            if bonus in FIELDS and bonus not in ('SHEEP', 'WINE') and 'PlotType=1' in fields:
                penalty += 2
            if bonus in MINERALS - {'OIL'} and 'PlotType=1' not in fields:
                penalty += 2
            if bonus in ('DEER', 'FUR') and feature != 'FEATURE_FOREST':
                penalty += 2
            if bonus in ('BANANA', 'SPICES') and feature not in ('FEATURE_JUNGLE', 'FEATURE_FOREST'):
                penalty += 2
            if feature in ('FEATURE_OASIS', 'FEATURE_FLOOD_PLAINS') and bonus in MINERALS:
                continue
            relief_rank = int(rocky and 'PlotType=1' not in fields)
            if review and label == 'Crete vineyards':
                relief_rank = int('PlotType=1' in fields)
            if review and bonus in ('WHEAT', 'RICE', 'CORN'):
                relief_rank = int('PlotType=1' in fields)
            choices.append((relief_rank, dx*dx+dy*dy+penalty, pos))
        if not choices:
            omitted.append((bonus, label))
            continue
        # Restrict the local envelope to the anchor's connected land/sea patch.
        def medium(pos):
            fs = plots.get(pos, ())
            if review and (bonus in SEA or (bonus == 'OIL' and 'offshore' in label.lower())):
                return pos in ocean
            if island_regions and origin in island_regions and pos not in island_regions[origin]:
                return False
            return bool(fs) and ('PlotType=3' in fs) == (bonus in SEA or (bonus == 'OIL' and 'offshore' in label.lower()))
        anchor = min((p for p in plots if medium(p) and abs(p[0]-center[0]) <= 2 and abs(p[1]-center[1]) <= 2),
                     key=lambda p: ((p[0]-center[0])**2+(p[1]-center[1])**2, p), default=None)
        reachable, queue = set(), [anchor] if anchor else []
        while queue:
            p = queue.pop()
            if p in reachable:
                continue
            reachable.add(p)
            for dx, dy in ((-1,0),(1,0),(0,-1),(0,1)):
                q = p[0]+dx, p[1]+dy
                if q not in reachable and abs(q[0]-center[0]) <= 4 and abs(q[1]-center[1]) <= 4 and medium(q):
                    queue.append(q)
        choices = [entry for entry in choices if entry[2] in reachable]
        if not choices:
            omitted.append((bonus, label))
            continue
        pos = min(choices)[2]
        reserved.add(pos)
        if review:
            year = XL_EARLIER_YEARS.get((bonus, label), year)
        fields = plots[pos]
        if rocky and 'PlotType=2' in fields:
            fields[fields.index('PlotType=2')] = 'PlotType=1'
            relief_edits.append((bonus, label, pos))
        if year <= -3000:
            fields.append('BonusType=BONUS_' + bonus)
            # Cultivated fields and vineyards, not unexplained new vegetation.
            if bonus in FIELDS:
                fields[:] = [f for f in fields if not f.startswith(('FeatureType=FEATURE_FOREST', 'FeatureType=FEATURE_JUNGLE'))]
        else:
            additions.append((year, 'BONUS_' + bonus, pos))
        catalog.append((bonus, year, label, pos))
    if review:
        review_xl_metals(plots, catalog, reserved, settlements)
        omitted[:] = [site for site in omitted if site not in XL_METAL_REPLACED]
    # Swamp is decorative terrain art, not a traded economic resource. Rebuild
    # it from the finished marsh rather than retaining source-map positions.
    for pos, fields in plots.items():
        if 'TerrainType=TERRAIN_MARSH' in fields and pos not in reserved:
            fields.append('BonusType=BONUS_SWAMP')
    output = '# Generated by tools/generate_large_world.py. Python 2.4.\n'
    output += '# Independent Large World introductions: (year, bonus, (x, y)).\n'
    output += 'ADDITIONS = ' + pprint.pformat(tuple(sorted(additions)), width=110) + '\n'
    (data_dir / (profile + 'Resources.py')).write_text(output, encoding='ascii', newline='\n')
    # Compact reviewable atlas of final coordinates, including later resources.
    out = Path(__file__).resolve().parents[1] / 'docs' / atlas_name
    rows = ['resource\tyear\tregion\tx\ty'] + ['%s\t%d\t%s\t%d\t%d' % (b,y,n,p[0],p[1]) for b,y,n,p in catalog]
    out.write_text('\n'.join(rows)+'\n', encoding='utf-8', newline='\n')
    print('Authored resources: %d initial, %d later; %d inaccessible/unsuitable sites omitted' %
          (len(catalog)-len(additions), len(additions), len(omitted)))
    print('Resource atlas counts:', dict(sorted(Counter(b for b,y,n,p in catalog).items())))
    if omitted:
        print('Omitted sites (no distant substitutes):', omitted)
    if review:
        print('Rocky district hills authored:', relief_edits)
