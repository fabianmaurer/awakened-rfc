# Large World, 3000 BC

## Additional Huge World start

Select **Start 1 XL - 3000BC** for the additional 200 x 110 map.
It has 22,000 tiles, 56.25% more than Large World, with 5,032 passable land
tiles. Of its 8,390 land tiles, 3,358 (40.0%) are blocked by wasteland, peaks
or ice, compared with 37.7% in Large World. It starts in 3000 BC with the same
four founding civilizations and later RFC births.

The map retains RFC's enlarged European proportions and compressed oceans at
the larger grid scale. Europe keeps its settlement belt and ordinary mountain
barriers. Additional wilderness extends the Saharan, Congo, Amazon, Canadian,
Alaskan, Siberian and Australian interiors, with new Gobi and Patagonian
barriers. This uses the EU4-inspired regional inventory below, with deliberately
broad interiors outside Europe; it does not copy EU4 province boundaries.
Coastal fringes, all 33 major birth sites and the 26 named route networks retain
access. Route authoring protects 571 tiles and opens 21 peak tiles.
There are no prebuilt roads or technology unlocks for the wastelands.

The connectivity pass adds eastern and southern Tibetan approaches, extends
the Andean corridor through central Chile, opens a central Andes-Pampas
crossing, and connects Alberta and northern Great Basin resource pockets.
Huge World's route paths share tile edges wherever source land allows, rather
than relying on corner-only gaps between enlarged peak blocks. Diagonal-only
isthmuses between water tiles retain Civ4's normal diagonal movement.
Tibetan routes are coarse terrain adaptations of the
[Sichuan/Yunnan-Tibet network](https://en.chinaculture.org/created/2005-09/16/content_73021_3.htm)
and [Nepal-Tibet approaches](https://www.asiasocietymuseum.org/buddhist_trade/himalaya_nepal.html),
not claims that these trade networks already operated in 3000 BC.

The shared historical resource atlas is placed against the new finished terrain:
776 initial resources and 197 later introductions, with 25 unsuitable sites
omitted rather than moved far away. See [HugeWorldResources.tsv](HugeWorldResources.tsv).
The independent `Earth200x110` profile supplies all geography grids, event
coordinates and its own resource schedule. Generate this variant with
`python tools/generate_large_world.py --huge`; the command without that flag
continues to author Large World.

Large World is temporarily disabled: its WorldBuilder file is retained under
`tools/scenario_templates/disabled`, outside the playable mod and release ZIPs.
The generator without `--huge` writes to that archived location.

Huge's event geography includes every reference-profile key. The Libyan raids
use the open coastal approach west of the Nile, and the early chariot raids
have ordered west/east bounds. Gadir's crab and Karalis's clam beds are reserved
for their founding-event fishing boats. All scripted raid areas have suitable
terrain; ownership, culture and other normal gameplay conditions can still
prevent an individual event. This is a static source/map review, not in-game
or multiplayer validation.

Huge's 3000 BC start also schedules four independent cities: Merv in 600 BC,
Anuradhapura in 400 BC, Palembang in AD 700 and Great Zimbabwe in AD 1100.
Each starts at population one with a small garrison, and appears only if the
site remains available under the normal ownership and nearby-city checks.
Great Zimbabwe uses the inland cattle and gold belt rather than the dormant
southern marker. These additions do not change the other scenarios.

The resource/terrain correction pass expands fish, shellfish and whale sites
from 110 to 207 using additional named shelves, estuaries and upwelling coasts.
Every water resource, including offshore oil, is on the connected ocean and
within Civ4's working radius of a potential coastal city on suitable land.
Clams and crabs stay on coast terrain; whales may also use coastal migration
waters. Polar or remote sites without a suitable nearby city site are omitted.
The distribution follows productive coastal regions, not a uniform ocean quota;
[NOAA's upwelling overview](https://oceanexplorer.noaa.gov/ocean-fact/upwelling/)
provides the ecological basis for the richer current systems.

All 44 remaining floodplain tiles are flat desert beside a river. Invalid
off-river copies normally retain their underlying terrain: nine outer Nile
tiles remain desert. Fourteen tiles in explicitly reviewed Niger inland-delta,
Mesopotamian and Indus alluvial fringes use plains to represent broader seasonal
flood/grazing land. There is no automatic grassland upgrade. This avoids widening
Egypt's narrow farming belt simply because a source floodplain was enlarged;
see [FAO on Nile soils and irrigation](https://www.fao.org/4/y5863e/y5863e06.htm)
and [USGS on the Niger's seasonal flood extent](https://eros.usgs.gov/earthshots/inland-delta-seasonal-flooding).
Mineral placements avoid these alluvial tiles.
Named rocky districts prefer existing local hills; nine small hills/outcrops are
authored where no suitable hill exists. Routes, starts, improvements and valley
terrain are protected from these relief edits. Oil, sedimentary basins, alluvial
deposits and ordinary quarries can retain flat terrain. Grain prefers local
lowlands, with hillside sites retained where necessary; the DLL's bonus exception
allows farms there. Egyptian gold, emeralds and Sinai copper/turquoise now use
upland sites, while Nile limestone and Suez oil remain flat where appropriate.
[UCL's geology summary](https://www.ucl.ac.uk/museums-static/digitalegypt/geo/geology.html)
and [Sinai material](https://www.ucl.ac.uk/museums-static/digitalegypt/sinai/index.html)
support that regional distinction.

Fifteen source-footprint tiles in the Bolivian plateau belt retain their relief
with open plains and no tropical jungle, protected from the overlapping Amazon
mask. A narrow Andean plateau branch connects them to the existing route; Potosi
silver stays in its local highland district. This adapts the highland/rainforest
boundary described by [NASA](https://science.nasa.gov/earth/earth-observatory/bolivian-andes-8830/),
with [Potosi's mountain setting](https://science.nasa.gov/earth/earth-observatory/potosi-and-cerro-rico-151059/)
as a placement reference.

Static review on 2026-11-02 covered plot dimensions and identifiers, all major
birth sites, profile grids and native schema, resource introduction sites and
five-language scenario text. The connectivity review confirmed local Tibetan,
Andean, Alberta and Great Basin passages; all initial and future economic land
resources, initial units/cities/improvements and major birth sites have land
access to an open-ocean coast. The correction review also checked river adjacency,
marine city workability, named rocky-site relief, crop terrain, unique atlas
sites and the later-resource schedule. Empty polar and mountain pockets remain; they
are not opened indiscriminately. No DLL changes are needed. In-game loading,
campaign pacing and multiplayer remain unverified; travel distances, historical
objectives and starting army sizes have not been rebalanced for this size.

Huge World's mountain refinement replaces rectangular enlargement at range
edges with interpolated foothills, retaining source summit anchors and links
between neighboring peaks. Mountain-region boundaries use the finer grid;
they cannot turn the softened shoulders straight back into peaks. The finished
map has 716 peaks instead of 1,148, with the largest visible changes along the
Rockies, Andes and central Asian ranges. Broad range interiors remain mountainous.
Some additional edge land is traversable; this is a gameplay change as well as
a visual adjustment. Routes and resources are regenerated against the new relief,
and resource placement excludes enclosed foothill pockets without coastal access.
The four enlarged Venice/Aquileia hill tiles are flattened to continue the
eastern lowland toward the Adriatic; the Alpine foothills to their north remain.

Crete has three passable hills and three lowland tiles, with sheep, wine and
one adjacent fish site. Its named supplies stay on the island or its immediate
shore. This represents its [mountainous relief](https://www.crete.gov.gr/perifereia/),
[pastoral economy](https://ashmolean.web.ox.ac.uk/article/dining-with-the-minoans)
and [Minoan wine](https://heraklionmuseum.gr/en/en-oi-dromoi-tou-krasiou-sto-archaiologiko-mouseio-irakleiou-2/);
resource dates are the atlas's broad abstractions, not exact first attestations.
Mainland refinements add two Attic hills while keeping Athens's birth tile flat,
and open one Peloponnesian valley tile. The existing Thessalian/Macedonian
lowlands, Pindus uplands and coastal access remain.

Birth placement preserves source-map river and shoreline access within each
original tile's enlarged footprint. Egypt moves from dry desert `(112,54)` to
Nile floodplains `(111,54)`; England, Russia and the Mississippians regain river
access, and America and the Inca regain shoreline access. The other 27 primary
birth sites remain unchanged. Reserve starts and Korean/native setup coordinates
use the same placement rule, including the Mississippian setup override. The
WorldBuilder start and generated capital table agree. This reviews geography,
not starting-army balance or historical relocation of the original RFC capitals.

The historical-centre review protects small Sichuan and Wei/middle Yellow River
lowland belts from the mountain masks. It retains the surrounding uplands, adds
no prebuilt irrigation, and follows the distinction between the
[Chengdu plain and Tibetan margin](https://whc.unesco.org/en/list/1001/) and the
[Chang'an/Luoyang centres](https://whc.unesco.org/en/list/1442/).
Cyprus gains one coastal lowland beside its former summit, now a wooded hill;
its copper moves from Syria onto the island, following its
[Troodos deposits](https://www.gov.cy/moa-mines/en/documents/mineral-resources-of-cyprus/).
Both island tiles use Salamis naming and matching AI geography. Two Red River
delta tiles become lowlands, with a short river branch to the sea; the southern
wetlands remain, reflecting the [Hanoi delta setting](https://whc.unesco.org/en/list/1328).
Scripted foundations at Samarkand, Pagan, Hanoi, Nineveh, Bordeaux, Rusadir and
Zimbabwe move within their source footprints to retain rivers or shore access.
Where both cannot share an enlarged tile (Rusadir), the river takes priority
with the shore at most two tiles away. Foundation dates and owners are unchanged.

## Large World start

Currently disabled: **Start 1b - 3000 BC - Large World**. Egypt, India, China and Babylonia
are the four playable founding civilizations. Uruk retains its buildings and
defenders; the usual RFC birth system supplies starting units and later births.
Other scenarios retain their geography and resource events.

| Measure | Original world | Large World |
| --- | ---: | ---: |
| Dimensions | 124 x 68 | 160 x 88 |
| Total tiles | 8,432 | 14,080 (+66.98%) |
| Passable land tiles | 2,714 | 3,330 (+22.70%) |

Passable land counts flatland and hills without impassable terrain or ice.
It is a movement measure, not a measure of fertile city sites. There is no
barrier quota or resource quota per civilization.

## Barriers and historical routes

The map retains RFC's enlarged Europe and compressed oceans. Its regional
barriers use the [EU4 1.30 SVG](https://github.com/primislas/eu4-svg-map/blob/master/maps/1.30.0/eu4-political.svg)
as a benchmark, adapting regions rather than reproducing province borders.
The reviewed inventory covers the Sahara; Namib and Kalahari; Guinea, Congo,
Imatong and Urgoma; Amazon and Guyana; Great Basin and Rockies; northern Canada,
Alaska and Greenland; Scandes, Alps, Carpathians, Caucasus, Atlas and Hakkari;
Arabian deserts; northern Siberia; Tian Shan, Pamir, Himalaya, Changtang, Qilian
and Suleiman; Southeast Asian border ranges and Changbai; Borneo, Papua and
Australia. Adirondacks and Annamite were supplemental later-reference regions.
**Takla Makan is passable desert in the benchmark and has no added barrier.**

Nineteen named route networks protect 303 tiles. They cover western Saharan
oases and Fezzan-Kanem, the Nile, Arabian incense routes, Persia-Bactria,
northern and southern Tarim routes and Hexi, Khyber/Ganges, Bengal-Burma-Yunnan,
mainland Southeast Asia, Congo/lake approaches, the Zambezi, Amazon and Andes,
southern Canada and Siberia, two Alpine approaches and northern Caucasus access.
Thirteen source peak tiles become hills where narrow passes are needed.
Routes are ordinary traversable terrain, without prebuilt roads. Other peaks
remain, and historical birth and settlement locations retain coastal access.
Three improvements move locally; all 28 initial villages and both farms remain.

The [UNESCO Chang'an-Tianshan corridor description](https://whc.unesco.org/en/list/1442/)
supports connected routes through Hexi and around the Tian Shan; the
[Metropolitan Museum's Sahel material](https://www.metmuseum.org/de/exhibitions/sahel-art-empire-sahara/inside-the-exhibition)
provides the trans-Saharan oasis-network context. Route waypoints are coarse
adaptations to RFC's projection, not precise archaeological itineraries.

## Normal terrain features and fog

The four special wilderness gameplay features are removed. Added barriers use
normal jungle, evergreen forest, marsh/mud, ice, or bare desert; snowy barriers
use ice rather than forest. Appended impassable terrain variants retain the
appropriate underlying appearance. Terrain remains impassable even when a normal
feature is present or removed; the DLL checks terrain and feature independently.

Civ4 stores only one gameplay feature per plot. **FEATURE_IMPASSABLE** is a
separate, transient display entity over blocked land, preserving normal trees,
jungle and ice. It has no saved state or gameplay callback, and respects map
revelation. Peaks and ocean ice use their ordinary artwork. The neutral fog
retains animated fallout smoke without radiation glow; its vertex opacity is
35% stronger than the previous coloured overlays. The original fallout feature
is unchanged. Build the derived mesh with:

```powershell
.venv-art/Scripts/python.exe tools/build_wasteland_art.py
```

Impassability remains a permanent strategic abstraction. No technology-based
unlocking, seasonal ice changes or save migration is introduced.

## Ocean ice

262 additional ocean tiles use normal impassable ice: central Arctic pack,
Canadian high-Arctic waters and the extreme Antarctic fringe, including small
Weddell/Ross extensions. The open Norwegian Atlantic and Bering approaches are
outside the new northern mask. A local exception protects the southern Cape
Horn sea lane, which lies close to the map edge; the Cape of Good Hope is
outside the southern mask. This models a conservative perennial barrier,
not the winter maximum or modern annual weather.

[NSIDC's sea-ice overview](https://nsidc.org/learn/parts-cryosphere/sea-ice/science-sea-ice)
distinguishes persistent Arctic pack from mostly seasonal Antarctic ice. The
[Australian Antarctic Program](https://www.antarctica.gov.au/about-antarctica/weather-and-climate/climate-change/sea-ice/sea-ice/)
describes the smaller summer ice concentrations used as the southern reference.
There is no Bermuda Triangle barrier.

## Resource atlas

Resource authoring runs **after all terrain, routes and ocean ice**. Every old
bonus is discarded. The independent atlas in `tools/large_world_resources.py`
places **678 initial economic resources and 194 later introductions**, covering
all 33 map resource types. Decorative swamp artwork is rebuilt separately from
finished marsh terrain. [LargeWorldResources.tsv](LargeWorldResources.tsv)
lists each placed resource, introduction year, named region and final coordinates.

Mineral markers represent geological deposits, not the date a modern mine opened;
existing technology reveals still govern visibility. Named districts include
ancient copper/gold/silver sources and later-important coal, oil, bauxite and
uranium basins. Generic quarry stone is lower priority than regionally distinctive
resources. Random-map restrictions such as silver appearing only on tundra are
not historical geology and do not constrain this authored map. Neither terrain
nor relief is changed to accommodate a deposit.

Crops and livestock distinguish initial regional availability from later spread.
Maize begins in the Americas; Eurasian livestock and wheat reach American
regions after contact; Australian pastoral/agricultural introductions are later.
Horse supply begins on the Pontic-Caspian steppe around 2200 BC and subsequently
spreads. Initial silk, sugarcane and spice locations follow their native/early
production regions rather than later colonial plantations. Bonuses represent
local supply, not imports. Missing crops such as millet, sorghum, potatoes and
cassava are not silently represented by unrelated wheat or maize bonuses.

Introduction years are coarse regional milestones, not precise first-find dates.
The calendar-crossing callback works independently of game speed and replaces
the original resource-event schedule only for this scenario. Future sites are
reserved during authoring. An introduction never overwrites a bonus supplied by
another mechanic, and cultivated fields may clear normal forest or jungle.
Existing historical birth, trade and technology rules otherwise remain.

Placement stays within a small local geographic envelope (at most 3.2 enlarged
tiles from the atlas anchor), on the same local land/sea patch, outside barriers
and ice. Twenty-one unsuitable, crowded or inaccessible sites are omitted rather
than moved far away. Small islands cannot display every historical commodity on
Civ4's one-bonus-per-tile grid. Counts are not normalized for civilization balance;
this is a history-first atlas, not a campaign balance claim.

Evidence and authoring references:

- [USGS mineral resource data](https://www.usgs.gov/programs/mineral-resources-program/mineral-resources-data)
  and [Mineral Commodity Summaries](https://pubs.usgs.gov/publication/mcs2026)
  for mineral districts and resource-bearing regions. Locations are manually
  adapted to the projection, not an automatic import of reserve tonnages.
- [Origins of food crops connect countries worldwide](https://pmc.ncbi.nlm.nih.gov/articles/PMC4920324/)
  and the [Alliance of Bioversity/CIAT origin map](https://alliancebioversityciat.org/origin-crops-family-genus-center-origin-map)
  for crop origins and regional diversity; [crop dispersal review](https://puruggananlab.org/Papers/2023/Crop_GeographicSpread_Adaptation_Review2023.pdf)
  for ancient exchange and post-Columbian introductions.
- [Ancient horse genomes](https://www.nature.com/articles/s41586-021-04018-9)
  for the Pontic-Caspian origin and Bronze Age expansion of modern domestic horses.

## Maintaining the scenario

Run `python tools/generate_large_world.py`. It emits the WorldBuilder map,
resource introduction schedule and atlas, geography values, native coordinates,
compact civilization grids and appended terrain/feature definitions. Authoring
coordinates use the original reference projection; runtime loads independent
`Earth160x88` data. All 33 starts, city-name/settlement/war grids, birth/stability
regions and scripted geographic bounds remain scenario-selected. Original
terrain/feature IDs preceding the removed scenario-only entries are unchanged.
The fog overlay and terrain/feature movement fix require the accompanying
production DLL built with the legacy VC7.1 toolchain.

Static review on 2026-11-02 confirmed all 33 starts, the 19 route networks,
unique resource sites and schedules, Cape Horn and major ocean connections.
Changed XML parses and each text entry has all five languages. The fog mesh
reads back with six smoke layers and 0.54 vertex opacity (previously 0.40).
The production VC7.1 build succeeded; changed runtime files and the DLL were
synchronized to the installed mod and hash-verified.

The previous revision loaded into Egypt's opening position in German. That is
not runtime validation of this revision. No new game, campaign, observer test or
multiplayer validation was run for these changes. Fixed travel distances,
historical objectives and army sizes have not been rebalanced for the larger map.
