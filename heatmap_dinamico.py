import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(layout="wide")
st.title("Mapa de Calor de Colombia 🇨🇴")

# Añadir el uploader de archivos
uploaded_file = st.file_uploader("Subir archivo CSv", type=['csv'])

# Función para procesar el CSV
def procesar_csv(df):
    # Verificar las columnas necesarias
    columnas_requeridas = ['departamento', 'latitud', 'longitud']
    if not all(col in df.columns for col in columnas_requeridas):
        st.error("¡Uy parcera! Tu CSV debe tener las columnas: departamento, latitud y longitud")
        return None
    
    # Mostrar selector de columna para el valor del mapa de calor
    columnas_numericas = df.select_dtypes(include=['float64', 'int64']).columns
    columnas_numericas = [col for col in columnas_numericas if col not in ['latitud', 'longitud']]
    
    if len(columnas_numericas) > 0:
        columna_valor = st.selectbox(
            "¿Qué datos querés mostrar en el mapa?",
            columnas_numericas
        )
        df['valor'] = df[columna_valor]
    else:
        st.error("Tu CSV debe tener al menos una columna numérica para el mapa de calor")
        return None
    
    return df

# Datos de ejemplo por si no se sube archivo
datos_ejemplo = {
    'departamento': ['Antioquia', 'Cundinamarca', 'Valle del Cauca'],
    'latitud': [6.2530, 4.6097, 3.4372],
    'longitud': [-75.5736, -74.0817, -76.5225],
    'valor': [100, 80, 90]
}

# Usar datos subidos o ejemplo
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df = procesar_csv(df)
        if df is None:
            df = pd.DataFrame(datos_ejemplo)
    except Exception as e:
        st.error(f"Uy mor, hubo un error leyendo tu archivo: {str(e)}")
        df = pd.DataFrame(datos_ejemplo)
else:
    st.info("👆 Subí tu CSV o mirá el ejemplo que armamos")
    df = pd.DataFrame(datos_ejemplo)

# Crear el mapa
fig = px.scatter_mapbox(
    df, 
    lat='latitud', 
    lon='longitud',
    color='valor',
    size=[20]*len(df),
    hover_name='departamento',
    color_continuous_scale='Viridis',
    zoom=5,
    mapbox_style='carto-positron',
    center={'lat': 4.5709, 'lon': -74.2973},
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
st.write("Datos que estamos usando:")
st.dataframe(df)
