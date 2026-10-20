# Dynamic country names

Theocracy combined with State Atheism selects a bespoke **ATHEOCRACY** name
for each of the 28 naming civilizations, including the Huns, regardless of government or era. These
are deliberately fictional enforced creeds of reason, such as the Roman
**Pontificate of Reason**, German **Holy Empire of Reason**, and Egyptian
**Order of the Godless Sun**. This combination overrides the usual independent
government and historical names, including Egypt's Temple State. Existing
vassal and colonial naming takes priority as usual. English and German names
are authored in `tools/country_name_catalog.py`; other languages currently use
the English names.

Independent countries use named civic types in `CvPlayer::processCivNames()`.
The rule names below are internal categories, not compulsory words in the
displayed name. Several civic combinations deliberately share a natural name:
India remains the Kingdom of India under Rule of Law, for example. Names are
authored individually rather than assembled from civic modifiers. Historical
identities are mixed with plausible alternate histories; this is a roleplaying
catalogue, not a reconstruction of each state's dates, borders, or dynasty.
Existing vassal and colonial names retain priority. The new names are stored as
translation keys, using the existing RFC name setter and save format.

The Huns use the same government, religion and economy rules under code `XIO`.
Examples include **The Huns / Die Hunnen** under Tribal
System, **Realm of the Chanyu / Reich des Chanyu** under ordinary monarchy,
**Hunnic Empire / Hunnenreich** above six cities, and **Hunnic Federation /
Hunnischer Bund** under a republic. Other possibilities include **Union of the
Steppe**, **League of the Steppe Routes**, and **Sacred Realm of the Eternal Sky**.
These include alternate-history names; no dynasty or territorial change is
forced. The unsuffixed legacy base key is preserved when constructing Hun keys.

Egypt's Tribal System variant is Pharaonic Kingship, and its Despotism variant
is Divine Kingship, without date or religion gates. Independent Egypt using
Pharaonic Kingship is named **Pharaonic Egypt / Pharaonenreich**. Theocracy or
God State instead selects **Temple State of Egypt / Tempelstaat Ägypten**, even
before a state religion is adopted. Other Egyptian government forms retain their
existing country-name rules. The displayed leader under Pharaonic Kingship is
**Pharaoh [personal name]**; this title is computed for display and not saved as
a replacement personal name.

Rules are evaluated in this order:

| Condition | Name family |
| --- | --- |
| Tribal System without a religious government | Tribal Confederation |
| State religion and Holy State or Theocratic Legitimacy | Holy Kingdom, Theocracy, or Theocratic Republic according to government; Islamic rulers use Caliphate or Islamic Republic |
| Monarchy, Islam, and State Religion | Sultanate |
| Monarchy and Rule of Law | Constitutional Kingdom |
| Monarchy with Planned Economy and Plutocracy | Plutocratic Planned State |
| Other monarchies with Planned Economy | Royal Planned Economy |
| Other monarchies | Kingdom up to six cities; Empire above six cities |
| Planned Economy with Plutocracy, under Republic, Democracy or Dictatorship | Plutocratic Planned State |
| Planned Economy with Democracy | Democratic Socialist Republic |
| Planned Economy with Republic | Socialist Republic |
| Planned Economy with Dictatorship | People's State |
| Dictatorship and Nationalism | National State |
| Other dictatorships with Professional Army or Conscription | Military Government |
| Other dictatorships | State |
| Republic or Democracy with State Atheism | Secular Republic |
| Republic or Democracy with Islam and State Religion | Islamic Republic |
| Republic or Democracy with Plutocracy | Merchant Republic |
| Republic or Democracy with Nationalism | National Republic |
| Other Republic or Democracy | Republic or Democratic Republic |

Religious naming requires an actual state religion. A professional army alone
does not make a democracy a military government. Planned Economy does not turn
a monarchy into a republic. Constitutional monarchies keep their name at any
size. Religion and economics take priority over nationalism when both apply.

Country-specific alternatives include the Hanseatic League, Middle Kingdom,
Celestial Empire, Heavenly Kingdom of Great Peace, Land of the Four Quarters,
Regno d'Italia, Commonwealth of England, Batavian Republic, Novgorod Republic,
North Sea Empire, Tawantinsuyu, and the United Kingdom. Invented alternatives include the Nile
League, League of the Jade Cities, Andean Federation, and Union of Bharat.
Before 962, Germany's ordinary or Christian religious monarchy uses East Francia
(Ostfränkisches Reich). From 962 onward the usual
civic and religious names apply. Constitutional and alternate religious titles
remain available before that date.
The period rules and the audit of the starting scenarios are recorded in
`docs/ScenarioCountryNamesAudit.md`. They change names only, preserve vassal
priority, and retain alternate civic and religious outcomes.
Germany uses the Holy Roman Empire for a Christian religious monarchy. Rome
uses the Papal States for a Christian religious government which is not a
Republic or Democracy. Other state religions use the ordinary country entries.

China uses **Celestial Empire** for a monarchy with more than six cities, and
**Heavenly Kingdom of Great Peace** for a non-Islamic religious monarchy or
theocracy. A religious republic uses the alternate-history **Commonwealth of
Great Peace**. The Taiping-inspired title follows the civic family rather than
requiring Christianity or a particular historical date.

The Inca use **Kingdom of Cusco / Königreich Cusco** for a smaller or
constitutional monarchy and **Land of the Four Quarters / Land der vier
Weltgegenden** for a larger empire. **Tawantinsuyu** is the Quechua name for
the same imperial identity, rather than a separate civic outcome. Religious rulers use
**Realm of the Sun**. Rome's constitutional monarchy becomes **Regno d'Italia**;
its nationalist republic uses **Repubblica Italiana**. Ancient Rome's ordinary
kingdom, empire, and republican names remain available.

America's tribal form is **American Settlements / Amerikanische Siedlungen**,
reflecting its settler-founded identity rather than implying an indigenous
people. The Maya, Inca and Aztecs retain their indigenous tribal identities;
European colonial powers retain names for their own homelands.

American religious forms use **Kingdom of Providence / Königreich der Vorsehung**
for a religious monarchy, **State of Deseret / Staat Deseret** for a theocracy,
and **Puritan Commonwealth / Puritanisches Gemeinwesen** for a religious republic.
The kingdom is an invented alternate-history title; Deseret and the Puritan
commonwealth provide historical inspiration. These names follow the existing
non-Islamic religious families: the game does not distinguish Amish, Puritan
or Mormon denominations, nor require their original historical locations.
An Amish kingdom was avoided because Amish church/state separation makes it
a weaker model for a religious government.

Other evocative titles include Egypt's **Realm of the Two Lands**, Persia's
**Empire of the King of Kings**, Japan's religious **Land of the Gods**, and
Greece's merchant **Delian League**. Some names are literary adaptations of
historical titles; their civic mappings are roleplaying choices.

### Crown economies and plutocratic planning

Two additional families cover Planned Economy: **ROYAL_PLANNED** for Monarchy,
and **PLUTOCRATIC_PLANNED** for Plutocracy under Monarchy, Republic, Democracy
or Dictatorship. Each has 27 authored English/German entries. Plutocracy takes
priority when both combinations apply. Tribal governments retain tribal names;
religious governments, sultanates, constitutional monarchies, and the existing
period-specific historical overrides retain their priority. Egypt's Temple State
and the atheist theocracy also retain priority. Vassal/colonial rules are unchanged.
Scenario previews and live names use the same classifier.

The crown family describes a monarch directing a common economy, with names
such as **Imperial Economic Union of China / Kaiserliche Wirtschaftsunion
China**, **French Manufactory Monarchy / Französische Manufakturmonarchie**,
**Royal Polder Union / Königliche Polderunion**, and **United Crown Industries
of America / Vereinigte Kronwerke Amerikas**. Names evoke particular economic
institutions rather than repeating a common crown-union template. The Inca
retain **Land of the Four Quarters** rather than receiving a new economic label.

The plutocratic family imagines wealthy houses jointly controlling the plan:
**Directorate of the Seven Houses / Direktorium der Sieben Häuser** for Carthage,
**German Cartel Union / Deutscher Kartellbund**, **United Netherlandish Company /
Vereinigte Niederländische Kompanie**, and **American Corporate Collective /
Amerikanisches Konzernkollektiv**. Other examples include **Babylonian Canal
Company / Babylonische Kanalgesellschaft** and **Portuguese Spice Monopoly /
Portugiesisches Gewürzmonopol**. These are fictional alternate-history identities, not
claims that the named historical societies used the game's Planned Economy.
They avoid compulsory republican titles so they can also name monarchies.

Naming does not alter stability. Monarchy + Planned Economy remains neutral;
Plutocracy + Planned Economy retains its small -1 contribution, waived under
Democracy along with other negative civic-combination contributions. A ruling
elite can direct a plan, but its private wealth interests can still conflict with
central allocation. The names acknowledge a possible institutional arrangement
without granting it an automatic stability bonus.

### Military regimes

Every civilization has an individually authored `MILITARY` title rather than
inheriting its ordinary dictatorship name. This family applies to Dictatorship
with Professional Army or Conscription, unless religion, Planned Economy, or
Nationalism selects a higher-priority family. Those other families retain their
own names.

Examples include **Mamluk Realm**, **Punic Hegemony**, **Roman Imperium**,
**French Consulate**, **Celestial Directorate**, **Batavian Protectorate**,
**Jaguar Realm**, **Great Mongol Horde**, and **Continental Protectorate**.
The Japanese Shogunate, English Protectorate, and German Reich remain available.
Names such as Batavian Protectorate and Jaguar Realm are invented
alternate-history identities. Mamluk Realm and French Consulate draw on
historical institutions without requiring their historical dates or borders.

English and German titles describe the same institutions, with natural phrasing
in each language: examples include **Mamlukenreich**, **Babylonisches
Imperium**, **Kaiserreich Iran**, **Nordreich**, **Reich des Kondors**, and
**Anatolisches Militärdirektorium**. Existing titles such as Punische Hegemonie,
Französisches Konsulat, Japanisches Shogunat, and Batavisches Protektorat retain
their different institutional character.

Civic changes and conversions refresh names through the original event hooks.
Names also refresh once per player turn, including in existing saves. The five
authored scenario selection screens preview country names using the same DLL
classifier, with the intended profiles from `StartingCivics.PROFILES`, authored
state religions, and authored city counts. These are starting-profile previews;
technology restrictions and subsequent gameplay may produce a different name
in play. `ScenarioCountryNames.py` supplies the preview descriptions through
`CvWBInterface.getPlayerDesc`, without modifying scenario files or player state.
Country short names and nationality adjectives use the original RFC text.
Name selection does not depend on UI language or random numbers.

`CountryNames.csv` lists 710 entries representing 495 distinct English/German
name pairs. Repeated entries are intentional. The new text
file is `Assets/XML/Text/CIV4GameText_RFCMP_CountryNames.xml`. All five Civ4 language
elements are present; French, Italian, and Spanish use English fallbacks.

To maintain the translations, edit `tools/country_name_catalog.py` and run
`tools/generate_country_names.py` with development Python 3. It generates the XML
using numeric Unicode entities for compatibility with Civ4's XML reader.

Historical references used for selected identities:

The major-empire coverage, additional period windows, and their references are
listed in [HistoricalEmpireNames.md](HistoricalEmpireNames.md). Russia's
**PEOPLES_STATE** title is **Union of Soviet Socialist Republics / Union der
Sozialistischen Sowjetrepubliken** (USSR / UdSSR). This applies to Dictatorship
with Planned Economy under the ordinary classifier, without a date or size gate.
Religious naming and Plutocracy + Planned Economy keep their higher priority.
Republic + Planned Economy retains **Russian Soviet Republic**.

Germany's ordinary **NATIONAL_STATE** name becomes **Greater German Reich /
Großdeutsches Reich** under Dictatorship + Nationalism with at least **100 owned
land plots** (`CvPlayer::getTotalLand`). Overseas land counts; water and vassal
territory do not. Below 100 plots it remains **German Reich / Deutsches Reich**.
The rule has no date, Vienna or city-count condition. Religious and planned
economy names, and vassal/colonial names, retain priority. The ordinary turn
refresh changes the name again after territory is lost or civics change.
Scenario previews pass zero land plots because WB descriptions do not contain
resolved cultural borders; they show the base name until the live map is built.

- [The Hanseatic League, European Hansemuseum](https://www.hansemuseum.eu/en/)
- [Batavian Republic, Dutch National Archives](https://www.nationaalarchief.nl/beleven/onderwijs/bronnenbox/bataafse-revolutie-1795)
- [Commonwealth of England, UK National Archives](https://www.nationalarchives.gov.uk/education/students/videos/history-hook/christmas-is-cancelled/)
- [Holy Roman Empire, German Historical Museum](https://www.dhm.de/publikation/heiliges-roemisches-reich-deutscher-nation-962-1806/)
- [Papal States, Vatican City State](https://www.vaticanstate.va/en/state-and-government/general-informations/flag.html)
- [Celestial Empire, National Library of Australia](https://www.library.gov.au/learn/digital-classroom/celestial-empire/contact-and-conflict)
- [Taiping Heavenly Kingdom correspondence, US Office of the Historian](https://history.state.gov/historicaldocuments/frus1862/d669)
- [Tawantinsuyu and its four regions, NIST Museum](https://www.nist.gov/nist-museum/standardizing-empire)
- [Regno d'Italia, Italian Presidency](https://www.quirinale.it/it/comunicato/dichiarazione-presidente-mattarella-occasione-giornata-nazionale-bandiera)
- [Egypt's Two Lands, Louvre](https://www.louvre.fr/en/exhibitions-and-events/exhibitions/pharaoh-of-the-two-lands)
- [Persian King of Kings, British Museum](https://www.britishmuseum.org/blog/long-live-king-kings-accession-ritual-ancient-persia)
- [Mamluk military elite, Metropolitan Museum of Art](https://www.metmuseum.org/de/toah/ht/08/afe)
- [French Consulate and the coup of Brumaire, Fondation Napoléon](https://www.napoleon.org/en/history-of-the-two-empires/close-up/the-coup-detat-of-18-and-19-brumaire-an-viii-9-and-10-november1799)
- [Cromwell's army and Protectorate, National Army Museum](https://www.nam.ac.uk/explore/british-civil-wars)
- [State of Deseret, Utah Division of Archives and Records Service](https://archives.utah.gov/research/entities/5548/)
- [Puritan Commonwealth, National Park Service](https://home.nps.gov/bost/learn/historyculture/puritans.htm)
- [Amish separation of church and government, Associated Press](https://apnews.com/article/02879042c8ee425c345daa971ecd341e)
