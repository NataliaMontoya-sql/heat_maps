import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(layout="wide")
st.title("Mapa de Calor de Colombia 🇨🇴")

# Añadir el uploader de archivos
uploaded_file = st.file_uploader("Subir archivo CSV", type=['csv'])

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
    st.info("👆 Subí tu CSV o usa los datos de ejemplo")
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

# [El resto del código manteniendo los controles de zoom y visualización...]
