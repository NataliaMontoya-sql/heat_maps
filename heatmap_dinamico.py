import pandas as pd
import streamlit as st
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import pydeck as pdk

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Proyecto Solaris",
    page_icon="☀️",
    layout="wide"
)
st.title("Proyecto Solaris")
st.sidebar.title("Opciones de Navegación")

@st.cache_data
def cargar_datos():
    df = pd.read_csv("datos_unificados (2).csv")
    
    # Renombrar columnas para consistencia
    df = df.rename(columns={
        "RH2M": "humedad",
        "PRECTOTCORR": "precipitacion",
        "T2M": "temperatura"
    })
    
    # Crear columna de fecha
    df['Fecha'] = pd.to_datetime(df.astype(str).loc[:, ["YEAR", "MO", "DY"]].agg('-'.join, axis=1))
    
    # Clasificación de regiones
    def get_region(lat, lon):
        if lat > 8:
            return "Caribe"
        if lat < 2:
            return "Sur"
        if lon < -75:
            return "Pacífico"
        return "Andina"
    
    df['Region'] = df.apply(lambda x: get_region(x['LAT'], x['LON']), axis=1)
    
    return df

df_all = cargar_datos()

def crear_mapa_clima_streamlit(df, columna, titulo):
    """
    Se crea un mapa de calor usando pydeck.
    Se utiliza una capa HexagonLayer para simular la distribución y se define un
    rango de colores acorde a la variable.
    """
    # Determinar escala en función de la variable
    if columna == "humedad":
        min_val, max_val = 0, 100
        color_range = [[0, 0, 255], [0, 255, 255]]
    elif columna == "precipitacion":
        min_val, max_val = 0, df['precipitacion'].quantile(0.95)
        color_range = [[230, 240, 230], [0, 128, 0]]
    elif columna == "temperatura":
        min_val, max_val = df['temperatura'].min(), df['temperatura'].max()
        color_range = [[255, 200, 200], [255, 0, 0]]
    else:
        min_val, max_val = 0, 1
        color_range = [[200, 200, 200], [0, 0, 0]]
    
    # Crear una capa de hexágonos (HexagonLayer)
    layer = pdk.Layer(
        "HexagonLayer",
        data=df,
        get_position='[LON, LAT]',
        auto_highlight=True,
        elevation_scale=50,
        pickable=True,
        extruded=True,
        coverage=1,
        radius=15000,
        get_weight=columna
    )
    
    # Configuración de la vista
    view_state = pdk.ViewState(
        latitude=4.5709,
        longitude=-74.2973,
        zoom=5,
        pitch=40,
    )
    
    # Crear el mapa
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"html": f"<b>{titulo}</b><br/>Valor: {{{columna}}}"},
    )
    
    return r, min_val, max_val, color_range

# Menú de navegación
menu = st.sidebar.selectbox(
    "Selecciona una opción:",
    ["Inicio", "Datos", "Visualización", "Mapa Principal", 
     "Mapas Climáticos", "Análisis Detallado", "Matriz de Correlación", "Percentiles"]
)

if menu == "Inicio":
    st.subheader("¡Bienvenidos!")
    st.markdown("""
    **Objetivo del dashboard:**  
    Identificar y visualizar las zonas de mayor potencial para la ubicación de parques solares en Colombia,
    contribuyendo al desarrollo de energía limpia y sostenible.
    
    **Secciones disponibles:**
    1. **Datos:** Visualización completa del dataset  
    2. **Visualización:** Análisis temporal por ubicación  
    3. **Mapa Principal:** Radiación solar a nivel nacional  
    4. **Mapas Climáticos:** Variables meteorológicas clave  
    5. **Análisis Detallado:** Comparación por regiones  
    6. **Matriz de Correlación:** Relaciones entre variables  
    7. **Percentiles:** Zonas de mayor potencial
    """)
    
elif menu == "Datos":
    st.subheader("Datos Complejos")
    with st.expander("Descripción de variables"):
        st.markdown("""
        - **ALLSKY_KT:** Índice de claridad del cielo  
        - **ALLSKY_SFC_SW_DWN:** Irradiación superficial  
        - **temperatura:** Temperatura a 2m (°C)  
        - **humedad:** Humedad relativa (%)  
        - **precipitacion:** Precipitación (mm/día)
        """)
    st.dataframe(df_all, use_container_width=True)
    
elif menu == "Visualización":
    st.subheader("Análisis Temporal por Ubicación")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        año = st.selectbox("Seleccione el año", sorted(df_all["YEAR"].unique()))
        lat = st.selectbox("Latitud", sorted(df_all["LAT"].unique()))
        lon = st.selectbox("Longitud", sorted(df_all["LON"].unique()))
    
    df_filtrado = df_all[
        (df_all["YEAR"] == año) &
        (df_all["LAT"] == lat) &
        (df_all["LON"] == lon)
    ]
    
    with col2:
        fig = px.line(
            df_filtrado,
            x='Fecha',
            y=['ALLSKY_KT', 'ALLSKY_SFC_SW_DWN'],
            title=f"Comportamiento temporal en {lat}, {lon}",
            labels={'value': 'Valor', 'variable': 'Indicador'},
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
elif menu == "Mapa Principal":
    st.subheader("Potencial Solar por Ubicación")
    zoom_level = st.sidebar.slider("Nivel de zoom", 4, 12, 6)
    fig = px.density_mapbox(
        df_all,
        lat='LAT',
        lon='LON',
        z='ALLSKY_KT',
        radius=15,
        zoom=zoom_level,
        mapbox_style="carto-positron",
        color_continuous_scale="hot",
        range_color=[df_all['ALLSKY_KT'].quantile(0.1), df_all['ALLSKY_KT'].quantile(0.9)],
        title="Densidad de Potencial Solar"
    )
    st.plotly_chart(fig, use_container_width=True)
    
elif menu == "Mapas Climáticos":
    st.subheader("Variables Meteorológicas")
    variable = st.selectbox(
        "Seleccione variable",
        ["humedad", "precipitacion", "temperatura", "ALLSKY_KT"]
    )
    
    deck_map, min_val, max_val, color_range = crear_mapa_clima_streamlit(df_all, variable, variable.capitalize())
    st.pydeck_chart(deck_map)
    
    # Agregar información de la leyenda
    st.markdown(f"**{variable.capitalize()}**")
    st.markdown(f"Rango: **{min_val:.1f}** a **{max_val:.1f}**")
    st.markdown("Gradiente de colores:")
    st.markdown(
        f"<div style='background: linear-gradient(to right, rgb({color_range[0][0]},{color_range[0][1]},{color_range[0][2]}), rgb({color_range[1][0]},{color_range[1][1]},{color_range[1][2]})); height: 20px; width: 300px;'></div>",
        unsafe_allow_html=True
    )
    
elif menu == "Análisis Detallado":
    st.subheader("Comparación Regional")
    df_region = df_all.groupby('Region').agg({
        'ALLSKY_KT': 'mean',
        'temperatura': 'mean',
        'precipitacion': 'mean',
        'humedad': 'mean'
    }).reset_index()
    
    st.info("Este gráfico muestra los valores promedio de cada variable por región, ayudando a identificar las mejores ubicaciones para instalaciones solares.")
    
    variables_mostrar = st.multiselect(
        "Seleccione variables a comparar",
        ["ALLSKY_KT", "temperatura", "precipitacion", "humedad"],
        default=["ALLSKY_KT"]
    )
    
    if variables_mostrar:
        fig = px.bar(
            df_region.melt(id_vars='Region', value_vars=variables_mostrar),
            x='Region',
            y='value',
            color='variable',
            barmode='group',
            title="Indicadores Promedio por Región",
            labels={'value': 'Valor Promedio', 'variable': 'Indicador'}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Por favor seleccione al menos una variable para mostrar")
    
elif menu == "Matriz de Correlación":
    st.subheader("Relaciones entre Variables")
    corr_matrix = df_all[[
        'ALLSKY_KT',
        'ALLSKY_SFC_SW_DWN',
        'temperatura',
        'humedad',
        'precipitacion'
    ]].corr()
    
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale='RdBu',
        range_color=[-1, 1],
        title="Matriz de Correlación"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    **Interpretación de correlaciones:**
    - **Valores cercanos a 1:** Correlación positiva fuerte  
    - **Valores cercanos a -1:** Correlación negativa fuerte  
    - **Valores cercanos a 0:** Poca o ninguna correlación  
    """)
    
elif menu == "Percentiles":
    st.subheader("Zonas de Alto Potencial")
    percentil = st.slider(
        "Seleccione percentil",
        min_value=70,
        max_value=95,
        value=85,
        step=5
    ) / 100
    threshold = df_all['ALLSKY_KT'].quantile(percentil)
    df_top = df_all[df_all['ALLSKY_KT'] > threshold]
    
    st.write(f"Se muestran ubicaciones con índice de claridad solar > {threshold:.3f} (percentil {percentil*100:.0f})")
    
    regiones_count = df_top.groupby('Region').size().reset_index(name='Conteo')
    fig_regiones = px.pie(
        regiones_count, 
        values='Conteo', 
        names='Region',
        title="Distribución de zonas de alto potencial por región"
    )
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.map(df_top[['LAT', 'LON']], zoom=4)
    with col2:
        st.plotly_chart(fig_regiones, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("""
**Proyecto Solaris** - Análisis de potencial para energía solar en Colombia.
""")
