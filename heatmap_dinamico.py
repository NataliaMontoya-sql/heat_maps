import pandas as pd
import streamlit as st
import plotly.express as px
import folium
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
from branca.element import Template, MacroElement

# Configuración de la página de Streamlit
st.set_page_config(page_title="Proyecto Solaris", page_icon="", layout="wide")
st.title("Proyecto Solaris")
st.sidebar.title("Opciones de Navegación")

# Funciones de carga de datos
@st.cache_data
def cargar_humedad():
    df = pd.read_csv("datos_agrupados_humedity.csv")
    df = df.rename(columns={"RH2M": "humedad"})
    return df

@st.cache_data
def cargar_precipitacion():
    df = pd.read_csv("datos_agrupados_precipitacion.csv")
    df = df.rename(columns={"PRECTOTCORR": "precipitacion"})
    return df

@st.cache_data
def cargar_temperatura():
    df = pd.read_csv("datos_agrupados_temperature1.csv")
    df = df.rename(columns={"T2M": "temperatura"})
    return df

df_humedad = cargar_humedad()
df_precipitacion = cargar_precipitacion()
df_temperatura = cargar_temperatura()

@st.cache_data
def cargar_datos():
    return pd.read_csv("datos_unificados (2).csv")
df_all = cargar_datos()

# Crear columna 'Fecha' combinando 'YEAR', 'MO', 'DY'
df_all['Fecha'] = pd.to_datetime(
    df_all.astype(str).loc[:, ["YEAR", "MO", "DY"]].agg('-'.join, axis=1)
)

# Función para agregar leyenda a un mapa Folium utilizando MacroElement y Template de branca
def agregar_leyenda(mapa, titulo, items):
    html = """
    {% macro html(this, kwargs) %}
    <div style="
         position: fixed;
         bottom: 50px; left: 50px;
         width: 220px;
         background-color: white;
         border:2px solid grey;
         z-index:9999;
         font-size:14px;
         padding: 10px;
         ">
         <b>""" + titulo + """</b><br>
    """
    for color, descripcion in items:
        html += '<i style="background: ' + color + '; width: 10px; height: 10px; display: inline-block; margin-right: 5px; border-radius: 50%;"></i>' + descripcion + '<br>'
    html += """</div>
    {% endmacro %}"""
    
    template = Template(html)
    macro = MacroElement()
    macro._template = template
    mapa.get_root().add_child(macro)

# Función para crear mapas climáticos con leyenda
def crear_mapa_clima(df, columna, titulo):
    q75 = df[columna].quantile(0.75)
    q50 = df[columna].quantile(0.5)
    max_row = df.loc[df[columna].idxmax()]
    map_center = [max_row["LAT"], max_row["LON"]]
    mapa = folium.Map(location=map_center, zoom_start=6)
    
    for _, row in df.iterrows():
        valor = row[columna]
        if valor > q75:
            color = 'green'
        elif valor > q50:
            color = 'orange'
        else:
            color = 'red'
        folium.CircleMarker(
            location=[row['LAT'], row['LON']],
            radius=valor * 0.1,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            popup=f"{titulo}: {valor:.2f}"
        ).add_to(mapa)
        
    # Agregar leyenda al mapa
    leyenda_items = [
        ("green", "Mayor al 75%"),
        ("orange", "Entre 50% y 75%"),
        ("red", "Menor o igual al 50%")
    ]
    agregar_leyenda(mapa, f"Leyenda {titulo}", leyenda_items)
    return mapa

# Menú de navegación en la barra lateral
menu = st.sidebar.selectbox("Selecciona una opción:", [
    "Inicio", "Datos", "Visualización", "Mapa Prin
