# RFC MP Plus

**English** | [Deutsch](README.de.md)

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
| **Monarchy** | Monarchy | Medium | +25% production for world, team, and national wonders. |
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
| **Warrior Society** | None | None | Units start with +2 experience; siege units have -20% combat strength. |
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
[StartingCivics.md](docs/StartingCivics.md) for all profiles and fallback rules.

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

See [CivicStability.md](docs/CivicStability.md) for the reasoning and save-game
behavior, and [CivicEffects.md](docs/CivicEffects.md) for implementation details.

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

## Dynamic country names

Country names reflect government, legitimacy, economy, state religion, and
empire size. Existing vassal and colonial naming takes priority. Names refresh
after civic/religion changes and once per player turn.

The catalogue contains **569 entries covering 356 distinct English/German name
pairs**. Names are written individually, using historical identities where
appropriate and plausible alternate-history names elsewhere. A name need not
encode every active civic.

Examples include the **Holy Roman Empire**, **Hanseatic League**, **Commonwealth
of England**, **Batavian Republic**, **Novgorod Republic**, **North Sea Empire**,
**Celestial Empire**, **Heavenly Kingdom of Great Peace**, **Land of the Four
Quarters**, **Regno d'Italia**, **Tawantinsuyu**, **Nile League**, and **Union of Bharat**. Different civic
combinations can intentionally share the same natural country name.

See [CountryNames.csv](docs/CountryNames.csv) for the catalogue and
[CountryNaming.md](docs/CountryNaming.md) for selection rules. English and German
names are provided; French, Italian, and Spanish use English fallbacks for the
new country-name entries.

## Installation and multiplayer

1. Copy the **`RFC MP Plus`** folder into Beyond the Sword's **`Mods`** directory.
2. Keep that folder name: the included scenario files reference it. The original
   RFC MP mod can remain installed alongside this fork.
3. Load RFC MP Plus from the game's mod menu, or use
   [Launch RFC MP Plus.bat](<Launch RFC MP Plus.bat>). The launcher currently
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

See [AGENTS.md](AGENTS.md) and [BUILDING.md](<RFC MP Plus/CvGameCoreDLL/BUILDING.md>)
for prerequisites and the compilation routine. The configured build copies the
rebuilt DLL into the workspace mod and the installed mod folder. Close Civ4
before rebuilding so the installed DLL can be replaced.
