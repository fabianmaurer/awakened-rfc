# 900 AD: European settler start

Choose `Start 3b - 900 AD.CivBeyondSwordWBSave` in the scenario menu.
France, Spain, Germany, Russia, England and the Vikings all begin immediately
without cities. The date is turn 211, after Russia's normal birth at turn 207,
the latest normal birth among these six civilizations.

The start uses the existing medieval technology and military packages:

| Civilization | Settlers |
| --- | ---: |
| France | 2 |
| Spain | 1 |
| Germany | 3 |
| Russia | 4 |
| England | 4 |
| Vikings | 3 |

England's fourth settler and the Vikings' third settler depend on the existing
adjacent-sea placement logic. The Viking expedition includes a settler on its
coastal ship tile. All six receive workers and their existing starting armies;
naval civilizations retain their starting ships. They do not receive a second
birth package or automatic birth territory transfers.

Spain represents Alfonso III's Asturias and starts its settlers, workers and
army in the northern Oviedo region at (51,46), rather than the normal Madrid-area
birth tile (52,43). It receives one settler to establish its northern base,
with subsequent expansion south through conquest. This is a scenario-specific starting position;
the other starts retain Spain's original birth location.
Spain starts at war with the independent Andalusi cities described below. This
is an explicit gameplay starting condition, not a claim that every local ruler
was at war with Asturias on the same date in 900.

China, Japan and Khmer also start immediately. The Islamic states start with
the established positions described below. Later civilizations,
beginning with the Netherlands, retain their normal future births and starting
gold. The selection rules for later joining follow the existing 600 AD scenario.

This is a settlement scenario, not a reconstruction of every state in 900 AD.
Terrain, resources and most non-European cities come from the 600 AD map.
Western and northern European starting regions are cleared of cities, units,
culture and improvements, with the southern Iberian emirate described below;
Italy and Byzantium remain settled. The Chinese core
starts Chinese; Egypt and southern Syria start Tulunid. Makkah is the Islamic
holy city, because the normal founding event predates this start. Existing
leader portraits, unique powers and civilization slots are reused. Ancient historical
victories whose early objectives have already expired are disabled as in the
other late starts.

## Starting ruler names

| Slot | German displayed name |
| --- | --- |
| Egypt / Tulunids | Harun ibn Khumarawayh |
| Carthage / Aghlabids | Ibrahim II ibn Ahmad |
| China | Tang Zhaozong |
| Japan | Daigo |
| Vikings | Harald Schönhaar |
| Arabia / Abbasids | al-Mu'tadid |
| Khmer | Yasovarman I. |
| Spain | Alfons III. von Asturien |
| France | Karl III. der Einfältige |
| England | Eduard der Ältere |
| Germany | Ludwig das Kind |
| Russia | Oleg von Kiew |
| Umayyads / Córdoba | Abd Allah ibn Muhammad |
| Byzantium | Leo VI. der Weise |

The names represent contemporary rulers of the states aggregated into RFC's
slots: Asturias for Christian Iberia, West/East Francia, Wessex, the Kievan Rus',
Norway and the Abbasid caliphate. Harald represents Norway, rather than a single
monarch over all Scandinavia; his chronology and extent of rule are uncertain.
Names are localized in all five game languages and appear in selection and at
initialization for human and AI players. Later leader changes follow normal rules.

## Established Islamic states in 900

| State | Playable slot | Ruler | Capital | Direct starting cities |
| --- | --- | --- | --- | --- |
| Abbasid caliphate | Arabia (12), `CIVILIZATION_ABBASID` | al-Mu'tadid | Baghdad | Baghdad, Al-Raqqa, Al-Mawsil, Al-Basra, Makkah |
| Tulunid emirate | Egypt (0) | Harun ibn Khumarawayh | Al-Qata'i | Al-Qata'i, Al-Iskandariyya, Barqa, Al-Quds, Dimashq |
| Aghlabid emirate | Carthage (6) | Ibrahim II ibn Ahmad | Raqqada | Raqqada, Tarabulus, Balarm |
| Umayyad emirate | Successor slot (27), `CIVILIZATION_UMAYYAD` | Abd Allah ibn Muhammad | Cordoba | Cordoba |

These states start with garrisons, field troops, workers, local roads, markets,
granaries and walls; capitals also have palaces and libraries. The Tulunids,
Aghlabids and Umayyads receive 200 gold each, the Abbasids 300. Each capital has
three longbowmen, one spearman, two horse archers, two swordsmen and two workers;
other authored cities have two longbowmen. All four use the existing medieval
Arabian technology package and prefer monarchy, despotism, serfdom, warrior
society and state religion. The original Arabian settlers and expansion army
are not created in this scenario; the 600 AD start retains its existing forces.
Each state has its own opening briefing (English and German; other languages
currently use English). Names and selection labels have all five languages.

The Tulunids and Aghlabids acknowledge nominal Abbasid authority historically,
but are separate, autonomous playable states here. They are not locked into
Civ4's military vassal rules. The Aghlabids start at war with Byzantium, with two
galleys and a trireme near Ifriqiya; the scenario does not grant them Taormina,
which fell in 902. Raqqada and nearby Kairouan share one tile. Al-Qata'i and
Fustat likewise share the inherited Egyptian urban tile; Cairo was not founded
until 969. The inherited northern-Levant tile represents Damascus approximately;
Al-Raqqa, Mosul and Basra also use nearby passable tiles on the compressed map.
Population and force sizes are gameplay weights, not historical census totals.

Fes (Idrisid Morocco), Tahert (the Rustamid imamate), Al-Ahsa (the Qarmatian base)
and San'a (local Yemeni rule) are independent cities, not possessions of one of
the four large states. They share RFC's independent-player slots, so their
individual diplomacy is an abstraction. Al-Ahsa represents the regional revolt,
not the Qarmatian capture of Hajar in 903. Persian and Central Asian cities remain
independent rather than becoming a fictitious directly administered Abbasid
empire. Makkah's assignment to the Abbasids represents caliphal authority and
the holy city; local Hijazi government is not modeled separately.

The Fatimid caliphate was founded in Ifriqiya in 909 and conquered Egypt in 969;
it does not receive a state in 900. No automatic later dynastic transition or
territorial reconquest is scripted. Later play can diverge from history.
Regional stability areas and Abbasid/Umayyad settlement preferences reflect
this start, rather than the broad regions used by the normal partition mechanic.
Original regional civilization powers and portraits remain gameplay abstractions.

Sources for the dated political position:

- [Egyptian Ministry of Tourism and Antiquities: Tulunids, 868–905 and Al-Qata'i](https://egymonuments.gov.eg/en/historical-periods/tulunid-dynasty/).
- [Harun and the return of northern Syria to the Abbasids](https://en.wikipedia.org/wiki/Harun_ibn_Khumarawayh).
- [Aghlabid dynasty and the unfinished Sicilian campaign](https://en.wikipedia.org/wiki/Aghlabid_dynasty).
- [Museum With No Frontiers: Raqqada as Ibrahim II's capital from 876](https://islamicart.museumwnf.org/database_item.php?id=object%3BISL%3Btn%3BMus01%3B45%3Ben).
- [Museum With No Frontiers: Rustamid Tahert and the Idrisids](https://islamicart.museumwnf.org/dynasty.php?id=48).
- [Encyclopaedia Iranica: Abu Sa'id al-Jannabi and Bahrayn in 900](https://www.iranicaonline.org/articles/abu-said-jannabi-hasan-b/).
- [Egypt's National Museum of Egyptian Civilization: the Fatimid conquest in 969 and Cairo](https://nmec.gov.eg/historical-timeline/).

### Independent Andalusi cities

| City | Displayed name | Position | Population | Local authority represented |
| --- | --- | --- | --- | --- |
| Seville | Ishbiliyya | (49,41) | 5 | Ibrahim ibn Hajjaj / Banu Hajjaj |
| Badajoz | Batalyaws | (50,43) | 4 | The local Marwanid dynasty |
| Toledo | Tulaytula | (52,43) | 5 | Autonomous local Muslim rulers and urban elites |
| Zaragoza | Saraqusta | (54,45) | 5 | Muhammad al-Anqar and the Tujibid governors |

These represent local autonomy within fragmented al-Andalus, rather than the
eleventh-century taifa kingdoms. Each city has Islam, two longbow defenders,
walls, a granary, a market, local culture and roads. Seville is shifted one tile
west of its usual RFC position to preserve the minimum spacing from Cordoba.
The northern Asturian starting tile remains unoccupied and outside their culture.

The four cities share dedicated minor player/team 28, labeled Independent
Andalusi rulers. Their personal names and dynasties above explain the historical
position; the game uses one collective ruler and diplomacy slot, not four
separate leaders. The slot is not selectable. Spain/team 14 starts at war with
team 28; Córdoba is not automatically at war with them. The other independent
players (30 and 31), including their North African and Asian cities, do not join
that starting war. Other scenarios retain their original team setup.

Bobastro is not added as another Muslim principality: Ibn Hafsun's reported
conversion to Christianity in 899 makes that label misleading for this start,
and it is too close to Cordoba at this map scale.

Sources: [Seville's local rulers](https://scholarshare.temple.edu/server/api/core/bitstreams/8d01b7b4-081e-418c-b46c-7a3ace8cc57d/content),
[the Tujibid governors of Zaragoza](https://en.wikipedia.org/wiki/Banu_Tujib),
[regional autonomy and the civil war](https://digibug.ugr.es/bitstream/handle/10481/104332/Albarra%CC%81n_AlAndalus_War%20in%20the%20Iberian%20Peninsula.pdf?isAllowed=y&sequence=1),
and [Ibn Hafsun's conversion](https://islamansiklopedisi.org.tr/omer-b-hafsun).

### Emirate of Córdoba

The existing `CIVILIZATION_UMAYYAD` successor civilization starts in reserved
slot 27 as an independent, selectable state, under Abd Allah ibn Muhammad (888–912).
Choose the Emirate of Córdoba in the 900 AD scenario to play it; otherwise the
AI controls it. The other scenarios retain the reserved successor-slot rules.
It is named the Emirate of Córdoba, rather than a caliphate, in this scenario.
The native successor initialization preserves that name when loading a game.
The scenario does not add a separate civilization or simulate the proclamation
of the caliphate in 929.

Cordoba at (51,41) starts at population 6 with the established capital package
above and Islam.
Initial culture and roads cover only adjacent land, leaving Spain's starting
tile (51,46) free and outside the one-tile minimum city spacing.

One city represents the emirate's core during a period of fragmented authority;
the scenario does not give it all Iberia or western North Africa. The existing
successor AI uses Iberian settlement preferences for this start. The Abbasid
civilization is already a successor and does not trigger Arabia's original jihad
and partition. The occupied successor slot also prevents duplicate allocation.
See [Abd Allah's reign and the regional rebellions](https://en.wikipedia.org/wiki/Abdullah_of_C%C3%B3rdoba).

Reference chronologies: [rulers in 900](https://dewiki.de/Lexikon/Liste_der_Staatsoberhäupter_900),
[Norwegian royal succession](https://www.kongehuset.no/historie/kongerekken),
and [Leo VI](https://www.worldhistory.org/Leo_VI/).

Regenerate the map with `python tools/generate_900_ad_scenario.py` after changing
its source map or generation rules. The runtime initialization is in
`Assets/Python/Scenario900AD.py`. Native name preservation and settlement rules
are in `CvPlayer.cpp` and `CvCaliphate.cpp`; changing them requires the legacy DLL build.

New-game loading, gameplay balance and multiplayer behavior remain unverified
in game; gameplay validation is user-operated.

Korea is also selectable: late Silla under Hyogong, with its capital at Gyeongju
and a northern regional center at Pyongyang. See [Korean starts](800BCScenario.md#korea-across-the-scenarios)
for the regional aggregation, starting assets and historical objectives.
