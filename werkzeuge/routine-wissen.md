# Routine: wöchentlicher Wissens-Beitrag

Fertig konfiguriert, **noch nicht aktiv**. Beim Anlegen kommt weiterhin:

```
HTTP 403 — You don't have access to a repository this routine uses.
```

Zuletzt geprüft am 10.08.2026, auch nachdem der Zugriff bereits erteilt wurde. Es ist
eine reine Berechtigungsfrage, an der Konfiguration liegt es nicht.

## Was zu prüfen ist

1. **github.com/settings/installations** → Eintrag *Claude* → *Repository access*.
   Entweder „All repositories" oder `dvgp-website` in der Auswahlliste.
2. Es gibt mehrere Claude-Integrationen. Die Routine läuft über **Claude Code**, nicht
   über die claude.ai-Chat-Anbindung — die Freigabe muss bei der richtigen liegen.
3. Freigaben brauchen manchmal ein paar Minuten. Danach erneut versuchen.

Alternative, falls es dabei bleibt: das Repo auf öffentlich stellen. Die Seite ist
ohnehin für die Öffentlichkeit bestimmt, im Repo stehen keine Zugangsdaten.

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

Der Themenplan enthält bereits eine geprüfte Quellenbasis mit DOIs. Cloud-Routinen
erreichen die interaktiv angemeldeten Konnektoren nicht — PubMed steht dort also nicht
zur Verfügung, deshalb die harte Regel gegen erfundene Quellen im Auftragstext.

## Der Auftrag an den Agenten

> Du schreibst den wöchentlichen Beitrag für die Rubrik "Wissen" der Website des DVGP
> (Deutscher Verband für Gesundheitsförderung und Prävention, dvgp.info). Arbeite
> selbstständig bis zum Push — es gibt keine Rückfragemöglichkeit.
>
> **SCHRITT 1 — Kontext lesen, nicht überspringen:**
> - `content/SCHREIBWEISE.md` — verbindliche Ton- und Sprachregeln
> - `content/themenplan.md` — Themen und Reihenfolge
> - `content/artikel/*.md` — die erschienenen Beiträge als Vorbild für Aufbau und Ton
>
> **SCHRITT 2 — Thema wählen:**
> Nimm die oberste Frage aus "Als Nächstes" in `content/themenplan.md`, zu der es noch
> keine Datei in `content/artikel/` gibt.
>
> **SCHRITT 3 — Beitrag schreiben:**
> Lege `content/artikel/<slug>.md` an mit Frontmatter (`titel`, `beschreibung`, `datum`
> per `date +%F`, `cluster`, `slug`).
>
> Harte Vorgaben:
> - 800 bis 1200 Wörter.
> - Der ERSTE Satz beantwortet die Titelfrage direkt und vollständig.
> - Zwischenüberschriften sind selbst echte Fragen, im ersten Satz beantwortet. Nur
>   Überschriften mit Fragezeichen landen im FAQ-Schema.
> - Ende: "## Einordnung im STARK-Prinzip", danach nur noch der Quellenteil.
> - Mindestens eine Tabelle oder Liste.
> - Ein Zehntklässler muss alles verstehen. Trotzdem fachlich ernsthaft.
> - VERBOTEN: Diagnosen, Behandlungsempfehlungen, Dosierungen, Präparate,
>   Heilungsversprechen, erfundene Zahlen, KI-Floskeln.
>
> **SCHRITT 4 — Belege:**
> Jede fachliche Aussage über Alltagswissen hinaus wird belegt, bevorzugt mit
> systematischen Übersichtsarbeiten, Metaanalysen oder Leitlinien. Quellen am Ende unter
> "## Quellen" mit Titel, Jahr und DOI-Link. Der Themenplan enthält eine geprüfte
> Ausgangsbasis.
> **Erfinde niemals eine Quelle oder eine DOI.** Was sich nicht belegen lässt, wird
> vorsichtiger formuliert oder weggelassen. Die Aussage im Text muss das hergeben, was
> die Quelle wirklich zeigt.
>
> **SCHRITT 5 — Bauen und prüfen:** `python3 werkzeuge/baue_wissen.py`
>
> **SCHRITT 6 — Themenplan pflegen:** Frage von "Als Nächstes" nach "Erschienen".
>
> **SCHRITT 7 — Veröffentlichen:** committen, auf `main` pushen. Der Push löst das
> Deployment aus.
>
> Wenn etwas nicht funktioniert: nichts halb Fertiges pushen, sondern den Grund im
> Abschlussbericht nennen.

## Danach

Routinen verwalten: https://claude.ai/code/routines
