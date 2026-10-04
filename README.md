# Tableau de bord du secteur pétrolier amont ivoirien

Dashboard interactif d'analyse du secteur pétrolier amont de la Côte d'Ivoire,
construit avec **Streamlit** et **Plotly**. Il permet d'explorer les 50 blocs
pétroliers du pays : statuts, opérateurs, contrats de partage de production
(CPP), productions de pétrole et de gaz naturel, et ventes de gaz sur la
période 2018-2023.

## Fonctionnalités

- **Indicateurs clés (KPI)** : production de pétrole (Bbls), production de gaz
  naturel (MMSCF), ventes de gaz (MMBTU) et nombre de forages, avec variation
  entre deux années choisies par l'utilisateur.
- **Répartition des blocs par statut** : jauges circulaires des parts de blocs
  en production, en exploration, en négociation et libres.
- **Carte interactive des blocs pétroliers** : carte choroplèthe (Plotly,
  fond CARTO) des contours de blocs issus d'un GeoJSON, colorée par statut,
  avec infobulle détaillée (opérateur, superficie, type de profondeur,
  productions 2023).
- **Base de données personnalisable** : tableau filtrable colonne par colonne
  (numérique, date, catégoriel, texte/regex) et export CSV de la sélection.
- **Analyses graphiques** :
  - analyse univariée (diagramme circulaire et diagramme en barres) sur les
    variables catégorielles et calendaires ;
  - évolution temporelle 2018-2023 des productions et ventes (somme totale ou
    détail par bloc) ;
  - analyse croisée entre deux variables catégorielles (barres groupées ou
    empilées).
- **Filtres globaux** dans la barre latérale : période d'analyse, statut du
  bloc, type de profondeur.

## Stack technique

| Outil | Rôle |
|---|---|
| [Streamlit](https://streamlit.io) | Framework de l'application web |
| [Plotly Express](https://plotly.com/python/) | Graphiques et carte choroplèthe interactifs |
| [pandas](https://pandas.pydata.org) | Préparation et agrégation des données |
| [openpyxl](https://openpyxl.readthedocs.io) | Lecture des fichiers Excel |
| GeoJSON | Contours géographiques des blocs pétroliers |

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
sombre (palette ambre / bleu pétrole) est défini dans
`.streamlit/config.toml`.

## Structure du projet

```
.
├── Oil_Dashboard.py                      # Application Streamlit
├── Base Pétrole finale.xlsx              # Base de données principale
├── GéoJson Blocs pétroliers.json         # Contours des blocs (GeoJSON)
├── Coordonnées géographiques Blocs.xlsx  # Coordonnées sources
├── requirements.txt                      # Dépendances Python
├── .streamlit/
│   └── config.toml                       # Thème de l'application
└── README.md
```

## Déploiement (Streamlit Community Cloud)

1. Rendez-vous sur [share.streamlit.io](https://share.streamlit.io) et connectez-vous avec votre compte GitHub.
2. Cliquez sur **New app**, puis choisissez ce dépôt, la branche à déployer et le fichier principal `Oil_Dashboard.py`.
3. Cliquez sur **Deploy** : l'application est construite puis mise en ligne sur une URL du type `https://<nom-de-l-appli>.streamlit.app`.

> **Version Python** : dans **Advanced settings** (avant le déploiement), choisissez une
> version récente de Python (3.11 ou 3.12), compatible avec les versions minimales
> listées dans `requirements.txt`.

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
