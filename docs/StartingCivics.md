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
Obelisk, capped at +2 per city. It preserves the Obelisk's two priest slots and
allows its construction after Calendar while active. Free and settled priests
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
Self-sufficiency, Warrior Society and Ancestor Cult. Persia and the Latin
settlements use tribal government. The existing ancient technology packages
are otherwise retained. Later births use their normal profiles.
See [800BCScenario.md](800BCScenario.md) for the complete audit and ruler names.

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
