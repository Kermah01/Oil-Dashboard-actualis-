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

# Palette validée pour fond sombre (identité des séries)
PALETTE = [
    "#3987e5", "#d95926", "#199e70", "#c98500",
    "#d55181", "#008300", "#9085e9", "#e66767",
] + list(px.colors.qualitative.Safe)

COULEURS_STATUT = {
    "En activité - production": "#199e70",
    "En activité - exploration": "#3987e5",
    "En activité - négociation": "#d95926",
    "Libre": "#8a93a0",
}

COULEUR_TEXTE = "#e8edf4"
COULEUR_GRILLE = "#242c38"
COULEUR_NEUTRE = "#232b37"

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
    """Applique le gabarit graphique commun (fond, grille, typographie)."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COULEUR_TEXTE, size=13),
        height=hauteur,
        margin=dict(l=10, r=10, t=50, b=10),
        colorway=PALETTE,
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor=COULEUR_GRILLE, zerolinecolor=COULEUR_GRILLE)
    fig.update_yaxes(gridcolor=COULEUR_GRILLE, zerolinecolor=COULEUR_GRILLE)
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
        font=dict(size=20, color=COULEUR_TEXTE),
    )
    fig.update_layout(
        showlegend=False,
        height=170,
        margin=dict(l=6, r=6, t=6, b=6),
        paper_bgcolor="rgba(0,0,0,0)",
        title=dict(text=libelle, x=0.5, xanchor="center", font=dict(size=13)),
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
# En-tête
# ---------------------------------------------------------------------------
st.title("Tableau de bord du secteur pétrolier amont ivoirien")
st.caption(
    f"{len(df_filtre)} bloc(s) sélectionné(s) sur {len(df)} — "
    f"comparaison {annee_etude} vs {annee_ref}."
)

# ---------------------------------------------------------------------------
# Indicateurs clés
# ---------------------------------------------------------------------------
st.subheader(f"Indicateurs clés {annee_etude}", divider="orange")

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
    delta=f"{fmt_fr(delta_petrole)} Bbls vs {annee_ref}",
    border=True,
)
kpi[1].metric(
    "Production de gaz naturel",
    f"{fmt_fr(prod_gaz / 1e3, 2)} K MMSCF",
    delta=f"{fmt_fr(delta_gaz)} MMSCF vs {annee_ref}",
    border=True,
)
kpi[2].metric(
    "Vente de gaz naturel",
    f"{fmt_fr(vente_gaz / 1e6, 2)} M MMBTU",
    delta=f"{fmt_fr(delta_vente)} MMBTU vs {annee_ref}",
    border=True,
)
kpi[3].metric(
    "Forages réalisés",
    fmt_fr(forages),
    delta=f"{fmt_fr(delta_forages)} vs {annee_ref}",
    border=True,
)

# ---------------------------------------------------------------------------
# Répartition des blocs par statut
# ---------------------------------------------------------------------------
st.subheader("Répartition des blocs par statut", divider="orange")
st.caption("Parts calculées sur l'ensemble des blocs de la base.")

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
st.subheader("Carte des blocs pétroliers", divider="orange")

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
    font=dict(color=COULEUR_TEXTE),
    legend=dict(
        title="Statut du bloc",
        bgcolor="rgba(16,21,29,0.75)",
        x=0.01,
        y=0.99,
    ),
)
st.plotly_chart(fig_carte, width="stretch")
st.caption(
    "Les blocs sans contour géographique référencé dans le GeoJSON "
    "n'apparaissent pas sur la carte."
)

# ---------------------------------------------------------------------------
# Base de données personnalisable
# ---------------------------------------------------------------------------
st.subheader("Base de données personnalisée", divider="orange")


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
st.subheader("Analyses graphiques", divider="orange")

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
st.caption(
    "Tableau de bord du secteur pétrolier amont ivoirien — données publiques, "
    "blocs pétroliers de Côte d'Ivoire (2018-2023)."
)
