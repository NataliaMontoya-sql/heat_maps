import pandas as pd
import streamlit as st
import plotly.express as px
import folium
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
from branca.element import Template, MacroElement

# Configuración de la página de Streamlit
st.set_page_config(page_title="Proyecto Solaris", page_icon="", layout="wide")
st.title("Proyecto Solaris")
st.sidebar.title("Opciones de Navegación")

# Funciones de carga de datos
@st.cache_data
def cargar_humedad():
    df = pd.read_csv("datos_agrupados_humedity.csv")
    df = df.rename(columns={"RH2M": "humedad"})
    return df

@st.cache_data
def cargar_precipitacion():
    df = pd.read_csv("datos_agrupados_precipitacion.csv")
    df = df.rename(columns={"PRECTOTCORR": "precipitacion"})
    return df

@st.cache_data
def cargar_temperatura():
    df = pd.read_csv("datos_agrupados_temperature1.csv")
    df = df.rename(columns={"T2M": "temperatura"})
    return df

df_humedad = cargar_humedad()
df_precipitacion = cargar_precipitacion()
df_temperatura = cargar_temperatura()

@st.cache_data
def cargar_datos():
    return pd.read_csv("datos_unificados (2).csv")
df_all = cargar_datos()

# Crear columna 'Fecha' combinando 'YEAR', 'MO', 'DY'
df_all['Fecha'] = pd.to_datetime(
    df_all.astype(str).loc[:, ["YEAR", "MO", "DY"]].agg('-'.join, axis=1)
)

# Función para agregar leyenda a un mapa Folium utilizando MacroElement y Template de branca
def agregar_leyenda(mapa, titulo, items):
    html = """
    {% macro html(this, kwargs) %}
    <div style="
         color: black;
         position: fixed;
         bottom: 50px; left: 50px;
         width: 220px;
         background-color: white;
         border:2px solid grey;
         z-index:9999;
         font-size:14px;
         padding: 10px;
         ">
         <b>""" + titulo + """</b><br>
    """
    for color, descripcion in items:
        html += '<i style="background: ' + color + '; width: 10px; height: 10px; display: inline-block; margin-right: 5px; border-radius: 50%;"></i>' + descripcion + '<br>'
    html += """</div>
    {% endmacro %}"""
    
    template = Template(html)
    macro = MacroElement()
    macro._template = template
    mapa.get_root().add_child(macro)

# Modificamos la función para recibir un parámetro de zoom
def crear_mapa_clima(df, columna, titulo, zoom=6):
    q75 = df[columna].quantile(0.75)
    q50 = df[columna].quantile(0.5)
    max_row = df.loc[df[columna].idxmax()]
    map_center = [max_row["LAT"], max_row["LON"]]
    mapa = folium.Map(location=map_center, zoom_start=zoom)
    
    for _, row in df.iterrows():
        valor = row[columna]
        if valor > q75:
            color = 'green'
        elif valor > q50:
            color = 'orange'
        else:
            color = 'red'
        folium.CircleMarker(
            location=[row['LAT'], row['LON']],
            radius=valor * 0.1,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            popup=f"{titulo}: {valor:.2f}"
        ).add_to(mapa)
        
    # Agregar leyenda al mapa
    leyenda_items = [
        ("green", "Mayor al 75%"),
        ("orange", "Entre 50% y 75%"),
        ("red", "Menor o igual al 50%")
    ]
    agregar_leyenda(mapa, f"Leyenda {titulo}", leyenda_items)
    return mapa

# Menú de navegación en la barra lateral
menu = st.sidebar.selectbox("Selecciona una opción:", [
    "Inicio", "Datos", "Visualización", "Mapa Principal", 
    "Mapas Climáticos", "Análisis Detallado", "Matriz de Correlación", "Percentiles"
])

def get_region(lat, lon):
    if lat > 8:
        return "Caribe"
    elif lat < 2:
        return "Sur"
    elif lon < -75:
        return "Pacífico"
    return "Andina"

df_all['Region'] = df_all.apply(lambda x: get_region(x['LAT'], x['LON']), axis=1)

if menu == "Datos":
    st.subheader("Datos Disponibles")
    st.dataframe(df_all.head(100))

elif menu == "Inicio":
    st.subheader("¡Bienvenidos!")
    st.text("En este dashboard se identifica y visualiza las zonas de mayor potencial para la ubicación de parques solares en Colombia, con el objetivo de impulsar el desarrollo de energía limpia y contribuir a un futuro sostenible.")
    st.markdown(""" 
    El dashboard se divide en las siguientes secciones:
    - Tabla de datos
    - Valores por ubicación en el mapa
    - Mapa de irradiación
    - Mapas de datos climáticos
    - Diagrama de barras de zonas geográficas
    - Matriz de correlación de las variables
    - Mapa con percentiles de irradiación
    """)

elif menu == "Visualización":
    st.subheader("📊 Visualización datos climáticos")
    año = st.sidebar.selectbox("Selecciona el año", df_all["YEAR"].unique())
    df_filtrado = df_all[df_all["YEAR"] == año]
    st.write(f"Mostrando datos para el año: {año}")
    
    fecha_inicio, fecha_fin = st.sidebar.date_input(
        "Selecciona el rango de fechas:",
        [df_filtrado["Fecha"].min(), df_filtrado["Fecha"].max()]
    )
    df_filtrado = df_filtrado[
        (df_filtrado["Fecha"] >= pd.to_datetime(fecha_inicio)) & 
        (df_filtrado["Fecha"] <= pd.to_datetime(fecha_fin))
    ]
    
    latitudes_disponibles = df_filtrado["LAT"].unique()
    longitudes_disponibles = df_filtrado["LON"].unique()
    
    lat = st.sidebar.selectbox("Selecciona la latitud", latitudes_disponibles)
    lon = st.sidebar.selectbox("Selecciona la longitud", longitudes_disponibles)
    
    df_filtrado_lat_lon = df_filtrado[(df_filtrado["LAT"] == lat) & (df_filtrado["LON"] == lon)]
    mapa = folium.Map(location=[lat, lon], zoom_start=10)
    folium.Marker(
        location=[lat, lon],
        popup=f"Lat: {lat}, Lon: {lon}",
        icon=folium.Icon(color="blue")
    ).add_to(mapa)
    
    st.subheader("🌍 Mapa de Ubicación")
    st_folium(mapa, width=700, height=400)
    
    fig = px.line(
        df_filtrado_lat_lon,
        x="Fecha",
        y=["ALLSKY_KT"],
        title=f"All Sky Surface Shortwave Downward Irradiance (kW/m²/day) en Lat: {lat} y Lon: {lon} en el año {año}",
        labels={"Fecha": "Fecha", "value": "Valor", "variable": "Variable"},
        line_shape='linear',
        template="plotly_dark"
    )
    fig.update_traces(line=dict(color='red'))
    st.plotly_chart(fig)
    
    fig2 = px.line(
        df_filtrado_lat_lon,
        x="Fecha",
        y=["ALLSKY_SFC_SW_DWN"],
        title=f"All Sky Insolation Clearness Index en Lat: {lat} y Lon: {lon} en el año {año}",
        labels={"Fecha": "Fecha", "value": "Valor", "variable": "Variable"},
        line_shape='linear',
        template="plotly_dark"
    )
    st.plotly_chart(fig2)
    
elif menu == "Mapa Principal":
    # Slider de zoom encapsulado en formulario para que se actualice solo al presionar el botón
    with st.sidebar.form(key="zoom_form"):
        zoom_level = st.slider("Nivel de Zoom", 4, 15, 6)
        submit_zoom = st.form_submit_button("Aplicar Zoom")
    if not submit_zoom:
        zoom_level = 6
    st.subheader("🌍 Mapa de Calor de Radiación Solar en Colombia")
    fig = px.scatter_mapbox(
        df_all, lat='LAT', lon='LON', color='ALLSKY_KT',
        size=[3]*len(df_all), hover_name='LAT', zoom=zoom_level,
        color_continuous_scale='plasma', mapbox_style='open-street-map',
        center={'lat': 4.5709, 'lon': -74.2973},
        opacity=0.15
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=700)
    st.plotly_chart(fig, use_container_width=True)
    
elif menu == "Análisis Detallado":
    st.subheader("📈 Análisis de Datos Climáticos")
    region_avg = df_all.groupby('Region')['ALLSKY_SFC_SW_DWN'].mean()
    st.bar_chart(region_avg)
    df_all['Viabilidad'] = (df_all['ALLSKY_SFC_SW_DWN'] * 0.6 + df_all['ALLSKY_KT'] * 0.4)
    top3 = df_all.nlargest(3, 'Viabilidad')
    for i, (_, row) in enumerate(top3.iterrows()):
        st.metric(
            f"🥇 Ubicación {i+1}", 
            f"{row['Viabilidad']:.2f} pts", 
            f"Lat: {row['LAT']:.4f} Lon: {row['LON']:.4f}"
        )
    
elif menu == "Matriz de Correlación":
    st.subheader("Matriz de Correlación de Variables Climáticas")
    df_corr = pd.read_csv("datos_unificados_all.csv")
    df = df_corr.rename(columns={
        "RH2M": "Humedad relativa", 
        "T2M": "Temperatura", 
        "ALLSKY_SFC_SW_DWN": "Indice de claridad", 
        "ALLSKY_KT": "Irradiancia solar", 
        "PRECTOTCORR": "Precipitacion"
    })
    columnas_deseadas = [
        "Irradiancia solar", "Indice de claridad", 
        "Temperatura", "Humedad relativa", "Precipitacion"
    ]
    df_seleccionado = df[columnas_deseadas]
    matriz_correlacion = df_seleccionado.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        matriz_correlacion, annot=True, cmap='coolwarm', 
        fmt=".2f", linewidths=.5
    )
    plt.title('Matriz de Correlación')
    st.pyplot(plt)
    
elif menu == "Mapas Climáticos":
    st.subheader("Mapas de Humedad, Precipitación y Temperatura")
    tipo_mapa = st.selectbox(
        "Selecciona el tipo de mapa:", 
        ["Humedad", "Precipitación", "Temperatura"]
    )
    # Slider de zoom específico para mapas climáticos
    with st.sidebar.form(key="zoom_clima_form"):
        zoom_clima = st.slider("Nivel de Zoom para Mapas Climáticos", 4, 15, 6)
        submit_zoom_clima = st.form_submit_button("Aplicar Zoom")
    if not submit_zoom_clima:
        zoom_clima = 6

    if tipo_mapa == "Humedad":
        mapa = crear_mapa_clima(df_humedad, "humedad", "Humedad", zoom=zoom_clima)
    elif tipo_mapa == "Precipitación":
        mapa = crear_mapa_clima(df_precipitacion, "precipitacion", "Precipitación", zoom=zoom_clima)
    elif tipo_mapa == "Temperatura":
        mapa = crear_mapa_clima(df_temperatura, "temperatura", "Temperatura", zoom=zoom_clima)
    
    if mapa:
        st_folium(mapa, width=700, height=400)
    
elif menu == "Percentiles":
    st.subheader("📊 Mapa con los valores más altos de All Sky Surface Shortwave Downward Irradiance")
    percentil_seleccionado = st.sidebar.radio("Selecciona el percentil:", ["75", "50"], index=0)
    percentil_valor = 0.75 if percentil_seleccionado == "75" else 0.50
    df_promedio = df_all.groupby(['LAT', 'LON'])['ALLSKY_KT'].mean().reset_index()
    percentil = df_all['ALLSKY_KT'].quantile(percentil_valor)
    df_puntos_altos = df_promedio[df_promedio['ALLSKY_KT'] > percentil]
    df_puntos_bajos = df_promedio[df_promedio['ALLSKY_KT'] <= percentil]
    mapa = folium.Map(
        location=[df_promedio['LAT'].mean(), df_promedio['LON'].mean()], 
        zoom_start=6
    )
    
    for _, row in df_puntos_altos.iterrows():
        folium.CircleMarker(
            location=[row['LAT'], row['LON']],
            radius=8,
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=0.6,
            popup=f"Lat: {row['LAT']} - Lon: {row['LON']}<br>Promedio ALLSKY_KT: {row['ALLSKY_KT']:.2f}"
        ).add_to(mapa)
        
    for _, row in df_puntos_bajos.iterrows():
        radius = 4 + (row['ALLSKY_KT'] / df_promedio['ALLSKY_KT'].max()) * 10
        folium.CircleMarker(
            location=[row['LAT'], row['LON']],
            radius=radius,
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=0.6,
            popup=f"Lat: {row['LAT']} - Lon: {row['LON']}<br>Promedio ALLSKY_KT: {row['ALLSKY_KT']:.2f}"
        ).add_to(mapa)
        
    leyenda_items = [
        ("red", "ALLSKY_KT > Percentil"),
        ("blue", "ALLSKY_KT <= Percentil")
    ]
    agregar_leyenda(mapa, "Leyenda Percentiles", leyenda_items)
    
    st.subheader(f"🌍 Mapa de Puntos Mayores y Menores al Percentil {percentil_seleccionado}")
    st_folium(mapa, width=700, height=400)

if __name__ == "__main__":
    st.sidebar.info("Ejecuta este script con: streamlit run entrenamiento_app.py")
