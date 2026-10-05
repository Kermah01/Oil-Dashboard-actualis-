import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from streamlit_extras.metric_cards import style_metric_cards # beautify metric card with css
import plotly.graph_objects as go
import json
from pyecharts.charts import Pie
from pyecharts import options as opts
from streamlit_echarts import st_pyecharts
from pyecharts.charts import Line
import openpyxl
from openpyxl import load_workbook
import altair as alt
import math
import warnings
from pathlib import Path
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

# Dossier du script : les fichiers de données sont lus à côté de ce fichier,
# quel que soit le dossier de lancement (noms avec accents et espaces compris).
BASE_DIR = Path(__file__).resolve().parent

# Largeur de barre latérale de la version d'origine (336 px, valeur par défaut de Streamlit 1.30)
st. set_page_config(layout="wide", initial_sidebar_state=336)

#Chargement des bases de données
def read_excel_file(file):
    data = load_workbook(file)
    datas = data.active
    donnees = []
    for ligne in datas.iter_rows(values_only=True):
        donnees.append(list(ligne))
    en_tetes = donnees[0]
    donnees = donnees[1:]
    new_df = pd.DataFrame(donnees, columns=en_tetes)
    return new_df
df=read_excel_file(BASE_DIR / "Base Pétrole finale.xlsx")
# Correction des coquilles dans les intitulés de colonnes (affichage uniquement,
# les fichiers de données restent inchangés)
df = df.rename(columns={
    'Superfice (en Km²)': 'Superficie (en Km²)',
    'Patenaires (hors PETROCI)': 'Partenaires (hors PETROCI)',
    'Patenaires CPP 2 (hors PETROCI)': 'Partenaires CPP 2 (hors PETROCI)',
    'Patenaires CPP 3 (hors PETROCI)': 'Partenaires CPP 3 (hors PETROCI)',
})
coord_géo= read_excel_file(BASE_DIR / "Coordonnées géographiques Blocs.xlsx")
with open(BASE_DIR / "GéoJson Blocs pétroliers.json", encoding="utf-8") as f:
  counties = json.load(f)
st.sidebar.image('https://static.vecteezy.com/system/resources/thumbnails/010/248/729/original/national-emblem-coat-of-arms-or-symbol-of-ivory-coast-in-waving-flag-smooth-4k-seemless-loop-free-video.jpg', width="stretch")
st.sidebar.subheader("Cabinet du Ministre de l'Economie, du Plan et du Développement", divider="orange")

 #Définition des ordres de mois et des jours
 #Définition des ordres de mois et des jours
order_of_months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
dic_month={1:"Janvier",2:"Février",3:"Mars",4:"Avril",5:"Mai",6:"Juin",7:"Juillet",8:"Août",9:"Septembre",10:"Octobre",11:"Novembre",12:"Décembre"}
order_of_days = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi']
dic_day={0:"Lundi",1:"Mardi",2:"Mercredi",3:"Jeudi",4:"Vendredi",5:"Samedi",6:"Dimanche"}

def order_of_months_year(Année):
    order_of_months_year = []
    start_year = df[Année].min()
    end_year = df[Année].max()
    for year in range(start_year, end_year + 1):
        for month in order_of_months:
            order_of_months_year.append(f"{month} {year}")
    return order_of_months_year

def convertir_date(serie):
    # Les cellules Excel sont déjà lues comme des dates par openpyxl : on ne les
    # reparse pas. Les éventuelles dates saisies en texte (jj/mm/aaaa [hh:mm])
    # sont converties, les valeurs invalides deviennent NaT.
    if is_datetime64_any_dtype(serie):
        return serie
    texte = serie.where(serie.map(lambda v: isinstance(v, str)))
    dates = pd.to_datetime(serie.where(texte.isna()), errors='coerce')
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        dates_texte = pd.to_datetime(texte, dayfirst=True, errors='coerce')
    return dates.fillna(dates_texte)

def transf_df(df):
    for date in ["Date de signature du 1er CPP", "Date de la 2ème signature du CPP","Date de fin de validité d'exploration 1", "Date de fin de validité d'exploration 2","Date de fin de validité exploitation 1"]:
        df[date]= convertir_date(df[date])
        df[f"Mois {str(date).replace('Date','')}"] = df[date].dt.month
        df[f"Jour {str(date).replace('Date','')}"] = df[date].dt.day_of_week
        df[f"heure {str(date).replace('Date','')}"]=df[date].dt.hour
        df[f"Année {str(date).replace('Date','')}"]=df[date].dt.year
        df[f"Mois {str(date).replace('Date','')}"]=df[f"Mois {str(date).replace('Date','')}"].map(dic_month)
        df[f"Mois* {str(date).replace('Date','')}"] = pd.Categorical(df[f"Mois {str(date).replace('Date','')}"], categories=order_of_months, ordered=True)
        df[f"Jour {str(date).replace('Date','')}"]=df[f"Jour {str(date).replace('Date','')}"].map(dic_day)
        df[f"Jour* {str(date).replace('Date','')}"] = pd.Categorical(df[f"Jour {str(date).replace('Date','')}"], categories=order_of_days, ordered=True)
        #df[f"Mois de l'année / {str(date).replace('Date','')}"] = df[f"Mois* {str(date).replace('Date','')}"].astype("str") + ' ' + df[f"Année {str(date).replace('Date','')}"].astype("str")
        #df[f"Mois de l'année / {str(date).replace('Date','')}"] = pd.Categorical(df[f"Mois de l'année / {str(date).replace('Date','')}"], categories=order_of_months_year(f"Année {str(date).replace('Date','')}"), ordered=True)    
    return df
df=transf_df(df)
page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] > .main,
    [data-testid="stMain"] {{
    background-image: url(https://www.vudaf.com/wp-content/uploads/2021/09/petrole-en-cote-divoire.jpg);
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    height: 100vh;
    margin: 0;
    display: flex;

    
    }}
    [data-testid="stSidebar"] {{
        background-color: #000 !important;  /* Fond noir */
        border: 2px solid #f7a900 !important;  /* Bordure rouge */
        border-radius: 10px;  /* Coins arrondis */
        margin-top: 0 px;  /* Ajuster la position vers le haut */
        position: relative;
        z-index: 1;  /* S'assurer que la barre latérale est au-dessus du contenu */
        padding: 10px;
    }}

    [data-testid="stHeader"] {{
    background: rgba(0, 0, 0, 0);
    color: white;
    }}

    [data-testid="stToolbar"] {{
    right: 2rem;
    }}

    /* Barre latérale repliée : pas de bande vide à gauche du contenu */
    [data-testid="stSidebar"][aria-expanded="false"] {{
        padding: 0;
        border-width: 0 !important;
    }}

    /* Tablettes et téléphones */
    @media (max-width: 768px) {{
        [data-testid="stSidebar"][aria-expanded="true"] {{
            position: absolute;  /* la barre latérale passe au-dessus du contenu */
            z-index: 999991;     /* et au-dessus de l'en-tête (bouton de fermeture accessible) */
        }}
    }}

    /* Téléphones */
    @media (max-width: 640px) {{
        [data-testid="stMain"] h1 {{
            font-size: 1.75rem;
        }}
        [data-testid="stToolbar"] {{
            right: 0.5rem;
        }}
    }}
    </style>
    """

st.markdown(page_bg_img, unsafe_allow_html=True)
st.markdown('<div style="text-align:center;width:100%;"><h1 style="color:white;background-color:black;border:red;border-style:solid;border-radius:5px;">TABLEAU DE BORD DU SECTEUR PETROLIER AMONT IVOIRIEN </h1></div>', unsafe_allow_html=True)
st.write("")



def make_donut(input_response, input_text, input_color):
  if input_color == 'blue':
      chart_color = ['#29b5e8', '#155F7A']
  if input_color == 'green':
      chart_color = ['#27AE60', '#12783D']
  if input_color == 'orange':
      chart_color = ['#F39C12', '#875A12']
  if input_color == 'red':
      chart_color = ['#E74C3C', '#781F16']
    
  source = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100-input_response, input_response]
  })
  source_bg = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100, 0]
  })
    
  plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          #domain=['A', 'B'],
                          domain=[input_text, ''],
                          # range=['#29b5e8', '#155F7A']),  # 31333F
                          range=chart_color),
                      legend=None),
  ).properties(width=130, height=130)
    
  text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
  plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          # domain=['A', 'B'],
                          domain=[input_text, ''],
                          range=chart_color),  # 31333F
                      legend=None),
  ).properties(width=130, height=130)
  return plot_bg + plot + text




def afficher_carte():
    fig_map = px.choropleth_map(df, geojson=counties, locations='Blocs',featureidkey="properties.name", color='Statut du bloc',
                            color_continuous_scale="Viridis",
                            range_color=(0, 12),
                            map_style="open-street-map",
                            zoom=6,center = {"lat": 5.8, "lon": -5.61},
                            opacity=0.5,
                            labels={'Statut du bloc':'Statut du bloc'},
                            custom_data= [df["Blocs"],df["Opérateur le plus récent"], df['Superficie (en Km²)'], df["Type de profondeur"], df["Prod. Pétrole 2023 Bbls"], df['Prod Gaz N. 2023 MMSCF']]
                            )
    fig_map.update_traces(text=df['Blocs'], hovertemplate='<b>Nom du bloc</b>: %{customdata[0]}<br>'
                                                            '<b>Opérateur le plus récent</b>: %{customdata[1]}<br>'
                                                            '<b>Superficie</b>: %{customdata[2]} Km2<br>'
                                                            '<b>Type de profondeur</b>: %{customdata[3]}<br>'
                                                            '<b>Production de pétrole du Bloc en 2023</b>: %{customdata[4]} Bbls<br>'
                                                            '<b>Production de gaz du Bloc en 2023</b>: %{customdata[5]} MMSCF',
                                                            hoverlabel=dict(font=dict(size=10, color='white')),)
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig_map.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0.3)',})
    return st.plotly_chart(fig_map,width="stretch")


year=st.sidebar.select_slider("sélectionnez votre période d'analyse", options=[2018,2019,2020,2021,2022,2023],value=(2022,2023))
st.subheader(f"Productions en {year[1]} par rapport à {year[0]}", divider="rainbow")

col = st.columns((5,5), gap='medium')
with col[0]:
    l=(df[f"Prod. Pétrole {year[1]} Bbls"].sum()-df[f"Prod. Pétrole {year[0]} Bbls"].sum())/1000
    st.metric(label=f"Production totale de barils de pétrole en {year[1]} (Bbls)", value=f"{((df[f'Prod. Pétrole {year[1]} Bbls'].sum())/1000000).round(2)} M Bbls", delta=f"{l} K Bbls")
    
with col[1]:
    p=(df[f"Prod Gaz N. {year[1]} MMSCF"].sum()-df[f"Prod Gaz N. {year[0]} MMSCF"].sum())
    st.metric(label=f"Production totale de barils de Gaz naturel en {year[1]}", value=f"{((df[f'Prod Gaz N. {year[1]} MMSCF'].sum())/1000).round(2)} K MMSCF", delta= f"{p} MMSCF")

st.subheader("Proportion de :", divider="rainbow") 
col2=st.columns((2.5,2.5,2.5,2.5), gap='medium')
  
with col2[0]:
    st.write("blocs en production")
    st.altair_chart(make_donut((df[df["Statut du bloc"]=="En activité - production"].shape[0]/df.shape[0])*100, 'Proportion de blocs en production', 'green'), width="content")
with col2[1]:    
    st.write("blocs en exploration")
    st.altair_chart(make_donut((df[df["Statut du bloc"]=="En activité - exploration"].shape[0]/df.shape[0])*100, 'Proportion de blocs exploration', 'blue'), width="content")
with col2[2]:
    st.write("blocs en négociation")
    st.altair_chart(make_donut(np.round(((df[df["Statut du bloc"]=="En activité - négociation"].shape[0]/df.shape[0])*100)), 'Proportion de blocs en négociation', 'orange'), width="content")
with col2[3]:
    st.write("blocs libres")
    st.altair_chart(make_donut((df[df["Statut du bloc"]=="Libre"].shape[0]/df.shape[0])*100, 'Proportion de blocs libres', 'red'), width="content")

style_metric_cards(background_color='#0c0c0c',border_color="#CCC",border_left_color="#f7a900",box_shadow=True)


afficher_carte()

st.header("Base de données personnalisée",divider="rainbow" )
def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("AJOUTEZ UN FILTRE")
    

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Choisissez les variables que vous souhaitez utiliser comme filtre", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            int_columns = df.select_dtypes(include="int").columns
            float_columns = df.select_dtypes(include="float").columns

            if is_numeric_dtype(df[column]) :
                valeurs = df[column].dropna()
                if valeurs.empty or valeurs.min() == valeurs.max():
                    right.info(f"Aucune plage de valeurs à filtrer pour {column}.")
                    continue
                _min = math.floor(valeurs.min())
                _max = math.ceil(valeurs.max())
                user_num_input = right.slider(
                    f"Valeurs de {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                if df[column].dropna().empty:
                    right.info(f"Aucune date à filtrer pour {column}.")
                    continue
                user_date_input = right.date_input(
                    f"Valeur de {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            elif isinstance(df[column].dtype, pd.CategoricalDtype) or df[column].unique().shape[0]<100:
                arr=df[column].unique()
                user_cat_input = right.multiselect(
                    f"Valeur de {column}",
                    arr
                    ,
                    default=list(arr),
                )
                df = df[df[column].isin(user_cat_input)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df
    
df_perso=filter_dataframe(df)
st.dataframe(df_perso)

colors = list(px.colors.sequential.Rainbow_r)
colors.extend(px.colors.sequential.Agsunset)
colors.extend(px.colors.sequential.Aggrnyl)

# SECTION GRAPHIQUE
st.header("Analyses graphiques", divider="rainbow")

#Analyse univariée
st.subheader("Analyse graphique avec une seule variable")
# Histogramme et Camembert sur la même ligne
cam, hist = st.columns(2,gap='medium')
with cam:
    st.subheader("CAMEMBERT")
    selected_categorical_variable_p = st.selectbox("***Sélectionnez la variable catégorielle pour le camembert***",['Type de profondeur', 'Opérateur1',
    'Partenaires (hors PETROCI)', 'Opérateur CPP 2',
    'Partenaires CPP 2 (hors PETROCI)', 'Opérateur CPP 3',
    'Partenaires CPP 3 (hors PETROCI)', 'Statut du bloc','Mois  de signature du 1er CPP', 'Année  de signature du 1er CPP', 'Année  de la 2ème signature du CPP', 'Mois  de la 2ème signature du CPP', "Mois  de fin de validité d'exploration 1", "Année  de fin de validité d'exploration 1", "Année  de fin de validité d'exploration 2", "Mois  de fin de validité d'exploration 2",'Mois  de fin de validité exploitation 1','Année  de fin de validité exploitation 1'], index=1)
    #📌 Charger les données
        # 📌 Charger les données
    df_counts = df[selected_categorical_variable_p].value_counts().reset_index()
    df_counts.columns = ['Category', 'Count']
    if df_counts.empty:
        st.warning(f"Aucune donnée disponible pour {selected_categorical_variable_p}. Veuillez choisir une autre variable.")
    else:
        # 📌 Création du camembert avec adaptation à la colonne
        pie = (
            Pie(init_opts=opts.InitOpts(
                width="100%",  # 📌 Permet au graphique de s'étirer selon la colonne
                height="1000px",  # 📌 Ajuste la hauteur pour éviter l'écrasement
                bg_color="black",  # ✅ Fond totalement transparent
            ))
            .add(
                "", 
                [list(z) for z in zip(df_counts["Category"], df_counts["Count"])], 
                center=["50%", "60%"],
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=f"Répartition de {selected_categorical_variable_p}",
                    pos_left="center",
                    pos_top="2%",
                    title_textstyle_opts=opts.TextStyleOpts(
                        color="white",
                        font_size=16
                    )
                ),
                legend_opts=opts.LegendOpts(is_show=False),
            )
            .set_series_opts(
                label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)", color="white"),
                tooltip_opts=opts.TooltipOpts(trigger="item", formatter="{b}: {c} ({d}%)"),
            )
        )
        st.markdown("""
            <style>
            div.echarts-container {
                background: transparent !important;
            }
            </style>
            """, unsafe_allow_html=True
        )
        st_pyecharts(pie)

with hist:
    st.subheader("HISTOGRAMME")
    selected_categorical_variable = st.selectbox("***Sélectionnez la variable catégorielle pour l'histogramme***",['Type de profondeur', 'Opérateur1',
    'Partenaires (hors PETROCI)', 'Opérateur CPP 2',
    'Partenaires CPP 2 (hors PETROCI)', 'Opérateur CPP 3',
    'Partenaires CPP 3 (hors PETROCI)', 'Statut du bloc','Mois  de signature du 1er CPP', 'Année  de signature du 1er CPP', 'Année  de la 2ème signature du CPP', 'Mois  de la 2ème signature du CPP', "Mois  de fin de validité d'exploration 1", "Année  de fin de validité d'exploration 1", "Année  de fin de validité d'exploration 2", "Mois  de fin de validité d'exploration 2",'Mois  de fin de validité exploitation 1','Année  de fin de validité exploitation 1'], index=1)
    fig_histogram = px.histogram(df, x=df[selected_categorical_variable], color=df[selected_categorical_variable],title=f"Histogramme de {selected_categorical_variable}",color_discrete_sequence=colors)
    fig_histogram.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0.3)',},title_x=0.35)
    fig_histogram.update_traces( textfont_color='rgba(255, 255, 255, 1)')
    if selected_categorical_variable in ['Mois  de signature du 1er CPP',  'Mois  de la 2ème signature du CPP', "Mois  de fin de validité d'exploration 1","Mois  de fin de validité d'exploration 2",'Mois  de fin de validité exploitation 1']:
        fig_histogram.update_xaxes(categoryorder='array', categoryarray=order_of_months)
    fig_histogram.update_xaxes(showticklabels=False)
    st.plotly_chart(fig_histogram,width="stretch")

st.subheader("Analyse de l'évolution de la production et de la vente")

# 📌 Définition des grandeurs à analyser
grandeurs_mapping = {
    "Production de Gaz (en MMSCF)": [col for col in df.columns if "Prod Gaz" in col],
    "Production de Pétrole (en Bbls)": [col for col in df.columns if "Prod. Pétrole" in col],
    "Vente de Gaz (en MMBTU)": [col for col in df.columns if "Vente Gaz" in col]
}

# 📌 Sélection de la grandeur
grandeur_selectionnee = st.selectbox("📊 Sélectionnez une grandeur :", list(grandeurs_mapping.keys()))

# 📌 Option d'affichage
mode_affichage = st.radio("🔎 Mode d'affichage :", ["Valeur par bloc", "Somme totale"])

# 📌 Récupérer les colonnes associées à la grandeur choisie
colonnes_a_utiliser = grandeurs_mapping[grandeur_selectionnee]

# 📌 Extraction des années
annees = [str(int("".join(filter(str.isdigit, col)))) for col in colonnes_a_utiliser]

# 📌 Création du DataFrame pour PyEcharts
df_temps = df[['Blocs'] + colonnes_a_utiliser].copy()
df_temps.columns = ['Blocs'] + annees  # Renommage des colonnes

# 📌 Transformation des données pour affichage avec PyEcharts
df_melted = df_temps.melt(id_vars="Blocs", var_name="Année", value_name="Valeur")
df_melted = df_melted[df_melted["Valeur"] > 0]  # Supprimer les valeurs nulles

# 🚨 Vérification s'il y a des données à afficher
if df_melted.empty:
    st.warning(f"Aucune donnée disponible pour {grandeur_selectionnee}. Veuillez choisir une autre grandeur.")
else:
    # 📌 Création du graphique PyEcharts avec plus de hauteur et légende à droite
    line_chart = Line(init_opts=opts.InitOpts(
        width="100%", height="2500px", bg_color="black"
    ))

    line_chart.add_xaxis(df_melted["Année"].unique().tolist())  # Ajout des années

    # 📌 Mode d'affichage par bloc
    if mode_affichage == "Valeur par bloc":
        for bloc in df_melted["Blocs"].unique():
            df_bloc = df_melted[df_melted["Blocs"] == bloc]
            line_chart.add_yaxis(
                bloc, df_bloc["Valeur"].tolist(),
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(width=3),
                label_opts=opts.LabelOpts(is_show=False)  # ❌ Suppression des étiquettes
            )
    else:
        # Mode Somme Totale
        df_summed = df_melted.groupby("Année")["Valeur"].sum().reset_index()
        line_chart.add_yaxis(
            "Total", df_summed["Valeur"].tolist(),
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(width=3),
            label_opts=opts.LabelOpts(is_show=False)  # ❌ Suppression des étiquettes
        )

    # 📌 Personnalisation du graphique
    line_chart.set_global_opts(
        title_opts=opts.TitleOpts(
            title=f"📊 Évolution de {grandeur_selectionnee}",
            pos_left="20%",
            pos_top="5%",
            title_textstyle_opts=opts.TextStyleOpts(color="white", font_size=16)
        ),
        xaxis_opts=opts.AxisOpts(
            name="Année",
            axislabel_opts=opts.LabelOpts(color="white"),
            type_="category",
            splitline_opts=opts.SplitLineOpts(is_show=False)  # ❌ Supprimer le quadrillage X
        ),
        yaxis_opts=opts.AxisOpts(
            name="Valeur",
            axislabel_opts=opts.LabelOpts(color="white"),
            splitline_opts=opts.SplitLineOpts(is_show=False)  # ❌ Supprimer le quadrillage Y
        ),
        legend_opts=opts.LegendOpts(
            pos_right="5%",
            pos_top="15%",  # ✅ Déplacement de la légende à droite
            orient="vertical",  # ✅ Alignement vertical de la légende
            textstyle_opts=opts.TextStyleOpts(color="white")
        )
    )

    # 📌 Affichage dans Streamlit
    st_pyecharts(line_chart)

# Section des analyses croisées

st.subheader("Analyse croisée entre variables catégorielles")
#Type de l'histogramme croisé
def barmode_selected(t):
    if t =='empilé':
        a='relative'  
    else: 
        a='group'
    return a



selected_variable_1 = st.selectbox("***Variable 1***", ['Type de profondeur', 'Opérateur1',
'Partenaires (hors PETROCI)', 'Opérateur CPP 2',
'Partenaires CPP 2 (hors PETROCI)', 'Opérateur CPP 3',
'Partenaires CPP 3 (hors PETROCI)', 'Statut du bloc','Mois  de signature du 1er CPP', 'Année  de signature du 1er CPP', 'Année  de la 2ème signature du CPP', 
'Mois  de la 2ème signature du CPP', "Mois  de fin de validité d'exploration 1", "Année  de fin de validité d'exploration 1", "Année  de fin de validité d'exploration 2", 
"Mois  de fin de validité d'exploration 2",'Mois  de fin de validité exploitation 1','Année  de fin de validité exploitation 1'], index=7)
selected_variable_2 = st.selectbox("***Variable 2***", ['Type de profondeur', 'Opérateur1',
'Partenaires (hors PETROCI)', 'Opérateur CPP 2',
'Partenaires CPP 2 (hors PETROCI)', 'Opérateur CPP 3',
'Partenaires CPP 3 (hors PETROCI)', 'Statut du bloc','Mois  de signature du 1er CPP', 'Année  de signature du 1er CPP', 'Année  de la 2ème signature du CPP', 
'Mois  de la 2ème signature du CPP', "Mois  de fin de validité d'exploration 1", "Année  de fin de validité d'exploration 1", 
"Année  de fin de validité d'exploration 2", "Mois  de fin de validité d'exploration 2",'Mois  de fin de validité exploitation 1',
'Année  de fin de validité exploitation 1'],index=1)
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.subheader("PARAMETRES DES GRAPHIQUES")
type_graph=st.sidebar.radio("***:grey[Choisissez le type d'histogramme croisé]***", ['empilé','étalé'], index=1)
if selected_variable_2 in [f"Prod Gaz N. {i} MMSCF" for i in range(2018,2024)] + [f"Prod. Pétrole {i} Bbls" for i in range(2018,2024)]:
    fig_croisé = px.bar(df.groupby(selected_variable_1)[selected_variable_2].sum().reset_index(), x=selected_variable_1,y=selected_variable_2, color=selected_variable_2,barmode=barmode_selected(type_graph),color_continuous_scale=['red', 'yellow', 'green'],range_color=[0, 5])
else:
    fig_croisé = px.histogram(df, x=selected_variable_1, color=selected_variable_2,barmode=barmode_selected(type_graph),color_discrete_sequence= colors)
    m=['Mois  de signature du 1er CPP', 'Mois  de la 2ème signature du CPP', "Mois  de fin de validité d'exploration 1", "Mois  de fin de validité d'exploration 2",'Mois  de fin de validité exploitation 1']
    if selected_variable_1 in m or selected_variable_2 in m:
        fig_croisé.update_xaxes(categoryorder='array', categoryarray=order_of_months)
fig_croisé.update_layout(title=f'Graphique en barres groupées - {selected_variable_1 } vs {selected_variable_2 }')
fig_croisé.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0.3)',},title_x=0.20)

st.plotly_chart(fig_croisé,  width="stretch")





