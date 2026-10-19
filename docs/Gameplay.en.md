# Awakened RFC — Gameplay guide

**English** | [Deutsch](../README.de.md)

A multiplayer-focused overhaul of **Rhye's and Fall Multiplayer** for
**Civilization IV: Beyond the Sword**. It adds a five-column civic system,
civic-combination stability, advance warnings of civilization spawns, and
country names that reflect the player's government and institutions.

This README describes the gameplay changes implemented in this fork. The
original RFC MP world maps, historical civilization spawns, unique powers,
victory goals, and other inherited systems form the underlying game.

## Historical wonder requirements

These additional requirements apply equally to human players and AI. Regions refer to the RFC Earth map and do not depend on civilization or ownership. Existing technology, resource and building requirements still apply. Religion must be present in the city; it need not be the state religion. Civic requirements also apply to queued construction; completed wonders retain their effects after civic changes.

| Wonder | Additional requirement |
| --- | --- |
| Great Lighthouse, Colossus | Mediterranean coast |
| Parthenon, Temple of Artemis, Statue of Zeus, Mausoleum of Maussollos | Mediterranean region |
| Temple of Kukulkan (Chichen Itza) | Mesoamerica (Mexico / Central America) |
| Great Wall | East Asia |
| Moai Statues | Pacific coast or Pacific island |
| Pyramids | At least one desert tile in the city radius, including the city tile |
| Hanging Gardens | City on a river |
| Shwedagon Paya | Buddhism in the city |
| Angkor Wat | Hinduism in the city |
| Hagia Sophia, Sistine Chapel, Notre Dame, Cristo Redentor | Christianity in the city |
| Spiral Minaret, University of Sankore, Taj Mahal | Islam in the city |
| Versailles | Monarchy during construction |
| Statue of Liberty | Coastal city; Republic or Democracy during construction |
| Kremlin | Capital |
| Great Library | Library in the city |
| Pentagon | Barracks in the city |
| Wembley | Colosseum in the city |
| Graceland, Hollywood | Theatre in the city |

## Gameplay overview

- **25 civics in five columns:** Government, Legitimacy, Labor, Military, and
  Religion replace the original six-column arrangement. The civic screen fills
  the available width and includes new civic artwork.
- **Democratic elections:** every ten turns, one other civic column changes to
  a randomly selected available alternative.
- **Starting civics:** every civilization receives a starting profile suited to
  its period, using civics available with its scenario or spawn technologies.
- **Civic-combination stability:** compatible institutions receive small bonuses;
  Theocracy with Tolerance incurs a small penalty. The total is bounded.
- **Spawn warnings:** tile tooltips identify pending civilizations whose core
  flip areas or additional exception tiles include that tile. Cities receive
  unrest from the civilization's appearance until the flip.
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

Named unique powers apply independently of the shared cost baseline. China's
melee and gunpowder units train at **1.5x speed**; Maya have **40% lower research
costs through the Medieval era**; Persia gains **+2 stability per conquered city**.

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

The settings Producing settlers, workers or other food-production units does not prevent
starvation: food deficits consume stored food and can reduce population when
stores run out. Only a positive surplus is converted into production.

`RFCMP_GROWTH_BASE_PENALTY_TIMES100` (3000) and
`RFCMP_GROWTH_TECH_REDUCTION_TIMES100` (50) in `Assets/XML/GlobalDefines.xml`
use hundredths of a percentage point. Existing saves begin with zero fractional
growth remainder and use the new rate immediately.

## Land reclamation

- **Oases** yield **2 food and 2 commerce** and allow only **farms**, available
  with Agriculture. Farming preserves the oasis and its fresh water, normally
  yielding **3 food and 2 commerce**, or **4 food and 2 commerce** with Biology.
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
  and give 100% within distance **12**, or **20** when the originating city has a harbor, until **Astronomy** removes the range limit. The existing terrain-navigation restrictions still apply.
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
  The AI proposes it only when access opens a known route or saves at least
  three tiles: a land connection from its capital to another friendly city or
  a current/planned enemy city, or a route to an existing unit-group mission
  near the partner's border (including civilian and naval missions). This is
  a geographic estimate, not a full unit movement simulation. Trade income
  gives the treaty no value; normal diplomatic refusal rules still apply.
- Every route exchanges **culture and religions in both directions**, including
  domestic routes. Each receiving city's population weakens the influence.
  Culture per route and direction is `floor(5 × route commerce / receiving population) / 10`:
  half the unrounded former rate, rounded down to one decimal place.
  religion spread is `floor(5 × route commerce at full infrastructure efficiency / receiving population)` percent
  per religion present in the partner city, capped at **12%** per route before penalties and bonuses.
  The receiving city's owner-culture share adds a linear penalty: zero at
  **75%**, rising to the full **12 percentage points at 100%**, which reduces
  the base trade spread chance to zero before additive bonuses. The share uses stored city culture before that route's
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
  turn** and a **12% spread chance** for each eligible partner religion. The same
  route into a size-ten city gives 0.3 culture and a 3% religion chance.
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

Food flows along actual trade routes toward the city with the stronger combined attraction. The comparison uses local commerce per population point after modifiers, excluding trade-route commerce, plus wellbeing per population point. Wellbeing is happiness minus unhappiness plus half the net health (good health minus bad health). Gold from specialists or the tax slider does not determine direction.

- Wealth inequality contributes up to **100 pressure points**. Wellbeing inequality remains capped at **50 pressure points**: happiness differences can supply the full 50, while health differences supply at most 25. The signed pressures are added before the food-flow direction and amount are chosen. A healthy, happy new city can therefore attract food despite a modest wealth disadvantage; wellbeing cannot overcome a large wealth gap by itself.
- Base food demand is `ceil(absolute combined pressure / 10) + max(0, route commerce - 1)`, multiplied by infrastructure efficiency. Routes at 0% efficiency cannot be established or transfer food. For reciprocal routes, use the stronger request once rather than counting the city pair twice.
- Route selection values the expected food import or export as one commerce per food, alongside the route's ordinary commerce. The estimate does not reserve a supplier's food: the shared export cap is still applied after all routes have been selected.
- A supplier's combined exports are capped at **one food per population point**. Exports need not come from surplus: supplying cities can grow more slowly or starve. Size-one cities may export only their local surplus after consumption and health costs.
- When requests exceed capacity, destinations receive proportional shares. Total food is rounded down to whole points, with the remaining whole points assigned to the largest fractional shares; ties use deterministic city/route order. Small requests may yield no food.
- All allocations are computed together once per game turn before player turns, then saved. Before either endpoint processes growth, the shipment is checked against current routes, disruption and export capacity. Its final amount is then locked identically at both ends: a later population/cap change or disruption cannot erase only the debit or only the credit. Already booked shipments finish their matching accounting, even if a city enters disorder; later allocations reflect the disruption. Freed capacity is redistributed at the next allocation, not mid-turn.
- Food is deducted from the supplier and added to the recipient **after yield modifiers**. Imports are not multiplied by food bonuses and cannot be exported again. They affect ordinary growth, starvation, and food-based unit production. Routes inherit the existing infrastructure, Sailing, Astronomy and harbor rules.
- Hover the population bar for total imports/exports, or a trade route for the signed food exchange with that partner. Positive means import, negative export. Existing saves start receiving allocations at the next game turn.

Example: a size-four city can export at most four food. If destinations request four, two and two, they receive two, one and one. Routes lost before booking cancel both sides. Routes lost after booking stop future shipments once the current shipment has been accounted for at both ends.

Infrastructure connectivity is evaluated when shipments are allocated. A road
destroyed later in the turn affects the next allocation; an existing shipment
can still be booked if its selected trade route remains present. Diplomacy,
embargoes, city disruption and the supplier's export cap are still checked
before booking.

The `RFCMP_FOOD_EXPORT_PER_POPULATION` and `RFCMP_TRADE_FOOD_PRESSURE_PER_FOOD` settings in `Assets/XML/GlobalDefines.xml` control the population cap and base transfer amount. The technology-based growth penalty affects positive surplus after these transfers; it does not reduce food production or transferred amounts.

## New civics

Stationed military units provide **+1 happiness per two units**, rounded down, up to **+3 happiness at six units**. This applies under every civic and appears in the city's military presence happiness breakdown.

City tiles retain their natural terrain, hill, river, feature and revealed resource yields, then gain **+1 production and +1 commerce**. There is no minimum food yield: a bare desert city tile produces no food. Founding a city preserves flood plains and their natural yields. This applies to all city tiles; previously removed flood plains are not restored in existing saves.

Each column allows one active civic. Bonuses from different columns combine;
for example, Dictatorship and Nationalism together provide +40% production.

**Commerce** means the economic yield allocated through the sliders to gold,
research, culture, and espionage. It is distinct from gold income and from
trade-route income. Percentage bonuses are modifiers, not percentage-point
changes to slider settings. Flat building and improvement bonuses apply to
each qualifying building or worked improvement.

### Government

For Egypt, Tribal System is called **Pharaonic Kingship** and Despotism is
called **Divine Kingship**, in every era. Pharaonic Kingship grants +1 production
from farms and per slave specialist, with medium civic upkeep. It replaces the
unit production bonus, research penalty and city-maintenance penalties of Tribal
System. Under Divine Kingship, each assigned priest in a city with an Egyptian
Obelisk grants +1 happiness, capped at +2 per city. This replaces the happiness
from palaces and monuments. Obelisks do not become obsolete while the civic is
active: all effects and construction remain available after Calendar.
If Calendar obsoletes the Pyramids while Divine Kingship is active, their
existing free Obelisks become permanent city buildings. The obsolete Pyramids
do not grant Obelisks to newly founded cities.
No state religion is required. Independent
Egypt under Pharaonic Kingship is **Pharaonic Egypt**, with the leader titled
**Pharaoh**. Theocracy or God State instead produces a **Temple State of Egypt**:
political rule is subordinate to religion, whereas Divine Kingship presents the
ruler as embodying divine authority.

| Civic | Required technology | Upkeep | Effects |
| --- | --- | --- | --- |
| **Tribal System** | None | None | +20% production for all units; -20% research; +100% distance and number-of-cities maintenance. |
| **Monarchy** | Monarchy | Medium | Capital buildings give +1 culture and +1 commerce each. Capital world wonders give +1 happiness in all cities, capped at +3, including obsolete wonders. Enables inheritance events. |
| **Republic** | Code of Laws | Medium | Assigned non-slave specialists consume 1 less food. Free specialists and settled Great People are excluded. |
| **Dictatorship** | Fascism | High | +20% production; no war weariness; -2 happiness in every city. |
| **Democracy** | Democracy | High | +2 happiness in every city; +1 commerce per assigned or free specialist. Adoption randomizes all other civic columns; elections every ten turns change one column. Other columns cannot be changed manually while Democracy is retained. Leaving adds two turns to normal revolution anarchy. |

### Legitimacy

| Civic | Required technology | Upkeep | Effects |
| --- | --- | --- | --- |
| **Despotism** | None | None | +1 happiness from palaces and monuments, including their civilization-specific replacements. |
| **Theocracy** | Divine Right | High | +1 happiness per building of the state religion; -2 happiness per building of another religion. With a state religion, land units receive +15% combat strength against barbarians and countries with a different or no state religion, on attack and defense. |
| **Plutocracy** | Banking | Medium | +25% gold income; +50% commerce from trade routes. |
| **Nationalism** | Nationalism | Medium | +5 culture in every city; +20% production; -5 happiness in cities where another player's culture exceeds the owner's culture on the city tile. |
| **Rule of Law** | Constitution | High | +2 happiness in every city; +10% commerce yield. |

### Labor

| Civic | Required technology | Upkeep | Effects |
| --- | --- | --- | --- |
| **Self-sufficiency** | None | None | +2 health in every city; cottage improvements do not grow; assigned specialists are blocked and existing assignments removed; free specialists remain. |
| **Slavery** | Bronze Working | Low | Captured population becomes slave units. Slave units have 25% upkeep, are targeted first in combat, can upgrade along a dedicated line, and can work in cities for 20 turns as a +3 production, -1 food specialist. Revolt risk falls with total garrison strength and disappears once it matches the available armed-slave force. Large conquests create regional slave-market or refugee events. Slave units created from captured populations retain a small origin-based promotion. |
| **Serfdom** | Civil Service | Low | +1 food from farms; workers build improvements 50% faster. Population can rush units only, not buildings or projects. |
| **Planned Economy** | Communism | High | +1 production from workshops, watermills, and windmills; +1 food from farms; -10% commerce yield. No trade routes with Capitalists. |
| **Market Economy** | Economics | Medium | +1 free specialist in every city; cottage improvements grow twice as fast. No trade routes with Communists. |

Improvement growth includes every upgrade stage: **Cottage → Hamlet → Village →
Town**. Self-sufficiency stops upgrades; Market Economy doubles their rate.
Normal idle citizens remain available under Self-sufficiency as a population fallback.

### Conquest aftermath

Conquering a large city while using **Slavery** creates a regional slave market. Other Slavery states can buy a slave unit, while other states can buy a captive's freedom: the freed person adds population, former-owner culture, and 20 turns of happiness. A large city conquered without Slavery instead sends refugees: non-Slavery states can accept them for free, while Slavery states can force them into 20 turns of labour for one temporary slave specialist and one temporary unhappiness. Only major civilizations with a city on the same continent receive an offer.

Under Slavery, conquest removes **two population** instead of one and creates one slave unit per population lost. Cities remain at least size one; recaptures are exempt.

Under Slavery, captured **workers, missionaries and settlers** become one slave
unit each, including civilization-specific variants. The slave appears on the
captive's tile with no movement left and receives its former owner's origin
promotion where available.

All armed-slave tiers can settle as a slave specialist for **20 turns** in a
city on their team while Slavery is active. Abolishing Slavery gives each armed
slave a **50% chance** to become its corresponding regular unit, including
civilization-specific replacements: for example, an Axeman, Swordsman or
Maceman; modern slave infantry becomes a Marine. The remaining armed slaves
disband. Converted units keep experience, promotions, damage and spent
movement, but lose Cannon Fodder and the slave upkeep discount.

A land attacker under Slavery also has a **50% chance to capture one slave** after killing a weaker non-animal land defender. Strength is compared at the start of combat, including defensive bonuses. The attacker must start at full health and take no damage except from defender first strikes. Withdrawals and collateral kills do not qualify. The slave appears on the attacker's tile and receives the defeated civilization's origin promotion where available.

### Military

| Civic | Required technology | Upkeep | Effects |
| --- | --- | --- | --- |
| **Warrior Society** | None | None | Melee units start with +2 experience; siege units have -20% combat strength. |
| **Naval Warfare** | Sailing | Low | +50% production and +2 experience for newly trained military ships, including transports. Workboats receive neither bonus. |
| **Feudal Retinues** | Feudalism | Medium | +5% land military unit production per Farm worked by the city, including siege units. Six worked Farms give +30%. |
| **Professional Army** | Military Tradition | High | Units start with +5 experience. |
| **Conscription** | Military Science | Medium | +25% production for all units. Food surplus also produces military land units, stopping growth while they are trained. Ships do not use this food conversion. |

Tribal System and Conscription's production bonuses include workers, settlers,
and missionaries. Conscription's food conversion is limited to military land units;
it does not grant an additional drafting ability.

### Islamic expansion event

Arabia's birth-flip zone also includes eastern Egypt and Sinai (x=69–72, y=31–37), subject to the normal capital and human-player flip rules. This does not expand its stability core.

Arabia starts with **6 Longbowmen, 6 Swordsmen, 8 Camel Archers and 4 Catapults**, in both normal births and the 600 AD start. Swordsmen and Catapults start with city-assault roles.

When Islam is first founded in **any Arabian city**, Arabia automatically joins the Islamic cause. Mecca is not required. If another country founds Islam, it chooses between **joining** and **suppression**. Joining adopts **Islam, Monarchy, Theocracy (Legitimacy), and Holy State** without additional anarchy, converts all owned cities, and expels their other religions using the normal expulsion rules. Economy and Military civics are unchanged. The full expansion event below applies to the joining country, regardless of civilization. This replaces Arabia's former permanent conquest-conversion power.

AI founders join with an **85%** chance when unaffiliated, **25%** when following another religion, and **100%** when already Islamic. Human founders outside Arabia receive an owner-addressed decision; its effects are synchronized.

Suppression expels Islam from the founder's cities and raises a barbarian army of **10 units** near its holy city: **2 Longbowmen, 3 Swordsmen, 3 Camel Archers and 2 Catapults**. The army cannot move that turn. Arabia instead adopts the Islamic cause and converts its cities, receiving **population-scaled recruitment packages (see below) for each newly converted city**, including its subsequent birth flips during the rally. If Arabia has not established a city, this rally waits until it does. Arabia has **20 turns from the rally** to conquer Islam's holy city militarily. It receives no full-event benefits before that capture; a timely capture starts the full event with its normal duration. Failure retains the converted cities, adopted civics and troops but grants no full event. During the rally, Arabia automatically declares total war on the holy city's current non-Islamic owner, overriding temporary peace treaties while respecting permanent peace and vassal relationships. Ownership is checked every turn, including changes before Arabia appears. If another country holding the holy city is Islamic, that country receives the full event instead and Arabia's rally ends. AI targeting prioritizes the holy city while its owner is at war with Arabia. This does not grant the full event's wars against met civilizations or peace-lock rules.

The event lasts **300 calendar years plus 10 turns**. The calendar duration is converted once into an expiry turn, then the extra turns are added (normally AD 620 to AD 1020, 40 turns). During the event:

- During the event, the participating country's AI prioritizes military production, targets garrisons of two defenders in its capital and one in other quiet cities, advances with smaller assault groups, and accepts riskier attacks. City targeting also values the population-scaled recruitment reward: each expected recruit adds four target-value points, favoring developed first conquests. Previously rewarded city locations receive no recruitment weighting; normal distance and attack considerations still apply. These AI preferences end immediately with the event.
- Every military conquest by the participating country, and Arabian birth flips during its own event, is converted to Islam. All other religions are expelled and banned using the normal expulsion rules; ordinary religious buildings are destroyed and holy cities retain dormant shrines. Holy State's normal conversion-pacification benefit still applies when eligible.
- Each military conquest during the event also establishes immediate control of the city tile and its eight neighboring tiles. Their foreign plot culture is reset and transferred to the conqueror, with **20 extra culture per tile**. Other city centers are excluded; stored city culture is unchanged. This also applies to recaptures, but not peaceful transfers or suppression-rally conversions.
- Each city's first acquisition through an Arabian military conquest or birth flip grants **one recruitment package plus another per four population**: `1 + floor(population / 4)` packages, each containing **2 Swordsmen, 1 Camel Archer, and 1 Catapult**, even without their normal training prerequisites. Population is measured before conquest losses and Holy State's population reward. Sizes 1–3 grant 4 units, 4–7 grant 8, and 8–11 grant 12. The same scaling applies to newly converted cities during Arabia's suppression rally, using their population before conversion. Reinforcements have no movement remaining that turn. Recaptures grant no further troops; the saved history uses city locations, including conquests before the event. Other gifts, trades and peaceful transfers grant no event rewards.
If another civilization has already received the full jihad event, Arabia's birth flips are restricted to the Arabian Peninsula. The extra territory in Egypt, Sinai and the Levant, including Jerusalem, is excluded. This also applies to culture, units, advance warnings and map hints; an expired event still counts.

- Arabia receives **one Settler** when it militarily captures Cairo during the event. The bonus is granted once, regardless of the city's current name; peaceful transfers and repeated captures grant no additional Settler. It cannot move on its arrival turn.
- The participating country immediately declares total war on all met non-Islamic countries, and checks for new contacts each turn. A team with any living Islamic member is exempt. The event overrides ordinary peace treaties, while scenario-level permanent peace and the participating country's own master/vassal relationships remain respected. Event wars, including newly involved defensive-pact/master/vassal belligerents, cannot be ended through peace, third-party mediation, capitulation or scripted peace until expiry.

Start and end announcements name the participating country and are addressed to nearby players: its team, event enemies, and countries with a city within 16 map-distance units of Islam's holy city or a participating city. Expiry stops forced conversion, recruitment and war declarations, and removes the event peace locks. Existing units, city religions/bans, adopted civics and state religion remain; ongoing wars become negotiable rather than ending automatically. Duration, troop counts and message radius use `RFCMP_ARABIAN_JIHAD_*`; suppression armies and the conquest deadline use `RFCMP_ISLAM_*` in `GlobalDefines.xml`. Pending founding decisions, the rally deadline, event timing, war locks and conquest history are saved and shared by multiplayer peers; runtime multiplayer validation remains separate.

When **Arabia's own jihad expires**, its caliphate divides into new successor civilizations: **Abbasids** in Iraq, Persia and Arabia; **Fatimids** in Egypt, the Levant and eastern North Africa; and **Umayyads** in western North Africa and Iberia. Cities outside these regions join the geographically nearest realm region, including across the world's wraparound boundary. These are approximate geographic realms, not a recreation of their exact historical borders or dates. Only Arabian cities are divided, and a realm appears only if it receives at least one city. With only one represented region, Arabia becomes that single successor realm. Each successor realm receives at most **4 cities if one realm appears, 6 each if two appear, and 8 each if three appear** at partition. Surplus cities become independent. Cities near the historical realm centers are retained preferentially, and each appearing realm keeps at least one city. This limit applies only to the partition.

Human Arabia chooses which eligible realm to continue governing. AI Arabia keeps the Abbasids when represented, otherwise the more populous remaining realm. The chosen realm retains the player's connection and diplomatic identity. Each other realm becomes an independent civilization in a reserved new slot, inherits known technologies, civics, state religion and existing foreign wars, and starts at peace with its siblings. Gold and each unit class are divided approximately by regional population; transports retain their cargo, and forces redeploy to their realm's cities or ports with no movement remaining. The partition grants no new army or conquest rewards. Each realm chooses an existing capital near its historical center. Regional stability data is updated and stability starts at +5. Successors use standard victories rather than Arabia's historical goals. A human decision remains pending across saves and is resolved once on every multiplayer peer; multiplayer runtime behavior remains unverified.

The canonical partition causes neither city-loss stability penalties nor conquest stability rewards. Foreign-land and missing-homeland-city counters are cleared until the next regular recount.

### Religion

| Civic | Required technology | Upkeep | Effects |
| --- | --- | --- | --- |
| **Ancestor Cult** | None | None | +1 culture from monuments, including civilization-specific replacements. |
| **State Religion** | Priesthood | Low | +1 happiness in cities with the state religion; +100% production for its missionaries and +25% production for its religious buildings. |
| **Holy State** | Theology | High | +10% production in cities with the state religion; an additional -1 happiness per non-state religion. Conquered cities are pacified by conversion. |
| **Tolerance** | Liberalism | Low | Removes unhappiness caused by foreign religions and different-religion diplomatic penalties involving your country. Countries with a different state religion have +2 relations toward you, except under State Atheism. The bonus requires both countries to have state religions. +5 percentage points to incoming religion spread chances through trade routes. Allows training missionaries of all religions. |
| **State Atheism** | Scientific Method | High | +10% research and +10% production; -1 happiness in all cities. Religious buildings have no effects; religions cannot spread in your cities. |


Tolerance adds **5 percentage points** to incoming trade spread for each missing religion and route after all culture and holy-city penalties (before rivalry and infrastructure efficiency). A chance otherwise reduced to zero becomes 5% before these factors; domestic routes also qualify. State Atheism and other spread restrictions still apply.

Missionaries can only be trained for your state religion, unless you adopt **Tolerance**. Without either a state religion or Tolerance, no missionaries can be trained. This also applies to production already in progress.

When **Christianity is founded**, the **two closest eligible Mediterranean coastal cities** also immediately receive it. The founding city is excluded. Selection uses actual adjacent Mediterranean water, excluding the Black Sea and Red Sea, and respects State Atheism, city bans and non-state-religion spread restrictions. Fewer than two cities are converted if insufficient eligible cities exist. These conversions use the normal Christian/Jewish replacement rule.

**Christianity and Islam** multiply the base trade-spread chance remaining after cultural and holy-city penalties by **1.5**. They then receive **+10 percentage points only in cities without religion**; Christianity also receives this flat bonus in cities containing only Judaism. The flat bonus can raise a zero chance, while the multiplier cannot. Tolerance adds its separate +5 percentage points after multiplication. If the receiving city contains the other religion, Christian-Islamic rivalry reduces the resulting trade chance to **25%** and missionary success to **50%** of its normal value. Trade chances are then multiplied by infrastructure efficiency and rounded down; a valid route is required. These rules apply worldwide, without civilization or region restrictions.

Successful Christian spread through trade or a missionary into a previously exclusively Jewish city has a **50%** chance to remove Judaism. The Jewish holy city is exempt. This replacement does not ban Judaism.

**Expel Religion:** A missionary in an owned city containing its religion can be consumed to remove all other religions and destroy their ordinary religious buildings. A holy city retains its holy status and unique shrine, with a grey holy-city symbol. The religion counts as absent and the shrine has no effects, including income, specialists and Great Person points. Spreading the religion there again restores full holy-city status and shrine effects; destroyed ordinary buildings must be rebuilt.

Expelled religions, including holy religions, are banned from trade, missionaries, events and scripted spread until the city changes owner. Adopting a new state religion immediately lifts all bans for that religion in all owned cities, without automatically spreading it. Bans and dormant holy-city status survive saving and loading; changing owner alone does not reactivate the religion. An action with no removable religions is unavailable.

Holy State pacification: If your state religion was absent at conquest, spreading it once ends occupation, adds +1 population and restores one building destroyed in that conquest if it can currently be built. Holy State must be active at conquest and conversion, with the same state religion. Each recapture checks eligibility anew; pending rewards survive saving.

Each **non-state religion present in a city causes -1 happiness by default**.
Without a state religion, this applies to every religion present. Tolerance
removes this religious unhappiness without granting extra happiness. Other
non-state-religion happiness bonuses offset the baseline penalty. Holy State
adds another -1, for a total of **-2 happiness per non-state religion**.

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

Profiles cover all four scenarios and do not override subsequent player choices.
Existing civilizations in saved games keep their current civics. See
[StartingCivics.md](StartingCivics.md) for all profiles and fallback rules.

## Democratic elections

Elections occur on **global turn multiples of ten**, while Democracy is active.
Adoption immediately chooses an available civic at random in each other column,
including the possibility of retaining the existing civic. Other columns cannot
be changed manually while retaining Democracy; leaving it unlocks them and adds
**two turns to normal revolution anarchy**. Existing immunity to anarchy applies.
They select one of the other four columns that has an available alternative,
then select a different civic that the player can currently adopt. If no column
has an available alternative, there is no change. Human players receive a
notification of the result.

Each election also opens a civic-specific announcement with a single **Adopt** button. Its tooltip says only **Adopt [civic]**. The result applies immediately; acknowledging the popup does not change synchronized game state. English and German announcements include a little satire about the winning policy.

Democracy ignores all **negative civic combination stability modifiers**, including Plutocracy with Planned Economy and Theocracy with Tolerance. Positive combination bonuses remain active. Other stability losses still apply.

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
| Monarchy + Feudal Retinues | +2 |
| Theocracy in Legitimacy + State Religion or Holy State in Religion | +2 |
| Plutocracy + Market Economy | +1 |
| Theocracy in Legitimacy + Tolerance | -3 |

Theocracy with State Atheism gives land units +15% combat strength against
countries of any state religion, and still against barbarians. The bonus does
not apply against countries without a state religion. Religious buildings each
cause -2 happiness even while State Atheism suppresses their positive effects;
technologically obsolete buildings still do not count. There is no happiness
bonus for buildings of your own state religion. The combination selects bespoke
names such as **Pontificate of Reason** and **Holy Empire of Reason**. This combination causes no inherent stability penalty.

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
whose core flip areas or additional scripted flip tiles include it. Each name
appears on its own line in that civilization's color. Your own civilization and civilizations currently alive
are excluded. The labels use names such as **Germany**, rather than an early
dynamic name such as “Germanic Peoples.”

The tooltip reads the core-area rectangles and additional exception tiles from
the same data as the spawn logic. It retains a birth-turn cutoff and does not
predict adjusted spawn delays or whether a particular city is eligible to flip,
so it is an aid to planning rather than a guarantee of a flip.

### Pre-flip unrest

**When the civilization appears**, cities in its core area and exception tiles
receive three turns of unrest using the occupation timer. For the usual
two-phase birth, this keeps unrest active until the city flip. An existing longer
occupation is preserved; a later flip extends unrest until the scheduled turn.

Affected human owners receive a message using the civilization's early dynamic
name, for example **“The [people] are rising up!”** This warning accompanies the inherited flip
system; it does not introduce a separate unit-flipping rule.

### Returning civilizations

A respawn can claim a major civilization's cities only when that owner's
stability is **below -20**. The hidden ten-point stability deduction and the
more permissive exception for the returning civilization's historical capital
are removed.

The owner's current and historical capitals and celebrating cities are
protected; the owner must have at least three cities. A claimed city must have
been founded by the returning civilization, be its historical capital, or have
at least **25% of its city culture**. At stability **from -40 to below -20**,
the city must also have angry citizens, be occupied, or be at least eight tiles
from the owner's capital; the distance condition requires at least four owned
cities. Below -40 this additional condition is waived.

Existing regional limits, minimum claimable city counts and rules for
independent and barbarian cities remain in place.

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

- **Serfdom** can sacrifice population to finish units, but cannot use this rush
  for buildings or projects.
- With **Banking**, gold can immediately finish a unit. The completed unit is a
  **mercenary**: it starts with one to three valid random promotions, cannot
  gain experience or further promotions, and cannot upgrade.
  Mercenaries do not consume free-unit or free-military-unit allowances. Each
  pays its regular unit cost plus a 100% surcharge, before difficulty modifiers.
- With **Corporation**, gold can also finish buildings.
- **Conscription** sends surplus food into production while training military
  land units. Food is therefore not stored for city growth during that production.

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

1. Copy the **`Awakened RFC`** folder into Beyond the Sword's **`Mods`** directory.
2. Keep that folder name: the included scenario files reference it. The original
   RFC MP mod can remain installed alongside this fork.
3. Load Awakened RFC from the game's mod menu, or use
   [Launch Awakened RFC.bat](<../Launch Awakened RFC.bat>). The launcher currently
   points to the standard Steam installation path; adjust it for other locations.
4. Choose an included scenario: **3000 BC**, **800 BC**, **600 AD**, or **1453 AD**.

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

See [AGENTS.md](../AGENTS.md) and [BUILDING.md](<../Awakened RFC/CvGameCoreDLL/BUILDING.md>)
for prerequisites and the compilation routine. The configured build copies the
rebuilt DLL into the workspace mod and the installed mod folder. Close Civ4
before rebuilding so the installed DLL can be replaced.

### Modern era and future research

Global warming and air units, including missiles and nuclear weapons, are
removed. Three separate repeatable research fields improve happiness, health
or combat strength; each field's costs increase by 35% per completion. Military
Research ends at +15%. A very expensive AI/automation branch unlocks six new
city buildings. Welfare-state policies are not implemented yet.
See [rules, costs and implementation details](ModernEra.md).

### 1453 AD start

The 1453 scenario begins immediately after the Ottoman capture of Constantinople,
with 96 cities and all 25 established major civilization slots selectable.
Period names and profiles represent the Mamluks, Ming, Muscovy, Italian states,
the Ottomans and their contemporaries. America keeps its usual future spawn.
See the [roster, map abstractions and setup notes](1453ADScenario.md).

### Food-transfer accounting

Each booked shipment has an equal export debit and import credit; rounding is
shared rather than performed independently by its endpoints. Raw trade food
therefore sums to zero across the participating cities. Growth speed need not:
small cities have cheaper population thresholds, granaries retain food, and
technology penalties affect positive surplus differently from starvation.
Redistributing food can increase population growth without increasing food
production. Imports from foreign cities also need not balance exports within
one country; the balance is global.

### Armed-slave upgrades

Slave units can upgrade directly to the most advanced armed-slave tier unlocked
by their team. Earlier armed tiers are no longer offered once a newer weapon
technology is known; normal upgrade costs and city requirements still apply.

Armed-slave equipment costs increase by weapon tier, before normal upgrade
discounts and AI adjustments:
The destination tier alone determines the price: direct upgrades do not pay
for skipped weapon tiers. Existing free-upgrade unique powers still apply.

| Armed-slave tier | Technology | Strength | Equipment gold |
| --- | --- | ---: | ---: |
| Bronze weapons | Bronze Working | 3 | 15 |
| Swordsman | Iron Working | 4 | 25 |
| Maceman | Machinery | 5 | 40 |
| Musketeer | Gunpowder | 7 | 60 |
| Rifleman | Rifling | 10 | 80 |
| Infantry | Assembly Line | 14 | 100 |
| Modern infantry | Robotics | 20 | 130 |

All tiers remain melee-class slave units with cannon fodder and quarter upkeep;
firearm tiers retain their matching firing animations. The final tier remains
a foot soldier rather than a mechanized vehicle. Revolts and garrison
suppression calculations use the strongest tier the owner has unlocked.

All slave tiers share the unarmed slave's distinctive body, with era-specific
weapons and animations, mixed figure variants and irregular formations. See [slave unit art](SlaveUnitArt.md)
for the tier roster, source credits and a static preview.
