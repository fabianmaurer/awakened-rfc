# RFC MP Plus

[English](README.md) | **Deutsch**

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
| Einfache Geldkonvertierung | Keine; von Beginn an verfügbar | 25% Produktion in Gold |
| Geldkonvertierung | Währung | 50% Produktion in Gold |
| Forschung | Alphabet | 25% Produktion in Forschung |
| Kultur | Musik | 50% Produktion in Kultur |

Währung ersetzt die einfache durch die stärkere Geldkonvertierung. Laufende
und vorgemerkte einfache Geldkonvertierungen werden automatisch umgestellt;
andere Aufträge in der Produktionsliste bleiben erhalten. Die Werte gelten
einheitlich für alle Zivilisationen und Spieler.

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
| **Kriegergesellschaft** | Keine | Keiner | Einheiten starten mit +2 Erfahrung; Belagerungseinheiten haben -20% Kampfstärke. |
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
[StartingCivics.md](docs/StartingCivics.md).

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
[CivicStability.md](docs/CivicStability.md); technische Details in
[CivicEffects.md](docs/CivicEffects.md).

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

## Dynamische Ländernamen

Ländernamen reagieren auf Regierung, Legitimation, Wirtschaft, Staatsreligion
und Reichsgröße. Bestehende Vasallen- und Kolonialnamen haben Vorrang. Namen
werden nach Staatsformen- und Religionswechseln sowie einmal pro Spielerzug
aktualisiert.

Der Katalog enthält **569 Einträge mit 356 unterschiedlichen deutsch-englischen
Namenspaaren**. Die Namen verwenden passende historische Bezeichnungen und
plausible alternative Entwicklungen. Ein Name muss nicht jede aktive Staatsform
abbilden.

Beispiele sind das **Heilige Römische Reich**, die **Hanse**, die **Batavische
Republik**, die **Republik Nowgorod**, das **Reich des Himmels**, das **Himmlische
Reich des Großen Friedens**, das **Land der vier Weltgegenden**, das **Königreich
Italien** und **Tawantinsuyu**. Unterschiedliche
Staatsformen-Kombinationen können bewusst denselben natürlichen Ländernamen
verwenden.

Der Katalog steht in [CountryNames.csv](docs/CountryNames.csv), die Auswahlregeln
in [CountryNaming.md](docs/CountryNaming.md). Die neuen Ländernamen sind auf
Deutsch und Englisch vorhanden; Französisch, Italienisch und Spanisch verwenden
englische Ersatztexte.

## Installation und Mehrspieler

1. Den Ordner **`RFC MP Plus`** in das **`Mods`**-Verzeichnis von Beyond the Sword kopieren.
2. Den Ordnernamen beibehalten: Die enthaltenen Szenarien verweisen darauf. Der
   ursprüngliche RFC-MP-Mod kann parallel installiert bleiben.
3. RFC MP Plus über das Mod-Menü des Spiels oder
   [Launch RFC MP Plus.bat](<Launch RFC MP Plus.bat>) starten. Der Starter
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

Voraussetzungen und Kompilierungsablauf stehen in [AGENTS.md](AGENTS.md) und
[BUILDING.md](<RFC MP Plus/CvGameCoreDLL/BUILDING.md>). Der konfigurierte Build
kopiert die neu erzeugte DLL in den Mod-Ordner des Projekts und in den
installierten Mod. Civ4 vor dem Kompilieren schließen, damit die installierte
DLL ersetzt werden kann.
