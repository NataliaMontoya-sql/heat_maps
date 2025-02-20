import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(layout="wide")
st.title("🗺️ Mapa de Calor de Colombia")

# Añadir el uploader de archivos
uploaded_file = st.file_uploader("📄 Ingresar archivo CSV", type=['csv'])

# Función para validar y filtrar coordenadas
def filtrar_coordenadas(df):
    # Rango aproximado de Colombia
    mask = (df['LAT'].between(-4.23, 12.45)) & (df['LON'].between(-79.00, -66.87))
    df_filtrado = df[mask].copy()
    
    if len(df_filtrado) == 0:
        st.error("¡No hay coordenadas válidas dentro de Colombia!")
        return None
    
    n_invalidas = len(df) - len(df_filtrado)
    if n_invalidas > 0:
        st.warning(f"Se eliminaron {n_invalidas} registros con coordenadas fuera de Colombia")
    
    return df_filtrado

# Función para procesar el CSV
def procesar_csv(df):
    # Verificar columnas obligatorias
    columnas_requeridas = ['LAT', 'LON', 'YEAR', 'MO', 'DY', 'ALLSKY_KT', 'ALLSKY_SFC_SW_DWN']
    if not all(col in df.columns for col in columnas_requeridas):
        st.error("Faltan columnas requeridas en el CSV")
        return None
    
    # Filtrar coordenadas
    df = filtrar_coordenadas(df)
    if df is None:
        return None
    
    # Seleccionar columnas específicas
    df = df[['LAT', 'LON', 'ALLSKY_KT', 'ALLSKY_SFC_SW_DWN']]
    
    return df

# Datos de ejemplo
datos_ejemplo = {
    'LAT': [6.2530, 4.6097, 3.4372, 10.3910],  # Última coordenada válida (La Guajira)
    'LON': [-75.5736, -74.0817, -76.5225, -72.9408],
    'ALLSKY_KT': [100, 80, 90, 85],
    'ALLSKY_SFC_SW_DWN': [200, 180, 190, 185]
}

# Procesamiento de datos
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df = procesar_csv(df)
        
        # Si falla el procesamiento, usar ejemplo
        if df is None:
            st.info("Usando datos de ejemplo debido a problemas con el archivo subido")
            df = pd.DataFrame(datos_ejemplo)
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        df = pd.DataFrame(datos_ejemplo)
else:
    st.info("👆 Carga tu CSV o usa los datos de ejemplo")
    df = pd.DataFrame(datos_ejemplo)

# Asegurar que tenemos las columnas especificadas
if 'ALLSKY_KT' not in df.columns or 'ALLSKY_SFC_SW_DWN' not in df.columns:
    st.error("Faltan las columnas ALLSKY_KT o ALLSKY_SFC_SW_DWN en el archivo CSV")
    st.stop()

# Crear el mapa
fig = px.scatter_mapbox(
    df, 
    lat='LAT', 
    lon='LON',
    color='ALLSKY_KT',
    size=[3]*len(df),
    hover_name='LAT',
    color_continuous_scale='plasma',
    zoom=4,
    mapbox_style='open-street-map',
    opacity=0.45,
    title='Mapa de Calor por Puntos Geográficos'
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

# Descargar datos procesados
st.sidebar.header("Descargar Datos")
if st.sidebar.button("Descargar CSV"):
    csv = df.to_csv(index=False)
    st.sidebar.download_button(
        label="Descargar CSV",
        data=csv,
        file_name='datos_procesados.csv',
        mime='text/csv',
    )
