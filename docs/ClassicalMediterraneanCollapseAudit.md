# Classical Mediterranean collapse audit

Initial investigation dated 2026-10-16 used source inspection and existing
recordings only. Subsequent authorized changes are documented in the final
section. No new simulations were run.

Batch: `testing/runs/balance-ai-3000bc-20games-200turns-seeds-1-20-20261016-224552-b87fd3`.
Twenty complete, error-free 3000 BC / Prince / Normal / Aggressive AI games,
200 simulated turns, ending at engine turn 199 (780 AD).

## Finding

Barbarian conquests are the main observed military pressure. Automatic collapse
rules then turn territorial setbacks into complete elimination, often while
the civilization still owns its capital and other cities. This is not primarily
a pattern of independently occurring stability civil wars.

Of 194 recorded `cityAcquired` events with `conquest=True` and Greece, Carthage
or Rome as the old owner, 176 (90.7%) transfer to barbarians:

| Civilization | To barbarians | To Celts | To Natives | To another major |
| --- | ---: | ---: | ---: | ---: |
| Greece | 41 | 0 | 0 | 0 |
| Carthage | 54 | 0 | 2 | 0 |
| Rome | 81 | 14 | 0 | 2, to Greece |

These are conquest events, not unique cities; repeated captures count again.
Scripted non-conquest city transfers are excluded. Barbarian ownership does not
identify whether an attacking unit came from a scripted wave or ordinary game
spawning.

The 38 observed transitions from owning cities to owning none have these causes:

| Civilization | City count halved | Barbarian city rule | Stability civil war | Homeland rule | Last city conquered |
| --- | ---: | ---: | ---: | ---: | ---: |
| Greece | 4 | 3 | 3 | 0 | 0 |
| Carthage | 7 | 4 | 2 | 1 | 2 |
| Rome | 5 | 4 | 3 | 0 | 0 |

Thus 36 deaths involve explicit full-collapse calls with cities still owned;
only two are ordinary elimination by conquest. This does not prove the 36
would have survived without the scripted rules. Each of those collapse events
has at least one recorded barbarian conquest against that civilization within
the preceding 36 engine turns, including the trigger turn.

Earlier aggregate reports counted 38 collapse trigger events for these three
civilizations. Two were secondary calls after an earlier branch had already
removed every city: Rome seed 8 and Carthage seed 14. Excluding zero-city calls
avoids mistaking those for additional collapses.

## Rules that amplify city losses

### City count check

`RiseAndFall.collapseGeneric`, called every 18 turns after 2000 BC, compares
current cities with its stored count. Once past the 25-turn birth grace period,
an AI civilization that is not a vassal fully collapses if:

`currentCities * 2 <= storedCities`

The stored count normally updates on a successful check. It is not a lifetime
peak-city counter. The condition includes exactly half, has no minimum number
of lost cities, and requires no negative stability. A fall from two cities to
one can therefore remove the remaining capital.

The six Roman games with triggers at turn 180 include five primary city-count
collapses and one barbarian collapse with a secondary zero-city count check.
The concentration follows the 18-turn checking schedule, not a Roman death date.

Examples:

- **Carthage, seed 4:** two cities at turn 144; Sabratha is conquered by
  barbarians at 147; Qart-Hadasht remains until the city-count rule removes it
  at 162. The preceding snapshot has stability -26, above the civil-war
  threshold. Losing one city leads to complete elimination.
- **Rome, seed 3:** four cities at turn 162; barbarians capture Mediolanum at
  175 and Lugdunum at 177. At 180, the rule transfers the still-held Roma and
  Pompeii to independents. Previous-turn stability is -19.
- **Greece, seed 12:** the city-count rule removes its last owned city at turn
  108; the preceding snapshot has stability -1. Low stability is not a
  prerequisite for this type of collapse.

### Barbarian city check

`RiseAndFall.collapseByBarbs`, called every four turns from 200 AD, counts cities
currently owned by barbarians whose `getOriginalOwner()` is the civilization.
It triggers full collapse when:

`barbarianHeldOriginallyFoundedCities * 2 > currentCities`, with currentCities > 0.

This is not a recent direct-loss counter. There is no lookback window or
stability prerequisite, and original ownership differs from last ownership.
A civilization that founded a city, lost it to Greece, and later saw Greece
lose it to barbarians can have that city count against it.

**Rome, seed 9:** before the turn-168 check, barbarians hold Lentia and Emona,
both recorded as Roman-founded cities. Rome lost Emona to Greece at turn 124;
Lentia was captured directly by barbarians at 164. Rome still owns three cities,
so `2 * 2 > 3` triggers fragmentation at 168. Roma, Mediolanum and Pompeii are
all transferred without conquest. Previous-turn stability is -14; Rome still
has four Praetorians, two archers and two axemen, alongside naval units.
The surviving empire is removed by the original-ownership rule rather than
being conquered or crossing the -40 civil-war threshold.

### Stability and secession reinforce losses

`Stability.onCityAcquired` applies an immediate stability penalty to the loser.
Outside special birth/resurrection cases, the base penalty is
`max(-5, (16 - remainingCities) / 2)` using Python 2 integer division. Losing to
barbarians or Celts adds one, and losing the historical capital adds 20.
A two-city civilization losing one non-capital city to barbarians ordinarily
loses eight stability points; a historical-capital loss adds 20 more.

Combat defeats also feed negative stability through `onCombatResult` and
`updateBaseStability`. Secession can remove another city below -20 stability;
full AI civil war is checked every ten turns and requires stability below -40
(with birth and golden-age guards). Secession, city losses and automatic
fragmentation can therefore reinforce one another.

The current collapse event is emitted after fragmentation, which itself fires
city-loss callbacks. Final snapshot stability can include the consequences of
collapse. It must not be treated as the stability that caused the collapse.
Previous-turn snapshots are useful context, but are not exact pre-check values.

## Scripted invasion pressure

`Barbs.checkTurn` contains substantial overlapping schedules:

- European axemen and swordsmen before and during late antiquity.
- Between 300 and 600 AD, western European groups of four axemen, four
  swordsmen and three horse archers on staggered six-turn schedules, in
  addition to overlapping older schedules and an eastern horse-archer schedule.
- North Africa receives two horse archers and two camel archers on separate
  ten-turn schedules from 50 AD, with additional African schedules later.

These are configured attempts, not measured successful spawns. `spawnUnits`
requires a valid plot. The actual spawn count, the origin of attacking units,
local concentration and defenders at the attacked city are not recorded by
the balance mode. National army totals cannot answer those questions and
include naval units and other units that may not defend the threatened city.

The schedules are a plausible source of the observed pressure. The recordings
establish who conquered the cities, not which schedule or combat matchup was
responsible. Weak production, obsolete defenders, positioning, secession and
invasion intensity cannot yet be cleanly separated.

## Do we need more recording and another batch?

No new run is needed to establish the collapse chain or identify the rules
that amplify losses. Another unchanged 20-game balance batch would add little
to this diagnosis. Targeted recording is useful before deciding how much to
change invasion strength, stability penalties or collapse thresholds.

Recommended additions, dormant outside observer mode:

1. Emit a collapse-decision event **before** any inheritance or fragmentation
   mutation: rule, current/stored counts, relevant barbarian-held original-city
   coordinates, pre-check stability, capital, vassal status, and outcome guards.
   A small record for checks close to the threshold would also show recovery
   and near misses among survivors.
2. Record secession explicitly, including city, pre-transfer stability and
   qualifying conditions. `conquest=False` alone does not establish secession.
3. Record successful scripted spawns with schedule identifier, location, type
   and count; aggregate skipped attempts. Observe existing results without
   consuming RNG or invoking spawn/AI calculations again.
4. In diagnostics mode, record local combat/city-loss context: unit coordinates,
   type, owner and damage, city defenders and defense state, and nearby threats.
   Existing diagnostic combat events record owner/type but lack location;
   diagnostic unit snapshots can miss units spawned and killed in the same turn.
5. Record existing stability inputs for each monitored civilization: total/base
   stability, combat modifier and actual city-loss deltas. Existing UI parameter
   arrays are maintained for the active player, so they cannot simply be logged
   as valid per-civilization breakdowns. Do not rerun stability calculations for
   reporting.

After adding recording, a focused five-seed diagnostic batch, **3, 4, 7, 9 and
17**, for **200 turns from 3000 BC**, with the same settings, would cover Roman
and Carthaginian city-count collapse, civil war, the original-city barbarian
rule, and ordinary last-city conquest. These are selected case studies, not a
new representative balance estimate. Keep gameplay unchanged for that pass.
Once a mechanic is changed, use the same 20 balance seeds for its evaluation.

No test launcher was created or executed as part of this investigation.

## Source references

- `Awakened RFC/Assets/Python/RiseAndFall.py`: `checkTurn`, `collapseByBarbs`,
  `collapseGeneric`, `collapseMotherland`, `secession`.
- `Awakened RFC/Assets/Python/Stability.py`: `onCityAcquired`, `onCombatResult`,
  `updateBaseStability`, `checkImplosion`.
- `Awakened RFC/Assets/Python/Barbs.py`: `checkTurn`, `spawnUnits`.
- `Awakened RFC/Assets/Python/RFCUtils.py`: `pickFragmentation`.
- `Awakened RFC/Assets/Python/GameObserver.py`: `event`, `city_data`, `snapshot`.

Additional extracted events are preserved in the ignored batch folder as
`collapse_details.json`.

## Historical accuracy: rise, extent and timing

Follow-up analysis uses all per-turn city rosters and the recorded calendar,
not just end-of-run survival. Historical accuracy on average is the target;
equal survival or equal civilization strength is not the objective. The earlier
description of harsh collapse rules does not by itself justify making every
classical civilization survive longer.

All three normally grow beyond their first city, but their territorial growth
is limited:

| Civilization | Median maximum simultaneous cities | Range of maxima | Eliminated by 780 AD | Median elimination year among eliminated games |
| --- | ---: | ---: | ---: | ---: |
| Greece | 3 | 2-6 | 10/20 | 615 AD |
| Carthage | 4 | 1-6 | 16/20 | 530 AD |
| Rome | 6 | 4-8 | 12/20 | 590 AD |

Maximum city count is computed separately for each game before taking its
median. It is not the number of unique cities ever owned. Elimination dates
exclude surviving, right-censored runs and are not whole-cohort median survival
times. City counts alone cannot quantify historical land area or maritime
commercial influence.

### Carthage: political survival is late, expansion is modest

Historical Punic Carthage was a Mediterranean trading power before its Roman
destruction in 146 BC; subsequent Roman Carthage is not continued independence
of the Punic state. See [UNESCO's Carthage overview](https://whc.unesco.org/en/list/37/).

At the recorded 145 BC boundary, all 20 Carthages still own cities (median
three). All remain at 110 AD. The 16 eliminations occur from 215 to 770 AD,
with median 530 AD: their independent political demise is centuries late,
usually through barbarian pressure instead of Roman conquest.

They do form a modest North African network: Hippo occurs in 16 games,
Sabratha in 11. Using the map-coordinate rectangle x44-55/y40-46 as a coarse
Iberian city-location check, 12 games reach Iberia at some point, so overseas
colonization is not absent. Only one conquest into Carthaginian ownership is
recorded across the batch. The appropriate question is whether it becomes a
credible commercial and military rival to Rome before Roman expansion, not
whether its independent state survives longer after late antiquity.

### Greece: colonial development without the eastern conquests

The slot's historical scope matters: independent city-states, Alexander's
empire and separate Hellenistic kingdoms are different political formations.
Alexander's campaigns of 334-323 BC extended through Egypt and the Persian
Empire toward India; successor kingdoms followed his death. The final
Hellenistic dynasty fell to Rome in 31/30 BC. See the
[Metropolitan Museum's Hellenistic overview](https://www.metmuseum.org/fr/essays/art-of-the-hellenistic-age-and-the-hellenistic-tradition).

At 325 BC, the batch has median two Greek cities. Typical holdings are Athens,
Byzantion, Sparta, Crete, and occasional Italian or Black Sea colonies. Only six
incoming conquests are recorded in all 20 games: four from barbarians and two
from Rome, with none from Persia. No game records a Greek city in the coarse
Persian-core rectangle x79-86/y37-46. One game reaches Alexandria.

This reproduces some Greek colonization, but not an average Macedonian or
Hellenistic imperial expansion. Independent survival is generally too long if
the slot represents ancient Greek/Hellenistic states: 19/20 remain at 145 BC,
17/20 at 395 AD, and 10/20 at 780 AD. There are early individual failures,
including 490 BC, but they do not describe the overall pattern. Continued Greek
culture under Roman or Byzantine government should not be equated with an
independent ancient Greek player.

### Rome: regional growth, missing Mediterranean empire, late western collapse

Historical Rome reached its maximum territorial extent around 117 AD across
Europe, North Africa and Asia Minor, and the conventional Western imperial
endpoint is 476 AD. The Eastern Empire continued, so disappearance of all Roman
authority is not an appropriate interpretation of that date. See
[Milwaukee Public Museum's Roman overview](https://www.mpm.org/research-collections/anthropology/anthropology-collections-research/mediterranean-oil-lamps/roman-empire-brief-history)
and the [Metropolitan Museum's Roman history](https://www.metmuseum.org/essays/the-roman-empire-27-b-c-393-a-d).

The game Romans do grow: every game reaches at least four simultaneous cities,
with median six, and median population rises from 15 around 325 BC to 25.5 at
110 AD. Their typical territory is Italy, parts of Gaul and the Adriatic fringe.
Conquests total 46 across the batch, all from Celts (36) or barbarians (10);
none are from another major civilization. City rosters show no Roman holdings
in North Africa, Egypt or the Levant in any game. Four games reach the coarse
Iberian rectangle, and two hold Constantinople at its usual coordinate.

All 20 survive at 395 AD and 19 at 470 AD. Observed eliminations span 410-740 AD,
with median 590 AD among the twelve eliminated runs. Against a Western Roman
benchmark, the general failure is not premature disappearance. Rome does not
first achieve its historical imperial reach, then usually survives somewhat
late as a regional state before abrupt fragmentation. An eastern-continuity
benchmark would additionally require looking for a durable Roman successor,
not merely moving Rome's elimination date.

### Revised evaluation priorities

First measure territorial and political outcomes at historical dates: Greek
eastern expansion in the fourth century BC, Carthaginian strength and its
transfer to Roman control in the third/second centuries BC, Roman Mediterranean
reach in the first/second centuries AD, and western fragmentation with eastern
continuity in late antiquity. Exact repetitions of every conquest in every seed
are unnecessary; the distribution should make those broad trajectories common.

The current evidence prioritizes missing major-civilization conquest and
imperial expansion over a general survival buff. Further recording should
therefore include war initiation, military objectives and local force balance
while these civilizations are rising, as well as the previously proposed
collapse context. Targeted collapse diagnostics alone would not explain why
the Roman and Greek empires usually fail to form.

Extracted per-game peaks and city rosters are in the ignored batch artifact
`historical_expansion_details.json`. No new simulations were run.

## Implemented first pass

Following the user's request to soften extreme collapse and strengthen Rome:

- **City-count fragmentation:** now requires at least two lost cities, at least
  half of the stored city count lost, at least one city remaining, and stability
  strictly below -20. Existing birth grace and AI/vassal guards still apply.
  A 2-to-1 loss no longer qualifies. Protected setbacks update the stored count
  at the check, so they are not held against the country indefinitely.
- **Barbarian-city fragmentation:** now additionally requires at least two
  originally founded cities held by barbarians and stability below -20. A lone
  lost outpost no longer qualifies, and an otherwise stable country is not
  removed by this rule. This still uses original ownership, not a recent-loss
  history; it is a limited safeguard rather than a rewrite of the mechanic.
- **Empty-country checks:** the homeland rule skips cityless civilizations,
  and the city-count rule cannot fragment them again. Civil war, conquest and
  secession remain possible; this is not immunity for small countries.
- **AI Roman starting force:** two additional Praetorians with the city-assault
  AI role accompany the existing four, three settlers and two assault galleys.
  This is a one-time AI starting-force adjustment, with no civilization cost
  modifiers or unit-stat changes. Human Rome's starting force is unchanged.
- **Karalis, Sardinia:** a new optional independent settlement at (58, 42),
  scheduled around 700 BC in the 3000 BC scenario. It has population two and
  one archer. On successful founding, an unimproved nearby clam resource gets
  fishing boats to support the small island's food budget. Existing ownership,
  nearby cities and the normal founding/retry guards can prevent its creation;
  it does not overwrite another civilization's settlement. It lies outside
  Rome's birth-flip rectangle and exceptions. Rome or Carthage must acquire it
  through ordinary gameplay. Both existing war maps value the location.

Karalis represents an already inhabited Phoenician/Punic center rather than
unclaimed land. The date is a coarse scenario approximation, not a claim of an
exact archaeological foundation year. See the
[Cagliari archaeological museum](https://museinazionalicagliari.cultura.gov.it/en/musei/esplora-la-collezione/luogo/cagliari/).
Roman expansion combined conquest and diplomacy with subsequent colonial
settlement; those are complementary processes. See the
[Metropolitan Museum's Roman Republic overview](https://www.metmuseum.org/ja/essays/the-roman-republic).

New observer `collapse_check` events preserve candidate counts, pre-check
stability and whether the new numeric thresholds pass, including blocked
2-to-1 cases. The numeric result is not a full eligibility decision: separate
human/vassal guards can still prevent city-count fragmentation. Existing
`collapse_trigger` events now include `stability_before`, captured before
inheritance/fragmentation and its city-loss callbacks. Detailed check payloads
remain in the raw recordings.

This is deliberately a modest experiment. A neutral island can strengthen
Carthage instead of Rome; additional Roman units do not guarantee successful
amphibious operations or wars against the intended rivals. The next priorities
are Roman target selection and sea-invasion execution if the larger army still
avoids major opponents. More neutral cities should be added where they replace
historically inhabited territory, with attention to existing birth flips and
city spacing, rather than as arbitrary Roman rewards.

Files changed for this pass: `RiseAndFall.py`, `Barbs.py`, and `RFCUtils.py`.
No DLL rebuild is needed. Static source review and whitespace checks were
performed; no tests or gameplay simulations were run. In-game loading, whether
Karalis successfully appears and remains viable, and balance/multiplayer
effects remain unvalidated. Changes are in the workspace mod tree; the installed
mod must be synchronized before using the observer launcher.
