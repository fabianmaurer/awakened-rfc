# Unique powers audit

Compared the current DLL and Python sources with the original installed **Rhye's and Fall MP** sources, using the unique-power descriptions and the hook list in `Assets/Python/UniquePowers.py`. This was a source audit; runtime and multiplayer validation remain separate.

General civilization cost/threshold tuning stays removed. Named unique powers are separate mechanics.

## Additional powers (2026-10-24)

Civilizations with missing or placeholder powers now have the following permanent
abilities. These apply equally to AI and human players, use civilization identity
rather than player slots, and are independent of civics except where stated.

| Civilization | Power | Effect |
| --- | --- | --- |
| Byzantium | Imperial Crossroads | +50 percentage points to the trade-income modifier for routes between its own cities. Normal infrastructure and range rules still apply. |
| Celtia | Sacred Groves | +1 food on owned forest tiles. |
| Holy Roman Empire | Imperial Church | +100% production of non-wonder buildings belonging to its current state religion. No benefit without a state religion. |
| Korea | Scholarly Institutions | +100% production of non-wonder buildings with a percentage research modifier, including the Seowon. Replaces the unique-unit/building placeholder. |
| Mississippians | Mound Builders | +1 production from owned farms beside rivers. |
| Adena | Earthwork Builders | +1 production from owned farms beside rivers; a separate civilization in the 800 BC regional slot. |
| Sumeria | Temple Cities | Priest specialists yield +1 production and +1 commerce. |
| Zulu | Buffalo Horns | Melee units have +1 movement point. Applies to existing and new units; upgrades out of the melee class lose it. |
| Abbasids | House of Wisdom | All specialists, including settled Great People, yield +2 research. |
| Fatimids | The Nile's Bounty | +1 food from owned desert farms beside rivers, including flood plains. |
| Umayyads | Gardens of al-Andalus | +1 commerce from owned irrigated farms. |

The three caliphate successor powers replace the inheritance-only description;
their partition inheritance remains unchanged. Independents, generic Natives,
Minor and Barbarian entries are administrative factions, not additional named
civilizations. The existing Hunnic and Papal powers remain unchanged. Several
base-game civilization entries are not assigned a historical major-player slot;
their new powers apply whenever those civilizations are used.

Implementation: `CvPlayer` (construction and specialists), `CvCity`
(trade-income modifier), `CvPlot` (tile yields), `CvUnit` (movement) and
`CvRhyes` (civilization help). Descriptions are provided in all five languages.
These additions have not been validated in gameplay or multiplayer.

## Existing powers

| Power | Implementation |
| --- | --- |
| China — Myriads | Melee and gunpowder units cost two-thirds of the shared production cost, giving the advertised 1.5x training speed. Applied outside the bypassed civilization cost switch in `CvPlayer::getProductionNeeded(UnitTypes)`. |
| Maya — Astronomy | Research costs are reduced by 40% through the Medieval era in `CvHandicapInfo::getResearchPercentByID`. No general Mayan research multiplier is reintroduced. |
| Persia — Satrapy | Each conquered city gives +2 stability in `Stability.onCityAcquired`, included in the expansion stability breakdown. Independent of the removed sixth civic column. |

The original Chinese and Mayan cost branches mixed their powers with balance tuning. The separated effects use their advertised strengths rather than retaining those old tuning percentages.

Other unique-power hooks remain present and reachable:

| Civilizations | Hooks checked |
| --- | --- |
| Egypt | Starts with Pharaonic Kingship, Divine Kingship and Slavery in 3000 BC. Early Slavery access in `CvPlayer::canDoCivics` is resolved by civic type. Pharaonic Kingship replaces Tribal System's effects for Egypt with +1 production from farms and slave specialists and medium upkeep. Divine Kingship replaces palace/monument happiness with +1 happiness per assigned priest in cities with an Egyptian Obelisk (cap +2), preventing Obelisk obsolescence while active (all effects and construction remain available after Calendar). Egypt also starts with Pharaonic Kingship, Divine Kingship and Slavery in 800 BC, with the Pharaoh title and Pharaonic Egypt country name. Its existing Monarchy technology remains available for later government changes. |
| India | No revolution anarchy in `updateMaxAnarchyTurns`. |
| Babylon, Greece | No conquest resistance in `CvPlayer::acquireCity`; early +150% great person rate in `CvCity::getGreatPeopleRate`. The generic great person threshold tuning is separate. |
| Carthage, Mali | Extra commerce on sea/land plots respectively in `CvPlot::calculateYield`. Removed maintenance/research penalties were balance offsets to these powers. |
| Rome, Inca | Roman road movement in `CvPlot::movementCost`; mountain yields in `calculateNatureYield`. |
| Japan, Spain, England, Portugal | Unit bonuses in `CvUnit::init`: city defense, naval movement, naval first-strike chances and naval visibility. |
| Ethiopia, Khmer, Netherlands | Ethiopian cultural defection protection in `CvPlot::doCulture`; jungle access and naval territorial access in `CvUnit`. |
| France, Germany, Vikings | Diplomatic friendliness in `CvPlayerAI`/Congresses; Industrialism upgrade discount in `CvUnit::upgradePrice`; pillage gold in `CvUnit`. |
| Arabia | By requested rework, the permanent Python conquest-conversion/building grants are replaced by the saved 300-year Mecca/Islam expansion event in `CvPlayer`: conquest/birth-flip conversion and expulsion, first-acquisition recruits and locked border wars. See `Gameplay.en.md`. |
| Russia, Mongolia, Aztecs, Turkey, America | The existing Python unique-power implementations and their event hooks remain active: winter damage, razing terror, enslavement, cultural assimilation and migration. |

The Turkish half-revolt-probability adjustment was general balance tuning; its named culture-assimilation power remains in `UniquePowers.py`. The obsolete Persian maintenance and English naval unit-cost code was already inactive in the original and is not revived.
