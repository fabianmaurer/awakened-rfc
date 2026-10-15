# Awakened Rhye's and Fall of Civilization

[English](README.md) | **Deutsch**

**Awakened RFC** · [GitHub](https://github.com/fabianmaurer/awakened-rfc)

Eine Mehrspieler-Überarbeitung von **Rhye's and Fall Multiplayer** für
**Civilization IV: Beyond the Sword**: eine Zivilisation durch die Geschichte
führen, mit einheitlicherer Wirtschaft, neuen Staatsformen und Handel, der
Kultur und Religion prägt. RFC-Weltkarten, historische Gründungen, einzigartige
Fähigkeiten und Siegziele bleiben erhalten.

## Was ändert sich?

- **25 neue Staatsformen in fünf Kategorien**, mit neuen Illustrationen und
  historisch passenden Startprofilen. Demokratie hält alle zehn Runden Wahlen ab,
  die eine andere Kategorie zufällig ändern.
- **Stabilität durch passende Staatsformen**, insgesamt begrenzt auf −5 bis +5.
  Der Malus für veraltete Staatsformen entfällt.
- **Einheitlichere Wirtschaft:** Individuelle Anpassungen für Wachstum,
  Produktion, Forschung und Unterhalt entfallen; die Inflation bleibt bei null.
  Gemeinsame Regeln für Zivilisationsgruppen bleiben bestehen.
- **Technologieabhängiges Wachstum:** Ein gemeinsamer Malus von 30% auf den
  positiven Wachstumsüberschuss sinkt je bekannter Technologie um 0,5 Prozentpunkte
  und entfällt ab 60 Technologien. Nahrungsproduktion und Verbrauch bleiben gleich.
- **Landerschließung:** Bauernhöfe auf Schwemmland ab Landwirtschaft;
  Bautrupps können Sumpf ab Maschinenbau zu Grasland trockenlegen.
- **Handel ohne Straßen oder Grenzabkommen:** 50% Effektivität bis Entfernung 5,
  danach linear sinkend auf null bei 15. Straßen ermöglichen 100% ohne Entfernungslimit; Wasserwege
  benötigen Segeln und sind bis Astronomie auf zwölf Felder begrenzt.
  Wasserhandel wird halbiert, wenn nicht beide Städte einen Hafen besitzen.
  Häfen sind auch eine Landkachel hinter der Meeresküste baubar und verbessern
  bearbeitete Wasserfelder.
  Routen verbreiten Kultur und Religion in
  beide Richtungen und ersetzen die bisherige passive Religionsverbreitung.
  Missionare bleiben erhalten. Kulturelle Homogenität und heilige Städte hemmen
  Religionen durch Handel; Staatsatheismus verhindert religiöse Verbreitung.
- **Nahrungshandel versorgt wohlhabende Städte:** Routen verlagern Nahrung
  aus ärmeren Städten, begrenzt auf eine Nahrung je Bevölkerungspunkt des Lieferanten.
  Embargos und Blockaden können importabhängige Städte in Hungersnot bringen.
- **Militärzugang** ersetzt Offene Grenzen und bleibt gegenseitig.
  **Handelsembargos** sind ab Währung im Außenberater möglich.
- **Vorwarnungen vor Gründungen:** Feld-Tooltips zeigen zukünftige Wechselgebiete;
  betroffene Städte erhalten drei Runden vor dem ersten Gebietswechsel Unruhen.
- **Kulturaufstände ersetzen direktes Überlaufen** regulärer Städte:
  25% Bevölkerungsverlust, weniger aufständische Kultur und zwei Barbareneinheiten
  je verlorenem Bevölkerungspunkt. Barbarische und unabhängige Städte können
  weiterhin kulturell überlaufen. Kulturelle Revolten benötigen mehr als 50%
  fremde Kultur einer einzelnen Zivilisation auf dem Stadtfeld.
- **Dynamische deutsche und englische Ländernamen**, inspiriert von historischen
  Staaten und plausiblen alternativen Entwicklungen.
- **Eroberte Städte umsiedeln:** Bei mehr als 25% eigener Team-Stadtkultur lässt
  sich die Stadt im Eroberungsdialog auflösen und durch einen Siedler ersetzen.

## Produktionskonvertierungen

| Konvertierung | Verfügbar ab | Effektivität |
| --- | --- | ---: |
| Warenverkauf | Spielbeginn | 25% in Gold |
| Wohlstand | Währung; ersetzt Warenverkauf | 50% in Gold |
| Forschung | Alphabet | 25% in Forschung |
| Kultur | Musik | 50% in Kultur |

## Staatsformen

Eine Staatsform pro Kategorie. **Handel** bezeichnet die Wirtschaftspunkte,
die auf Gold, Forschung, Kultur und Spionage verteilt werden, nicht nur Gold.

<details>
<summary>Alle 25 Staatsformen: Technologien, Unterhalt und Boni</summary>

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

### Militär

| Staatsform | Benötigte Technologie | Unterhalt | Effekte |
| --- | --- | --- | --- |
| **Kriegergesellschaft** | Keine | Keiner | Nahkampfeinheiten starten mit +2 Erfahrung; Belagerungseinheiten haben -20% Kampfstärke. |
| **Miliz** | Bogenschießen | Niedrig | +30% Stadtverteidigung; -10% Kampfstärke außerhalb des eigenen Gebiets. |
| **Rittertum** | Maschinenbau | Mittel | +25% Produktion für berittene Einheiten; +10% Stadtangriff. |
| **Berufsarmee** | Militärwesen | Hoch | Einheiten starten mit +5 Erfahrung. |
| **Wehrpflicht** | Militärwissenschaft | Mittel | +25% Produktion für alle Einheiten. |

### Religion

| Staatsform | Benötigte Technologie | Unterhalt | Effekte |
| --- | --- | --- | --- |
| **Ahnenkult** | Keine | Keiner | +1 Kultur durch Monumente einschließlich ihrer zivilisationsspezifischen Ersatzgebäude. |
| **Staatsreligion** | Priestertum | Niedrig | +1 Zufriedenheit in Städten mit Staatsreligion; +100% Produktion für Missionare aller Religionen. |
| **Gottesstaat** | Theologie | Hoch | +2 Zufriedenheit und +10% Produktion in Städten mit Staatsreligion; -2 Zufriedenheit in Städten ohne Staatsreligion. |
| **Toleranz** | Liberalismus | Mittel | Entfernt Unzufriedenheit durch fremde Religionen. |
| **Staatsatheismus** | Wissenschaftliche Methode | Hoch | +10% Forschung; religiöse Gebäude haben keine Effekte; Religionen können sich in den eigenen Städten nicht verbreiten. |

</details>

## Spielen

1. **`Awakened RFC`** in den **`Mods`**-Ordner von Beyond the Sword kopieren.
   Den Namen beibehalten; der ursprüngliche Mod kann daneben installiert bleiben.
2. Über das Mod-Menü oder [den Starter](<Launch Awakened RFC.bat>) laden
   (für Steam eingerichtet).
3. **3000 v. Chr.**, **800 v. Chr.**, **600 n. Chr.** oder **840 n. Chr.** wählen. Alle Mitspieler
   benötigen identische Mod-Dateien und DLLs.

Nach Textänderungen beim Start **Shift gedrückt halten**. Nach Änderungen an
XML-Staatsformenboni ein neues Spiel beginnen. Die Validierung der Überarbeitung
im Mehrspielerbetrieb steht noch aus.

## Details und Entwicklung

[Ausführliche Spielregeln](docs/Gameplay.de.md) · [Start-Staatsformen](docs/StartingCivics.md) ·
[Staatsformen-Stabilität](docs/CivicStability.md) · [Implementierung](docs/CivicEffects.md) ·
[Ländernamen](docs/CountryNames.csv) · [Namensregeln](docs/CountryNaming.md)

Die DLL benötigt den ursprünglichen **32-Bit-VC7.1-Werkzeugsatz**. Siehe
[Kompilierungsanleitung](<Awakened RFC/CvGameCoreDLL/BUILDING.md>) und [AGENTS.md](AGENTS.md).
