# 1453 AD: after the fall of Constantinople

Open `PublicMaps/Start 4 - 1453 AD.CivBeyondSwordWBSave` through the scenario
menu. The map belongs to `Mods\Awakened RFC` and uses the legacy game DLL.
Its shared world geography is selected by the scenario registry; see
[Scenario geography](ScenarioGeography.md) for authoring another map size.
The authored position is immediately after the Ottoman capture of
Constantinople, rather than the later conquest of the Mamluks or all Anatolia.

The scenario contains 109 cities and 26 initially playable major civilization
slots. Every major civilization with cities is selectable, including early
civilizations repurposed to represent contemporary successor states. Babylon
has no independent state in this roster. America has not spawned and retains
its normal future birth. Independent and Native players still represent states
without a separate major civilization slot; they are not selectable countries.
For this map, the DLL treats both true and false `PlayableCiv` flags as binding;
the older RFC later-join rules cannot unlock Babylon, America or minor slots.
The generator also checks the emitted selection flags against the populated
major roster. America's later AI birth remains enabled.

## Playable roster and intended names

| RFC civilization | State represented / German starting name | Capital | Starting leader |
| --- | --- | --- | --- |
| Egypt | Mamlukensultanat | Al-Qahira | Inal |
| India | Sultanat von Delhi | Delhi | Bahlul Lodi |
| China | Ming-Reich | Beijing | Jingtai |
| Greece | Despotat Morea | Mistra | Demetrios Palaiologos |
| Persia | Timuridenreich | Samarqand | Abu Sa'id Mirza |
| Carthage | Hafsiden-Sultanat | Tunis | Abu Amr Uthman |
| Rome | Republik Venedig | Venezia | Francesco Foscari |
| Japan | Ashikaga-Shogunat | Kyoto | Ashikaga Yoshimasa |
| Korea | Joseon | Hanseong | Danjong |
| Ethiopia | Kaiserreich Abessinien | Aksum | Zara Yaqob |
| Maya | Mani und Tayasal | Mani | Ah Xupan Xiu |
| Vikings | Kalmarer Union | Kobenhavn | Christian I. |
| Arabia | Scharifat von Mekka | Makkah | Barakat ibn Hasan |
| Khmer | Königreich Kambodscha | Chaktomuk | Ponhea Yat |
| Spain | Kastilien und Aragon | Toledo | Johann II. von Kastilien |
| France | Königreich Frankreich | Paris | Karl VII. |
| England | Königreich England | London | Heinrich VI. |
| Germany | Heiliges Römisches Reich | Wien | Friedrich III. |
| Russia | Großfürstentum Moskau | Moskva | Wassili II. |
| Netherlands | Burgundische Niederlande | Brugge | Philipp der Gute |
| Mali | Malireich | Niani | Uli II. |
| Portugal | Königreich Portugal | Lisboa | Alfons V. |
| Inca | Land der vier Weltgegenden | Qusqu | Pachacuti |
| Mongolia | Nördliche Yuan | Qaraqorum | Esen Taishi |
| Aztecs | Aztekischer Dreibund | Tenochtitlan | Moctezuma I. |
| Turkey | Osmanenreich | Konstantiniyye | Mehmed II. |

Names use the shared live/preview classifier, not fixed strings in the map.
The 1453 start has its own civic profiles, selected after authored technologies
are loaded. In particular, the Ottoman state uses the name Osmanenreich before
1517 rather than an early Ottoman caliphate. Changing institutions, religion, city count,
or vassal status can change names in play. No naming rule changes synchronized
institutions merely to obtain a desired label.

## World position and abstractions

The named leaders represent the center of each aggregated slot. Demetrios
Palaiologos represents Mistra, alongside his historical co-ruler Thomas;
Abu Sa'id Mirza represents Samarqand rather than sole control of every Timurid
principality. Francesco Foscari represents Venice rather than historical rule
over Rome. John II represents Castile within the combined Castile-and-Aragon
slot; Alfonso V ruled Aragon separately. Christian I represents Denmark and
Norway within the contested Kalmar Union, including the separately ruled Sweden
on this compressed map. Ah Xupan Xiu represents the Xiu of the Mani region,
not historical rule over Tayasal. His chronology is based on later traditions;
Uli II is a mid-fifteenth-century representative for Mali whose exact accession
date is uncertain. These choices simplify political geography without inventing
personal names or changing starting ownership and diplomacy.

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
  powers and leader abilities remain those of RFC. Displayed leaders use historical personal names; existing leader portraits
  and traits are reused.

## Assets and initialization

Each of the 25 starting major civilizations has its own short Dawn of Man
briefing describing its local position in 1453 and possible strategic goals.
`INTRODUCTIONS` in the generator stores the German and English wording;
the other three language fields currently use English. The screen selects the
briefing by active player slot so repurposed civilizations receive the correct
regional introduction. Other scenarios retain their existing opening text.

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
unrelated states. Baghdad, Shiraz, Tabriz, Sana'a, Gharnata, Jaunpur, Gaur,
Dabhol, Multan, Timbuktu, Gao and Kilwa start with Islam; Vijayanagara starts
with Hinduism. Inbhir Nis, Krakow, Novgorod and Trapezous start with Christianity;
Ava, Ayutthaya and Thang Long with Buddhism, and Hanseong with Confucianism.
The Ottoman slot starts with Islam, with a Christian city override for
Thessaloniki. Holy-city religions remain additional city religions (for example,
Jaunpur also retains Hinduism and Buddhism).
Cities representing local American, African and Mongolian traditions retain
explicit exceptions for faiths outside the seven game religions. The generator
rejects any other city without a religion assignment.

Independent status is a gameplay abstraction: Dublin represents
settled Ireland without granting England the whole island, while Napoli and
Palermo represent the southern kingdoms separately from the Italian city-state
slot and the aggregated Iberian crowns. Their shared Aragonese monarch is not
modeled as a new diplomacy relationship. Napoli uses the land tile at (62,42)
to preserve spacing from Rome on the compressed map. Surabaya represents an
urban center in eastern Java rather than a claim to be Majapahit's capital.

`tools/generate_1453_ad_scenario.py` authors the map, five-language scenario and
leader text, and `Scenario1453Data.py`. It reads the internal Earth-map template
`tools/scenario_templates/1453_ad_base.CivBeyondSwordWBSave` and replaces every
city and unit, diplomacy, technology packages and visibility. The template is
kept outside the mod and is not a playable scenario.
It checks generated XML type references while producing the assets.

Old World countries receive medieval technologies, with Gunpowder and Optics
for selected states. American civilizations have separate packages without
horses, iron weapons or oceanic navigation. The Ottomans have Janissaries and
trebuchets representing bombards; Steel-era cannon are not granted prematurely.
Cities have garrisons, useful buildings, nearby improvements and local roads;
capitals have workers and small field forces. Maritime countries receive ships
on adjacent water, with caravels only where Optics is present.
Japan's capital receives two Samurai instead of the generic knight field force.
The city-garrison promotion on Japanese military land units comes from Japan's
unique power, including on mounted units; it is not a WorldBuilder assignment.

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

- [Treccani: Francesco Foscari](https://www.treccani.it/enciclopedia/francesco-foscari_%28Dizionario-di-Storia%29/)
- [TDV: Abu Sa'id Mirza (1451-1469)](https://islamansiklopedisi.org.tr/ebu-said-mirza-han)
- [TDV: Barakat of Mecca](https://islamansiklopedisi.org.tr/berekat)
- [National Museum of Denmark: Christian I](https://natmus.dk/historisk-viden/temaer/kongeraekken/christian-1/)
- [UNAM: Ah Xupan Xiu in the Maya historical traditions](https://archivos.juridicas.unam.mx/www/bjv/libros/11/5390/7.pdf)
- [Uli II: uncertain mid-fifteenth-century chronology](https://en.wikipedia.org/wiki/Uli_II)
- [Esen Taishi](https://en.wikipedia.org/wiki/Esen_Taishi)

- [Met: Muromachi Japan and Ashikaga authority](https://www.metmuseum.org/ja/essays/muromachi-period-1392-1573)
- [UNESCO: Hampi, capital of Vijayanagara](https://whc.unesco.org/en/list/241/)
- [Stanford Encyclopedia of Philosophy: Korean Confucianism](https://plato.stanford.edu/entries/korean-confucianism/)
- [Treccani: Alfonso V, king of Aragon and Naples](https://www.treccani.it/enciclopedia/alfonso-v-il-magnanimo-re-di-aragona-iv-come-conte-di-catalogna-i-come-re-di-napoli/)
- [UNESCO: Melaka and George Town](https://whc.unesco.org/en/list/1223/)
- [Met: Eastern Mediterranean, 1400–1600](https://www.metmuseum.org/it/toah/ht/08/wae)
- [National Palace Museum: Ming period](https://www.npm.edu.tw/exh99/ceramics/en/page-4.html)
- [Smithsonian: Delhi Sultanate, 1206–1526](https://asia.si.edu/explore-art-culture/collections/search/?edan_fq%5B%5D=topic%3ADelhi+Sultanate+%281206+-+1526%29)
- [Oxford: Delhi under the Sultanate](https://academic.oup.com/book/36782/chapter-abstract/321921075)
- [UNESCO: Angkor and the Khmer state](https://whc.unesco.org/en/list/668/)
- [Store norske leksikon: the interrupted Kalmar union](https://snl.no/Kalmarunionen)
- [Met: Islamic arms and the fifteenth-century political world](https://resources.metmuseum.org/resources/metpublications/pdf/Islamic_Arms_and_Armor_in_The_Metropolitan_Museum_of_Art.pdf)
