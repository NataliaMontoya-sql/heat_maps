import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import seaborn as sns
import matplotlib.pyplot as plt

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Proyecto Solaris",
    page_icon="☀️",
    layout="wide"
)
st.title("Proyecto Solaris")
st.sidebar.title("Opciones de Navegación")

@st.cache_data
def cargar_datos():
    # Asegúrate de que el archivo CSV esté en la misma carpeta que este script o ajustar la ruta
    df = pd.read_csv("datos_unificados (2).csv")
    
    # Renombrar columnas para consistencia
    df = df.rename(columns={
        "RH2M": "humedad",
        "PRECTOTCORR": "precipitacion",
        "T2M": "temperatura"
    })
    
    # Crear columna de fecha
    df['Fecha'] = pd.to_datetime(df.astype(str).loc[:, ["YEAR", "MO", "DY"]].agg('-'.join, axis=1))
    
    # Clasificación de regiones
    def get_region(lat, lon):
        if lat > 8:
            return "Caribe"
        if lat < 2:
            return "Sur"
        if lon < -75:
            return "Pacífico"
        return "Andina"
    
    df['Region'] = df.apply(lambda x: get_region(x['LAT'], x['LON']), axis=1)
    return df

# Cargar datos
try:
    df_all = cargar_datos()
except FileNotFoundError:
    st.error("No se encontró el archivo 'datos_unificados (2).csv'. Verifica que esté en la ubicación correcta.")
    df_all = pd.DataFrame()  # DataFrame vacío para evitar otros errores

def crear_mapa_clima_streamlit(df, columna, titulo):
    """
    Crea un mapa de calor usando pydeck con una capa HexagonLayer.
    """
    # Determinar escala y colores según la variable
    if columna == "humedad":
        min_val, max_val = 0, 100
        color_range = [[0, 0, 255], [0, 255, 255]]
    elif columna == "precipitacion":
        min_val, max_val = 0, df['precipitacion'].quantile(0.95)
        color_range = [[230, 240, 230], [0, 128, 0]]
    elif columna == "temperatura":
        min_val, max_val = df['temperatura'].min(), df['temperatura'].max()
        color_range = [[255, 200, 200], [255, 0, 0]]
    else:
        min_val, max_val = 0, 1
        color_range = [[200, 200, 200], [0, 0, 0]]
    
    layer = pdk.Layer(
        "HexagonLayer",
        data=df,
        get_position='[LON, LAT]',
        auto_highlight=True,
        elevation_scale=50,
        pickable=True,
        extruded=True,
        coverage=1,
        radius=15000,
        get_weight=columna
    )
    
    view_state = pdk.ViewState(
        latitude=4.5709,
        longitude=-74.2973,
        zoom=5,
        pitch=40,
    )
    
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"html": f"<b>{titulo}</b><br/>Valor: {{{columna}}}"}
    )
    
    return de
