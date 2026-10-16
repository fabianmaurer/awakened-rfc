# Unique powers audit

Compared the current DLL and Python sources with the original installed **Rhye's and Fall MP** sources, using the unique-power descriptions and the hook list in `Assets/Python/UniquePowers.py`. This was a source audit; runtime and multiplayer validation remain separate.

General civilization cost/threshold tuning stays removed. Named unique powers are separate mechanics.

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
| Arabia, Russia, Mongolia, Aztecs, Turkey, America | The existing Python unique-power implementations and their event hooks remain active: conquered-city religion, winter damage, razing terror, enslavement, cultural assimilation and migration. |

The Turkish half-revolt-probability adjustment was general balance tuning; its named culture-assimilation power remains in `UniquePowers.py`. The obsolete Persian maintenance and English naval unit-cost code was already inactive in the original and is not revived.
