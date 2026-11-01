"""
Géométrie INDICATIVE du cadastre pétrolier.

Le découpage ci-dessous reproduit la logique de la carte DGH (bandes onshore / plateau /
offshore profond / ultra-profond, ordre ouest -> est), mais les limites ne sont PAS les
coordonnées officielles. Pour la géométrie exacte, charger le shapefile/GeoJSON officiel :

    python manage.py load_amont --geojson data/blocs_officiels.geojson

(propriété `code` attendue, ex. "CI-101").
"""
import math

# Trait de côte simplifié (lon, lat), du Liberia au Ghana
COTE = [(-7.53, 4.36), (-7.10, 4.42), (-6.64, 4.73), (-6.20, 4.93), (-5.90, 5.00), (-5.50, 5.11),
        (-5.00, 5.17), (-4.50, 5.22), (-4.00, 5.25), (-3.75, 5.20), (-3.30, 5.12), (-3.10, 5.10)]

# Contour simplifié du territoire (décor de la carte quand les tuiles ne chargent pas)
TERRITOIRE = COTE + [(-2.75, 5.60), (-3.00, 6.30), (-3.20, 6.80), (-2.95, 7.70), (-2.60, 8.10), (-2.50, 9.00),
                     (-2.70, 9.50), (-3.00, 9.90), (-3.60, 9.95), (-4.30, 9.60), (-4.70, 9.90), (-5.50, 10.40),
                     (-6.20, 10.30), (-6.90, 10.20), (-7.60, 10.40), (-8.20, 10.10), (-8.00, 9.40), (-8.20, 9.00),
                     (-7.80, 8.40), (-8.30, 7.60), (-8.40, 6.90), (-7.80, 6.30), (-7.50, 5.80), (-7.40, 5.10),
                     (-7.53, 4.36)]


def lat_cote(lon):
    if lon <= COTE[0][0]:
        return COTE[0][1]
    for (x0, y0), (x1, y1) in zip(COTE, COTE[1:]):
        if x0 <= lon <= x1:
            return y0 + (y1 - y0) * (lon - x0) / (x1 - x0)
    return COTE[-1][1]


# bandes : (décalage haut, décalage bas) en degrés de latitude par rapport à la côte
BANDES = {
    "onshore": (+0.30, +0.02),
    "plateau": (-0.03, -0.24),
    "profond": (-0.24, -0.58),
    "tres_profond": (-0.58, -0.98),
    "ultra": (-0.98, -1.55),
}

RANGEES = {
    "onshore": ([-5.62, -5.30, -5.00, -4.70, -4.42, -4.10, -3.72, -3.12],
                ["CI-518", "CI-519", "CI-520", "CI-521", "CI-522", "CI-524", "CI-803"]),
    "plateau": ([-7.50, -7.05, -6.60, -6.20, -5.85, -5.50, -5.20, -4.95, -4.72, -4.52, -4.32, -4.12, -3.94, -3.68, -3.10],
                ["CI-500", "CI-513", "CI-503", "CI-24", "CI-301", "CI-302", "CI-531", "CI-523", "CI-525",
                 "CI-40", "CI-26", "CI-11", "CI-12", "CI-27"]),
    "profond": ([-7.50, -6.90, -6.35, -5.90, -5.55, -5.20, -4.98, -4.72, -4.45, -4.20, -3.95, -3.60, -3.10],
                ["CI-604", "CI-600", "CI-601", "CI-502", "CI-504", "CI-501", "CI-205", "CI-401", "CI-102",
                 "CI-103", "CI-101", "CI-804"]),
    "tres_profond": ([-7.50, -6.80, -6.20, -5.70, -5.15, -4.60, -4.25, -3.98, -3.80, -3.10],
                     ["CI-602", "CI-603", "CI-605", "CI-709", "CI-526", "CI-705", "CI-706", "CI-801", "CI-802"]),
    "ultra": ([-7.50, -6.99, -6.48, -5.96, -5.45, -4.94, -4.42, -3.91, -3.40],
              ["CI-700", "CI-701", "CI-702", "CI-703", "CI-704", "CI-707", "CI-708", "CI-710"]),
}


def _bord(x0, x1, offset, n=6):
    return [(x0 + (x1 - x0) * i / n, round(lat_cote(x0 + (x1 - x0) * i / n) + offset, 4)) for i in range(n + 1)]


def polygone(x0, x1, bande):
    haut, bas = BANDES[bande]
    top = _bord(x0, x1, haut)
    bottom = list(reversed(_bord(x0, x1, bas)))
    ring = [[round(x, 4), y] for x, y in top + bottom]
    ring.append(ring[0])
    return ring


def superficie_km2(ring):
    """Aire approchée (projection équirectangulaire locale)."""
    lat0 = sum(p[1] for p in ring) / len(ring)
    kx, ky = 111.32 * math.cos(math.radians(lat0)), 110.57
    pts = [(x * kx, y * ky) for x, y in ring]
    return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:]))) / 2


def geometries():
    """-> {code: (zone_bande, ring)}"""
    out = {}
    for bande, (bornes, codes) in RANGEES.items():
        for code, x0, x1 in zip(codes, bornes, bornes[1:]):
            out[code] = (bande, polygone(x0, x1, bande))
    return out
