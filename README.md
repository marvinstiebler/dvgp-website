# dvgp-website

Website des **DVGP — Deutscher Verband für Gesundheitsförderung und Prävention**.
Statische Site, ausgeliefert als **Cloudflare Worker mit Static Assets**. Live unter
**https://dvgp.info**

> **Wer hier neu einsteigt — auch als KI — liest zuerst [HANDOFF.md](HANDOFF.md).**
> Dort steht der aktuelle Stand, die getroffenen Entscheidungen samt Begründung und die
> Fallstricke. Die Änderungshistorie führt [WORKLOG.md](WORKLOG.md).

---

## Was von allein läuft

Die Seite pflegt sich weitgehend selbst. Wichtig ist zu verstehen, **wo** was läuft —
daran hing schon mehr als ein Fehler.

```
Mo/Do 08:00   Cloud-Routine schreibt den Beitrag
                 · liest SCHREIBWEISE, Themenplan, Evidenzkarte
                 · prüft Quellen über PubMed
                 · schreibt content/artikel/<slug>.md samt bild_suche und bild_alt
                 · baut, pflegt den Themenplan, committet, pusht
                 · schickt Marvin Beitrag und Patch (Sicherheitsnetz)
                          │
                          ▼  der Push löst aus:
GitHub Actions  .github/workflows/deploy.yml
                 1. holt fehlende Bilder  (werkzeuge/hole_bilder.py)
                 2. schreibt sie ins Repo zurück
                 3. baut die Seiten       (werkzeuge/baue_wissen.py)
                 4. deployt nach Cloudflare
                 5. prüft, ob die Seite mit 200 antwortet
                          │
                          ▼
Mo 08:00        Sichtbarkeitsmessung  (lokal, geplante Aufgabe dvgp-sichtbarkeit)
```

**Die Regel dahinter:** Alles, was ohne Marvins Rechner laufen muss, läuft in der Cloud
oder in Actions. Auf dem Rechner bleibt nur, was dort bleiben muss — die
Sichtbarkeitsmessung, weil ihr Messwerkzeug ein lokaler MCP-Server ist.

| Was | Wo | Warum dort |
|---|---|---|
| Beitrag schreiben | Cloud-Routine | braucht ein Modell, keinen Rechner |
| Bilder beschaffen | GitHub Actions | muss laufen, auch wenn der Laptop zu ist |
| Seiten bauen, deployen | GitHub Actions | dito |
| Sichtbarkeit messen | lokal, Mo 08:00 | Messwerkzeug ist ein lokaler MCP-Server |

Die Cloud-Routine **kann keine Bilder ziehen** — Stockfoto-Suche und Geotaggen sind
lokale Werkzeuge, die sie nicht erreicht. Deshalb die Arbeitsteilung: **Sie entscheidet
das Motiv, Actions besorgt es.** Die Routine schreibt `bild_suche` (englischer
Suchbegriff) und `bild_alt` (deutscher Alternativtext) ins Frontmatter, den Rest macht
[werkzeuge/hole_bilder.py](werkzeuge/hole_bilder.py) beim nächsten Push.

Was die Automatik braucht, steht als Repo-Secret hinterlegt:

| Secret | Wofür |
|---|---|
| `CLOUDFLARE_API_TOKEN` | `wrangler deploy` |
| `UNSPLASH_API_KEY` | Bildersuche |

---

## Aufbau

```
dvgp-website/
├── wrangler.toml            # Cloudflare-Config — liegt NEBEN site/, nie darin
├── content-engine.json      # Projektvertrag: Takt, Pfade, Bilder, Tracking
├── content/                 # Quellen, nicht veröffentlicht
│   ├── artikel/             # die Beiträge als Markdown
│   ├── SCHREIBWEISE.md      # verbindliche Ton- und Sprachregeln
│   ├── themenplan.md        # was wann erscheint
│   ├── evidenz.md           # Beleg-Landkarte, nach Thesen geordnet
│   └── bilder-roh/          # Originale, per .gitignore ausgeschlossen
├── site/                    # das einzige, was veröffentlicht wird
├── tracking/                # Sichtbarkeit über die Zeit
├── werkzeuge/               # Generator, Bildbeschaffung, Auswertung
└── .github/workflows/       # Bilder holen, bauen, deployen
```

Layout und CSS-System stammen aus `webpage-landlord-blueprint`
(`templates/site/_css.css.j2`), angepasst auf die Verbandsfarben Schwarz-Rot-Gold.

## Inhaltliche Struktur der Startseite

Der Aufbau folgt „Start with Why":

| Abschnitt | Inhalt |
|---|---|
| Hero | Kernaussage: Gesundheit ist kein Zufall, sondern eine Fähigkeit |
| `#warum` | Systemkritik — vier Prämissen, die nicht stimmen |
| `#verstaendnis` | Definition von Gesundheit + Ja/Nein-Abgrenzung + vier Dimensionen |
| `#auftrag` | Verstehen · Befähigen · Begleiten |
| `#prinzip` | S.T.A.R.K. als Zusammenfassung — bewusst erst am Ende |
| `#fuer-wen` | Zielgruppen |
| `#kontakt` | Vertretungsberechtigter Vorstand, E-Mail, Telefon, Sitz |

Fachbegriffe (Robustheit, Restitution, Erholungsfähigkeit) kommen bewusst **nicht** in der
Übersicht vor, sondern erst im Prinzip-Abschnitt.

## Rubrik „Wissen"

Beiträge liegen als Markdown in `content/artikel/`. Das Frontmatter hat sechs Felder:

| Feld | |
|---|---|
| `titel` | die Titelfrage |
| `beschreibung` | ein bis zwei Sätze, beantworten die Frage bereits |
| `datum` | `JJJJ-MM-TT` |
| `cluster` | Kategorie aus dem Themenplan |
| `slug` | Dateiname ohne `.md` |
| `bild_suche` | **englischer** Suchbegriff für die Stockfoto-Suche |
| `bild_alt` | **deutscher** Alternativtext zum Bild |

Der Generator baut daraus die HTML-Seiten und zieht Sitemap und `llms.txt` nach:

```bash
python3 werkzeuge/baue_wissen.py
```

Erzeugte Dateien unter `site/wissen/` werden **mit eingecheckt**. Fehlt zu einem Beitrag
das Bild, baut er trotzdem sauber — er sieht nur ärmer aus, bis Actions es nachholt.

Themen und Suchvolumen: [content/themenplan.md](content/themenplan.md).
Tonalität: [content/SCHREIBWEISE.md](content/SCHREIBWEISE.md).

## Bilder

Ein Aufmacher je Beitrag, dasselbe Bild als Vorschau in der Übersicht und beim Teilen.
Die Kette — die Reihenfolge ist nicht verhandelbar:

1. **Suchen** über die Unsplash-API mit `bild_suche`
2. **Download registrieren** — Lizenzpflicht, nicht überspringbar
3. **Original** nach `content/bilder-roh/` (bleibt aus dem Repo, mehrere MB je Datei)
4. **Rechnen** auf 1200 px als WebP *und* JPG nach `site/bilder/<slug>.{webp,jpg}`
5. **Beschriften** — Ort, Bildunterschrift, Stichworte, Lizenzangabe in die Dateien
6. **Impressum** — Fotograf ergänzen

Schritt 5 muss **nach** Schritt 4 laufen. Das Rechnen schreibt die Pixel neu und wirft
jede Metadatenspur weg; umgekehrt wäre die Arbeit sofort wieder verloren.

Geotaggt wird auf **Magdeburg**, den Vereinssitz. Die Koordinate steht nicht für den Ort
der Aufnahme, sondern für den Herausgeber. Die Werte stehen im Block `bilder` in
[content-engine.json](content-engine.json).

Der Bildnachweis steht im [Impressum](site/impressum.html) — dort ist die maßgebliche
Liste. Zusätzlich trägt jede Datei Urheber und Quelle in ihren Metadaten.

## Sichtbarkeit

Wo die Seite bei Google steht, gemessen über die Zeit: [tracking/](tracking/).
Das MCP misst, das Repo führt die Akte. Details in
[tracking/README.md](tracking/README.md).

## Deployment

**Ein Push auf `main` deployt.** Über GitHub Actions, siehe
[.github/workflows/deploy.yml](.github/workflows/deploy.yml).

Von Hand geht es weiterhin:

```bash
npx wrangler deploy
```

Cloudflare Workers Builds wird **bewusst nicht** benutzt — Begründung und Vorgeschichte
in [DEPLOYMENT.md](DEPLOYMENT.md).

Die Custom Domains `dvgp.info` und `www.dvgp.info` stehen als `custom_domain`-Routen in
`wrangler.toml`; Cloudflare legt die DNS-Einträge beim Deploy selbst an.

## Lokal ansehen

```bash
python3 -m http.server 8000 --directory site
```

Saubere URLs (`/wissen/foo` statt `/wissen/foo.html`) macht nur der Worker — lokal die
`.html` mit aufrufen.

## SEO und KI-Sichtbarkeit — Stand

Geprüft gegen `webpage-landlord-blueprint/meta/KI-SICHTBARKEIT.md` und `tools/site-tests.md`.

| Punkt | Stand |
|---|---|
| `sitemap.xml` | ✅ generiert, saubere URLs |
| `llms.txt` | ✅ Betreiber, Gegenstand, alle Beiträge |
| `robots.txt` mit Sitemap-Verweis | ✅ |
| JSON-LD Startseite | ✅ `NGO`, `WebSite`, `FAQPage` |
| JSON-LD Beiträge | ✅ `Article` inkl. `image`, `BreadcrumbList`, `FAQPage` |
| FAQ-Block und Schema aus einer Quelle | ✅ beide aus dem Markdown |
| Überschriften als echte Nutzerfragen | ✅ Vorgabe in SCHREIBWEISE.md |
| Antwort im ersten Satz | ✅ Vorgabe in SCHREIBWEISE.md |
| Canonical je Seite | ✅ |
| 404-Seite | ✅ `site/404.html`, als einzige mit `noindex` |
| WebP mit JPG-Rückfall | ✅ `<picture>` und `image-set()` |
| Eigenes `og:image` je Beitrag | ✅ |
| Bildmaße im HTML | ✅ gegen Layoutsprünge |
| Externe Belege (DOI) in Beiträgen | ✅ über PubMed |
| Google Search Console | ✅ verifiziert |
| Positionsverfolgung über die Zeit | ✅ `tracking/` |
| **Bing Webmaster Tools** | ❌ offen |
| **Google-Unternehmensprofil** | ❌ offen |
| **Verzeichniseinträge, NAP-Konsistenz** | ❌ offen |

Die drei offenen Punkte brauchen einen Menschen — Verifizierung und Verzeichniseinträge
lassen sich nicht generieren.
