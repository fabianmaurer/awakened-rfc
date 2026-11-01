# Military unit mastery

Military fighting units have three cumulative, unit-specific mastery levels.
Each level costs twice the previous one: base, 2x base, 4x base. The base is
8 times the unit's base XML production cost: levels I, II and III therefore
start at 8x, 16x and 32x base production. Normal research modifiers still apply.
This is calibrated to roughly 20x the displayed production cost for level I
under the reported game settings (13-hammer Warrior: about 255 research).
It is not a fixed final ratio across difficulties, teams, eras or other cost
modifiers. City and civilization production bonuses do not change the XML base.
Reward strength does not change the multiplier. Research unlocks with all unit technology
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
| Scout | 120 | +1 visibility range. | Double movement in forests; Double movement in jungle. | Heals 15 extra HP per turn; Immune to first strikes. |
| Explorer | 320 | +1 movement. | Units on the same tile heal 15 extra HP per turn. | Ignores terrain movement costs; Heals 15 extra HP per turn. |
| Warrior | 120 | +30% city defense. | +30% against melee units. | Heals 15 extra HP per turn; Can heal while moving. |
| Quechua Warrior | 280 | +50% against archery units. | Double movement in hills. | +40% city attack; Heals 15 extra HP per turn. |
| Swordsman | 320 | +30% city attack. | Immune to first strikes. | Can attack multiple times per turn; +1 movement. |
| Aztec Jaguar | 280 | Double movement in jungle. | +50% jungle attack; +50% forest attack. | Can heal while moving; Heals 20 extra HP per turn. |
| Celtic Gallic Warrior | 320 | +50% hills attack. | Double movement in hills. | +40% withdrawal chance; +30% hills defense. |
| Legion | 360 | +40% city attack. | Units on the same tile heal 15 extra HP per turn. | Ignores building defenses. |
| Axeman | 280 | +35% against melee units. | +40% forest attack. | +30% collateral damage; +3 collateral targets; +40% collateral damage limit. |
| Greek Phalanx | 280 | +50% against mounted units. | +2 first strikes. | +40% against melee units; +30% hills defense. |
| Sumerian Vulture | 280 | +40% against melee units. | +40% city attack. | Immune to first strikes; Heals 15 extra HP per turn. |
| Native America Dog Soldier | 280 | +50% forest defense. | Double movement in forests. | +40% against melee units; Units on the same tile heal 15 extra HP per turn. |
| Maceman | 560 | +30% city attack. | +25% against armored units; +25% against gunpowder units. | +2 first strikes. |
| Japan Samurai | 560 | +2 first strikes. | +40% city attack. | Can attack multiple times per turn; +1 movement. |
| Berserker | 560 | +40% city attack. | No river attack penalty; +1 movement. | Can attack multiple times per turn. |
| Spearman | 280 | +50% against mounted units. | +40% hills defense. | +2 first strikes. |
| Zulu Impi | 280 | +40% withdrawal chance. | Can use enemy roads. | Units on the same tile heal 20 extra HP per turn; Can heal while moving. |
| Maya Holkan | 280 | +50% jungle defense. | Double movement in jungle. | +50% against mounted units; +2 first strikes. |
| Pikeman | 480 | +50% against mounted units. | +30% against melee units. | Immune to first strikes; Heals 15 extra HP per turn. |
| Holy Roman Landsknecht | 480 | +50% against melee units. | +50% against mounted units. | +2 first strikes; Heals 15 extra HP per turn. |
| Musketman | 640 | +30% city defense. | +2 first strikes. | No amphibious attack penalty; No river attack penalty. |
| French Musketeer | 640 | +35% withdrawal chance. | Can use enemy roads. | Can attack multiple times per turn. |
| Janissary | 640 | +30% against melee units; +30% against archery units; +30% against mounted units. | +40% city attack. | +2 first strikes. |
| Ethiopian Oromo Warrior | 640 | +2 first strikes. | +50% hills defense. | Double movement in hills; Heals 20 extra HP per turn. |
| Rifleman | 880 | +25% against gunpowder units. | +40% hills defense. | Can heal while moving; Heals 15 extra HP per turn. |
| English Redcoat | 880 | +40% against gunpowder units. | No amphibious attack penalty; No river attack penalty. | +2 first strikes; +30% city defense. |
| Grenadier | 800 | +35% city attack. | +35% collateral damage; +3 collateral targets; +50% collateral damage limit. | Immune to first strikes. |
| At Infantry | 960 | +50% against armored units. | +40% hills defense. | +40% withdrawal chance. |
| Infantry | 1120 | +30% city attack. | Units on the same tile heal 15 extra HP per turn. | Can attack multiple times per turn; +1 movement. |
| Marine | 1280 | +35% city attack. | +2 first strikes. | Can heal while moving; Heals 20 extra HP per turn. |
| American Navy Seal | 1280 | +2 first strikes. | Can use enemy roads. | Can attack multiple times per turn; +1 movement. |
| Paratrooper | 1280 | +40% hills defense. | Can use enemy roads. | +35% city attack; Immune to first strikes. |
| Mechanized Infantry | 1600 | +35% against armored units. | Units on the same tile heal 20 extra HP per turn. | +1 movement; Can use enemy roads. |
| Archer | 280 | +40% city defense. | +40% hills defense. | +2 first strikes. |
| Mali Skirmisher | 280 | +40% withdrawal chance. | +1 movement. | +50% hills defense; +2 first strikes. |
| Asharittu Bowman | 200 | +50% against melee units. | +40% city defense. | +2 first strikes; Units on the same tile heal 15 extra HP per turn. |
| Longbowman | 520 | +40% city defense. | +2 first strikes. | Units on the same tile heal 15 extra HP per turn; Heals 15 extra HP per turn. |
| Crossbowman | 560 | +40% against melee units. | +40% hills attack. | +2 first strikes. |
| China Chokonu | 480 | +3 collateral targets. | +20% collateral damage limit. | Can attack multiple times per turn; +1 movement. |
| Chariot | 240 | +30% withdrawal chance. | +40% against archery units. | +1 movement; No river attack penalty. |
| Egypt Warchariot | 240 | +50% against archery units. | +40% withdrawal chance. | +1 movement; Can attack multiple times per turn. |
| Persia Immortal | 200 | +40% city attack. | Units on the same tile heal 15 extra HP per turn. | Can heal while moving; Heals 25 extra HP per turn. |
| Horse Archer | 400 | +30% withdrawal chance. | +2 first strikes. | Can use enemy roads. |
| Numidian Cavalry | 320 | +40% against melee units. | +40% withdrawal chance. | Can use enemy roads; +1 movement. |
| Mongol Keshik | 720 | +40% withdrawal chance. | Can use enemy roads. | Can attack multiple times per turn; +1 movement. |
| Knight | 720 | +30% city attack. | +30% withdrawal chance. | Can attack multiple times per turn; +1 movement. |
| Arabia Camelarcher | 720 | +40% against mounted units. | Heals 25 extra HP per turn; Can heal while moving. | Can attack multiple times per turn; +1 movement. |
| Byzantine Cataphract | 720 | +40% against melee units. | Immune to first strikes. | +40% city attack; +35% withdrawal chance. |
| Spanish Conquistador | 800 | +35% against gunpowder units. | No amphibious attack penalty; No river attack penalty. | +40% city attack; Units on the same tile heal 15 extra HP per turn. |
| Cuirassier | 800 | +30% against gunpowder units. | +35% withdrawal chance. | +1 movement; Immune to first strikes. |
| Cavalry | 960 | +50% against siege units. | Can use enemy roads. | Can attack multiple times per turn; +1 movement. |
| Russia Cossack | 960 | +50% against mounted units. | +40% withdrawal chance. | Can attack multiple times per turn; +1 movement. |
| War Elephant | 480 | +35% against melee units. | +35% city attack. | +40% collateral damage; +4 collateral targets; +50% collateral damage limit. |
| Khmer Ballista Elephant | 480 | +50% against mounted units. | +40% collateral damage; +4 collateral targets; +50% collateral damage limit. | Immune to first strikes. |
| Tank | 1440 | +35% city attack. | +35% withdrawal chance. | +1 movement; Can use enemy roads. |
| German Panzer | 1440 | +50% against armored units. | +40% withdrawal chance. | +1 movement; Can use enemy roads. |
| Main Battle Tank | 1920 | +35% against armored units. | Immune to first strikes. | +1 movement; Can heal while moving. |
| Catapult | 320 | +20% city bombardment. | +3 collateral targets. | +40% withdrawal chance. |
| Korean Hwacha | 320 | +50% against melee units. | +4 collateral targets. | +25% collateral damage limit; +35% withdrawal chance. |
| Trebuchet | 640 | +50% city attack. | +25% city bombardment. | +20% collateral damage limit; +2 collateral targets. |
| Cannon | 800 | +30% collateral damage. | +30% city bombardment. | +40% withdrawal chance. |
| Machine Gun | 1000 | +35% against gunpowder units. | +3 first strikes. | Units on the same tile heal 20 extra HP per turn. |
| Artillery | 1200 | +4 collateral targets. | +20% collateral damage limit. | +1 movement. |
| Mobile Artillery | 1600 | +40% city bombardment. | +4 collateral targets. | +50% withdrawal chance; Can use enemy roads. |
| Trireme | 400 | +2 first strikes. | +40% withdrawal chance. | +2 movement. |
| Caravel | 480 | +2 visibility range. | +2 movement. | +50% withdrawal chance. |
| Portugal Carrack | 480 | Heals 20 extra HP per turn; Can heal while moving. | +2 visibility range. | +2 movement; +35% withdrawal chance. |
| Netherlands Oostindievaarder | 640 | +2 first strikes. | Heals 25 extra HP per turn; Can heal while moving. | +2 movement. |
| Privateer | 640 | +40% withdrawal chance. | +2 movement. | Can heal while moving; Heals 25 extra HP per turn. |
| Frigate | 720 | +25% city bombardment. | +2 first strikes. | +2 movement. |
| Ship Of The Line | 960 | Immune to first strikes. | +30% city bombardment. | +3 first strikes. |
| Ironclad | 800 | +25% city bombardment; Heals 15 extra HP per turn. | Immune to first strikes. | +2 movement. |
| Destroyer | 1600 | +2 visibility range. | +3 first strikes. | +2 movement; +30% withdrawal chance. |
| Battleship | 1800 | +40% city bombardment. | +3 collateral targets; +20% collateral damage limit. | Can attack multiple times per turn; +1 movement. |
| Missile Cruiser | 2080 | Units on the same tile heal 20 extra HP per turn; Heals 15 extra HP per turn. | +2 visibility range. | Can attack multiple times per turn; +2 movement. |
| Stealth Destroyer | 1760 | +3 first strikes. | +45% withdrawal chance. | +2 movement; Can heal while moving. |
| Submarine | 1200 | +40% withdrawal chance. | +3 first strikes. | +2 movement. |
| Attack Submarine | 1600 | +3 first strikes. | Immune to first strikes; Heals 20 extra HP per turn. | +2 movement; +30% withdrawal chance. |
| Autonomous Combat Vehicle | 2560 | +40% city defense. | Can heal while moving; Heals 20 extra HP per turn. | +3 first strikes. |
| Autonomous Battle Tank | 3360 | +40% city attack. | +40% against armored units. | +1 movement; Can use enemy roads. |
| War Galley | 480 | +2 first strikes. | Heals 20 extra HP per turn; Can heal while moving. | Can attack multiple times per turn. |
| Arctic hunter | 240 | +1 visibility range; +50% against animals. | Double movement in hills. | +2 first strikes; Heals 20 extra HP per turn. |
| Woodland Warrior | 120 | +50% forest attack; +50% forest defense. | Double movement in forests. | Units on the same tile heal 15 extra HP per turn; +2 first strikes. |
