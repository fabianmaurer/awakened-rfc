# 800 BC starting institutions and identities

The scenario starts on turn 87. Its nine initial major players include four
settler starts (Persia, Carthage, Rome and Japan). They are intentional early
starts, rather than proof that their later empires already existed in 800 BC.
The map, forces and expansion rules are unchanged by this audit.

| Slot | Starting country identity | Displayed ruler | Government | Labor | Military | Religion |
| --- | --- | --- | --- | --- | --- | --- |
| Egypt | Pharaonic Egypt | Pharaoh Shoshenq III | Pharaonic Kingship | Slavery | Militia | State Religion |
| India | Kuru and Panchala | Kesin Dalbhya | Monarchy | Self-sufficiency | Warrior Society | State Religion |
| China | Zhou Kingdom | Xuan of Zhou | Monarchy | Self-sufficiency | Militia | Ancestor Cult |
| Babylonia | Kingdom of Babylon | Ninurta-apla-X | Monarchy | Slavery | Militia | State Religion |
| Greece | Greek City-States | Ariphron | Monarchy | Slavery | Warrior Society | Ancestor Cult |
| Persia | Iranian Tribes | Persian tribal chiefs | Tribal System | Slavery | Militia | State Religion |
| Carthage | Kingdom of Carthage | Elissa | Monarchy | Slavery | Militia | State Religion |
| Rome | Latin Communities | Latin tribal elders | Tribal System | Slavery | Warrior Society | State Religion |
| Japan | Peoples of the Japanese Islands | Japanese clan elders | Tribal System | Self-sufficiency | Warrior Society | Ancestor Cult |

All nine use Despotism in the legitimacy column (shown as Divine Kingship for
Egypt). These are gameplay approximations of local institutions, not claims of
uniform government across the represented regions. In particular, Greek
Monarchy represents the hereditary leadership of the early polis rather than a
unified Greek kingdom. Kuru and Panchala represent the wider late Vedic north
Indian slot, whose existing cities extend beyond those kingdoms.

India, China, Greece and Carthage receive Monarchy alongside their existing
scenario technologies. No Republic, Plutocracy, Serfdom or Knighthood is requested
for an 800 BC start. The original technology packages, including their broader
historical simplifications, are otherwise retained. Egypt still has its unique
early access to Slavery. Later civilizations keep the normal spawn profiles.

Profiles in `StartingCivics.py` drive both initialization and country-name
previews. Zhou (-1046 to -256), Kuru/Panchala (-1500 to -600, small monarchies)
and pre-753 Latin communities also appear naturally in other scenarios when
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
- Elissa (Dido) is the traditional, legendary founder of Carthage, used as a
  recognizable early ruler rather than presented as securely documented. See
  [Oxford Classical Dictionary](https://academic.oup.com/edited-volume/61673/chapter-abstract/548725644).
- Persia, the Latin communities and Japan have collective leadership labels
  because no individual ruler can be securely assigned here to 800 BC. Cyrus,
  Augustus and Tokugawa would be substantially anachronistic.

No gameplay or multiplayer test was run. New-game load validation is pending.
