# Dynamic country names

Independent countries use named civic types in `CvPlayer::processCivNames()`.
The rule names below are internal categories, not compulsory words in the
displayed name. Several civic combinations deliberately share a natural name:
India remains the Kingdom of India under Rule of Law, for example. Names are
authored individually rather than assembled from civic modifiers. Historical
identities are mixed with plausible alternate histories; this is a roleplaying
catalogue, not a reconstruction of each state's dates, borders, or dynasty.
Existing vassal and colonial names retain priority. The new names are stored as
translation keys, using the existing RFC name setter and save format.

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
| Other monarchies | Kingdom up to six cities; Empire above six cities |
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

`CountryNames.csv` lists 601 entries representing 388 distinct English/German
name pairs. Repeated entries are intentional. The new text
file is `Assets/XML/Text/CIV4GameText_RFCMP_CountryNames.xml`. All five Civ4 language
elements are present; French, Italian, and Spanish use English fallbacks.

To maintain the translations, edit `tools/country_name_catalog.py` and run
`tools/generate_country_names.py` with development Python 3. It generates the XML
using numeric Unicode entities for compatibility with Civ4's XML reader.

Historical references used for selected identities:

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
