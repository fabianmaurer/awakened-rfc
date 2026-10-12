# RFC MP Plus — Gameplay guide

**English** | [Deutsch](../README.de.md)

A multiplayer-focused overhaul of **Rhye's and Fall Multiplayer** for
**Civilization IV: Beyond the Sword**. It adds a five-column civic system,
civic-combination stability, advance warnings of civilization spawns, and
country names that reflect the player's government and institutions.

This README describes the gameplay changes implemented in this fork. The
original RFC MP world maps, historical civilization spawns, unique powers,
victory goals, and other inherited systems form the underlying game.

## Gameplay overview

- **25 civics in five columns:** Government, Legitimacy, Labor, Military, and
  Religion replace the original six-column arrangement. The civic screen fills
  the available width and includes new civic artwork.
- **Democratic elections:** every ten turns, one other civic column changes to
  a randomly selected available alternative.
- **Starting civics:** every civilization receives a starting profile suited to
  its period, using civics available with its scenario or spawn technologies.
- **Civic-combination stability:** compatible institutions receive small bonuses;
  Theocracy with State Atheism incurs a small penalty. The total is bounded.
- **Spawn warnings:** tile tooltips identify pending civilizations whose core
  flip areas include that tile. Cities receive unrest three turns before a flip.
- **Dynamic country names:** English and German names respond to civic choices,
  religion, empire size, and existing vassal/colonial relationships.
- **Production consistency:** major civilizations no longer have their original
  civilization-specific unit and building production-cost multipliers.
- **Research consistency:** the additional per-civilization research-cost tuning
  was removed. Inherited scenario, timeline, and human/AI research pacing remains.
- **No inflation:** the inflation rate is fixed at zero rather than increasing
  automatically with time.
- **Cultural uprisings:** foreign cultural pressure causes population loss and
  barbarian rebels instead of directly transferring a non-barbarian city.

### Scope of civilization consistency

Major civilizations use shared base calculations for **city growth, Great Person
and Great General thresholds, culture accumulation, unit upkeep, city maintenance,
civic upkeep, and health**. Mali's individual economic-stability adjustment and
Turkey's individual revolt-probability discount are removed.

Shared civilization-group modifiers remain, including early-civilization scenario
adjustments, China/Japan's research discount, and regional and economic stability
rules. Unique units, buildings, powers, and historical spawn dates also continue
to distinguish civilizations. Minor-faction tuning remains separate.

## Technology-based growth

All civilizations have a **30% penalty to positive food surplus used for growth**,
reduced by **0.5 percentage points per distinct known technology**. It reaches
zero at 60 technologies and never becomes a bonus. Starting, acquired and traded
technologies count; repeatable technologies count only once. Knowledge is shared
at team level, as in the normal technology system.

| Known technologies | Growth penalty |
| --- | --- |
| 0 | 30% |
| 2 | 29% |
| 20 | 20% |
| 40 | 10% |
| 60+ | None |

For example, a surplus of four food with two known technologies adds **2.84 food**
toward growth each turn. Fractional progress is retained internally and saved;
the growth countdown and food bars use the adjusted rate. Hover the population
bar to see the current penalty and growth rate.

Food production, consumption, trade transfers, starvation and food used for
settlers/workers are unaffected. The penalty applies after trade and consumption,
so positive surplus from imported food is reduced too. Existing shared growth
threshold rules and granary retention remain in effect.

The settings `RFCMP_GROWTH_BASE_PENALTY_TIMES100` (3000) and
`RFCMP_GROWTH_TECH_REDUCTION_TIMES100` (50) in `Assets/XML/GlobalDefines.xml`
use hundredths of a percentage point. Existing saves begin with zero fractional
growth remainder and use the new rate immediately.

## Land reclamation

- **Flood-plain farms** require only Agriculture and the usual farm conditions.
  Farming preserves the flood plains; there is no additional technology or
  construction-time requirement for the feature.
- **Drain marsh** is available to workers and Indian Fast Workers from
  **Engineering**, within their team's territory. It converts marsh terrain
  into grassland, removes the mud feature and decorative swamp resource, and
  grants **no production**. Normal improvements can then be built separately.
- Drainage costs **1200 base work**, normally twelve turns for one standard
  worker before game-speed, scenario-era and worker-speed modifiers. AI and
  automated workers consider the reclaimed land's yields when choosing actions.

## Production conversions

| Conversion | Required technology | Efficiency |
| --- | --- | --- |
| Sale of goods | None; available from the beginning | 25% production into gold |
| Wealth | Currency | 50% production into gold |
| Research | Alphabet | 25% production into research |
| Culture | Music | 50% production into culture |

Currency replaces Sale of goods with Wealth. Cities already using or queuing
Sale of goods automatically switch to the stronger version, preserving other
queued orders. Rates are shared by all civilizations and players.

## Trade routes, military access and embargoes

Cities may select undiscovered cities as trade partners. When a route is
selected, the partner city's tile becomes revealed to the route owner's team.

- **Harbors can be built one land tile inland from an ocean coast**, including
  unique replacements such as the Cothon. Their existing food bonus applies to
  worked water tiles. This does not enable inland ship construction.
- Known cities can trade without roads or a Military access treaty. Normal
  route limits, war, city disorder, blockades and foreign-trade civic restrictions
  still apply. Infrastructure-free routes use **50% efficiency through distance 5**,
  declining linearly by five percentage points per additional tile to **0% at 15**.
  Routes at distance 15 or farther are unavailable without infrastructure. Distance
  uses Civ4's `plotDistance` metric, also used by the original trade-profit formula.
  Eligible routes retain a minimum of one commerce point. A continuous road,
  connection gives **100% efficiency without a range limit**. Water-assisted
  connections (sea or river, including mixed road/water paths) require **Sailing**
  and give 100% only within distance **12** until **Astronomy** removes the range
  limit. The existing terrain-navigation restrictions still apply.
  Cities on different landmasses require an actual navigable connection;
  infrastructure-free caravan routes cannot bypass these sea-trade restrictions.
  Water-assisted trade runs at **50% instead of 100%** unless both cities have
  a harbor (civilization-specific replacements count). This applies to river
  and mixed road/water connections too, but not to a continuous road-only path.
  Cities rank candidates by the exact route value before rounding, so an
  infrastructure-efficient route wins even when several routes would each round
  up to one displayed commerce point.
- **Military access** replaces the name Open Borders. It governs unit entry,
  including civilian units, independently of trade. The agreement remains
  reciprocal; one-sided agreements are not implemented yet.
- Every route exchanges **culture and religions in both directions**, including
  domestic routes. Each receiving city's population weakens the influence.
  Culture per route and direction is `floor(5 × route commerce / receiving population) / 10`:
  half the unrounded former rate, rounded down to one decimal place.
  religion spread is `floor(2.5 × route commerce / receiving population)` percent
  per religion present in the partner city, capped at **12%** per route.
  The receiving city's owner-culture share adds a linear penalty: zero at
  **75%**, rising to the full **12 percentage points at 100%**, which blocks
  trade spread entirely. The share uses stored city culture before that route's
  cultural exchange. A holy city subtracts another **3 percentage points** for
  religions for which it is not holy; multiple holy religions do not stack this
  penalty. Final chances are rounded down and cannot fall below zero. These
  penalties affect trade spread only, not missionaries.
  Culture below **0.1** per route/direction is discarded; tenths accumulate in
  city culture. City-tile culture gains whole points as city culture crosses
  whole-point thresholds. Religion chances still discard fractions below one
  percentage point. Culture is
  credited to the partner city's owner in the receiving city and its city tile.
  State Atheism blocks religious exchange; other religious-spread restrictions
  remain respected. Separately allocated reciprocal routes each contribute.
  This replaces the old passive religion-spread mechanic. Missionaries and
  historical founding rules remain; State Atheism continues to block missionary
  spread and prevents both sending and receiving religions through trade.
- Example before cultural and holy-city resistance: a six-commerce route into a size-two city produces **1.5 culture per
  turn** and a **7% spread chance** for each eligible partner religion. The same
  route into a size-ten city gives 0.3 culture and a 1% religion chance.
- From **Currency**, select a civilization on the Foreign Advisor's Relations
  page to **impose or lift a trade embargo**. It immediately blocks routes
  between both civilizations, remains saved, and leaves military access intact.
  Each side controls its own embargo: both must lift theirs to restore trade.
  The existing diplomatic request to stop trading also imposes a route embargo;
  that request retains its inherited cancellation of other agreements.

Route tooltips show infrastructure efficiency and cultural contributions.
Tuning values are in `Assets/XML/GlobalDefines.xml` (`RFCMP_*TRADE*`). Embargo
actions use synchronized network messages; religious spread uses game RNG.

### Food transfers

Actual trade routes also move food from the poorer city to the wealthier one,
including domestic routes. Wealth is **local commerce yield per population point
after modifiers, excluding trade-route commerce**; gold from specialists or the tax slider does
not determine direction. Equal wealth means no transfer.

- Requested food is `route commerce / 2 × (richer wealth per capita − poorer wealth per capita) / richer wealth per capita`.
  Small wealth differences weaken the transfer; a large difference approaches
  one food per two route-commerce points. For reciprocal routes, use the stronger
  request once rather than counting the city pair twice.
- A supplier's combined exports are capped at **one food per population point**.
  Exports need not come from
  surplus: supplying cities can grow more slowly or starve. Size-one cities may
  export only their local surplus after consumption and health costs.
- When requests exceed capacity, destinations receive proportional shares.
  Total food is rounded down to whole points, with the remaining whole points
  assigned to the largest fractional shares; ties use deterministic city/route
  order. Small requests may yield no food.
- All allocations are computed together once per game turn before player turns,
  then saved. A falling supplier cap reduces commitments during the round.
  Destroyed/captured cities, lost routes, disorder, blockades, war and embargoes
  invalidate affected transfers immediately. Freed capacity is redistributed
  at the next allocation, not mid-turn.
- Food is deducted from the supplier and added to the recipient **after yield
  modifiers**. Imports are not multiplied by food bonuses and cannot be exported
  again. They affect ordinary growth, starvation, and food-based unit production.
  Routes inherit the existing infrastructure, Sailing, Astronomy and harbor rules.
- Hover the population bar for total imports/exports, or a trade route for the
  signed food exchange with that partner. Positive means import, negative export.
  Existing saves start receiving allocations at the next game turn.

Example: a size-four city can export at most four food. If
destinations request four, two and two, they receive two, one and one. Losing
the routes restores the supplier's food but removes the recipients' imports.

Net unhappiness and unhealthiness create migration pressure, increasing a
supplier's route demand by up to 100%. Each net unhappy citizen adds twice the
pressure of one net unhealthy citizen. Surplus happiness and health counter that
pressure at lower strength: one surplus happiness cancels one pressure point,
while one surplus health cancels half a point. The population export cap still
applies.

The `RFCMP_FOOD_EXPORT_PER_POPULATION`, `RFCMP_TRADE_FOOD_COMMERCE_DIVISOR`,
and `RFCMP_FOOD_TRADE_MIGRATION_*` settings in `Assets/XML/GlobalDefines.xml`
control the population cap, route capacity, and migration pressure. The
technology-based growth penalty affects positive surplus after these transfers;
it does not reduce food production or transferred amounts.


## New civics

Each column allows one active civic. Bonuses from different columns combine;
for example, Dictatorship and Nationalism together provide +40% production.

**Commerce** means the economic yield allocated through the sliders to gold,
research, culture, and espionage. It is distinct from gold income and from
trade-route income. Percentage bonuses are modifiers, not percentage-point
changes to slider settings. Flat building and improvement bonuses apply to
each qualifying building or worked improvement.

### Government

| Civic | Required technology | Upkeep | Effects |
| --- | --- | --- | --- |
| **Tribal System** | None | None | +20% production for all units; -20% research; +100% distance and number-of-cities maintenance. |
| **Monarchy** | Monarchy | Medium | +25% production for world, team, and national wonders. Enables inheritance events. |
| **Republic** | Code of Laws | Low | +50% great person birth rate. |
| **Dictatorship** | Fascism | High | +20% production; no war weariness; -2 happiness in every city. |
| **Democracy** | Democracy | High | +2 happiness in every city; elections every ten turns randomly change one other civic column. |

### Legitimacy

| Civic | Required technology | Upkeep | Effects |
| --- | --- | --- | --- |
| **Despotism** | None | None | +1 happiness from palaces and monuments, including their civilization-specific replacements. |
| **Theocracy** | Divine Right | High | +1 happiness per building of the state religion; -2 happiness per building of another religion; +10% combat strength for all units. |
| **Plutocracy** | Banking | Low | +25% gold income; +50% commerce from trade routes. |
| **Nationalism** | Nationalism | Medium | +5 culture in every city; +20% production; -5 happiness in cities where another player's culture exceeds the owner's culture on the city tile. |
| **Rule of Law** | Constitution | High | +2 happiness in every city; +10% commerce yield. |

### Labor

| Civic | Required technology | Upkeep | Effects |
| --- | --- | --- | --- |
| **Self-sufficiency** | None | None | +2 health in every city; cottage improvements do not grow; assigned specialists are blocked and existing assignments removed; free specialists remain. |
| **Slavery** | Bronze Working | Low | May sacrifice population to rush production; +2 commerce from plantations. |
| **Serfdom** | Feudalism | Low | +1 food from farms; -1 commerce from villages; workers build improvements 50% faster. |
| **Planned Economy** | Communism | High | +1 production from workshops, watermills, and windmills; +1 food from farms; -20% commerce yield. |
| **Market Economy** | Economics | Medium | +1 free specialist in every city; cottage improvements grow twice as fast. |

Improvement growth includes every upgrade stage: **Cottage → Hamlet → Village →
Town**. Self-sufficiency stops upgrades; Market Economy doubles their rate.
Serfdom's commerce penalty specifically affects the **Village** stage. Normal
idle citizens remain available under Self-sufficiency as a population fallback.

### Military

| Civic | Required technology | Upkeep | Effects |
| --- | --- | --- | --- |
| **Warrior Society** | None | None | Melee units start with +2 experience; siege units have -20% combat strength. |
| **Militia** | Archery | Low | +30% city defense; -10% combat strength outside the unit owner's territory. |
| **Knighthood** | Engineering | Medium | +25% production for mounted units; +10% city attack. |
| **Professional Army** | Military Tradition | High | Units start with +5 experience. |
| **Conscription** | Military Science | Medium | +25% production for all units. |

Tribal System and Conscription's production bonuses include workers, settlers,
and missionaries. Conscription's name does not grant an additional drafting
ability; its implemented effect is the production bonus listed above.

### Religion

| Civic | Required technology | Upkeep | Effects |
| --- | --- | --- | --- |
| **Ancestor Cult** | None | None | +1 culture from monuments, including civilization-specific replacements. |
| **State Religion** | Priesthood | Low | +1 happiness in cities with the state religion; +100% production for missionaries of any religion. |
| **Holy State** | Theology | High | +2 happiness and +10% production in cities with the state religion; -2 happiness in cities without it. |
| **Tolerance** | Liberalism | Medium | Removes unhappiness caused by foreign religions. |
| **State Atheism** | Scientific Method | High | +10% research; religious buildings have no effects; religions cannot spread in your cities. |


State Atheism disables a state religion; the other four Religion civics allow one.

Under State Atheism, religious buildings remain owned and retain their place in
wonder limits, but their effects are disabled, including happiness, production,
commerce, obsolete-safe culture, shrine income, free specialists, and great
person generation. Their effects are restored when leaving the civic. Religious
buildings are identified by their religion or religion prerequisite.

Atheism blocks natural, missionary, event, and scripted religion spread. Existing
religions remain, including after city ownership changes. Founding or relocating
a holy city is preserved as a separate action.

## Starting civics

Every playable civilization, including Byzantium in the 600 AD scenario, has a
profile for all five civic columns. Profiles apply to human and AI players at
scenario initialization or their initial spawn, after starting technologies and
before scripted starting units. Unavailable civics use explicit fallbacks;
no extra technologies or anarchy are introduced.

Profiles cover all three scenarios and do not override subsequent player choices.
Existing civilizations in saved games keep their current civics. See
[StartingCivics.md](StartingCivics.md) for all profiles and fallback rules.

## Democratic elections

Elections occur on **global turn multiples of ten**, while Democracy is active.
They select one of the other four columns that has an available alternative,
then select a different civic that the player can currently adopt. If no column
has an available alternative, there is no change. Human players receive a
notification of the result.

The game uses its synchronized random generator for both selections. The
government remains Democracy, and elections have no additional transition
stability penalty.

## Civic stability

### Dynastic inheritance

When a monarchy with a state religion collapses, it has a **50%** chance to be
inherited instead of fragmenting. An heir must be a living monarchy with the
same state religion, at least **0 stability**, and at least one city on the
continent of the collapsing monarchy's capital. One eligible heir is selected
deterministically; there is no size requirement. The heir receives every city
and unit of the collapsed realm. If no heir qualifies or the chance fails, the
normal collapse rules apply.

The following combinations contribute to base stability:

| Combination | Stability |
| --- | ---: |
| Tribal System + Despotism | +1 |
| Monarchy + Theocracy | +1 |
| Plutocracy + Planned Economy | -1 |
| Republic or Democracy + Rule of Law | +2 |
| Monarchy + Knighthood | +2 |
| Theocracy in Legitimacy + State Religion or Holy State in Religion | +2 |
| Plutocracy + Market Economy | +1 |
| Theocracy in Legitimacy + State Atheism | -3 |

Matching contributions add together, with an overall limit of **-5 to +5**.
Other combinations contribute zero. This is a base-stability modifier recalculated
every three turns, not a permanent gain or loss accumulated every turn.
Actual happiness and economic performance continue to affect stability through
the existing general systems.

The overhaul removes:

- Fixed stability values assigned to individual civics.
- Automatic government-specific stability rescue and threshold bonuses.
- The “outdated civics” penalty and Democracy's old transition instability.
- Market Economy's special depression mechanic and contagion through open borders.
- The eight-turn crisis after leaving Planned Economy.
- Extra religious-city penalties specific to State Religion and Holy State.
- Nationalism's separate foreign-culture stability threshold.
- The extra jail-construction stability bonus specific to Dictatorship.
- Civic bonuses from the removed Expansion column for vassals, distant cities,
  conquest, and trade/economy.

See [CivicStability.md](CivicStability.md) for the reasoning and save-game
behavior, and [CivicEffects.md](CivicEffects.md) for implementation details.

## Civilization spawns and flips

### Tile tooltips

Hovering over a tile shows the **base country names** of pending civilizations
whose core flip areas include it. Each name appears on its own line in that
civilization's color. Your own civilization and civilizations currently alive
are excluded. The labels use names such as **Germany**, rather than an early
dynamic name such as “Germanic Peoples.”

The tooltip uses fixed core-area rectangles and a birth-turn cutoff. It does not
recalculate every scripted exception or adjusted spawn delay, so it is an aid
to planning rather than a complete prediction of every possible flip.

### Pre-flip unrest

**Three turns before a scheduled initial flip**, cities in the spawning
civilization's core area and exception tiles receive three turns of unrest,
using the city's occupation timer. An existing longer occupation is preserved.
The schedule accounts for the spawn/flip delays used by the birth logic.

Affected human owners receive a message using the civilization's early dynamic
name, for example **“The [people] are rising up!”** This warning accompanies the inherited flip
system; it does not introduce a separate unit-flipping rule.

## Cultural uprisings

Successful cultural revolts in regular civilizations' cities now cause an uprising instead
of an automatic change of owner. The existing cultural-pressure and garrison
checks determine whether it occurs. Historical civilization-spawn flips remain
separate, as does the existing cultural flipping of barbarian and independent cities.

All cultural revolts and flips require one foreign civilization to hold **more
than 50% of the city tile's total culture**. A plurality or exactly 50% is not
enough. Independent and barbarian cities no longer bypass the garrison check or
receive their former increased revolt-test probability; garrison revolt protection
can reduce that probability to zero. Independent cities still need one warning
revolt before a later successful revolt can flip them, subject to game options.
Barbarian cities may flip on their first successful revolt. Historical spawn
flips are separate and do not use these cultural-revolt rules.

- The city loses **25% of its population, rounded up**, but remains at least size 1.
- The rebellious civilization's culture in the city and on the city tile decreases
  proportionally to the population lost. Other civilizations' culture is preserved.
  In a size-one city, rebellious culture decreases by 25% without population loss.
- **Two barbarian units per lost population point** appear on adjacent, passable
  land tiles without cities or non-barbarian units. They are distributed across
  eligible tiles and may stack. If no eligible tile exists, no units appear.
- Rebels use the strongest standard melee, archer, or gunpowder infantry type
  unlocked by the owner's technologies; strategic resources are not required.
- The city enters unrest using the base revolt occupation duration. Its garrison
  is not automatically damaged by this uprising.

Size-one cities spawn no rebels. The No Barbarians option suppresses rebel units,
while the population, culture, and unrest effects still apply. The owner receives
a message with the actual losses and number of spawned rebels. Barbarians can later
capture the city through combat; cultural pressure cannot directly transfer it.

The culture reduction normally lowers the foreign share, but a city with no
other culture can remain entirely foreign in percentage terms. Culture on nearby
tiles and existing units is not erased. The mechanism uses shared game state
and fixed unit/tile iteration order; multiplayer runtime validation is pending.

## Relocating conquered cities

The conquest popup offers **Relocate (receive a settler)** when more than **25%**
of the captured city's stored culture belongs to your team. This is city culture,
not tile culture; the comparison uses its unrounded stored value. Exactly 25%
does not qualify. The option is available only during the turn of acquisition.

Relocation removes the city and all its buildings and grants one settler of your
civilization on that tile, with no remaining movement for the turn. Normal
territory rules can move it to a valid tile when removal changes ownership.
Other units and tile culture follow the normal city-removal rules. This uses
city disbanding rather than the razing-specific diplomatic and event penalties.
Keeping, razing (where permitted), gifting and inspecting retain their usual options.

Eligible population-one cities receive the choice rather than automatically
being razed. No City Razing, One City Challenge and city-elimination modes
retain their restrictions. AI capture decisions are unchanged. Relocation uses
the existing synchronized city-task network message and rechecks eligibility
when executed; no new saved state or task-index changes are introduced.

## Production rushes

- **Slavery** can sacrifice population to finish any production.
- **Serfdom** can sacrifice population to finish units, but cannot use this rush
  for buildings or projects.
- With **Banking**, gold can immediately finish a unit. The completed unit is a
  **mercenary**: it starts with one to three valid random promotions, cannot
  gain experience or further promotions, and cannot upgrade.
  Mercenaries do not consume free-unit or free-military-unit allowances. Each
  pays its regular unit cost plus a 100% surcharge, before difficulty modifiers.
- With **Corporation**, gold can also finish buildings.
- **Conscription** sends surplus food into production while training military
  units. Food is therefore not stored for city growth during that production.

All mercenary random choices use Civ4's synchronized game RNG and are made while
the gold-rush command completes, so no additional persistent city state is used.

## Dynamic country names

Country names reflect government, legitimacy, economy, state religion, and
empire size. Existing vassal and colonial naming takes priority. Names refresh
after civic/religion changes and once per player turn.

The catalogue contains **569 entries covering 358 distinct English/German name
pairs**. Names are written individually, using historical identities where
appropriate and plausible alternate-history names elsewhere. A name need not
encode every active civic.

Examples include the **Holy Roman Empire**, **Hanseatic League**, **Commonwealth
of England**, **Batavian Republic**, **Novgorod Republic**, **North Sea Empire**,
**Celestial Empire**, **Heavenly Kingdom of Great Peace**, **Land of the Four
Quarters**, **Regno d'Italia**, **Nile League**, and **Union of Bharat**. Different civic
combinations can intentionally share the same natural country name.

See [CountryNames.csv](CountryNames.csv) for the catalogue and
[CountryNaming.md](CountryNaming.md) for selection rules. English and German
names are provided; French, Italian, and Spanish use English fallbacks for the
new country-name entries.

## Installation and multiplayer

1. Copy the **`RFC MP Plus`** folder into Beyond the Sword's **`Mods`** directory.
2. Keep that folder name: the included scenario files reference it. The original
   RFC MP mod can remain installed alongside this fork.
3. Load RFC MP Plus from the game's mod menu, or use
   [Launch RFC MP Plus.bat](<../Launch RFC MP Plus.bat>). The launcher currently
   points to the standard Steam installation path; adjust it for other locations.
4. Choose an included scenario: **3000 BC**, **800 BC**, or **600 AD**.

All multiplayer peers need the same mod assets, Python files, XML, and DLL.
Gameplay code uses synchronized game state and election randomness; multiplayer
runtime validation of the overhaul is still pending.

After text changes, hold **Shift while launching** to rebuild the text cache.

Start a new game when adopting changes to XML civic modifiers, since old saves
can retain cached player/city bonuses. The new stability combinations take effect
at the next base-stability recalculation in an existing save. Removed crisis
countdown fields remain readable but no longer impose penalties; past stability
changes are not retroactively rewritten.

## Building the game DLL

Use the original **32-bit VC7.1 toolchain**, Python 2.4, and Boost.Python 1.32
for compatibility with Civ4's runtime.

See [AGENTS.md](../AGENTS.md) and [BUILDING.md](<../RFC MP Plus/CvGameCoreDLL/BUILDING.md>)
for prerequisites and the compilation routine. The configured build copies the
rebuilt DLL into the workspace mod and the installed mod folder. Close Civ4
before rebuilding so the installed DLL can be replaced.
