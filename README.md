# dvgp-website

Website des **DVGP — Deutscher Verband für Gesundheitsförderung und Prävention**.
Statische Site, ausgeliefert als **Cloudflare Worker mit Static Assets**.

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
