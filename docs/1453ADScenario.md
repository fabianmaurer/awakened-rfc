# 1453 AD: after the fall of Constantinople

Open `PublicMaps/Start 5 - 1453 AD.CivBeyondSwordWBSave` through the scenario
menu. The map belongs to `Mods\Awakened RFC` and uses the legacy game DLL.
The authored position is immediately after the Ottoman capture of
Constantinople, rather than the later conquest of the Mamluks or all Anatolia.

The scenario contains 108 cities and 25 initially playable major civilization
slots. Every major civilization with cities is selectable, including early
civilizations repurposed to represent contemporary successor states. Babylon
has no independent state in this roster. America has not spawned and retains
its normal future birth. Independent and Native players still represent states
without a separate major civilization slot; they are not selectable countries.

## Playable roster and intended names

| RFC civilization | State represented / German starting name | Capital |
| --- | --- | --- |
| Egypt | Mamlukensultanat | Al-Qahira |
| India | Sultanat von Delhi | Delhi |
| China | Ming-Reich | Beijing |
| Greece | Griechisches Despotat (Morea) | Mistra |
| Persia | Timuridenreiche | Samarqand |
| Carthage | Hafsiden-Sultanat | Tunis |
| Rome | Italienische Stadtstaaten | Venezia |
| Japan | Ashikaga-Shogunat | Kyoto |
| Ethiopia | Kaiserreich Abessinien | Aksum |
| Maya | Königreiche der Maya | Mani |
| Vikings | Skandinavische Königreiche | Kobenhavn |
| Arabia | Scharifat von Mekka | Makkah |
| Khmer | Königreich Kambodscha | Chaktomuk |
| Spain | Christliche Reiche Iberiens | Toledo |
| France | Königreich Frankreich | Paris |
| England | Königreich England | London |
| Germany | Heiliges Römisches Reich | Wien |
| Russia | Großfürstentum Moskau | Moskva |
| Netherlands | Burgundische Niederlande | Brugge |
| Mali | Malireich | Niani |
| Portugal | Königreich Portugal | Lisboa |
| Inca | Land der vier Weltgegenden | Qusqu |
| Mongolia | Nördliche Yuan | Qaraqorum |
| Aztecs | Aztekischer Dreibund | Tenochtitlan |
| Turkey | Osmanisches Sultanat | Konstantiniyye |

Names use the shared live/preview classifier, not fixed strings in the map.
The 1453 start has its own civic profiles, selected after authored technologies
are loaded. In particular, the Ottoman state uses its sultanate identity before
1517, not an early Ottoman caliphate. Changing institutions, religion, city count,
or vassal status can change names in play. No naming rule changes synchronized
institutions merely to obtain a desired label.

## World position and abstractions

- Constantinople is Ottoman; Mamluk Egypt and the Levant remain separate. Morea
  and Trebizond survive. The Meccan slot does not own Yemen.
- France and England are at war. Bordeaux is still English in this post-May
  1453 position; it was not silently assigned its later French ownership.
- Novgorod remains independent. Jaunpur, Bengal, the Deccan and regional Iranian
  states are independent rather than assigned to a much larger Delhi/Timurid
  empire. The Timurids are explicitly represented as several principalities.
- Timbuktu is independent of Mali. Chan Chan, Cajamarca and the northern/southern
  Andean settlements are outside the early Pachacuti empire. Mayapan's abandoned
  city is represented by the surviving regional center Mani instead.
- Italy, Christian Iberia, Scandinavia and the Low Countries aggregate several
  real polities. Scandinavia is not presented as an uncontested unified Kalmar
  monarchy in 1453. Their individual wars and personal unions are not simulated
  by adding invented civilization slots.
- Holy cities represent all seven game religions. Eastern Christianity and
  Catholicism share Civ4's Christianity. Geographic approximations include the
  shared Jerusalem holy-city site, Jaunpur for the Ganges holy-city region,
  Mistra on the inherited Greek capital tile, and Brugge on RFC's Low Countries
  tile. Aksum represents the Ethiopian slot's established royal region rather
  than claiming that the historically itinerant court was permanently there.
- City sizes are relative urban weights. Terrain, map scale, civilization unique
  powers and leader abilities remain those of RFC. Displayed leaders use period
  names or collective courts; existing leader portraits and traits are reused.

## Assets and initialization

Additional independent regional centers fill otherwise empty settled regions:

| Region | Cities | Initial population |
| --- | --- | --- |
| Ireland | Dublin | 3 |
| Southern Italy and Sicily | Napoli, Palermo | 6, 5 |
| Hungary | Buda | 5 |
| Georgia | Tbilisi | 3 |
| Western Maghreb | Fes, Tlemcen | 6, 4 |
| Oman | Masqat | 3 |
| Tibet | Lhasa | 3 |
| Sri Lanka | Colombo | 3 |
| Malay Peninsula | Melaka | 5 |
| Java | Surabaya | 4 |

These cities receive the same size-based buildings, two longbow defenders,
local culture, roads and surrounding improvements as other Old World cities.
Their religions are assigned per city because the two independent slots group
unrelated states. Independent status is a gameplay abstraction: Dublin represents
settled Ireland without granting England the whole island, while Napoli and
Palermo represent the southern kingdoms separately from the Italian city-state
slot and the aggregated Iberian crowns. Their shared Aragonese monarch is not
modeled as a new diplomacy relationship. Napoli uses the land tile at (62,42)
to preserve spacing from Rome on the compressed map. Surabaya represents an
urban center in eastern Java rather than a claim to be Majapahit's capital.

`tools/generate_1453_ad_scenario.py` authors the map, five-language scenario and
leader text, and `Scenario1453Data.py`. It reuses Earth terrain from the 840 map
but replaces every city and unit, diplomacy, technology packages and visibility.
It checks generated XML type references while producing the assets.

Old World countries receive medieval technologies, with Gunpowder and Optics
for selected states. American civilizations have separate packages without
horses, iron weapons or oceanic navigation. The Ottomans have Janissaries and
trebuchets representing bombards; Steel-era cannon are not granted prematurely.
Cities have garrisons, useful buildings, nearby improvements and local roads;
capitals have workers and small field forces. Maritime countries receive ships
on adjacent water, with caravels only where Optics is present.

Inherited tribal villages inside the initial city culture radii are removed.
WorldBuilder applies city culture before city creation is complete; claiming a
village at that point invokes the goody routine during loading. Villages outside
the initial borders remain available for discovery during play.

`Scenario1453AD.setup` uses the authored state without replaying old spawns or
handing out ancient/600 AD starting packages. It fixes palaces to the authored
capitals and initializes stability, live-turn and city-count records. Previously
missed ancient victory objectives follow the existing late-start failure
handling; there is no wholesale rewrite of historical victories for 1453.
America retains its usual birth, starting treasury and spawn logic.

The start uses RFC turn 271, ordinarily 1450. The DLL displays that scenario's
first turn as 1453 and returns to the normal calendar at turn 272 (1455).
Subsequent birth dates and historical deadlines are not shifted by changing
`StartYear`. The introduction and selection preview also use 1453.

AI war scheduling starts no earlier than this scenario. Setup tech/religion
events are suppressed on the initial turn, as in the other authored starts.
All multiplayer peers need the same map, Python, XML and DLL.

## Verification limits

The asset generation, complete language coverage, playable major roster and
legacy DLL build were checked. No game was launched and no gameplay or
multiplayer tests were run. Population, army and technology balance remains
unmeasured; successful asset generation and compilation do not establish runtime
or multiplayer correctness.

## Historical references

- [Treccani: Alfonso V, king of Aragon and Naples](https://www.treccani.it/enciclopedia/alfonso-v-il-magnanimo-re-di-aragona-iv-come-conte-di-catalogna-i-come-re-di-napoli/)
- [UNESCO: Melaka and George Town](https://whc.unesco.org/en/list/1223/)
- [Met: Eastern Mediterranean, 1400–1600](https://www.metmuseum.org/it/toah/ht/08/wae)
- [National Palace Museum: Ming period](https://www.npm.edu.tw/exh99/ceramics/en/page-4.html)
- [Smithsonian: Delhi Sultanate, 1206–1526](https://asia.si.edu/explore-art-culture/collections/search/?edan_fq%5B%5D=topic%3ADelhi+Sultanate+%281206+-+1526%29)
- [Oxford: Delhi under the Sultanate](https://academic.oup.com/book/36782/chapter-abstract/321921075)
- [UNESCO: Angkor and the Khmer state](https://whc.unesco.org/en/list/668/)
- [Store norske leksikon: the interrupted Kalmar union](https://snl.no/Kalmarunionen)
- [Met: Islamic arms and the fifteenth-century political world](https://resources.metmuseum.org/resources/metpublications/pdf/Islamic_Arms_and_Armor_in_The_Metropolitan_Museum_of_Art.pdf)
