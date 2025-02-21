import streamlit as st 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(layout="wide", page_title="Análisis Solar Colombia")
st.title("🗺️ Mapa de Calor y Análisis Solar de Colombia")

# =============================================
# FUNCIONES DE PROCESAMIENTO Y CONFIGURACIÓN
# =============================================

def procesar_csv(df):
    columnas_requeridas = ['LAT', 'LON', 'YEAR', 'MO', 'DY', 'ALLSKY_KT', 'ALLSKY_SFC_SW_DWN']
    if not all(col in df.columns for col in columnas_requeridas):
        st.error("Faltan columnas requeridas en el CSV")
        return None
    return df

def cargar_datos_ejemplo():
    return pd.DataFrame({
        'LAT': [6.2530, 4.6097, 3.4372, 10.3910],
        'LON': [-75.5736, -74.0817, -76.5225, -72.9408],
        'YEAR': [2020, 2021, 2022, 2023],
        'MO': [1, 2, 3, 4],
        'DY': [15, 20, 25, 30],
        'ALLSKY_KT': [100, 80, 90, 85],
        'ALLSKY_SFC_SW_DWN': [200, 180, 190, 185]
    })

# =============================================
# COMPONENTES DE LA BARRA LATERAL (SIDEBAR)
# =============================================

with st.sidebar:
    st.header("🌄 Panel de Control")
    
    uploaded_file = st.file_uploader("📄 Subir archivo CSV", type=['csv'])
    
    pagina_actual = st.radio("Navegación", 
                           ["🗺 Mapa Principal", 
                            "📊 Análisis Detallado", 
                            "📅 Comparativa Histórica", 
                            "📦 Datos"])

# =============================================
# CARGA DE DATOS (SCOPE GLOBAL)
# =============================================

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df = procesar_csv(df) or cargar_datos_ejemplo()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        df = cargar_datos_ejemplo()
else:
    df = cargar_datos_ejemplo()

# =============================================
# CONTENIDO PRINCIPAL BASADO EN NAVEGACIÓN
# =============================================

# Página de comparativa histórica (sin filtro por año)
if pagina_actual == "📅 Comparativa Histórica":
    st.header("📆 Análisis Temporal")
    
    st.subheader("Tendencia Anual")
    df_anual = df.groupby('YEAR')[['ALLSKY_KT', 'ALLSKY_SFC_SW_DWN']].mean().reset_index()
    fig_line = px.line(
        df_anual, x='YEAR', y=['ALLSKY_KT', 'ALLSKY_SFC_SW_DWN'],
        markers=True, labels={'value': 'Valor', 'variable': 'Indicador'}
    )
    st.plotly_chart(fig_line, use_container_width=True)

# Página de datos (corregida para imprimir la tabla correctamente)
elif pagina_actual == "📦 Datos":
    st.header("📂 Conjunto de Datos Completo")
    
    if df is not None and not df.empty:
        st.dataframe(df)
    else:
        st.warning("No hay datos disponibles para mostrar.")
