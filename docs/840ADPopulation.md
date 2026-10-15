# 840 AD starting populations

City sizes represent an approximate ninth-century urban hierarchy. They are
scenario design judgments informed by historical context, not documented census
figures or a direct conversion from inhabitants to Civ4 citizens. All 50 cities
have explicit values in `POPULATIONS_840` in
[the scenario generator](../tools/generate_840_ad_scenario.py).

## Historical approach

- Chang'an (the map's Xi'an) is the largest city, ahead of Beijing. The Met
  describes Tang Chang'an as the dynasty's imperial and exceptionally populous
  center; Guangzhou was an important maritime hub.
  [Tang internationalism](https://www.metmuseum.org/essays/internationalism-in-the-tang-dynasty-618-906).
- Baghdad remains a major metropolis. Its size does not imply that it was the
  caliph's residence in exactly 840: the Abbasid court had moved to Samarra in
  836. The map has no separate Samarra city.
  [The Abbasid period](https://www.metmuseum.org/essays/the-art-of-the-abbasid-period-750-1258).
- Constantinople is much larger than its provincial cities and the small towns
  of northern Europe. Size 7 is an abstraction of its imperial urban role, not
  an assertion of a precise population. Earlier Byzantine depopulation and the
  subsequent recovery make projections from its sixth- or twelfth-century peak
  inappropriate.
  [The Byzantine Economy, eighth to tenth centuries](https://www.cambridge.org/core/books/abs/byzantine-economy/restructuring-recovery-and-controlled-expansion-early-eighth-to-tenth-centuries/5A438DB820A2D4EF2970B95BAD834704).
- Kyoto remains a substantial capital, reflecting the court's establishment
  there in 794. Edo is a small placeholder rather than its later metropolis.
  [Kyoto's history](https://kyoto.travel/en/about_kyoto.html).
- London is a modest trading settlement. Historic England estimates Lundenwic's
  peak at about 6,000-7,000 people, far below later medieval London.
  [Westminster archaeological priority areas](https://historicengland.org.uk/content/docs/planning/apa-city-of-westminster.pdf).
- Berlin and Madrid retain the mod's capital locations, but start at size 1.
  Berlin's documented founding dates to 1237; Madrid's fortified urban nucleus
  dates to the middle of the ninth century. Neither is treated as an established
  large capital in 840.
  [Berlin](https://www.berlin.de/en/history/8476760-8619314-the-medieval-trading-center.en.html),
  [Madrid historical review](https://www.madrid.es/UnidadesDescentralizadas/EducacionyJuventud/ActividadesEducativasComplementarias/MadridUnLibroAbierto/BibliotecaDigital/Capitulos/ficheros/M16MuseoHistoriaMadridIngles.pdf).

Remaining sizes are approximate regional judgments, with generally small towns
in northern Europe, stronger established trading centers, and no automatic
increase for every city since 600 AD. The inherited India/Southeast Asia map
also contains cities whose later prominence should not determine their size in
840. This pass changes populations, not settlement locations or political borders.

Constantinople receives fishing boats on its two previously unimproved nearby
fish resources and a pasture on its second sheep resource, to help support its
larger population.

The Vikings, Khmer, Spain, France, England and Germany start with lightly
developed countryside. The generator adds at most one improvement around a
size-1 city and two around larger cities, including at most one food improvement
(farm/pasture). Shared working radii count toward both cities' limits. Other
eligible tiles retain their original terrain and forests; new settlements get
cottages rather than hamlets. Improvements inherited from the 600 AD map and
intercity road connections remain. Older urban regions retain their more
developed starting countryside.

## Complete roster

| Scenario owner | City | Starting size |
| --- | --- | ---: |
| China | Beijing | 3 |
| China | Guangzhou | 5 |
| China | Guiyang | 1 |
| China | Hangzhou | 4 |
| China | Qufu | 3 |
| China | Xi'an | 9 |
| Japan | Edo | 1 |
| Japan | Kyoto | 5 |
| Vikings | Nidaros | 1 |
| Vikings | Roskilde | 1 |
| Arabia | Al-Fustat | 5 |
| Arabia | Al-Iskandariyya | 4 |
| Arabia | Al-Quds | 3 |
| Arabia | Baghdad | 8 |
| Arabia | Barqa | 1 |
| Arabia | Iskenderun | 2 |
| Arabia | Makkah | 3 |
| Arabia | Sana'a | 3 |
| Arabia | Shiraz | 4 |
| Arabia | Tarabulus | 2 |
| Khmer | Angkor | 3 |
| Spain | Barcelona | 2 |
| Spain | Madrid | 1 |
| Spain | Santiago | 1 |
| France | Bordeaux | 2 |
| France | Marseille | 2 |
| France | Paris | 3 |
| England | London | 2 |
| England | York | 2 |
| Germany | Berlin | 1 |
| Germany | Frankfurt | 3 |
| Independent | Delhi | 3 |
| Independent | Hanseong | 3 |
| Independent | Inbhir Nis | 1 |
| Independent | Merv | 3 |
| Independent | Mumbai | 1 |
| Independent | Pagan | 2 |
| Independent | Samarqand | 4 |
| Independent | Venetia | 3 |
| Independent II | Aksum | 2 |
| Independent II | Cordoba | 5 |
| Independent II | Kandahar | 3 |
| Independent II | Patliputra | 3 |
| Independent II | Roma | 3 |
| Native | Chich'en Itz&#225; | 3 |
| Native | Yax Mutal | 2 |
| Byzantium | Athenae | 2 |
| Byzantium | Constantinopolis | 7 |
| Byzantium | Iconium | 3 |
| Byzantium | Trapezus | 3 |

## Starting units

Capital reinforcements are tailored to settlement space and existing city count.
These are gameplay packages, not reconstructions of historical army strengths.
The table lists extras beyond each city's garrison; inherited garrisons remain,
and previously empty active-player cities receive an archer.

| Civilization | Workers | Capital troops | Settlers | Ships |
| --- | ---: | --- | ---: | --- |
| China | 3 | 1 Cho-Ko-Nu, 1 swordsman | 0 | 1 work boat at Guangzhou |
| Japan | 2 | 2 swordsmen | 1 | 1 galley, 1 work boat |
| Vikings | 1 | 2 swordsmen | 1 | 2 galleys, 1 work boat |
| Arabia | 3 | 2 camel archers | 0 | None |
| Khmer | 2 | 1 swordsman, 1 spearman | 1 | None |
| Spain | 2 | 1 swordsman, 1 horse archer | 0 | 1 work boat at Barcelona |
| France | 2 | 1 swordsman, 1 horse archer | 0 | 1 work boat at Marseille |
| England | 2 | 2 swordsmen | 0 | 1 galley, 1 work boat |
| Germany | 2 | 1 swordsman, 1 horse archer | 1 | None |

Settlers support nearby expansion for Japan, the Vikings, Khmer and Germany.
Spain's starting towns and independent Cordoba already occupy much of Iberia;
France, England, China and Arabia begin with established city networks rather
than receiving another blanket settler. Ships start on adjacent coastal water.
