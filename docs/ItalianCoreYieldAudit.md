# Italian core yield audit

Investigation of the hypothesis that weak Italian terrain limits Roman
expansion. Uses the existing 20-game, 200-turn balance batch
`balance-ai-3000bc-20games-200turns-seeds-1-20-20261016-224552-b87fd3`, the 3000 BC
map, XML yields and DLL source. No new simulations or terrain edits were made.
The batch predates the subsequent extra Roman units, Karalis and collapse
safeguards; it cannot establish their effects.

## Conclusion

There is a concrete early food bottleneck in southern Italy, especially the
Pompeii/Paestum site at (62, 42). It is not evidence that the whole Italian
core lacks productive land, or that Pompeii remains useless throughout a game.
Roma develops strongly; Pompeii starts slowly but eventually produces as many
hammers as Mediolanum at the same observed age.

A targeted Campanian food improvement is a justified experiment. A blanket
Italian yield buff, a general production increase, or the claim that poor
terrain explains all missing Roman conquests is not supported by these data.

## Recorded city development

Cities are grouped by coordinate, not name: the (62, 42) site is named Pompeii
or Paestum and occurs under Roman ownership in 15/20 games. Roma and Mediolanum
occur in all twenty. Age means turns since first recorded Roman ownership of
the site, which need not equal its original foundation date. Later recapture
does not restart that clock.

Exact age-10 samples below are normal: no disorder, anarchy, occupation or
food-based production. Each game contributes one sample to its site's median.

| City | Games at age 10 | Median population | Median hammers/turn | Median local food |
| --- | ---: | ---: | ---: | ---: |
| Roma | 20 | 3 | 7 | 11 |
| Mediolanum | 20 | 2 | 2 | 7 |
| Pompeii/Paestum | 15 | 1 | 4 | 2 |

Among cities first observed at size one, the median time to reach size two is
five turns for Roma (20 games), seven for Mediolanum (18), and sixteen for
Pompeii/Paestum (15). All fifteen southern sites eventually reach size two.
Their first size-three observation ranges from age 16 to 59.

During ages 0-15, Pompeii/Paestum has 240 normal city samples:

- 189/240 (78.8%) have local food at most two.
- 115/240 (47.9%) have negative food surplus, including current imports/exports
  and consumption. These are deficit observations, not proof of population loss;
  a size-one city cannot shrink further.
- Only 78/240 (32.5%) receive food imports.

Roma has no deficit samples in its corresponding 314 normal observations, and
Mediolanum has none in 320. The early contrast persists after excluding startup
disorder and food-based production.

The southern site becomes useful later. At age 50, among normal observations:

| City | Games with eligible samples | Median population | Median hammers/turn |
| --- | ---: | ---: | ---: |
| Roma | 18 | 7 | 16 |
| Mediolanum | 14 | 5 | 7 |
| Pompeii/Paestum | 13 | 3 | 7 |

Its median maximum population over the entire observed Roman ownership period
is six, with range three to eight. Exact-age samples condition on continued
Roman ownership and normal operation; they are not survival-adjusted outcomes.
Hammers are observed city production yields, not completed military production
or a measurement of which units the AI actually builds.

## Terrain mechanism

`CvPlot::calculateNatureYield` applies terrain, hill, feature and visible-resource
yields. `calculateYield` adds one production and one commerce to city centers,
with **no minimum food yield**. The inherited yield XML gives hills -1 food and
+1 production. Ordinary forest removal on founding does not change the food
conclusion at these sites.

| Site | Center terrain | Center food / production after ordinary feature removal | Water tiles in 21-tile radius |
| --- | --- | ---: | ---: |
| Roma (60, 44) | Flat grassland | 2 / 1 | 11 |
| Mediolanum (59, 47) | Flat grassland | 2 / 1 | 2 |
| Pompeii/Paestum (62, 42) | Plains hills | 0 / 3 | 14 |
| Messana (61, 40) | Plains hills | 0 / 3 | 17 |

The tile inventory describes potential radius access, not exclusive ownership
or actual worked tiles. It includes the center. Peaks are counted separately
from water; five of Mediolanum's potential tiles are peaks.

Pompeii has seven land tiles including its center; five are hills. Its three
resources are pigs at (61, 43), sheep at (62, 41), and clams at (63, 44).
The pigs overlap Roma's radius, so both cities cannot work them simultaneously.
The clams are in Pompeii's outer ring. First-ring sheep are plains hills: only
one food before improvement, rising to three with a pasture, plus production
and commerce. They are a good improved tile, but do not remove the initial
development requirement.

With a zero-food center, an unimproved two-food worked tile merely feeds the
first citizen; it does not supply growth. Working one-food sheep or ordinary
coast instead creates a deficit without imports or other bonuses. That is a
specific, source-supported reason for slow growth, consistent with the observed
early local-food totals.

Roma already has substantial potential resources: fish, pigs, sheep, marble,
wine, iron and clams, although some overlap neighbors or lie overseas.
Mediolanum has wheat on flat grassland, two stone resources, and shared wine,
marble and clams. It has a different mix of flat land, hills and Alpine peaks;
these are not uniformly poor sites.

Messana shows a related problem: local food is insufficient after exports in
70.2% of its normal age-10-to-50 samples. That comparison has only five games
with eligible samples, so it is weaker evidence than Pompeii. Its food resources
include fish two tiles west and sheep shared with the southern mainland site.

## What is established and what remains uncertain

The map and source validate a southern Italian starting-food disadvantage;
the recordings validate a substantial early growth delay. They also refute
the stronger claim that the southern city never becomes productive.

Balance recordings do not contain worked plots, improvement dates, culture
access, building completion dates, city maintenance or actual production queues.
They therefore cannot separate how much of the delay comes from inherent land,
slow pasture/work-boat development, Roma taking shared pigs, trade allocation,
or the AI choosing production over growth. In this mod it is the Sailing-era
harbor that gives +1 food on sea tiles; the lighthouse is a different,
Compass-era building and does not provide that ordinary coastal-food bonus.
Whether the AI builds the harbor promptly is not recorded here.

## Targeted next change to consider

Improve the represented Campanian agricultural base, rather than adding more
production to an already production-heavy city center. Options include:

- Convert the southern city-center tile from plains hills to grass hills:
  center food rises from zero to one, while production falls from three to two.
  This changes food/production balance rather than granting every yield at once.
- Give the southern city a fertile flat agricultural tile or food resource
  within its first ring that does not depend on borrowing Roma's pigs. This
  preserves the defensive hill site but requires workers and tile assignment.

These are alternatives to evaluate, not a recommendation to stack multiple
bonuses immediately. The historical rationale for a fertile Campanian pocket
is sound: the Pompeii archaeological park describes fertile, cultivated land
around the city and productive farms at Boscoreale. See
[Boscoreale](https://pompeiisites.org/en/boscoreale/) and its
[landscape exhibit](https://pompeiisites.org/en/boscoreale-en/antiquarium-sala-i/).
The exact Civ4 terrain representation is a design choice, not something the
historical evidence uniquely determines.

No additional run is required to establish this diagnosis. To choose the size
of a terrain adjustment and determine its effect on Roman expansion, a later
comparison should measure early city growth, actual military production and
conquests. Additional worked-tile, improvement and harbor-completion recording
would make that comparison more informative. No test was launched or prepared.

Source references: `CvPlot.cpp` (`calculateNatureYield`, `calculateYield`),
`CvCity.cpp` (`getLocalFoodYield`, `getYieldRate`), the 3000 BC WorldBuilder map,
mod terrain/bonus/improvement/building XML, inherited `CIV4YieldInfos.xml`, and
`Resources.py` (no scripted early Italian resource additions).

Extracted observations and map inventory are preserved in the ignored batch
folder as `italian_city_samples.json` and `italian_tile_inventory.json`.

## Implemented adjustment

The user selected one modest adjustment. The tile at (62, 42) is now grassland
hills rather than plains hills in all four scenario maps. This is one geographic
terrain change kept consistent across starts; hills, resources, routes and
existing scenario cities remain intact. Its ordinary city-center yield changes
from 0 food / 3 production to 1 food / 2 production after feature removal.
The unworked terrain also changes, so other city placements can benefit from
the tile. The measurements above describe the previous terrain, not a tested
outcome of the change. No simulations were run; installed maps require sync.
