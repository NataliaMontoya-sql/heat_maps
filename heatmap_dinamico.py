import streamlit as st
import pandas as pd
import plotly.express as px
import json

# Configuración de la página
st.set_page_config(layout="wide")
st.title("Mapa de Calor de Colombia 🇨🇴")

# Cargar el GeoJSON
@st.cache_data
def load_geojson():
    with open("Colombia.geo.json") as f:
        return json.load(f)

try:
    # Subir archivo CSV
    uploaded_file = st.file_uploader("Sube tu archivo CSV, mi amor", type=['csv'])
    
    if uploaded_file is not None:
        # Leer datos
        df = pd.read_csv(uploaded_file)
        
        # Cargar GeoJSON
        geojson = load_geojson()
        
        # Selector de columna para el mapa de calor
        valor_columna = st.selectbox(
            "¿Qué datos querés mostrar en el mapa?",
            df.select_dtypes(include=['float64', 'int64']).columns
        )
        
        # Crear mapa
        fig = px.choropleth(
            df,
            geojson=geojson,
            locations='departamento',  # Columna con nombres de departamentos
            featureidkey="properties.NOMBRE_DPT",
            color=valor_columna,
            color_continuous_scale="Viridis",
            title=f"Mapa de calor: {valor_columna}"
        )
        
        # Ajustar vista
        fig.update_geos(
            center=dict(lat=4.5709, lon=-74.2973),
            projection_scale=3,
            showcoastlines=True,
            showland=True,
            fitbounds="locations"
        )
        
        # Mostrar mapa
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Ay parcera, algo salió mal: {str(e)}")
    st.write("Revisá que tu CSV tenga una columna 'departamento' con los nombres bien escriticos")
