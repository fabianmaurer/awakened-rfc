# RFC MP Plus — Spielregeln

[English](../README.md) | **Deutsch**

Eine auf Mehrspielerpartien ausgerichtete Überarbeitung von **Rhye's and Fall
Multiplayer** für **Civilization IV: Beyond the Sword**. Sie bietet fünf
Staatsformen-Kategorien, Stabilität durch passende Staatsformen-Kombinationen,
Vorwarnungen vor der Entstehung neuer Zivilisationen und dynamische Ländernamen.

Diese README beschreibt die Spieländerungen dieses Projekts. Weltkarten,
historische Gründungszeitpunkte, einzigartige Fähigkeiten, Siegziele und weitere
Systeme aus dem ursprünglichen RFC MP bilden weiterhin die Grundlage.

## Spieländerungen im Überblick

- **25 Staatsformen in fünf Kategorien:** Regierung, Legitimation, Arbeit,
  Militär und Religion ersetzen die bisherigen sechs Kategorien. Der Bildschirm
  nutzt die verfügbare Breite und enthält neue Illustrationen.
- **Demokratische Wahlen:** Alle zehn Runden wird eine andere Kategorie auf eine
  zufällig ausgewählte verfügbare Staatsform umgestellt.
- **Start-Staatsformen:** Jede Zivilisation erhält ein Profil passend zu ihrer
  Zeit, soweit die Starttechnologien des Szenarios oder der Gründung es erlauben.
- **Stabilität durch Kombinationen:** Passende Institutionen erhalten kleine
  Boni; Theokratie mit Staatsatheismus erhält einen Malus. Die Summe ist begrenzt.
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
  **Astronomie** nur bis Entfernung **12** die 100%. Astronomie hebt dieses Limit
  auf. Die bestehenden Beschränkungen für befahrbare Geländearten gelten weiterhin.
  Städte auf verschiedenen Landmassen benötigen eine tatsächlich befahrbare
  Verbindung; Handel ohne Infrastruktur umgeht diese Seehandelsregeln nicht.
  Wasserhandel liefert **50% statt 100%**, wenn nicht beide Städte einen Hafen
  besitzen; zivilisationsspezifische Ersatzgebäude zählen mit. Das gilt auch für
  Flüsse und gemischte Straßen-/Wasserwege, nicht für durchgehende reine Straßenwege.
- **Militärzugang** ersetzt die Bezeichnung Offene Grenzen und regelt die
  Einreise von Einheiten, einschließlich ziviler Einheiten, unabhängig vom Handel.
  Das Abkommen bleibt gegenseitig; einseitige Abkommen sind noch nicht umgesetzt.
- Jede Route verbreitet **Kultur und Religionen in beide Richtungen**, auch
  beim Inlandshandel. Die Bevölkerung der jeweils empfangenden Stadt schwächt
  den Einfluss. Kultur pro Route und Richtung: `abgerundet(5 × Routenwert / Bevölkerung) / 10`:
  die Hälfte der bisherigen ungerundeten Rate, auf eine Nachkommastelle abgerundet.
  Religionschance: `abgerundet(2,5 × Routenwert / Bevölkerung)` Prozent je
  Religion der Partnerstadt, höchstens **12%** pro Route.
  Der Anteil der Besitzerkultur in der empfangenden Stadt verursacht einen
  linearen Abzug: null bei **75%**, bis zu **12 Prozentpunkten bei 100%**.
  Bei vollständig eigener Kultur ist die Handelsverbreitung damit unmöglich.
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

Bestehende Handelsrouten verlagern Nahrung von der ärmeren zur wohlhabenderen
Stadt, auch innerhalb desselben Landes. Wohlstand ist der **lokale Handelsertrag
nach Modifikatoren, ohne Wirtschaftspunkte aus Handelsrouten**. Spezialisten-Gold
und die Einstellung des Goldreglers bestimmen die Richtung nicht. Bei gleichem
Wohlstand findet kein Transfer statt.

- Angeforderte Nahrung: `Routenwert / 2 × (reicherer Wohlstand − ärmerer Wohlstand) / reicherer Wohlstand`.
  Kleine Wohlstandsunterschiede schwächen den Transfer. Bei großem Unterschied
  nähert er sich einer Nahrung je zwei Wirtschaftspunkten der Route. Bei
  gegenseitigen Routen zählt die stärkere Anforderung einmal pro Städtepaar.
- Die gesamten Exporte einer Stadt sind auf **eine Nahrung je Bevölkerungspunkt** begrenzt.
  Es muss kein Überschuss sein: Lieferstädte können langsamer wachsen oder hungern.
  Städte der Größe eins exportieren nur ihren lokalen Überschuss nach Verbrauch
  und Gesundheitskosten.
- Bei übermäßiger Nachfrage werden Exporte proportional aufgeteilt. Die
  Gesamtmenge wird auf ganze Nahrungspunkte abgerundet; verbleibende Punkte
  erhalten die größten Nachkommareste. Gleichstände werden durch eine feste
  Städte-/Routenreihenfolge entschieden. Kleine Anforderungen können leer ausgehen.
- Alle Zuteilungen entstehen gemeinsam einmal pro Spielrunde vor den Spielerzügen
  und werden gespeichert. Sinkende Lieferkapazität reduziert Zusagen während
  der Runde. Zerstörte/eroberte Städte, verlorene Routen, Unruhen, Blockaden,
  Krieg und Embargos beenden betroffene Transfers sofort. Freie Kapazität wird
  bei der nächsten Zuteilung neu verteilt.
- Nahrung wird beim Lieferanten abgezogen und beim Empfänger **nach allen
  Ertragsmodifikatoren** hinzugefügt. Importe werden weder vervielfacht noch erneut
  exportiert. Sie wirken auf Wachstum, Hunger und nahrungsbasierte Einheitenproduktion.
  Infrastruktur, Segeln, Astronomie und Häfen beeinflussen bereits den Routenwert.
- Der Tooltip des Bevölkerungsbalkens zeigt gesamte Importe/Exporte, eine
  Handelsroute den Austausch mit der Partnerstadt: positiv für Import, negativ
  für Export. Bestehende Spielstände beginnen mit der nächsten Spielrunde.

Beispiel: Eine Stadt der Größe vier kann vier Nahrung exportieren.
  Fordern die Ziele vier, zwei und zwei, erhalten sie zwei, eins und eins.
  Verlorene Routen geben dem Lieferanten Nahrung zurück und entziehen sie den Empfängern.

Die Einstellungen `RFCMP_FOOD_EXPORT_PER_POPULATION` und `RFCMP_TRADE_FOOD_COMMERCE_DIVISOR`
in `Assets/XML/GlobalDefines.xml` steuern Bevölkerungsgrenze
und Routenkapazität. Ein Epochen- oder Technologie-Malus auf lokale Nahrung ist
noch nicht enthalten.


## Neue Staatsformen

In jeder Kategorie ist eine Staatsform aktiv. Boni verschiedener Kategorien
addieren sich: Diktatur und Nationalismus ergeben zusammen beispielsweise
+40% Produktion.

**Handel** bezeichnet die Wirtschaftspunkte, die über die Regler auf Gold,
Forschung, Kultur und Spionage verteilt werden. Gold- und Handelswegeinnahmen
sind davon zu unterscheiden. Prozentboni verändern die Erträge, nicht die
Prozentpunkte der Reglereinstellungen. Feste Gebäude- und Verbesserungsboni
gelten je passendem Gebäude beziehungsweise bearbeiteter Verbesserung.

### Regierung

| Staatsform | Benötigte Technologie | Unterhalt | Effekte |
| --- | --- | --- | --- |
| **Stammessystem** | Keine | Keiner | +20% Produktion für alle Einheiten; -20% Forschung; +100% entfernungsabhängiger und durch die Städteanzahl verursachter Städteunterhalt. |
| **Monarchie** | Monarchie | Mittel | +25% Produktion für Welt-, Team- und nationale Wunder. |
| **Republik** | Gesetzgebung | Niedrig | +50% Geburtenrate Großer Persönlichkeiten. |
| **Diktatur** | Faschismus | Hoch | +20% Produktion; keine Kriegsmüdigkeit; -2 Zufriedenheit in jeder Stadt. |
| **Demokratie** | Demokratie | Hoch | +2 Zufriedenheit in jeder Stadt; Wahlen alle zehn Runden ändern zufällig eine andere Staatsformen-Kategorie. |

### Legitimation

| Staatsform | Benötigte Technologie | Unterhalt | Effekte |
| --- | --- | --- | --- |
| **Despotismus** | Keine | Keiner | +1 Zufriedenheit durch Paläste und Monumente einschließlich ihrer zivilisationsspezifischen Ersatzgebäude. |
| **Theokratie** | Göttliches Recht | Hoch | +1 Zufriedenheit je Gebäude der Staatsreligion; -2 Zufriedenheit je Gebäude einer anderen Religion; +10% Kampfstärke für alle Einheiten. |
| **Plutokratie** | Bankwesen | Niedrig | +25% Goldeinnahmen; +50% Handel durch Handelswege. |
| **Nationalismus** | Nationalismus | Mittel | +5 Kultur in jeder Stadt; +20% Produktion; -5 Zufriedenheit in Städten, in denen die Kultur eines anderen Spielers auf dem Stadtfeld größer ist als die des Besitzers. |
| **Rechtsstaat** | Verfassung | Hoch | +2 Zufriedenheit in jeder Stadt; +10% Handel. |

### Arbeit

| Staatsform | Benötigte Technologie | Unterhalt | Effekte |
| --- | --- | --- | --- |
| **Selbstversorgung** | Keine | Keiner | +2 Gesundheit in jeder Stadt; Hüttenverbesserungen wachsen nicht; zugewiesene Spezialisten sind gesperrt und bestehende Zuweisungen werden entfernt; freie Spezialisten bleiben erhalten. |
| **Sklaverei** | Bronzebearbeitung | Niedrig | Bevölkerung kann für Produktion geopfert werden; +2 Handel durch Plantagen. |
| **Leibeigenschaft** | Feudalismus | Niedrig | +1 Nahrung durch Bauernhöfe; -1 Handel durch Dörfer; Bautrupps errichten Verbesserungen 50% schneller. |
| **Planwirtschaft** | Kommunismus | Hoch | +1 Produktion durch Werkstätten, Wassermühlen und Windmühlen; +1 Nahrung durch Bauernhöfe; -20% Handel. |
| **Marktwirtschaft** | Wirtschaftswesen | Mittel | +1 freier Spezialist in jeder Stadt; Hüttenverbesserungen wachsen doppelt so schnell. |

Das Wachstum umfasst sämtliche Ausbaustufen: **Hütte → Weiler → Dorf → Gemeinde**.
Selbstversorgung verhindert die Aufwertung; Marktwirtschaft verdoppelt ihre
Geschwindigkeit. Der Handelsmalus der Leibeigenschaft betrifft ausschließlich
die Stufe **Dorf**. Normale unbeschäftigte Bürger bleiben bei Selbstversorgung
als Möglichkeit für überschüssige Bevölkerung verfügbar.

### Militär

| Staatsform | Benötigte Technologie | Unterhalt | Effekte |
| --- | --- | --- | --- |
| **Kriegergesellschaft** | Keine | Keiner | Nahkampfeinheiten starten mit +2 Erfahrung; Belagerungseinheiten haben -20% Kampfstärke. |
| **Miliz** | Bogenschießen | Niedrig | +30% Stadtverteidigung; -10% Kampfstärke außerhalb des eigenen Gebiets. |
| **Rittertum** | Maschinenbau | Mittel | +25% Produktion für berittene Einheiten; +10% Stadtangriff. |
| **Berufsarmee** | Militärwesen | Hoch | Einheiten starten mit +5 Erfahrung. |
| **Wehrpflicht** | Militärwissenschaft | Mittel | +25% Produktion für alle Einheiten. |

Die Einheitenproduktionsboni von Stammessystem und Wehrpflicht gelten auch für
Bautrupps, Siedler und Missionare. Wehrpflicht gewährt keine zusätzliche
Rekrutierungsfähigkeit; ihr Effekt ist der oben aufgeführte Produktionsbonus.

### Religion

| Staatsform | Benötigte Technologie | Unterhalt | Effekte |
| --- | --- | --- | --- |
| **Ahnenkult** | Keine | Keiner | +1 Kultur durch Monumente einschließlich ihrer zivilisationsspezifischen Ersatzgebäude. |
| **Staatsreligion** | Priestertum | Niedrig | +1 Zufriedenheit in Städten mit Staatsreligion; +100% Produktion für Missionare aller Religionen. |
| **Gottesstaat** | Theologie | Hoch | +2 Zufriedenheit und +10% Produktion in Städten mit Staatsreligion; -2 Zufriedenheit in Städten ohne Staatsreligion. |
| **Toleranz** | Liberalismus | Mittel | Entfernt Unzufriedenheit durch fremde Religionen. |
| **Staatsatheismus** | Wissenschaftliche Methode | Hoch | +10% Forschung; religiöse Gebäude haben keine Effekte; Religionen können sich in den eigenen Städten nicht verbreiten. |

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

Die Profile gelten für alle drei Szenarien und überschreiben keine späteren
Spielerentscheidungen. Bereits vorhandene Zivilisationen in Spielständen behalten
ihre Staatsformen. Alle Profile und Ersatzregeln stehen in
[StartingCivics.md](StartingCivics.md).

## Demokratische Wahlen

Wahlen finden bei aktiver Demokratie auf **globalen Rundenzahlen statt, die
durch zehn teilbar sind**. Zuerst wird eine der anderen vier Kategorien mit
verfügbarer Alternative ausgewählt, dann eine andere Staatsform, die der Spieler
aktuell annehmen kann. Gibt es keine verfügbare Alternative, erfolgt kein
Wechsel. Menschliche Spieler erhalten eine Benachrichtigung.

Beide Auswahlen verwenden den synchronisierten Zufallsgenerator des Spiels.
Die Regierung bleibt Demokratie; Wahlen verursachen keinen zusätzlichen
Stabilitätsmalus für den Übergang.

## Stabilität durch Staatsformen

Die folgenden Kombinationen tragen zur Basisstabilität bei:

| Kombination | Stabilität |
| --- | ---: |
| Stammessystem + Despotismus | +1 |
| Monarchie + Theokratie | +1 |
| Plutokratie + Planwirtschaft | -1 |
| Republik oder Demokratie + Rechtsstaat | +2 |
| Monarchie + Rittertum | +2 |
| Theokratie + Staatsreligion oder Gottesstaat | +2 |
| Plutokratie + Marktwirtschaft | +1 |
| Theokratie + Staatsatheismus | -3 |

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

1. Den Ordner **`RFC MP Plus`** in das **`Mods`**-Verzeichnis von Beyond the Sword kopieren.
2. Den Ordnernamen beibehalten: Die enthaltenen Szenarien verweisen darauf. Der
   ursprüngliche RFC-MP-Mod kann parallel installiert bleiben.
3. RFC MP Plus über das Mod-Menü des Spiels oder
   [Launch RFC MP Plus.bat](<../Launch RFC MP Plus.bat>) starten. Der Starter
   verwendet den üblichen Steam-Installationspfad; bei anderen Installationen
   muss der Pfad angepasst werden.
4. Eines der enthaltenen Szenarien wählen: **3000 v. Chr.**, **800 v. Chr.** oder **600 n. Chr.**.

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
[BUILDING.md](<../RFC MP Plus/CvGameCoreDLL/BUILDING.md>). Der konfigurierte Build
kopiert die neu erzeugte DLL in den Mod-Ordner des Projekts und in den
installierten Mod. Civ4 vor dem Kompilieren schließen, damit die installierte
DLL ersetzt werden kann.
