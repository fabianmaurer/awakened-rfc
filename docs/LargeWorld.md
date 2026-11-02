# Large World, 3000 BC

Select **Start 1b - 3000 BC - Large World**. Egypt, India, China and Babylonia
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
