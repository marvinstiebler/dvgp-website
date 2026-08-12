#!/usr/bin/env python3
"""Baut aus den Markdown-Beiträgen in content/artikel/ die Rubrik "Wissen".

    python3 werkzeuge/baue_wissen.py

Erzeugt site/wissen/index.html und je Beitrag site/wissen/<slug>.html, trägt die
neuen Seiten in sitemap.xml und llms.txt nach und lässt alles andere in Ruhe.

Bewusst ohne fremde Pakete: die Seite wird über Cloudflare Workers Builds
ausgeliefert, dort läuft nur `wrangler deploy`. Der Generator läuft lokal, sein
Ergebnis wird eingecheckt. Eine Abhängigkeit weniger ist eine Fehlerquelle
weniger.

Markdown-Umfang: Überschriften (##, ###), Absätze, Listen (-, 1.), Zitate (>),
Tabellen (|), **fett**, *kursiv*, [Text](Ziel). Mehr braucht die Content-Engine
nicht, und mehr wird hier absichtlich nicht unterstützt -- unbekannte Syntax
soll auffallen statt still falsch gerendert zu werden.
"""

from __future__ import annotations

import html
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
ARTIKEL_VERZ = WURZEL / "content" / "artikel"
SITE = WURZEL / "site"
WISSEN = SITE / "wissen"
BASIS_URL = "https://dvgp.info"

PFLICHTFELDER = ("titel", "beschreibung", "datum")


# --------------------------------------------------------------------------
# Einlesen
# --------------------------------------------------------------------------

@dataclass
class Beitrag:
    slug: str
    titel: str
    beschreibung: str
    datum: str
    cluster: str = "Allgemein"
    quelle: Path | None = None
    koerper: str = ""
    abschnitte: list[tuple[str, str]] = field(default_factory=list)

    @property
    def url(self) -> str:
        return f"{BASIS_URL}/wissen/{self.slug}"

    @property
    def datum_lesbar(self) -> str:
        j, m, t = self.datum.split("-")
        return f"{t}.{m}.{j}"

    @property
    def lesezeit(self) -> int:
        woerter = len(self.koerper.split())
        return max(1, round(woerter / 200))


def lies_frontmatter(text: str, pfad: Path, pflicht: tuple[str, ...] = PFLICHTFELDER) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        raise SystemExit(f"{pfad.name}: Frontmatter fehlt (Datei muss mit '---' beginnen).")
    _, kopf, rest = text.split("---", 2)
    daten: dict[str, str] = {}
    for zeile in kopf.strip().splitlines():
        if not zeile.strip():
            continue
        if ":" not in zeile:
            raise SystemExit(f"{pfad.name}: Zeile ohne Doppelpunkt im Frontmatter: {zeile!r}")
        schluessel, wert = zeile.split(":", 1)
        daten[schluessel.strip()] = wert.strip().strip('"')
    fehlend = [f for f in pflicht if f not in daten]
    if fehlend:
        raise SystemExit(f"{pfad.name}: Pflichtfelder fehlen: {', '.join(fehlend)}")
    if "datum" in daten and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", daten["datum"]):
        raise SystemExit(f"{pfad.name}: datum muss JJJJ-MM-TT sein, ist {daten['datum']!r}.")
    return daten, rest.lstrip("\n")


def lies_beitraege() -> list[Beitrag]:
    beitraege = []
    for pfad in sorted(ARTIKEL_VERZ.glob("*.md")):
        daten, koerper = lies_frontmatter(pfad.read_text(encoding="utf-8"), pfad)
        beitrag = Beitrag(
            slug=daten.get("slug") or pfad.stem,
            titel=daten["titel"],
            beschreibung=daten["beschreibung"],
            datum=daten["datum"],
            cluster=daten.get("cluster", "Allgemein"),
            quelle=pfad,
            koerper=koerper,
        )
        beitraege.append(beitrag)
    # neueste zuerst
    beitraege.sort(key=lambda b: b.datum, reverse=True)
    return beitraege


# --------------------------------------------------------------------------
# Markdown -> HTML
# --------------------------------------------------------------------------

def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def tabelle(zeilen: list[str]) -> str:
    kopf = [z.strip() for z in zeilen[0].strip("|").split("|")]
    rumpf = []
    for zeile in zeilen[2:]:
        rumpf.append([z.strip() for z in zeile.strip("|").split("|")])
    teile = ['<div class="tabelle-wrap"><table>', "<thead><tr>"]
    teile += [f"<th>{inline(z)}</th>" for z in kopf]
    teile.append("</tr></thead><tbody>")
    for reihe in rumpf:
        teile.append("<tr>" + "".join(f"<td>{inline(z)}</td>" for z in reihe) + "</tr>")
    teile.append("</tbody></table></div>")
    return "".join(teile)


def markdown_zu_html(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Gibt HTML und die Liste der (Überschrift, Antwortabsatz)-Paare zurück.

    Das zweite Rückgabestück speist das FAQPage-Schema: jede ##-Überschrift ist
    eine Frage, der erste Absatz darunter die Antwort.
    """
    ausgabe: list[str] = []
    abschnitte: list[tuple[str, str]] = []
    letzte_frage: str | None = None

    zeilen = text.splitlines()
    i = 0
    while i < len(zeilen):
        zeile = zeilen[i]
        strip = zeile.strip()

        if not strip:
            i += 1
            continue

        if strip.startswith("### "):
            ausgabe.append(f"<h3>{inline(strip[4:])}</h3>")
            i += 1
            continue

        if strip.startswith("## "):
            ueberschrift = strip[3:].strip()
            # Nur echte Fragen wandern ins FAQ-Schema. Überschriften wie
            # "Einordnung im STARK-Prinzip" sind keine und hätten dort nichts
            # verloren -- Google wertet fragefremde Einträge als Missbrauch.
            letzte_frage = ueberschrift if ueberschrift.endswith("?") else None
            ausgabe.append(f"<h2>{inline(ueberschrift)}</h2>")
            i += 1
            continue

        if strip.startswith("> "):
            block = []
            while i < len(zeilen) and zeilen[i].strip().startswith("> "):
                block.append(zeilen[i].strip()[2:])
                i += 1
            ausgabe.append(f'<blockquote>{inline(" ".join(block))}</blockquote>')
            continue

        if strip.startswith("|"):
            block = []
            while i < len(zeilen) and zeilen[i].strip().startswith("|"):
                block.append(zeilen[i].strip())
                i += 1
            if len(block) >= 2:
                ausgabe.append(tabelle(block))
            continue

        if re.match(r"^[-*] ", strip):
            block = []
            while i < len(zeilen) and re.match(r"^[-*] ", zeilen[i].strip()):
                block.append(zeilen[i].strip()[2:])
                i += 1
            punkte = "".join(f"<li>{inline(p)}</li>" for p in block)
            ausgabe.append(f"<ul>{punkte}</ul>")
            continue

        if re.match(r"^\d+\. ", strip):
            block = []
            while i < len(zeilen) and re.match(r"^\d+\. ", zeilen[i].strip()):
                block.append(re.sub(r"^\d+\. ", "", zeilen[i].strip()))
                i += 1
            punkte = "".join(f"<li>{inline(p)}</li>" for p in block)
            ausgabe.append(f"<ol>{punkte}</ol>")
            continue

        # Absatz
        block = []
        while i < len(zeilen) and zeilen[i].strip() and not re.match(
            r"^(#{2,3} |> |\||[-*] |\d+\. )", zeilen[i].strip()
        ):
            block.append(zeilen[i].strip())
            i += 1
        absatz = " ".join(block)
        ausgabe.append(f"<p>{inline(absatz)}</p>")
        if letzte_frage:
            abschnitte.append((letzte_frage, absatz))
            letzte_frage = None

    return "\n".join(ausgabe), abschnitte


# --------------------------------------------------------------------------
# Seitenrahmen
# --------------------------------------------------------------------------

def kopf_seite(titel: str, beschreibung: str, kanonisch: str, extra: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(titel)}</title>
<meta name="description" content="{html.escape(beschreibung)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{kanonisch}">
<meta property="og:type" content="article">
<meta property="og:locale" content="de_DE">
<meta property="og:url" content="{kanonisch}">
<meta property="og:title" content="{html.escape(titel)}">
<meta property="og:description" content="{html.escape(beschreibung)}">
<meta property="og:image" content="{BASIS_URL}/bilder/wissen.jpg">
<meta property="og:site_name" content="DVGP">
<meta name="theme-color" content="#0f1419">
<link rel="icon" type="image/png" href="/bilder/logo-dvgp.png">
<link rel="stylesheet" href="/style.css">
{extra}</head>
<body>

<div class="topbar">
 <div class="container">
  <span class="flagge auf-dunkel" role="img" aria-label="Deutschland"></span>
  <span>Deutscher Verband für Gesundheitsförderung und Prävention · <a href="mailto:kontakt@dvgp.info">kontakt@dvgp.info</a></span>
 </div>
</div>

<header class="header">
 <div class="container header-inner">
  <a href="/" class="logo" aria-label="DVGP — Startseite">
   <img src="/bilder/logo-dvgp-beschnitten.png" alt="DVGP — Deutscher Verband für Gesundheitsförderung und Prävention" width="312" height="174">
  </a>
  <nav id="nav">
   <ul>
    <li><a href="/#warum">Warum</a></li>
    <li><a href="/#verstaendnis">Gesundheit</a></li>
    <li><a href="/#auftrag">Auftrag</a></li>
    <li><a href="/#prinzip">STARK-Prinzip</a></li>
    <li><a href="/wissen/">Wissen</a></li>
    <li><a href="/publikationen/">Publikationen</a></li>
    <li><a href="/#kontakt">Kontakt</a></li>
   </ul>
  </nav>
  <a href="/#kontakt" class="header-cta">Kontakt aufnehmen</a>
  <button class="menu-toggle" onclick="document.getElementById('nav').classList.toggle('open')" aria-label="Menü öffnen">☰</button>
 </div>
</header>
"""


FUSS = """
<footer>
 <div class="container footer-grid">
  <div>
   <img class="footer-logo" src="/bilder/logo-dvgp-voll-beschnitten.png" alt="Deutscher Verband für Gesundheitsförderung und Prävention">
   <p class="footer-text">
    Wir denken Gesundheit als System — und geben Menschen die Werkzeuge, sie selbst
    zu gestalten.
   </p>
   <a class="footer-mail" href="mailto:kontakt@dvgp.info">kontakt@dvgp.info</a>
   <p class="footer-ort">Vertretungsberechtigter Vorstand: Marvin Stiebler · 39130 Magdeburg</p>
  </div>
  <div>
   <h4>Inhalt</h4>
   <ul>
    <li><a href="/#warum">Wofür wir stehen</a></li>
    <li><a href="/#verstaendnis">Unser Gesundheitsbegriff</a></li>
    <li><a href="/#auftrag">Was wir tun</a></li>
    <li><a href="/#prinzip">Das STARK-Prinzip</a></li>
   </ul>
  </div>
  <div>
   <h4>Verband</h4>
   <ul>
    <li><a href="/wissen/">Wissen</a></li>
    <li><a href="/publikationen/">Publikationen</a></li>
    <li><a href="/#fuer-wen">Für wen wir da sind</a></li>
    <li><a href="/#kontakt">Kontakt</a></li>
    <li><a href="/impressum">Impressum</a></li>
   </ul>
  </div>
 </div>
 <div class="container">
  <div class="footer-bottom">
   © 2026 DVGP — Deutscher Verband für Gesundheitsförderung und Prävention · <a href="/impressum">Impressum</a>
  </div>
 </div>
</footer>

</body>
</html>
"""

HINWEIS = """
<aside class="hinweis">
 <strong>Wichtig:</strong> Der DVGP stellt keine Diagnosen und behandelt keine Krankheiten.
 Dieser Beitrag erklärt Zusammenhänge und ordnet ein — er ersetzt keine ärztliche
 Abklärung. Wer Beschwerden hat oder Medikamente nimmt, klärt Belastung vorher ärztlich ab.
</aside>
"""


def json_ld_artikel(b: Beitrag, abschnitte: list[tuple[str, str]]) -> str:
    import json

    graph = [
        {
            "@type": "Article",
            "@id": f"{b.url}#artikel",
            "headline": b.titel,
            "description": b.beschreibung,
            "datePublished": b.datum,
            "dateModified": b.datum,
            "inLanguage": "de-DE",
            "mainEntityOfPage": b.url,
            "author": {"@id": f"{BASIS_URL}/#organisation"},
            "publisher": {"@id": f"{BASIS_URL}/#organisation"},
        },
        {
            "@type": "NGO",
            "@id": f"{BASIS_URL}/#organisation",
            "name": "Deutscher Verband für Gesundheitsförderung und Prävention",
            "alternateName": "DVGP",
            "url": f"{BASIS_URL}/",
            "email": "kontakt@dvgp.info",
        },
    ]
    graph.append(
        {
            "@type": "BreadcrumbList",
            "@id": f"{b.url}#brotkrumen",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Startseite", "item": f"{BASIS_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Wissen", "item": f"{BASIS_URL}/wissen/"},
                {"@type": "ListItem", "position": 3, "name": b.titel, "item": b.url},
            ],
        }
    )
    if abschnitte:
        graph.append(
            {
                "@type": "FAQPage",
                "@id": f"{b.url}#faq",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": frage,
                        "acceptedAnswer": {"@type": "Answer", "text": antwort},
                    }
                    for frage, antwort in abschnitte
                ],
            }
        )
    daten = {"@context": "https://schema.org", "@graph": graph}
    return (
        '<script type="application/ld+json">\n'
        + json.dumps(daten, ensure_ascii=False, indent=1)
        + "\n</script>\n"
    )


def baue_beitrag(b: Beitrag) -> str:
    inhalt, abschnitte = markdown_zu_html(b.koerper)
    b.abschnitte = abschnitte
    seite = kopf_seite(f"{b.titel} — DVGP", b.beschreibung, b.url)
    seite += f"""
<main class="content-page">
 <a class="back-link" href="/wissen/">Zurück zur Übersicht</a>
 <span class="section-kicker">{html.escape(b.cluster)}</span>
 <h1>{inline(b.titel)}</h1>
 <p class="meta">{b.datum_lesbar} · {b.lesezeit} Min. Lesezeit · Deutscher Verband für Gesundheitsförderung und Prävention</p>

 <div class="beitrag">
{inhalt}
 </div>
{HINWEIS}
 <div class="beitrag-cta">
  <h2>Fragen dazu?</h2>
  <p>Wir antworten persönlich — formlos per E-Mail oder Telefon.</p>
  <a class="cta-primary" href="/#kontakt">Kontakt aufnehmen</a>
 </div>
</main>
"""
    seite += FUSS.rstrip() + "\n"
    seite = seite.replace("</body>", json_ld_artikel(b, abschnitte) + "</body>")
    return seite


def baue_uebersicht(beitraege: list[Beitrag]) -> str:
    url = f"{BASIS_URL}/wissen/"
    seite = kopf_seite(
        "Wissen — DVGP",
        "Beiträge des DVGP zu Gesundheit, Prävention, Krafttraining und gesundem Altern. "
        "Verständlich erklärt, ohne Verkaufsabsicht.",
        url,
    )
    if beitraege:
        karten = "\n".join(
            f"""  <a class="wissen-karte" href="/wissen/{b.slug}">
   <span class="wissen-cluster">{html.escape(b.cluster)}</span>
   <h2>{inline(b.titel)}</h2>
   <p>{inline(b.beschreibung)}</p>
   <span class="wissen-meta">{b.datum_lesbar} · {b.lesezeit} Min.</span>
  </a>"""
            for b in beitraege
        )
        liste = f'<div class="wissen-liste">\n{karten}\n </div>'
    else:
        liste = '<p class="lead">Die ersten Beiträge erscheinen in Kürze.</p>'

    seite += f"""
<main>
<section>
 <div class="container">
  <span class="section-kicker">Wissen</span>
  <h2>Gesundheit, verständlich erklärt.</h2>
  <p class="lead">
   Hier beantworten wir die Fragen, die uns am häufigsten gestellt werden — ohne
   Fachchinesisch und ohne Verkaufsabsicht. Jeder Beitrag ordnet ein, was im Körper
   passiert und was sich daran ändern lässt.
  </p>
  {liste}
 </div>
</section>
</main>
"""
    seite += FUSS.rstrip() + "\n"
    return seite


# --------------------------------------------------------------------------
# Publikationsseite
# --------------------------------------------------------------------------

PUBLIKATIONEN_QUELLE = WURZEL / "content" / "publikationen.md"


@dataclass
class Publikation:
    titel: str
    autoren: str
    quelle: str
    doi: str
    aussage: str

    @property
    def url(self) -> str:
        return f"https://doi.org/{self.doi}" if self.doi else ""


def lies_publikationen() -> tuple[dict[str, str], list[tuple[str, list[Publikation]]]]:
    """Liest content/publikationen.md.

    Zeilenformat je Eintrag:
        - Titel | Autoren | Journal Jahr | doi:10.xxxx/yyy | Aussage
    Die DOI darf leer bleiben. Titel und Aussage sind Pflicht -- eine Publikation
    ohne Aussage sagt dem Leser nichts und fliegt mit Fehlermeldung raus.
    """
    if not PUBLIKATIONEN_QUELLE.exists():
        return {}, []
    kopf, koerper = lies_frontmatter(
        PUBLIKATIONEN_QUELLE.read_text(encoding="utf-8"),
        PUBLIKATIONEN_QUELLE,
        pflicht=("titel", "beschreibung"),
    )

    themen: list[tuple[str, list[Publikation]]] = []
    vorspann: list[str] = []
    aktuelles_thema: str | None = None

    im_kommentar = False
    for zeile in koerper.splitlines():
        strip = zeile.strip()
        # HTML-Kommentare vollständig überspringen -- vorher rutschte der
        # Formathinweis aus der Quelldatei in den Vorspann der Seite.
        if strip.startswith("<!--"):
            im_kommentar = "-->" not in strip
            continue
        if im_kommentar:
            im_kommentar = "-->" not in strip
            continue
        if strip.startswith("## "):
            aktuelles_thema = strip[3:].strip()
            themen.append((aktuelles_thema, []))
            continue
        if strip.startswith("- ") and aktuelles_thema:
            felder = [f.strip() for f in strip[2:].split("|")]
            while len(felder) < 5:
                felder.append("")
            titel, autoren, quelle, doi_roh, aussage = felder[:5]
            if not titel or not aussage:
                raise SystemExit(
                    f"publikationen.md: Eintrag ohne Titel oder Aussage: {strip[:70]!r}"
                )
            doi = doi_roh.removeprefix("doi:").strip()
            themen[-1][1].append(Publikation(titel, autoren, quelle, doi, aussage))
            continue
        if strip and aktuelles_thema is None:
            vorspann.append(strip)

    kopf["_vorspann"] = " ".join(vorspann)
    return kopf, themen


def json_ld_publikationen(themen: list[tuple[str, list[Publikation]]], url: str) -> str:
    import json

    eintraege = []
    position = 1
    for _, liste in themen:
        for p in liste:
            werk = {
                "@type": "ScholarlyArticle",
                "name": p.titel,
                "description": p.aussage,
            }
            if p.autoren:
                werk["author"] = p.autoren
            if p.quelle:
                werk["publication"] = p.quelle
            if p.doi:
                werk["identifier"] = f"https://doi.org/{p.doi}"
                werk["url"] = f"https://doi.org/{p.doi}"
            eintraege.append({"@type": "ListItem", "position": position, "item": werk})
            position += 1

    daten = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "@id": f"{url}#seite",
                "name": "Publikationen",
                "url": url,
                "inLanguage": "de-DE",
                "publisher": {"@id": f"{BASIS_URL}/#organisation"},
            },
            {
                "@type": "ItemList",
                "@id": f"{url}#liste",
                "numberOfItems": len(eintraege),
                "itemListElement": eintraege,
            },
        ],
    }
    return (
        '<script type="application/ld+json">\n'
        + json.dumps(daten, ensure_ascii=False, indent=1)
        + "\n</script>\n"
    )


def baue_publikationen() -> int:
    kopf, themen = lies_publikationen()
    if not themen:
        return 0
    url = f"{BASIS_URL}/publikationen/"
    seite = kopf_seite(f"{kopf['titel']} — DVGP", kopf["beschreibung"], url)

    abschnitte = []
    for thema, liste in themen:
        zeilen = "\n".join(
            f"""    <li class="publikation">
     <span class="pub-titel">{inline(p.titel)}</span>
     <span class="pub-quelle">{inline(p.autoren)}{' · ' if p.autoren and p.quelle else ''}{inline(p.quelle)}</span>
     <span class="pub-aussage">{inline(p.aussage)}</span>
     {f'<a class="pub-doi" href="{p.url}" target="_blank" rel="noopener">DOI: {p.doi}</a>' if p.doi else ''}
    </li>"""
            for p in liste
        )
        abschnitte.append(
            f"""  <h2>{inline(thema)}</h2>
   <ul class="pub-liste">
{zeilen}
   </ul>"""
        )

    anzahl = sum(len(l) for _, l in themen)
    seite += f"""
<main class="content-page">
 <a class="back-link" href="/">Zurück zur Startseite</a>
 <span class="section-kicker">Publikationen</span>
 <h1>{inline(kopf['titel'])}</h1>
 <p class="meta">{anzahl} Arbeiten in {len(themen)} Themenbereichen</p>

 <p>{inline(kopf.get('_vorspann', ''))}</p>

{chr(10).join(abschnitte)}
</main>
"""
    seite += FUSS.rstrip() + "\n"
    seite = seite.replace("</body>", json_ld_publikationen(themen, url) + "</body>")

    ziel = SITE / "publikationen"
    ziel.mkdir(parents=True, exist_ok=True)
    (ziel / "index.html").write_text(seite, encoding="utf-8")
    print(f"  geschrieben  publikationen/index.html   ({anzahl} Arbeiten, {len(themen)} Themen)")
    return anzahl


# --------------------------------------------------------------------------
# Sitemap und llms.txt nachziehen
# --------------------------------------------------------------------------

def schreibe_sitemap(beitraege: list[Beitrag]) -> None:
    heute = date.today().isoformat()
    eintraege = [
        f"  <url>\n    <loc>{BASIS_URL}/</loc>\n    <changefreq>monthly</changefreq>\n    <priority>1.0</priority>\n  </url>",
        f"  <url>\n    <loc>{BASIS_URL}/wissen/</loc>\n    <lastmod>{heute}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>",
    ]
    for b in beitraege:
        eintraege.append(
            f"  <url>\n    <loc>{b.url}</loc>\n    <lastmod>{b.datum}</lastmod>\n"
            f"    <changefreq>yearly</changefreq>\n    <priority>0.6</priority>\n  </url>"
        )
    eintraege.append(
        f"  <url>\n    <loc>{BASIS_URL}/publikationen/</loc>\n    <lastmod>{heute}</lastmod>\n"
        f"    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>"
    )
    eintraege.append(
        f"  <url>\n    <loc>{BASIS_URL}/impressum</loc>\n    <changefreq>yearly</changefreq>\n    <priority>0.3</priority>\n  </url>"
    )
    inhalt = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(eintraege)
        + "\n</urlset>\n"
    )
    (SITE / "sitemap.xml").write_text(inhalt, encoding="utf-8")


MARKE_START = "## Beiträge (Wissen)"
MARKE_ENDE = "## Kontakt"


def schreibe_llms(beitraege: list[Beitrag]) -> None:
    pfad = SITE / "llms.txt"
    text = pfad.read_text(encoding="utf-8")
    if beitraege:
        zeilen = [MARKE_START, ""]
        zeilen += [
            f"- [{b.titel}]({b.url}): {b.beschreibung}" for b in beitraege
        ]
        zeilen += ["", MARKE_ENDE]
        block = "\n".join(zeilen)
    else:
        block = MARKE_ENDE

    if MARKE_START in text:
        text = re.sub(
            re.escape(MARKE_START) + r".*?" + re.escape(MARKE_ENDE),
            block,
            text,
            flags=re.S,
        )
    else:
        text = text.replace(MARKE_ENDE, block, 1)
    pfad.write_text(text, encoding="utf-8")


# --------------------------------------------------------------------------

def main() -> int:
    if not ARTIKEL_VERZ.exists():
        print(f"Kein Verzeichnis {ARTIKEL_VERZ.relative_to(WURZEL)} — nichts zu tun.")
        return 1

    beitraege = lies_beitraege()
    WISSEN.mkdir(parents=True, exist_ok=True)

    for b in beitraege:
        ziel = WISSEN / f"{b.slug}.html"
        ziel.write_text(baue_beitrag(b), encoding="utf-8")
        print(f"  geschrieben  wissen/{b.slug}.html   ({b.lesezeit} Min., {len(b.abschnitte)} Fragen im Schema)")

    (WISSEN / "index.html").write_text(baue_uebersicht(beitraege), encoding="utf-8")
    print(f"  geschrieben  wissen/index.html   ({len(beitraege)} Beiträge)")

    # Verwaiste HTML-Dateien melden, aber nicht löschen.
    bekannt = {f"{b.slug}.html" for b in beitraege} | {"index.html"}
    for datei in WISSEN.glob("*.html"):
        if datei.name not in bekannt:
            print(f"  HINWEIS      wissen/{datei.name} hat keine Markdown-Quelle mehr")

    baue_publikationen()

    schreibe_sitemap(beitraege)
    print("  aktualisiert sitemap.xml")
    schreibe_llms(beitraege)
    print("  aktualisiert llms.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
