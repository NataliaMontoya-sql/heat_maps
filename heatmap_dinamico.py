import pandas as pd
import streamlit as st
import plotly.express as px
import folium
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_folium import st_folium

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Proyecto Solaris",
    page_icon="☀️",
    layout="wide"
)
st.title("Proyecto Solaris")
st.sidebar.title("Opciones de Navegación")

# Función de carga de datos unificada
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
        if lat > 8: return "Caribe"
        if lat < 2: return "Sur"
        if lon < -75: return "Pacífico"
        return "Andina"
    
    df['Region'] = df.apply(lambda x: get_region(x['LAT'], x['LON']), axis=1)
    
    return df

df_all = cargar_datos()

# Función para crear mapas climáticos mejorada
def crear_mapa_clima(df, columna, titulo):
    # Configuración de escalas por variable
    escalas = {
        "humedad": {"radio": 0.5, "color": "Blues"},
        "precipitacion": {"radio": 0.01, "color": "Greens"},
        "temperatura": {"radio": 1, "color": "Reds"},
        "ALLSKY_KT": {"radio": 3, "color": "Oranges"}
    }
    
    mapa = folium.Map(
        location=[4.5709, -74.2973],  # Centro de Colombia
        zoom_start=5,
        tiles='CartoDB positron'
    )
    
    # Añadir capa de calor
    heat_data = [[row['LAT'], row['LON'], row[columna]] for _, row in df.iterrows()]
    folium.plugins.HeatMap(
        heat_data,
        radius=15,
        gradient={0.4: 'blue', 0.6: 'lime', 0.8: 'orange', 1: 'red'},
        blur=15
    ).add_to(mapa)
    
    return mapa

# Menú de navegación
menu = st.sidebar.selectbox(
    "Selecciona una opción:",
    ["Inicio", "Datos", "Visualización", "Mapa Principal", 
     "Mapas Climáticos", "Análisis Detallado", 
     "Matriz de Correlación", "Percentiles"]
)

# Contenido de cada sección
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
        año = st.selectbox("Seleccione el año", df_all["YEAR"].unique())
        lat = st.selectbox("Latitud", df_all["LAT"].unique())
        lon = st.selectbox("Longitud", df_all["LON"].unique())
    
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
    
    mapa = crear_mapa_clima(df_all, variable, variable.capitalize())
    st_folium(mapa, width=1200, height=600)

elif menu == "Análisis Detallado":
    st.subheader("Comparación Regional")
    
    df_region = df_all.groupby('Region').agg({
        'ALLSKY_KT': 'mean',
        'temperatura': 'mean',
        'precipitacion': 'mean'
    }).reset_index()
    
    fig = px.bar(
        df_region.melt(id_vars='Region'),
        x='Region',
        y='value',
        color='variable',
        barmode='group',
        title="Indicadores Promedio por Región",
        labels={'value': 'Valor Promedio'}
    )
    st.plotly_chart(fig, use_container_width=True)

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
    
    st.map(df_top[['LAT', 'LON']], zoom=4)

if __name__ == "__main__":
    st.sidebar.info("Ejecuta la aplicación con: streamlit run nombre_del_script.py")
