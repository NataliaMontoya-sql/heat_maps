import pandas as pd
import streamlit as st
import plotly.express as px
import folium
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
from branca.element import Template, MacroElement

# Configuración de la página
st.set_page_config(page_title="Proyecto Solaris", page_icon="", layout="wide")
st.title("Proyecto Solaris")
st.sidebar.title("Opciones de Navegación")

st.sidebar.subheader("Carga de archivos CSV")
# Subida de archivos
uploaded_datos = st.sidebar.file_uploader("Sube datos unificados", type=["csv"])
uploaded_humedad = st.sidebar.file_uploader("Sube datos de humedad", type=["csv"])
uploaded_precipitacion = st.sidebar.file_uploader("Sube datos de precipitación", type=["csv"])
uploaded_temperatura = st.sidebar.file_uploader("Sube datos de temperatura", type=["csv"])

# Función para cargar datos a partir de un file uploader
@st.cache_data
def cargar_csv(file) -> pd.DataFrame:
    return pd.read_csv(file)

# Variables de datos
if uploaded_datos is not None:
    df_all = cargar_csv(uploaded_datos)
    # Crear columna Fecha
    df_all['Fecha'] = pd.to_datetime(
        df_all.astype(str).loc[:, ["YEAR", "MO", "DY"]].agg('-'.join, axis=1)
    )
else:
    st.warning("Sube el archivo de datos unificados")
    df_all = None

if uploaded_humedad is not None:
    df_humedad = cargar_csv(uploaded_humedad)
    df_humedad = df_humedad.rename(columns={"RH2M": "humedad"})
else:
    st.warning("Sube el archivo de datos de humedad")
    df_humedad = None

if uploaded_precipitacion is not None:
    df_precipitacion = cargar_csv(uploaded_precipitacion)
    df_precipitacion = df_precipitacion.re
