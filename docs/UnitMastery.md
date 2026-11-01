# Military unit mastery

Military fighting units have three cumulative, unit-specific mastery levels.
Each level costs twice the previous one: base, 2x base, 4x base. The base is
20 times the unit's base XML production cost: levels I, II and III therefore
cost 20x, 40x and 80x production. City and civilization production bonuses do
not change this base. Reward strength does not change the multiplier.
Normal research modifiers apply. Research unlocks with all unit technology
requirements and ends at III or when an upgrade successor is technologically
available, independently of resources/buildings. Unique units use their own
tracks; civilizations cannot research another civilization's replacement.

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
| Scout | 300 | +1 visibility range. | Double movement in forests; Double movement in jungle. | Heals 15 extra HP per turn; Immune to first strikes. |
| Explorer | 800 | +1 movement. | Units on the same tile heal 15 extra HP per turn. | Ignores terrain movement costs; Heals 15 extra HP per turn. |
| Warrior | 300 | +30% city defense. | +30% against melee units. | Heals 15 extra HP per turn; Can heal while moving. |
| Quechua Warrior | 700 | +50% against archery units. | Double movement in hills. | +40% city attack; Heals 15 extra HP per turn. |
| Swordsman | 800 | +30% city attack. | Immune to first strikes. | Can attack multiple times per turn; +1 movement. |
| Aztec Jaguar | 700 | Double movement in jungle. | +50% jungle attack; +50% forest attack. | Can heal while moving; Heals 20 extra HP per turn. |
| Celtic Gallic Warrior | 800 | +50% hills attack. | Double movement in hills. | +40% withdrawal chance; +30% hills defense. |
| Legion | 900 | +40% city attack. | Units on the same tile heal 15 extra HP per turn. | Ignores building defenses. |
| Axeman | 700 | +35% against melee units. | +40% forest attack. | +30% collateral damage; +3 collateral targets; +40% collateral damage limit. |
| Greek Phalanx | 700 | +50% against mounted units. | +2 first strikes. | +40% against melee units; +30% hills defense. |
| Sumerian Vulture | 700 | +40% against melee units. | +40% city attack. | Immune to first strikes; Heals 15 extra HP per turn. |
| Native America Dog Soldier | 700 | +50% forest defense. | Double movement in forests. | +40% against melee units; Units on the same tile heal 15 extra HP per turn. |
| Maceman | 1400 | +30% city attack. | +25% against armored units; +25% against gunpowder units. | +2 first strikes. |
| Japan Samurai | 1400 | +2 first strikes. | +40% city attack. | Can attack multiple times per turn; +1 movement. |
| Berserker | 1400 | +40% city attack. | No river attack penalty; +1 movement. | Can attack multiple times per turn. |
| Spearman | 700 | +50% against mounted units. | +40% hills defense. | +2 first strikes. |
| Zulu Impi | 700 | +40% withdrawal chance. | Can use enemy roads. | Units on the same tile heal 20 extra HP per turn; Can heal while moving. |
| Maya Holkan | 700 | +50% jungle defense. | Double movement in jungle. | +50% against mounted units; +2 first strikes. |
| Pikeman | 1200 | +50% against mounted units. | +30% against melee units. | Immune to first strikes; Heals 15 extra HP per turn. |
| Holy Roman Landsknecht | 1200 | +50% against melee units. | +50% against mounted units. | +2 first strikes; Heals 15 extra HP per turn. |
| Musketman | 1600 | +30% city defense. | +2 first strikes. | No amphibious attack penalty; No river attack penalty. |
| French Musketeer | 1600 | +35% withdrawal chance. | Can use enemy roads. | Can attack multiple times per turn. |
| Janissary | 1600 | +30% against melee units; +30% against archery units; +30% against mounted units. | +40% city attack. | +2 first strikes. |
| Ethiopian Oromo Warrior | 1600 | +2 first strikes. | +50% hills defense. | Double movement in hills; Heals 20 extra HP per turn. |
| Rifleman | 2200 | +25% against gunpowder units. | +40% hills defense. | Can heal while moving; Heals 15 extra HP per turn. |
| English Redcoat | 2200 | +40% against gunpowder units. | No amphibious attack penalty; No river attack penalty. | +2 first strikes; +30% city defense. |
| Grenadier | 2000 | +35% city attack. | +35% collateral damage; +3 collateral targets; +50% collateral damage limit. | Immune to first strikes. |
| At Infantry | 2400 | +50% against armored units. | +40% hills defense. | +40% withdrawal chance. |
| Infantry | 2800 | +30% city attack. | Units on the same tile heal 15 extra HP per turn. | Can attack multiple times per turn; +1 movement. |
| Marine | 3200 | +35% city attack. | +2 first strikes. | Can heal while moving; Heals 20 extra HP per turn. |
| American Navy Seal | 3200 | +2 first strikes. | Can use enemy roads. | Can attack multiple times per turn; +1 movement. |
| Paratrooper | 3200 | +40% hills defense. | Can use enemy roads. | +35% city attack; Immune to first strikes. |
| Mechanized Infantry | 4000 | +35% against armored units. | Units on the same tile heal 20 extra HP per turn. | +1 movement; Can use enemy roads. |
| Archer | 700 | +40% city defense. | +40% hills defense. | +2 first strikes. |
| Mali Skirmisher | 700 | +40% withdrawal chance. | +1 movement. | +50% hills defense; +2 first strikes. |
| Asharittu Bowman | 500 | +50% against melee units. | +40% city defense. | +2 first strikes; Units on the same tile heal 15 extra HP per turn. |
| Longbowman | 1300 | +40% city defense. | +2 first strikes. | Units on the same tile heal 15 extra HP per turn; Heals 15 extra HP per turn. |
| Crossbowman | 1400 | +40% against melee units. | +40% hills attack. | +2 first strikes. |
| China Chokonu | 1200 | +3 collateral targets. | +20% collateral damage limit. | Can attack multiple times per turn; +1 movement. |
| Chariot | 600 | +30% withdrawal chance. | +40% against archery units. | +1 movement; No river attack penalty. |
| Egypt Warchariot | 600 | +50% against archery units. | +40% withdrawal chance. | +1 movement; Can attack multiple times per turn. |
| Persia Immortal | 500 | +40% city attack. | Units on the same tile heal 15 extra HP per turn. | Can heal while moving; Heals 25 extra HP per turn. |
| Horse Archer | 1000 | +30% withdrawal chance. | +2 first strikes. | Can use enemy roads. |
| Numidian Cavalry | 800 | +40% against melee units. | +40% withdrawal chance. | Can use enemy roads; +1 movement. |
| Mongol Keshik | 1800 | +40% withdrawal chance. | Can use enemy roads. | Can attack multiple times per turn; +1 movement. |
| Knight | 1800 | +30% city attack. | +30% withdrawal chance. | Can attack multiple times per turn; +1 movement. |
| Arabia Camelarcher | 1800 | +40% against mounted units. | Heals 25 extra HP per turn; Can heal while moving. | Can attack multiple times per turn; +1 movement. |
| Byzantine Cataphract | 1800 | +40% against melee units. | Immune to first strikes. | +40% city attack; +35% withdrawal chance. |
| Spanish Conquistador | 2000 | +35% against gunpowder units. | No amphibious attack penalty; No river attack penalty. | +40% city attack; Units on the same tile heal 15 extra HP per turn. |
| Cuirassier | 2000 | +30% against gunpowder units. | +35% withdrawal chance. | +1 movement; Immune to first strikes. |
| Cavalry | 2400 | +50% against siege units. | Can use enemy roads. | Can attack multiple times per turn; +1 movement. |
| Russia Cossack | 2400 | +50% against mounted units. | +40% withdrawal chance. | Can attack multiple times per turn; +1 movement. |
| War Elephant | 1200 | +35% against melee units. | +35% city attack. | +40% collateral damage; +4 collateral targets; +50% collateral damage limit. |
| Khmer Ballista Elephant | 1200 | +50% against mounted units. | +40% collateral damage; +4 collateral targets; +50% collateral damage limit. | Immune to first strikes. |
| Tank | 3600 | +35% city attack. | +35% withdrawal chance. | +1 movement; Can use enemy roads. |
| German Panzer | 3600 | +50% against armored units. | +40% withdrawal chance. | +1 movement; Can use enemy roads. |
| Main Battle Tank | 4800 | +35% against armored units. | Immune to first strikes. | +1 movement; Can heal while moving. |
| Catapult | 800 | +20% city bombardment. | +3 collateral targets. | +40% withdrawal chance. |
| Korean Hwacha | 800 | +50% against melee units. | +4 collateral targets. | +25% collateral damage limit; +35% withdrawal chance. |
| Trebuchet | 1600 | +50% city attack. | +25% city bombardment. | +20% collateral damage limit; +2 collateral targets. |
| Cannon | 2000 | +30% collateral damage. | +30% city bombardment. | +40% withdrawal chance. |
| Machine Gun | 2500 | +35% against gunpowder units. | +3 first strikes. | Units on the same tile heal 20 extra HP per turn. |
| Artillery | 3000 | +4 collateral targets. | +20% collateral damage limit. | +1 movement. |
| Mobile Artillery | 4000 | +40% city bombardment. | +4 collateral targets. | +50% withdrawal chance; Can use enemy roads. |
| Trireme | 1000 | +2 first strikes. | +40% withdrawal chance. | +2 movement. |
| Caravel | 1200 | +2 visibility range. | +2 movement. | +50% withdrawal chance. |
| Portugal Carrack | 1200 | Heals 20 extra HP per turn; Can heal while moving. | +2 visibility range. | +2 movement; +35% withdrawal chance. |
| Netherlands Oostindievaarder | 1600 | +2 first strikes. | Heals 25 extra HP per turn; Can heal while moving. | +2 movement. |
| Privateer | 1600 | +40% withdrawal chance. | +2 movement. | Can heal while moving; Heals 25 extra HP per turn. |
| Frigate | 1800 | +25% city bombardment. | +2 first strikes. | +2 movement. |
| Ship Of The Line | 2400 | Immune to first strikes. | +30% city bombardment. | +3 first strikes. |
| Ironclad | 2000 | +25% city bombardment; Heals 15 extra HP per turn. | Immune to first strikes. | +2 movement. |
| Destroyer | 4000 | +2 visibility range. | +3 first strikes. | +2 movement; +30% withdrawal chance. |
| Battleship | 4500 | +40% city bombardment. | +3 collateral targets; +20% collateral damage limit. | Can attack multiple times per turn; +1 movement. |
| Missile Cruiser | 5200 | Units on the same tile heal 20 extra HP per turn; Heals 15 extra HP per turn. | +2 visibility range. | Can attack multiple times per turn; +2 movement. |
| Stealth Destroyer | 4400 | +3 first strikes. | +45% withdrawal chance. | +2 movement; Can heal while moving. |
| Submarine | 3000 | +40% withdrawal chance. | +3 first strikes. | +2 movement. |
| Attack Submarine | 4000 | +3 first strikes. | Immune to first strikes; Heals 20 extra HP per turn. | +2 movement; +30% withdrawal chance. |
| Autonomous Combat Vehicle | 6400 | +40% city defense. | Can heal while moving; Heals 20 extra HP per turn. | +3 first strikes. |
| Autonomous Battle Tank | 8400 | +40% city attack. | +40% against armored units. | +1 movement; Can use enemy roads. |
| War Galley | 1200 | +2 first strikes. | Heals 20 extra HP per turn; Can heal while moving. | Can attack multiple times per turn. |
| Arctic hunter | 600 | +1 visibility range; +50% against animals. | Double movement in hills. | +2 first strikes; Heals 20 extra HP per turn. |
| Woodland Warrior | 300 | +50% forest attack; +50% forest defense. | Double movement in forests. | Units on the same tile heal 15 extra HP per turn; +2 first strikes. |
