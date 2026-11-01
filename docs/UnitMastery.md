# Military unit mastery

Military fighting units have three cumulative, unit-specific mastery levels.
Each level costs twice the previous one: base, 2x base, 4x base. The base is
the base XML research cost of the unit's most expensive required technology.
The mastery uses that technology's era for research cost modifiers. Warriors
require no technology and use a fallback base cost of 100. Normal research
modifiers still apply; technology diffusion discounts do not apply to mastery.
Calendar thresholds do not reprice research. Unit production costs and reward
strength do not change the research cost. Research unlocks with all unit technology
requirements and ends at III or when an upgrade successor is technologically
available, independently of resources/buildings. Unique units use their own
tracks; civilizations cannot research another civilization's replacement.

Each direct combat grants both participants' teams 1% of their exact unit type's
next mastery level's total research cost, whether attacking, defending, losing
or withdrawing. Mastery need not be selected for research, but must currently be
researchable. Collateral victims and civilian captures do not grant progress.
The XML define UNIT_MASTERY_COMBAT_RESEARCH_PERCENT controls the percentage;
0 disables it. Awards round down to whole research points, with a minimum of 1,
and are capped at the current level's remaining cost without research overflow.

Bonuses follow the current owner's team and exact unit type. Existing and new
units benefit; upgrading switches tracks. Surviving obsolete units retain
completed benefits. No promotions are added or transferred. Existing unique
powers and capped global Military Research remain active and stack normally.
Unfinished retired research returns to the acquiring player's research overflow.

Small mastery icons sit below the ordinary tree without arrows, grouped side
by side within their unlocking technology's column. The dialog grows to fit
the row; shorter screens use tighter spacing to avoid vertical scrolling.
Research help lists
all three rewards; the research name shows the next level, such as Archer
Mastery I, II, or III. Completed tracks remain labeled III. General rules are
in the Civilopedia rather than the hover text. The top research bar shows
the research name and turns remaining. Unit tooltips only append (I), (II), or (III) to the name;
unmastered units have no suffix. Visible enemies follow the same display rule.
No map badges or mastery effect explanations are added to unit tooltips.

Civilian/transport units, aircraft and nuclear weapons are excluded. Aircraft
remain disabled by the existing mod rules. Armed exploration and unique
Carrack/East Indiaman combat ships have tracks. No existing-save compatibility
is required. Run `python tools/generate_unit_mastery.py` after changing tracks
or unit/tech prerequisites, then rebuild with the legacy VC7.1 toolchain.
Research names, reward descriptions and rules include all five languages.

Gameplay and multiplayer validation are user-operated and remain unverified.

| Unit | Base cost | I | II | III |
| --- | ---: | --- | --- | --- |
| Scout | 42 | +1 visibility range. | Double movement in forests; Double movement in jungle. | Heals 15 extra HP per turn; Immune to first strikes. |
| Explorer | 750 | +1 movement. | Units on the same tile heal 15 extra HP per turn. | Ignores terrain movement costs; Heals 15 extra HP per turn. |
| Warrior | 100 | +30% city defense. | +30% against melee units. | Heals 15 extra HP per turn; Can heal while moving. |
| Quechua Warrior | 53 | +50% against archery units. | Double movement in hills. | +40% city attack; Heals 15 extra HP per turn. |
| Swordsman | 300 | +30% city attack. | Immune to first strikes. | Can attack multiple times per turn; +1 movement. |
| Aztec Jaguar | 126 | Double movement in jungle. | +50% jungle attack; +50% forest attack. | Can heal while moving; Heals 20 extra HP per turn. |
| Celtic Gallic Warrior | 300 | +50% hills attack. | Double movement in hills. | +40% withdrawal chance; +30% hills defense. |
| Legion | 300 | +40% city attack. | Units on the same tile heal 15 extra HP per turn. | Ignores building defenses. |
| Axeman | 126 | +35% against melee units. | +40% forest attack. | +30% collateral damage; +3 collateral targets; +40% collateral damage limit. |
| Greek Phalanx | 126 | +50% against mounted units. | +2 first strikes. | +40% against melee units; +30% hills defense. |
| Sumerian Vulture | 126 | +40% against melee units. | +40% city attack. | Immune to first strikes; Heals 15 extra HP per turn. |
| Native America Dog Soldier | 126 | +50% forest defense. | Double movement in forests. | +40% against melee units; Units on the same tile heal 15 extra HP per turn. |
| Maceman | 1200 | +30% city attack. | +25% against armored units; +25% against gunpowder units. | +2 first strikes. |
| Japan Samurai | 1200 | +2 first strikes. | +40% city attack. | Can attack multiple times per turn; +1 movement. |
| Berserker | 1200 | +40% city attack. | No river attack penalty; +1 movement. | Can attack multiple times per turn. |
| Spearman | 42 | +50% against mounted units. | +40% hills defense. | +2 first strikes. |
| Zulu Impi | 42 | +40% withdrawal chance. | Can use enemy roads. | Units on the same tile heal 20 extra HP per turn; Can heal while moving. |
| Maya Holkan | 126 | +50% jungle defense. | Double movement in jungle. | +50% against mounted units; +2 first strikes. |
| Pikeman | 1500 | +50% against mounted units. | +30% against melee units. | Immune to first strikes; Heals 15 extra HP per turn. |
| Holy Roman Landsknecht | 1500 | +50% against melee units. | +50% against mounted units. | +2 first strikes; Heals 15 extra HP per turn. |
| Musketman | 1500 | +30% city defense. | +2 first strikes. | No amphibious attack penalty; No river attack penalty. |
| French Musketeer | 1500 | +35% withdrawal chance. | Can use enemy roads. | Can attack multiple times per turn. |
| Janissary | 1500 | +30% against melee units; +30% against archery units; +30% against mounted units. | +40% city attack. | +2 first strikes. |
| Ethiopian Oromo Warrior | 1500 | +2 first strikes. | +50% hills defense. | Double movement in hills; Heals 20 extra HP per turn. |
| Rifleman | 2208 | +25% against gunpowder units. | +40% hills defense. | Can heal while moving; Heals 15 extra HP per turn. |
| English Redcoat | 2208 | +40% against gunpowder units. | No amphibious attack penalty; No river attack penalty. | +2 first strikes; +30% city defense. |
| Grenadier | 2116 | +35% city attack. | +35% collateral damage; +3 collateral targets; +50% collateral damage limit. | Immune to first strikes. |
| At Infantry | 3220 | +50% against armored units. | +40% hills defense. | +40% withdrawal chance. |
| Infantry | 3680 | +30% city attack. | Units on the same tile heal 15 extra HP per turn. | Can attack multiple times per turn; +1 movement. |
| Marine | 4140 | +35% city attack. | +2 first strikes. | Can heal while moving; Heals 20 extra HP per turn. |
| American Navy Seal | 4140 | +2 first strikes. | Can use enemy roads. | Can attack multiple times per turn; +1 movement. |
| Paratrooper | 2944 | +40% hills defense. | Can use enemy roads. | +35% city attack; Immune to first strikes. |
| Mechanized Infantry | 4564 | +35% against armored units. | Units on the same tile heal 20 extra HP per turn. | +1 movement; Can use enemy roads. |
| Archer | 63 | +40% city defense. | +40% hills defense. | +2 first strikes. |
| Mali Skirmisher | 63 | +40% withdrawal chance. | +1 movement. | +50% hills defense; +2 first strikes. |
| Asharittu Bowman | 63 | +50% against melee units. | +40% city defense. | +2 first strikes; Units on the same tile heal 15 extra HP per turn. |
| Longbowman | 1125 | +40% city defense. | +2 first strikes. | Units on the same tile heal 15 extra HP per turn; Heals 15 extra HP per turn. |
| Crossbowman | 1125 | +40% against melee units. | +40% hills attack. | +2 first strikes. |
| China Chokonu | 1125 | +3 collateral targets. | +20% collateral damage limit. | Can attack multiple times per turn; +1 movement. |
| Chariot | 63 | +30% withdrawal chance. | +40% against archery units. | +1 movement; No river attack penalty. |
| Egypt Warchariot | 63 | +50% against archery units. | +40% withdrawal chance. | +1 movement; Can attack multiple times per turn. |
| Persia Immortal | 42 | +40% city attack. | Units on the same tile heal 15 extra HP per turn. | Can heal while moving; Heals 25 extra HP per turn. |
| Horse Archer | 375 | +30% withdrawal chance. | +2 first strikes. | Can use enemy roads. |
| Numidian Cavalry | 375 | +40% against melee units. | +40% withdrawal chance. | Can use enemy roads; +1 movement. |
| Mongol Keshik | 1500 | +40% withdrawal chance. | Can use enemy roads. | Can attack multiple times per turn; +1 movement. |
| Knight | 1500 | +30% city attack. | +30% withdrawal chance. | Can attack multiple times per turn; +1 movement. |
| Arabia Camelarcher | 1500 | +40% against mounted units. | Heals 25 extra HP per turn; Can heal while moving. | Can attack multiple times per turn; +1 movement. |
| Byzantine Cataphract | 1125 | +40% against melee units. | Immune to first strikes. | +40% city attack; +35% withdrawal chance. |
| Spanish Conquistador | 1500 | +35% against gunpowder units. | No amphibious attack penalty; No river attack penalty. | +40% city attack; Units on the same tile heal 15 extra HP per turn. |
| Cuirassier | 1656 | +30% against gunpowder units. | +35% withdrawal chance. | +1 movement; Immune to first strikes. |
| Cavalry | 2208 | +50% against siege units. | Can use enemy roads. | Can attack multiple times per turn; +1 movement. |
| Russia Cossack | 2208 | +50% against mounted units. | +40% withdrawal chance. | Can attack multiple times per turn; +1 movement. |
| War Elephant | 450 | +35% against melee units. | +35% city attack. | +40% collateral damage; +4 collateral targets; +50% collateral damage limit. |
| Khmer Ballista Elephant | 450 | +50% against mounted units. | +40% collateral damage; +4 collateral targets; +50% collateral damage limit. | Immune to first strikes. |
| Tank | 4140 | +35% city attack. | +35% withdrawal chance. | +1 movement; Can use enemy roads. |
| German Panzer | 4140 | +50% against armored units. | +40% withdrawal chance. | +1 movement; Can use enemy roads. |
| Main Battle Tank | 4122 | +35% against armored units. | Immune to first strikes. | +1 movement; Can heal while moving. |
| Catapult | 375 | +20% city bombardment. | +3 collateral targets. | +40% withdrawal chance. |
| Korean Hwacha | 375 | +50% against melee units. | +4 collateral targets. | +25% collateral damage limit; +35% withdrawal chance. |
| Trebuchet | 1500 | +50% city attack. | +25% city bombardment. | +20% collateral damage limit; +2 collateral targets. |
| Cannon | 1500 | +30% collateral damage. | +30% city bombardment. | +40% withdrawal chance. |
| Machine Gun | 3220 | +35% against gunpowder units. | +3 first strikes. | Units on the same tile heal 20 extra HP per turn. |
| Artillery | 3220 | +4 collateral targets. | +20% collateral damage limit. | +1 movement. |
| Mobile Artillery | 4122 | +40% city bombardment. | +4 collateral targets. | +50% withdrawal chance; Can use enemy roads. |
| Trireme | 675 | +2 first strikes. | +40% withdrawal chance. | +2 movement. |
| Caravel | 1200 | +2 visibility range. | +2 movement. | +50% withdrawal chance. |
| Portugal Carrack | 1200 | Heals 20 extra HP per turn; Can heal while moving. | +2 visibility range. | +2 movement; +35% withdrawal chance. |
| Netherlands Oostindievaarder | 1472 | +2 first strikes. | Heals 25 extra HP per turn; Can heal while moving. | +2 movement. |
| Privateer | 1656 | +40% withdrawal chance. | +2 movement. | Can heal while moving; Heals 25 extra HP per turn. |
| Frigate | 1656 | +25% city bombardment. | +2 first strikes. | +2 movement. |
| Ship Of The Line | 2116 | Immune to first strikes. | +30% city bombardment. | +3 first strikes. |
| Ironclad | 2484 | +25% city bombardment; Heals 15 extra HP per turn. | Immune to first strikes. | +2 movement. |
| Destroyer | 3404 | +2 visibility range. | +3 first strikes. | +2 movement; +30% withdrawal chance. |
| Battleship | 4140 | +40% city bombardment. | +3 collateral targets; +20% collateral damage limit. | Can attack multiple times per turn; +1 movement. |
| Missile Cruiser | 4564 | Units on the same tile heal 20 extra HP per turn; Heals 15 extra HP per turn. | +2 visibility range. | Can attack multiple times per turn; +2 movement. |
| Stealth Destroyer | 4564 | +3 first strikes. | +45% withdrawal chance. | +2 movement; Can heal while moving. |
| Submarine | 3165 | +40% withdrawal chance. | +3 first strikes. | +2 movement. |
| Attack Submarine | 3404 | +3 first strikes. | Immune to first strikes; Heals 20 extra HP per turn. | +2 movement; +30% withdrawal chance. |
| Autonomous Combat Vehicle | 47840 | +40% city defense. | Can heal while moving; Heals 20 extra HP per turn. | +3 first strikes. |
| Autonomous Battle Tank | 80960 | +40% city attack. | +40% against armored units. | +1 movement; Can use enemy roads. |
| War Galley | 1125 | +2 first strikes. | Heals 20 extra HP per turn; Can heal while moving. | Can attack multiple times per turn. |
| Arctic hunter | 100 | +1 visibility range; +50% against animals. | Double movement in hills. | +2 first strikes; Heals 20 extra HP per turn. |
| Woodland Warrior | 100 | +50% forest attack; +50% forest defense. | Double movement in forests. | Units on the same tile heal 15 extra HP per turn; +2 first strikes. |
