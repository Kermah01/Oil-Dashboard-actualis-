"""Couche analytique : assemble les données et calcule les indicateurs dérivés + insights."""
from collections import defaultdict

from .models import (Bloc, Brent, Champ, Evenement, Exportation, Forage, Operateur, Parametre,
                     ProductionAnnuelle, Puits, RecetteAnnuelle)


def _p(cle, defaut=None):
    o = Parametre.objects.filter(cle=cle).first()
    return o.valeur if o else defaut


def tcam(v0, v1, n):
    return (v1 / v0) ** (1 / n) - 1 if v0 and v1 and n else None


def bundle():
    ops = {o.id: o for o in Operateur.objects.all()}
    blocs = list(Bloc.objects.all())
    champs = list(Champ.objects.prefetch_related("blocs").all())
    prods = list(ProductionAnnuelle.objects.select_related("champ"))
    annees = sorted({p.annee for p in prods})

    # --- séries production par champ -----------------------------------------------
    series = defaultdict(lambda: {"petrole": [0] * len(annees), "gaz": [0] * len(annees),
                                  "ventes": [0] * len(annees), "pcs": [None] * len(annees)})
    for p in prods:
        i = annees.index(p.annee)
        s = series[p.champ.nom]
        s["petrole"][i], s["gaz"][i] = p.petrole_bbl, p.gaz_mmscf
        s["ventes"][i], s["pcs"][i] = p.ventes_gaz_mmbtu, p.pouvoir_calorifique
    champs_prod = [c for c in champs if c.nom in series]
    champs_prod.sort(key=lambda c: -series[c.nom]["petrole"][-1])
    tot_pet = [sum(series[c.nom]["petrole"][i] for c in champs_prod) for i in range(len(annees))]
    tot_gaz = [sum(series[c.nom]["gaz"][i] for c in champs_prod) for i in range(len(annees))]
    matures = [sum(series[c.nom]["petrole"][i] for c in champs_prod if c.nom != "Baleine") for i in range(len(annees))]

    # --- blocs -> GeoJSON ------------------------------------------------------------
    prod_par_bloc = defaultdict(lambda: [0] * len(annees))
    for c in champs_prod:
        codes = [b.code for b in c.blocs.all()]
        for code in codes:
            for i, v in enumerate(series[c.nom]["petrole"]):
                prod_par_bloc[code][i] += v / len(codes)
    ev_par_bloc = defaultdict(list)
    for e in Evenement.objects.all():
        if e.bloc_code:
            ev_par_bloc[e.bloc_code].append({"date": e.date.isoformat(), "titre": e.titre, "cat": e.categorie})
    puits_par_bloc = defaultdict(list)
    for w in Puits.objects.all():
        puits_par_bloc[w.bloc_code].append({"nom": w.nom, "type": w.type, "annee": w.annee, "resultat": w.resultat})
    forages_par_bloc = defaultdict(int)
    for f in Forage.objects.all():
        forages_par_bloc[f.bloc_code] += f.nombre

    features = []
    for b in blocs:
        op, op26 = ops.get(b.operateur_id), ops.get(b.operateur_2026_id)
        features.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [b.geometrie]} if b.geometrie else None, "properties": {
            "code": b.code, "zone": b.zone, "zone_label": b.get_zone_display(),
            "statut_2024": b.statut_2024, "statut_2026": b.statut_2026,
            "operateur": op.nom if op else None, "operateur_code": op.code if op else None,
            "operateur_2026": op26.nom if op26 else None, "operateur_2026_code": op26.code if op26 else None,
            "date_cpp": b.date_cpp.isoformat() if b.date_cpp else None,
            "date_cpp_2026": b.date_cpp_2026.isoformat() if b.date_cpp_2026 else None,
            "superficie": b.superficie_km2, "superficie_officielle": b.superficie_officielle,
            "geometrie_officielle": b.geometrie_officielle, "geometrie_note": b.geometrie_note, "contour_large": b.geometrie_note.startswith("Contour source"), "note_2026": b.note_2026,
            "superficie_source": b.superficie_source, "profondeur": b.profondeur, "historique": b.historique,
            "champs": [c.nom for c in b.champs.all()], "production": [round(v) for v in prod_par_bloc.get(b.code, [])],
            "evenements": ev_par_bloc.get(b.code, []), "puits": puits_par_bloc.get(b.code, []),
            "forages_2016_2024": forages_par_bloc.get(b.code, 0)}})

    # --- économie ------------------------------------------------------------------
    rec = list(RecetteAnnuelle.objects.all())
    brent_an = {b.annee: b.prix for b in Brent.objects.filter(mois__isnull=True)}
    marge = {b.annee: b.marge_sir for b in Brent.objects.filter(mois__isnull=True)}
    brent_m = [b.prix for b in Brent.objects.filter(annee=2024, mois__isnull=False)]
    rec_rows = []
    for r in rec:
        i = annees.index(r.annee) if r.annee in annees else None
        pet = tot_pet[i] if i is not None else None
        ventes = sum(series[c.nom]["ventes"][i] for c in champs_prod) if i is not None else None
        rec_pet = r.bic_petrole + r.taxe_petrole
        rec_gaz = r.bic_gaz + r.taxe_gaz
        valeur_brut = pet * brent_an[r.annee] * r.fcfa_usd / 1e9 if pet else None  # Mds FCFA
        rec_rows.append({
            "annee": r.annee, "bic_petrole": r.bic_petrole, "bic_gaz": r.bic_gaz, "taxe_petrole": r.taxe_petrole,
            "taxe_gaz": r.taxe_gaz, "bonus": r.bonus, "total": r.total, "rec_petrole": round(rec_pet, 1),
            "rec_gaz": round(rec_gaz, 1), "fcfa_usd": r.fcfa_usd, "brent": brent_an.get(r.annee),
            "fcfa_par_baril": round(rec_pet * 1e9 / pet) if pet else None,
            "usd_par_baril": round(rec_pet * 1e9 / pet / r.fcfa_usd, 2) if pet else None,
            "usd_par_mmbtu": round(rec_gaz * 1e9 / ventes / r.fcfa_usd, 2) if ventes else None,
            "valeur_brut_mds": round(valeur_brut, 1) if valeur_brut else None,
            "taux_prelevement": round(100 * rec_pet / valeur_brut, 1) if valeur_brut else None,
        })

    exports = [{"champ": e.champ, "bloc": e.bloc_code, "api": e.degre_api, "total": e.total_bbl,
                "etat": e.etat_bbl, "petroci": e.petroci_bbl, "prives": e.prives_bbl}
               for e in Exportation.objects.filter(annee=2024)]
    exp_tot = sum(e["total"] for e in exports)
    exp_public = sum(e["etat"] + e["petroci"] for e in exports)
    imports = _p("imports_brut_2024", [])
    imp_tot = sum(r[3] for r in imports)

    # --- exploration / acteurs -------------------------------------------------------
    cpp_par_an = defaultdict(lambda: defaultdict(int))
    for b in blocs:
        if b.date_cpp_2026 and b.operateur_2026_id:
            cpp_par_an[b.date_cpp_2026.year][ops[b.operateur_2026_id].code] += 1
    forages = defaultdict(lambda: defaultdict(int))
    for f in Forage.objects.all():
        forages[f.type][f.annee] += f.nombre

    acteurs = []
    for o in ops.values():
        bl24 = [b for b in blocs if b.operateur_id == o.id]
        bl26 = [b for b in blocs if b.operateur_2026_id == o.id]
        prod = sum(series[c.nom]["petrole"][-1] for c in champs_prod if c.operateur_id == o.id)
        gaz = sum(series[c.nom]["gaz"][-1] for c in champs_prod if c.operateur_id == o.id)
        acteurs.append({"code": o.code, "nom": o.nom, "pays": o.pays, "type": o.type, "couleur": o.couleur,
                        "blocs_2024": [b.code for b in bl24], "blocs_2026": [b.code for b in bl26],
                        "surface_2024": round(sum(b.superficie_km2 or 0 for b in bl24 if b.superficie_officielle)),
                        "surface_2026": round(sum(b.superficie_km2 or 0 for b in bl26 if b.superficie_officielle)),
                        "blocs_sans_surface": sum(not b.superficie_officielle for b in bl26),
                        "petrole_2024": prod, "gaz_2024": gaz,
                        "champs": [c.nom for c in champs if c.operateur_id == o.id]})
    acteurs.sort(key=lambda a: (-a["petrole_2024"], -a["surface_2026"]))
    surf_tot = sum(a["surface_2026"] for a in acteurs) or 1
    hhi = round(sum((100 * a["surface_2026"] / surf_tot) ** 2 for a in acteurs))

    # --- insights -------------------------------------------------------------------
    i24, i23 = len(annees) - 1, len(annees) - 2
    bal = series.get("Baleine", {"petrole": [0] * len(annees), "gaz": [0] * len(annees)})
    cagr_mat = tcam(matures[1], matures[-1], len(annees) - 2)
    r24 = next(r for r in rec_rows if r["annee"] == 2024)
    r23 = next(r for r in rec_rows if r["annee"] == 2023)
    ci27 = series.get("Foxtrot · Mahi · Marlin · Manta", {"gaz": [0] * len(annees)})
    eni = next((a for a in acteurs if a["code"] == "ENI"), None)
    insights = [
        {"k": f"{100 * bal['petrole'][i24] / tot_pet[i24]:.0f} %", "t": "de la production de brut 2024 vient de Baleine",
         "d": "Un seul gisement, mis en production en août 2023, pèse déjà plus que tous les champs historiques réunis."},
        {"k": f"{100 * cagr_mat:.1f} %/an" if cagr_mat else "—", "t": "déclin des champs matures (2019-2024)",
         "d": "Espoir, Baobab, CI-27 et CI-11 : sans nouveaux investissements, leur production se divise par deux en ≈ 7 ans."},
        {"k": f"{100 * ci27['gaz'][i24] / tot_gaz[i24]:.0f} %", "t": "du gaz national vient du seul bloc CI-27",
         "d": "Et 91,5 % du gaz vendu va à l'électricité : le parc thermique dépend d'un champ qui recule de 12 % en 2024."},
        {"k": f"× {r24['total'] / r23['total']:.1f}", "t": "revenus pétroliers et gaziers de l'État en 2024",
         "d": f"{r24['total']:.0f} Md FCFA contre {r23['total']:.0f} : effet Baleine (BIC gaz × 2,9) malgré un Brent en baisse."},
        {"k": f"{100 * exp_public / exp_tot:.1f} %", "t": "des barils exportés reviennent à l'État et PETROCI",
         "d": "Sur 15,2 M bbl exportés en 2024 : 1,68 M à l'État, 1,89 M à PETROCI, 11,66 M aux partenaires privés."},
        {"k": f"{imp_tot / 1e6:.1f} M bbl", "t": "de brut importé pour 15,2 M exportés",
         "d": "Paradoxe du raffinage : la SIR traite surtout du brut nigérian ; le brut ivoirien part à l'export."},
        {"k": f"{r24['usd_par_baril']:.1f} $/bbl", "t": "de recettes publiques par baril produit (2024)",
         "d": f"Soit un taux de prélèvement apparent de {r24['taux_prelevement']:.0f} % de la valeur brute du brut au prix du Brent."},
        {"k": f"{100 * eni['surface_2026'] / surf_tot:.0f} %" if eni else "—", "t": "de la surface attribuée est opérée par Eni (nov. 2026)",
         "d": f"Indice de concentration HHI (surface) : {hhi}. Petrobras (8 blocs, ≈ 34 000 km², 2026) devient le 1er détenteur de surface."},
    ]

    for it in insights:
        it["k"] = it["k"].replace(".", ",")

    ind = _p("indicateurs_2024", {})
    kpis = {
        "petrole_bopd": ind.get("petrole_bopd"), "gaz_mmscfd": ind.get("gaz_mmscfd"),
        "petrole_bbl": tot_pet[i24], "petrole_var": 100 * (tot_pet[i24] / tot_pet[i23] - 1),
        "gaz_var": 100 * (tot_gaz[i24] / tot_gaz[i23] - 1), "revenus": r24["total"],
        "revenus_var": 100 * (r24["total"] / r23["total"] - 1),
        "blocs_total": len(blocs), "blocs_actifs_2024": sum(b.statut_2024 != "libre" for b in blocs),
        "blocs_actifs_2026": sum(b.statut_2026 != "libre" for b in blocs),
        "attribues_depuis_2025": sum(b.statut_2024 == "libre" and b.statut_2026 != "libre" for b in blocs),
        "cpp_cumules": ind.get("cpp_cumules"), "brent": brent_an.get(2024),
        "decouvertes_2024_2026": Puits.objects.filter(resultat="Découverte").count(),
    }

    return {
        "annees": annees, "kpis": kpis, "insights": insights, "indicateurs": ind,
        "champs": [{"nom": c.nom, "operateur": ops[c.operateur_id].nom if c.operateur_id else None,
                    "statut": c.statut, "fluide": c.fluide, "decouverte": c.annee_decouverte,
                    "mise_prod": c.annee_mise_production, "lon": c.lon, "lat": c.lat, "couleur": c.couleur,
                    "description": c.description, "blocs": [b.code for b in c.blocs.all()],
                    "serie": series.get(c.nom)} for c in champs],
        "ordre_champs": [c.nom for c in champs_prod],
        "total_petrole": tot_pet, "total_gaz": tot_gaz, "matures_petrole": matures,
        "tcam_matures": cagr_mat,
        "gaz_industrie": _p("gaz_industrie", {}), "brent_annuel": brent_an, "marge_sir": marge, "brent_2024": brent_m,
        "recettes": rec_rows, "exports": exports, "imports": imports,
        "brut_local_raffine": _p("brut_local_raffine_2024_tm", {}),
        "cpp_par_an": {str(k): dict(v) for k, v in sorted(cpp_par_an.items())},
        "forages": {k: dict(v) for k, v in forages.items()}, "forages_total": _p("forages_total_dgh", {}),
        "puits": list(Puits.objects.values("nom", "bloc_code", "type", "annee", "resultat", "note")),
        "sismique": _p("sismique", {}), "acteurs": acteurs, "hhi": hhi,
        "evenements": [{"date": e.date.isoformat(), "titre": e.titre, "cat": e.categorie,
                        "cat_label": e.get_categorie_display(), "bloc": e.bloc_code,
                        "description": e.description, "source": e.source} for e in Evenement.objects.all()],
        "objectifs": _p("objectifs", []), "territoire": _p("territoire", []), "cadastre_ancien": _p("cadastre_ancien", {}),
        "blocs": {"type": "FeatureCollection", "features": features},
    }
