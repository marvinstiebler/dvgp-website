#!/usr/bin/env python3
"""Baut tracking/VERLAUF.md aus den Messdateien in tracking/messungen/.

Das Messen macht der visibility-MCP-Server, der nichts speichert. Dieses Skript
führt nur die Akte: es liest alle abgelegten Messungen und schreibt daraus eine
Tabelle, in der man die Bewegung je Suchbegriff auf einen Blick sieht.

Ohne Abhängigkeiten, nur Standardbibliothek.
"""

import json
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
MESSUNGEN = WURZEL / "tracking" / "messungen"
ZIEL = WURZEL / "tracking" / "VERLAUF.md"


def lies_messungen() -> list[dict]:
    dateien = sorted(MESSUNGEN.glob("*.json"))
    if not dateien:
        raise SystemExit(f"Keine Messungen unter {MESSUNGEN}")
    return [json.loads(p.read_text(encoding="utf-8")) for p in dateien]


def rang_zelle(eintrag: dict | None) -> str:
    """Ein Rang als Tabellenzelle. Nicht gefunden ist nicht dasselbe wie nicht gemessen."""
    if eintrag is None:
        return "–"
    if not eintrag.get("gefunden"):
        return "—"
    return str(eintrag["rang"])


def bewegung(reihe: list[str]) -> str:
    """Vergleicht die letzte gemessene Position mit der ersten."""
    zahlen = [(i, int(w)) for i, w in enumerate(reihe) if w.isdigit()]
    if not zahlen:
        return "noch nicht in den Top 100"
    if len(zahlen) == 1:
        return f"neu auf {zahlen[0][1]}"
    diff = zahlen[0][1] - zahlen[-1][1]
    if diff > 0:
        return f"**{diff} Plätze besser**"
    if diff < 0:
        return f"{-diff} Plätze schlechter"
    return "unverändert"


def main() -> None:
    laeufe = lies_messungen()
    datumsspalten = [lauf["datum"] for lauf in laeufe]

    # Alle je gemessenen Suchbegriffe, in der Reihenfolge ihres ersten Auftretens.
    keywords: list[str] = []
    for lauf in laeufe:
        for m in lauf["messungen"]:
            if m["keyword"] not in keywords:
                keywords.append(m["keyword"])

    zeilen = [
        "# Sichtbarkeit im Verlauf",
        "",
        "Erzeugt von `werkzeuge/verlauf_sichtbarkeit.py`. Nicht von Hand bearbeiten —",
        "die Zahlen stehen in `tracking/messungen/`.",
        "",
        "Gemessen wird von neutraler Infrastruktur mit fester Koordinate, nicht aus einem",
        "Browser. Was hier steht, weicht deshalb von dem ab, was du selbst angezeigt",
        "bekommst — Google personalisiert nach Anmeldung, Verlauf und Standort. Beides ist",
        "echt. Der Wert dieser Tabelle ist der **gleichbleibende Bezugspunkt über die Zeit**,",
        "nicht die Vorhersage eines einzelnen Bildschirms.",
        "",
        "`—` heißt: gemessen, aber nicht in den Ergebnissen. `–` heißt: an dem Tag nicht gemessen.",
        "",
        "| Suchbegriff | " + " | ".join(datumsspalten) + " | Bewegung |",
        "|---|" + "---|" * (len(datumsspalten) + 1),
    ]

    for kw in keywords:
        reihe = []
        for lauf in laeufe:
            treffer = next((m for m in lauf["messungen"] if m["keyword"] == kw), None)
            reihe.append(rang_zelle(treffer))
        zeilen.append(f"| {kw} | " + " | ".join(reihe) + f" | {bewegung(reihe)} |")

    # Domain-Metriken, sofern erfasst
    metrik_laeufe = [l for l in laeufe if l.get("domain_metriken")]
    if metrik_laeufe:
        zeilen += [
            "",
            "## Domain-Werte (Ahrefs)",
            "",
            "| Datum | Domain Rating | Organische Keywords | Geschätzter Traffic |",
            "|---|---|---|---|",
        ]
        for lauf in metrik_laeufe:
            m = lauf["domain_metriken"]
            zeilen.append(
                f"| {lauf['datum']} | {m.get('domain_rating', '–')} | "
                f"{m.get('organic_keywords', '–')} | {m.get('organic_traffic', '–')} |"
            )
        zeilen += [
            "",
            "Eine 0 heißt bei einer jungen Domain **„noch nicht im Index“**, nicht",
            "„nicht vorhanden“. Ahrefs nimmt neue Domains mit Verzögerung auf.",
        ]

    # Search Console -- was Google selbst meldet. Von Hand eingetragen, sofern vorhanden.
    gsc_laeufe = [l for l in laeufe if l.get("search_console")]
    if gsc_laeufe:
        zeilen += [
            "",
            "## Was die Search Console meldet",
            "",
            "Googles eigene Zahlen — echte Einblendungen, nicht gemessene Positionen.",
            "",
            "| Stand | Zeitraum | Impressionen | Klicks | Ø Position |",
            "|---|---|---|---|---|",
        ]
        for lauf in gsc_laeufe:
            g = lauf["search_console"]
            zeilen.append(
                f"| {lauf['datum']} | {g.get('zeitraum', '–')} | {g.get('impressionen', '–')} | "
                f"{g.get('klicks', '–')} | {g.get('durchschnittliche_position', '–')} |"
            )
        anfragen = gsc_laeufe[-1]["search_console"].get("suchanfragen", [])
        if anfragen:
            zeilen += [
                "",
                f"Suchanfragen im jüngsten Stand ({gsc_laeufe[-1]['datum']}):",
                "",
                "| Suchanfrage | Impressionen | Klicks |",
                "|---|---|---|",
            ]
            for a in anfragen:
                zeilen.append(
                    f"| {a['anfrage']} | {a.get('impressionen', '–')} | {a.get('klicks', '–')} |"
                )

    # Wer sonst oben steht -- nur der jüngste Lauf, sonst wird es unlesbar
    letzter = laeufe[-1]
    zeilen += [
        "",
        f"## Wer aktuell oben steht (Stand {letzter['datum']})",
        "",
        "| Suchbegriff | Platz 1 bis 3 |",
        "|---|---|",
    ]
    for m in letzter["messungen"]:
        zeilen.append(f"| {m['keyword']} | " + ", ".join(m.get("top5", [])[:3]) + " |")

    ZIEL.parent.mkdir(parents=True, exist_ok=True)
    ZIEL.write_text("\n".join(zeilen) + "\n", encoding="utf-8")
    print(f"  geschrieben  {ZIEL.relative_to(WURZEL)}   "
          f"({len(keywords)} Suchbegriffe, {len(laeufe)} Messtage)")


if __name__ == "__main__":
    main()
