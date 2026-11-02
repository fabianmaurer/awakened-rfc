# Large World, 3000 BC

Select **Start 1b - 3000 BC - Large World** in the scenario menu. Egypt,
India, China and Babylonia are the four playable founding civilizations. The
WorldBuilder file contains their starting locations and preserves the original
minor city of Uruk with its buildings and defenders. The ordinary RFC birth
system supplies major civilizations' starting units and later civilizations.
Scripted minor settlements use the same spawn turns as the default 3000 BC
scenario, including its immediate spawns.

| Measure | Original world | Large World |
| --- | ---: | ---: |
| Dimensions | 124 × 68 | 160 × 88 |
| Total tiles | 8,432 | 14,080 (+66.98%) |
| Passable land tiles | 2,714 | 3,241 (+19.42%) |

Passable land means flatland or hills without impassable terrain or ice. Peaks
and water are excluded; ordinary desert, tundra, snow and marsh count. This is a
movement budget, not a count of fertile city sites. The larger projection has
4,567 passable land tiles before adding 1,326 impassable wilderness tiles. The
earlier 25% figure is not a target: barriers follow geography, and usable land
is measured afterward.

## Geography and barriers

The map expands the existing RFC coastlines and terrain into a larger grid,
retaining its deliberately enlarged Europe and compressed oceans. It is an
alternative RFC world, rather than a new geographic projection. Existing peaks
remain peaks. Added impassable terrain retains its desert, snow, tundra or
vegetated appearance and is identified as **Impassable wilderness** on hover.
These additional terrain types are appended to the XML; original terrain IDs
and the original scenarios remain unchanged.

The revised layout uses the complete EU4 1.30 wasteland inventory as a regional
reference, supplemented by Adirondacks and Annamite Mountains from later province
lists. It adapts those regions to RFC's projection rather than copying EU4 borders.
The reference is the [full SVG generated from EU4 map data](https://github.com/primislas/eu4-svg-map/blob/master/maps/1.30.0/eu4-political.svg).
EU4 defines wasteland as terrain that cannot be crossed or colonized; see the
[official manual](https://forumcontent.paradoxplaza.com/public/79250/EuropaUniversalisIV_Manual.pdf).
This is an exhaustive review of that reference snapshot, not a claim to reproduce
every border in the latest EU4 patch.

| EU4 wastelands reviewed | Large World treatment |
| --- | --- |
| El Djouf, Central Sahara, East Sahara | Broad deep-desert regions, two narrow north-south oasis routes, open Nile and coastal margins. 168 of 258 land tiles in the Saharan envelope are blocked, including existing peaks. |
| Namibia, Kalahari | Impassable desert interiors with coastal and southern approaches. |
| Guinea, Central Africa, Northern Congo Basin, Imatong, Urgoma | Rainforest interiors and highlands; lower Congo, lake approaches and historical settlements remain accessible. |
| Western Amazonas, Eastern Amazonas, Guyana | Large rainforest interior with an Amazon trunk route and Andean approaches. Guyana overlaps the northern Amazon envelope and existing peaks. |
| Great Basin, Columbia, Rocky Mountains | Desert core and mountain barriers with open approaches. |
| Alaska, Northwest Territories, Nunavut, Baffin, Weagamow, Ungava | Northern wilderness; coastal margins and the southern Canadian route stay open. |
| Greenland | Impassable ice interior. |
| Scandes, Alps (both regions), Carpathians, Caucasus, High Atlas, Hakkari | Selected upland barriers with lowland passes. The small Caucasus envelope already has peaks and narrow coastal approaches. |
| Badiyat ash Sham, Rub al Khali | Syrian and Empty Quarter desert barriers; Levant, western Arabia and Persian approaches remain open. |
| Nenets, Yamal, Western Siberia, Central Siberia, Eastern Siberia | Extensive remote northern wilderness above the southern route. |
| Tian Shan, Pamir, Himalaya, Arunachal, Changtang, Qilian, Suleiman Range | Existing peaks plus selected additional highlands. Tarim rim, Khyber and Ganges approaches remain open. |
| Naga Hills, Arakan Mountains, Gaoligong Mountains, Annamite Mountains, Changbai Mountains | Border highlands. At this resolution Annamite already has peaks and little room between coasts and lowland routes. |
| Borneo, Papua | Existing interior peaks retained; these narrow islands have no additional interior tiles after protecting their coastal margins. |
| Western Australia, Central Australia | Broad desert interior with usable coasts. |
| Adirondacks (later addition) | Small upland barrier. |

Four scenario-only features identify deep desert, dense rainforest, remote
northern wilderness and frozen wilderness. Deep desert, frozen wilderness and
dense rainforest use brown-orange, light blue and dark green animated fog,
respectively. These reuse Civilization IV's fallout smoke with its radiation
glow removed; the original fallout feature is unchanged. Remote northern forest
also uses dark green fog, so every impassable land tile except mountain peaks
has fog. Rebuild the derived fog models and shared smoke texture with
`.venv-art/Scripts/python.exe tools/build_wasteland_art.py`.
All four are impassable, do not spread and cannot be removed. Underlying
impassable terrain remains a second movement guard. Mountain additions are peaks.
The default scenarios receive no new wasteland placements.

Shorelines, civilization capitals, historical settlements and fixed resource
events retain access. Selected corridors are open terrain, not prebuilt roads.
Unlike the earlier revision, every riverbank is not automatically exempt:
large wilderness regions stay coherent. The generator opens paths from fixed
historical sites to the coastal land network where necessary. Ordinary resources
and tribal villages inside a barrier move to compatible accessible fringe tiles;
91 resource/village placements move, at most 17.1 enlarged-map tiles. Counts of
every resource, all 28 villages, both farms, Uruk's buildings and defenders are
preserved. The decorative swamp bonus may remain on blocked marsh.

Rivers extend along the correct enlarged tile edges: a plot north of a river
keeps it on its southern boundary, and a plot west of a river keeps it on its
eastern boundary. Resources are retained once rather than multiplied across
enlarged cells.

Impassability is a strategic abstraction for sustaining substantial premodern
armies, not a claim that these lands were uninhabited or never crossed. Saharan
travel in particular followed established oasis networks; see the
[Metropolitan Museum's account of Sahelian trade](https://www.metmuseum.org/de/exhibitions/sahel-art-empire-sahara/inside-the-exhibition).
Barriers remain impassable in later eras; there is no new technology-based
unlocking mechanic.

## Maintaining the scenario

Run `python tools/generate_large_world.py` to regenerate the WorldBuilder map,
static values, native coordinates, compact civilization grids and appended
terrain and feature definitions. The generator uses the original map/profile as an offline
cartographic reference, with regional polygons, selected uplands,
corridor lines and axis metadata. There is no global barrier quota.
Region bounds include the full extent of each enlarged source
tile; regional exceptions and scripted terrain edits cover its full footprint.
Runtime code loads independent `Earth160x88` data; it does not
stretch the original profile at runtime. `Earth160x88.py` supplies the dimensions
and continent subdivisions; `ScenarioGeography.py` registers the filename.
Scenario text is in `CIV4GameText_LargeWorld.xml` with all five languages.

All 33 civilization starts, settlement maps, war maps, city-name grids, stability
and birth regions, scripted-event coordinates and native geographic bounds are
mapped to the enlarged projection. Remaining fixed coordinates in Babylonian
and French victory checks, Russia's unique-power region, Saharan continent
handling, the Huna warning and the papacy's Rome lookup use the selected profile.
Barbarian, conqueror and slave-rebel placement rejects impassable terrain.
Country-name previews recognize the scenario. Civilization birth dates, unique
powers and gameplay rules are retained. City-name regions may span multiple tiles. Fixed travel
distances, army sizes and historical objectives have not been rebalanced for the
larger world; a successful startup does not establish campaign balance or
multiplayer readiness. Profile/map edits need no DLL rebuild; the papacy lookup
fix requires the accompanying rebuilt production DLL.

Validation on 2026-11-01: profile schema and all 99 grids checked; WorldBuilder
plots complete and unique; original resource counts and minor spawn times preserved; changed XML
parsed and all new text entries contain five languages. The installed production
DLL matched the workspace. The scenario loaded through civilization selection
into Egypt's 3000 BC starting position and opening dialog in German, with no
Python exception logged. Civilization IV was closed afterward. No campaign or
multiplayer run was performed.

Map revision on 2026-11-02 follows the complete EU4 reference inventory above.
The 19.42% additional passable land is an outcome of the geography, not a quota.
Static review confirms all 33 starts, scripted minor settlements, fixed resource
events and land resources connect to the coastal land network. Resource, village,
city and defender counts and river edges are preserved. Feature XML and all five
text languages parse; both new meshes read back in Civ4's NIF format. Startup of
the revised installed scenario reached Egypt's opening position without a Python
exception; the desert dunes rendered correctly. No turns or multiplayer campaign
were run by the agent. The game was left open at the user's request.
