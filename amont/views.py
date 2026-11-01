import csv
import json
import os

from django.core.cache import cache
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render

from .analytics import bundle

PAGES = [
    # slug, titre, sous-titre (bandeau), libellé d'onglet
    ("cockpit", "Accueil", "L'amont pétrolier et gazier ivoirien en un coup d'œil", "Accueil"),
    ("carte", "Carte des blocs", "Le cadastre pétrolier interactif : 50 blocs, gisements, opérateurs et historique des contrats.", "Carte"),
    ("production", "Production", "Pétrole brut et gaz naturel par gisement, déclin des champs matures, ventes de gaz.", "Production"),
    ("exploration", "Exploration", "Contrats de partage de production, forages, sismique et découvertes depuis 1992.", "Exploration"),
    ("acteurs", "Acteurs", "Les opérateurs du domaine, leurs surfaces, leur production et la concentration du marché.", "Acteurs"),
    ("economie", "Économie & fiscalité", "Recettes de l'État, partage de la rente et sensibilité au prix du Brent.", "Économie"),
    ("simulateur", "Simulateur CPP", "Modélisez le partage de production d'un gisement : part de l'État, VAN, TRI, Brent d'équilibre.", "Simulateur"),
    ("perspectives", "Perspectives 2035", "Scénarios de production et de recettes face aux objectifs de 200 000 b/j en 2030 et 500 000 b/j en 2035.", "Perspectives"),
    ("donnees", "Données & API", "Registre des blocs, exports CSV, API ouverte et méthodologie.", "Données"),
]


def get_bundle():
    data = cache.get("bundle")
    if data is None:
        data = bundle()
        cache.set("bundle", data, 300)
    return data


def page(request, slug="cockpit"):
    meta = next((p for p in PAGES if p[0] == slug), None)
    if not meta:
        raise Http404
    return render(request, f"amont/{slug}.html", {"pages": PAGES, "slug": slug, "titre": meta[1],
                                                   "sous_titre": meta[2], "data": get_bundle(),
                                                   "carto_key": os.environ.get("CARTO_API_KEY", "")})


def api_index(request):
    return JsonResponse({"endpoints": {
        "/api/bundle.json": "Toutes les données de la plateforme",
        "/api/blocs.geojson": "Cadastre (FeatureCollection)",
        "/api/<cle>.json": "Une section du bundle (recettes, champs, acteurs, evenements, exports...)",
        "/export/<table>.csv": "production | recettes | blocs | evenements | exports",
    }}, json_dumps_params={"ensure_ascii": False, "indent": 2})


def api(request, cle):
    data = get_bundle()
    if cle == "bundle":
        return JsonResponse(data, json_dumps_params={"ensure_ascii": False})
    if cle == "blocs":
        resp = HttpResponse(json.dumps(data["blocs"], ensure_ascii=False), content_type="application/geo+json")
        return resp
    if cle not in data:
        raise Http404
    return JsonResponse({cle: data[cle]}, json_dumps_params={"ensure_ascii": False})


def export_csv(request, table):
    d = get_bundle()
    resp = HttpResponse(content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = f'attachment; filename="amont_ci_{table}.csv"'
    resp.write("﻿")
    w = csv.writer(resp, delimiter=";")
    if table == "production":
        w.writerow(["champ", "annee", "petrole_bbl", "gaz_mmscf", "ventes_gaz_mmbtu", "pouvoir_calorifique"])
        for c in d["champs"]:
            if c["serie"]:
                for i, an in enumerate(d["annees"]):
                    s = c["serie"]
                    w.writerow([c["nom"], an, s["petrole"][i], s["gaz"][i], s["ventes"][i], s["pcs"][i]])
    elif table == "blocs":
        cols = ["code", "zone_label", "statut_2024", "statut_2026", "operateur", "operateur_2026", "date_cpp",
                "date_cpp_2026", "superficie", "superficie_officielle", "geometrie_officielle"]
        w.writerow(cols)
        for f in d["blocs"]["features"]:
            w.writerow([f["properties"][c] for c in cols])
    elif table in ("recettes", "evenements", "exports"):
        rows = d[table]
        w.writerow(rows[0].keys())
        for r in rows:
            w.writerow(r.values())
    else:
        raise Http404
    return resp
