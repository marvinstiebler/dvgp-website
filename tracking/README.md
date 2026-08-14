# Sichtbarkeits-Tracking

Wo dvgp.info bei Google steht, gemessen über die Zeit.

## Wie es aufgebaut ist

Das Messgerät und die Akte sind getrennt — genau wie im Blueprint beschrieben
(`webpage-landlord-blueprint/HANDOFF-VISIBILITY.md`).

| Teil | Wer | Was |
|---|---|---|
| Messgerät | `visibility-mcp-server` (MCP, lokal) | misst und gibt zurück, speichert nichts |
| Akte | dieses Verzeichnis | eine JSON-Datei je Messtag, versioniert im Repo |
| Auswertung | `werkzeuge/verlauf_sichtbarkeit.py` | baut daraus [VERLAUF.md](VERLAUF.md) |
| Takt | geplante Aufgabe `dvgp-sichtbarkeit` | montags 08:00, misst und pusht selbst |

Welche Suchbegriffe gemessen werden, steht im Block `tracking` in
[content-engine.json](../content-engine.json). **Wer einen Beitrag zu einem neuen Thema
veröffentlicht, trägt den zugehörigen Suchbegriff dort nach** — sonst wächst die Rubrik,
aber die Messung nicht.

## Was diese Zahlen sind und was nicht

Gemessen wird von neutraler Infrastruktur mit fester Koordinate (Vereinssitz Magdeburg),
nicht aus einem Browser. Was hier steht, weicht deshalb von dem ab, was du selbst
angezeigt bekommst — Google personalisiert nach Anmeldung, Verlauf und Standort.

Beides ist echt. Der Wert dieser Reihe ist der **gleichbleibende Bezugspunkt über die
Zeit**, nicht die Vorhersage eines einzelnen Bildschirms. Ein Rang, der von 40 auf 12
wandert, ist eine Aussage. Ein einzelner Rang ist keine.

Der DVGP ist ein bundesweiter Verband, kein lokales Geschäft. Deshalb kein Geo-Grid und
kein Local Pack — das sind Werkzeuge für Betriebe mit Einzugsgebiet.

## Zur Nulllinie vom 14.08.2026

Die Domain war zu dem Zeitpunkt drei Tage alt und trug vier Beiträge.

- **Bei der Verbandssuche Platz 5.** Der einzige Treffer. Über der Seite stehen zwei
  eingeführte Verbände und `dvgp.org` — ein Namensnachbar, den man im Blick behalten
  sollte.
- **Bei allen inhaltlichen Suchen nicht in den Ergebnissen.** Erwartbar. Oben stehen
  Krankenkassen, Kliniken und das IQWiG — Domains mit jahrelanger Historie.
- **Ahrefs meldet überall 0.** Das heißt „noch nicht im Index", nicht „nicht vorhanden".
  Neue Domains nimmt Ahrefs mit Wochen Verzögerung auf.
- **Bei fünf von sechs Suchen zeigt Google eine KI-Übersicht.** Genau darauf zielt die
  Bauweise der Beiträge: Frage als Überschrift, Antwort im ersten Satz, FAQ-Schema.
  Ob es trägt, zeigt diese Reihe.

Realistisch bewegt sich vor mehreren Wochen nichts. Stillstand in den ersten Messungen
ist kein Befund, aus dem man etwas ableiten sollte.
