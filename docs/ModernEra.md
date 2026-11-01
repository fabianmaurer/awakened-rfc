# Modern-era core changes

These rules apply to new games. The welfare-state policy proposal is not part of
this implementation.

## Climate and warfare

The global-warming turn routine and its invocation are removed. Industrial
unhealthiness, terrain, forests and city health retain their own existing rules;
there is no longer a global warming roll that turns worked land into desert.

Aircraft, airships, helicopters, guided missiles, tactical nuclear weapons and
ICBMs are unavailable. Carriers, SAM infantry, mobile SAM, airports, bomb shelters,
the Manhattan Project and SDI are retired as well. Air-only promotions and event
requirements are disabled, naval air/missile cargo and missile-carrier AI roles
are removed, and obsolete unit/building options are filtered from the technology
screen and Civilopedia. Cavalry now upgrades to tanks; ordinary infantry and
machine-gun paths to mechanized infantry remain.

Non-air naval units, including missile cruisers used as surface combatants,
stealth destroyers, and attack submarines used for reconnaissance/spy transport,
remain. Their unrelated capabilities are retained. Space research and civil
nuclear power remain available; their technologies no longer require retired
aviation technologies.

Retired XML infos remain in their original slots because RFC uses numeric IDs in
Python and DLL constants. They are disabled in normal gameplay rather than
renumbering every later unit and technology. This is not a save migration or a
promise of old-save compatibility. WorldBuilder/debug creation is outside normal
production rules.

## Repeatable research

| Field | Prerequisite | Base cost | Per completion |
| --- | --- | ---: | --- |
| Environmental Quality | Ecology | 4,416 | +1 happiness in every city |
| Medical Progress | Genetics | 4,784 | +1 health in every city |
| Military Research | Computers | 5,888 | +1 percentage point combat strength for land/naval units |

The original combined Future Tech is disabled. Each field's cost increases by
35% for every completion of that field, independently of the other two. Integer
rounding goes upward at each step. Standard game-speed, difficulty, team, empire
modifiers still apply. Fixed Modern/Future base costs include the former 92%
factor and 20% late-game discount (73.6% combined); calendar thresholds no longer
reprice research.
Costs have an engine arithmetic safety
ceiling of 2,000,000 beakers. Growth uses deterministic 64-bit integer arithmetic.

Military Research stops at level 15, giving at most +15 percentage points. The
research queue is cleared at that limit, and players/AI cannot select level 16.
The combat bonus is computed from the owning team's research count, applies to
both attack and defense, works for existing and newly trained units, and is
included in the engine's strength/odds calculations. It creates no promotions or
per-unit stored state. Health/happiness use the native repeatable-tech processing.

AI research valuation now recognizes the happiness and military benefits and
does not apply the old tenfold repeat-tech penalty. The ordinary cost comparison
still allows long-term research to compete with repeated improvements.

Military units also have three unit-specific mastery levels, separate from
global Military Research. See [UnitMastery.md](UnitMastery.md) for costs,
retirement rules and the complete reward table, including unique units.

## AI and automation branch

The three repeatable fields share column 21. Everything to their right belongs
to the AI/automation branch. Digital Administration now also requires Fiber
Optics, and Machine Learning follows Digital Administration. No repeatable
technology must be completed to enter this branch. The original tree height is
retained.

| Technology | Prerequisites | Base cost | Building unlocked |
| --- | --- | ---: | --- |
| Digital Administration | Computers, Fiber Optics | 11,776 | Administration centre: -20% city maintenance |
| Machine Learning | Digital Administration | 17,664 | ML laboratory: +25% research |
| AI-Assisted Services | Machine Learning | 26,496 | Services centre: +15% gold, +2 health, +1 happiness |
| Networked Production | Machine Learning, Robotics | 36,800 | Networked factory: +25% production |
| General AI | AI-Assisted Services, Networked Production | 58,880 | General AI research centre: +40% research |
| Full Automation | General AI, Fusion | 103,040 | Automated complex: +50% production, +25% gold |
| Autonomous Systems | Networked Production | 47,840 | Autonomous Combat Vehicle |
| Autonomous Warfare | Autonomous Systems, General AI | 80,960 | Autonomous Battle Tank |

Buildings cost 400, 500, 650, 850, 1,100 and 1,800 production respectively. Each
city can construct one of each. They reuse suitable existing building art and introduce
no welfare spending levels, demographic model or new victory condition.

These eight technologies and the three repeat fields cannot be traded. The
eight AI/automation technologies are also excluded from the old worldwide tech-owner
discount, so other countries discovering them does not erase the intended
investment. Espionage retains its normal rules. The costs and effect sizes are
initial design values, not measured balance results.

The Autonomous Combat Vehicle has strength 42, 2 movement and a production cost
of 320. Mechanized Infantry can upgrade to it. The Autonomous Battle Tank has
strength 54, 2 movement and a production cost of 420; Modern Armor can upgrade
to it. The tank retains the Oil and Aluminum requirements, Blitz and armored
combat role of Modern Armor; the combat vehicle retains Mechanized Infantry's
March promotion, terrain restrictions and gunpowder combat role. Both are normal
player-controlled land units, cannot be drafted and provide no military
happiness. They reuse the existing vehicle models. No aircraft are reintroduced.

Research descriptions explain their subject rather than repeating cost warnings.
Civilopedia entries link the unlocked buildings and units. The technology
advisor shows their native clickable icons for the selected civilization.
Embassy-only rules in city construction, AI valuation, communication events and
building help are restricted to the actual embassy ID range; appended buildings
are ordinary buildings.

## Assets and validation

`tools/generate_modern_era.py` maintains the XML and the five-language text file,
and generates `Assets/Python/ModernEraData.py` for consistent UI filtering.
Tech/building/unit identifiers are appended or retained rather than renumbered.
Runtime RFC technology-copy and victory-count loops use the loaded technology
count so new ordinary technologies are included.

The DLL is built with the legacy VC7.1 toolchain. XML parsing, enabled research
dependencies and complete five-language coverage are audited separately. No
gameplay, load or multiplayer tests have been run. A German menu/technology-screen
inspection remains a user-operated runtime check.
