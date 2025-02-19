import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Datos básicos de ejemplo
datos = {
    'departamento': ['Antioquia', 'Cundinamarca', 'Valle del Cauca'],
    'latitud': [6.2518, 4.6097, 3.4372],
    'longitud': [-75.5636, -74.0817, -76.5225],
    'valor': [100, 80, 90]
}

# Crear el dataframe
df = pd.DataFrame(datos)

# Título de la página
st.title('Mapa Básico de Colombia 🇨🇴')

# Crear el mapa
fig = go.Figure(go.Scattergeo(
    lon = df['longitud'],
    lat = df['latitud'],
    text = df['departamento'],
    mode = 'markers',
    marker = dict(
        size = 10,
        color = df['valor'],
        colorscale = 'Viridis',
        showscale = True
    )
))

# Configurar el mapa para Colombia
fig.update_geos(
    visible=True,
    resolution=50,
    scope='south america',
    showcountries=True,
    countrycolor="Black",
    showsubunits=True,
    showland=True,
    landcolor="lightgray"
)

# Centrar en Colombia
fig.update_geos(
    center=dict(lat=4.5709, lon=-74.2973),
    projection_scale=3
)

# Mostrar el mapa
st.plotly_chart(fig)
