# dvgp-website

Website des **DVGP — Deutscher Verband für Gesundheitsförderung und Prävention**.
Statische Site, ausgeliefert als **Cloudflare Worker mit Static Assets**. Live unter
**https://dvgp.info**

> **Wer hier neu einsteigt — auch als KI — liest zuerst [HANDOFF.md](HANDOFF.md).**
> Dort steht der aktuelle Stand, die getroffenen Entscheidungen samt Begründung und die
> Fallstricke. Die Änderungshistorie führt [WORKLOG.md](WORKLOG.md).

## Aufbau

```
dvgp-website/
├── wrangler.toml        # Cloudflare-Config — liegt NEBEN site/, nie darin
├── site/                # das einzige, was veröffentlicht wird
│   ├── index.html       # Startseite
│   ├── impressum.html
│   ├── style.css
│   ├── robots.txt
│   ├── sitemap.xml
│   └── bilder/
└── logo-quellen/        # Logo-Master (nicht veröffentlicht)
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
| `#framework` | S.T.A.R.K. als Zusammenfassung — bewusst erst am Ende |
| `#fuer-wen` | Zielgruppen |
| `#kontakt` | Vorstand, E-Mail, Telefon, Sitz |

Fachbegriffe (Robustheit, Restitution, Erholungsfähigkeit) kommen bewusst **nicht** in der
Übersicht vor, sondern erst im Framework-Abschnitt.

## Lokal ansehen

```bash
python3 -m http.server 8000 --directory site
```

## Deployment

Cloudflare Workers Builds deployt automatisch bei jedem Push auf `main`.

Einrichtung Schritt für Schritt inklusive DNS-Umzug: siehe **[DEPLOYMENT.md](DEPLOYMENT.md)**.

- Repo: `marvinstiebler/dvgp-website`
- Bereitstellungsbefehl: `npx wrangler deploy`
- Stammverzeichnis: `/`
- Produktions-Branch: `main`

Die Custom Domains `dvgp.info` und `www.dvgp.info` stehen als `custom_domain`-Routen in
`wrangler.toml` — Cloudflare legt die DNS-Einträge beim Deploy selbst an. Voraussetzung ist,
dass die Zone `dvgp.info` zu diesem Zeitpunkt bereits im Cloudflare-Konto aktiv ist.

Manuelles Deployment:

```bash
npx wrangler deploy
```

## Bildnachweise

Fotos von Victor Freitas, John Arano und Centre for Ageing Better auf Unsplash.

## Rubrik „Wissen"

Beiträge liegen als Markdown in `content/artikel/` (Frontmatter: `titel`,
`beschreibung`, `datum`, optional `cluster` und `slug`). Der Generator baut daraus
die HTML-Seiten und zieht Sitemap und `llms.txt` nach:

```bash
python3 werkzeuge/baue_wissen.py
```

Erzeugte Dateien unter `site/wissen/` werden **mit eingecheckt** — Cloudflare Workers
Builds führt nur `wrangler deploy` aus und baut nichts.

Themen und Suchvolumen: `content/themenplan.md`.
Tonalität: `content/SCHREIBWEISE.md`.

## SEO und KI-Sichtbarkeit — Stand

Geprüft gegen `webpage-landlord-blueprint/meta/KI-SICHTBARKEIT.md` und `tools/site-tests.md`.

| Punkt | Stand |
|---|---|
| `sitemap.xml` | ✅ generiert, saubere URLs |
| `llms.txt` | ✅ Betreiber, Gegenstand, alle Beiträge |
| `robots.txt` mit Sitemap-Verweis | ✅ |
| JSON-LD Startseite | ✅ `NGO`, `WebSite`, `FAQPage` |
| JSON-LD Beiträge | ✅ `Article`, `BreadcrumbList`, `FAQPage` |
| FAQ-Block und Schema aus einer Quelle | ✅ beide aus dem Markdown |
| Überschriften als echte Nutzerfragen | ✅ Vorgabe in SCHREIBWEISE.md |
| Antwort im ersten Satz | ✅ Vorgabe in SCHREIBWEISE.md |
| Canonical je Seite | ✅ |
| 404-Seite | ✅ `site/404.html` |
| WebP mit JPG-Rückfall | ✅ `<picture>` und `image-set()` |
| Bildmaße im HTML | ✅ gegen Layoutsprünge |
| Externe Belege (DOI) in Beiträgen | ✅ über PubMed |
| **Search Console + Bing** | ❌ erst nach dem Umzug auf dvgp.info |
| **Google-Unternehmensprofil** | ❌ offen, siehe unten |
| **Verzeichniseinträge, NAP-Konsistenz** | ❌ offen |

Die drei offenen Punkte brauchen die eigene Domain und einen Menschen — Verifizierung
und Verzeichniseinträge lassen sich nicht generieren.
