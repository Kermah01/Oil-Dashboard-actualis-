# -*- coding: utf-8 -*-
"""Tableau de bord du secteur pétrolier amont ivoirien.

Dashboard Streamlit d'exploration des blocs pétroliers de Côte d'Ivoire :
indicateurs de production, carte interactive des blocs, base de données
filtrable et analyses graphiques (univariées, temporelles et croisées).
"""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_string_dtype,
)

# ---------------------------------------------------------------------------
# Configuration générale
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Secteur pétrolier ivoirien",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
FICHIER_BASE = BASE_DIR / "Base Pétrole finale.xlsx"
FICHIER_GEOJSON = BASE_DIR / "GéoJson Blocs pétroliers.json"

ANNEES = list(range(2018, 2024))

ORDRE_MOIS = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]
NOM_MOIS = dict(enumerate(ORDRE_MOIS, start=1))

# Palette validée pour fond sombre (identité des séries) — contrôlée avec le
# validateur dataviz contre la surface sombre #101722 (bande de luminosité,
# plancher de chroma, séparation daltonisme, plancher vision normale, contraste).
PALETTE = [
    "#3987e5", "#d95926", "#199e70", "#c98500",
    "#d55181", "#008300", "#9085e9", "#e66767",
] + list(px.colors.qualitative.Safe)

# Statuts actifs : trio validé toutes-paires sur #101722 ; « Libre » est une
# classe neutre (aucune activité) rendue en gris volontairement désaturé,
# séparée d'au moins ΔE 16 de chaque statut actif, toujours nommée en légende
# et dans l'infobulle (jamais portée par la couleur seule).
COULEURS_STATUT = {
    "En activité - production": "#199e70",
    "En activité - exploration": "#3987e5",
    "En activité - négociation": "#d95926",
    "Libre": "#a3adba",
}

# Jetons de design — ambiance « pétrole profond / ambre incandescent »
COULEUR_FOND = "#05080d"          # noir pétrole
COULEUR_SURFACE = "#101722"       # surface des cartes de verre
COULEUR_TEXTE = "#eef2f8"
COULEUR_TEXTE_2 = "#aab4c4"
COULEUR_GRILLE = "rgba(238,242,248,0.07)"
COULEUR_AXE = "rgba(238,242,248,0.16)"
COULEUR_NEUTRE = "#1a2230"        # anneau de fond des jauges
AMBRE = "#f6a21e"
AMBRE_VIF = "#ffc24d"
CUIVRE = "#c87f45"

POLICE_TEXTE = "Inter, 'Segoe UI', sans-serif"
POLICE_TITRE = "Sora, Inter, sans-serif"

# Colonnes de dates exploitées pour dériver mois / année
COLONNES_DATES = [
    "Date de signature du 1er CPP",
    "Date de la 2ème signature du CPP",
    "Date de fin de validité d'exploration 1",
    "Date de fin de validité d'exploration 2",
    "Date de fin de validité exploitation 1",
]

# Correction de coquilles dans les intitulés de colonnes (affichage uniquement,
# le fichier source reste inchangé)
RENOMMAGE_COLONNES = {
    "Superfice (en Km²)": "Superficie (en km²)",
    "Opérateur1": "Opérateur 1",
    "Patenaires (hors PETROCI)": "Partenaires (hors PETROCI)",
    "Patenaires CPP 2 (hors PETROCI)": "Partenaires CPP 2 (hors PETROCI)",
    "Patenaires CPP 3 (hors PETROCI)": "Partenaires CPP 3 (hors PETROCI)",
}


# ---------------------------------------------------------------------------
# Thème visuel : CSS immersif injecté sur toute l'application
# ---------------------------------------------------------------------------
def inject_css() -> None:
    """Injecte le thème « pétrole profond » : fond animé, verre, typographie."""
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg-0: #05080d;
    --bg-1: #0a1018;
    --bg-chaud: #140d05;
    --surface: #101722;
    --verre: rgba(15, 22, 33, 0.55);
    --verre-bord: rgba(246, 162, 30, 0.14);
    --verre-bord-vif: rgba(246, 162, 30, 0.38);
    --ink: #eef2f8;
    --ink-2: #aab4c4;
    --ink-3: #7d8899;
    --ambre: #f6a21e;
    --ambre-vif: #ffc24d;
    --cuivre: #c87f45;
    --or: #e8c069;
}

html, body, .stApp, [class*="css"] {
    font-family: Inter, 'Segoe UI', sans-serif;
}

/* ---- Fond pleine page : nappe de pétrole animée ---- */
.stApp {
    background: linear-gradient(165deg, var(--bg-0) 0%, var(--bg-1) 46%, var(--bg-chaud) 100%);
    background-size: 160% 160%;
    animation: nappe 36s ease-in-out infinite alternate;
    color: var(--ink);
}
@keyframes nappe {
    0%   { background-position: 0% 0%; }
    100% { background-position: 100% 100%; }
}

/* Halos ambrés / cuivre en mouvement lent */
.stApp::before {
    content: "";
    position: fixed;
    inset: -25%;
    z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(circle at 18% 22%, rgba(246, 162, 30, 0.16), transparent 42%),
        radial-gradient(circle at 82% 72%, rgba(200, 127, 69, 0.14), transparent 46%),
        radial-gradient(circle at 65% 12%, rgba(57, 135, 229, 0.08), transparent 38%),
        radial-gradient(circle at 35% 85%, rgba(232, 192, 105, 0.07), transparent 40%);
    filter: blur(70px);
    animation: halos 28s ease-in-out infinite alternate;
    will-change: transform;
}
@keyframes halos {
    0%   { transform: translate3d(-3%, -2%, 0) scale(1) rotate(0deg); }
    50%  { transform: translate3d(3%, 4%, 0) scale(1.12) rotate(4deg); }
    100% { transform: translate3d(-2%, 2%, 0) scale(1.04) rotate(-3deg); }
}

/* Vignette radiale : profondeur de champ */
.stApp::after {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background: radial-gradient(ellipse 120% 90% at 50% 18%, transparent 55%, rgba(2, 4, 8, 0.55) 100%);
}

/* Le contenu passe au-dessus des couches décoratives */
.stApp > header, .stMain, section[data-testid="stSidebar"] {
    position: relative;
    z-index: 1;
}

@media (prefers-reduced-motion: reduce) {
    .stApp, .stApp::before { animation: none; }
}

/* ---- En-tête Streamlit transparent ---- */
header[data-testid="stHeader"] {
    background: transparent;
}

/* ---- Hero ---- */
.hero {
    padding: 2.2rem 0 0.6rem 0;
}
.hero-kicker {
    font-family: Sora, Inter, sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    color: var(--ambre);
    margin-bottom: 0.9rem;
}
.hero-kicker::before {
    content: "";
    display: inline-block;
    width: 2.2rem;
    height: 1px;
    background: linear-gradient(90deg, var(--ambre), transparent);
    vertical-align: middle;
    margin-right: 0.8rem;
}
.hero-titre {
    font-family: Sora, Inter, sans-serif;
    font-size: clamp(2rem, 4.2vw, 3.3rem);
    font-weight: 800;
    line-height: 1.12;
    margin: 0 0 0.8rem 0;
    background: linear-gradient(100deg, #fdf6e9 8%, var(--ambre-vif) 42%, var(--ambre) 62%, var(--cuivre) 95%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    color: var(--ambre-vif); /* repli si background-clip indisponible */
}
.hero-sous-titre {
    color: var(--ink-2);
    font-size: 1.02rem;
    max-width: 46rem;
    line-height: 1.6;
    margin-bottom: 1.3rem;
}
.hero-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
}
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.42rem 0.95rem;
    border-radius: 999px;
    font-size: 0.86rem;
    font-weight: 600;
    color: var(--ink);
    background: var(--verre);
    border: 1px solid var(--verre-bord);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.35);
}
.badge .puce {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--ambre);
    box-shadow: 0 0 10px rgba(246, 162, 30, 0.9);
}
.badge--or { border-color: var(--verre-bord-vif); }

/* ---- Titres de section ---- */
.section-titre {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 2.6rem 0 0.4rem 0;
}
.section-titre .barre {
    width: 4px;
    height: 1.6rem;
    border-radius: 2px;
    background: linear-gradient(180deg, var(--ambre-vif), var(--cuivre));
    box-shadow: 0 0 12px rgba(246, 162, 30, 0.55);
}
.section-titre h2 {
    font-family: Sora, Inter, sans-serif;
    font-size: 1.32rem;
    font-weight: 700;
    color: var(--ink);
    margin: 0;
    padding: 0;
}
.section-sous-titre {
    color: var(--ink-3);
    font-size: 0.88rem;
    margin: 0.1rem 0 1rem 0.95rem;
}

/* ---- Cartes KPI (st.metric) en verre ---- */
div[data-testid="stMetric"] {
    position: relative;
    overflow: hidden;
    background: var(--verre);
    border: 1px solid var(--verre-bord) !important;
    border-radius: 16px;
    padding: 1.1rem 1.2rem;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}
div[data-testid="stMetric"]::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--ambre), transparent);
    opacity: 0.55;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: var(--verre-bord-vif) !important;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5), 0 0 24px rgba(246, 162, 30, 0.12);
}
div[data-testid="stMetric"] label p {
    color: var(--ink-2) !important;
    font-size: 0.85rem !important;
    font-weight: 600;
    letter-spacing: 0.02em;
}
div[data-testid="stMetricValue"] {
    font-family: Sora, Inter, sans-serif;
    font-weight: 700;
    font-size: 1.45rem !important;
    color: var(--ink);
    white-space: normal;
}
div[data-testid="stMetricValue"] div,
div[data-testid="stMetricDelta"] div,
div[data-testid="stMetricLabel"] div,
div[data-testid="stMetricLabel"] p {
    overflow: visible !important;
    text-overflow: clip !important;
    white-space: normal !important;
}
div[data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
}

/* ---- Cadres de verre appliqués via st.container(key=...) ---- */
.st-key-cadre_carte, .st-key-cadre_donnees,
.st-key-cadre_carte div[data-testid="stVerticalBlockBorderWrapper"],
.st-key-cadre_donnees div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--verre);
    border: 1px solid var(--verre-bord) !important;
    border-radius: 18px;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    box-shadow: 0 14px 40px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.04);
}
/* Évite le double cadre : seul le niveau extérieur porte le verre */
.st-key-cadre_carte div[data-testid="stVerticalBlockBorderWrapper"],
.st-key-cadre_donnees div[data-testid="stVerticalBlockBorderWrapper"] {
    background: transparent;
    border: none !important;
    box-shadow: none;
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
}

/* ---- Graphiques Plotly : carte de verre ---- */
div[data-testid="stPlotlyChart"] {
    background: var(--verre);
    border: 1px solid var(--verre-bord);
    border-radius: 16px;
    padding: 0.55rem;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 10px 32px rgba(0, 0, 0, 0.38);
    transition: border-color 0.25s ease, box-shadow 0.25s ease;
}
div[data-testid="stPlotlyChart"]:hover {
    border-color: var(--verre-bord-vif);
    box-shadow: 0 14px 40px rgba(0, 0, 0, 0.5), 0 0 28px rgba(246, 162, 30, 0.10);
}
/* La carte géographique vit déjà dans un cadre : pas de double verre */
.st-key-cadre_carte div[data-testid="stPlotlyChart"] {
    background: transparent;
    border: none;
    padding: 0;
    box-shadow: none;
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
    border-radius: 12px;
    overflow: hidden;
}

/* ---- Barre latérale assortie ---- */
section[data-testid="stSidebar"] {
    background: linear-gradient(185deg, rgba(10, 15, 23, 0.92), rgba(13, 15, 12, 0.94));
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border-right: 1px solid var(--verre-bord);
}
section[data-testid="stSidebar"] h1 {
    font-family: Sora, Inter, sans-serif;
    background: linear-gradient(95deg, #fdf6e9, var(--ambre-vif) 55%, var(--cuivre));
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    color: var(--ambre-vif);
}

/* ---- Boutons en dégradé ambre → cuivre ---- */
div[data-testid="stDownloadButton"] button,
div[data-testid="stButton"] button {
    background: linear-gradient(120deg, var(--ambre-vif), var(--ambre) 55%, var(--cuivre));
    color: #1a1104 !important;
    font-weight: 700;
    border: none;
    border-radius: 12px;
    padding: 0.6rem 1.3rem;
    box-shadow: 0 6px 20px rgba(246, 162, 30, 0.25);
    transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
}
div[data-testid="stDownloadButton"] button:hover,
div[data-testid="stButton"] button:hover {
    transform: translateY(-2px);
    filter: brightness(1.06);
    box-shadow: 0 10px 28px rgba(246, 162, 30, 0.4);
}
div[data-testid="stDownloadButton"] button:active,
div[data-testid="stButton"] button:active {
    transform: translateY(0);
}
div[data-testid="stDownloadButton"] button p,
div[data-testid="stButton"] button p {
    color: #1a1104 !important;
}

/* ---- Tableau de données ---- */
div[data-testid="stDataFrame"] {
    border: 1px solid var(--verre-bord);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}

/* ---- Divers ---- */
hr { border-color: rgba(238, 242, 248, 0.08); }
div[data-testid="stCaptionContainer"] { color: var(--ink-3); }
.pied-page {
    text-align: center;
    color: var(--ink-3);
    font-size: 0.84rem;
    padding: 1.6rem 0 0.6rem 0;
}
.pied-page .goutte { color: var(--ambre); }
</style>
        """,
        unsafe_allow_html=True,
    )


def enregistrer_template_plotly() -> None:
    """Déclare et active le gabarit Plotly assorti au thème sombre ambré."""
    pio.templates["petrole_profond"] = go.layout.Template(
        layout=go.Layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family=POLICE_TEXTE, color=COULEUR_TEXTE, size=13),
            title=dict(
                font=dict(family=POLICE_TITRE, size=16, color=COULEUR_TEXTE),
                x=0.02,
                xanchor="left",
            ),
            colorway=PALETTE,
            hoverlabel=dict(
                bgcolor="rgba(8,13,20,0.94)",
                bordercolor="rgba(246,162,30,0.45)",
                font=dict(family=POLICE_TEXTE, color=COULEUR_TEXTE, size=12),
            ),
            legend=dict(
                bgcolor="rgba(0,0,0,0)",
                font=dict(color=COULEUR_TEXTE_2, size=11.5),
                title=dict(font=dict(color=COULEUR_TEXTE_2)),
            ),
            xaxis=dict(
                gridcolor=COULEUR_GRILLE,
                zerolinecolor=COULEUR_AXE,
                linecolor=COULEUR_AXE,
                tickfont=dict(color=COULEUR_TEXTE_2),
                title=dict(font=dict(color=COULEUR_TEXTE_2)),
            ),
            yaxis=dict(
                gridcolor=COULEUR_GRILLE,
                zerolinecolor=COULEUR_AXE,
                linecolor=COULEUR_AXE,
                tickfont=dict(color=COULEUR_TEXTE_2),
                title=dict(font=dict(color=COULEUR_TEXTE_2)),
            ),
        )
    )
    pio.templates.default = "petrole_profond"


def titre_section(texte: str, sous_titre: str | None = None) -> None:
    """Affiche un titre de section avec barre lumineuse ambrée."""
    st.markdown(
        f'<div class="section-titre"><span class="barre"></span>'
        f"<h2>{texte}</h2></div>",
        unsafe_allow_html=True,
    )
    if sous_titre:
        st.markdown(
            f'<p class="section-sous-titre">{sous_titre}</p>',
            unsafe_allow_html=True,
        )


inject_css()
enregistrer_template_plotly()


# ---------------------------------------------------------------------------
# Chargement et préparation des données (mis en cache)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Chargement de la base pétrole…")
def charger_base() -> pd.DataFrame:
    """Charge la base Excel et dérive les variables calendaires."""
    df = pd.read_excel(FICHIER_BASE)
    df = df.rename(columns=RENOMMAGE_COLONNES)

    # Harmonisation légère des libellés (espaces parasites, casse)
    df["Type de profondeur"] = (
        df["Type de profondeur"].str.strip().replace({"onshore": "Onshore"})
    )

    for col in COLONNES_DATES:
        dates = pd.to_datetime(df[col], errors="coerce")
        suffixe = col.removeprefix("Date ")
        df[f"Mois {suffixe}"] = pd.Categorical(
            dates.dt.month.map(NOM_MOIS), categories=ORDRE_MOIS, ordered=True
        )
        df[f"Année {suffixe}"] = dates.dt.year.astype("Int64")
    return df


@st.cache_data(show_spinner=False)
def charger_geojson() -> dict:
    """Charge le GeoJSON des contours de blocs pétroliers."""
    with open(FICHIER_GEOJSON, encoding="utf-8") as fichier:
        return json.load(fichier)


VARIABLES_SUFFIXES = [col.removeprefix("Date ") for col in COLONNES_DATES]
VARIABLES_CATEGORIELLES = (
    [
        "Statut du bloc",
        "Type de profondeur",
        "Opérateur 1",
        "Opérateur le plus récent",
        "Partenaires (hors PETROCI)",
        "Opérateur CPP 2",
        "Partenaires CPP 2 (hors PETROCI)",
        "Opérateur CPP 3",
        "Partenaires CPP 3 (hors PETROCI)",
    ]
    + [f"Mois {s}" for s in VARIABLES_SUFFIXES]
    + [f"Année {s}" for s in VARIABLES_SUFFIXES]
)

GRANDEURS_TEMPORELLES = {
    "Production de pétrole (Bbls)": [f"Prod. Pétrole {a} Bbls" for a in ANNEES],
    "Production de gaz naturel (MMSCF)": [f"Prod Gaz N. {a} MMSCF" for a in ANNEES],
    "Vente de gaz naturel (MMBTU)": [f"Vente Gaz N. {a} MMBTU" for a in ANNEES],
}


# ---------------------------------------------------------------------------
# Aides de mise en forme
# ---------------------------------------------------------------------------
def fmt_fr(valeur: float, decimales: int = 0) -> str:
    """Formate un nombre avec séparateur de milliers à la française."""
    return f"{valeur:,.{decimales}f}".replace(",", " ").replace(".", ",")


def styliser(fig: go.Figure, hauteur: int = 420) -> go.Figure:
    """Applique les réglages communs (le gabarit « petrole_profond » fait le reste)."""
    fig.update_layout(
        height=hauteur,
        margin=dict(l=10, r=24, t=56, b=16),
    )
    return fig


def jauge_donut(pourcentage: float, libelle: str, couleur: str) -> go.Figure:
    """Petit anneau de progression affichant une part en pourcentage."""
    fig = go.Figure(
        go.Pie(
            values=[pourcentage, 100 - pourcentage],
            hole=0.72,
            marker=dict(colors=[couleur, COULEUR_NEUTRE]),
            textinfo="none",
            sort=False,
            direction="clockwise",
            hoverinfo="skip",
        )
    )
    fig.add_annotation(
        text=f"<b>{pourcentage:.0f} %</b>",
        showarrow=False,
        font=dict(family=POLICE_TITRE, size=20, color=COULEUR_TEXTE),
    )
    fig.update_layout(
        showlegend=False,
        height=180,
        margin=dict(l=6, r=6, t=34, b=6),
        paper_bgcolor="rgba(0,0,0,0)",
        title=dict(
            text=libelle,
            x=0.5,
            xanchor="center",
            font=dict(family=POLICE_TEXTE, size=13, color=COULEUR_TEXTE_2),
        ),
    )
    return fig


# ---------------------------------------------------------------------------
# Données
# ---------------------------------------------------------------------------
df = charger_base()
geojson_blocs = charger_geojson()


# ---------------------------------------------------------------------------
# Barre latérale : filtres
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("Pétrole CI")
    st.caption("Secteur pétrolier amont de la Côte d'Ivoire")
    st.divider()

    st.subheader("Filtres")

    periode = st.select_slider(
        "Période d'analyse (année de référence → année étudiée)",
        options=ANNEES,
        value=(2022, 2023),
    )
    annee_ref, annee_etude = periode

    statuts = st.multiselect(
        "Statut du bloc",
        options=sorted(df["Statut du bloc"].dropna().unique()),
        default=sorted(df["Statut du bloc"].dropna().unique()),
    )
    profondeurs = st.multiselect(
        "Type de profondeur",
        options=sorted(df["Type de profondeur"].dropna().unique()),
        default=sorted(df["Type de profondeur"].dropna().unique()),
    )

    st.divider()
    st.caption(
        "Source : Cabinet du Ministre de l'Économie, du Plan et du "
        "Développement — données publiques sur les blocs pétroliers ivoiriens."
    )

df_filtre = df[
    df["Statut du bloc"].isin(statuts) & df["Type de profondeur"].isin(profondeurs)
]

# ---------------------------------------------------------------------------
# En-tête : hero immersif
# ---------------------------------------------------------------------------
st.markdown(
    f"""
<div class="hero">
  <div class="hero-kicker">Côte d'Ivoire · Énergie &amp; Hydrocarbures</div>
  <h1 class="hero-titre">Secteur pétrolier amont&nbsp;ivoirien</h1>
  <p class="hero-sous-titre">
    Exploration interactive des blocs pétroliers de Côte d'Ivoire :
    production, statuts des blocs, cartographie et analyses croisées
    sur la période 2018-2023.
  </p>
  <div class="hero-badges">
    <span class="badge badge--or"><span class="puce"></span>
      Comparaison {annee_etude} vs {annee_ref}</span>
    <span class="badge"><span class="puce"></span>
      {len(df_filtre)} bloc(s) sélectionné(s) sur {len(df)}</span>
    <span class="badge"><span class="puce"></span>
      Données publiques 2018-2023</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Indicateurs clés
# ---------------------------------------------------------------------------
titre_section(
    f"Indicateurs clés {annee_etude}",
    f"Évolutions exprimées par rapport à l'année de référence {annee_ref}.",
)

prod_petrole = df_filtre[f"Prod. Pétrole {annee_etude} Bbls"].sum()
delta_petrole = prod_petrole - df_filtre[f"Prod. Pétrole {annee_ref} Bbls"].sum()
prod_gaz = df_filtre[f"Prod Gaz N. {annee_etude} MMSCF"].sum()
delta_gaz = prod_gaz - df_filtre[f"Prod Gaz N. {annee_ref} MMSCF"].sum()
vente_gaz = df_filtre[f"Vente Gaz N. {annee_etude} MMBTU"].sum()
delta_vente = vente_gaz - df_filtre[f"Vente Gaz N. {annee_ref} MMBTU"].sum()
forages = df_filtre[f"Nbre de forages {annee_etude}"].sum()
delta_forages = forages - df_filtre[f"Nbre de forages {annee_ref}"].sum()

kpi = st.columns(4, gap="medium")
kpi[0].metric(
    "Production de pétrole",
    f"{fmt_fr(prod_petrole / 1e6, 2)} M Bbls",
    delta=f"{fmt_fr(delta_petrole)} Bbls",
    border=True,
)
kpi[1].metric(
    "Production de gaz",
    f"{fmt_fr(prod_gaz / 1e3, 2)} K MMSCF",
    delta=f"{fmt_fr(delta_gaz)} MMSCF",
    border=True,
)
kpi[2].metric(
    "Vente de gaz naturel",
    f"{fmt_fr(vente_gaz / 1e6, 2)} M MMBTU",
    delta=f"{fmt_fr(delta_vente)} MMBTU",
    border=True,
)
kpi[3].metric(
    "Forages réalisés",
    fmt_fr(forages),
    delta=f"{fmt_fr(delta_forages)} forage(s)",
    border=True,
)

# ---------------------------------------------------------------------------
# Répartition des blocs par statut
# ---------------------------------------------------------------------------
titre_section(
    "Répartition des blocs par statut",
    "Parts calculées sur l'ensemble des blocs de la base.",
)

donuts = st.columns(4, gap="medium")
definitions_donuts = [
    ("En activité - production", "Blocs en production"),
    ("En activité - exploration", "Blocs en exploration"),
    ("En activité - négociation", "Blocs en négociation"),
    ("Libre", "Blocs libres"),
]
for colonne, (statut, libelle) in zip(donuts, definitions_donuts):
    part = 100 * (df["Statut du bloc"] == statut).mean()
    colonne.plotly_chart(
        jauge_donut(part, libelle, COULEURS_STATUT[statut]),
        width="stretch",
        key=f"donut_{statut}",
    )

# ---------------------------------------------------------------------------
# Carte des blocs pétroliers
# ---------------------------------------------------------------------------
titre_section(
    "Carte des blocs pétroliers",
    "Survolez un bloc pour consulter son opérateur, sa superficie et sa production.",
)

df_carte = df_filtre.dropna(subset=["Blocs"])
fig_carte = px.choropleth_map(
    df_carte,
    geojson=geojson_blocs,
    locations="Blocs",
    featureidkey="properties.name",
    color="Statut du bloc",
    color_discrete_map=COULEURS_STATUT,
    category_orders={"Statut du bloc": list(COULEURS_STATUT)},
    map_style="carto-darkmatter",
    zoom=6.1,
    center={"lat": 4.6, "lon": -5.1},
    opacity=0.65,
    custom_data=[
        df_carte["Blocs"],
        df_carte["Opérateur le plus récent"].fillna("Non attribué"),
        df_carte["Superficie (en km²)"],
        df_carte["Type de profondeur"],
        df_carte["Prod. Pétrole 2023 Bbls"],
        df_carte["Prod Gaz N. 2023 MMSCF"],
    ],
)
fig_carte.update_traces(
    hovertemplate=(
        "<b>Bloc %{customdata[0]}</b><br>"
        "Opérateur le plus récent : %{customdata[1]}<br>"
        "Superficie : %{customdata[2]:,.0f} km²<br>"
        "Type de profondeur : %{customdata[3]}<br>"
        "Production de pétrole 2023 : %{customdata[4]:,.0f} Bbls<br>"
        "Production de gaz 2023 : %{customdata[5]:,.0f} MMSCF"
        "<extra></extra>"
    )
)
fig_carte.update_layout(
    height=560,
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family=POLICE_TEXTE, color=COULEUR_TEXTE),
    legend=dict(
        title="Statut du bloc",
        bgcolor="rgba(8,13,20,0.82)",
        bordercolor="rgba(246,162,30,0.25)",
        borderwidth=1,
        x=0.012,
        y=0.985,
    ),
)
with st.container(border=True, key="cadre_carte"):
    st.plotly_chart(fig_carte, width="stretch")
    st.caption(
        "Les blocs sans contour géographique référencé dans le GeoJSON "
        "n'apparaissent pas sur la carte."
    )

# ---------------------------------------------------------------------------
# Base de données personnalisable
# ---------------------------------------------------------------------------
titre_section(
    "Base de données personnalisée",
    "Filtrez colonne par colonne puis exportez votre sélection au format CSV.",
)


def filtrer_dataframe(donnees: pd.DataFrame) -> pd.DataFrame:
    """Ajoute une interface de filtrage colonne par colonne au tableau."""
    activer = st.checkbox("Ajouter des filtres sur les colonnes")
    if not activer:
        return donnees

    donnees = donnees.copy()
    colonnes_choisies = st.multiselect(
        "Colonnes à utiliser comme filtres", donnees.columns
    )
    for colonne in colonnes_choisies:
        serie = donnees[colonne].dropna()
        if serie.empty:
            st.info(f"La colonne « {colonne} » ne contient aucune valeur.")
            continue

        if is_numeric_dtype(serie):
            borne_min, borne_max = float(serie.min()), float(serie.max())
            if borne_min == borne_max:
                continue
            bornes = st.slider(
                f"Valeurs de « {colonne} »",
                min_value=borne_min,
                max_value=borne_max,
                value=(borne_min, borne_max),
            )
            donnees = donnees[donnees[colonne].between(*bornes)]
        elif is_datetime64_any_dtype(serie):
            plage = st.date_input(
                f"Plage de dates de « {colonne} »",
                value=(serie.min(), serie.max()),
            )
            if len(plage) == 2:
                debut, fin = map(pd.to_datetime, plage)
                donnees = donnees[donnees[colonne].between(debut, fin)]
        elif (
            isinstance(donnees[colonne].dtype, pd.CategoricalDtype)
            or is_string_dtype(serie)
            and serie.nunique() < 100
        ):
            modalites = sorted(serie.unique().astype(str))
            choix = st.multiselect(
                f"Valeurs de « {colonne} »", modalites, default=modalites
            )
            donnees = donnees[donnees[colonne].astype(str).isin(choix)]
        else:
            motif = st.text_input(f"Texte ou expression régulière dans « {colonne} »")
            if motif:
                donnees = donnees[
                    donnees[colonne].astype(str).str.contains(motif, na=False)
                ]
    return donnees


with st.container(border=True, key="cadre_donnees"):
    df_personnalise = filtrer_dataframe(df_filtre)
    st.dataframe(df_personnalise, width="stretch")
    st.download_button(
        "Télécharger la sélection (CSV)",
        df_personnalise.to_csv(index=False).encode("utf-8-sig"),
        file_name="blocs_petroliers_selection.csv",
        mime="text/csv",
    )

# ---------------------------------------------------------------------------
# Analyses graphiques
# ---------------------------------------------------------------------------
titre_section(
    "Analyses graphiques",
    "Analyses univariées, évolutions temporelles et croisements de variables.",
)

# --- Analyse univariée -----------------------------------------------------
st.markdown("#### Analyse univariée")
col_pie, col_bar = st.columns(2, gap="medium")

with col_pie:
    variable_pie = st.selectbox(
        "Variable du diagramme circulaire",
        VARIABLES_CATEGORIELLES,
        index=2,
        key="variable_pie",
    )
    comptes = (
        df_filtre[variable_pie]
        .value_counts()
        .rename_axis("Modalité")
        .reset_index(name="Effectif")
    )
    fig_pie = px.pie(
        comptes,
        names="Modalité",
        values="Effectif",
        hole=0.45,
        title=f"Répartition — {variable_pie}",
        color_discrete_sequence=PALETTE,
    )
    fig_pie.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>%{value} bloc(s) — %{percent}<extra></extra>",
    )
    st.plotly_chart(styliser(fig_pie, hauteur=440), width="stretch")

with col_bar:
    variable_bar = st.selectbox(
        "Variable du diagramme en barres",
        VARIABLES_CATEGORIELLES,
        index=1,
        key="variable_bar",
    )
    fig_bar = px.histogram(
        df_filtre,
        x=variable_bar,
        color=variable_bar,
        title=f"Effectifs — {variable_bar}",
        color_discrete_sequence=PALETTE,
    )
    if variable_bar.startswith("Mois "):
        fig_bar.update_xaxes(categoryorder="array", categoryarray=ORDRE_MOIS)
    fig_bar.update_layout(showlegend=False, yaxis_title="Nombre de blocs")
    st.plotly_chart(styliser(fig_bar, hauteur=440), width="stretch")

# --- Évolution temporelle ---------------------------------------------------
st.markdown("#### Évolution de la production et des ventes (2018-2023)")

param_evo = st.columns((3, 2), gap="medium")
grandeur = param_evo[0].selectbox(
    "Grandeur analysée", list(GRANDEURS_TEMPORELLES)
)
mode_affichage = param_evo[1].radio(
    "Mode d'affichage",
    ["Somme totale", "Détail par bloc"],
    horizontal=True,
)

colonnes_grandeur = GRANDEURS_TEMPORELLES[grandeur]
df_evolution = (
    df_filtre[["Blocs"] + colonnes_grandeur]
    .set_axis(["Blocs"] + [str(a) for a in ANNEES], axis=1)
    .melt(id_vars="Blocs", var_name="Année", value_name="Valeur")
)
df_evolution = df_evolution[df_evolution["Valeur"] > 0]

if df_evolution.empty:
    st.warning(
        f"Aucune donnée disponible pour « {grandeur} » avec les filtres actuels."
    )
else:
    if mode_affichage == "Somme totale":
        df_trace = df_evolution.groupby("Année", as_index=False)["Valeur"].sum()
        fig_evolution = px.line(
            df_trace,
            x="Année",
            y="Valeur",
            markers=True,
            title=f"{grandeur} — somme totale",
        )
    else:
        fig_evolution = px.line(
            df_evolution.sort_values("Année"),
            x="Année",
            y="Valeur",
            color="Blocs",
            markers=True,
            title=f"{grandeur} — détail par bloc",
            color_discrete_sequence=PALETTE,
        )
    fig_evolution.update_traces(line=dict(width=2), marker=dict(size=8))
    fig_evolution.update_layout(yaxis_title=grandeur, xaxis_title="Année")
    st.plotly_chart(styliser(fig_evolution, hauteur=480), width="stretch")

# --- Analyse croisée ---------------------------------------------------------
st.markdown("#### Analyse croisée entre variables catégorielles")

param_croise = st.columns((2, 2, 1), gap="medium")
variable_1 = param_croise[0].selectbox(
    "Variable 1 (axe horizontal)", VARIABLES_CATEGORIELLES, index=0
)
variable_2 = param_croise[1].selectbox(
    "Variable 2 (couleur)", VARIABLES_CATEGORIELLES, index=1
)
type_barres = param_croise[2].radio(
    "Type de barres", ["Groupées", "Empilées"], horizontal=True
)

fig_croise = px.histogram(
    df_filtre,
    x=variable_1,
    color=variable_2,
    barmode="group" if type_barres == "Groupées" else "relative",
    title=f"{variable_1} selon {variable_2}",
    color_discrete_sequence=PALETTE,
)
if variable_1.startswith("Mois "):
    fig_croise.update_xaxes(categoryorder="array", categoryarray=ORDRE_MOIS)
fig_croise.update_layout(yaxis_title="Nombre de blocs")
st.plotly_chart(styliser(fig_croise, hauteur=480), width="stretch")

# ---------------------------------------------------------------------------
# Pied de page
# ---------------------------------------------------------------------------
st.divider()
st.markdown(
    '<p class="pied-page"><span class="goutte">◆</span> '
    "Tableau de bord du secteur pétrolier amont ivoirien — données publiques, "
    "blocs pétroliers de Côte d'Ivoire (2018-2023) "
    '<span class="goutte">◆</span></p>',
    unsafe_allow_html=True,
)
