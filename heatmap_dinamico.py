import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(layout="wide", page_title="Análisis Solar Colombia")
st.title("🗺️ Mapa de Calor y Análisis Solar de Colombia")

# =============================================
# FUNCIONES DE PROCESAMIENTO Y CONFIGURACIÓN
# =============================================

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

def filtrar_coordenadas(df):
    df_filtrado = df[(df['LAT'].between(-4.23, 12.45)) & (df['LON'].between(-79.00, -66.87))].copy()
    if df_filtrado.empty:
        st.error("¡No hay coordenadas válidas dentro de Colombia!")
        return None
    registros_eliminados = len(df) - len(df_filtrado)
    if registros_eliminados > 0:
        st.warning(f"Se eliminaron {registros_eliminados} registros con coordenadas fuera de Colombia")
    return df_filtrado

def procesar_csv(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        columnas_requeridas = {'LAT', 'LON', 'YEAR', 'MO', 'DY', 'ALLSKY_KT', 'ALLSKY_SFC_SW_DWN'}
        if not columnas_requeridas.issubset(df.columns):
            st.error("El CSV no contiene todas las columnas necesarias.")
            return None
        return filtrar_coordenadas(df)
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
        return None

def get_region(lat, lon):
    if lat > 8:
        return "Caribe"
    elif lat < 2:
        return "Sur"
    elif lon < -75:
        return "Pacífico"
    return "Andina"

def crear_mapa(df, zoom_level):
    fig = px.scatter_mapbox(
        df, lat='LAT', lon='LON', color='ALLSKY_KT',
        size=[3]*len(df), hover_name='LAT', zoom=zoom_level,
        color_continuous_scale='plasma', mapbox_style='open-street-map',
        center={'lat': 4.5709, 'lon': -74.2973}
    )
    fig.update_traces(marker=dict(opacity=0.45))
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=700)
    return fig

# =============================================
# INTERFAZ DE USUARIO
# =============================================

with st.sidebar:
    st.header("🌄 Panel de Control")
    uploaded_file = st.file_uploader("📄 Subir archivo CSV", type=['csv'])
    pagina_actual = st.radio("Navegación", ["🗺 Mapa Principal", "📊 Análisis Detallado", "📅 Comparativa Histórica", "📦 Datos"])
    zoom_level = st.slider("Nivel de Zoom", 4, 15, 6)

# =============================================
# CARGA DE DATOS
# =============================================

df = procesar_csv(uploaded_file) if uploaded_file else cargar_datos_ejemplo()

if df is not None:
    df['Region'] = df.apply(lambda x: get_region(x['LAT'], x['LON']), axis=1)

# =============================================
# PÁGINAS PRINCIPALES
# =============================================

if pagina_actual == "🗺 Mapa Principal" and df is not None:
    st.plotly_chart(crear_mapa(df, zoom_level), use_container_width=True)

elif pagina_actual == "📊 Análisis Detallado" and df is not None:
    st.header("📈 Análisis Profundo de Datos")
    top_zonas = df.nlargest(5, 'ALLSKY_SFC_SW_DWN')
    st.subheader("Top 5 Zonas de Radiación")
    st.dataframe(top_zonas.style.background_gradient(cmap='YlOrRd'))
    region_avg = df.groupby('Region')['ALLSKY_SFC_SW_DWN'].mean()
    st.bar_chart(region_avg)
    df['Viabilidad'] = (df['ALLSKY_SFC_SW_DWN'] * 0.6 + df['ALLSKY_KT'] * 0.4)
    top3 = df.nlargest(3, 'Viabilidad')
    for i, (_, row) in enumerate(top3.iterrows()):
        st.metric(f"🥇 Ubicación {i+1}", f"{row['Viabilidad']:.2f} pts", f"Lat: {row['LAT']:.4f} Lon: {row['LON']:.4f}")

elif pagina_actual == "📅 Comparativa Histórica":
    st.header("📆 Análisis Temporal")
    
    st.subheader("Tendencia Anual")
    df_anual = df.groupby('YEAR')[['ALLSKY_KT', 'ALLSKY_SFC_SW_DWN']].mean().reset_index()
    fig_line = px.line(
        df_anual, x='YEAR', y=['ALLSKY_KT', 'ALLSKY_SFC_SW_DWN'],
        markers=True, labels={'value': 'Valor', 'variable': 'Indicador'}
    )
    st.plotly_chart(fig_line, use_container_width=True)
    
elif pagina_actual == "📦 Datos":
    st.header("📂 Conjunto de Datos Completo")
    
    if df is not None and not df.empty:
        min_rad = st.slider("Radiación Mínima", float(df['ALLSKY_SFC_SW_DWN'].min()), float(df['ALLSKY_SFC_SW_DWN'].max()), 150.0)
        max_kt = st.slider("Claridad Máxima", float(df['ALLSKY_KT'].min()), float(df['ALLSKY_KT'].max()), 95.0)
        df_filtrado = df[(df['ALLSKY_SFC_SW_DWN'] >= min_rad) & (df['ALLSKY_KT'] <= max_kt)]
        st.dataframe(df_filtrado)
        st.download_button("📥 Exportar Datos", df_filtrado.to_csv(index=False), "datos_filtrados.csv", "text/csv")
    else:
        st.warning("No hay datos disponibles para mostrar.")
