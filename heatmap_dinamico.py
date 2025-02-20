import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

def crear_mapa_calor():
    # Configuración inicial de la página
    st.set_page_config(layout="wide")
    st.title("Mapa de Calor de Colombia 🇨🇴")

    # Cargar el archivo GeoJSON de Colombia
    # Puede descargarlo de: https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/be6a6e239cd5b5b803c6e7c2ec405b793a9064dd/Colombia.geo.json
    @st.cache_data
    def cargar_geodata():
        return gpd.read_file("Colombia.geo.json")

    # Cargar los datos del CSV
    uploaded_file = st.file_uploader("Sube tu archivo CSV", type=['csv'])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        gdf = cargar_geodata()
        
        # Asegúrate de que tu CSV tenga una columna con el nombre del departamento
        # y una columna con el valor que quieres mostrar en el mapa de calor
        st.sidebar.header("Configuración")
        columna_valor = st.sidebar.selectbox(
            "Selecciona la columna para el mapa de calor",
            df.select_dtypes(include=['float64', 'int64']).columns
        )
        
        # Crear el mapa con Plotly
        fig = px.choropleth(
            df,
            geojson=gdf,
            locations=df['departamento'],  # Nombre de la columna con los departamentos
            featureidkey="properties.NOMBRE_DPT",
            color=columna_valor,
            color_continuous_scale="Viridis",
            scope="south america"
        )
        
        # Ajustar el zoom al mapa de Colombia
        fig.update_geos(
            showcountries=True,
            showcoastlines=True,
            showland=True,
            fitbounds="locations",
            visible=False
        )
        
        # Mostrar el mapa
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    crear_mapa_calor()
