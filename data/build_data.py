"""Construit data/cadastre.geojson et data/base_blocs.json depuis les fichiers sources (data/source/)."""
import json
from pathlib import Path

import pandas as pd

ACTUELS = None  # liste des 50 blocs DGH 2024, passée par l'appelant
SRC = Path(__file__).parent / "source"
OUT = Path(__file__).parent


def ring(coords):
    pts = [[round(x, 6), round(y, 6)] for x, y in coords]
    if pts and pts[0] != pts[-1]:
        pts.append(pts[0])
    return pts


def build(codes_actuels):
    g = json.load(open(SRC / "GéoJson Blocs pétroliers.json", encoding="utf-8"))
    actuels, anciens = [], []
    for f in g["features"]:
        code = f["properties"].get("name", "").strip().upper()
        coords = f["geometry"]["coordinates"][0]
        if not code or not coords or any(len(pt) != 2 for pt in coords):
            continue  # ex. CI-100 (ancien bloc) : coordonnée mal saisie dans la source
        feat = {"type": "Feature", "properties": {"code": code}, "geometry": {"type": "Polygon", "coordinates": [ring(coords)]}}
        (actuels if code in codes_actuels else anciens).append(feat)
    # CI-302 : présent dans l'Excel de coordonnées mais pas dans le GeoJSON
    xy = pd.read_excel(SRC / "Coordonnées géographiques Blocs.xlsx")
    present = {f["properties"]["code"] for f in actuels}
    for code in sorted(set(xy.BLOCS) & set(codes_actuels) - present):
        pts = xy[xy.BLOCS == code][["Longitude", "Latitude"]].values.tolist()
        note = ""
        if code == "CI-302":  # latitude 4,248 isolée au milieu de points à 5,2-5,4 : probable faute de saisie
            pts = [[x, 5.248146 if abs(y - 4.248146) < 1e-5 else y] for x, y in pts]
            note = "Latitude 4,248146 corrigée en 5,248146 (probable faute de saisie dans la source)"
        actuels.append({"type": "Feature", "properties": {"code": code, "note": note},
                        "geometry": {"type": "Polygon", "coordinates": [ring(pts)]}})
    json.dump({"type": "FeatureCollection", "features": actuels}, open(OUT / "cadastre.geojson", "w"), ensure_ascii=False)
    json.dump({"type": "FeatureCollection", "features": anciens}, open(OUT / "cadastre_ancien.geojson", "w"), ensure_ascii=False)

    b = pd.read_excel(SRC / "Base Pétrole finale.xlsx", sheet_name="Feuil1")
    base = {}
    for _, r in b.iterrows():
        hist = []
        for op, pa, dt in [("Opérateur1", "Patenaires (hors PETROCI)", "Date de signature du 1er CPP"),
                           ("Opérateur CPP 2", "Patenaires CPP 2 (hors PETROCI)", "Date de la 2ème signature du CPP"),
                           ("Opérateur CPP 3", "Patenaires CPP 3 (hors PETROCI)", "Date de la 3ème signature du CPP")]:
            if pd.notna(r.get(op)):
                hist.append({"operateur": str(r[op]).strip(), "partenaires": str(r[pa]).replace("\n", ", ").strip() if pd.notna(r.get(pa)) else "",
                             "date": r[dt].date().isoformat() if pd.notna(r.get(dt)) else None})
        base[r["Blocs"].strip().upper()] = {
            "superficie": None if pd.isna(r["Superfice (en Km²)"]) else float(r["Superfice (en Km²)"]),
            "profondeur": str(r["Type de profondeur"]).strip(),
            "historique": hist,
            "statut_base": str(r["Statut du bloc"]).strip(),
        }
    json.dump(base, open(OUT / "base_blocs.json", "w"), ensure_ascii=False, indent=1)
    return len(actuels), len(anciens), sorted(set(codes_actuels) - {f["properties"]["code"] for f in actuels})


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(OUT.parent))
    from amont import seed_data as S
    codes = set(S.BLOCS_ACTIFS) | set(S.BLOCS_LIBRES_2024)
    print(build(codes))
