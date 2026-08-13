# Worklog

Append-only history. Newest entries on top. Never edit past entries.

<!-- newest entries first -->

## 2026-08-12 07:17 CEST — Claude (Sitzung)
**What:** Ein Rot (#B00000) statt drei Toenen, alle elf Kacheln auf ein Format mit Bild oben, Vorstand ueberall als vertretungsberechtigt ausgewiesen.
**Where:** site/index.html, site/style.css, site/impressum.html, site/404.html, werkzeuge/baue_wissen.py
**Why:** Buttons und Ueberschriften hatten unterschiedliche Rottoene, und die drei Kachelgruppen drei verschiedene Formate. Den Dimensions-Kacheln fehlte Rot ganz.

## 2026-08-11 21:29 CEST — Claude (Sitzung)
**What:** Bilder hinter die vier Dimensionen und den Uebergangsblock gelegt, Menue-Knopf von Systemblau auf Schwarz.
**Where:** site/style.css, site/index.html, site/bilder/
**Why:** Die Startseite war auf dem Telefon zu weiss-auf-weiss. Bei <button> ohne color-Angabe zeichnet iOS die Systemfarbe, deshalb war das Menue blau.

## 2026-08-11 21:29 CEST — Claude (Sitzung)
**What:** DNS-Ausfall behoben: dvgp.info war mehrere Stunden komplett offline, Website und Mail.
**Where:** Cloudflare-Zone, Nameserver bei IONOS
**Why:** Die Zone war versehentlich als dvpg.info angelegt worden, mit vertauschtem p und g. Deren Nameserver landeten bei IONOS fuer die richtige Domain, die damit auf Nameserver zeigte, die keine Zone fuer sie hatten. Diagnose ueber dig gegen Registry und autoritative Server.
**Next:** Vor jeder DNS-Aenderung MX pruefen. Diagnosebefehle stehen in DEPLOYMENT.md.

## 2026-08-11 21:29 CEST — Claude (Sitzung)
**What:** Seite von Grund auf gebaut und unter dvgp.info live gestellt: Startseite, Rubrik Wissen mit Generator und drei Beiträgen, Publikationsseite mit 33 Arbeiten, Impressum mit Registerangaben. Dazu Themenplan, Beleg-Landkarte und das Modell des Vorstands schriftlich festgehalten sowie eine Cloud-Routine eingerichtet, die Mo und Do automatisch einen Beitrag schreibt.
**Where:** site/, content/, werkzeuge/, wrangler.toml, DEPLOYMENT.md, HANDOFF.md
**Why:** Der Verband braucht eine Seite, die seinen Gesundheitsbegriff erklaert und konkrete Fragen belegt beantwortet. Statisch statt Framework, weil es einfach bleiben und ohne Build-Schritt ausgeliefert werden soll.
**Next:** Am 13.08. frueh pruefen, ob der erste automatische Beitrag sauber durchgelaufen ist.
