import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(layout="wide")
st.title("Mapa de Calor de Colombia 🇨🇴")

# Datos de ejemplo de departamentos (coordenadas aproximadas del centro de cada depto)
datos_deptos = {
    'departamento': [
        'Antioquia', 'Cundinamarca', 'Valle del Cauca', 
        'Atlántico', 'Santander', 'Bolívar'
    ],
    'latitud': [
        6.2530, 4.6097, 3.4372,
        10.6966, 6.6437, 8.6704
    ],
    'longitud': [
        -75.5736, -74.0817, -76.5225,
        -74.8741, -73.6535, -74.0300
    ],
    'valor': [100, 80, 90, 70, 85, 75]  # Valores de ejemplo
}

# Crear DataFrame
df = pd.DataFrame(datos_deptos)

# Crear el mapa
fig = px.scatter_mapbox(
    df, 
    lat='latitud', 
    lon='longitud',
    color='valor',
    size=[20]*len(df),  # Tamaño fijo para todos los puntos
    hover_name='departamento',
    color_continuous_scale='Viridis',
    zoom=5,
    mapbox_style='carto-positron',
    center={'lat': 4.5709, 'lon': -74.2973},  # Centro en Colombia
    title='Mapa de Calor por Departamentos'
)

# Ajustar el layout
fig.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    height=600
)

# Mostrar el mapa
st.plotly_chart(fig, use_container_width=True)

# Mostrar los datos en una tabla
st.write("Datos por Departamento:")
st.dataframe(df)
