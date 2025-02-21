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
    columnas_requeridas = ['LAT', 'LON', 'YEAR', 'MO', 'DY', 'ALLSKY_KT', 'ALLSKY_SFC_SW_DWN']
    if not all(col in df.columns for col in columnas_requeridas):
        st.error("Faltan columnas requeridas en el CSV")
        return None
    df = filtrar_coordenadas(df)
    if df is None:
        return None
    df = df[['LAT', 'LON', 'ALLSKY_KT', 'ALLSKY_SFC_SW_DWN']]
    return df

# Datos de ejemplo mejorados
datos_ejemplo = {
    'LAT': [6.2530, 4.6097, 3.4372, 10.3910],
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
        if df is None:
            st.info("Usando datos de ejemplo debido a problemas con el archivo subido")
            df = pd.DataFrame(datos_ejemplo)
    except Exception as e:
        st.error(f"Error: {str(e)}")
        df = pd.DataFrame(datos_ejemplo)
else:
    st.info("👆 Carga tu CSV o usa los datos de ejemplo")
    df = pd.DataFrame(datos_ejemplo)

# Agregar control de zoom en la barra lateral
st.sidebar.header("Controles del Mapa")
zoom_level = st.sidebar.slider("Nivel de Zoom", 4, 15, 6)

# Crear el mapa con los nuevos ajustes
fig = px.scatter_mapbox(
    df, 
    lat='LAT', 
    lon='LON', 
    color='ALLSKY_KT',
    size=[3]*len(df),  # Puntos más pequeños
    hover_name='LAT',
    color_continuous_scale='plasma',
    zoom=zoom_level,  # Zoom controlado por el slider
    mapbox_style='open-street-map',
    center={'lat': 4.5709, 'lon': -74.2973},
    title='Mapa de Calor por Puntos Geográficos'
)

# Ajustar la opacidad de los puntos al 45%
fig.update_traces(marker=dict(opacity=0.45))

# Ajustar el layout y agregar la barra de zoom
fig.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    height=600,
    mapbox=dict(
        style='open-street-map',
        zoom=zoom_level
    )
)

# Mostrar el mapa
st.plotly_chart(fig, use_container_width=True)

# Creamos las pestañitas pa' todo el análisis
st.header("📊 Análisis Detallado")
tab1, tab2, tab3 = st.tabs([
    "📈 Zonas con Mayor Radiación",
    "🌞 Potencial para Parques Solares",
    "📝 Conclusiones"
])

with tab1:
    st.subheader("Análisis de Zonas con Mayor Radiación Solar")
    
    # Análisis general
    with st.expander("Ver Análisis General"):
        # Top 5 zonas con mayor radiación
        top_zonas = df.nlargest(5, 'ALLSKY_SFC_SW_DWN')
        st.write("Top 5 Zonas con Mayor Radiación:")
        st.dataframe(top_zonas[['LAT', 'LON', 'ALLSKY_SFC_SW_DWN']])
        
        # Promedio por región
        st.write("Promedio de Radiación por Región:")
        # Definimos regiones básicas de Colombia
        def get_region(lat, lon):
            if lat > 8:
                return "Costa Caribe"
            elif lat < 2:
                return "Sur"
            elif lon < -75:
                return "Pacífico"
            else:
                return "Andina"
        
        df['Region'] = df.apply(lambda x: get_region(x['LAT'], x['LON']), axis=1)
        region_avg = df.groupby('Region')['ALLSKY_SFC_SW_DWN'].mean().sort_values(ascending=False)
        st.bar_chart(region_avg)

with tab1:
    st.subheader("📊 Análisis por Temporadas")
    
    # Análisis por meses
    df['Mes'] = df['MO'].map({
        1: 'Enero', 2: 'Febrero', 3: 'Marzo',
        4: 'Abril', 5: 'Mayo', 6: 'Junio',
        7: 'Julio', 8: 'Agosto', 9: 'Septiembre',
        10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    })
    
    # Agregamos las temporadas del año
    df['Temporada'] = df['MO'].apply(lambda x: 
        'Temporada Seca' if x in [12, 1, 2, 6, 7, 8] 
        else 'Temporada de Lluvia')
    
    # Gráfico de radiación por mes
    st.write("### Radiación Solar por Mes 🌞")
    monthly_radiation = df.groupby('Mes')['ALLSKY_SFC_SW_DWN'].mean()
    st.line_chart(monthly_radiation)
    
    # Análisis por temporadas
    st.write("### Comportamiento por Temporadas ☔️")
    col1, col2 = st.columns(2)
    
    with col1:
        season_avg = df.groupby('Temporada')['ALLSKY_SFC_SW_DWN'].mean()
        st.bar_chart(season_avg)
    
    with col2:
        st.write("""
        **¿Qué nos dice esto, mi amor?**
        - En temporada seca la radiación está más percha 🌞
        - En temporada de lluvia baja un tris, pero igual sirve 🌧️
        """)
    
    # Análisis de variabilidad
    st.write("### Estabilidad de la Radiación 📈")
    variability = df.groupby('Mes')['ALLSKY_SFC_SW_DWN'].agg(['mean', 'std'])
    variability['cv'] = variability['std'] / variability['mean']
    
    # Gráfico de variabilidad
    import plotly.express as px
    fig_var = px.bar(
        variability.reset_index(),
        x='Mes',
        y='cv',
        title='Variabilidad de la Radiación por Mes'
    )
    st.plotly_chart(fig_var)

    # Mejores zonas por temporada
    st.write("### Mejores Zonas según la Época 🗺️")
    for temporada in df['Temporada'].unique():
        with st.expander(f"Ver mejores zonas en {temporada}"):
            temp_data = df[df['Temporada'] == temporada]
            top_zones = temp_data.nlargest(3, 'ALLSKY_SFC_SW_DWN')
            
            st.write(f"Top 3 Zonas pa' {temporada}:")
            for idx, row in top_zones.iterrows():
                st.metric(
                    f"Zona {idx + 1}",
                    f"Lat: {row['LAT']:.2f}, Lon: {row['LON']:.2f}",
                    f"Radiación: {row['ALLSKY_SFC_SW_DWN']:.2f}"
                )

# Y en la segunda pestaña, le metemos este análisis más completico:
with tab2:
    st.write("### Análisis Avanzado de Ubicaciones 🎯")
    
    # Criterios de evaluación detallados
    evaluation_criteria = {
        'Radiación Solar': df['ALLSKY_SFC_SW_DWN'].max(),
        'Claridad del Cielo': df['ALLSKY_KT'].max(),
        'Estabilidad': -df.groupby(['LAT', 'LON'])['ALLSKY_SFC_SW_DWN'].std().mean()
    }
    
    # Gráfico de radar para mejores ubicaciones
    import plotly.graph_objects as go
    
    fig_radar = go.Figure()
    top_locations = df.nlargest(3, 'Viabilidad')
    
    for idx, row in top_locations.iterrows():
        fig_radar.add_trace(go.Scatterpolar(
            r=[row['ALLSKY_SFC_SW_DWN'], row['ALLSKY_KT'], 
               -df.groupby(['LAT', 'LON'])['ALLSKY_SFC_SW_DWN'].std().loc[row['LAT'], row['LON']]],
            theta=['Radiación', 'Claridad', 'Estabilidad'],
            name=f'Ubicación {idx + 1}'
        ))
    
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])))
    st.plotly_chart(fig_radar)

with tab2:
    st.subheader("Zonas Óptimas para Parques Solares")
    
    # Criterios para parques solares
    with st.expander("Criterios de Evaluación"):
        st.write("""
        Pa' determinar las mejores zonas, analizamos:
        - Radiación solar promedio ☀️
        - Claridad del cielo 🌤️
        - Estabilidad en mediciones 📊
        """)
    
    # Calcular índice de viabilidad
    df['Viabilidad'] = (
        df['ALLSKY_SFC_SW_DWN'] * 0.6 +  # Peso mayor a la radiación
        df['ALLSKY_KT'] * 0.4  # Peso menor a la claridad
    )
    
    # Mostrar mejores ubicaciones
    top_lugares = df.nlargest(3, 'Viabilidad')
    st.write("Top 3 Ubicaciones Recomendadas:")
    for idx, row in top_lugares.iterrows():
        st.metric(
            f"Ubicación {idx + 1}",
            f"Lat: {row['LAT']:.2f}, Lon: {row['LON']:.2f}",
            f"Viabilidad: {row['Viabilidad']:.2f}"
        )

with tab3:
    st.subheader("Conclusiones del Análisis")
    
    # Conclusiones generales
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

    # Botón pa' descargar el informe completo
    if st.button("Descargar Informe Completo 📑"):
        # Aquí podemos generar un PDF o un archivo más detallado
        st.info("¡Proximamente! Estamos armando un informe más completico 🚀")

# Mostrar los datos en una tabla desplegable
with st.expander("Ver datos"):
    st.dataframe(df)

# Descargar datos procesados
st.sidebar.header("Descargar Datos")
if st.sidebar.button("Descargar CSV"):
    csv = df.to_csv(index=False)
    st.sidebar.download_button(
        label="Descargar CSV", 
        data=csv,
        file_name='datos_procesados.csv',
        mime='text/csv'
    )


# Botón para descargar el mapa como PNG
st.sidebar.header("¡Llevate el mapa pa' la casa! 📸")
if st.sidebar.button("Descargar Mapa como PNG"):
    # Guardamos ese visaje temporalmente
    fig.write_image("mapa_temporal.png", scale=2)  # scale=2 para que quede HD
    
    # Leemos el archivo para descargarlo
    with open("mapa_temporal.png", "rb") as file:
        btn = st.sidebar.download_button(
            label="¡Bajate el mapa! 🗺️",
            data=file,
            file_name="mapa_calor_colombia.png",
            mime="image/png"
        )
