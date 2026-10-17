# Awakened RFC — Spielregeln

[English](../README.md) | **Deutsch**

Eine auf Mehrspielerpartien ausgerichtete Überarbeitung von **Rhye's and Fall
Multiplayer** für **Civilization IV: Beyond the Sword**. Sie bietet fünf
Staatsformen-Kategorien, Stabilität durch passende Staatsformen-Kombinationen,
Vorwarnungen vor der Entstehung neuer Zivilisationen und dynamische Ländernamen.

Diese README beschreibt die Spieländerungen dieses Projekts. Weltkarten,
historische Gründungszeitpunkte, einzigartige Fähigkeiten, Siegziele und weitere
Systeme aus dem ursprünglichen RFC MP bilden weiterhin die Grundlage.

## Historische Wunderbedingungen

Diese zusätzlichen Voraussetzungen gelten gleichermaßen für Menschen und KI. Regionen beziehen sich auf die RFC-Weltkarte und sind unabhängig von Zivilisation und Besitzer. Bestehende Technologie-, Ressourcen- und Gebäudevoraussetzungen gelten weiterhin. Religionen müssen in der Stadt vorhanden sein; sie müssen keine Staatsreligion sein. Staatsformbedingungen gelten auch für laufende Bauaufträge; fertige Wunder behalten ihre Wirkung nach einem Staatsformwechsel.

| Wunder | Zusätzliche Voraussetzung |
| --- | --- |
| Großer Leuchtturm, Koloss | Mittelmeerküste |
| Parthenon, Artemistempel, Zeusstatue, Mausoleum von Maussollos | Mittelmeerraum |
| Tempel des Kukulkan (Chichén Itzá) | Mesoamerika (Mexiko / Mittelamerika) |
| Große Mauer | Ostasien |
| Moai-Statuen | Pazifikküste oder Pazifikinsel |
| Pyramiden | Mindestens ein Wüstenfeld im Stadtradius, einschließlich Stadtfeld |
| Hängende Gärten | Stadt an einem Fluss |
| Shwedagon-Pagode | Buddhismus in der Stadt |
| Angkor Wat | Hinduismus in der Stadt |
| Hagia Sophia, Sixtinische Kapelle, Notre Dame, Cristo Redentor | Christentum in der Stadt |
| Spiralminarett, Universität von Sankore, Taj Mahal | Islam in der Stadt |
| Versailles | Monarchie während des Baus |
| Freiheitsstatue | Küstenstadt; Republik oder Demokratie während des Baus |
| Kreml | Hauptstadt |
| Große Bibliothek | Bibliothek in der Stadt |
| Pentagon | Kaserne in der Stadt |
| Wembley | Kolosseum in der Stadt |
| Graceland, Hollywood | Theater in der Stadt |

## Spieländerungen im Überblick

- **25 Staatsformen in fünf Kategorien:** Regierung, Legitimation, Arbeit,
  Militär und Religion ersetzen die bisherigen sechs Kategorien. Der Bildschirm
  nutzt die verfügbare Breite und enthält neue Illustrationen.
- **Demokratische Wahlen:** Alle zehn Runden wird eine andere Kategorie auf eine
  zufällig ausgewählte verfügbare Staatsform umgestellt.
- **Start-Staatsformen:** Jede Zivilisation erhält ein Profil passend zu ihrer
  Zeit, soweit die Starttechnologien des Szenarios oder der Gründung es erlauben.
- **Stabilität durch Kombinationen:** Passende Institutionen erhalten kleine
  Boni; Theokratie mit Toleranz erhält einen Malus. Die Summe ist begrenzt.
- **Vorwarnungen vor Gebietswechseln:** Feld-Tooltips zeigen zukünftige
  Zivilisationen, deren Kerngebiet das Feld einschließt. Städte erhalten drei
  Runden vor dem Wechsel Unruhen.
- **Dynamische Ländernamen:** Deutsche und englische Namen reagieren auf
  Staatsformen, Religion, Reichsgröße sowie Vasallen- und Kolonialverhältnisse.
- **Einheitliche Produktionskosten:** Die individuellen Produktionskosten-
  Multiplikatoren der spielbaren Zivilisationen für Einheiten und Gebäude entfallen.
- **Einheitlichere Forschung:** Die individuelle Forschungskosten-Tabelle
  entfällt. Gemeinsame Anpassungen für Szenarien, Zeitverlauf und menschliche
  beziehungsweise KI-Spieler bleiben erhalten.
- **Keine Inflation:** Die Inflationsrate bleibt bei null.
- **Kulturaufstände:** Fremder kultureller Druck führt zu Bevölkerungsverlust und
  barbarischen Rebellen statt zum direkten Überlaufen einer nichtbarbarischen Stadt.

### Umfang der Vereinheitlichung

Spielbare Zivilisationen verwenden gemeinsame Grundberechnungen für
**Stadtwachstum, Schwellen für Große Persönlichkeiten und Große Generäle,
Kulturzuwachs, Einheitenunterhalt, Städteunterhalt, Staatsformen-Unterhalt und
Gesundheit**. Malis individuelle Anpassung der Wirtschaftsstabilität und der
individuelle Rabatt der Türkei auf die Aufstandswahrscheinlichkeit entfallen.

Gemeinsame Gruppenmodifikatoren bleiben erhalten, darunter Szenario-Anpassungen
für frühe Zivilisationen, der Forschungsrabatt für China/Japan und regionale
sowie wirtschaftliche Stabilitätsregeln. Einzigartige Einheiten, Gebäude,
Fähigkeiten und historische Gründungszeitpunkte unterscheiden die Zivilisationen
weiterhin. Sonderregeln für kleinere Fraktionen bleiben separat bestehen.

Einzigartige Fähigkeiten gelten unabhängig von den gemeinsamen Grundkosten.
China bildet Nahkampf- und Schießpulvereinheiten mit **1,5-facher Geschwindigkeit**
aus; die Maya haben **40% geringere Forschungskosten bis zum Ende des Mittelalters**;
Persien erhält **+2 Stabilität je eroberter Stadt**.

## Technologieabhängiges Wachstum

Alle Zivilisationen haben einen **Wachstumsmalus von 30% auf den positiven
Nahrungsüberschuss**, der je unterschiedlicher bekannter Technologie um
**0,5 Prozentpunkte** sinkt. Ab 60 Technologien entfällt er; ein Bonus entsteht
nicht. Starttechnologien und erworbene Technologien zählen ebenso wie erforschte.
Wiederholbare Technologien zählen nur einmal. Maßgeblich ist der Wissensstand
des Teams, entsprechend dem normalen Technologiesystem.

| Bekannte Technologien | Wachstumsmalus |
| --- | --- |
| 0 | 30% |
| 2 | 29% |
| 20 | 20% |
| 40 | 10% |
| 60+ | Keiner |

Beispiel: Vier Nahrungsüberschuss bringen bei zwei bekannten Technologien
**2,84 Nahrung** pro Runde für das Wachstum. Nachkommastellen werden intern
erhalten und gespeichert. Wachstumsdauer und Nahrungsbalken verwenden den
angepassten Wert; der Tooltip des Bevölkerungsbalkens zeigt Malus und Wachstum.

Nahrungsproduktion, Verbrauch, Handelstransfers, Hunger und Nahrung für
Siedler/Bautrupps bleiben unverändert. Der Malus greift nach Handel und Verbrauch,
also auch auf positiven Überschuss aus importierter Nahrung. Bestehende gemeinsame
Wachstumsschwellen und die Nahrungserhaltung durch Kornspeicher bleiben bestehen.

`RFCMP_GROWTH_BASE_PENALTY_TIMES100` (3000) und
`RFCMP_GROWTH_TECH_REDUCTION_TIMES100` (50) in `Assets/XML/GlobalDefines.xml`
verwenden Hundertstel eines Prozentpunkts. Bestehende Spielstände beginnen ohne
gespeicherten Nachkommarest und verwenden den neuen Malus sofort.

## Landerschließung

- **Oasen** liefern **2 Nahrung und 2 Handel** und erlauben ausschließlich
  **Bauernhöfe** ab Landwirtschaft. Die Oase bleibt erhalten und liefert das
  nötige Süßwasser; mit Bauernhof ergibt das normalerweise **3 Nahrung und
  2 Handel**, mit Biologie **4 Nahrung und 2 Handel**.
- **Bauernhöfe auf Schwemmland** benötigen nur Landwirtschaft und die üblichen
  Voraussetzungen für Bauernhöfe. Das Schwemmland bleibt erhalten; es gibt keine
  zusätzliche Technologie oder zusätzliche Bauzeit für dieses Geländemerkmal.
- **Sumpf trockenlegen** steht Bautrupps und indischen Schnellen Bautrupps ab
  **Maschinenbau** innerhalb des eigenen Teamgebiets zur Verfügung. Die Aktion
  wandelt Sumpfgelände in Grasland um, entfernt das Schlamm-Geländemerkmal und die
  zusätzliche Sumpfdarstellung und liefert **keine Produktion**. Normale
  Verbesserungen können anschließend separat errichtet werden.
- Trockenlegen benötigt **1200 Basis-Arbeitspunkte**, normalerweise zwölf Runden
  für einen normalen Bautrupp vor Spieltempo-, Szenario-Epochen- und
  Arbeitsgeschwindigkeits-Modifikatoren. KI und automatisierte Bautrupps
  berücksichtigen den Ertrag des erschlossenen Landes bei ihrer Aktionswahl.

## Produktionskonvertierungen

| Konvertierung | Voraussetzung | Effektivität |
| --- | --- | --- |
| Warenverkauf | Keine; von Beginn an verfügbar | 25% Produktion in Gold |
| Wohlstand | Währung | 50% Produktion in Gold |
| Forschung | Alphabet | 25% Produktion in Forschung |
| Kultur | Musik | 50% Produktion in Kultur |

Währung ersetzt Warenverkauf durch Wohlstand. Laufende
und vorgemerkte Warenverkaufsaufträge werden automatisch umgestellt;
andere Aufträge in der Produktionsliste bleiben erhalten. Die Werte gelten
einheitlich für alle Zivilisationen und Spieler.

## Handelsrouten, Militärzugang und Embargos

Städte können auch unbekannte Städte als Handelspartner wählen. Sobald eine
Route ausgewählt wird, wird das Stadtfeld der Partnerstadt für das Team des
Routenbesitzers aufgedeckt.

- **Häfen sind auch eine Landkachel hinter einer Meeresküste baubar**, einschließlich
  einzigartiger Ersatzgebäude wie des Kothons. Ihr bestehender Nahrungsbonus gilt
  für bearbeitete Wasserfelder. Schiffe können dort weiterhin nicht gebaut werden.
- Bekannte Städte handeln auch ohne Straßen oder Militärzugangsabkommen.
  Die üblichen Routenbegrenzungen, Krieg, städtische Unruhen, Blockaden und
  Staatsformen-Einschränkungen bleiben wirksam. Ohne Infrastruktur beträgt die
  **Effektivität 50% bis Entfernung 5**, danach linear fünf Prozentpunkte weniger
  pro zusätzlichem Feld bis **0% bei 15**. Ab Entfernung 15 sind unverbundene
  Routen nicht verfügbar. Es gilt Civ4s `plotDistance`-Entfernungsmaß,
  das auch die ursprüngliche Handelsertragsformel verwendet. Zulässige Routen
  liefern mindestens einen Wirtschaftspunkt. Eine durchgehende Straßenverbindung
  liefert **100% ohne Entfernungslimit**. Wasserverbindungen (Meer oder Fluss,
  auch gemischte Straßen-/Wasserwege) benötigen **Segeln** und liefern bis
  **Astronomie** nur bis Entfernung **12** die 100%, oder bis **20**, wenn die Ausgangsstadt einen Hafen besitzt. Astronomie hebt dieses Limit auf. Die bestehenden Beschränkungen für befahrbare Geländearten gelten weiterhin.
  Städte auf verschiedenen Landmassen benötigen eine tatsächlich befahrbare
  Verbindung; Handel ohne Infrastruktur umgeht diese Seehandelsregeln nicht.
  Wasserhandel liefert **50% statt 100%**, wenn nicht beide Städte einen Hafen
  besitzen; zivilisationsspezifische Ersatzgebäude zählen mit. Das gilt auch für
  Flüsse und gemischte Straßen-/Wasserwege, nicht für durchgehende reine Straßenwege.
  Städte bewerten mögliche Partner mit dem exakten Routenwert vor der Rundung.
  Infrastruktur-Effizienz entscheidet damit auch zwischen Routen, die jeweils
  auf einen angezeigten Wirtschaftspunkt aufgerundet würden.
- **Militärzugang** ersetzt die Bezeichnung Offene Grenzen und regelt die
  Einreise von Einheiten, einschließlich ziviler Einheiten, unabhängig vom Handel.
  Das Abkommen bleibt gegenseitig; einseitige Abkommen sind noch nicht umgesetzt.
  Die KI schlägt es nur vor, wenn der Zugang einen bekannten Weg eröffnet oder
  mindestens drei Felder einspart: eine Landverbindung von ihrer Hauptstadt zu
  einer weiteren eigenen Stadt oder einer Stadt eines aktuellen/geplanten
  Kriegsgegners, oder einen Weg zum bestehenden Auftrag einer Einheitengruppe
  nahe der Grenze des Partners (auch zivile Einheiten und Schiffe). Dies ist
  eine geografische Schätzung, keine vollständige Bewegungssimulation.
  Handelseinnahmen geben dem Abkommen keinen Wert; die üblichen diplomatischen
  Ablehnungsgründe gelten weiterhin.
- Jede Route verbreitet **Kultur und Religionen in beide Richtungen**, auch
  beim Inlandshandel. Die Bevölkerung der jeweils empfangenden Stadt schwächt
  den Einfluss. Kultur pro Route und Richtung: `abgerundet(5 × Routenwert / Bevölkerung) / 10`:
  die Hälfte der bisherigen ungerundeten Rate, auf eine Nachkommastelle abgerundet.
  Religionschance: `abgerundet(2,5 × Routenwert / Bevölkerung)` Prozent je
  Religion der Partnerstadt, höchstens **12%** pro Route.
  Der Anteil der Besitzerkultur in der empfangenden Stadt verursacht einen
  linearen Abzug: null bei **75%**, bis zu **12 Prozentpunkten bei 100%**.
  Bei vollständig eigener Kultur ist die Handelsverbreitung ohne Toleranz damit unmöglich.
  Grundlage ist die gespeicherte Stadtkultur vor dem Kulturaustausch dieser Route.
  Heilige Städte erhalten weitere **3 Prozentpunkte Abzug** für Religionen,
  für die sie nicht heilig sind; mehrere heilige Religionen stapeln diesen Abzug
  nicht. Die endgültige Chance wird abgerundet und bleibt mindestens null.
  Diese Abzüge gelten nur für Handel, nicht für Missionare. Kulturbeiträge unter
  **0,1** pro Route/Richtung verfallen; Zehntelpunkte sammeln sich in der Stadt.
  Das Stadtfeld erhält ganze Kulturpunkte, wenn die Stadtkultur eine Ganzzahlgrenze
  überschreitet. Religionschancen bleiben auf ganze Prozentpunkte abgerundet.
  Kultur wird dem Besitzer der
  Partnerstadt in der empfangenden Stadt und auf ihrem Stadtfeld zugerechnet.
  Staatsatheismus verhindert religiösen Austausch; andere Verbreitungsverbote
  werden beachtet. Separat vergebene Routen in der Gegenrichtung wirken zusätzlich.
  Handelsrouten ersetzen die bisherige passive Religionsverbreitung. Missionare
  und historische Religionsgründungen bleiben erhalten. Staatsatheismus sperrt
  weiterhin Missionare sowie das Senden und Empfangen von Religionen durch Handel.
- Beispiel vor Kultur- und Heilige-Stadt-Abzügen: Eine Route mit sechs Wirtschaftspunkten bringt einer Stadt der
  Größe 2 **1,5 Kultur pro Runde** und **7% Verbreitungschance** je zulässiger
  Partnerreligion. Bei Größe 10 sind es 0,3 Kultur und 1% Religionschance.
- Ab **Währung** lässt sich im Außenberater unter Beziehungen eine Zivilisation
  auswählen und ein **Handelsembargo verhängen oder aufheben**. Es blockiert
  sofort die Routen zwischen beiden Zivilisationen, wird gespeichert und lässt
  Militärzugang bestehen. Beide Seiten kontrollieren ihr eigenes Embargo;
  der Handel kehrt erst zurück, wenn beide ihre Embargos aufgehoben haben.
  Die bestehende diplomatische Aufforderung zum Handelsabbruch verhängt ebenfalls
  ein Routenembargo und behält ihre bisherigen Vertragskündigungen bei.

Routen-Tooltips zeigen Infrastruktur-Effektivität und Kulturbeiträge. Die Werte
stehen zentral in `Assets/XML/GlobalDefines.xml` (`RFCMP_*TRADE*`). Embargo-Aktionen
verwenden synchronisierte Netzwerk-Nachrichten, die Religion den Spiel-Zufallsgenerator.

### Nahrungstransfers

Nahrung fließt über bestehende Handelsrouten zu der Stadt mit der höheren kombinierten Anziehungskraft. Verglichen werden lokaler Handelsertrag je Bevölkerungspunkt nach Modifikatoren, ohne Wirtschaftspunkte aus Handelsrouten, und Wohlbefinden je Bevölkerungspunkt. Wohlbefinden ist Zufriedenheit minus Unzufriedenheit plus die Hälfte der Nettogesundheit (Gesundheit minus Krankheit). Spezialisten-Gold und die Einstellung des Goldreglers bestimmen die Richtung nicht.

- Wohlstandsunterschiede liefern bis zu **100 Druckpunkte**. Wohlbefindensunterschiede liefern bis zu **50 Druckpunkte** und sind damit sp?rbar, aber im Allgemeinen schw?cher. Beide vorzeichenbehafteten Werte werden addiert, bevor Richtung und Menge des Nahrungstransfers feststehen. Eine gesunde und zufriedene neue Stadt kann somit trotz eines kleinen Wohlstandsnachteils Nahrung anziehen; Wohlbefinden allein ?berwindet keinen gro?en Wohlstandsunterschied.
- Grundbedarf an Nahrung: `aufrunden(absoluter Gesamtdruck / 10) + max(0, Routenwert - 1)`, multipliziert mit der Infrastruktur-Effektivität. Routen mit 0% Effektivität können weder eingerichtet werden noch Nahrung übertragen. Bei gegenseitigen Routen zählt die stärkere Anforderung einmal pro Städtepaar.
- Bei der Routenauswahl zählt die erwartete importierte oder exportierte Nahrung mit dem Wert eines Handelspunkts je Nahrung zusätzlich zum gewöhnlichen Routenhandel. Dies reserviert noch keine Nahrung: Die gemeinsame Exportgrenze wird erst nach Auswahl aller Routen angewandt.
- Die gesamten Exporte einer Stadt sind auf **eine Nahrung je Bev?lkerungspunkt** begrenzt. Es muss kein ?berschuss sein: Lieferst?dte k?nnen langsamer wachsen oder hungern. St?dte der Gr??e eins exportieren nur ihren lokalen ?berschuss nach Verbrauch und Gesundheitskosten.
- Bei ?berm??iger Nachfrage werden Exporte proportional aufgeteilt. Die Gesamtmenge wird auf ganze Nahrungspunkte abgerundet; verbleibende Punkte erhalten die gr??ten Nachkommareste. Gleichst?nde werden durch eine feste St?dte-/Routenreihenfolge entschieden. Kleine Anforderungen k?nnen leer ausgehen.
- Alle Zuteilungen entstehen gemeinsam einmal pro Spielrunde vor den Spielerzügen und werden gespeichert. Vor der ersten Wachstumsabrechnung einer beteiligten Stadt werden Route und Exportgrenze geprüft; anschließend wird derselbe Lieferbetrag an beiden Enden festgeschrieben. Spätere Änderungen können nicht nur eine Seite der Verbuchung aufheben. Bereits verbuchte Lieferungen werden beidseitig abgeschlossen; Störungen wirken auf die folgenden Lieferungen. Freie Kapazität wird bei der nächsten Zuteilung neu verteilt.
- Nahrung wird beim Lieferanten abgezogen und beim Empf?nger **nach allen Ertragsmodifikatoren** hinzugef?gt. Importe werden weder vervielfacht noch erneut exportiert. Sie wirken auf Wachstum, Hunger und nahrungsbasierte Einheitenproduktion. Infrastruktur, Segeln, Astronomie und H?fen beeinflussen bereits den Routenwert.
- Der Tooltip des Bev?lkerungsbalkens zeigt gesamte Importe/Exporte, eine Handelsroute den Austausch mit der Partnerstadt: positiv f?r Import, negativ f?r Export. Bestehende Spielst?nde beginnen mit der n?chsten Spielrunde.

Beispiel: Eine Stadt der Gr??e vier kann vier Nahrung exportieren. Fordern die Ziele vier, zwei und zwei, erhalten sie zwei, eins und eins. Verlorene Routen geben dem Lieferanten Nahrung zur?ck und entziehen sie den Empf?ngern.

Die Einstellungen `RFCMP_FOOD_EXPORT_PER_POPULATION` und `RFCMP_TRADE_FOOD_PRESSURE_PER_FOOD` in `Assets/XML/GlobalDefines.xml` steuern Bevölkerungsgrenze und Basismenge. Der technologieabhängige Wachstumsmalus betrifft positiven Überschuss nach den Transfers, nicht die Nahrungsproduktion oder Transfermengen.

## Neue Staatsformen

Stationierte Militäreinheiten geben **+1 Zufriedenheit je zwei Einheiten**, abgerundet, bis maximal **+3 bei sechs Einheiten**. Dies gilt unter jeder Staatsform und erscheint in der städtischen Zufriedenheitsaufschlüsselung als Militärpräsenz.

Stadtfelder behalten ihre natürlichen Erträge aus Gelände, Hügeln, Flüssen, Landschaftsmerkmalen und bekannten Ressourcen und erhalten **+1 Produktion und +1 Handel**. Es gibt keinen Mindestnahrungsertrag: Ein kahles Wüstenstadtfeld erzeugt keine Nahrung. Bei Stadtgründung bleibt Schwemmland einschließlich seiner Erträge erhalten. Die Ertragsregel gilt für alle Stadtfelder; bereits entferntes Schwemmland wird in bestehenden Spielständen nicht wiederhergestellt.

In jeder Kategorie ist eine Staatsform aktiv. Boni verschiedener Kategorien
addieren sich: Diktatur und Nationalismus ergeben zusammen beispielsweise
+40% Produktion.

**Handel** bezeichnet die Wirtschaftspunkte, die über die Regler auf Gold,
Forschung, Kultur und Spionage verteilt werden. Gold- und Handelswegeinnahmen
sind davon zu unterscheiden. Prozentboni verändern die Erträge, nicht die
Prozentpunkte der Reglereinstellungen. Feste Gebäude- und Verbesserungsboni
gelten je passendem Gebäude beziehungsweise bearbeiteter Verbesserung.

### Regierung

Für Ägypten heißt das Stammessystem in jeder Epoche **Pharaonentum** und
Despotismus **Gottkönigtum**. Pharaonentum gibt +1 Produktion durch Bauernhöfe
und je Sklavenspezialist bei mittlerem Staatsform-Unterhalt. Es ersetzt die
Einheitenproduktion, den Forschungsabzug und die erhöhten Unterhaltskosten des
Stammessystems. Unter Gottkönigtum gibt jeder zugewiesene Priester in einer Stadt
mit ägyptischem Obelisken +1 Zufriedenheit, höchstens +2 pro Stadt. Dies ersetzt
die Zufriedenheit durch Palast und Monument. Obelisken veralten unter dieser
Staatsform nicht: Alle Effekte bleiben nach Kalender wirksam und sie bleiben
baubar. Eine Staatsreligion ist nicht erforderlich. Das unabhängige Land
heißt unter Pharaonentum **Pharaonenreich**, sein Anführer trägt den Titel
**Pharao**. Theokratie oder Gottesstaat wählen stattdessen **Tempelstaat Ägypten**:
Hier ordnet sich die politische Herrschaft der Religion unter, während das
Gottkönigtum den Herrscher selbst als Verkörperung göttlicher Autorität versteht.

| Staatsform | Benötigte Technologie | Unterhalt | Effekte |
| --- | --- | --- | --- |
| **Stammessystem** | Keine | Keiner | +20% Produktion für alle Einheiten; -20% Forschung; +100% entfernungsabhängiger und durch die Städteanzahl verursachter Städteunterhalt. |
| **Monarchie** | Monarchie | Mittel | Hauptstadtgebäude geben je +1 Kultur und +1 Handel. Weltwunder der Hauptstadt geben je +1 Zufriedenheit in allen Städten, maximal +3, auch nach ihrer Veraltung. Ermöglicht Erbfolgeereignisse. |
| **Republik** | Gesetzgebung | Mittel | Zugewiesene Spezialisten außer Sklaven verbrauchen 1 Nahrung weniger. Freie Spezialisten und angesiedelte Große Persönlichkeiten sind ausgenommen. |
| **Diktatur** | Faschismus | Hoch | +20% Produktion; keine Kriegsmüdigkeit; -2 Zufriedenheit in jeder Stadt. |
| **Demokratie** | Demokratie | Hoch | +2 Zufriedenheit in jeder Stadt; +1 Handel je zugewiesenem oder freiem Spezialisten. Einführung wählt alle anderen Kategorien zufällig; Wahlen ändern alle zehn Runden eine Kategorie. Bei Beibehaltung der Demokratie sind manuelle Wechsel anderer Kategorien gesperrt. Abschaffung verlängert die normale Revolutionsanarchie um zwei Runden. |

### Legitimation

| Staatsform | Benötigte Technologie | Unterhalt | Effekte |
| --- | --- | --- | --- |
| **Despotismus** | Keine | Keiner | +1 Zufriedenheit durch Paläste und Monumente einschließlich ihrer zivilisationsspezifischen Ersatzgebäude. |
| **Theokratie** | Göttliches Recht | Hoch | +1 Zufriedenheit von Gebäuden der Staatsreligion; -2 Zufriedenheit von Gebäuden einer fremden Religion. Mit eigener Staatsreligion erhalten Landeinheiten +15% Kampfstärke gegen Barbaren und Länder mit fremder oder keiner Staatsreligion, bei Angriff und Verteidigung. |
| **Plutokratie** | Bankwesen | Mittel | +25% Goldeinnahmen; +50% Handel durch Handelswege. |
| **Nationalismus** | Nationalismus | Mittel | +5 Kultur in jeder Stadt; +20% Produktion; -5 Zufriedenheit in Städten, in denen die Kultur eines anderen Spielers auf dem Stadtfeld größer ist als die des Besitzers. |
| **Rechtsstaat** | Verfassung | Hoch | +2 Zufriedenheit in jeder Stadt; +10% Handel. |

### Arbeit

| Staatsform | Benötigte Technologie | Unterhalt | Effekte |
| --- | --- | --- | --- |
| **Selbstversorgung** | Keine | Keiner | +2 Gesundheit in jeder Stadt; Hüttenverbesserungen wachsen nicht; zugewiesene Spezialisten sind gesperrt und bestehende Zuweisungen werden entfernt; freie Spezialisten bleiben erhalten. |
| **Sklaverei** | Bronzebearbeitung | Niedrig | Eroberte Bevölkerung wird zu Sklaveneinheiten. Sklaveneinheiten haben 25% Unterhalt, werden im Kampf zuerst verteidigen, können eine eigene Upgrade-Reihe nutzen und 20 Runden lang als Spezialist mit +3 Produktion und -1 Nahrung in Städten arbeiten. Das Aufstandsrisiko sinkt proportional zur Gesamtstärke der Garnison und entfällt, wenn sie der verfügbaren bewaffneten Sklavenstreitmacht entspricht. Große Eroberungen lösen regionale Sklavenmarkt- oder Flüchtlingsereignisse aus. Sklaveneinheiten aus eroberter Bevölkerung behalten eine kleine herkunftsabhängige Beförderung. |
| **Leibeigenschaft** | Öffentliche Verwaltung | Niedrig | +1 Nahrung durch Bauernhöfe; Bautrupps errichten Verbesserungen 50% schneller. |
| **Planwirtschaft** | Kommunismus | Hoch | +1 Produktion durch Werkst?tten, Wasserm?hlen und Windm?hlen; +1 Nahrung durch Bauernh?fe; -10% Handel. Keine Handelswege mit Kapitalisten. |
| **Marktwirtschaft** | Wirtschaftswesen | Mittel | +1 freier Spezialist in jeder Stadt; H?ttenverbesserungen wachsen doppelt so schnell. Keine Handelswege mit Kommunisten. |

Das Wachstum umfasst sämtliche Ausbaustufen: **Hütte → Weiler → Dorf → Gemeinde**.
Selbstversorgung verhindert die Aufwertung; Marktwirtschaft verdoppelt ihre
Geschwindigkeit. Normale unbeschäftigte Bürger bleiben bei Selbstversorgung
als Möglichkeit für überschüssige Bevölkerung verfügbar.

### Folgen großer Eroberungen

Die Eroberung einer großen Stadt unter **Sklaverei** erzeugt einen regionalen Sklavenmarkt. Andere Sklavenhalter können eine Sklaveneinheit kaufen; andere Staaten können die Freiheit eines Gefangenen kaufen. Dieser erhöht die Bevölkerung, bringt Kultur des früheren Besitzers und 20 Runden Zufriedenheit. Erobert ein Staat ohne Sklaverei eine große Stadt, fliehen Menschen als Flüchtlinge: Staaten ohne Sklaverei nehmen sie kostenlos auf, Sklavenhalter können sie für 20 Runden zur Arbeit zwingen. Das gibt einen vorübergehenden Sklavenspezialisten und eine vorübergehende Unzufriedenheit. Angebote erhalten nur große Zivilisationen mit einer Stadt auf demselben Kontinent.

Unter Sklaverei kostet eine Eroberung **zwei Bevölkerungspunkte** statt einem und erzeugt eine Sklaveneinheit je verlorenem Bevölkerungspunkt. Städte behalten mindestens Größe eins; Rückeroberungen sind ausgenommen.

Ein Landangreifer unter Sklaverei hat außerdem eine **Chance von 50%, einen Sklaven gefangen zu nehmen**, wenn er einen schwächeren Landverteidiger tötet. Tiere sind ausgenommen. Verglichen wird die effektive Kampfstärke zu Kampfbeginn einschließlich Verteidigungsboni. Der Angreifer muss vollständig gesund beginnen und darf nur durch Erstangriffe des Verteidigers Schaden erleiden. Rückzüge und Kollateraltötungen zählen nicht. Der Sklave erscheint auf dem Feld des Angreifers und erhält, soweit vorhanden, die Herkunftsbeförderung der besiegten Zivilisation.

### Militär

| Staatsform | Benötigte Technologie | Unterhalt | Effekte |
| --- | --- | --- | --- |
| **Kriegergesellschaft** | Keine | Keiner | Nahkampfeinheiten starten mit +2 Erfahrung; Belagerungseinheiten haben -20% Kampfstärke. |
| **Seekriegsführung** | Segeln | Niedrig | +50% Produktion und +2 Erfahrung für neu gebaute militärische Schiffe, einschließlich Transportschiffen. Arbeitsboote erhalten keinen dieser Boni. |
| **Heeresfolge** | Feudalismus | Mittel | +5% Produktion für militärische Landeinheiten je von der Stadt bewirtschaftetem Bauernhof, einschließlich Belagerungseinheiten. Sechs bewirtschaftete Bauernhöfe geben +30%. |
| **Berufsarmee** | Militärwesen | Hoch | Einheiten starten mit +5 Erfahrung. |
| **Wehrpflicht** | Militärwissenschaft | Mittel | +25% Produktion für alle Einheiten. Nahrungsüberschuss produziert zusätzlich militärische Landeinheiten; währenddessen ruht das Wachstum. Schiffe nutzen diese Nahrungsumwandlung nicht. |

Die Einheitenproduktionsboni von Stammessystem und Wehrpflicht gelten auch für
Bautrupps, Siedler und Missionare. Wehrpflicht gewährt keine zusätzliche
Rekrutierungsfähigkeit; ihr Effekt ist der oben aufgeführte Produktionsbonus.

### Religion

| Staatsform | Benötigte Technologie | Unterhalt | Effekte |
| --- | --- | --- | --- |
| **Ahnenkult** | Keine | Keiner | +1 Kultur durch Monumente einschließlich ihrer zivilisationsspezifischen Ersatzgebäude. |
| **Staatsreligion** | Priestertum | Niedrig | +1 Zufriedenheit in Städten mit Staatsreligion; +100% Produktion für Missionare und +25% Produktion für Gebäude der Staatsreligion. |
| **Gottesstaat** | Theologie | Hoch | +10% Produktion in Städten mit Staatsreligion; -1 Zufriedenheit je fremder Religion. Eroberte Städte werden durch Konvertierung befriedet. |
| **Toleranz** | Liberalismus | Niedrig | Entfernt Unzufriedenheit durch fremde Religionen und diplomatische Religionsmali mit eurem Land. Länder mit anderer Staatsreligion erhalten +2 Beziehungen zu euch, außer unter Staatsatheismus. Beide Länder müssen eine Staatsreligion haben. +5 Prozentpunkte auf die Chance der Religionsverbreitung durch Handelswege in eigene Städte. |
| **Staatsatheismus** | Wissenschaftliche Methode | Hoch | +10% Forschung und +10% Produktion; -1 Zufriedenheit in allen Städten. Religiöse Gebäude haben keine Effekte; Religionen können sich in den eigenen Städten nicht verbreiten. |

Unter Toleranz erhöht sich die eingehende Handelsverbreitung je fehlender Religion und Route nach allen Kultur- und Heilige-Stadt-Abzügen um **5 Prozentpunkte** (maximal **17%**). Auch eine sonst auf null gesenkte Chance beträgt damit 5%; Inlandsrouten zählen ebenfalls. Staatsatheismus und andere Verbreitungsverbote bleiben wirksam.

Befriedung durch Gottesstaat: Fehlte die eigene Staatsreligion bei der Eroberung, beendet ihre Verbreitung einmalig die Eroberungsunruhe, gibt +1 Bevölkerung und stellt nach Möglichkeit ein dabei zerstörtes Gebäude wieder her. Gottesstaat muss bei Eroberung und Konvertierung aktiv und die Staatsreligion dieselbe sein. Jede Rückeroberung prüft den Anspruch neu; er bleibt beim Speichern erhalten.

Staatsatheismus deaktiviert die Staatsreligion; die anderen vier religiösen
Staatsformen erlauben eine Staatsreligion.

Unter Staatsatheismus bleiben religiöse Gebäude im Besitz und zählen weiterhin
für Wunderlimits. Ihre Effekte sind jedoch deaktiviert, einschließlich
Zufriedenheit, Produktion, Handel, Kultur trotz Veraltung, Schreineinnahmen,
freien Spezialisten und Punkten für Große Persönlichkeiten. Beim Verlassen der
Staatsform werden die Effekte wiederhergestellt. Als religiös gelten Gebäude
mit Religionszugehörigkeit oder Religionsvoraussetzung.

Staatsatheismus verhindert natürliche Ausbreitung sowie Ausbreitung durch
Missionare, Ereignisse und Skripte. Bestehende Religionen bleiben erhalten,
auch bei einem Besitzerwechsel der Stadt. Die Gründung oder Verlegung einer
heiligen Stadt bleibt als eigenständige Aktion möglich.

## Start-Staatsformen

Jede spielbare Zivilisation einschließlich Byzanz im Szenario 600 n. Chr. hat ein
Profil für alle fünf Kategorien. Es gilt für menschliche und KI-Spieler beim
Szenariostart oder der ersten Gründung, nach Zuweisung der Starttechnologien und
vor der Erzeugung der Start-Einheiten durch Skripte. Nicht verfügbare Staatsformen
werden durch festgelegte Alternativen ersetzt; zusätzliche Technologien oder
Anarchie entstehen dadurch nicht.

Die Profile gelten für alle vier Szenarien und überschreiben keine späteren
Spielerentscheidungen. Bereits vorhandene Zivilisationen in Spielständen behalten
ihre Staatsformen. Alle Profile und Ersatzregeln stehen in
[StartingCivics.md](StartingCivics.md).

## Demokratische Wahlen

Jede reguläre Wahl öffnet eine eigene, leicht satirische Bekanntmachung zur gewählten Staatsform mit einem einzigen Bestätigungsbutton. Dessen Tooltip lautet nur **[Staatsform] annehmen**. Das Ergebnis gilt sofort; die Bestätigung verändert keinen synchronisierten Spielzustand.

Demokratie ignoriert alle **negativen Stabilitätsmodifikatoren durch Staatsformkombinationen**, einschließlich Plutokratie mit Planwirtschaft und Theokratie mit Toleranz. Positive Kombinationsboni bleiben aktiv. Andere Stabilitätsverluste gelten weiterhin.

Bei Einführung wird in jeder anderen Kategorie sofort eine verfügbare Staatsform zufällig gewählt; die bisherige kann erneut gewählt werden. Solange Demokratie beibehalten wird, sind andere Kategorien nicht manuell wechselbar. Ihre Abschaffung entsperrt sie und verlängert die normale Revolutionsanarchie um **zwei Runden**. Bestehende Anarchieimmunität gilt weiterhin.

Wahlen finden bei aktiver Demokratie auf **globalen Rundenzahlen statt, die
durch zehn teilbar sind**. Zuerst wird eine der anderen vier Kategorien mit
verfügbarer Alternative ausgewählt, dann eine andere Staatsform, die der Spieler
aktuell annehmen kann. Gibt es keine verfügbare Alternative, erfolgt kein
Wechsel. Menschliche Spieler erhalten eine Benachrichtigung.

Beide Auswahlen verwenden den synchronisierten Zufallsgenerator des Spiels.
Die Regierung bleibt Demokratie; Wahlen verursachen keinen zusätzlichen
Stabilitätsmalus für den Übergang.

## Stabilität durch Staatsformen

### Dynastische Erbfolge

Wenn eine Monarchie mit Staatsreligion kollabiert, kann sie mit **50%**
Wahrscheinlichkeit vererbt werden, statt zu zerfallen. Ein Erbe muss eine
lebende Monarchie mit derselben Staatsreligion, mindestens **0 Stabilität** und
mindestens einer Stadt auf dem Kontinent der Hauptstadt der kollabierenden
Monarchie sein. Ein zulässiger Erbe wird deterministisch ausgewählt; eine
Größenvoraussetzung gibt es nicht. Der Erbe erhält alle Städte und Einheiten
des kollabierten Reichs. Ohne zulässigen Erben oder bei fehlgeschlagenem Wurf
gelten die normalen Kollapsregeln.

Die folgenden Kombinationen tragen zur Basisstabilität bei:

| Kombination | Stabilität |
| --- | ---: |
| Stammessystem + Despotismus | +1 |
| Monarchie + Theokratie | +1 |
| Plutokratie + Planwirtschaft | -1 |
| Republik oder Demokratie + Rechtsstaat | +2 |
| Monarchie + Heeresfolge | +2 |
| Theokratie + Staatsreligion oder Gottesstaat | +2 |
| Plutokratie + Marktwirtschaft | +1 |
| Theokratie + Toleranz | -3 |

Theokratie mit Staatsatheismus gibt Landeinheiten +15% Kampfstärke gegen Länder
mit beliebiger Staatsreligion und weiterhin gegen Barbaren. Gegen religionslose
Länder gilt dieser Bonus nicht. Religionsgebäude verursachen je -2 Zufriedenheit,
auch wenn Staatsatheismus ihre positiven Effekte unterdrückt; technisch veraltete
Gebäude zählen weiterhin nicht. Der Zufriedenheitsbonus für Gebäude der eigenen
Staatsreligion entfällt. Die Kombination erhält eigene Ländernamen wie
„Pontifikat der Vernunft“ und „Heiliges Reich der Vernunft“. Diese Kombination verursacht keinen eigenen Stabilitätsmalus.

Passende Beiträge werden addiert und insgesamt auf **-5 bis +5** begrenzt.
Andere Kombinationen tragen null bei. Der Modifikator wird alle drei Runden
für die Basisstabilität neu berechnet; er summiert sich nicht als dauerhafter
Gewinn oder Verlust pro Runde. Tatsächliche Zufriedenheit und wirtschaftliche
Leistung beeinflussen die Stabilität weiterhin über die allgemeinen Systeme.

Die Überarbeitung entfernt:

- Feste Stabilitätswerte einzelner Staatsformen.
- Automatische regierungsspezifische Stabilitätsrettung und Schwellenboni.
- Den Malus für „veraltete Staatsformen“ und die bisherige Übergangsinstabilität der Demokratie.
- Die besondere Wirtschaftskrise der Marktwirtschaft und ihre Übertragung durch offene Grenzen.
- Die acht Runden dauernde Krise nach dem Verlassen der Planwirtschaft.
- Zusätzliche religiöse Stadtstrafen speziell unter Staatsreligion und Gottesstaat.
- Die separate Fremdkultur-Stabilitätsschwelle des Nationalismus.
- Den zusätzlichen Stabilitätsbonus für Gefängnisbau unter Diktatur.
- Boni der entfernten Expansionskategorie für Vasallen, entfernte Städte,
  Eroberungen und Handel/Wirtschaft.

Hintergründe und Verhalten in Spielständen stehen in
[CivicStability.md](CivicStability.md); technische Details in
[CivicEffects.md](CivicEffects.md).

## Neue Zivilisationen und Gebietswechsel

### Feld-Tooltips

Beim Überfahren eines Feldes erscheinen die **Grundnamen** zukünftiger
Zivilisationen, deren Kerngebiet das Feld einschließt. Jeder Name steht in
einer eigenen Zeile in der Farbe der Zivilisation. Die eigene Zivilisation und
aktuell lebende Zivilisationen werden ausgeschlossen. Angezeigt wird etwa
**Deutschland** statt eines frühen dynamischen Namens wie „Germanische Völker“.

Der Tooltip verwendet feste Kerngebietsrechtecke und eine Grenze anhand der
Gründungsrunde. Er berechnet nicht jede Skriptausnahme oder angepasste
Verzögerung neu und dient daher als Planungshilfe.

### Unruhen vor dem Gebietswechsel

**Drei Runden vor einem geplanten ersten Gebietswechsel** erhalten Städte im
Kerngebiet und auf Ausnahmefeldern der neuen Zivilisation drei Runden Unruhen
über den Besatzungszähler. Eine bereits länger andauernde Besatzung bleibt
erhalten. Der Zeitplan berücksichtigt die Verzögerungen der Gründungslogik.

Betroffene menschliche Besitzer erhalten eine Nachricht mit dem frühen
dynamischen Namen der Zivilisation, etwa **„Die [Völker] erheben sich!“**.
Diese Vorwarnung begleitet das bestehende Gebietswechsel-System und führt
keine eigene Regel für den Wechsel stationierter Einheiten ein.

## Kulturaufstände

Erfolgreiche Kulturrevolten in Städten regulärer Zivilisationen lösen einen Aufstand
statt eines automatischen Besitzerwechsels aus. Die bestehenden Prüfungen für
kulturellen Druck und Garnison entscheiden weiterhin über das Auftreten.
Historische Gebietswechsel bei der Gründung von Zivilisationen und die bisherige
kulturelle Übernahme barbarischer und unabhängiger Städte bleiben eigenständige Mechaniken.

Alle kulturellen Revolten und Überläufe erfordern **mehr als 50% der gesamten
Stadtfeldkultur** für eine einzelne fremde Zivilisation. Eine relative Mehrheit
oder genau 50% genügt nicht. Unabhängige und barbarische Städte umgehen die
Garnisonsprüfung nicht mehr und erhalten keine erhöhte Revoltenwahrscheinlichkeit;
Revoltenschutz der Garnison kann die Chance auf null senken. Unabhängige Städte
benötigen weiterhin eine Warnrevolte vor einem späteren erfolgreichen Überlaufen,
abhängig von den Spieloptionen. Barbarische Städte können nach der ersten
erfolgreichen Revolte überlaufen. Historische Gründungswechsel bleiben separat.

- Die Stadt verliert **aufgerundet 25% ihrer Bevölkerung**, bleibt aber mindestens Größe 1.
- Die Kultur der aufständischen Zivilisation in der Stadt und auf dem Stadtfeld
  sinkt entsprechend dem verlorenen Bevölkerungsanteil. Andere Kulturen bleiben
  erhalten. Bei Größe 1 sinkt die aufständische Kultur ohne Bevölkerungsverlust um 25%.
- **Zwei Barbareneinheiten je verlorenem Bevölkerungspunkt** erscheinen auf direkt
  angrenzenden, passierbaren Landfeldern ohne Städte oder nichtbarbarische Einheiten.
  Sie werden über geeignete Felder verteilt und können sich stapeln. Gibt es kein
  geeignetes Feld, erscheinen keine Einheiten.
- Die Rebellen verwenden den stärksten regulären Nahkampf-, Bogenschützen- oder
  Schießpulver-Infanterietyp, den die Technologien des Besitzers erlauben.
  Strategische Ressourcen werden dafür nicht benötigt.
- Die Stadt erhält Unruhen für die grundlegende Besatzungsdauer eines Aufstands.
  Die Garnison wird durch diesen Aufstand nicht automatisch beschädigt.

Städte der Größe 1 erzeugen keine Rebellen. Die Option „Keine Barbaren“ unterdrückt
die Rebelleneinheiten; Bevölkerungs-, Kultur- und Unruheneffekte bleiben bestehen.
Der Besitzer erhält eine Nachricht mit den tatsächlichen Verlusten und der
Rebellenzahl. Barbaren können die Stadt später im Kampf erobern; kultureller Druck
überträgt sie nicht direkt.

Der Fremdkulturanteil sinkt normalerweise. Besteht jedoch ausschließlich fremde
Kultur, kann ihr prozentualer Anteil trotz sinkender Kulturpunkte bei 100% bleiben.
Kultur auf umliegenden Feldern und bestehende Einheiten werden nicht gelöscht.
Die Mechanik verwendet gemeinsamen Spielzustand und feste Auswahlreihenfolgen;
die Prüfung im Mehrspielerbetrieb steht noch aus.

## Eroberte Städte umsiedeln

Der Eroberungsdialog bietet **Umsiedeln (Siedler erhalten)** an, wenn mehr als
**25%** der gespeicherten Stadtkultur zum eigenen Team gehören. Es gilt die
ungerundete Stadtkultur, nicht die Feldkultur; genau 25% genügt nicht. Die Option
steht nur in der Runde des Besitzerwechsels zur Verfügung.

Die Stadt und alle Gebäude werden entfernt; ein Siedler der eigenen Zivilisation
entsteht auf ihrem Feld und hat in dieser Runde keine Bewegung mehr. Ändert sich
durch die Entfernung der Feldbesitzer, können die normalen Gebietsregeln den
Siedler auf ein zulässiges Feld versetzen. Andere Einheiten und Feldkultur folgen
den normalen Stadtentfernungsregeln. Die Umsiedlung verwendet die Stadtauflösung
und löst keine abbrennspezifischen Diplomatie- oder Ereignisstrafen aus. Behalten,
Abbrennen (soweit erlaubt), Verschenken und Stadtansicht bleiben verfügbar.

Auch berechtigte Städte der Größe 1 erhalten die Wahl, statt automatisch zerstört
zu werden. Kein Städtezerstören, Ein-Stadt-Herausforderung und Stadteliminierungsmodi
behalten ihre Einschränkungen. KI-Eroberungsentscheidungen bleiben unverändert.
Die Aktion läuft über die vorhandene synchronisierte Stadtaufgaben-Nachricht
und prüft die Bedingungen beim Ausführen erneut. Neue gespeicherte Zustände
oder Änderungen bestehender Aufgabenindizes sind nicht erforderlich.

## Produktionsbeschleunigung

- **Leibeigenschaft** kann Bevölkerung für Einheiten opfern, aber nicht für
  Gebäude oder Projekte.
- Mit **Bankwesen** kann Gold eine Einheit sofort abschließen. Die fertige
  Einheit ist ein **Söldner**: Sie startet mit einer bis drei gültigen
  zufälligen Beförderungen, kann weder Erfahrung noch weitere Beförderungen
  erhalten und nicht aufgerüstet werden. Söldner
  verbrauchen keine freien Einheiten- oder Militäreinheitenkontingente. Sie
  zahlen ihre regulären Einheitenkosten plus 100% Zuschlag vor
  Schwierigkeitsmodifikatoren.
- Mit **Kapitalgesellschaft** kann Gold zusätzlich Gebäude abschließen.
- **Wehrpflicht** wandelt Nahrungsüberschüsse beim Bau von militärischen Landeinheiten
  in Produktion um. Diese Nahrung wird also nicht für Stadtwachstum gespeichert.

Alle Söldner-Zufallsentscheidungen verwenden Civ4s synchronisierten
Spielzufall und entstehen beim Abschluss des Goldauftrags. Es ist kein
zusätzlicher gespeicherter Stadtzustand erforderlich.

## Dynamische Ländernamen

Ländernamen reagieren auf Regierung, Legitimation, Wirtschaft, Staatsreligion
und Reichsgröße. Bestehende Vasallen- und Kolonialnamen haben Vorrang. Namen
werden nach Staatsformen- und Religionswechseln sowie einmal pro Spielerzug
aktualisiert.

Der Katalog enthält **569 Einträge mit 358 unterschiedlichen deutsch-englischen
Namenspaaren**. Die Namen verwenden passende historische Bezeichnungen und
plausible alternative Entwicklungen. Ein Name muss nicht jede aktive Staatsform
abbilden.

Beispiele sind das **Heilige Römische Reich**, die **Hanse**, die **Batavische
Republik**, die **Republik Nowgorod**, das **Reich des Himmels**, das **Himmlische
Reich des Großen Friedens**, das **Land der vier Weltgegenden**, das **Königreich
Italien**. Unterschiedliche
Staatsformen-Kombinationen können bewusst denselben natürlichen Ländernamen
verwenden.

Der Katalog steht in [CountryNames.csv](CountryNames.csv), die Auswahlregeln
in [CountryNaming.md](CountryNaming.md). Die neuen Ländernamen sind auf
Deutsch und Englisch vorhanden; Französisch, Italienisch und Spanisch verwenden
englische Ersatztexte.

## Installation und Mehrspieler

1. Den Ordner **`Awakened RFC`** in das **`Mods`**-Verzeichnis von Beyond the Sword kopieren.
2. Den Ordnernamen beibehalten: Die enthaltenen Szenarien verweisen darauf. Der
   ursprüngliche RFC-MP-Mod kann parallel installiert bleiben.
3. Awakened RFC über das Mod-Menü des Spiels oder
   [Launch Awakened RFC.bat](<../Launch Awakened RFC.bat>) starten. Der Starter
   verwendet den üblichen Steam-Installationspfad; bei anderen Installationen
   muss der Pfad angepasst werden.
4. Eines der enthaltenen Szenarien wählen: **3000 v. Chr.**, **800 v. Chr.**, **600 n. Chr.** oder **1453 n. Chr.**.

Alle Teilnehmer benötigen dieselben Mod-Dateien einschließlich Python, XML und
DLL. Spielmechaniken und Wahlzufall verwenden synchronisierten Spielzustand;
die Überarbeitung muss noch im Mehrspielerbetrieb validiert werden.

Nach Textänderungen beim Start **Shift gedrückt halten**, um den Textcache neu
aufzubauen.

Nach Änderungen an XML-Staatsformen-Modifikatoren ein neues Spiel beginnen,
da alte Spielstände gespeicherte Spieler- und Stadtboni behalten können.
Die neuen Stabilitätskombinationen greifen in bestehenden Spielständen bei der
nächsten Neuberechnung der Basisstabilität. Entfernte Krisenzähler bleiben
lesbar, verursachen aber keine Strafen mehr; frühere Stabilitätsänderungen
werden nicht rückwirkend korrigiert.

## Spiel-DLL kompilieren

Für die Kompatibilität mit Civ4 den ursprünglichen **32-Bit-VC7.1-Werkzeugsatz**,
Python 2.4 und Boost.Python 1.32 verwenden.

Voraussetzungen und Kompilierungsablauf stehen in [AGENTS.md](../AGENTS.md) und
[BUILDING.md](<../Awakened RFC/CvGameCoreDLL/BUILDING.md>). Der konfigurierte Build
kopiert die neu erzeugte DLL in den Mod-Ordner des Projekts und in den
installierten Mod. Civ4 vor dem Kompilieren schließen, damit die installierte
DLL ersetzt werden kann.

### Moderne und Zukunftsforschung

Globale Erwärmung und Lufteinheiten einschließlich Raketen und Atomwaffen sind
entfernt. Drei getrennte Dauerforschungen verbessern Zufriedenheit, Gesundheit
oder Kampfstärke; ihre Kosten steigen je Abschluss um 35 %. Militärische
Forschung endet bei +15 %. Ein sehr teurer KI- und Automatisierungsbaum eröffnet
sechs neue Stadtgebäude. Ein Sozialstaatssystem ist noch nicht umgesetzt.
Siehe [Regeln, Kosten und technische Umsetzung](ModernEra.md).

### Start 1453 n. Chr.

Das Szenario von 1453 beginnt unmittelbar nach der osmanischen Eroberung
Konstantinopels. Es umfasst 96 Städte und 25 bestehende, sofort spielbare
Hauptzivilisationen. Namen und Startprofile bilden unter anderem das
Mamlukensultanat, Ming-China, Moskau, die italienischen Staaten und das
Osmanische Sultanat ab. Amerika behält seinen späteren Gründungszeitpunkt.
Siehe [Staatenliste, Kartenabstraktionen und Einrichtung](1453ADScenario.md).

### Verbuchung der Nahrungstransfers

Jede Lieferung wird vor der ersten Wachstumsabrechnung an beiden Enden auf
denselben Betrag festgelegt. Spätere Änderungen von Route, Exportgrenze oder
Unruhen dürfen nicht nur eine Seite der bereits verbuchten Lieferung aufheben.
Noch nicht verbuchte Lieferungen können an beiden Enden gemeinsam entfallen.
Die Bilanz der transferierten Nahrung ist weltweit null; innerhalb eines
Landes können Importe und Exporte durch Außenhandel voneinander abweichen.
Die Bevölkerung kann trotzdem schneller wachsen, wenn kleine Städte Nahrung
effizienter in neue Einwohner umsetzen.

### Aufwertung bewaffneter Sklaven

Sklaveneinheiten können direkt zur modernsten durch die Technologien ihres
Teams freigeschalteten bewaffneten Sklaveneinheit aufgewertet werden.
Ältere Waffenstufen werden dann nicht mehr angeboten. Die normalen
Aufwertungskosten und Stadtvoraussetzungen gelten weiterhin.

Die Bewaffnung wird mit jeder Waffenstufe teurer; die folgenden Preise gelten
vor normalen Aufwertungsrabatten und KI-Anpassungen.
Nur die Zielstufe bestimmt den Preis; übersprungene Waffenstufen werden
nicht mitbezahlt. Einzigartige Fähigkeiten für kostenlose Aufwertungen
gelten weiterhin.

| Bewaffnete Sklaveneinheit | Technologie | Stärke | Gold |
| --- | --- | ---: | ---: |
| Bronzewaffen | Bronzebearbeitung | 3 | 15 |
| Schwertkämpfer | Eisenverarbeitung | 4 | 25 |
| Streitkolbenträger | Maschinen | 5 | 40 |
| Musketier | Schießpulver | 7 | 60 |
| Schütze | Drall | 10 | 80 |
| Infanterie | Fließband | 14 | 100 |
| Moderne Infanterie | Robotik | 20 | 130 |

Alle Stufen bleiben Nahkampf-Sklaveneinheiten mit Kanonenfutter und einem Viertel
des Unterhalts. Die Schusswaffenstufen behalten passende Schussanimationen;
die letzte Stufe bleibt ein Fußsoldat statt eines Fahrzeugs.
Aufstände und die Berechnung der nötigen Garnisonsstärke berücksichtigen
die modernste durch den Besitzer freigeschaltete Stufe.

Alle Sklavenstufen verwenden das markante Körpermodell des unbewaffneten
Sklaven, mit passenden Waffen und Animationen je Epoche, gemischten
Figurenvarianten und unregelmäßigen Formationen.
Die [Dokumentation zur Einheitengrafik](SlaveUnitArt.md) enthält die Modelle
aller Waffenstufen, Quellenangaben und eine statische Vorschau.
