# Slave specialist AI audit

Investigation dated 2026-10-16, using the completed 20-game balance batch
`balance-ai-3000bc-20games-200turns-seeds-1-20-20261016-220415-a00844`.
The findings below are from source inspection and existing recordings, not a new
game test. Subsequent AI corrections are documented in the implementation section.

## Observed civic choices

The batch records 356 living major-civilization turns under Slavery, and no slave
specialists. Eight civilizations start with Slavery in each of the twenty games.
All 160 such starting spells end in Self-Sufficiency:

| Duration before leaving Slavery | Starting spells |
| --- | ---: |
| 2 turns | 153 |
| 3 turns | 2 |
| 4 turns | 3 |
| 5 turns | 2 |

These starting spells account for 334 civilization-turns. The remaining 22 are
China in seed 13, engine turns 163–184; China loses its remaining cities in turn
185. Thus long-term adoption is almost absent, independently of citizen assignment.

During Slavery the recordings contain 541 city-turns: 202 with a reported food
surplus of at least two, 38 with a negative surplus, and 152 with positive imports.
These observations overlap and include startup/disorder periods. The balance
records do not include the workable-tile alternatives or the city's disorder flag,
so these counts do not establish that assigning a slave was economically optimal.
They do rule out treating all these recorded states as food-deficit states.

## Civic evaluation undervalues the actual option

`CvCity::isSpecialistValid` permits unlimited assigned slaves under `CIVIC_SLAVERY`.
The specialist yields are -1 food and +3 production, in addition to the ordinary
population food consumption; it replaces a worked tile or another assigned job.

`CvPlayerAI::AI_civicValue` values specialist permissions only through its generic
small constant, roughly `(number of cities + 6) / 2` per unlocked specialist
outside the culture strategy. It does not estimate the usable slave jobs, their
net food/production tradeoff, or imported food that could support them.
Self-Sufficiency has no civic upkeep and +2 health, both recognized by the civic
evaluation. Slavery has low upkeep and no health bonus. This is consistent with
the observed rapid switches, but recordings do not contain the numerical civic
scores required to reconstruct each individual choice.

## Negative food is penalized even with ample imports

`CvCityAI::AI_yieldValue` uses
`min(iFoodGrowthValue, iMaxFoodValue * aiYields[YIELD_FOOD])`, with a normal
`iMaxFoodValue` of 44. A slave's -1 food therefore gets a growth component of at
most -44 even when growth is avoided or an existing food surplus makes the loss
cheap. This expression caps positive food value but becomes a lower bound on the
magnitude of a negative-food penalty.

With ordinary 100% multipliers, no starvation and no production emphasis, the
best-case arithmetic is approximately +45 for production, -44 for the food-growth
component and -1 for the small food preference: zero. Other branches may lower
it further. Production bonuses/emphasis can change that result. Slaves have no
great-person output to compensate. This is a concrete evaluation defect, rather
than evidence that the specialist itself is too weak.

## Trade food is included in some paths and omitted in another

- `CvCity::foodDifference` uses local modified food + imports - exports - consumption.
- `CvCity::getYieldRate(YIELD_FOOD)` includes imports minus exports after local modifiers.
- `CvCityAI::AI_yieldValue` obtains its current surplus from `foodDifference(false)`;
  its adjusted-food expression also calls `getYieldRate(YIELD_FOOD)`. These paths
  include current shipments. They do not predict a new trade allocation after
  changing jobs.
- `CvCityAI::AI_foodAvailable`, called by `AI_ignoreGrowth`, instead sums the actual
  city-center yield, the best available food tiles and free-specialist XML food.
  It does not apply local food yield modifiers or add net trade food. An importing
  city can consequently be classified as unable to support additional population
  even when current imports would support it; an exporting city can be overestimated.
  This gate affects growth valuation and is not itself a blanket specialist ban.

The city-center calculation reads the actual plot yield. `CvPlot::calculateYield`
retains terrain/feature yields and adds production/commerce for a city, without
a guaranteed two-food floor. No hardcoded two-food assumption was found in these
citizen-evaluation paths. Removing the floor can make real food constraints tighter,
but does not by itself explain the observed universal starting civic switches.

## Follow-up implementation priorities

1. Make negative-food job valuation reflect the marginal cost at the actual food
   surplus, while preserving starvation protection and add/remove consistency.
2. Include local modifiers and current net shipments in the food-availability
   estimate, without multiplying imported food or promising unchanged future imports.
3. Evaluate feasible slave employment when considering Slavery, including the
   displaced job, ordinary consumption, the specialist's extra food cost, and
   the lost health benefit of the current civic. Avoid a blanket civic preference.

Runtime and multiplayer validation remain outstanding. No new simulations were run.

## Implemented corrections

- `AI_yieldValue` caps the magnitude of negative food's growth value, rather than
  imposing the maximum food price in surplus. A separate marginal starvation
  penalty catches negative-food jobs that create or deepen a deficit; its
  without-job/with-job comparison is the same for additions and removals.
- `AI_foodAvailable` retains non-plot food, uses player-specific free-specialist
  yields and applies local food modifiers before adding current imports minus
  exports. Its hypothetical plot workers no longer receive Republic's current
  assigned-specialist consumption discount.
- `AI_slaveryEmploymentValue` replaces the generic slave-permission bonus in
  `AI_civicValue`. It considers currently worked plots and assigned specialists,
  their existing AI scores, exact local food rounding, current shipments and
  changes in health consumption from the candidate labor civic. It evaluates
  successive profitable replacements with a cumulative food budget and keeps
  two surplus food when growth is desired (zero when growth is avoided).
- Existing assigned slaves are first given distinct alternative unworked plots
  or generic citizen jobs for this estimate. This prevents treating all benefit
  as adoption-only and losing it immediately when deciding whether to retain
  Slavery. Hypothetical assignments are local data; no city, civic, RNG or trade
  state is changed during civic scoring.
- Recurring employment advantages are converted from citizen scores to civic
  scores at 250:1 (about six civic points per additional production before other
  yield tradeoffs). Health and civic upkeep continue to receive their ordinary
  evaluation; there is no unconditional preference for Slavery.

This remains a heuristic, not a complete counterfactual city optimizer. It does
not forecast future routes, population, alternative building specialists for
every existing slave, candidate changes in other civic columns, or revolt risk.
It uses present trade allocations; future shipments can change after assigning
workers. Those limitations and actual adoption/specialist usage need evaluation
in a subsequent user-operated balance batch. No balance improvement is claimed
from compilation alone.
