#!/usr/bin/env python3
"""Beschafft fehlende Beitragsbilder — für den Lauf in GitHub Actions.

Warum es dieses Skript gibt: Die Wissens-Routine läuft in der Cloud und kann keine
Stockfotos ziehen. Sie entscheidet aber sehr wohl, was aufs Bild gehört. Deshalb
schreibt sie beim Verfassen zwei Felder ins Frontmatter --

    bild_suche: englischer Suchbegriff für die Stockfoto-Suche
    bild_alt:   deutscher Alternativtext

-- und dieses Skript besorgt den Rest, wenn der Beitrag gepusht wird. Der Kopf des
Autors bleibt beim Modell, die Hände hat die Maschine.

Ablauf je Beitrag ohne Bild:
  1. Unsplash durchsuchen
  2. Download registrieren (Lizenzpflicht, nicht überspringbar)
  3. Original laden, auf 1200 px als WebP und JPG rechnen
  4. Ort, Bildunterschrift, Stichworte und Lizenzangabe in die Dateien schreiben
  5. Fotograf im Impressum ergänzen

Braucht UNSPLASH_API_KEY in der Umgebung, Pillow und exiftool.
Ohne Schlüssel bricht es nicht ab, sondern meldet das und lässt die Beiträge in Ruhe.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
ARTIKEL = WURZEL / "content" / "artikel"
BILDER = WURZEL / "site" / "bilder"
ROH = WURZEL / "content" / "bilder-roh"
IMPRESSUM = WURZEL / "site" / "impressum.html"
VERTRAG = WURZEL / "content-engine.json"

BREITE = 1200
API = os.environ.get("UNSPLASH_API_KEY", "").strip()


# --------------------------------------------------------------------------
# Projektdaten
# --------------------------------------------------------------------------

def bildvertrag() -> dict:
    """Ort und Koordinate für das Geotaggen, aus content-engine.json."""
    daten = json.loads(VERTRAG.read_text(encoding="utf-8"))
    b = daten.get("bilder", {})
    return {
        "ort": b.get("ort", "Magdeburg"),
        "breitengrad": b.get("koordinate", {}).get("latitude", 52.1314783),
        "laengengrad": b.get("koordinate", {}).get("longitude", 11.6400789),
        "bundesland": b.get("bundesland", "Sachsen-Anhalt"),
    }


def frontmatter(pfad: Path) -> tuple[dict[str, str], str]:
    text = pfad.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    _, kopf, rest = text.split("---", 2)
    daten = {}
    for zeile in kopf.strip().splitlines():
        if ":" in zeile:
            k, _, v = zeile.partition(":")
            daten[k.strip()] = v.strip()
    return daten, rest


def offene_beitraege() -> list[tuple[Path, dict]]:
    """Beiträge, zu denen noch keine oder nur eine der beiden Bildfassungen liegt."""
    offen = []
    for pfad in sorted(ARTIKEL.glob("*.md")):
        daten, _ = frontmatter(pfad)
        slug = daten.get("slug") or pfad.stem
        if (BILDER / f"{slug}.webp").exists() and (BILDER / f"{slug}.jpg").exists():
            continue
        daten["slug"] = slug
        offen.append((pfad, daten))
    return offen


# --------------------------------------------------------------------------
# Unsplash
# --------------------------------------------------------------------------

def hole(url: str, roh: bool = False):
    anfrage = urllib.request.Request(url, headers={
        "Authorization": f"Client-ID {API}",
        "User-Agent": "dvgp-website/1.0 (+https://dvgp.info)",
    })
    with urllib.request.urlopen(anfrage, timeout=60) as antwort:
        daten = antwort.read()
    return daten if roh else json.loads(daten)


def suche(begriff: str) -> dict | None:
    url = ("https://api.unsplash.com/search/photos"
           f"?query={urllib.parse.quote(begriff)}&per_page=5&orientation=landscape")
    treffer = hole(url).get("results", [])
    return treffer[0] if treffer else None


# --------------------------------------------------------------------------
# Bild
# --------------------------------------------------------------------------

def rechne(quelle: Path, slug: str) -> tuple[Path, Path]:
    from PIL import Image

    with Image.open(quelle) as bild:
        bild = bild.convert("RGB")
        if bild.width > BREITE:
            hoehe = round(bild.height * BREITE / bild.width)
            bild = bild.resize((BREITE, hoehe), Image.LANCZOS)
        BILDER.mkdir(parents=True, exist_ok=True)
        webp = BILDER / f"{slug}.webp"
        jpg = BILDER / f"{slug}.jpg"
        bild.save(webp, "WEBP", quality=82, method=6)
        bild.save(jpg, "JPEG", quality=85, optimize=True, progressive=True)
    return webp, jpg


def beschrifte(dateien: list[Path], ort: dict, titel: str, beschreibung: str,
               stichworte: list[str], credit: str, quelle_url: str, fotograf: str) -> bool:
    """Ort, Bildunterschrift und Lizenzangabe in die Dateien schreiben.

    Muss NACH dem Rechnen laufen -- Pillow schreibt die Pixel neu und wirft dabei
    jede Metadatenspur weg. Umgekehrt wäre die Arbeit sofort wieder verloren.
    """
    befehl = [
        "exiftool", "-m", "-overwrite_original",
        f"-GPSLatitude={ort['breitengrad']}", "-GPSLatitudeRef=N",
        f"-GPSLongitude={ort['laengengrad']}", "-GPSLongitudeRef=E",
        "-GPSMapDatum=WGS-84",
        f"-XMP:City={ort['ort']}", f"-IPTC:City={ort['ort']}",
        f"-XMP:State={ort['bundesland']}", f"-IPTC:Province-State={ort['bundesland']}",
        "-XMP:Country=Deutschland", "-IPTC:Country-PrimaryLocationName=Deutschland",
        "-IPTC:Country-PrimaryLocationCode=DEU",
        f"-IPTC:Caption-Abstract={beschreibung}", f"-XMP:Description={beschreibung}",
        f"-EXIF:ImageDescription={beschreibung}",
        f"-IPTC:ObjectName={titel}", f"-XMP:Title={titel}",
        f"-IPTC:Credit={credit}", f"-XMP:Credit={credit}",
        f"-IPTC:Source={quelle_url}", f"-XMP:Source={quelle_url}",
        f"-IPTC:By-line={fotograf}", f"-XMP:Creator={fotograf}",
        f"-EXIF:Artist={fotograf}",
    ]
    for wort in stichworte:
        befehl += [f"-IPTC:Keywords+={wort}", f"-XMP:Subject+={wort}"]
    befehl += [str(p) for p in dateien]

    ergebnis = subprocess.run(befehl, capture_output=True, text=True)
    if ergebnis.returncode != 0:
        print(f"    WARNUNG  exiftool: {ergebnis.stderr.strip()[:200]}")
    return ergebnis.returncode == 0


def pruefe(dateien: list[Path]) -> bool:
    """Nachsehen, ob die Koordinate wirklich in beiden Fassungen steht."""
    ergebnis = subprocess.run(
        ["exiftool", "-s", "-GPSLatitude", "-Credit", *[str(p) for p in dateien]],
        capture_output=True, text=True)
    treffer = ergebnis.stdout.count("GPSLatitude")
    if treffer < len(dateien):
        print(f"    WARNUNG  Koordinate nur in {treffer} von {len(dateien)} Dateien")
    return treffer == len(dateien)


# --------------------------------------------------------------------------
# Frontmatter und Impressum nachziehen
# --------------------------------------------------------------------------

def ergaenze_impressum(fotograf: str) -> bool:
    text = IMPRESSUM.read_text(encoding="utf-8")
    if fotograf in text:
        return False
    # Vor dem abschließenden "und X auf <a ...>Unsplash</a>" einhängen.
    muster = re.compile(r"(Fotos: .*?), ([^,]+?) auf\s*\n?\s*<a href=\"https://unsplash\.com\"",
                        re.S)
    treffer = muster.search(text)
    if not treffer:
        print(f"    WARNUNG  Bildnachweise im Impressum nicht gefunden, {fotograf} fehlt dort")
        return False
    neu = f"{treffer.group(1)}, {treffer.group(2)} und {fotograf} auf\n  <a href=\"https://unsplash.com\""
    IMPRESSUM.write_text(text[:treffer.start()] + neu + text[treffer.end():], encoding="utf-8")
    return True


# --------------------------------------------------------------------------

def main() -> int:
    offen = offene_beitraege()
    if not offen:
        print("  Alle Beiträge haben ein Bild. Nichts zu tun.")
        return 0

    if not API:
        print("  UNSPLASH_API_KEY fehlt — keine Bildersuche möglich.")
        for _, d in offen:
            print(f"    ohne Bild: {d['slug']}")
        return 0

    ort = bildvertrag()
    ROH.mkdir(parents=True, exist_ok=True)
    geholt = 0

    for pfad, daten in offen:
        slug = daten["slug"]
        begriff = daten.get("bild_suche", "").strip()
        if not begriff:
            print(f"  ÜBERSPRUNGEN  {slug}: kein 'bild_suche' im Frontmatter")
            continue

        print(f"  {slug}")
        print(f"    Suche: {begriff}")
        try:
            foto = suche(begriff)
        except Exception as fehler:
            print(f"    FEHLER  Suche: {type(fehler).__name__}: {fehler}")
            continue
        if not foto:
            print("    FEHLER  kein Treffer")
            continue

        fotograf = foto["user"]["name"]
        quelle_url = foto["links"]["html"]
        kuerzel = foto["id"]

        try:
            # Lizenzpflicht: jeder Download wird bei Unsplash registriert.
            hole(foto["links"]["download_location"])
            rohdaten = hole(foto["urls"]["full"], roh=True)
        except Exception as fehler:
            print(f"    FEHLER  Download: {type(fehler).__name__}: {fehler}")
            continue

        original = ROH / f"{slug}-us{kuerzel}.jpg"
        original.write_bytes(rohdaten)

        webp, jpg = rechne(original, slug)

        alt = daten.get("bild_alt", "").strip()
        if not alt:
            print("    WARNUNG  kein 'bild_alt' im Frontmatter — Metadaten bleiben dünn")
        beschreibung = (f"{alt} Deutscher Verband für Gesundheitsförderung und "
                        f"Prävention, {ort['ort']}." if alt else
                        f"{daten.get('titel', slug)} — Deutscher Verband für "
                        f"Gesundheitsförderung und Prävention, {ort['ort']}.")
        stichworte = [w for w in [daten.get("cluster", ""), "Krafttraining", "Prävention",
                                  ort["ort"], "DVGP"] if w]

        beschrifte([webp, jpg], ort, daten.get("titel", slug)[:180], beschreibung,
                   stichworte, f"Photo by {fotograf} on Unsplash", quelle_url, fotograf)
        pruefe([webp, jpg])

        if ergaenze_impressum(fotograf):
            print(f"    Impressum: {fotograf} ergänzt")

        print(f"    {webp.stat().st_size // 1024} KB WebP · "
              f"{jpg.stat().st_size // 1024} KB JPG · Foto: {fotograf}")
        geholt += 1

    print(f"\n  {geholt} von {len(offen)} Beiträgen mit Bild versorgt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
