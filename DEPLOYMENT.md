# Deployment — dvgp.info auf Cloudflare

Ausgangslage (Stand 10.08.2026, per `dig` geprüft):

| | |
|---|---|
| Registrar / DNS | **IONOS** (`ns1060.ui-dns.com` u. a.) |
| Website aktuell | IONOS-Parkseite (`217.160.0.228`) |
| **E-Mail** | **aktiv über IONOS** (`mx00.ionos.de`, `mx01.ionos.de`) |
| SPF | `v=spf1 include:_spf-eu.ionos.com ~all` |

> **Der kritische Punkt: die E-Mail.**
> `kontakt@dvgp.info` läuft über IONOS. Wechseln die Nameserver zu Cloudflare, gilt ab
> diesem Moment ausschließlich die Cloudflare-Zone. Fehlen dort die MX- und SPF-Einträge,
> kommt **keine Mail mehr an**. Schritt 2 unten ist deshalb keine Formalie.

---

## Schritt 1 — Domain in Cloudflare aufnehmen

Dashboard → **Add a domain** → `dvgp.info` → Plan **Free**.

Cloudflare scannt die bestehende IONOS-Zone und übernimmt die gefundenen Einträge
automatisch. Danach zeigt es **zwei Nameserver** an, etwa in der Form:

```
xxxx.ns.cloudflare.com
yyyy.ns.cloudflare.com
```

Diese beiden Namen werden in Schritt 3 gebraucht. Sie werden pro Konto zufällig
vergeben — sie stehen erst fest, wenn die Domain angelegt ist.

## Schritt 2 — DNS-Einträge in Cloudflare prüfen (vor der Umstellung!)

Cloudflare → `dvgp.info` → **DNS → Records**. Diese Einträge müssen vorhanden sein,
sonst bricht der Mailempfang ab:

| Typ | Name | Ziel | Prio | Proxy |
|---|---|---|---|---|
| MX | `dvgp.info` (bzw. `@`) | `mx00.ionos.de` | 10 | — |
| MX | `dvgp.info` (bzw. `@`) | `mx01.ionos.de` | 10 | — |
| TXT | `dvgp.info` (bzw. `@`) | `v=spf1 include:_spf-eu.ionos.com ~all` | — | — |

Fehlt etwas, von Hand nachtragen. MX- und TXT-Einträge sind nie „proxied" (keine
orangene Wolke) — das gilt nur für Web-Traffic.

Den alten **A-Eintrag auf `217.160.0.228`** (die IONOS-Parkseite) löschen oder ignorieren;
er wird in Schritt 5 ohnehin vom Worker-Eintrag ersetzt.

Falls IONOS zusätzlich DKIM/Autodiscover-Einträge hat, sollten diese mit übernommen sein —
im Zweifel im IONOS-Kundenkonto unter *Domains & SSL → dvgp.info → DNS* gegenprüfen und
Eintrag für Eintrag abgleichen. **Das ist der beste Zeitpunkt dafür — vor Schritt 3.**

## Schritt 3 — Nameserver bei IONOS umstellen

**Das ist der einzige Schritt beim Domain-Provider.**

IONOS-Kundenkonto → **Domains & SSL** → `dvgp.info` → **Nameserver** →
*Eigene Nameserver verwenden* → die vier IONOS-Einträge durch die **zwei
Cloudflare-Nameserver aus Schritt 1** ersetzen:

```
xxxx.ns.cloudflare.com
yyyy.ns.cloudflare.com
```

Keine A-, CNAME- oder sonstigen Records bei IONOS anlegen — ab hier verwaltet
Cloudflare die komplette Zone.

Die Übernahme dauert meist 1–4 Stunden, im Extremfall bis 24 Stunden. Cloudflare
schickt eine Mail, sobald die Zone **Active** ist.

## Schritt 4 — Repo mit Cloudflare verbinden

Dashboard → **Workers & Pages** → **Create** → **Workers** → **Connect to Git**

| Feld | Wert |
|---|---|
| Repository | `marvinstiebler/dvgp-website` |
| Produktions-Branch | `main` |
| Bereitstellungsbefehl | `npx wrangler deploy` |
| Stammverzeichnis | `/` |

Der Worker heißt laut `wrangler.toml` **`dvgp-website`**.

## Schritt 5 — Custom Domain

Passiert **automatisch**. In `wrangler.toml` stehen bereits:

```toml
[[routes]]
pattern = "dvgp.info"
custom_domain = true

[[routes]]
pattern = "www.dvgp.info"
custom_domain = true
```

Beim ersten Deploy legt Cloudflare die zugehörigen DNS-Einträge selbst an und stellt
das Zertifikat aus. **Von Hand ist hier nichts einzutragen.**

Wichtig ist nur die Reihenfolge: Schritt 4 erst starten, wenn die Zone in Cloudflare
**Active** ist. Läuft der Deploy vorher, bricht er mit einer Zone-Fehlermeldung ab —
dann nach der Aktivierung im Dashboard einfach *Retry deployment* klicken.

---

## Verifikation

```bash
# Zeigt die Domain auf Cloudflare?
dig +short NS dvgp.info

# Läuft die Site?
curl -sI https://dvgp.info | head -3

# Kommt Mail noch an? (MX müssen weiter auf IONOS zeigen)
dig +short MX dvgp.info
```

Erwartet: NS auf `*.ns.cloudflare.com`, HTTP 200 auf der Site, MX weiterhin `mx00/mx01.ionos.de`.
Danach zur Sicherheit eine Testmail an `kontakt@dvgp.info` schicken.

---

## Alternative: manuelles Deployment ohne Git-Anbindung

```bash
cd ~/projects/dvgp-website
npx wrangler login      # einmalig, öffnet den Browser
npx wrangler deploy
```

Das Ergebnis ist identisch. Die Git-Anbindung aus Schritt 4 hat nur den Vorteil,
dass jeder Push automatisch deployt.
