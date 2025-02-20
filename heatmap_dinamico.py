import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(layout="wide")
st.title("🗺️ Mapa de Calor de Colombia")

# Añadir el uploader de archivos
uploaded_file = st.file_uploader("Ingresar archivo CSV", type=['csv'])

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
    
    # Seleccionar columna numérica
    columnas_numericas = df.select_dtypes(include=['float64', 'int64']).columns
    columnas_numericas = [col for col in columnas_numericas if col not in ['LAT', 'LON']]
    
    if not columnas_numericas:
        st.error("No hay columnas numéricas para visualizar")
        return None
    
    columna_valor = st.selectbox("Selecciona la columna a visualizar", columnas_numericas)
    df['valor'] = df[columna_valor]
    
    return df

# Datos de ejemplo mejorados
datos_ejemplo = {
    'LAT': [6.2530, 4.6097, 3.4372, 10.3910],  # Última coordenada válida (La Guajira)
    'LON': [-75.5736, -74.0817, -76.5225, -72.9408],
    'YEAR': [2020, 2021, 2022, 2023],
    'MO': [1, 2, 3, 4],
    'DY': [15, 20, 25, 30],
    'ALLSKY_KT': [100, 80, 90, 85],
    'ALLSKY_SFC_SW_DWN': [200, 180, 190, 185]
}

# Procesamiento de datos
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df = procesar_csv(df)
        
        # Si falla el procesamiento, usar ejemplo
        if df is None or 'valor' not in df.columns:
            st.info("Usando datos de ejemplo debido a problemas con el archivo subido")
            df = pd.DataFrame(datos_ejemplo)
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        df = pd.DataFrame(datos_ejemplo)
else:
    st.info("👆 Carga tu CSV o usa los datos de ejemplo")
    df = pd.DataFrame(datos_ejemplo)

# Asegurar que tenemos la columna 'valor'
if 'valor' not in df.columns:
    df['valor'] = df['ALLSKY_KT']  # Valor por defecto

# Filtrado seguro de valores
try:
    valor_min = float(df['valor'].min())
    valor_max = float(df['valor'].max())
except KeyError:
    st.error("Error crítico: No se pudo determinar el rango de valores")
    st.stop()

# Calcular media, mediana, latitud y longitud por departamento (en este caso, agrupamos por LAT y LON)
if 'departamento' not in df.columns:
    df['departamento'] = df.apply(lambda row: f"Punto ({row['LAT']}, {row['LON']})", axis=1)

resumen_departamentos = df.groupby('departamento').agg({
    'LAT': 'mean',
    'LON': 'mean',
    'ALLSKY_KT': ['mean', 'median'],
    'ALLSKY_SFC_SW_DWN': ['mean', 'median']
}).reset_index()

# Renombrar columnas para mejor visualización
resumen_departamentos.columns = ['Departamento', 'Latitud Media', 'Longitud Media', 
                                 'Media ALLSKY_KT', 'Mediana ALLSKY_KT', 
                                 'Media ALLSKY_SFC_SW_DWN', 'Mediana ALLSKY_SFC_SW_DWN']

# Mostrar resumen de datos
st.write("Resumen de datos por departamento (o punto geográfico):")
st.dataframe(resumen_departamentos)

# Filtrado de datos
st.sidebar.header("Filtros")
valor_min = st.sidebar.number_input("Valor mínimo", min_value=float(df['valor'].min()), max_value=float(df['valor'].max()), value=float(df['valor'].min()))
valor_max = st.sidebar.number_input("Valor máximo", min_value=float(df['valor'].min()), max_value=float(df['valor'].max()), value=float(df['valor'].max()))
df_filtrado = df[(df['valor'] >= valor_min) & (df['valor'] <= valor_max)]

# Personalización del mapa
st.sidebar.header("Personalización del Mapa")
mapa_estilo = st.sidebar.selectbox("Estilo del Mapa", ["carto-positron", "open-street-map", "stamen-terrain"])
escala_colores = st.sidebar.selectbox("Escala de Colores", ["Viridis", "Plasma", "Inferno", "Magma", "Cividis"])
zoom_level = st.sidebar.slider("Nivel de Zoom", min_value=1, max_value=15, value=5)

# Crear el mapa
fig = px.scatter_mapbox(
    df_filtrado, 
    lat='LAT', 
    lon='LON',
    color='valor',
    size=[20]*len(df_filtrado),
    hover_name='departamento',
    color_continuous_scale=escala_colores.lower(),
    zoom=zoom_level,
    mapbox_style=mapa_estilo,
    center={'lat': 4.5709, 'lon': -74.2973},
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
st.dataframe(df_filtrado)

# Descargar datos procesados
st.sidebar.header("Descargar Datos")
if st.sidebar.button("Descargar CSV"):
    csv = df_filtrado.to_csv(index=False)
    st.sidebar.download_button(
        label="Descargar CSV",
        data=csv,
        file_name='datos_procesados.csv',
        mime='text/csv',
    )
