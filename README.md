# Awakened Rhye's and Fall of Civilization

**English** | [Deutsch](README.de.md)

**Awakened RFC** · [GitHub](https://github.com/fabianmaurer/awakened-rfc)

A multiplayer overhaul of **Rhye's and Fall Multiplayer** for
**Civilization IV: Beyond the Sword**. Build a civilization across history with
more consistent economics, new civics, and trade that shapes culture and religion.
RFC's world maps, historical spawns, unique powers and victory goals remain.

## What changes?

- **25 new civics in five columns**, with new artwork and historically suited
  starting choices. Democracy holds elections every ten turns, randomly changing
  one other civic column.
- **Civic stability rewards compatible institutions**, capped at −5 to +5.
  The outdated-civics penalty is removed.
- **Dynastic inheritance:** a collapsing monarchy can pass its realm to an
  eligible same-religion monarchy on the same continent.
- **More consistent civilization economics:** individual growth, production,
  research and upkeep tuning is removed, and inflation stays at zero.
  Shared civilization-group rules remain.
- **Technology-based growth:** a shared 30% penalty to positive growth surplus
  falls by 0.5 percentage points per known technology, disappearing at 60 techs.
  Food production and population consumption remain unchanged.
- **Land reclamation:** farms are available on flood plains with Agriculture;
  workers can drain marshes into grassland from Engineering.
- **Trade without roads or border agreements:** 50% efficiency through distance 5,
  declining linearly to zero at 15. Roads enable 100% at any distance; water connections require
  Sailing and have a twelve-tile limit until Astronomy. Water trade is halved
  unless both cities have harbors. Harbors can also be built one tile inland
  from an ocean coast, boosting worked water tiles.
  Routes exchange culture and religion in
  both directions; this replaces the old passive religion spread. Missionaries
  remain. Cultural homogeneity and holy cities resist trade-based religion spread;
  State Atheism blocks religious spread.
- **Food trade follows city attraction:** wealth per resident drives most food
  transfers, while health and happiness add a weaker pull. Supplier exports are
  capped at one food per population point; embargoes and blockades can leave
  import-dependent cities short of food.
- **Military access** replaces Open Borders and remains reciprocal.
  **Trade embargoes** are available from Currency in the Foreign Advisor.
- **Advance spawn warnings:** tile tooltips show future flip areas; affected
  cities enter unrest three turns before a civilization's initial flip.
- **Cultural uprisings replace direct flips** in regular civilizations' cities:
  25% population loss, reduced rebellious culture, and two barbarian rebels per
  population lost. Revolts require a foreign majority above 50% on the city tile;
  barbarian and independent cities retain cultural flipping under that condition.
- **Dynamic English and German country names**, inspired by historical states
  and plausible alternate histories.
- **Relocate conquered cities:** above 25% of your team's city culture, dismantle
  the city and receive a settler through the conquest popup.

## Production conversions

| Conversion | Available from | Efficiency |
| --- | --- | ---: |
| Sale of goods | Start | 25% into gold |
| Wealth | Currency; replaces Sale of goods | 50% into gold |
| Research | Alphabet | 25% into research |
| Culture | Music | 50% into culture |

## Civics

One civic per column. **Commerce** is the yield allocated to gold, research,
culture and espionage, distinct from gold income.

<details>
<summary>All 25 civics: technologies, upkeep and bonuses</summary>

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
| **Slavery** | Bronze Working | Low | +2 commerce from plantations; captured population becomes slave units. Slave units have 25% upkeep, are targeted first in combat, can upgrade along a dedicated line, and can work in cities for 20 turns as a +3 production, -1 food specialist. Revolt risk falls with total garrison strength and disappears once it matches the available armed-slave force. Large conquests create regional slave-market or refugee events. Slave units created from captured populations retain a small origin-based promotion. |
| **Serfdom** | Feudalism | Low | +1 food from farms; -1 commerce from villages; workers build improvements 50% faster; may rush units with population. |
| **Planned Economy** | Communism | High | +1 production from workshops, watermills, and windmills; +1 food from farms; -20% commerce yield. No trade routes with Capitalists. |
| **Market Economy** | Economics | Medium | +1 free specialist in every city; cottage improvements grow twice as fast. No trade routes with Communists. |

### Military

| Civic | Required technology | Upkeep | Effects |
| --- | --- | --- | --- |
| **Warrior Society** | None | None | Melee units start with +2 experience; siege units have -20% combat strength. |
| **Militia** | Archery | Low | +30% city defense; -10% combat strength outside the unit owner's territory. |
| **Knighthood** | Engineering | Medium | +25% production for mounted units; +10% city attack. |
| **Professional Army** | Military Tradition | High | Units start with +5 experience. |
| **Conscription** | Military Science | Medium | +25% production for all units; surplus food produces military units. |

### Religion

| Civic | Required technology | Upkeep | Effects |
| --- | --- | --- | --- |
| **Ancestor Cult** | None | None | +1 culture from monuments, including civilization-specific replacements. |
| **State Religion** | Priesthood | Low | +1 happiness in cities with the state religion; +100% production for missionaries of any religion. |
| **Holy State** | Theology | High | +2 happiness and +10% production in cities with the state religion; -2 happiness in cities without it. |
| **Tolerance** | Liberalism | Medium | Removes unhappiness caused by foreign religions. |
| **State Atheism** | Scientific Method | High | +10% research; religious buildings have no effects; religions cannot spread in your cities. |

</details>

## Play

1. Copy **`Awakened RFC`** into Beyond the Sword's **`Mods`** folder. Keep that name;
   the original mod can remain alongside it.
2. Load it from the game's mod menu or use [the launcher](<Launch Awakened RFC.bat>)
   (configured for Steam).
3. Choose **3000 BC**, **800 BC**, **600 AD** or **840 AD**. All multiplayer peers need identical
   mod files and DLLs.

Hold **Shift while launching** after text changes. Start a new game after changes
to civic XML modifiers. Multiplayer runtime validation of the overhaul is pending.

## Details and development

[Full gameplay rules](docs/Gameplay.en.md) · [Starting civics](docs/StartingCivics.md) ·
[Civic stability](docs/CivicStability.md) · [Civic implementation](docs/CivicEffects.md) ·
[Country names](docs/CountryNames.csv) · [Naming rules](docs/CountryNaming.md)

DLL builds require the original **32-bit VC7.1** toolchain. See
[build instructions](<Awakened RFC/CvGameCoreDLL/BUILDING.md>) and [AGENTS.md](AGENTS.md).
