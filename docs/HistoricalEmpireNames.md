# Historical empire names

The country-name catalogue includes historical imperial identities alongside
alternate civic outcomes. A title must be reachable through the DLL classifier,
not merely present as an unused translation key. The shared classifier also
supplies scenario previews. Dates below are naming windows, not scripted
dynasties, conquests, territorial checks or assertions of continuous historical
rule. The start is inclusive and the end exclusive; negative years are BC.

## Additions

| Civilization | German title | Naming window | Civic conditions |
| --- | --- | --- | --- |
| Russia | Union der Sozialistischen Sowjetrepubliken | Any date | Dictatorship + Planned Economy, ordinary People's State family |
| Germany | Großdeutsches Reich | Any date | Dictatorship + Nationalism, ordinary National State family, at least 100 owned land plots |
| France | Karolingerreich | 800 to 843 | Existing ordinary/Christian monarchy condition |
| China | Qin-Reich | -221 to -206 | Ordinary monarchy |
| China | Han-Reich | -206 to 220 | Ordinary monarchy |
| China | Tang-Reich | 618 to 907 | Ordinary monarchy |
| China | Song-Reich | 960 to 1271 | Ordinary monarchy |
| China | Yuan-Reich | 1271 to 1368 | Ordinary monarchy |
| China | Qing-Reich | 1644 to 1912 | Ordinary monarchy |
| India | Maurya-Reich | -321 to -185 | Ordinary monarchy |
| India | Gupta-Reich | 320 to 550 | Ordinary monarchy |
| India | Mogulreich | 1526 to 1858 | Islamic monarchy without Rule of Law |
| Persia | Achämenidenreich | -550 to -330 | Ordinary monarchy |
| Persia | Partherreich | -247 to 224 | Ordinary monarchy |
| Persia | Sassanidenreich | 224 to 651 | Ordinary monarchy |
| Persia | Safawidenreich | 1507 to 1722 | Islamic monarchy without Rule of Law |
| Greece | Makedonisches Weltreich | -336 to -323 | Ordinary monarchy with more than six cities |
| Arabia | Umayyadenkalifat | 661 to 750 | Islamic religious monarchy selecting Caliphate |
| Arabia | Abbasidenkalifat | 750 to 1258 | Islamic religious monarchy selecting Caliphate |

Ordinary monarchy means Monarchy without Rule of Law, Islamic state religion,
or the religious-government condition. It retains the existing priority of
historical period names over the new crown/plutocratic economic names.
Islamic period names require an actual Islamic state religion. Republics,
democracies and dictatorships do not receive these monarchical dynasty names.
The USSR replaces only Russia's People's State entry; the Russian Soviet
Republic remains the republican planned-economy identity. Religious and
plutocratic planning names continue to take precedence over People's State.

Song and Yuan overlapped historically; the classifier selects Yuan from 1271
and does not simulate simultaneous rival Chinese dynasties. The Safavid window
starts in 1507 to follow the existing Timurid window without overlap, rather
than using the dynasty's foundation in 1501. The Han and Tang windows abstract
their internal interruptions. Qing ends at the 1912 abdication boundary.
No stability, combat, production or other gameplay values change.

Germany's territorial variant counts its own land plots, including overseas
territory, using `CvPlayer::getTotalLand()`. Water and vassals' plots do not count.
It uses no Vienna/other fixed location check and no historical date gate. Below
100 land plots, the ordinary nationalist dictatorship remains **Deutsches
Reich**. Religious and planned-economy naming retain priority. Existing refresh
hooks and the per-turn refresh update the title as territory/civics change.
The scenario menu uses the base name because the WB descriptions have not yet
resolved cultural borders. This size threshold is a game naming choice, not a
historical definition of the term.

## Existing coverage and scope

Existing families already provide the Roman Empire, Holy Roman Empire,
German Empire, Russian Empire, French Empire, British Empire, Spanish Empire,
Portuguese Empire, Dutch Empire, Ottoman Empire, Mongol Empire, Mali Empire,
Khmer Empire, Ethiopian/Abyssinian Empire, Japanese Empire, Aztec Triple
Alliance and the Inca's Land of the Four Quarters. Period names already cover
Ming, northern Yuan, the Timurids, the Mamluks and Delhi, among others.
Byzantium has its own civilization identity outside the 27 major naming slots.

This is coverage of the represented civilizations, not a claim to include every
historical empire. Empires without a corresponding major slot, such as Austria,
Assyria or the Hittites, are not assigned to an unrelated civilization merely
to include their names. Habsburg Netherlands already exists as a regional name;
it does not stand for the Austrian or Austro-Hungarian Empire.

## References

- [Met: Qin and Han](https://www.metmuseum.org/fr/exhibitions/listings/2017/age-of-empires)
- [Met: Chinese chronology, including Han and Tang](https://resources.metmuseum.org/resources/metpublications/pdf/Cultural_Convergence_in_the_Northern_Qi_Period_A_Flamboyant_Chinese_Ceramic_Container_a_research.pdf)
- [Princeton University Art Museum: Chinese timeline](https://static.artmuseum.princeton.edu/asian-art/china/timeline)
- [Met: Yuan, 1271–1368](https://www.metmuseum.org/ja/essays/yuan-dynasty-1271-1368)
- [Chinese and Ethnographic Museum, Parma: Qing and the 1912 abdication](https://www.museocineseparma.org/en/scuole/le-dinastie-della-cina/119-1644-1911-qing-dynasty)
- [Met: Maurya and Gupta chronology](https://resources.metmuseum.org/resources/metpublications/pdf/The_Year_One_Art_of_the_Ancient_World_East_and_West.pdf)
- [Met: Mughal introduction, 1526–1858](https://www.metmuseum.org/it/learn/educators/curriculum-resources/art-of-the-islamic-world/unit-five/chapter-four/introduction)
- [Asian Art Museum: Achaemenid period](https://exhibitions.asianart.org/exhibitions/the-cyrus-cylinder-and-ancient-persia-a-new-beginning/)
- [Met: Parthian Empire, 247 BC–224 AD](https://www.metmuseum.org/de/essays/the-parthian-empire-247-b-c-224-a-d)
- [Met: Sasanian period, 224–651](https://www.metmuseum.org/art/collection/search/325710)
- [Met: Safavids, 1501–1722](https://www.metmuseum.org/exhibitions/listings/2003/persian-silks)
- [Met: Alexander and Macedon](https://www.metmuseum.org/ru/essays/the-rise-of-macedonia-and-the-conquests-of-alexander-the-great)
- [Met: Umayyads, 661–750](https://www.metmuseum.org/ja/essays/the-art-of-the-umayyad-period-661-750)
- [Met: Abbasids, 750–1258](https://www.metmuseum.org/de/essays/the-art-of-the-abbasid-period-750-1258)
- [DHM: Carolingian empire and Verdun](https://www.dhm.de/mediathek/der-rhein-von-basel-bis-koblenz/deutsch-franzoesische-geschichte-am-rhein/strassburger-eide/)
