# Routine: wöchentlicher Wissens-Beitrag

Fertig konfiguriert, aber **noch nicht aktiv**. Beim Anlegen kam:

```
HTTP 403 — You don't have access to a repository this routine uses.
```

Grund: `marvinstiebler/dvgp-website` ist privat, und die Claude-GitHub-App hat dafür
keine Freigabe. Das ist eine reine Berechtigungsfrage, kein Fehler in der Konfiguration.

## Was freizugeben ist

GitHub → Settings → Applications → Claude → **Repository access** → `dvgp-website`
hinzufügen. Danach lässt sich die Routine ohne weitere Änderung anlegen.

## Konfiguration

| | |
|---|---|
| Name | DVGP Wissen — wöchentlicher Beitrag |
| Takt | `0 6 * * 1` — jeden Montag 06:00 UTC = **08:00 Berlin** |
| Modell | `claude-opus-5` |
| Umgebung | Default (`env_011fpeEsxWpkqwY6cMbqGp2Y`) |
| Repo | `https://github.com/marvinstiebler/dvgp-website` |
| Werkzeuge | Bash, Read, Write, Edit, Glob, Grep |
| Konnektoren | keine |

Ahrefs wird nicht gebraucht: Die Themen samt Suchvolumen stehen bereits in
`content/themenplan.md`. Der Agent nimmt die oberste offene Frage aus der Liste
„Als Nächstes". Cloud-Routinen haben ohnehin keinen Zugriff auf die
interaktiv angemeldeten Konnektoren.

## Der Auftrag an den Agenten

> Du schreibst den wöchentlichen Beitrag für die Rubrik "Wissen" der Website des DVGP
> (Deutscher Verband für Gesundheitsförderung und Prävention, dvgp.info). Arbeite
> selbstständig bis zum Push — es gibt keine Rückfragemöglichkeit.
>
> **SCHRITT 1 — Kontext lesen (nicht überspringen):**
> - `content/SCHREIBWEISE.md` — verbindliche Ton- und Sprachregeln
> - `content/themenplan.md` — Themen mit Suchvolumen und die Reihenfolge am Dateiende
> - `content/artikel/*.md` — die bereits erschienenen Beiträge als Vorbild für Aufbau und Ton
>
> **SCHRITT 2 — Thema wählen:**
> Nimm die oberste Frage aus der Liste "Als Nächstes" am Ende von
> `content/themenplan.md`, zu der es noch keine Datei in `content/artikel/` gibt.
> Schwerpunkt des Projekts sind Krafttraining, Langhanteltraining und gesundes Altern.
>
> **SCHRITT 3 — Beitrag schreiben:**
> Lege `content/artikel/<slug>.md` an, mit diesem Frontmatter:
>
> ```
> ---
> titel: <die Frage wörtlich, so wie Menschen sie suchen>
> beschreibung: <ein bis zwei Sätze, beantworten die Frage bereits>
> datum: <heutiges Datum als JJJJ-MM-TT, per `date +%F` ermitteln>
> cluster: <Gesundes Altern | Krafttraining | Belastung und Erholung | Prävention | Arbeit und Betrieb>
> slug: <kleingeschrieben, mit Bindestrichen, ohne Umlaute>
> ---
> ```
>
> Harte Vorgaben für den Text:
> - 700 bis 1100 Wörter.
> - Der ERSTE Satz beantwortet die Titelfrage direkt und vollständig. Keine Hinführung.
> - Zwischenüberschriften (`##`) sind selbst echte Fragen und werden im ersten Satz
>   darunter beantwortet. Nur Überschriften mit Fragezeichen landen im FAQ-Schema.
> - Der Beitrag endet mit "## Einordnung im STARK-Prinzip" (ohne Fragezeichen).
> - Mindestens eine Tabelle oder Liste.
> - Sprache: ein Zehntklässler muss alles verstehen. Ein Gedanke pro Satz. Trotzdem
>   fachlich ernsthaft, kein Ratgeber-Ton, keine Werbesprache, keine Ausrufezeichen.
> - VERBOTEN: Diagnosen, Behandlungsempfehlungen, Dosierungen, Präparate-Empfehlungen,
>   Heilungsversprechen, nicht belegbare Wirksamkeitszahlen, KI-Floskeln.
> - Markdown-Umfang: `##`, `###`, Absätze, Listen, Zitate, Tabellen, fett, kursiv, Links.
>   Nichts anderes — der Generator unterstützt nur das.
>
> **SCHRITT 4 — Bauen und prüfen:**
> `python3 werkzeuge/baue_wissen.py`, dann prüfen, dass die Datei unter `site/wissen/`
> liegt, der Durchlauf fehlerfrei war und im JSON-LD nur Fragen mit Fragezeichen stehen.
>
> **SCHRITT 5 — Datenbank pflegen:**
> Die Frage in `content/themenplan.md` von "Als Nächstes" nach "Erschienen"
> verschieben, mit Datum.
>
> **SCHRITT 6 — Veröffentlichen:**
> Alles committen und auf `main` pushen. Commit-Nachricht auf Deutsch. Der Push löst bei
> Cloudflare Workers Builds das Deployment aus.
>
> Wenn etwas nicht geht: nichts halb Fertiges pushen, sondern den Grund im
> Abschlussbericht nennen.

## Danach

Routinen verwalten: https://claude.ai/code/routines
