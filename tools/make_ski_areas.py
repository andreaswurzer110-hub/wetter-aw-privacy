"""Erzeugt assets/ski_areas.tsv.gz: Skigebiete weltweit für die Karte
„Berg- und Skiwetter“.

Quelle: OpenSkiMap (aus OpenStreetMap berechnet, ODbL — die erzeugte Datei
ist damit ebenfalls ODbL, Hinweis „© OpenStreetMap-Mitwirkende“). Nur
Skigebiete in Betrieb (`status` „operating“, also nicht stillgelegt — nicht
„heute geöffnet“) mit Namen und mindestens 1 km Abfahrten oder 2 Liften.

Spalten: Name, Breite, Länge (Mittel der Umrisspunkte), tiefster und höchster
Punkt (m), Pisten-km leicht, mittel, schwer (advanced + expert), Lifte,
Website.

Warum als Datei in der App: Die Overpass-API von OpenStreetMap war beim
Ausprobieren (Oktober 2026) oft überlastet (504, 20 s und mehr, Spiegel ohne
Antwort) — die Suche nach dem nächsten Skigebiet geht so ohne Netz und sofort.
Damit die Liste ohne App-Update frisch bleibt, baut eine GitHub-Aktion sie
jede Woche neu (Repository wetter-aw-privacy, Ordner daten/); die App holt
sie einmal im Monat.

Die gepackte Datei hat keinen Zeitstempel (mtime 0): gleiche Liste, gleiche
Datei — sonst gäbe es jede Woche eine leere Änderung.

Aufruf: python tools/make_ski_areas.py assets/ski_areas.tsv.gz [--neu]
  --neu  OpenSkiMap neu herunterladen (sonst tools/ski_areas.geojson.gz, falls da)
"""
import gzip
import io
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = 'https://tiles.openskimap.org/geojson/ski_areas.geojson.gz'
UA = 'WetterAW-build/1.1 (at.aw.wetter; Datenabzug fuer die App)'


def download(path):
    req = urllib.request.Request(SOURCE, headers={'User-Agent': UA})
    data = urllib.request.urlopen(req, timeout=300).read()
    open(path, 'wb').write(data)


def points(c):
    if isinstance(c, list) and len(c) >= 2 and all(isinstance(x, (int, float)) for x in c[:2]):
        yield c
    elif isinstance(c, list):
        for x in c:
            yield from points(x)


def clean(s):
    return ' '.join(str(s).replace('\t', ' ').split())


def rows_from(src):
    """Zeilen (Text, ohne Zeilenende) aus der OpenSkiMap-Datei, sortiert."""
    features = json.loads(gzip.open(src).read())['features']
    rows = []
    for f in features:
        p = f.get('properties') or {}
        name = p.get('name')
        if p.get('status') != 'operating' or not name:
            continue
        st = p.get('statistics') or {}
        runs = (((st.get('runs') or {}).get('byActivity') or {}).get('downhill') or {}).get('byDifficulty') or {}
        km = {k: (v or {}).get('lengthInKm') or 0 for k, v in runs.items()}
        lifts = sum((v or {}).get('count') or 0 for v in ((st.get('lifts') or {}).get('byType') or {}).values())
        if sum(km.values()) < 1 and lifts < 2:
            continue
        pts = list(points((f.get('geometry') or {}).get('coordinates')))
        if not pts:
            continue
        lon = sum(x[0] for x in pts) / len(pts)
        lat = sum(x[1] for x in pts) / len(pts)
        lo, hi = st.get('minElevation'), st.get('maxElevation')
        web = next((w for w in (p.get('websites') or []) if isinstance(w, str) and w.startswith('http')), '')
        rows.append('\t'.join([
            clean(name),
            f'{lat:.4f}',
            f'{lon:.4f}',
            '' if lo is None else str(round(lo)),
            '' if hi is None else str(round(hi)),
            f"{km.get('easy', 0):.1f}",
            f"{km.get('intermediate', 0):.1f}",
            f"{km.get('advanced', 0) + km.get('expert', 0):.1f}",
            str(lifts),
            clean(web),
        ]))
    return sorted(rows)


def write(rows, out):
    data = ('\n'.join(rows) + '\n').encode('utf-8')
    buf = io.BytesIO()
    with gzip.GzipFile(filename='', mode='wb', fileobj=buf, compresslevel=9, mtime=0) as g:
        g.write(data)
    open(out, 'wb').write(buf.getvalue())
    return len(data), len(buf.getvalue())


def read(path):
    """Zeilen einer schon erzeugten Liste."""
    return [r for r in gzip.open(path).read().decode('utf-8').split('\n') if r]


def build(out, fresh=False):
    src = os.path.join(HERE, 'ski_areas.geojson.gz')
    if fresh or not os.path.exists(src):
        download(src)
    rows = rows_from(src)
    raw, packed = write(rows, out)
    return rows, raw, packed


if __name__ == '__main__':
    rows, raw, packed = build(sys.argv[1], fresh='--neu' in sys.argv)
    print(f'{len(rows)} Skigebiete, {raw // 1024} KB, gepackt {packed // 1024} KB')
