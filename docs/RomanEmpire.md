# Roman expansion and administration

Implemented 17 October 2026 for new games. These are named Roman civic
variants, not restored general civilization cost modifiers. Both human and
AI Rome receive the same civic effects. Other civilizations retain the
ordinary Republic and Warrior Society.

## Civics and provinces

- **Roman Legions** replaces Warrior Society: +50% melee/siege production,
  +2 experience for trained melee units, half foreign unit supply cost,
  and melee road construction (base work rate 100). It has no siege combat
  penalty. Galleys and triremes also receive +50% production; galleys gain
  one cargo slot while the civic is active. Existing passengers remain aboard
  after leaving the civic, but excess capacity cannot be refilled.
  Existing Roman road movement remains active. Mounted/gunpowder
  production and experience receive no bonus.
- **Roman Republic** replaces Republic: half initial conquest resistance,
  rounded up; half the connected historical provinces' proportional share
  of foreign-territory and empire-size stability penalties. It replaces the
  ordinary specialist food discount. Other stability components are unchanged.
  Rome can adopt it without Code of Laws, so its usual birth profile works.
- **Provincial Administration** replaces the Courthouse: 60 base production,
  Writing and Roman Republic required to construct; ordinary Courthouse
  effects, including -50% city maintenance, remain after government changes.
  Rome retains its Forum as its Market replacement.

`CvPlayer::getRomanProvinceStage` defines the fixed-map areas once, shared
with Python through `CyPlayer.isRomanProvince`: Italy and nearby islands,
Iberia, western North Africa, Greece/Balkans/Anatolia, Gaul/Rhine frontier,
southern Britain, Egypt/Cyrenaica and the Levant. Roads, rivers and maritime
connections use the normal capital trade network. Foreign-plot relief follows
the existing six-turn territory refresh; city-count relief checks current
connections. Discount shares are proportional to eligible plots/cities and
round down; unrelated territory contributes its normal share of the penalty.

## Starting advantage and intended trajectory

Rome receives Mathematics in both its ordinary birth tech list and the 800 BC
setup, equally for human and AI Rome. Catapults require Mathematics in this mod.
Construction is no longer forced merely to unlock catapults. Other research
continues normally. No recurring technology grants are added.

The objective is a substantial territorial peak around AD 100-200, followed by
frequent organic collapse. Endpoint survival is not a success criterion. The
existing stability and collapse rules remain unchanged.

## Campaign AI

Before AD 300, AI Rome using Roman Legions prefers accessible, revealed
provincial cities, weighted toward Italy, western Mediterranean possessions,
then Greece and further provinces. Existing wars/plans take priority over
opening another theater. Land and amphibious target scores reinforce that
opponent; provincial conquests are retained under Roman Republic, overriding
the inherited Carthage/Pompeii razing preference.

New campaign preparation requires Roma as capital, stability at least -10,
no active plague or financial trouble. Roma and currently threatened cities
must meet their defensive needs; quiet provinces do not veto a campaign for
lacking their ordinary preferred garrison. While early AI Roman Legions are
active, quiet cities train cheap archer garrisons: one defender and the capital two.
Rome starts with Archery as well as Mathematics. Existing Praetorians in quiet
cities switch to city-attack roles only after replacement archers are present;
safe field Praetorians also switch, except those accompanying settlers. Campaign
recruitment prefers Praetorians for non-siege attackers. Occupied or
threatened cities retain ordinary reinforcement calculations. After AD 300 or
leaving Roman Legions, ordinary garrison policies resume. Human garrisons remain
user-operated. Requirements scale with currently visible defenses, equally for
minor and major targets. At most two land defenders and at most 20% defense
need four non-siege attackers and no mandatory siege. Larger garrisons need
`clamp(defenders + 2, 4, 8)` non-siege attackers. Defense above 20% or at least
three defenders requires one siege unit; defense at least 60% or at least five
defenders requires two. An unobserved garrison uses five non-siege attackers
plus one siege. The local-strength check still applies. Overseas campaigns require enough assault
transport slots for the required attackers, with the expedition
assembled at one safe embarkation port on the capital's landmass. Route choice
compares passable land distance from Roman cities with passable sea distance
plus four steps for assembly and landing; ties favor land. A shared land area
does not exclude a shorter sea crossing. These are strategic distance estimates;
units still validate access, danger and movement on their actual paths. Major
opponents are judged by the assembled attackers' current strength against
visible land defenders within two tiles of the target, including defensive
bonuses. Rome accepts attack strength as low as 80% of that visible local
strength, rather than requiring 110% of the opponent's worldwide power. Hidden
defenders remain unknown; the estimate is not a combat-odds calculation.
Production prioritizes replacement
attackers, the target's required siege and assault capacity after
immediate necessities, with a military-size cap. Troops and ships gather at
the selected port using normal safe paths and loading/grouping rules, preserving
source-city garrisons. Escorts are optional: planning and departure do not wait
for one, and campaign production does not force an escort before transports.
Loaded galley groups retain ordinary path, danger and landing checks. Single-member Roman teams prioritize Mathematics if a setup lacks it;
subsequent technologies are researched normally.
Existing wars and war plans retain normal execution and cancellation handling.
Standard war-plan preparation, combat, defense
and peace handling remain responsible for executing the campaign.

The ordinary Python war scheduler and single-member team random war selection
defer new early Roman attacks to this planner for up to 30 stalled planning
turns. After that, normal war selection is allowed while the campaign planner
can still start a ready expedition. A new campaign or an existing major war/plan
resets the counter. Expedition production, Mathematics priority and gathering
continue after fallback while the campaign remains viable; they stop when the
capital, stability, plague or financial checks fail, the civic/window ends, or
there is no eligible target. The counter and preparation state are saved with
the AI state. Teams with multiple
members retain ordinary team war selection. After AD 300 normal planning resumes;
civic effects do not expire on that date.

## Territorial setbacks and decline

With Roman Republic, Roma and at least two Italian cities intact, and stability
at least -40, barbarian-loss/city-count-halved collapse checks threaten one
peripheral city instead of the whole state. Disconnected cities are selected
first, then the most distant. Secessions are limited to one per ten turns,
use existing city/unit transfer routines and record a partial collapse event.
With no peripheral city, a viable Italian state survives that territorial check.
Severe civil war, instability below -40, or loss of the Italian base retain
ordinary full collapse. There is no scheduled destruction of Rome.

The morning 17 October batch preceding these logistics and planning changes
still had median peak Roman city count six, only 2/20 reaching eight cities,
and 10/20 surviving to AD 780. Effectiveness of the new changes remains
unmeasured until user-operated gameplay runs. Suggested
targets: 15/20 games reaching eight cities; 10/20 reaching ten and substantial
territory outside Italy; expansion into both Mediterranean halves; a major
Roman power through AD 200, followed by credible later fragmentation.

## Campaign blockers corrected after the ten-game batch

The batch ending `20261017-095434-49c2f5` prompted the following corrections:

- Naval route choice uses passable land/sea distances rather than land-area
  inequality. Roma and Qart-Hadasht share a land component, but the static land
  route takes 35 adjacent steps excluding peaks/water. North African targets
  can now select Mediterranean embarkation despite that shared component.
- Embarkation subtracts only the city-role defending group heads actually
  removed by the departing group. Ordinary attackers were already absent from
  the garrison count and must not be subtracted again.
- Preparation is separate from the 30-turn monopoly on new war selection.
  Releasing that monopoly no longer disables expedition production or research.
- The guarded Roman embarkation helper can load at its selected owned port
  despite a generic offensive/defensive/massing area designation. Other loading
  calls retain their original restrictions. A sufficiently loaded
  fleet invokes normal assault transport handling before generic land-war
  handling can unload it into its source port.

Across 709 living, city-owning Roman snapshots before AD 300, 622 (87.7%) had
fewer than two recorded siege units and 68 (9.6%) had stability below -10.
The target-scaled siege requirement remains for fortified or larger garrisons;
lightly defended visible targets need no siege. The route fixes preserve preparation support. The subsequent starting
Mathematics advantage and thin-garrison policy address early siege access and
release attackers without changing the collapse thresholds.

Recordings lack unit AI roles/positions, selected targets, garrison needs and
the fallback counter, so source-level defects cannot be assigned exact runtime
frequencies. Effectiveness of these corrections remains unverified pending a
user-operated batch. No gameplay runs were launched for this work.

## Sparse campaign readiness recording

Observer balance/diagnostics runs collect `roman_campaign_readiness` every five
engine turns while Rome has cities before AD 300, plus every observed new
campaign war plan. Ordinary gameplay and performance runs do not collect these
records. Native AI caches its actual decision in transient, unsaved fields;
the authenticated observer pulls it through `getRomanCampaignReadiness()` at
end turn and appends it directly to the observer's event stream. No callback
into RomanEmpire or module-global observer reference is required for delivery.

Records identify the first blocking gate, selected target/port, required and
available attackers/siege/cargo/escorts, strength estimates, stall counter,
stability and plague countdown. Early gates leave uncomputed fields at -1,
not zero. Overseas force counts refer to the selected port. Native evaluation
turn, cached reason, observer/performance flags and campaign-active state are
included. Missing current decisions explicitly report `not_evaluated` (or an
inactive native observer/performance state), with current decision fields -1.
An installed DLL lacking the getter raises an explicit observer recording
error rather than silently producing a batch without these diagnostics.

The first push-based hook produced no events in the batch ending
`20261017-110456-33dd90`. The following pull-based batch ending
`20261017-112101-8a92f8` delivered 150 fresh native prerequisite failures. Its
shared PythonErr.log reported that the DLL could not find RomanEmpire for
`canCampaign`, as well as GameObserver for labor recording. Calling
`moduleExists` directly on those helpers still failed in the batch ending
`20261017-113410-825f34` (149 explicit load failures). The DLL now calls the
engine-visible `EntryPoints/CvEventInterface.py`: `canRomanCampaign` imports
RomanEmpire through Python and `recordLaborEvaluation` imports GameObserver.
Both wrappers receive one `argsList` from the engine and unpack it before
calling their helpers. Separate positional parameters caused a labor recording
TypeError and would also pass a list instead of a player ID to canCampaign.
The existing event-manager entry points remain unchanged. Module availability
is checked for CvEventInterface, and the Roman call's success is checked
separately from its result; failures record
`prerequisite_module_load_failed`, `prerequisite_callback_failed`, or
`prerequisite_result_invalid` and do not permit an unchecked campaign.

`canCampaign` returns 1 for ready and distinct negative codes for ineligible
player (-2), stability (-3), plague (-4), capital (-5), and Italian occupation
(-6). Native readiness records use these actual reasons; the observer no
longer guesses the blocking gate from end-turn state. Prerequisite thresholds
and other balance rules are unchanged. This repairs a call that prevented
preparation from running. The labor callback also checks loading/call success
and logs an explicit failure if recording cannot be delivered.

Pull-based collection does not rerun campaign scoring or change RNGs. Its
runtime delivery is verified by the 150-event batch; successful prerequisite
callback delivery through the entry-point bridge still needs the next
user-operated run. Python parsing and the legacy build are static validation.

Records are in `turns.jsonl.gz`. Five-turn sampling can miss short-lived states
and does not measure exact blocked-turn exposure. Existing major wars/plans
are recorded as such and remain under normal execution handling.
