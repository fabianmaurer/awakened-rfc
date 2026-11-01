# Scenario geography

WorldBuilder scenarios select a geography profile through `SCENARIOS` in
`Assets/Python/ScenarioGeography.py`. All five existing start dates explicitly
select `Earth124x68`; selection is by scenario filename, not map dimensions or
start turn. A copied or renamed scenario needs its own registry entry.

Profiles live in `Assets/Python/ScenarioGeographyData`. They supply:

- Grid width and height, settlement preferences, war targets and city-name maps.
- Capitals, birth-flip areas and exceptions, stability and resurrection regions.
- Coordinates and bounds used by historical events, resource changes, regional
  units, religious mechanics, wonders and the associated UI.
- Native continent subdivisions, Caliphate regions and crusade fronts.

Civ4 imports files in this directory by flat module name, not as a Python
package. Use unique filenames and imports such as `from Earth124x68Values import
VALUES`; avoid `ScenarioGeographyData.` prefixes.

The scenario's authored cities, units and diplomacy remain in its WorldBuilder
file. Date-specific setup modules and generated scenario data remain responsible
for their own starting positions and rules. This change creates no larger map
and does not automatically adapt historical setup to a new geography.

## Adding a different world map

Create a Python 2.4-compatible profile module, using `Earth124x68.py` as the
schema reference. Supply its own `VALUES`, `NATIVE`, grids and area rectangles,
then register the scenario's lowercase basename in `SCENARIOS`. Profiles may be
shared by several scenarios using the same geography. Do not change the existing
profile's dimensions to create a second map size.

Core geography keys must be supplied; missing core data or a mismatch with
WorldBuilder dimensions rejects initialization. Scripted-event coordinates in
`Resources`, `Barbs`, `Religions`, `RiseAndFall`, `Arctic` and
`CvRFCEventHandler` may be omitted or set to `None`. A missing lookup silently
stops the current Python event callback; other registered handlers continue.
This is handled centrally by the event dispatcher, with no per-event guards or
fallback coordinates. Earlier effects in that callback are not rolled back.
Other script errors still propagate. DLL geography remains required.
Each grid has one plane per major player slot, with exactly the profile's width
and height. Native values are integer sequences; their lengths form part of the
schema. Keys used by a particular mechanic are referenced directly in its code.
Coordinates are authored, never automatically stretched from the original map.

Area entries are `(group, west, south, east, north)`, inclusive, using Civ4's
south-to-north y coordinates. `AREA_COUNT` specifies the additional land areas;
entries apply in order after the ordinary land/water flood fill.

## Compact grids

`Earth124x68Grids.py` stores settlement, city-name and war maps as sparse runs.
Each civilization plane is `(default, values)`, where each value entry is
`(value, ((row, first_x, last_x), ...))`. Spans include both endpoints. Rows run
**north to south**, so `row = height - 1 - game_y`. A bare integer plane reuses
an earlier civilization's plane. Overlapping or out-of-bounds spans are rejected.

For example, `(20, ((300, ((10, 30, 35),)),))` sets six tiles on row 10 to 300
and leaves all other cells at 20. `SparseGrids.expand` reconstructs immutable
grids once when importing the profile. AI lookups use expanded grids; they do
not decode spans during turns. Missing legacy city-name cells use `"-1"`, and
the two unauthored legacy war-map slots use zero target weights.

## Initialization and saves

WorldBuilder installs the profile before creating the map, continent areas or
initial cities. Native successor settlement maps are finalized after map
creation. Python module bindings refresh when switching scenarios in the same
process, including aliases of mutable regional tables.

Saves store the profile name, native geography and settlement maps. Load handling
restores Python bindings before civilization callbacks. This changes the save
format; existing saves are unsupported. All multiplayer peers require identical
profile files and the matching DLL.

Changing profile data needs no DLL rebuild. Changing native accessors or the
bridge does require the legacy production build. Source and data checks do not
establish in-game loading or multiplayer readiness.
