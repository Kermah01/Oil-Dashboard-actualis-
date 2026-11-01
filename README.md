# AMONT·CI — Observatoire de l'amont pétrolier ivoirien

Plateforme Django d'analyse du secteur pétrolier et gazier amont de Côte d'Ivoire.
Données : *Annuaire des statistiques des hydrocarbures de Côte d'Ivoire*, édition 2025 (DGH, exercice 2024),
complété des faits publics 2025-2026 (Calao South, Bubale-1X, FID Baleine phase 3, CPP Petrobras).

## Modules
| Page | Contenu |
|---|---|
| Cockpit | KPI, production par gisement, fil d'actualité, 8 analyses automatiques, recettes, partage des exportations |
| Carte des blocs | Cadastre interactif des 50 blocs : coloration par statut / opérateur / zone / superficie / production / ancienneté, situation 2024 vs 2026, frise animée 1992-2026, fiches bloc et gisement, recherche, filtres, fonds de carte (nuit, bathymétrie, satellite, hors-ligne) |
| Production | Trajectoires par champ, analyse de déclin (Arps exponentiel) des champs matures, gaz, pouvoir calorifique, heatmap des ventes industrielles |
| Exploration | CPP par année et opérateur, forages, taux de succès, sismique, puits 2024-2026, chronologie filtrable |
| Acteurs | Surfaces 2024/2026, indice HHI, parts de production, fiches opérateurs |
| Économie & fiscalité | Recettes TOFE, recettes par baril, taux de prélèvement apparent, paradoxe import/export du brut, élasticité au Brent, marge SIR |
| Simulateur CPP | Modèle de partage de production : cost stop, tranches de profit oil, PETROCI, bonus → government take, VAN, TRI, Brent d'équilibre, sensibilité |
| Perspectives 2035 | Scénarios prudent / central / ambitieux réglables vs objectifs 200 kb/j (2030) et 500 kb/j (2035), gaz, recettes |
| Données & API | Registre des blocs, exports CSV, API JSON/GeoJSON, méthodologie |

## Démarrage local
```bash
python -m venv .venv && source .venv/bin/activate      # Windows : .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py load_amont            # charge toutes les données
python manage.py createsuperuser       # accès au back-office /admin/
python manage.py runserver             # http://127.0.0.1:8000
```

## Mise à jour annuelle (annuaire 2026, etc.)
- Par le back-office `/admin/` (production, recettes, blocs, événements…), ou
- en éditant `amont/seed_data.py` puis `python manage.py load_amont`.

## Géométrie des blocs
Contours issus de la base cartographique du projet (`data/source/`). `python data/build_data.py` régénère
`data/cadastre.geojson`, `data/cadastre_ancien.geojson` et `data/base_blocs.json`, puis `python manage.py load_amont` recharge la base.
Le chargement contrôle chaque contour contre la superficie officielle et signale les écarts.
Un GeoJSON officiel DGH peut aussi être appliqué : `python manage.py load_amont --geojson fichier.geojson` (propriété `code`).

## Déploiement
- **Render** : `render.yaml` prêt (Blueprint). Base PostgreSQL optionnelle via `DATABASE_URL`.
- Tout autre hébergeur Python : `Procfile` (gunicorn + whitenoise).
- Variables : `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_ORIGINS`, `DATABASE_URL` (optionnel).

Les librairies (ECharts 5.5, Leaflet 1.9) et les polices sont embarquées dans `static/vendor/` :
la plateforme fonctionne sur un intranet sans accès Internet (seuls les fonds de carte en ligne nécessitent Internet ;
un fond « Hors-ligne » est fourni).
