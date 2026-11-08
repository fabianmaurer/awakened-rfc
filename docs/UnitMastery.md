# Military unit mastery

Military fighting units have three cumulative, unit-specific mastery levels.
Tier I gives a useful role bonus, tier II adds a supporting ability, and tier III
provides a major improvement. Unique tracks build on each unit's own abilities.
Naval mastery grants at most two attacks per turn, still requiring movement.
Native Blitz and promotions retain their normal effects. Mastery permits enemy
road use only; native enemy-route abilities also permit railroads.
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
Completing a tier ends that research selection. Any queued next technology
continues normally; otherwise humans choose their next research and AI evaluates
its choices again. Continuing the same mastery requires a new research choice.

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
Bonuses against Chariots, Archers, Riflemen or Infantry also affect their unique
replacements. Extra cargo capacity follows the owner's mastery; losing capacity
does not unload existing passengers, but prevents loading above the new limit.

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
| Scout | 42 | +25% against animals; Heals 5 extra HP per turn. | +1 visibility range; Double movement in forests; Double movement in jungle. | Ignores terrain movement costs; +1 movement. |
| Explorer | 750 | Heals 10 extra HP per turn. | +1 visibility range; +1 movement. | Can use enemy roads, but not railroads; Units on the same tile heal 20 extra HP per turn. |
| Warrior | 100 | +15% city defense. | +25% against melee units. | +30% combat strength; Heals 15 extra HP per turn. |
| Quechua Warrior | 53 | +15% against archery units. | +25% city attack. | +30% combat strength; Immune to first strikes. |
| Swordsman | 300 | +15% city attack. | +25% against melee units. | +1 movement; Can attack multiple times per turn. |
| Aztec Jaguar | 126 | +15% jungle attack. | Double movement in forests; Double movement in jungle. | Heals 25 extra HP per turn; Can heal while moving. |
| Celtic Gallic Warrior | 300 | +15% hills defense. | Double movement in hills. | +40% hills attack; +40% withdrawal chance. |
| Legion | 300 | +10% combat strength. | Units on the same tile heal 15 extra HP per turn. | +35% combat strength; Immune to first strikes. |
| Axeman | 126 | +15% against melee units. | +25% forest attack; +25% forest defense. | +30% combat strength; Immune to first strikes. |
| Greek Phalanx | 126 | +15% against melee units. | +25% hills defense; +1 first strikes. | +40% against mounted units; +25% against melee units. |
| Sumerian Vulture | 126 | +15% city attack. | Heals 15 extra HP per turn. | Can attack multiple times per turn; +1 movement. |
| Native America Dog Soldier | 126 | +15% against melee units. | Units on the same tile heal 15 extra HP per turn. | +40% against melee units; +2 first strikes. |
| Maceman | 1200 | +15% city attack. | +25% against melee units; +25% against gunpowder units. | +35% combat strength; Immune to first strikes. |
| Japan Samurai | 1200 | +15% against melee units. | +1 first strikes; +20% city attack. | +2 first strikes; Heals 20 extra HP per turn. |
| Berserker | 1200 | +15% city attack. | No river attack penalty; Heals 10 extra HP per turn. | +1 movement; Can attack multiple times per turn. |
| Spearman | 42 | +20% against mounted units. | +25% hills defense; +1 first strikes. | +35% combat strength; +40% against mounted units. |
| Zulu Impi | 42 | +15% withdrawal chance. | Heals 15 extra HP per turn; Can heal while moving. | Can use enemy roads, but not railroads; +1 movement. |
| Maya Holkan | 126 | +15% against melee units. | +25% jungle defense; +1 first strikes. | +35% combat strength; Double movement in jungle. |
| Pikeman | 1500 | +20% against mounted units. | +25% against melee units. | +35% combat strength; +2 first strikes. |
| Holy Roman Landsknecht | 1500 | +15% against melee units. | +25% hills defense; +1 first strikes. | +35% against melee units; +35% against mounted units; Units on the same tile heal 15 extra HP per turn. |
| Musketman | 1500 | +15% city defense. | +1 first strikes; +20% city attack. | +35% combat strength; Can heal while moving. |
| French Musketeer | 1500 | +15% withdrawal chance. | No river attack penalty; Heals 15 extra HP per turn. | Can use enemy roads, but not railroads; Can attack multiple times per turn. |
| Janissary | 1500 | +15% against archery units. | +25% city attack; Immune to first strikes. | +35% against melee units; +35% against archery units; +35% against mounted units. |
| Ethiopian Oromo Warrior | 1500 | +15% hills defense. | +1 first strikes; Heals 10 extra HP per turn. | +2 first strikes; +30% city defense. |
| Rifleman | 2208 | +15% against gunpowder units. | +25% city defense; +25% hills defense. | +35% combat strength; Heals 15 extra HP per turn. |
| English Redcoat | 2208 | +15% against gunpowder units. | No amphibious attack penalty; No river attack penalty. | +35% combat strength; +2 first strikes. |
| Grenadier | 2116 | +15% city attack. | +25% against gunpowder units. | +40% city attack; Immune to first strikes. |
| At Infantry | 3220 | +20% against armored units. | +25% hills defense; +1 first strikes. | +40% against armored units; +30% combat strength. |
| Infantry | 3680 | +15% city attack. | +25% against gunpowder units. | +1 movement; Can attack multiple times per turn. |
| Marine | 4140 | +15% city attack. | +1 first strikes; +20% against gunpowder units. | +40% city attack; Can heal while moving; Heals 20 extra HP per turn. |
| American Navy Seal | 4140 | Heals 10 extra HP per turn. | +1 first strikes; +20% city attack. | +1 movement; Can attack multiple times per turn. |
| Paratrooper | 2944 | +15% hills defense. | +25% city attack; Heals 10 extra HP per turn. | Can use enemy roads, but not railroads; +1 movement. |
| Mechanized Infantry | 4564 | +15% against armored units. | Units on the same tile heal 15 extra HP per turn. | +1 movement; Heals 20 extra HP per turn. |
| Archer | 63 | +15% city defense. | +20% hills defense; +1 first strikes. | +35% combat strength; +2 first strikes. |
| Mali Skirmisher | 63 | +15% hills defense. | +1 first strikes; +20% withdrawal chance. | +1 movement; +35% combat strength. |
| Asharittu Bowman | 63 | +15% collateral damage. | +2 collateral targets. | +20% collateral damage limit; +40% withdrawal chance. |
| Longbowman | 1125 | +15% city defense. | +25% hills defense; +1 first strikes. | +35% combat strength; Units on the same tile heal 20 extra HP per turn. |
| Crossbowman | 1125 | +15% against melee units. | +25% city defense; +1 first strikes. | +35% combat strength; +40% against melee units. |
| China Chokonu | 1125 | +15% against melee units. | +2 collateral targets. | +1 movement; Can attack multiple times per turn. |
| Chariot | 63 | +15% withdrawal chance. | +25% against archery units. | +1 movement; +30% combat strength. |
| Egypt Warchariot | 63 | +15% against archery units. | +25% withdrawal chance. | +1 movement; +35% combat strength. |
| Persia Immortal | 42 | +15% attack against Archers. | Heals 15 extra HP per turn; Immune to first strikes. | +40% city attack; Units on the same tile heal 15 extra HP per turn. |
| Horse Archer | 375 | +15% withdrawal chance. | +25% against archery units. | Can use enemy roads, but not railroads; +30% combat strength. |
| Numidian Cavalry | 375 | +15% against melee units. | +25% withdrawal chance. | +1 movement; Heals 20 extra HP per turn; Can heal while moving. |
| Mongol Keshik | 1500 | +15% withdrawal chance. | No river attack penalty; Heals 15 extra HP per turn. | Can use enemy roads, but not railroads; Can attack multiple times per turn. |
| Knight | 1500 | +15% city attack. | +25% withdrawal chance. | +1 movement; Can attack multiple times per turn. |
| Arabia Camelarcher | 1500 | Heals 10 extra HP per turn. | +25% withdrawal chance. | Heals 15 extra HP per turn; Can heal while moving. |
| Byzantine Cataphract | 1125 | +15% city attack. | +25% withdrawal chance. | +35% combat strength; Can attack multiple times per turn. |
| Spanish Conquistador | 1500 | +15% against melee units. | +25% hills defense; +25% forest defense. | +35% combat strength; Units on the same tile heal 20 extra HP per turn. |
| Cuirassier | 1656 | +15% withdrawal chance. | +25% against gunpowder units. | +1 movement; +35% combat strength. |
| Cavalry | 2208 | +20% against siege units. | +25% withdrawal chance. | +1 movement; Can attack multiple times per turn. |
| Russia Cossack | 2208 | +15% against mounted units. | +25% withdrawal chance. | +1 movement; +40% against mounted units. |
| War Elephant | 450 | +15% against melee units. | +25% city attack. | +40% collateral damage; +4 collateral targets; +50% collateral damage limit. |
| Khmer Ballista Elephant | 450 | +15% against mounted units. | +25% withdrawal chance. | +40% against mounted units; Immune to first strikes. |
| Tank | 4140 | +15% city attack. | +25% withdrawal chance. | Can use enemy roads, but not railroads; +1 movement. |
| German Panzer | 4140 | +15% attack against Riflemen and Infantry. | Heals 15 extra HP per turn. | +1 movement; Can heal while moving. |
| Main Battle Tank | 4122 | +15% against armored units. | +25% city attack. | +1 movement; Can heal while moving; Heals 20 extra HP per turn. |
| Catapult | 375 | +8% city bombardment. | +2 collateral targets. | +20% collateral damage limit; +40% withdrawal chance. |
| Korean Hwacha | 375 | +15% against melee units. | +2 collateral targets. | +40% against melee units; +20% collateral damage limit. |
| Trebuchet | 1500 | +15% city attack. | +10% city bombardment. | +40% city attack; +3 collateral targets. |
| Cannon | 1500 | +8% city bombardment. | +2 collateral targets. | +20% collateral damage limit; +40% withdrawal chance. |
| Machine Gun | 3220 | +15% against gunpowder units. | +25% hills defense; +1 first strikes. | +35% combat strength; Units on the same tile heal 20 extra HP per turn. |
| Artillery | 3220 | +8% city bombardment. | +2 collateral targets. | +1 movement; +20% collateral damage limit. |
| Mobile Artillery | 4122 | +8% city bombardment. | +2 collateral targets. | Can use enemy roads, but not railroads; +20% collateral damage limit. |
| Trireme | 675 | +15% combat strength. | +1 first strikes; +20% withdrawal chance. | +2 movement; +30% combat strength. |
| Caravel | 1200 | Heals 10 extra HP per turn. | +1 visibility range; +1 movement. | +2 movement; +40% withdrawal chance. |
| Portugal Carrack | 1200 | +1 visibility range; Heals 5 extra HP per turn. | +1 cargo capacity. | +2 movement; Can heal while moving; Heals 20 extra HP per turn. |
| Netherlands Oostindievaarder | 1472 | +15% combat strength. | +1 cargo capacity. | +2 movement; Can attack twice per turn. |
| Privateer | 1656 | +15% withdrawal chance. | +1 movement; +20% combat strength. | Can heal while moving; Heals 25 extra HP per turn. |
| Frigate | 1656 | +8% city bombardment. | +20% combat strength; +1 first strikes. | +2 movement; Can attack twice per turn. |
| Ship Of The Line | 2116 | +15% combat strength. | +1 first strikes; +10% city bombardment. | +35% combat strength; Can attack twice per turn. |
| Ironclad | 2484 | Heals 10 extra HP per turn. | +20% combat strength; +1 first strikes. | +2 movement; Can heal while moving. |
| Destroyer | 3404 | +15% combat strength. | +1 visibility range; +1 first strikes. | +2 movement; Can attack twice per turn. |
| Battleship | 4140 | +8% city bombardment. | +2 collateral targets. | Can attack twice per turn; +20% collateral damage limit. |
| Missile Cruiser | 4564 | Heals 10 extra HP per turn. | +1 visibility range; +20% combat strength. | Can attack twice per turn; Units on the same tile heal 20 extra HP per turn. |
| Stealth Destroyer | 4564 | +15% withdrawal chance. | +20% combat strength; +1 first strikes. | +2 movement; Can heal while moving; Heals 20 extra HP per turn. |
| Submarine | 3165 | +15% withdrawal chance. | +25% combat strength. | +2 movement; +15% withdrawal chance. |
| Attack Submarine | 3404 | +15% combat strength. | +1 visibility range; +20% withdrawal chance. | +2 movement; Can attack twice per turn. |
| Autonomous Combat Vehicle | 47840 | +15% city defense. | +25% against gunpowder units. | +35% combat strength; Heals 20 extra HP per turn. |
| Autonomous Battle Tank | 80960 | +15% city attack. | +25% against armored units. | Can use enemy roads, but not railroads; +1 movement. |
| War Galley | 1125 | +15% combat strength. | +1 first strikes; Heals 10 extra HP per turn. | +1 movement; Can attack twice per turn. |
| Arctic hunter | 100 | +25% against animals. | +1 visibility range; +20% hills defense. | Double movement in hills; +35% combat strength. |
| Woodland Warrior | 100 | +15% forest defense. | Double movement in forests. | +40% forest attack; Units on the same tile heal 20 extra HP per turn. |
