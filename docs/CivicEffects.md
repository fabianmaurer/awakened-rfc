# Civic effect audit

Reviewed against the requested five-column civic table on 2026-10-08.
All effects below have implementation paths in XML, C++, or Python, and are
described in civic help. This is a source and asset audit; it does not replace
an in-game or multiplayer check.

| Civic | Implemented effects | Implementation |
| --- | --- | --- |
| Stammessystem | +20% production for all units; −20% research; +100% distance and number-of-cities maintenance | `CvCity::getProductionModifier(UnitTypes)`; civic XML |
| Monarchie | +25% production for world, team and national wonders | `CvCity::getProductionModifier(BuildingTypes)` |
| Republik | +50% great person rate | civic XML; `CvPlayer::processCivics` |
| Diktatur | +20% production; −100% war weariness; −2 happiness in every city | civic XML; `CvPlayer::processCivics` |
| Demokratie | +2 happiness in every city; one random other civic column changes at elections every 10 turns | civic XML; `CvRFCEventHandler.onBeginPlayerTurn` |
| Despotismus | +1 happiness from palaces and monuments, including civilization replacements | civic XML building class happiness; `CvPlayer::processCivics` |
| Theokratie | +1 happiness per state-religion building; −2 happiness per other religious building; +10% combat strength | `CvCity::getExtraHappiness`; `CvUnit::maxCombatStr` |
| Plutokratie | +25% gold; +50% trade-route commerce | civic XML commerce and trade yield modifiers |
| Nationalismus | +5 culture in every city; −5 happiness where a foreign player's culture exceeds the owner's culture on the city tile; +20% production | `CvCity::getBaseCommerceRateTimes100`, `getExtraHappiness`; civic XML |
| Rechtsstaat | +2 happiness in every city; +10% commerce yield before allocation to gold/research/culture/espionage | civic XML |
| Selbstversorgung | +2 health in every city; stops improvement upgrades; blocks assigned specialists, retains free specialists | civic XML; `CvPlayer::getImprovementUpgradeRate`, `setCivics`; `CvCity::isSpecialistValid` |
| Sklaverei | Population rush; +2 commerce from plantations | civic XML |
| Leibeigenschaft | +1 food from farms; −1 commerce from villages; +50% worker speed | civic XML |
| Planwirtschaft | +1 production from workshops, watermills and windmills; +1 food from farms; −20% commerce yield | civic XML |
| Marktwirtschaft | +1 free specialist per city; +100% improvement upgrade rate | civic XML |
| Kriegergesellschaft | +2 starting experience for melee units only; −20% siege combat strength | civic XML; `CvCity::getProductionExperience`; `CvUnit::maxCombatStr` |
| Miliz | +30% city defense; −10% combat strength on tiles outside the unit owner's territory | `CvCity::getTotalDefense`; `CvUnit::maxCombatStr` |
| Rittertum | +25% mounted unit production; +10% city attack | `CvCity::getProductionModifier(UnitTypes)`; `CvUnit::cityAttackModifier` |
| Berufsarmee | +5 starting experience | civic XML |
| Wehrpflicht | +25% production for all units | `CvCity::getProductionModifier(UnitTypes)` |
| Ahnenkult | +1 culture from monuments, including civilization replacements | `CvCity::getBaseCommerceRateTimes100` |
| Staatsreligion | +1 happiness in state-religion cities; +100% missionary production, irrespective of missionary religion | civic XML; `CvCity::getProductionModifier(UnitTypes)` |
| Gottesstaat | +2 happiness and +10% production in state-religion cities; −2 happiness in other cities | civic XML; `CvCity::getBaseYieldRateModifier` and `getExtraHappiness` |
| Toleranz | Removes religion anger; does not grant additional happiness for religions | `CvCity::getReligionPercentAnger` |
| Staatsatheismus | +10% research; disables religious building effects; blocks natural, missionary, event and scripted spread | civic XML; `CvCity::processBuilding`, `getNumActiveBuilding`, `getBuildingCommerceByBuilding`, `setHasReligion`, `doReligion`; `CvPlayer::setCivics`; `CvUnit::canSpread` |

## Details and boundaries

- Civic stability is determined by bounded combination bonuses/penalties;
  see [CivicStability.md](CivicStability.md) for the complete rules. Individual
  civic weights and the legacy market/planned-economy crises have been removed.
- Only the religion column enables a state religion. Theocracy in the legitimacy
  column applies its building and combat bonuses without enabling a state
  religion independently or implying that other legitimacy civics prohibit one.
- Normal citizens remain the fallback for idle population under self-sufficiency.
  Assigned specialists are removed upon adoption; free specialists use separate
  counters and are retained.
- Improvement growth covers every upgrade stage of cottages. Serfdom's commerce
  penalty applies to the village improvement, as specified in the original table.
- Democracy uses the synchronized game RNG and only selects columns with an
  available alternative. If no other column has an available alternative, nothing
  changes. Elections occur on global turn multiples of ten.
- Democracy's old temporary transition instability has been removed. Its election
  effect is displayed once through the civic's XML Help entry.
- Production bonuses from dictatorship and nationalism now add together through
  the standard yield modifier rather than a shared conditional bonus.
- Religious buildings are identified by `ReligionType` or `PrereqReligion`.
  Atheism removes/restores cached local and global building effects on adoption
  and departure; buildings remain owned and still count toward wonder limits.
  Suppression also covers obsolete-safe building culture, shrine income, free
  specialists and great person generation.
- Existing religions remain under atheism, including when a city changes owners.
  Founding or relocating a holy city is preserved as a separate game action;
  ordinary religion spread, including event and Python calls, is blocked.
- Changing XML civic modifiers affects cached player/city data. Start a new game
  when checking these changes; an older save may retain earlier cached bonuses.

## Asset checks

`python tools/audit_civic_assets.py` checks all loaded text entries for all five
languages, the 25 civic definitions, their description/help keys and civic IDs
referenced by XML and the changed C++ files. The civic XML was additionally checked with
MSXML 3.0 against its XDR schema. Python event code was syntax checked using the
bundled Python 2.4 interpreter and universal-newline input.

Custom help uses one `[ICON_BULLET]` per effect, `[NEWLINE]` between effects and
the Civ4 production, happiness, unhappiness, culture and strength symbol macros.
Standard XML effects retain the game's standard generated help.
