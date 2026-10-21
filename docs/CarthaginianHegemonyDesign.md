# Carthaginian Mediterranean hegemony: proposed tuning

User target: roughly 25% of ordinary AI games should produce Carthaginian
Mediterranean hegemony. This is a desired alternate-history frequency, not an
estimate of the historical probability of winning the Punic Wars.

The first sections record the original diagnosis and proposed approach.
The implemented first pass is documented at the end. The Pompeii terrain
change is documented separately in `ItalianCoreYieldAudit.md`.

## North African invasions

`Barbs.checkTurn` has fixed schedules, with `iHandicap = 0`:

- About 210 BC to AD 50: one horse archer per nine turns, if a valid spawn plot
  is available in the designated North African rectangle.
- AD 50 to 900: two horse archers per ten turns and two camel archers per ten
  turns, staggered five turns apart. Camel archers have combat strength ten and
  normally require Guilds, but these scripted spawns do not wait for that tech.
- From AD 450, separate nearby western African schedules add war elephants and
  Impi; there are also more southerly Native-player Impi and coastal pirates.

These are configured spawn attempts, not measured actual spawn counts. The
land-spawn predicate requires an empty land plot with zero culture, so actual
pressure depends on cultural coverage as well as the calendar. The schedule
does not check whether Arabia has spawned, whether Arabs are conquering, who
owns the North African coast, or whether that owner has a thriving empire.
It can attack Punic, Roman or other coastal states alike.

There is historical justification for frontier conflict, including serious
late Roman and Byzantine raids. The Laguatan were more complex than a simple
camel-nomad stereotype; research cautions against explaining their emergence
by camel diffusion alone. See [Mattingly, The Laguatan](https://www.cambridge.org/core/journals/libyan-studies/article/abs/laguatan-a-libyan-tribal-confederation-in-the-late-roman-empire/FF2EC28ECF020405FD6E9756833BAAA2).

That supports regional raiding, not a specific continuous spawn rate or
Guilds-strength units beginning in AD 50. Roman North Africa also sustained
prosperous urban and agricultural communities; the Vandal invasions came from
Spain in 429-439. Byzantine reconquest followed in 533, and Arab expansion in
the seventh century. See the Metropolitan Museum's
[AD 1-500 chronology](https://www.metmuseum.org/toah/ht/05/afw.html) and
[AD 500-1000 chronology](https://www.metmuseum.org/toah/ht/06/afw.html).

Source inspection cannot establish the original author's intent. Mechanically,
this is persistent scripted attrition with the capacity to clear coastal states;
it is not an explicit Arabia-triggered clearing operation. The previous balance
batch's many barbarian conquests demonstrate the pressure, but do not identify
the spawn schedule or unit responsible for each conquest.

## Recommended sequence

1. **Normalize frontier pressure for every coastal owner.** Replace the early
   strength-ten camel stream with a smaller force appropriate to contemporary
   defenses. A candidate experiment is one horse archer per 15 turns before
   AD 300, then episodic, regionally concentrated pressure in late antiquity.
   Keep the ability of strong states to secure frontiers. Neither the date nor
   the rate is a calibrated result yet. Apply this equally to Rome and Carthage.
2. **Create a contested Punic sphere before Rome dominates.** Karalis already
   provides one neutral island opportunity. Further historically placed towns
   in Sicily, coastal Numidia or Iberia could create valuable conquest targets,
   with placement checked against birth-flip rectangles, map food and city
   spacing. Avoid handing all settlements directly to Carthage; Rome and Greece
   should also be able to contest them.
3. **Enable effective Punic campaigns.** Carthage starts with three Numidian
   cavalry, one assault galley and one escort trireme as well as its settler
   galley. Numidians have +50% against melee, which helps against Roman infantry,
   but have no listed city-assault AI role and do not form a complete city-taking
   army. Investigate assembling infantry, siege once available, and transports,
   and targeting Sicily/Italy instead of endless peripheral settlement.
4. **Support outcomes short of extermination.** Carthage can win by controlling
   strategic islands, Iberian access and Mediterranean commerce while forcing
   Rome into a subordinate regional position. A peace that strips Rome of its
   overseas footholds can be meaningful without requiring immediate occupation
   of every Italian city. Full Mediterranean hegemony should then require a
   leading position relative to Greece and Egypt as well.
5. **Calibrate frequency from outcomes.** Define a fixed territorial/political
   success criterion and a classical checkpoint, such as AD 100, then measure
   both Punic victory over Rome and wider Mediterranean dominance. Survival,
   a single Roman defeat, and full hegemony are distinct observations. Use all
   eligible seeds as the denominator. Twenty games are useful for screening;
   larger later batches are needed to judge whether the frequency is near 25%.

The existing extra Roman assault units and Campanian food adjustment must be
included when measuring the final distribution. Preserve both sides' named
unique powers, including Carthage's extra sea-tile commerce. The evidence does
not yet call for blanket civilization-specific production/research discounts.

No new test script was created or executed. The recommendation is to fix the
anachronistic frontier pressure and the ability to conduct real Punic wars
before using additional unit grants or numerical economic bonuses to chase a
target percentage.

## Implemented first targeted overhaul

The user authorized implementation and synchronization of the installed mod.
This pass adds no starting units, unit-stat bonuses or economic cost modifiers
to Carthage. Its sea-commerce unique power remains active.

### Regional pressure

The North African land schedule now attempts:

- 210 BC to AD 300: one horse archer every 15 turns.
- AD 300 to 700: two horse archers every 18 turns, restricted to Tripolitania
  (x60-70/y31-35), with recovery time between groups.
- AD 700 to 900: one horse archer every 15 turns.
- The existing smaller post-900 camel schedule remains unchanged.

The continuous AD 50-900 strength-ten camel stream is removed. The nearby
AD 450-1700 western African elephant stream becomes one swordsman per 16 turns,
instead of two war elephants. Southern Native Impi, the separate western Impi
schedule, pirates and non-African invasions remain unchanged. This is regional
tuning that also helps Roman or other coastal owners; it does not grant Punic
immunity. All groups still require valid empty, zero-culture spawn locations.
The rates are experimental design choices, not historically derived troop
counts or calibrated balance results.

### Opportunities and campaign priorities

An optional independent Gadir at (51, 40) is activated around 1100 BC in the
3000 BC scenario. It starts at population two with one archer and an improved
adjacent crab resource, providing a viable existing port rather than empty
land for a settler. Normal ownership, city-spacing and founding/retry checks
can prevent creation. It lies outside the Punic birth-flip area, so it is not
a free Carthaginian city. Existing Karalis provides a second island opportunity.

From twenty turns after Carthage's historical birth until AD 300, the existing
AI war-selection routine gives an additional 60 raw target-value points per
eligible enemy city in Iberia (x49-55/y40-45) and the central Mediterranean /
Italian region (x57-63/y40-44), before score normalization and diplomatic
adjustments. This favors valuable footholds over diffuse inland territory.
It does not add a war-selection turn, guarantee war with Rome, bypass existing
target filters, or directly order naval movements. Cities held by independent
states or Greece can also attract Carthaginian campaigns.

Successful scripted unit groups now emit observer `scripted_spawn` events with
owner, unit type, count, location, region and period. Recording reuses the
existing spawn result and consumes no extra RNG. This will let future analysis
distinguish configured attempts from actual successful groups. The existing
war and city-acquisition events show whether campaign priorities translate
into conquests.

### Validation and evaluation

Static syntax parsing and whitespace review were performed. No tests or Civ4
simulations were run. No DLL rebuild is required. The effects on shipping,
military composition, successful city captures and the desired roughly 25%
hegemony frequency remain unmeasured. Do not interpret this pass as having
achieved that frequency. Gadir and Karalis are new-game opportunities in the
3000 BC start, not retroactive additions to later scenarios or saved games.

The next balance analysis should report Carthaginian acquisition of Gadir,
Karalis and Italian cities, wars against Rome, actual African scripted spawns,
city-loss collapses, and Mediterranean territory at classical checkpoints.

Installed synchronization completed: all 654 runtime files match the workspace
using the observer launcher's SHA-256 manifest. Runtime fingerprint:
`c51450388b6a7e50c15c6e7dc5891a8f3823cf13f5aa4395260b7bb02c3cbdbb`.
The eight replaced installed files were backed up under
`testing/runs/deployment-backup-20261016-235006/`. Civ4 was closed during copying;
no game or test batch was launched.

## Implemented military civics and Punic hinterland improvements

Implementation dated 17 October 2026, following the next 20-game batch and
the user's authorization. See `EarlyGameBalanceBatch20261017.md` for the
production deficit that motivates the geographic changes. No post-change
balance result is claimed.

### Military alternatives

All civilizations can adopt either new civic once they have its technology.
Neither mechanic checks civilization identity.

| Civic | Replaces | Technology | Upkeep | Effects |
| --- | --- | --- | --- | --- |
| Naval Warfare | Militia | Sailing | Low | +50% military ship production; +2 experience for newly trained military ships, including armed transports |
| Feudal Retinues | Knighthood | Feudalism | Medium | +5% land military unit production per Farm actually worked by the producing city, including siege |

Naval Warfare excludes workboats. The unit XML's military-production flag is
also set for those civilian boats, so eligibility additionally requires combat
strength and the sea domain. Feudal Retinues applies the corresponding land
domain/combat check, excluding settlers, workers, missionaries and spies.
Neither bonus applies to buildings or projects. Production modifiers are
additive with other production modifiers, not independent multipliers.

Worked farms are counted from the city's current citizen assignments. Idle
and pillaged farms, the city center, and farms assigned to another city do not
contribute. The bonus updates directly with assignments; it is not saved or
cached as an empire-wide farm total. Six worked farms give +30% land military
production. There is no castle requirement, mounted experience bonus or extra
castle happiness. Professional Army retains +5 experience for newly trained
units, preserving the quantity-versus-training choice. The existing
Monarchy/medieval-military stability synergy now refers to Feudal Retinues.

The old Militia city-defense bonus and foreign-territory combat penalty are
removed. Knighthood's mounted/Samurai experience bonus and Japan-specific
Bushido presentation are removed. The new internal identifiers are
`CIVIC_NAVAL_WARFARE` and `CIVIC_FEUDAL_RETINUES`; they occupy the old military
category positions. Existing saves are not a compatibility target.

AI civic valuation uses actual coastal productive capacity, naval forces and
overseas assault plans for Naval Warfare. Feudal Retinues uses each city's
current worked farms and production. Citizen evaluation also accounts for
the marginal farm production modifier while training a land military unit.
This does not forecast future farms or provide a complete naval campaign AI.

Starting profiles no longer assign the old home-defense civic indiscriminately
to inland nations. Carthage, Greece, Vikings, the Netherlands and Portugal
prefer Naval Warfare when available; inland former Militia profiles use
Warrior Society. Former Knighthood profiles prefer Feudal Retinues. These are
starting preferences, not restrictions on later choices or civilization bonuses.
Leader favorite-civic references are updated as well. Naval Warfare uses the
existing Sailing button; Feudal Retinues retains the medieval military button.

Descriptions, effects, strategy summaries, Civilopedia explanations, production
help and election announcements have all five language elements and translated
new wording. The election messages now describe naval investment and farm-supported
levies. `tools/military_civic_text.py` supplies the shared new translations;
the strategy and election generators use it so regeneration retains the changes.

### Geographic changes

The same ten plots change in all four starts and the 1453 scenario's source
template. Existing cities, improvements, routes, river edges and unrelated
resources are preserved. No free farms, mines, fishing boats or starting units
are granted. Any owner can benefit from the land.

| Plot | Change | Intended contribution |
| --- | --- | --- |
| (54,39), Iol hill site | Plains hills -> grassland hills | +1 raw food, -1 raw production; retain the hill and allow more growth |
| (56,39), Hippo hill site | Plains hills -> grassland hills | Same; preserve the forest in starts that have it |
| (58,39), Qart-Hadasht/Tunis | Plains -> grassland | +1 raw food at the capital site |
| (56,38), Numidian/Tunisian hinterland | Desert -> plains; add Wheat | A farmable cereal source supporting western core cities |
| (57,38), inland Tunisia | Plains peak -> plains hills; add Iron | A workable upland mine and a local strategic iron source after Iron Working |
| (59,37), Sabratha site | Plains -> grassland | Better initial city food, trading one raw production for one food |
| (60,37), Oea/Tripolis site | Plains -> grassland | Same growth improvement |
| (59,36), Tripolitanian hinterland | Desert -> plains; add Wheat | A farmable cereal source for the small eastern ports |
| (60,36), Tripolitanian hinterland | Desert -> plains; add Sheep | Pastoral food and production, improved through ordinary worker actions |
| (61,36), Leptis-area site | Plains -> grassland | Support alternative eastern settlement and later growth |

These are small fertile and productive pockets, not a conversion of the
Sahara. The single peak-to-hill change represents an exploitable upland on a
coarse map; the surrounding mountain barrier remains. The food improvements
are intended to support citizens who can work the new mine and existing
productive tiles. Some individual grassland conversions reduce initial
hammers, so the expected benefit depends on growth and worker development.

Historical support is regional rather than a claim about exact map squares:

- The [Central Medjerda Valley study](https://www.cambridge.org/core/journals/libyan-studies/article/urban-transformation-in-the-central-medjerda-valley-northwest-tunisia-in-late-antiquity-and-the-middle-ages-a-regional-approach/73CC0A98FF842B6D2F10B5BB374CAAF5)
  documents agricultural surplus and the Carthage/Hippo/Cirta corridor.
- The Italian National Research Council's
  [Ancient Mines of the Mediterranean: Tunisia](https://ancientmines.ispc.cnr.it/tunisia-2/)
  identifies iron deposits and exploitation during the Carthaginian era in
  western Tunisia. The chosen iron hill is a geographic abstraction.
- The [UNESCO Libyan Valleys botanical survey](https://www.cambridge.org/core/journals/libyan-studies/article/abs/unesco-libyan-valleys-survey-x-botanical-evidence-for-ancient-farming-in-the-predesert/F3E8AADAB2F18208693F60C43124CEC4)
  and [Romano-Libyan crops and animals study](https://www.researchgate.net/publication/338453042_Romano-Libyan_agriculture_crops_and_animals_Chapter_8)
  support agricultural and pastoral pockets in Tripolitania. Later evidence
  supports the landscape's capacity; it does not establish an identical Punic
  settlement density or prescribe the size of a gameplay bonus.

Exact placement and yield strength are experimental balance choices. Carthage's
sea-commerce unique power and other named civilization unique powers remain
active. No civilization-specific production or research discount is added.

### Validation

The Release DLL compiled successfully through the legacy VC7.1 toolchain.
Localization and civic-reference audits cover all loaded text XML; Python
syntax and whitespace were reviewed. No gameplay tests were run. In-game
loading, citizen-assignment behavior, balance and multiplayer validation remain
user-operated checks. Inspect a non-English menu and the changed civic/election
text.

The built DLL is x86, with linker version 7.10 and imports of `MSVCR71.dll`,
`msvcp71.dll`, `python24.dll` and `boost_python-vc71-mt-1_32.dll`; no modern VC
runtime imports were found. The localization audit passed for 75 text files
and 2,472 entries, with complete language sets and no suspicious encoding.

Installed synchronization is complete: all 654 runtime files match the
workspace. Fingerprint:
`fd0668b0a3c4447ccc6299508576207c501071dc8c66099c21165c78f7b6909b`.
The Makefile deployed the DLL; the eleven remaining changed runtime files
were copied with backups in `testing/runs/deployment-civic-terrain-20261017/`.
Pre-edit workspace sources are preserved in
`testing/runs/civic-terrain-before-20261017/`. The build log is
`Awakened RFC/CvGameCoreDLL/legacy-toolchain/civic-terrain-build.log`.
