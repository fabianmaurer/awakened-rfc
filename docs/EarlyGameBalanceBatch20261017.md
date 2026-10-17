# Early-game balance: 17 October 2026 batch analysis

The latest changes greatly improve Carthaginian survival, but do not yet
produce effective Punic conquest or demonstrate the desired Mediterranean
hegemony frequency. Rome's late-antique collapse remains common.

## Recordings and comparison

Current batch: `testing/runs/balance-ai-3000bc-20games-200turns-seeds-1-20-20261016-235048-d7628a`.
Baseline: `testing/runs/balance-ai-3000bc-20games-200turns-seeds-1-20-20261016-224552-b87fd3`.

Both contain 20 complete games, seeds 1-20, with no recorded gameplay errors
or recording-integrity issues. All 20 seeds qualify for comparison. Settings
are 3000 BC, Prince, Normal, Aggressive AI and No Technology Brokering, with
every-turn recording. The endpoint is engine turn 199, AD 780: the launcher's
200 completed turns include engine turn zero.

Current runtime fingerprint: `c51450388b6a7e50c15c6e7dc5891a8f3823cf13f5aa4395260b7bb02c3cbdbb`.
Baseline: `098c28050aa461223d3a8e97c99bb7a14bd9e13a899965dbd2dbc9f4870ac650`.

The deployment backup shows several simultaneous changes: African invasion
schedules, Gadir/Karalis opportunities, Punic war priorities, stricter collapse
conditions, two extra AI Roman assault Praetorians and the Pompeii grassland
adjustment. This comparison measures the combined package. Matching seeds
does not isolate individual changes; changed actions also change subsequent RNG
consumption. Earlier differing outcomes occur even before the targeted changes
take effect, so these are not identical deterministic histories up to intervention.

## Survival and population

Population is the sum of city population points. Medians include eliminated
civilizations as zero; survivor-only values remain in the generated reports.

| Civilization | AD 780 survivors, previous -> current | Median population, previous -> current |
| --- | ---: | ---: |
| Carthage | 4/20 -> 17/20 | 0 -> 10.5 |
| Egypt | 14/20 -> 19/20 | 16 -> 24 |
| Greece | 10/20 -> 13/20 | 3 -> 10.5 |
| Rome | 8/20 -> 10/20 | 0 -> 5.5 |
| China | 18/20 -> 19/20 | 66.5 -> 58.5 |
| India | 20/20 -> 20/20 | 49.5 -> 51.5 |
| Persia | 18/20 -> 16/20 | 17 -> 18 |

All four previous Carthaginian survivors survive again; thirteen previously
eliminated seeds now survive. The three remaining deaths are seeds 7, 8 and 10.
The median matched-seed final population change is +8.5, with a range of 0 to
+18. Median matched city change is +2.5. These paired statistics differ from
the difference between the two cohorts' medians.

Much of the improvement is late survival rather than classical dominance:

| Checkpoint | Carthage median population / cities, previous -> current | Survivors, previous -> current |
| --- | --- | ---: |
| 25 BC | 9.5 / 3 -> 10 / 4 | 20 -> 20 |
| AD 110 | 10 / 3 -> 11 / 4 | 20 -> 20 |
| AD 260 | 11 / 3 -> 12 / 4 | 19 -> 20 |
| AD 500 | 6.5 / 2 -> 10 / 3 | 14 -> 19 |
| AD 780 | 0 / 0 -> 10.5 / 3 | 4 -> 17 |

At AD 110, Roman median population is 25.5 in both batches. Current Carthage
has less population than Rome in every seed at that checkpoint. This is one
economic indicator, not a territorial hegemony definition.

## Punic wars and territorial opportunities

Wars between Carthage and Rome occur while both own cities in 15/20 current
games, versus 12/20 previously. By AD 100 the counts are 11/20 versus 12/20:
the extra eventual wars do not demonstrate an earlier Punic offensive.
Pre-spawn diplomatic war flags were excluded from these counts.

Carthage conquers **zero Roman cities**, zero Greek cities and zero independent
cities across all twenty current games. Its only conquest is Sabratha from
the Native player in seed 19, AD 710. Rome conquers one Punic city. War incidence
therefore does not establish successful campaigning.

Both independent opportunities actually appear in all twenty current games:

- **Gadir (51,40):** Carthage receives it through a non-conquest transfer in
  seed 18, AD 245, and loses it to barbarians in AD 455. In seed 14, it founds
  Qart-Gadir on the cleared site in AD 710, then loses it to Spain's transfer
  in AD 730. It never conquers the original independent city. Greece receives
  Gadir through non-conquest transfers in six seeds; Rome in two.
- **Karalis (58,42):** Carthage receives it through a non-conquest transfer in
  seed 14, AD 320, and retains it to the endpoint. Rome receives it in seed 17,
  40 BC. Neither acquisition is recorded as conquest.
- Carthage never owns an Italian mainland city in this batch. Its only owned
  location in the central Mediterranean/Italian target rectangle is Karalis.

There is no evidence here that the roughly 25% hegemony target has been
achieved. A numerical hegemony success rate still needs a fixed territorial
and political criterion, selected before calibration. Surviving after Rome
collapses is insufficient evidence of that outcome.

## Invasions and collapse

Carthaginian conquest losses to barbarians fall from 54 to 17 events, while
losses to Natives rise from 2 to 9. These are capture events, not unique cities.
Egyptian losses to barbarians fall from 41 to 13; Roman losses fall from 81 to
66. The regional relief benefits multiple coastal civilizations.

New successful scripted-spawn events record 140 North African horse archers
across the twenty games: 60 in the broad North African rectangle and 80 in
Tripolitania. The modified western African schedule adds 40 swordsmen. These
are actual created units, not configured attempts. The previous batch lacks
this event, so a measured before/after spawn-count reduction is unavailable.
The events do not trace individual spawned units to subsequent city captures.

Three Carthaginian collapse checks fail the new extra conditions: seed 8's
single barbarian-held original city, and single-city losses in seeds 15 and
16. Seeds 15 and 16 survive to the endpoint. Seed 8 later collapses through
civil war, so a blocked check does not guarantee survival.

The remaining Punic deaths show different chains:

- Seed 7: barbarians take Qart-Hadasht in AD 710; civil war removes the
  remaining city in AD 740, at pre-collapse stability -44.
- Seed 8: Native conquests, a non-conquest city transfer and a barbarian
  conquest precede civil war in AD 515, at stability -43.
- Seed 10: Natives take Arae and Oea in AD 155/170. The city-count rule removes
  Qart-Hadasht and Hippo in AD 320: four reference cities, two remaining,
  stability -22. The revised rule still removes a two-city core at modestly
  negative stability after two losses.

All ten current Roman deaths have an explicit collapse trigger with cities
still owned: five barbarian-city-loss collapses, three city-count collapses
and two civil wars. All ten remove two or three remaining cities. Five of the
eight loss-rule collapses occur above the civil-war threshold of -40. These
rules remain major amplifiers of military setbacks; the data do not establish
that the affected empires would otherwise recover.

## Labor and food

The median completed Slavery spell remains two turns for the civilizations
starting in it. Some later adoption and real employment occur, but classical
Slavery remains uncommon. Mean assigned slaves per normal city snapshot under
active Slavery are 0.31 for Carthage, 0.41 for Rome, 0.30 for China and 0.57
for Japan. Rome's corresponding baseline value is 0.21; Carthage's is 0.31.
These conditional sample averages are not controlled estimates of a civic's
benefit or measures of adoption frequency.

No labor civic score evaluations were recorded. The batch cannot explain the
numerical score behind a particular switch. It shows that the existing labor
heuristic has not produced widespread sustained classical Slavery.

Normal food-deficit samples are 8.2% at city sizes 1-3, 12.6% at sizes 4-7,
and 18.3% at sizes 8+, versus 7.9%, 12.2% and 17.2% previously. Mean surplus
remains positive in every size group. This is not evidence of general famine;
shortages are concentrated, and population losses have other possible causes.

## Follow-up: can Punic cities support an offensive?

Further inspection of the same twenty recordings supports production capacity
as a substantial constraint alongside military choices. At exact calendar
checkpoints, the median sum of recorded city production yields is:

| Checkpoint | Carthage hammers/turn | Rome hammers/turn |
| --- | ---: | ---: |
| 625 BC | 10 | 13 |
| 250 BC | 15 | 29 |
| AD 95 | 19 | 45.5 |
| AD 275 | 22 | 46.5 |

These are national production yields, not hammers actually allocated to units
or a reconstruction of unit-specific production modifiers. At AD 95, Carthage
has a median four cities versus Rome's five: weaker output per settlement is
part of the gap, alongside the smaller empire.

Qart-Hadasht's median production at AD 95 is seven hammers at population six
(20 observations). Hippo at (56,39) supplies six at population four (15 games).
The eastern settlements remain small: Sabratha supplies 2.5 hammers at median
population 1.5 (six games); Oea supplies three at population one (seven games).
These site medians condition on the city being owned at that checkpoint.

Same-age normal samples also show slow secondary-city development. Hippo's
median population at age 25 is still one, with four hammers and two local food
(16 games). Median imports and surplus at that exact age are both two. Sabratha
and Oea also have median population one at age 25 (eight and seven games).
Qart-Hadasht reaches median population four at age 25 (18 normal observations),
so the capital's initial growth is stronger than its satellites'. Imports help
but do not make all settlements rapidly productive.

At AD 95, Carthage has median three galleys, 4.5 archers and 1.5 Numidian cavalry;
only three games have any catapult. Rome has median five Praetorians and two
axemen. During engine turns 100-160, Carthage never has an ordinary swordsman
or axeman in any recorded army. These snapshots cannot distinguish units never
trained from units lost before the end-turn recording, or establish whether
technology/resources prevented construction. Ship presence does not establish
that transports are loaded or assigned to an assault.

The evidence therefore supports a combined bottleneck: a modest production
base carries settlement, defense and naval costs, while the resulting army
lacks a substantial city-assault component. It does not support attributing
failure primarily to naval execution, or claiming that improved orders alone
would reliably overcome Rome. A terrain/food audit of the Punic satellites
and investigation of military eligibility/build allocation should precede
further generic war-target weighting.

The extraction script and raw output are preserved as
`testing/runs/analyze_carthage_capacity.py` and
`testing/runs/carthage-capacity-output.txt`.

## Recommended next work

Retain the African-pressure improvements while investigating Punic campaign
execution: city-assault composition, transport loading, target reachability and
actual landing orders. More target weighting alone has not yielded conquests.
Inspect why the independent ports change hands without conquest before treating
their ownership as proof of successful naval war.

Review whether two lost outposts should still dissolve a viable two-city core
at stability -22. Rome's frequent losses also justify examining European
invasion pressure and defense behavior before adding further starting units.
The current evidence cannot isolate the extra Praetorians or Pompeii's food
change, and does not yet justify another unconditional grant.

Define a classical hegemony criterion before calibrating its frequency. Use
the existing recordings to specify which territory, rivals and checkpoint
matter; do not equate the 85% survival rate with that design target.

Generated `report.md`, `summary.json` and `comparison.md` are in the current
batch folder. Focused event extracts are in `focused-analysis-data.json` there.
Only existing recordings were analyzed; no gameplay was launched and no
gameplay files were changed for this analysis.
