"""
Données de référence de la plateforme AMONT·CI.

Sources principales :
  - DGH, Annuaire des statistiques des hydrocarbures de Côte d'Ivoire, édition 2025 (données 2024)
  - Communiqués officiels et presse spécialisée pour les faits 2025-2026 (voir champ `source`)

Toute valeur marquée `estime=True` ou rangée dans une "hypothèse" n'est PAS une statistique officielle.
"""

ANNEES = [2018, 2019, 2020, 2021, 2022, 2023, 2024]

OPERATEURS = [
    # code, nom, pays, type, couleur (identité, pas de sens statistique)
    ("ENI", "Eni Côte d'Ivoire Ltd", "Italie", "Major", "#3987e5"),
    ("PETROCI", "PETROCI Holding", "Côte d'Ivoire", "Compagnie nationale", "#d95926"),
    ("CNR", "CNR International", "Canada / Royaume-Uni", "Indépendant", "#199e70"),
    ("FOXTROT", "Foxtrot International", "—", "Indépendant", "#c98500"),
    ("MURPHY", "Murphy Oil", "États-Unis", "Indépendant", "#d55181"),
    ("TULLOW", "Tullow CI Onshore Ltd", "Royaume-Uni", "Indépendant", "#008300"),
    ("DRAGON", "Dragon Oil", "Émirats arabes unis", "Indépendant", "#9085e9"),
    ("ICE", "ICE Oil & Gas", "—", "Indépendant", "#e66767"),
    ("ELEPHANT", "Elephant Oil", "États-Unis", "Indépendant", "#8a94a6"),
    ("PETROBRAS", "Petrobras", "Brésil", "Compagnie nationale", "#8a94a6"),
]

# --- Blocs ---------------------------------------------------------------------------
# statut_2024 : situation officielle fin 2024 (Annuaire DGH 2025)
# statut_2026 : situation mise à jour avec les faits publics 2025-2026
# superficie : km2 officiels (Tableau 1) pour les blocs en activité ; None => estimée depuis la géométrie
BLOCS_ACTIFS = {
    # code: (operateur, date_cpp, superficie_km2, statut)
    "CI-11": ("PETROCI", "1992-06-27", 77, "production"),
    "CI-27": ("FOXTROT", "1994-12-14", 584, "production"),
    "CI-26": ("CNR", "1995-12-20", 235, "production"),
    "CI-40": ("CNR", "1998-04-09", 175, "production"),
    "CI-101": ("ENI", "2017-03-22", 1565, "production"),
    "CI-205": ("ENI", "2017-03-22", 1271, "exploration"),
    "CI-524": ("TULLOW", "2018-03-01", 261, "exploration"),
    "CI-24": ("DRAGON", "2018-06-01", 821, "exploration"),
    "CI-501": ("ENI", "2019-06-03", 511.96, "exploration"),
    "CI-802": ("ENI", "2021-07-13", 654.81, "production"),
    "CI-401": ("ENI", "2022-03-03", 284.54, "exploration"),
    "CI-801": ("ENI", "2022-03-03", 797.58, "exploration"),
    "CI-803": ("TULLOW", "2022-12-09", 1344.74, "exploration"),
    "CI-102": ("MURPHY", "2023-06-14", 862.91, "exploration"),
    "CI-103": ("MURPHY", "2023-06-14", 703.09, "exploration"),
    "CI-502": ("MURPHY", "2023-06-14", 222.46, "exploration"),
    "CI-709": ("MURPHY", "2023-06-14", 3480.09, "exploration"),
    "CI-531": ("MURPHY", "2023-06-14", 757.93, "exploration"),
    "CI-523": ("PETROCI", "2023-10-02", 325.12, "exploration"),
    "CI-525": ("PETROCI", "2023-10-02", 286.00, "exploration"),
    "CI-705": ("ICE", "2023-11-13", 2289.33, "exploration"),
    "CI-520": ("ELEPHANT", "2024-08-26", 1042.56, "exploration"),
    "CI-521": ("ELEPHANT", "2024-08-26", 1261.90, "exploration"),
    "CI-522": ("ELEPHANT", "2024-08-26", 1227.11, "exploration"),
    "CI-504": ("ENI", "2024-12-31", 398.79, "exploration"),
    "CI-526": ("ENI", "2024-12-31", 2979.08, "exploration"),
    "CI-706": ("ENI", "2024-12-31", 910.83, "exploration"),
    "CI-708": ("ENI", "2024-12-31", 1446.27, "exploration"),
}

BLOCS_LIBRES_2024 = ["CI-12", "CI-301", "CI-302", "CI-500", "CI-503", "CI-513", "CI-518", "CI-519",
                     "CI-600", "CI-601", "CI-602", "CI-603", "CI-604", "CI-605", "CI-700", "CI-701",
                     "CI-702", "CI-703", "CI-704", "CI-707", "CI-710", "CI-804"]

# Blocs attribués après l'annuaire (faits publics 2026)
ATTRIBUTIONS_2026 = {
    **{code: ("PETROBRAS", "2026-09-17",
              "CPP signé le 17/09/2026 (Petrobras 90 % opérateur, PETROCI 10 %), approuvé en Conseil des ministres le 03/06/2026.")
       for code in ["CI-513", "CI-600", "CI-601", "CI-602", "CI-603", "CI-605", "CI-701", "CI-702"]},
    "CI-707": ("ENI", "2025-10-01", "CPP signé avec Eni en octobre 2025 (≈ 2 926 km², 1 000 à 3 000 m d'eau)."),
}

ZONE_PAR_BLOC = {  # 7 onshore / 35 offshore / 8 ultra-profond (répartition DGH)
    **{c: "onshore" for c in ["CI-518", "CI-519", "CI-520", "CI-521", "CI-522", "CI-524", "CI-803"]},
    **{c: "ultra" for c in ["CI-700", "CI-701", "CI-702", "CI-703", "CI-704", "CI-707", "CI-708", "CI-710"]},
}

# --- Champs (gisements) --------------------------------------------------------------
CHAMPS = [
    # nom, blocs, operateur, statut, fluide, annee_decouverte, annee_mise_prod, lon, lat, description, couleur
    ("Baleine", ["CI-101", "CI-802"], "ENI", "production", "Pétrole + gaz associé", 2021, 2023, -3.66, 4.67,
     "Plus grande découverte de l'histoire du pays (sept. 2021). Phase 1 en production le 27/08/2023, "
     "phase 2 le 28/12/2024 ; FID de la phase 3 le 25/05/2026 (≈ 4 Md USD, de 60 000 à 150 000 b/j et de 80 à 200 MMscf/j, "
     "tout le gaz au marché domestique).", "#3987e5"),
    ("Baobab", ["CI-40"], "CNR", "production", "Pétrole + gaz", None, 2005, -4.45, 4.98,
     "Champ mature, 2e producteur de brut en 2024. Campagne sismique OBN (190 km²) fin 2024 pour son redéveloppement.",
     "#d95926"),
    ("Espoir", ["CI-26"], "CNR", "production", "Pétrole + gaz", None, 2002, -4.22, 5.03,
     "Champ mature en déclin, brut exporté.", "#199e70"),
    ("Foxtrot · Mahi · Marlin · Manta", ["CI-27"], "FOXTROT", "production", "Gaz + pétrole", None, 1999, -3.82, 5.09,
     "Pilier gazier du pays : ≈ 74 % de la production de gaz 2024, alimente les centrales électriques.", "#c98500"),
    ("Lion & Panthère", ["CI-11"], "PETROCI", "production", "Pétrole + gaz", None, 1995, -4.03, 5.14,
     "Petit champ côtier opéré par PETROCI ; brut léger (49,4° API) traité par la SIR.", "#d55181"),
    ("Calao", ["CI-205"], "ENI", "evaluation", "Gaz, condensats, pétrole léger", 2024, None, -4.86, 4.80,
     "Découverte du puits Murène-1X (mars 2024), 2e découverte du pays : 1 à 1,5 Md bep estimés. "
     "Cible du Plan directeur gaz (Gas Master Plan) lancé avec la Banque mondiale.", "#9085e9"),
    ("Calao South", ["CI-501"], "ENI", "evaluation", "Gaz et condensats", 2026, None, -4.99, 4.76,
     "Puits Murène South-1X (fév. 2026), 8 km au SO de Murène-1X. Selon Eni : jusqu'à 5 Tcf de gaz et 450 M bbl de "
     "condensats, soit ≈ 1,4 Md bep en place sur CI-501 + CI-205.",
     "#9085e9"),
    ("Bubale", ["CI-709"], "MURPHY", "evaluation", "Pétrole", 2026, None, -5.45, 4.40,
     "Puits Bubale-1X (juin 2026) : ≈ 30 m nets de pétrole sur deux réservoirs. Première découverte de Murphy "
     "après Civette-1X (CI-502, non commercial) et Caracal-1X (CI-102, sec).", "#9085e9"),
]

CHAMP_BLOC_PROD = {  # nom de champ -> clé de série dans les tableaux DGH
    "Lion & Panthère": "CI-11", "Espoir": "CI-26", "Foxtrot · Mahi · Marlin · Manta": "CI-27",
    "Baobab": "CI-40", "Baleine": "CI-101/802",
}

# --- Tableau 4 : production de pétrole brut (bbl) ------------------------------------
PROD_PETROLE = {
    "CI-11": [111520, 170496, 152174, 106959, 161194, 142553, 172665],
    "CI-26": [3107408, 2793656, 2242385, 1613597, 1972562, 1695988, 1627074],
    "CI-27": [599128, 590926, 605950, 540120, 612694, 598573, 573994],
    "CI-40": [7966586, 9639055, 7641883, 6512587, 6554106, 6235621, 5684736],
    "CI-101/802": [0, 0, 0, 0, 0, 2079461, 8096517],
}
# --- Tableau 6 : production de gaz naturel (MMSCF) -----------------------------------
PROD_GAZ = {
    "CI-11": [4160, 5897, 6737, 5746, 4178, 2973, 4405],
    "CI-26": [16068, 13602, 10719, 7718, 8555, 7008, 6541],
    "CI-27": [46624, 50469, 57925, 67836, 75214, 80928, 71007],
    "CI-40": [5044, 6707, 3326, 2487, 2346, 2467, 2163],
    "CI-101/802": [0, 0, 0, 0, 0, 2953, 11816],
}
# --- Tableau 7 : ventes de gaz (MMBTU) ----------------------------------------------
VENTES_GAZ = {
    "CI-11": [3825239, 5733573, 6700014, 5768604, 3918939, 2643721, 4257526],
    "CI-26": [13766202, 11687892, 9453153, 6552920, 7245263, 5941751, 5297606],
    "CI-27": [48108304, 52517916, 60216272, 70778901, 78293281, 83963277, 73621494],
    "CI-40": [3391483, 3851222, 0, 743829, 862610, 701981, 496206],
    "CI-101/802": [0, 0, 0, 0, 0, 435079, 7525170],
}
# --- Tableau 9 : pouvoir calorifique (MMBTU/MMSCF) ----------------------------------
PCS = {
    "CI-11": [1295, 1178, 1181, 1175, 1240, 1232, 1211],
    "CI-26": [1095, 1090, 1103, 1095, 1102, 1103, 1100],
    "CI-27": [1048, 1054, 1053, 1054, 1051, 1049, 1050],
    "CI-40": [1093, 1083, 1089, 1089, 1101, 1103, 1100],
    "CI-101/802": [None, None, None, None, None, 1185, 1188],
}

# --- Tableau 8 : ventes de gaz aux industries (MMSCF / mois) ------------------------
GAZ_INDUSTRIE = {
    2019: [51.739, 50.266, 58.396, 52.047, 60.191, 45.543, 60.071, 63.671, 50.544, 66.052, 62.785, 59.095],
    2020: [62.213, 66.748, 76.989, 80.590, 77.177, 68.820, 69.441, 64.312, 64.201, 86.588, 63.040, 68.332],
    2021: [79.995, 71.614, 88.704, 83.357, 78.239, 95.097, 118.939, 105.497, 118.868, 102.167, 116.947, 118.043],
    2022: [101.301, 97.829, 109.620, 111.463, 111.086, 116.431, 120.283, 131.894, 109.401, 126.925, 114.227, 114.429],
    2023: [95.145, 97.314, 114.030, 107.987, 117.191, 95.937, 119.304, 97.116, 104.143, 114.237, 99.916, 99.754],
    2024: [112.277, 114.938, 110.580, 105.059, 120.788, 107.592, 123.180, 123.995, 117.278, 113.925, 129.545, 133.078],
}

# --- Tableau 10 + 13 : Brent ---------------------------------------------------------
BRENT_2024_MENSUEL = [80.318, 83.927, 85.485, 90.150, 82.048, 82.608, 85.306, 80.906, 74.330, 75.659, 74.472, 73.944]
BRENT_ANNUEL = {2008: 99.25, 2009: 61.51, 2010: 79.40, 2011: 111.00, 2012: 112.00, 2013: 109.00, 2014: 99.00,
                2015: 52.00, 2016: 44.00, 2017: 54.00, 2018: 71.30, 2019: 64.06, 2020: 41.67, 2021: 70.91,
                2022: 101.19, 2023: 82.62, 2024: 80.76}
MARGE_SIR = {2008: 7.38, 2009: 1.25, 2010: 3.26, 2011: 2.20, 2012: 3.30, 2013: 1.00, 2014: 2.10, 2015: 3.30,
             2016: 3.20, 2017: 3.90, 2018: 5.04, 2019: 4.84, 2020: -2.96, 2021: 1.2, 2022: 17.21, 2023: 10.83,
             2024: 5.00}

# --- Tableau 2 : forages 2016-2024 ---------------------------------------------------
FORAGES = [
    # type, bloc, operateur, {annee: nb}
    ("Exploration", "CI-100", "TotalE&P CI", {2017: 1}),
    ("Exploration", "CI-513", "Ophir Energy", {2017: 1}),
    ("Exploration", "CI-527", "Anadarko", {2016: 1, 2017: 1}),
    ("Exploration", "CI-528", "Anadarko", {2016: 1}),
    ("Exploration", "CI-101", "Eni Côte d'Ivoire", {2021: 1}),
    ("Exploration", "CI-205", "Eni Côte d'Ivoire", {2024: 1}),
    ("Exploration", "CI-802", "Eni Côte d'Ivoire", {2022: 1}),
    ("Exploration", "CI-705", "TotalEnergies E&P CI", {2021: 1}),
    ("Évaluation", "CI-103", "Anadarko", {2016: 3, 2017: 1}),
    ("Évaluation", "CI-101", "Eni Côte d'Ivoire", {2022: 2}),
    ("Évaluation", "CI-40", "CNR International", {2019: 1}),
    ("Développement", "CI-27", "Foxtrot International", {2016: 4, 2021: 3, 2022: 3}),
    ("Exploration", "CI-12", "Foxtrot International", {2024: 2}),  # Puma-1X et Guépard-1X (texte DGH)
    ("Développement", "CI-101", "Eni Côte d'Ivoire", {2022: 1}),
    ("Développement", "CI-802", "Eni Côte d'Ivoire", {2023: 1, 2024: 5}),
    ("Développement", "CI-40", "CNR International", {2016: 1, 2018: 3, 2019: 3}),
    ("Développement", "CI-26", "CNR International", {2016: 1}),
]
FORAGES_TOTAL_DGH = {2016: 11, 2017: 4, 2018: 3, 2019: 4, 2020: 0, 2021: 5, 2022: 7, 2023: 1, 2024: 8}

PUITS = [
    # nom, bloc, type, annee, resultat, note
    ("Murène-1X", "CI-205", "Exploration", 2024, "Découverte", "Découverte du gisement Calao"),
    ("Puma-1X", "CI-12", "Exploration", 2024, "Foré", "Foxtrot International"),
    ("Guépard-1X", "CI-12", "Exploration", 2024, "Foré", "Foxtrot International"),
    ("BAL-OP1 à OP4", "CI-802", "Production", 2024, "Achevés", "4 producteurs, phase 2 Baleine"),
    ("BAL-WI09", "CI-802", "Injection d'eau", 2024, "Achevé", "Compte pour la phase 3 Baleine"),
    ("BAL-WI01/03/04", "CI-802", "Injection d'eau", 2024, "En cours", "Phase 2 Baleine"),
    ("BAL-WI02", "CI-802", "Injection d'eau", 2024, "En cours", "Achèvement prévu 2025"),
    ("Civette-1X", "CI-502", "Exploration", 2026, "Non commercial", "Murphy Oil, janv. 2026 : hydrocarbures non commerciaux"),
    ("Caracal-1X", "CI-102", "Exploration", 2026, "Sec", "Murphy Oil, fév. 2026"),
    ("Murène South-1X", "CI-501", "Exploration", 2026, "Découverte", "Calao South (Eni, fév. 2026)"),
    ("Bubale-1X", "CI-709", "Exploration", 2026, "Découverte", "Murphy Oil, juin 2026 (~30 m nets)"),
]

# --- Sismique (fin 2024) -------------------------------------------------------------
SISMIQUE = {"2d_onshore_km": 4644, "2d_offshore_km": 66648.06, "3d_offshore_km2": 92192, "4d_offshore_km2": 709,
            "campagnes_2024": 3, "campagnes_2023": 2}

# --- Tableau 17 : exportations de brut 2024 (bbl) ------------------------------------
EXPORTS_2024 = [
    # champ, bloc, api, total, etat, petroci, prives
    ("Espoir", "CI-26", 31.53, 1499649, 987, 162788, 1335874),
    ("Baobab", "CI-40", 22.63, 5393688, 877622, 365225, 4150841),
    ("Baleine", "CI-101/802", 37.00, 8331188, 796776, 1358661, 6175751),
]
IMPORTS_BRUT_2024 = [
    # pays, brut, raffinerie, bbl
    ("Nigeria", "Forcados", "SIR", 21016990), ("Nigeria", "Egina", "SIR", 951213),
    ("Nigeria", "Escravos", "SIR", 1952652), ("Colombie", "Apiay Blend", "SMB", 2653350),
    ("Colombie", "Vasconia Blend", "SMB", 529200),
]
BRUT_LOCAL_RAFFINE_2024_TM = {"Condensats CI": 37008, "Foxtrot": 4923, "Marlin": 34507, "Lion": 27069 + 909}

# --- Tableaux 50 à 54 : recettes (milliards FCFA) -----------------------------------
RECETTES = {
    "bic_petrole": [39.6, 48.4, 15.6, 21.8, 41.5, 71.2, 96.6],
    "bic_gaz": [47.8, 52.2, 49.8, 53.5, 52.3, 51.8, 149.0],
    "taxe_petrole": [17.0, 20.8, 6.7, 9.3, 16.6, 30.6, 40.0],
    "taxe_gaz": [20.5, 22.4, 21.3, 22.9, 22.4, 22.2, 63.9],
    "bonus": [6.0, 8.1, 0.0, 1.9, 3.6, 6.6, 3.6],
    "total": [130.8, 151.8, 93.4, 109.5, 136.5, 182.4, 353.1],
}
# Taux de change moyen FCFA/USD (moyennes annuelles BCEAO/FMI, arrondies) - utilisés pour les ratios dérivés
FCFA_USD = {2018: 555.7, 2019: 585.9, 2020: 575.6, 2021: 554.5, 2022: 623.8, 2023: 606.6, 2024: 606.6}

INDICATEURS_2024 = {
    "petrole_bopd": 44139, "gaz_mmscfd": 262, "super_m3": 1439327, "gasoil_m3": 1675655, "butane_tm": 749242,
    "prix_super": 875, "prix_gasoil": 715, "part_recettes_produits": 7.4, "part_recettes_brut_gaz": 2.9,
    "cpp_cumules": 65, "blocs_total": 50, "blocs_actifs": 28, "blocs_production": 6, "blocs_exploration": 22,
    "blocs_libres": 22, "puits_2011_2024": 84, "puits_expl_eval": 38, "decouvertes_indices": 12, "puits_dev": 46,
    "elec_part_gaz": 91.5,
}

# --- Objectifs & hypothèses (Perspectives) ------------------------------------------
OBJECTIFS = [
    # annee, petrole_bopd, gaz_mmscfd, libelle, source
    (2028, 200000, 450000 / 1000, "Objectif gouvernemental (AFP, janv. 2025)", "AFP"),
    (2030, 200000, 600, "Plan directeur pétrolier — amont (juin 2025)", "MMPE / AIP"),
    (2035, 500000, 1000, "Plan directeur pétrolier — horizon 2035", "MMPE"),
]

EVENEMENTS = [
    # date, titre, categorie, bloc, description, source
    ("1992-06-27", "CPP du bloc CI-11", "contrat", "CI-11", "Plus ancien CPP encore actif (PETROCI).", "DGH"),
    ("1995-01-01", "Mise en production de Lion & Panthère", "production", "CI-11", "", "DGH"),
    ("1999-01-01", "Premier gaz de Foxtrot (CI-27)", "production", "CI-27", "Le gaz domestique devient le socle de l'électricité.", "DGH"),
    ("2002-01-01", "Mise en production d'Espoir", "production", "CI-26", "", "DGH"),
    ("2005-01-01", "Mise en production de Baobab", "production", "CI-40", "", "DGH"),
    ("2017-03-22", "Eni entre sur CI-101 et CI-205", "contrat", "CI-101", "Signature des CPP qui mèneront à Baleine et Calao.", "DGH"),
    ("2021-07-13", "CPP du bloc CI-802 (Eni)", "contrat", "CI-802", "", "DGH"),
    ("2021-09-01", "Découverte de Baleine", "decouverte", "CI-101", "Plus grande découverte du pays ; 1re découverte commerciale en 20 ans.", "Eni"),
    ("2023-06-14", "Murphy Oil signe 5 CPP", "contrat", "CI-709", "CI-102, CI-103, CI-502, CI-531, CI-709.", "DGH"),
    ("2023-08-27", "Baleine phase 1 : premier pétrole", "production", "CI-101", "Développement accéléré, moins de 2 ans après la découverte.", "DGH"),
    ("2024-03-07", "Découverte de Calao (Murène-1X)", "decouverte", "CI-205", "1 à 1,5 Md bep ; 2e découverte du pays.", "Eni / MMPE"),
    ("2024-07-30", "Relance de l'onshore : 3 CPP Elephant Oil", "contrat", "CI-520", "CI-520/521/522 ; profit oil 52,5 % à l'État.", "Économie ivoirienne"),
    ("2024-12-27", "Foxtrot rend un bloc (CI-12)", "contrat", "CI-12", "Seul bloc rendu en 2024. La DGH ne nomme pas le bloc : CI-12, foré par Foxtrot en 2024 et libre fin 2024, est le seul candidat.", "DGH"),
    ("2024-12-28", "Baleine phase 2 démarre", "production", "CI-802", "50-60 000 b/j attendus contre 35 000 prévus.", "Gouvernement"),
    ("2024-11-28", "Eni signe 4 nouveaux CPP", "contrat", "CI-526", "CI-504, CI-526, CI-706, CI-708, signés au SIREXE 2024 (l'annuaire DGH les date du 31/12/2024). 65 CPP signés depuis 2011.", "Eni / DGH"),
    ("2025-06-19", "Plan directeur : 200 000 b/j en 2030", "politique", None, "Et ≈ 600 millions de pieds cubes de gaz ; au moins 500 000 b/j et plus d'1 milliard de pieds cubes/j en 2035.", "MMPE / AIP"),
    ("2025-10-01", "Eni obtient le bloc CI-707", "contrat", "CI-707", "≈ 2 926 km² par 1 000 à 3 000 m d'eau.", "Eni"),
    ("2026-01-19", "Murphy : Civette-1X (CI-502) non commercial", "forage", "CI-502", "Hydrocarbures non commerciaux ; puis Caracal-1X (CI-102) sec en février.", "Murphy Oil"),
    ("2026-02-16", "Découverte de Calao South (CI-501)", "decouverte", "CI-501", "Gaz et condensats : ≈ 1,4 Md bep en place sur CI-501 + CI-205.", "MMPE / Eni"),
    ("2026-06-03", "8 CPP Petrobras approuvés en Conseil des ministres", "contrat", "CI-600", "CI-513, CI-600 à 603, CI-605, CI-701, CI-702 ; 75 % du bassin sédimentaire désormais attribué.", "Gouvernement"),
    ("2026-09-17", "Petrobras signe ses 8 CPP", "contrat", "CI-600", "Petrobras 90 % (opérateur), PETROCI 10 %.", "Petrobras / energy-pedia"),
    ("2026-05-25", "FID de Baleine phase 3", "production", "CI-101", "≈ 4 Md USD (source ivoirienne) ; Baleine passe de 60 000 à 150 000 b/j et de 80 à 200 MMscf/j ; démarrage sous 36 mois.", "Eni"),
    ("2026-06-22", "Découverte de Bubale-1X (CI-709)", "decouverte", "CI-709", "≈ 30 m nets de pétrole ; Murphy opérateur à 90 %.", "Murphy Oil"),
        ("2026-07-29", "Baleine phase 3 : contrats attribués", "production", "CI-101", "FPSO neuf Altera (90 000 b/j, construit par Wison), système sous-marin SLB OneSubsea, installation Saipem.", "Altera / SLB / Saipem"),
]
