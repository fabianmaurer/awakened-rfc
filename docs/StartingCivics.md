# Starting civics

Every playable civilization has a starting profile for the five new civic columns,
including Byzantium in the 600 AD scenario. Profiles apply to both human and AI
players at scenario initialization and at a later civilization's initial spawn.
They do not overwrite civic choices every turn or when loading a save.

## Preferred profiles

These are preferences, not technology grants. A civic is selected only when the
player can adopt it under the game's technology and unique-power rules after
starting technologies are assigned by the scenario or spawn code. Thus an ancient civilization may start with the basic civics even
when its preferred later institutions are listed below.

Egypt keeps Tribal System in the 3000 BC start. In the 800 BC scenario
(start turn 87), its preferred government is Monarchy and its scenario technology
package includes Monarchy. The selection-screen preview uses the same profile
override. Egypt's unique power still grants early Slavery only.

The 1453 start (turn 271) uses late-medieval scenario profiles through the same
`getProfile` accessor as the selection preview. The Mamluk, Delhi, Hafsid,
Timurid, Meccan, Burgundian and Ottoman slots use monarchies with ordinary
legitimacy; Italy uses a merchant republic, Germany a Christian religious
monarchy, and the American states indigenous religious institutions. The map
provides the technologies needed for these profiles. See `1453ADScenario.md`.

| Civilization | Government | Legitimacy | Labor | Military | Religion |
| --- | --- | --- | --- | --- | --- |
| Egypt | Tribal System | Despotism | Slavery | Militia | State Religion |
| India | Monarchy | Despotism | Serfdom | Militia | State Religion |
| China | Monarchy | Despotism | Serfdom | Militia | Ancestor Cult |
| Babylonia | Monarchy | Despotism | Slavery | Militia | State Religion |
| Greece | Republic | Despotism | Slavery | Militia | Ancestor Cult |
| Persia | Monarchy | Despotism | Slavery | Militia | State Religion |
| Carthage | Republic | Plutocracy | Slavery | Militia | State Religion |
| Rome | Republic | Despotism | Slavery | Militia | State Religion |
| Japan | Monarchy | Despotism | Serfdom | Knighthood | Ancestor Cult |
| Ethiopia | Monarchy | Despotism | Serfdom | Militia | State Religion |
| Maya | Monarchy | Theocracy | Slavery | Warrior Society | State Religion |
| Vikings | Monarchy | Despotism | Serfdom | Warrior Society | Ancestor Cult |
| Arabia | Monarchy | Theocracy | Serfdom | Militia | Holy State |
| Khmer | Monarchy | Despotism | Serfdom | Militia | State Religion |
| Spain | Monarchy | Despotism | Serfdom | Knighthood | State Religion |
| France | Monarchy | Despotism | Serfdom | Knighthood | State Religion |
| England | Monarchy | Despotism | Serfdom | Knighthood | State Religion |
| Germany | Monarchy | Despotism | Serfdom | Knighthood | State Religion |
| Russia | Monarchy | Despotism | Serfdom | Militia | State Religion |
| Netherlands | Republic | Plutocracy | Market Economy | Militia | Tolerance |
| Mali | Monarchy | Theocracy | Slavery | Militia | State Religion |
| Portugal | Monarchy | Theocracy | Serfdom | Knighthood | State Religion |
| Inca | Monarchy | Theocracy | Serfdom | Militia | State Religion |
| Mongolia | Monarchy | Despotism | Serfdom | Knighthood | Ancestor Cult |
| Aztecs | Monarchy | Theocracy | Slavery | Warrior Society | State Religion |
| Turkey | Monarchy | Theocracy | Serfdom | Knighthood | State Religion |
| America | Republic | Rule Of Law | Market Economy | Professional Army | Tolerance |
| Byzantium | Monarchy | Theocracy | Serfdom | Militia | Holy State |

## Fallbacks

If the preferred civic is unavailable, the first adoptable civic in the following
sequence is selected. All five columns are initialized; no anarchy is introduced.

| Column | Fallback order |
| --- | --- |
| Government | Monarchy, then Tribal System |
| Legitimacy | Despotism |
| Labor | Slavery, then Self-sufficiency |
| Military | Militia, then Warrior Society |
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
