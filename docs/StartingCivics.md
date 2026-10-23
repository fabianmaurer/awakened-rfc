# Starting civics

Every playable civilization has a starting profile for the five new civic columns,
plus the non-playable Byzantine Empire in the 600 AD scenario. Profiles apply to both human and AI
players at scenario initialization and at a later civilization's initial spawn.
They do not overwrite civic choices every turn or when loading a save.

## Preferred profiles

Rome's Republic and Warrior Society choices now resolve to **Roman Republic**
and **Roman Legions**, including civilization-specific effects and help.
Roman Republic is available from birth. See [RomanEmpire.md](RomanEmpire.md)
for provincial administration, campaign AI and collapse behavior.

These are preferences, not technology grants. A civic is selected only when the
player can adopt it under the game's technology and unique-power rules after
starting technologies are assigned by the scenario or spawn code. Thus an ancient civilization may start with the basic civics even
when its preferred later institutions are listed below.

Egypt starts with **Pharaonic Kingship / Pharaonentum**, **Divine Kingship /
Gottkönigtum** and Slavery in 3000 BC.
The 3000 BC map removes the marble deposit at (69,35) as a small starting-position
reduction, retaining stone at (68,33) and the existing food and other resources.
The Egyptian government variant grants +1 production from farms and +1 production
per slave specialist, with medium civic upkeep. It replaces the generic Tribal
System's unit production bonus, research penalty and maintenance penalties.
Its civic ID and technology requirement remain unchanged. The AI values its
farm and slave production and actual upkeep. Despotism is displayed as
**Divine Kingship / Gottkönigtum** for Egypt. Both labels apply in every era
and with any religion. Divine Kingship replaces Despotism's palace/monument
happiness with +1 happiness per assigned priest in cities with an Egyptian
Obelisk, capped at +2 per city. Obelisks do not become obsolete while the civic
is active: all effects and construction remain available after Calendar. Free and settled priests
do not count. It describes a ruler embodying divine authority;
the separate Theocracy and God State civics describe rule subordinate to religion.
Under Pharaonic Kingship, the leader's displayed personal name receives the title
Pharaoh. These labels and titles do not change the starting institution profiles.
The three civilization-specific civic icons use a pharaoh with a nemes headdress
(Pharaonic Kingship), a golden falcon with a solar disk (Divine Kingship), and
a kabuto helmet (Bushido). Source images, generation prompts and the 64px preview
are kept in `art/civic-variants`; `tools/build_civic_variant_icons.py` converts
them to DXT3 DDS buttons. The civilization-specific button resolver is shared by
the civic screen, Civilopedia, technology screen and diplomacy civic icons.
In the 800 BC scenario (start turn 87), Egypt also starts with Pharaonic Kingship,
Divine Kingship and Slavery. This selects Pharaonic Egypt and gives Shoshenq III
the title Pharaoh. Its existing Monarchy technology remains available for later
government changes. The selection-screen preview uses the same starting profile.
Egypt's unique power still grants early Slavery only.

The other eight initial 800 BC players also have explicit profiles now. India,
China, Greece and Carthage receive Monarchy so their intended governments are
available at initialization. India and China use Self-sufficiency instead of
an unavailable medieval labor civic; Japan uses tribal government,
Self-sufficiency, Warrior Society and Ancestor Cult. Persia and Rome use tribal government and Ancestor Cult for their early local cults. The existing ancient technology packages
are otherwise retained. Later births use their normal profiles.
See [800BCScenario.md](800BCScenario.md) for the complete audit and ruler names.

## 600 AD scenario (turn 181)

The five initial polities have explicit scenario profiles. Later births retain
normal birth profiles. Every choice is available with the existing scenario
technologies; no technologies or civic prerequisites are changed.

| Civilization | Government | Legitimacy | Labor | Military | Religion |
| --- | --- | --- | --- | --- | --- |
| China | Monarchy | Despotism | Serfdom | Warrior Society | State Religion |
| Japan | Monarchy | Despotism | Serfdom | Warrior Society | State Religion |
| Vikings | Monarchy | Despotism | Slavery | Naval Warfare | Ancestor Cult |
| Arabia | Tribal System | Despotism | Slavery | Warrior Society | Ancestor Cult |
| Byzantium | Monarchy | Despotism | Slavery | Naval Warfare | State Religion |

These are approximations within the existing five-column system:

- **China:** Sui imperial government and dependent agricultural labor, with
  official religious patronage. State Religion replaces Ancestor Cult to allow
  court-sponsored religion; it does not erase ancestral rites or force a
  particular faith. [University of Washington: Sui Buddhist patronage](https://depts.washington.edu/silkroad/exhibit/sui/ps084830.html).
- **Japan:** Asuka court monarchy, hereditary dependent labor and clan warriors,
  before medieval samurai institutions. State Religion allows the court's
  Buddhist patronage alongside indigenous cults. Serfdom is a broad labor
  abstraction, not a claim that European manorialism existed in Japan in 600.
  [Metropolitan Museum: Asuka and Nara periods](https://www.metmuseum.org/essays/asuka-and-nara-periods-538-794).
- **Vikings:** early Scandinavian kingship, thrall labor and pagan cults.
  Slavery replaces the unavailable Serfdom preference. Naval Warfare represents
  maritime mobility; this early start does not imply that the later Viking Age
  or unified Scandinavian kingdoms already existed.
  [National Museum of Denmark: thralls](https://en.natmus.dk/historical-knowledge/denmark/prehistoric-period-until-1050-ad/the-viking-age/power-and-aristocracy/slaves-and-thralls/).
- **Arabia:** pre-Islamic tribal authority and local cults. Starting with
  Theocracy and God State would anticipate the Islamic polity: Muhammad's first
  revelations date to 610 and the hijra to 622. The existing Islamic-cause event
  later adopts Islam, Monarchy, Theocracy and God State automatically for Arabia;
  it directly sets those civics, so Ancestor Cult does not block the transition.
  [Metropolitan Museum: birth of Islam](https://www.metmuseum.org/essays/the-birth-of-islam).
- **Byzantium:** imperial authority with an official Christian church, rather
  than clerical government. Slavery is an explicit legal labor choice, replacing
  an unavailable Serfdom preference; it does not imply that all peasants were
  slaves. Naval Warfare represents the Mediterranean imperial fleets and removes
  Warrior Society's siege penalty. It cannot fully represent the professional
  late Roman land army: Professional Army requires Military Tradition, which
  would grant much later technology. No such technology is added.
  [Cambridge: Byzantine slavery](https://www.cambridge.org/core/books/abs/cambridge-world-history-of-slavery/slavery-in-the-byzantine-empire/6BC93914928532A51E2D9BE5EF40771F).

China and Japan retain the basic Warrior Society military approximation because
neither has Feudalism; neither is assigned the later Feudal Retinues civic.
State Religion enables religious affiliation but does not itself select a faith;
existing religion founding, spread and conversion rules remain in effect.
The original scenario's advanced starting armies and early settler starts remain
intentional gameplay simplifications.

## Other starts and normal birth preferences

The 1453 start (turn 271) uses late-medieval scenario profiles through the same
`getProfile` accessor as the selection preview. The Mamluk, Delhi, Hafsid,
Timurid, Meccan, Burgundian and Ottoman slots use monarchies with ordinary
legitimacy; Italy uses a merchant republic, Germany a Christian religious
monarchy, and the American states indigenous religious institutions. The map
provides the technologies needed for these profiles. See `1453ADScenario.md`.

| Civilization | Government | Legitimacy | Labor | Military | Religion |
| --- | --- | --- | --- | --- | --- |
| Egypt | Tribal System | Despotism | Slavery | Warrior Society | State Religion |
| India | Monarchy | Despotism | Serfdom | Warrior Society | State Religion |
| China | Monarchy | Despotism | Serfdom | Warrior Society | Ancestor Cult |
| Babylonia | Monarchy | Despotism | Slavery | Warrior Society | State Religion |
| Greece | Republic | Despotism | Slavery | Naval Warfare | Ancestor Cult |
| Persia | Monarchy | Despotism | Slavery | Warrior Society | State Religion |
| Carthage | Republic | Plutocracy | Slavery | Naval Warfare | State Religion |
| Rome | Republic | Despotism | Slavery | Warrior Society | State Religion |
| Japan | Monarchy | Despotism | Serfdom | Feudal Retinues | Ancestor Cult |
| Ethiopia | Monarchy | Despotism | Serfdom | Warrior Society | State Religion |
| Maya | Monarchy | Theocracy | Slavery | Warrior Society | State Religion |
| Vikings | Monarchy | Despotism | Serfdom | Naval Warfare | Ancestor Cult |
| Arabia | Monarchy | Theocracy | Serfdom | Warrior Society | Holy State |
| Khmer | Monarchy | Despotism | Serfdom | Warrior Society | State Religion |
| Spain | Monarchy | Despotism | Serfdom | Feudal Retinues | State Religion |
| France | Monarchy | Despotism | Serfdom | Feudal Retinues | State Religion |
| England | Monarchy | Despotism | Serfdom | Feudal Retinues | State Religion |
| Germany | Monarchy | Despotism | Serfdom | Feudal Retinues | State Religion |
| Russia | Monarchy | Despotism | Serfdom | Warrior Society | State Religion |
| Netherlands | Republic | Plutocracy | Market Economy | Naval Warfare | Tolerance |
| Mali | Monarchy | Theocracy | Slavery | Warrior Society | State Religion |
| Portugal | Monarchy | Theocracy | Serfdom | Naval Warfare | State Religion |
| Inca | Monarchy | Theocracy | Serfdom | Warrior Society | State Religion |
| Mongolia | Monarchy | Despotism | Serfdom | Horde | Ancestor Cult |
| Aztecs | Monarchy | Theocracy | Slavery | Warrior Society | State Religion |
| Turkey | Monarchy | Theocracy | Serfdom | Feudal Retinues | State Religion |
| America | Republic | Rule Of Law | Market Economy | Professional Army | Tolerance |
| Byzantium | Monarchy | Theocracy | Serfdom | Warrior Society | Holy State |

## Fallbacks

If the preferred civic is unavailable, the first adoptable civic in the following
sequence is selected. All five columns are initialized; no anarchy is introduced.

| Column | Fallback order |
| --- | --- |
| Government | Monarchy, then Tribal System |
| Legitimacy | Despotism |
| Labor | Slavery, then Self-sufficiency |
| Military | Warrior Society |
| Religion | State Religion, then Ancestor Cult |

Minor factions use Tribal System, Despotism, Self-sufficiency, Warrior Society,
and Ancestor Cult. Their existing units and scenario technologies are preserved.

## Initialization and multiplayer

Scenario technologies are assigned before starting civics and scripted starting
units. Later spawns use the same order. Existing units are not granted retroactive
XP; scripted unit creation retains the existing experience rules. The existing
state-religion selection is preserved.

Profiles are resolved from XML type names at runtime, after XML initialization.
They use no local UI state or randomness and apply identically to all peers.
All multiplayer peers must have the same Python and scenario files.
Start a new game to use these profiles for civilizations already present.
Runtime and multiplayer validation is pending.

Implementation: `Assets/Python/StartingCivics.py` and `RiseAndFall.py`.
