# Deployment — dvgp.info

**Stand: 11.08.2026 — die Seite ist live unter https://dvgp.info**

## Wie es läuft

| | |
|---|---|
| Worker | `dvgp-website` im Cloudflare-Konto `marvin.stiebler@gmail.com` |
| Domains | `dvgp.info` und `www.dvgp.info` als Custom Domains am Worker |
| Ausweichadresse | https://dvgp-website.marvin-stiebler.workers.dev |
| Nameserver | `norm.ns.cloudflare.com`, `rosalie.ns.cloudflare.com` |
| Registrar | IONOS (nur noch Registrierung, DNS liegt bei Cloudflare) |
| Mail | weiterhin IONOS: `mx00.ionos.de`, `mx01.ionos.de` |

Deployment über `npx wrangler deploy` oder automatisch über Cloudflare Workers Builds
bei Push auf `main`. Die Custom Domains stehen in `wrangler.toml` — Cloudflare legt die
DNS-Einträge dafür selbst an.

## Was beim Umzug schiefging — zum Nachlesen

Zwei Fehler, beide mit derselben Ursache: eine vertauschte Buchstabenfolge.

1. **Die Zone wurde als `dvpg.info` angelegt** statt `dvgp.info` (`p` und `g`
   vertauscht). Diese Domain gehört jemand anderem. Cloudflare nannte für die falsche
   Zone die Nameserver `elma`/`rocco`, die dann bei IONOS für die *richtige* Domain
   eingetragen wurden.

2. **Folge: `dvgp.info` war mehrere Stunden vollständig offline** — Website und Mail.
   Die Domain zeigte auf Cloudflare-Nameserver, die für sie keine Zone hatten. Die
   Direktabfrage lieferte `REFUSED`, öffentliche Resolver lieferten gar nichts mehr.

**Diagnose, falls so etwas wiederkommt:**

```bash
# Wen führt die Registry als zuständig?
dig +norecurse @a0.info.afilias-nst.info dvgp.info NS

# Antwortet dieser Nameserver für die Domain überhaupt?
dig @rosalie.ns.cloudflare.com dvgp.info SOA
# REFUSED = Zone existiert dort nicht. NOERROR = alles gut.

# Was sehen echte Nutzer?
dig @8.8.8.8 dvgp.info MX
```

**Lehre:** Nach dem Anlegen einer Zone immer den Domainnamen Zeichen für Zeichen
prüfen, bevor die Nameserver beim Registrar geändert werden. Und die Nameserver nehmen,
die Cloudflare *für diese Zone* nennt — sie unterscheiden sich je Zone.

## Verifikation nach Änderungen

```bash
dig @8.8.8.8 dvgp.info NS      # norm + rosalie
dig @8.8.8.8 dvgp.info MX      # mx00 + mx01 bei ionos -- sonst steht die Mail
curl -sI https://dvgp.info | head -3
```

Vollständiger Durchlauf über alle Seiten:

```bash
for p in "" wissen/ publikationen/ impressum sitemap.xml llms.txt robots.txt; do
  printf "%-30s %s\n" "/$p" "$(curl -s -o /dev/null -w '%{http_code}' https://dvgp.info/$p)"
done
```

## Weiterleitungen

Beide aktiv und geprüft (11.08.2026):

- **HTTPS erzwungen** über *SSL/TLS → Edge Certificates → Always Use HTTPS*.
- **`www` auf die Hauptdomain** über *Regeln → Weiterleitungsregeln*:

  | | |
  |---|---|
  | Bedingung | `http.host eq "www.dvgp.info"` |
  | Typ | Dynamisch |
  | Ausdruck | `concat("https://dvgp.info", http.request.uri.path)` |
  | Status | 301 |
  | Abfragezeichenfolge | beibehalten |

  Dynamisch statt statisch ist entscheidend — sonst landet jeder `www`-Aufruf auf der
  Startseite statt auf der angeforderten Unterseite.

Jede Kombination löst in genau einem Sprung auf: `http://`, `www.`, beides zusammen,
mit und ohne Abfragezeichenfolge.

## Suchmaschinen

- **Google Search Console:** Domain-Property über TXT-Eintrag bestätigt, Sitemap
  `https://dvgp.info/sitemap.xml` eingereicht.
- **Bing Webmaster Tools:** noch offen. Lässt sich per Import aus der Search Console
  anlegen.

## Offen

- Bing Webmaster Tools anmelden.
- Verzeichniseinträge und ein Google-Unternehmensprofil — beides zahlt auf die
  Erkennbarkeit als Entität ein, siehe `webpage-landlord-blueprint/meta/KI-SICHTBARKEIT.md`.
