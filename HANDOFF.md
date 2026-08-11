# DVGP-Website — Handoff

> **Stand:** 2026-08-11 21:30 CEST · **Von:** Claude (Sitzung) · **Rev:** 1
> **ZUERST LESEN.** Das hier ist das komprimierte Gedächtnis des Projekts. Wer das liest, kann
> weiterarbeiten, ohne den Gesprächsverlauf zu kennen. Details: `WORKLOG.md`, `DEPLOYMENT.md`,
> `content/modell.md`.

## Kurzfassung — in 30 Sekunden arbeitsfähig

- **Was das ist:** Website des DVGP e.V. (Deutscher Verband für Gesundheitsförderung und Prävention).
  Statische Seite, ausgeliefert als Cloudflare Worker. **Live unter https://dvgp.info**
- **Stand jetzt:** Fertig und online. Startseite, Rubrik „Wissen" mit 3 Beiträgen, Publikationsseite
  mit 33 Arbeiten, Impressum. Eine Cloud-Routine schreibt ab Do 13.08. montags und donnerstags
  automatisch je einen Beitrag.
- **Nächste Aktion:** Nichts Dringendes. Am **13.08. früh prüfen, ob der erste automatische Beitrag
  sauber durchgelaufen ist** (neue Datei in `content/artikel/`, Commit auf `main`, Seite live).

## Ziel und Abgrenzung

- **Ziel:** Aufklärung. Die Seite erklärt den Gesundheitsbegriff des Verbands und beantwortet
  konkrete Fragen von Betroffenen — belegt, verständlich, ohne Verkaufsabsicht.
- **Im Rahmen:** Inhalte, SEO/AEO, Betrieb der Seite.
- **Nicht im Rahmen:** Mitgliederverwaltung, Shop, Terminbuchung. Mitgliedschaft wird auf der Seite
  bewusst **nicht** beworben (frühe Entscheidung des Vorstands).

## Aktueller Stand

| Bereich | Stand | Notiz |
|---|---|---|
| Domain & DNS | fertig | `dvgp.info` auf Cloudflare, NS `norm` + `rosalie` |
| Mail | läuft | MX weiter bei IONOS (`mx00`/`mx01.ionos.de`) — **nie anfassen** |
| Worker & Deploy | fertig | `dvgp-website`, Custom Domains für Apex und `www` |
| Weiterleitungen | fertig | HTTPS erzwungen, `www` → Apex per Redirect-Regel (301) |
| Startseite | fertig | Systemkritik → Angebot → Gesundheitsbegriff → STARK → Zielgruppen → FAQ → Kontakt |
| Rubrik Wissen | läuft an | 3 Beiträge, Generator steht, Routine aktiv |
| Publikationen | fertig | 33 Arbeiten, `ItemList`/`ScholarlyArticle`-Schema |
| Search Console | fertig | Domain-Property bestätigt, Sitemap eingereicht |
| Bing | offen | noch nicht angemeldet |
| Google-Unternehmensprofil | offen | bewusst zurückgestellt, siehe Entscheidungen |

**Als Nächstes, in dieser Reihenfolge:**
1. Ersten automatischen Beitrag am 13.08. kontrollieren.
2. Bing Webmaster Tools anmelden (Import aus der Search Console).
3. STARK-Dokument im Google Drive korrigieren — Vorlage liegt in
   `content/korrektur-stark-dokument.md`, drei Zahlen sind falsch.

## Aufbau

| Pfad | Zweck |
|---|---|
| `site/` | **alles, was ausgeliefert wird.** Nur dieses Verzeichnis geht live |
| `site/index.html` | Startseite, handgepflegt |
| `site/impressum.html`, `site/404.html` | ebenfalls handgepflegt |
| `site/wissen/`, `site/publikationen/` | **generiert — nicht von Hand ändern** |
| `site/style.css` | ein Stylesheet für alles |
| `content/artikel/*.md` | Quelle der Wissensbeiträge (Frontmatter + Markdown) |
| `content/publikationen.md` | Quelle der Publikationsseite |
| `content/modell.md` | **Das Denkgebäude des Vorstands.** Grundlage jedes Textes |
| `content/SCHREIBWEISE.md` | verbindliche Ton- und Sprachregeln |
| `content/themenplan.md` | Reihenfolge der Beiträge, Kategorien |
| `content/evidenz.md` | Beleg-Landkarte, nach Thesen geordnet, mit Warnungen |
| `content/katalog.md` | Ahrefs-Recherche, Themen mit Volumen und Schwierigkeit |
| `werkzeuge/baue_wissen.py` | Generator: Markdown → HTML + Sitemap + llms.txt |
| `werkzeuge/routine-wissen.md` | Konfiguration der Cloud-Routine |
| `wrangler.toml` | Worker- und Domain-Konfiguration |

**Wie es zusammenhängt:** Markdown in `content/` → `python3 werkzeuge/baue_wissen.py` → HTML in
`site/` → `npx wrangler deploy` oder Push auf `main` (Workers Builds). Der Generator zieht
`sitemap.xml` und `llms.txt` automatisch nach. **Generiertes HTML wird mit eingecheckt** — Cloudflare
baut nichts, es liefert nur aus.

## Entscheidungen und Begründung *(nur ergänzen, nichts löschen)*

- **Kein Framework, reines HTML/CSS** — der Vorstand wollte etwas, das er beim Hoster selbst
  hochladen kann. Später auf Cloudflare Worker umgestellt, die Einfachheit blieb. 17.05.2026
- **Generator ohne fremde Pakete** — Cloudflare führt beim Deploy nur `wrangler deploy` aus. Der
  Generator läuft lokal, sein Ergebnis wird eingecheckt. Eine Abhängigkeit weniger ist eine
  Fehlerquelle weniger. 10.08.2026
- **Mitgliedschafts-Sektion entfernt** — der Vorstand will keine Mitglieder über die Seite werben.
  10.08.2026
- **Ton: „Feldzug, aber sachlich"** — der Verband hat eine Position und vertritt sie deutlich, aber
  jede scharfe Aussage braucht einen Beleg oder einen nachvollziehbaren logischen Schritt. Ich hatte
  erst zu laut, dann zu weich geschrieben; das ist die Mitte. 11.08.2026
- **Themenauswahl nach Schwere, nicht nach Suchvolumen** — ein Thema taugt nur, wenn es schwer
  wiegt, chronisch ist und die üblichen Kurzlösungen nicht tragen. Deshalb steht Muskelkater trotz
  7.800 Suchen nicht oben. 11.08.2026
- **Jeder Beitrag ist eine Kombination „Krafttraining und &lt;Problem&gt;"** — nie eine Übung für
  sich, weil ihr sonst der Bezug zu einer echten Beeinträchtigung fehlt. 11.08.2026
- **Publikationsseite führt auch widersprechende Arbeiten** — wer nur Bestätigendes sammelt,
  betreibt keine Aufklärung, und es nimmt Kritikern den Angriffspunkt. 11.08.2026
- **`html_handling` bleibt auf dem Standard** — ~~kurzzeitig auf `"none"` gesetzt~~, um `.html`-URLs
  direkt auszuliefern; damit lieferte `/` aber 404. Rückgängig, stattdessen saubere URLs ohne
  `.html` überall. 10.08.2026
- **Google-Unternehmensprofil zurückgestellt** — zahlt vor allem auf lokale Suchen ein, der Verband
  arbeitet bundesweit. Inhalte zuerst. 11.08.2026

## Landminen

- **MX-Einträge sind heilig.** `kontakt@dvgp.info` läuft über IONOS. Am 11.08. war die Domain
  mehrere Stunden komplett offline, weil die Zone versehentlich als **`dvpg.info`** angelegt wurde
  (`p` und `g` vertauscht) und deren Nameserver bei IONOS für die richtige Domain eingetragen
  wurden. Vor **jeder** DNS-Änderung: `dig @8.8.8.8 dvgp.info MX` prüfen.
- **Domainnamen zeichenweise prüfen.** Der Vorstand vertippt sich bei „DVGP" nach eigener Aussage
  häufig. Screenshots taugen nicht als Beleg — immer gegen DNS und Registry prüfen.
- **`site/wissen/` und `site/publikationen/` sind generiert.** Änderungen dort sind beim nächsten
  Generatorlauf weg. Quelle ist `content/`.
- **`[assets]` in `wrangler.toml`:** In TOML gehört alles unterhalb einer Tabellenüberschrift zu
  dieser Tabelle. `workers_dev` muss **vor** `[assets]` stehen, sonst wird es verworfen.
- **`.content-page a` ist spezifischer als `.cta-primary`.** Ohne die `:not()`-Ausnahme bekommen
  Buttons auf Inhaltsseiten dunkelrote Schrift auf rotem Grund.
- **`<button>` braucht eine `color`-Angabe**, sonst zeichnet iOS ihn systemblau.
- **Ins FAQ-Schema dürfen nur Überschriften mit Fragezeichen.** Der Generator filtert das; Google
  wertet fragefremde Einträge als Missbrauch des Markups.
- **Nie eine Quelle oder DOI erfinden.** Steht so in `SCHREIBWEISE.md` und im Routinen-Auftrag.
  Lieber keine Quellenliste als eine erfundene.

## Betrieb

```bash
# Seiten neu bauen (nach Änderungen in content/)
python3 werkzeuge/baue_wissen.py

# Veröffentlichen
npx wrangler deploy          # oder: git push origin main (Workers Builds)

# Lokale Vorschau
python3 -m http.server 8000 --directory site

# Kontrolle nach Änderungen
dig @8.8.8.8 dvgp.info MX    # muss mx00/mx01.ionos.de zeigen
for p in "" wissen/ publikationen/ impressum sitemap.xml llms.txt; do
  printf "%-24s %s\n" "/$p" "$(curl -s -o /dev/null -w '%{http_code}' https://dvgp.info/$p)"
done
```

**Umgebung:** wrangler ist mit `marvin.stiebler@gmail.com` angemeldet (Token unter
`~/Library/Preferences/.wrangler/config/`). Repo ist öffentlich. Bildbearbeitung lief über eine
venv mit Pillow — nicht Teil des Projekts, bei Bedarf neu anlegen.

## Werkzeuge und Gepflogenheiten

- **Commits auf Deutsch**, erste Zeile beschreibt die Wirkung, Fließtext erklärt das Warum.
- **PubMed-Konnektor** für Belege. **Ahrefs** für Themenrecherche. **Stock-Images-MCP** für Fotos
  (Unsplash, Fotografen gehören ins Impressum).
- **Cloudflare-Konnektor ist nur lesend** — keine Zonen, kein DNS, kein Deploy. Dafür wrangler.
- **Cloud-Routine:** `trig_01GkwJbEa8epTvbwo57GqZ2e`, Mo + Do 06:00 UTC, Modell `claude-opus-5`,
  Verwaltung unter https://claude.ai/code/routines. Der Auftragstext steht in
  `werkzeuge/routine-wissen.md`.
- **Bilder:** WebP mit JPG-Rückfall, 1200px (Hero 1920), Rohdateien unter `content/bilder-roh/`
  bleiben ungetrackt.

## Offene Fragen

- **Prothesen und Physiotherapie:** Der Vorstand hält die Evidenz für schlecht. Belastbar belegen
  ließ sich bisher nur die Reha-Studie nach Knieprothese (Bade 2017). Die Arbeiten, die er meint —
  „nichts tun versus Prothese nach fünf Jahren" — fehlen noch. Ohne sie bleibt das Thema von der
  Seite draußen.
- **Chronische Entzündung als Steckenbleiben in Phase eins** ist die These des Verbands, aber
  bislang **kein Befund**. In `evidenz.md` als Hypothese gekennzeichnet. Recherche zur Phasenabfolge
  steht aus.
- **Bewegung als Nebenprodukt der Nahrungssuche** — als Bild geführt, nicht als Beleg. Sollte es
  belegt werden, braucht es Quellen.

## Glossar

- **STARK-Prinzip** — System, Toleranz, Anpassung, Regeneration, Kapazität. Die Methodik des Verbands.
- **Erholungsfähigkeit** — Gesundheit = (Robustheit × Restitution) / Herausforderung. Siehe
  `content/modell.md`.
- **AEO** — Answer Engine Optimization: für Antwortmaschinen schreiben statt für Trefferlisten.
  Leitfaden: `~/projects/wll-spezialreinigung-gelsenkirchen/AEO_Guide.md`.
- **Blueprint** — `~/projects/webpage-landlord-blueprint`, Layout- und SEO-Vorlage dieses Projekts.
  Die dortigen **Ton-Regeln gelten hier nicht** (sie sind für Rank-&-Rent geschrieben), die
  technischen Kriterien schon.
