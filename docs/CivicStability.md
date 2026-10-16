# Stabilität durch Civic-Kombinationen

Die Civic-Stabilität wird aus den aktiven Kombinationen berechnet. Einzelne
Civics erhalten keinen pauschalen Stabilitätswert. Die passenden Beiträge
werden addiert und insgesamt auf **−5 bis +5** begrenzt.

| Kombination | Stabilität | Begründung |
| --- | ---: | --- |
| Stammessystem + Despotismus | +1 | Persönliche Autorität und traditionelle Institutionen passen zur Stammesregierung. |
| Monarchie + Theokratie | +1 | Religiöse Legitimation stützt die erbliche Herrschaft. |
| Monarchie + Planwirtschaft | 0 | Dynastische Herrschaft legt die Wirtschaftsordnung nicht fest; zentrale Planung begründet allein weder einen Bonus noch einen Malus. |
| Plutokratie + Planwirtschaft | −1 | Auch wenn vermögende Häuser den Plan gemeinsam kontrollieren, können ihre privaten Vermögensinteressen mit der zentralen Ressourcenverteilung kollidieren. |
| Republik oder Demokratie + Rechtsstaat | +2 | Rechtliche Institutionen stützen die geregelte Ausübung und Übertragung politischer Macht. |
| Monarchie + Rittertum | +2 | Dynastische Herrschaft und die militärische Ordnung des Rittertums passen zusammen. |
| Theokratie + Staatsreligion oder Gottesstaat | +2 | Religiöse Legitimation und die staatliche Religionsordnung stimmen überein. |
| Plutokratie + Marktwirtschaft | +1 | Politischer Einfluss durch Vermögen und privatwirtschaftliche Organisation passen zusammen. |
| Theokratie + Toleranz | −3 | Ein religiöser Herrschaftsanspruch steht in Spannung zur Gleichstellung fremder Glaubensrichtungen. |

Demokratie ignoriert alle negativen Kombinationsbeiträge, also auch den Malus
für Plutokratie + Planwirtschaft. Positive Beiträge bleiben erhalten.

Die besonderen Ländernamen für Monarchie beziehungsweise Plutokratie mit
Planwirtschaft ändern diese Wertung nicht. Monarchie + Planwirtschaft bleibt
neutral; der kleine Malus für Plutokratie + Planwirtschaft bleibt als bewusste
Balance-Entscheidung bestehen. Treffen beide Kombinationen zusammen, entsteht
ohne weitere Kombinationsbeiträge ein Wert von −1.

Alle anderen Kombinationen sind in diesem Modell neutral. Die Werte sind
Spielbalance-Entscheidungen und keine Aussage, dass eine Wirtschafts- oder
Regierungsform grundsätzlich überlegen wäre.

## Berechnung und Wahlen

- Die Berechnung verwendet die XML-Namen der Civics. Sie hängt nicht von ihrer
  Reihenfolge oder numerischen ID ab.
- Der Beitrag geht in die bestehende Neuberechnung der Basisstabilität alle
  drei Runden ein. Er wird nicht als dauerhafter Zugewinn pro Runde aufaddiert.
- Demokratische Wahlen ändern weiterhin alle zehn Runden eine andere Civic-Spalte.
  Für Wahlen gibt es keine zusätzliche Stabilitätsstrafe. Die Kombinationswerte
  gelten auch, wenn die Kombination durch eine Wahl entsteht.
- Die allgemeine Zufriedenheits- und Wirtschaftsauswertung berücksichtigt die
  tatsächlichen Folgen der Civics weiterhin.

## Entfernte Sonderregeln

- Pauschale Einzelwerte für alle 25 Civics.
- Automatische Stabilitätsrettung unter Stammessystem, Monarchie und Diktatur.
- Zusätzliche Schwellenboni für bereits stabile Republiken und Demokratien.
- Die Wirtschaftskrise speziell für Marktwirtschaft, einschließlich ihrer
  Ansteckung anderer Staaten über offene Grenzen.
- Die acht Runden lange Stabilitätsstrafe nach dem Verlassen der Planwirtschaft.
- Zusätzliche religiöse Stadtstrafen speziell unter Staatsreligion und Gottesstaat.
- Die abweichende Kulturgrenze unter Nationalismus.
- Der zusätzliche Gefängnis-Baubonus speziell für Diktatur.

Der veraltete-Civics-Malus und die Demokratie-Übergangsstrafe wurden bereits
zuvor entfernt und bleiben deaktiviert.

## Bestehende Spielstände und Multiplayer

Die gespeicherten Felder für alte Krisen-Countdowns bleiben erhalten. Sie werden
für diese Regeln nicht mehr ausgewertet, sodass vorhandene Spielstände ihre
Struktur behalten. Bereits vergangene Stabilitätsänderungen werden nicht
rückwirkend umgeschrieben. Der neue Kombinationsbeitrag wird mit der nächsten
Neuberechnung der Basisstabilität wirksam.

Die Berechnung benötigt keinen Zufallsaufruf und keine lokalen UI-Daten. Alle
Multiplayer-Spieler müssen dieselbe aktualisierte `Stability.py` verwenden.
Eine Prüfung im laufenden Multiplayer-Spiel steht noch aus.

Implementierung: `Stability.getCivicCombinationStability` und
`Stability.updateBaseStability` in `Assets/Python/Stability.py`.
