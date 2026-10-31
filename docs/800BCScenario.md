# 800 BC starting institutions and identities

The scenario starts on turn 87. Its ten initial major players include five
settler starts (Persia, Carthage, Rome, Japan and Korea). They are intentional early
starts, rather than proof that their later empires already existed in 800 BC.
Starting technologies and forces represent the early regional societies;
settler counts and expansion rules remain unchanged.

| Slot | Starting country identity | Displayed ruler | Government | Labor | Military | Religion |
| --- | --- | --- | --- | --- | --- | --- |
| Egypt | Pharaonic Egypt | Pharaoh Shoshenq III | Pharaonic Kingship | Slavery | Warrior Society | State Religion |
| India | Kuru and Panchala | Kesin Dalbhya | Monarchy | Self-sufficiency | Warrior Society | State Religion |
| China | Zhou Kingdom | Xuan of Zhou | Monarchy | Self-sufficiency | Warrior Society | Ancestor Cult |
| Babylonia | Kingdom of Babylon | Ninurta-apla-X | Monarchy | Slavery | Warrior Society | State Religion |
| Greece | Hellas | Ariphron | Monarchy | Slavery | Naval Warfare | Ancestor Cult |
| Persia | Persian Tribes | Achaemenes | Tribal System | Slavery | Warrior Society | Ancestor Cult |
| Carthage | Kingdom of Carthage | Dido | Monarchy | Slavery | Naval Warfare | Ancestor Cult |
| Rome | Rome | Romulus | Tribal System | Slavery | Warrior Society | Ancestor Cult |
| Japan | Jomon | Jimmu | Tribal System | Self-sufficiency | Warrior Society | Ancestor Cult |
| Korea | Gojoseon | Dangun | Tribal System | Self-sufficiency | Warrior Society | Ancestor Cult |

Carthage, Persia and Rome use Ancestor Cult rather than State Religion in this
start. For Persia and Rome this represents local and clan cults before their
later imperial religious institutions; it is a broad pagan-religion abstraction,
not a claim that ancestor worship was their only religious practice.

Review on 2026-10-20 retained the other eighth-century BC institutional choices:
Egyptian and Babylonian kingship, late Vedic and Zhou monarchy, hereditary early
Greek leadership, traditional Carthaginian kingship, and the early tribal
Persian, Roman and Japanese starts. Slavery represents an available institution,
not the labor status of the entire population. Naval Warfare represents Greek
and Phoenician seafaring, not the later Athenian naval empire. No classical
republics, medieval feudal retinues or modern institutions are imposed.

All nine use Despotism in the legitimacy column (shown as Divine Kingship for
Egypt). These are gameplay approximations of local institutions, not claims of
uniform government across the represented regions. In particular, Greek
Monarchy represents the hereditary leadership of the early polis rather than a
unified Greek kingdom. Kuru and Panchala represent the wider late Vedic north
Indian slot, whose existing cities extend beyond those kingdoms.

India, China, Greece and Carthage receive Monarchy alongside their existing
scenario technologies. No Republic, Plutocracy, Serfdom or Feudal Retinues is requested
for an 800 BC start. Greece additionally starts with Agriculture, Animal
Husbandry, Iron Working and Archery, but must research Aesthetics. Athens starts
without the Parthenon or Oracle: the Parthenon belongs to the fifth century BC,
while the Oracle represents Delphi rather than Athens. Later civilizations
keep the normal spawn profiles.

The other technology packages were revised on 2026-10-21:

| Civilization | Added technologies | Removed technologies |
| --- | --- | --- |
| Egypt | Bronze Working, Metal Casting, Mathematics, Calendar | None |
| India | Bronze Working, The Wheel, Archery, Iron Working | Writing |
| China | Bronze Working, Metal Casting, Sailing, Priesthood | None |
| Babylonia | Animal Husbandry, Mathematics, Calendar, Fishing, Sailing, Metal Casting, Iron Working | None |
| Persia | Agriculture, Iron Working | Writing, Monarchy, Monotheism |
| Carthage | Agriculture, Iron Working | None |
| Rome | Agriculture | Writing, Mathematics, Alphabet |
| Japan | Hunting, Archery | Bronze Working, Metal Casting, Meditation, Priesthood, Masonry, Monarchy, Writing |

Japan retains Agriculture as an early western-island farming abstraction, rather
than assuming uniform development across the archipelago. The Wheel is retained
solely as Pottery's game-tree prerequisite, not a claim of wheeled transport.
India's Writing is
left to research, reflecting its predominantly oral late Vedic tradition.
Calendar recipients also have its Sailing and Mathematics prerequisites; the
calendar and mathematics technologies represent broad practical knowledge.
China also receives Priesthood to complete its existing Monarchy prerequisites.

The 800 BC starting armies retain their original troop types: Greece has four
Phalanxes, Persia six Immortals, Carthage three Numidian Cavalry and an escort
Trireme, Rome four Praetorians, and China one Catapult. Japan starts with two
Warriors rather than Swordsmen, matching its lack of Iron Working in 800 BC.
The other troop substitutions from commit `1298cb9e` were reverted on 2026-10-23;
unit counts, placements and AI roles are preserved. Starting technologies and
civilian units are unchanged by this restoration. Carthage also starts with
Horseback Riding so its restored Numidian Cavalry match its technologies. In-game balance and
multiplayer behavior remain unverified.

## Independent starting technologies

Both Independent teams start with Agriculture, Animal Husbandry, Archery, Bronze Working, Fishing, Hunting, Masonry, Mining, Mysticism, Pottery and The Wheel. Their former empty technology lists prevented normal development: in the recorded 800 BC balance run `20261022-090848-c4a3c0`, Jerusalem learned Agriculture only in AD 110 and still lacked Masonry when barbarians razed it in AD 320. Workers and Walls still have to be produced normally; none are added free by this correction.

## Korea across the scenarios

Korea has a dedicated major-player slot, separate from China, Japan and the
Xiongnu. The 800 BC start provides no city: one settler, one worker, three
archers, two spearmen, a work boat and 80 gold begin near the Pyongyang site.
Its technologies cover farming, fishing, coastal sailing, pottery, hunting,
archery and bronze working. It has no starting Writing, Iron Working or wonder.

| Scenario | Korean position |
| --- | --- |
| 3000 BC | Not selectable; AI civilization with ordinary RFC birth around 800 BC, with one settler, one worker, three archers, two spearmen and a work boat. |
| 800 BC | Gojoseon with one settler near Pyongyang and no pre-founded city; choose the capital site. |
| 600 AD | Goguryeo under Yeongyang, capital Pyongyang; Gyeongju aggregates the southern kingdoms. This is not a claim that Goguryeo ruled the whole peninsula. |
| 900 AD | Silla under Hyogong, capital Gyeongju, with Pyongyang as the northern regional center. The slot aggregates the fragmented Korean states. |
| 1453 AD | Joseon under Danjong, capital Hanseong, with Uiju guarding the northern frontier; Seowon and Hwacha are available. |

The existing Korean art, leaderhead, Hwacha and Seowon are reused. Ruler labels
and briefings distinguish the historical starts from the shared leaderhead.
Country names progress through Gojoseon, Goguryeo, Silla,
Goryeo and Joseon where the date and institutions fit; republican and other
civic-driven names remain available. There is no additional cost modifier or
new unique-power mechanic.

The coastline is unchanged. Wheat at (109,46), copper at (110,47) and fish at
(111,47) supplement the existing pigs, deer, rice, silk, dye and iron. These
changes support two cities with different workable food and production tiles.
The core covers (108,45) through (110,49); the wider normal region allows a
small northern frontier without encouraging an automatic Chinese conquest.
The medieval maps use Pyongyang and Gyeongju, while the Joseon map retains
Hanseong and adds Uiju, respecting the compressed map's city spacing.
`Korea.CITY_NAMES` supplies the authored city centers. Founding and acquisition
names cover surrounding regions rather than individual tiles: Kaesong lies
north of Hanseong, Jeonju to its south, and Chuncheon occupies the northeastern
inland site formerly mislabeled Hamhung. Western border and northern approach
names include Dandong, Uiju, Ji'an, Hyesan, Hoeryong and Rason. Across China
and Manchuria, Korea reuses RFC's established geographic vocabulary and extends
nearby named regions into gaps. Coverage includes (96,32) through (111,55) and
(106,48) through (118,59), with Korean home-region overrides. These remain
regional approximations on the compressed map. Existing city names are not
retroactively rewritten; the rules apply to founding and acquisition.

Historical goals are to control two core cities with no foreign core cities by
1000 AD, build two Seowon by 1600 AD, and lose no city to conquest before 1900
while remaining independent with two core cities in 1900. In the 1453 scenario,
the already-expired first goal is failed rather than retroactively awarded.

Bronze Age chiefdoms are a regional abstraction, not a securely dated unified
Gojoseon kingdom in 800 BC. See the [National Museum of Korea](https://www.museum.go.kr/ENG/contents/E0201030400.do?schM=list&showHallId=760&showroomCode=DM0048)
and [the Met's Korean history overview](https://resources.metmuseum.org/resources/metpublications/pdf/The_Arts_of_Korea_A_Resource_for_Educators.pdf).
The [Silla catalogue](https://resources.metmuseum.org/resources/metpublications/pdf/Silla_Koreas_Golden_Kingdom.pdf)
places Hyogong in the late Silla period, rather than Goryeo's later foundation.

`tools/korea_scenarios.py` maintains the authored Korean positions and resource
changes; both later scenario generators call it. No gameplay run was started.

Profiles in `StartingCivics.py` drive both initialization and country-name
previews. Zhou (-1046 to -256), Kuru/Panchala (-1500 to -600, small monarchies)
and the pre-753 founding-era Rome identity also appear naturally in other scenarios when
their date and civic conditions fit. Their borders are approximate game naming
windows. Civic changes and vassal status continue to change country names.

Localized ruler names are authored in the map and
`CIV4GameText_Scenario800BC.xml`; existing leaderheads and personalities are
retained. The early AI leaderhead pass must not erase those custom names.
Normal later leaderhead replacements can replace the displayed ruler name.

## Historical confidence and sources

- Shoshenq III belongs to Egypt's divided Third Intermediate Period; chronologies
  vary, but his reign includes approximately 800 BC. See
  [the reign and monument references](https://pharaoh.se/ancient-egypt/pharaoh/shoshenq-iii/).
- Xuan is the appropriate Western Zhou king for 800 BC. See
  [Chinese Text Project](https://ctext.org/dictionary.pl?did=785&if=en).
- Kesin Dalbhya is a late Vedic Panchala ruler, selected as a regional
  representative. His exact reign cannot be fixed to the scenario's year.
  The game uses plain transliteration to avoid Civ4 font-symbol collisions. See
  [Michael Witzel, Early Sanskritization](https://michaelwitzel.org/wp-content/uploads/2014/06/ejvs0104article.pdf).
- Ninurta-apla-X is a poorly attested Babylonian king conventionally placed around
  800 BC; the X denotes the lost part of his name, not an ordinal. See
  [Brinkman, A Political History of Post-Kassite Babylonia](https://enenuru.net/pdfs/Brinkman%201968%20A%20Political%20History%20of%20Post-Kassite%20Babylonia%201158%E2%80%93722%20B.C._AO%2043.pdf).
- Ariphron comes from the traditional Athenian king/archon lists, not a securely
  dated contemporary inscription. See
  [the differing ancient lists](https://www.csun.edu/~hcfll004/kings-Athens.html).
- Dido (Elissa) is the traditional, legendary founder of Carthage, used as a
  recognizable early ruler rather than presented as securely documented. See
  [Oxford Classical Dictionary](https://academic.oup.com/edited-volume/61673/chapter-abstract/548725644).
- Rome starts as Rome under Romulus, treating its settler start as the legendary
  founding of the city. This is an intentional naming convention for the 800 BC
  scenario; the scenario date and starting institutions remain unchanged.
- Korea uses Dangun, Japan Jimmu and Persia Achaemenes as named early
  representatives rather than collective leadership labels. Legendary traditions
  and chronological flexibility are intentional; these choices do not assert
  that the individuals ruled in precisely 800 BC. Dangun also names Korea
  in the 3000 BC scenario before its later AI birth.

No gameplay or multiplayer test was run. New-game load validation is pending.

Jerusalem starts with Solomon's Temple (`BUILDING_JEWISH_SHRINE`) as well as
Judaism's holy city. The First Temple belongs in the 800 BC start; its traditional
dating precedes the scenario and its destruction was in 587/586 BC
([Getty record](https://www.getty.edu/cona/CONAFullSubject.aspx?subid=700009039)).
