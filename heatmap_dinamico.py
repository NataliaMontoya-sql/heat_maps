import pandas as pd
import streamlit as st
import plotly.express as px
import folium
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
from branca.element import Template, MacroElement

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

# Función para crear mapas climáticos mejorada con leyenda
def crear_mapa_clima(df, columna, titulo):
    # Configuración de escalas por variable
    escalas = {
        "humedad": {"min": 0, "max": 100, "color": "Blues", "unidad": "%"},
        "precipitacion": {"min": 0, "max": df['precipitacion'].quantile(0.95), "color": "Greens", "unidad": "mm/día"},
        "temperatura": {"min": df['temperatura'].min(), "max": df['temperatura'].max(), "color": "Reds", "unidad": "°C"},
        "ALLSKY_KT": {"min": 0, "max": 1, "color": "Oranges", "unidad": "índice"}
    }
    
    mapa = folium.Map(
        location=[4.5709, -74.2973],  # Centro de Colombia
        zoom_start=5,
        tiles='CartoDB positron'
    )
    
    # Definir gradiente y título según la variable
    escala = escalas.get(columna, {"min": 0, "max": 1, "color": "Blues", "unidad": ""})
    titulo_completo = f"{titulo} ({escala['unidad']})"
    
    # Añadir capa de calor
    heat_data = [[row['LAT'], row['LON'], row[columna]] for _, row in df.iterrows()]
    folium.plugins.HeatMap(
        heat_data,
        radius=15,
        gradient={0.4: 'blue', 0.6: 'lime', 0.8: 'orange', 1: 'red'},
        min_opacity=0.5,
        blur=15,
        max_val=escala['max']
    ).add_to(mapa)
    
    # Añadir leyenda
    template = """
    {% macro html(this, kwargs) %}
    <div style='position: fixed; 
        bottom: 50px; left: 50px; width: 200px; height: 120px; 
        border:2px solid grey; z-index:9999; font-size:14px;
        background-color: white; padding: 10px; border-radius: 5px;'>
        
        <p style="margin: 0; text-align: center; font-weight: bold;">{{ title }}</p>
        <div style="display: flex; align-items: center; margin-top: 10px;">
            <div style="background: linear-gradient(to right, blue, lime, orange, red); 
                  width: 100%; height: 20px;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 5px;">
            <span>{{ min_val }}</span>
            <span>{{ max_val }}</span>
        </div>
    </div>
    {% endmacro %}
    """
    
    macro = MacroElement()
    macro._template = Template(template)
    macro.template_vars = {
        'title': titulo_completo,
        'min_val': f"{escala['min']:.1f}",
        'max_val': f"{escala['max']:.1f}"
    }
    mapa.get_root().add_child(macro)
    
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
    
    mapa = crear_mapa_clima(df_all, variable, variable.capitalize())
    st_folium(mapa, width=1200, height=600)

    # Información adicional sobre la variable seleccionada
    st.subheader(f"Información sobre {variable}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Valor Promedio", f"{df_all[variable].mean():.2f}")
    with col2:
        st.metric("Valor Mínimo", f"{df_all[variable].min():.2f}")
    with col3:
        st.metric("Valor Máximo", f"{df_all[variable].max():.2f}")

elif menu == "Análisis Detallado":
    st.subheader("Comparación Regional")
    
    df_region = df_all.groupby('Region').agg({
        'ALLSKY_KT': 'mean',
        'temperatura': 'mean',
        'precipitacion': 'mean',
        'humedad': 'mean'
    }).reset_index()
    
    # Añadir explicación
    st.info("Este gráfico muestra los valores promedio de cada variable por región, ayudando a identificar las mejores ubicaciones para instalaciones solares.")
    
    # Permitir seleccionar qué variables mostrar
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
    - **Valores cercanos a 1:** Correlación positiva fuerte (cuando una variable aumenta, la otra también)
    - **Valores cercanos a -1:** Correlación negativa fuerte (cuando una variable aumenta, la otra disminuye)
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
    
    # Añadir más información sobre las zonas de alto potencial
    st.write(f"Se muestran ubicaciones con índice de claridad solar > {threshold:.3f} (percentil {percentil*100:.0f})")
    
    # Mostrar estadísticas por región para zonas de alto potencial
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

# Sección de información y ayuda
st.sidebar.markdown("---")
st.sidebar.info("""
**Proyecto Solaris** - Análisis de potencial para energía solar en Colombia.
""")

# Aseguramos que el script se ejecute correctamente en Streamlit
if __name__ == "__main__":
    pass
