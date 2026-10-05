# Tableau de bord du secteur pétrolier amont ivoirien

Dashboard interactif d'analyse du secteur pétrolier amont de la Côte d'Ivoire,
construit avec **Streamlit**, **Plotly**, **Altair** et **PyECharts**. Il permet
d'explorer les 50 blocs pétroliers du pays : statuts, opérateurs, contrats de
partage de production (CPP), productions de pétrole et de gaz naturel, et ventes
de gaz sur la période 2018-2023.

Application en ligne : <https://civ-oil-dashboard.streamlit.app>

## Fonctionnalités

- **Productions de l'année par rapport à une année de référence** (pétrole en
  Bbls, gaz naturel en MMSCF), période choisie dans la barre latérale
  (2018-2023).
- **Proportion de blocs** en production, en exploration, en négociation et
  libres (anneaux Altair).
- **Carte interactive des blocs pétroliers** : carte choroplèthe Plotly (fond
  OpenStreetMap) des contours de blocs issus d'un GeoJSON, colorée par statut,
  avec infobulle détaillée (opérateur, superficie, type de profondeur,
  productions 2023).
- **Base de données personnalisée** : tableau filtrable colonne par colonne
  (numérique, date, catégoriel, texte/regex).
- **Analyses graphiques** :
  - camembert (PyECharts) et histogramme (Plotly) d'une variable catégorielle ;
  - évolution 2018-2023 des productions et ventes (valeur par bloc ou somme
    totale, PyECharts) ;
  - analyse croisée entre deux variables catégorielles (barres étalées ou
    empilées, réglage dans la barre latérale).

## Stack technique

| Outil | Rôle |
|---|---|
| [Streamlit](https://streamlit.io) | Framework de l'application web |
| [Plotly Express](https://plotly.com/python/) | Carte choroplèthe, histogrammes |
| [Altair](https://altair-viz.github.io) | Anneaux de proportion |
| [PyECharts](https://pyecharts.org) + streamlit-echarts | Camembert, courbes d'évolution |
| streamlit-extras | Style des cartes d'indicateurs |
| [pandas](https://pandas.pydata.org) / [openpyxl](https://openpyxl.readthedocs.io) | Lecture et préparation des données Excel |

Les versions sont **épinglées exactement** (`==`) dans `requirements.txt` :
ce sont les versions testées en local (Python 3.12 et 3.13). Gardez cet
épinglage pour que l'appli en ligne s'affiche comme en local.

## Données

Données publiques sur les blocs pétroliers ivoiriens (Cabinet du Ministre de
l'Économie, du Plan et du Développement) :

- `Base Pétrole finale.xlsx` : base principale — 50 blocs, 51 variables
  (superficie, type de profondeur, opérateurs et partenaires, dates des CPP,
  statut, forages, productions et ventes 2018-2023) ;
- `GéoJson Blocs pétroliers.json` : contours géographiques des blocs ;
- `Coordonnées géographiques Blocs.xlsx` : coordonnées sources ayant servi à
  construire le GeoJSON.

## Installation et lancement

```bash
# 1. Cloner le dépôt
git clone <url-du-depot>
cd Oil-Dashboard-actualis-

# 2. Créer un environnement virtuel (recommandé)
python -m venv .venv
source .venv/bin/activate   # Windows : .venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
streamlit run Oil_Dashboard.py
```

L'application est alors disponible sur `http://localhost:8501`. Le thème
sombre (texte blanc) est défini dans `.streamlit/config.toml` ; l'image de fond
et l'image de la barre latérale sont chargées depuis leurs URL d'origine.

## Structure du projet

```
.
├── Oil_Dashboard.py                      # Application Streamlit
├── Base Pétrole finale.xlsx              # Base de données principale
├── GéoJson Blocs pétroliers.json         # Contours des blocs (GeoJSON)
├── Coordonnées géographiques Blocs.xlsx  # Coordonnées sources
├── requirements.txt                      # Dépendances Python
├── .streamlit/
│   └── config.toml                       # Thème de l'application (sombre)
└── README.md
```

## Déploiement (Streamlit Community Cloud)

1. Rendez-vous sur [share.streamlit.io](https://share.streamlit.io) et connectez-vous avec votre compte GitHub.
2. Cliquez sur **New app**, puis choisissez ce dépôt, la branche à déployer et le fichier principal `Oil_Dashboard.py`.
3. Cliquez sur **Deploy** : l'application est construite puis mise en ligne sur une URL du type `https://<nom-de-l-appli>.streamlit.app`.

> **Version Python** : dans **Advanced settings** (avant le déploiement), choisissez
> Python 3.12 ou 3.13 (versions avec lesquelles `requirements.txt` a été testé).

### Éviter l'hibernation

Streamlit Community Cloud met l'application en veille après environ 12 heures sans
trafic (un visiteur tombe alors sur un écran « l'appli se réveille » pendant
plusieurs dizaines de secondes). Pour l'éviter, ce dépôt contient le workflow
GitHub Actions [`.github/workflows/keep-alive.yml`](.github/workflows/keep-alive.yml)
qui envoie un ping HTTP à l'application toutes les 4 heures (cron `49 */4 * * *`).

Après le déploiement, renseignez l'URL de l'appli dans une variable de dépôt :

1. Sur GitHub : **Settings → Secrets and variables → Actions → Variables → New repository variable**.
2. Name : `APP_URL` — Value : l'URL publique de l'appli (ex. `https://<nom-de-l-appli>.streamlit.app`).

Tant que `APP_URL` n'est pas définie, le workflow se termine sans rien faire (et sans
échouer). À noter : GitHub désactive les workflows planifiés après 60 jours sans activité
sur le dépôt ; il suffit alors de le relancer une fois manuellement via l'onglet
**Actions → Keep-alive Streamlit → Run workflow**.

Alternative sans GitHub Actions : créer un moniteur HTTP(S) gratuit sur
[UptimeRobot](https://uptimerobot.com) qui interroge l'URL de l'appli toutes les 5 minutes.
