import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(layout="wide")
st.title("🗺️ Mapa de Calor de Colombia")

# Función para validar y filtrar coordenadas
def filtrar_coordenadas(df):
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
    columnas_requeridas = ['LAT', 'LON', 'YEAR', 'MO', 'DY', 'ALLSKY_KT', 'ALLSKY_SFC_SW_DWN']
    if not all(col in df.columns for col in columnas_requeridas):
        st.error("Faltan columnas requeridas en el CSV")
        return None
    df = filtrar_coordenadas(df)
    if df is None:
        return None
    return df[['LAT', 'LON', 'ALLSKY_KT', 'ALLSKY_SFC_SW_DWN']]

# Función para cargar datos de ejemplo
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

# Función para crear el mapa
def crear_mapa(df, zoom_level):
    fig = px.scatter_mapbox(
        df, 
        lat='LAT', 
        lon='LON', 
        color='ALLSKY_KT',
        size=[3]*len(df),
        hover_name='LAT',
        color_continuous_scale='plasma',
        zoom=zoom_level,
        mapbox_style='open-street-map',
        center={'lat': 4.5709, 'lon': -74.2973},
        title='Mapa de Calor por Puntos Geográficos'
    )
    fig.update_traces(marker=dict(opacity=0.45))
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=600)
    return fig

# Función para analizar y mostrar datos
def analizar_datos(df):
    st.subheader("📊 Análisis Detallado")
    tab1, tab2, tab3 = st.tabs(["📈 Zonas con Mayor Radiación", "🌞 Potencial para Parques Solares", "📝 Conclusiones"])

    with tab1:
        st.subheader("Análisis de Zonas con Mayor Radiación Solar")
        with st.expander("Ver Análisis General"):
            top_zonas = df.nlargest(5, 'ALLSKY_SFC_SW_DWN')
            st.write("Top 5 Zonas con Mayor Radiación:")
            st.dataframe(top_zonas[['LAT', 'LON', 'ALLSKY_SFC_SW_DWN']])
            df['Region'] = df.apply(lambda x: get_region(x['LAT'], x['LON']), axis=1)
            region_avg = df.groupby('Region')['ALLSKY_SFC_SW_DWN'].mean().sort_values(ascending=False)
            st.bar_chart(region_avg)

    with tab2:
        st.subheader("Zonas Óptimas para Parques Solares")
        with st.expander("Criterios de Evaluación"):
            st.write("""
            Pa' determinar las mejores zonas, analizamos:
            - Radiación solar promedio ☀️
            - Claridad del cielo 🌤️
            - Estabilidad en mediciones 📊
            """)
        df['Viabilidad'] = (df['ALLSKY_SFC_SW_DWN'] * 0.6 + df['ALLSKY_KT'] * 0.4)
        top_lugares = df.nlargest(3, 'Viabilidad')
        st.write("Top 3 Ubicaciones Recomendadas:")
        for idx, row in top_lugares.iterrows():
            st.metric(f"Ubicación {idx + 1}", f"Lat: {row['LAT']:.2f}, Lon: {row['LON']:.2f}", f"Viabilidad: {row['Viabilidad']:.2f}")

    with tab3:
        st.subheader("Conclusiones del Análisis")
        st.write("""
        💫 **Hallazgos Principales:**
        1. **Zonas Más Prometedoras:**
           - La región con más potencial es [región con mayor promedio]
           - Encontramos puntos súper pilos en [coordenadas específicas]
        2. **Recomendaciones:**
           - Los mejores lugares pa' montar parques solares están en [áreas específicas]
           - La época del año más chimba pa' aprovechar es [temporada]
        3. **Consideraciones Importantes:**
           - Hay que tener en cuenta la variabilidad del clima
           - Es importante revisar la infraestructura cercana
           - Se debe considerar el acceso a las zonas
        """)
        if st.button("Descargar Informe Completo 📑"):
            st.info("¡Proximamente! Estamos armando un informe más completico 🚀")

# Cargar datos
uploaded_file = st.file_uploader("📄 Ingresar archivo CSV", type=['csv'])
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df = procesar_csv(df)
        if df is None:
            st.info("Usando datos de ejemplo debido a problemas con el archivo subido")
            df = cargar_datos_ejemplo()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        df = cargar_datos_ejemplo()
else:
    st.info("👆 Carga tu CSV o usa los datos de ejemplo")
    df = cargar_datos_ejemplo()

# Control de zoom
st.sidebar.header("Controles del Mapa")
zoom_level = st.sidebar.slider("Nivel de Zoom", 4, 15, 6)

# Crear y mostrar el mapa
fig = crear_mapa(df, zoom_level)
st.plotly_chart(fig, use_container_width=True)

# Mostrar datos en una tabla desplegable
with st.expander("Ver datos"):
    st.dataframe(df)

# Descargar datos procesados
st.sidebar.header("Descargar Datos")
if st.sidebar.button("Descargar CSV"):
    csv = df.to_csv(index=False)
    st.sidebar.download_button(label="Descargar CSV", data=csv, file_name='datos_procesados.csv', mime='text/csv')

# Botón para descargar el mapa como PNG
st.sidebar.header("¡Llevate el mapa pa' la casa! 📸")
if st.sidebar.button("Descargar Mapa como PNG"):
    fig.write_image("mapa_temporal.png", scale=2)
    with open("mapa_temporal.png", "rb") as file:
        btn = st.sidebar.download_button(label="¡Bajate el mapa! 🗺️", data=file, file_name="mapa_calor_colombia.png", mime="image/png")
