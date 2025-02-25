import pandas as pd
import streamlit as st
import plotly.express as px
import folium
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_folium import st_folium

# Configuración de la página de Streamlit
st.set_page_config(page_title="Proyecto Solaris", page_icon="", layout="wide")
st.title("Proyecto Solaris")
st.sidebar.title(" Opciones de Navegación")

# Funciones de carga de datos
@st.cache_data
def cargar_humedad():
    df = pd.read_csv("datos_agrupados_humedity.csv")
    df = df.rename(columns={"RH2M": "humedad"})  # Renombrar columna
    return df

@st.cache_data
def cargar_precipitacion():
    df = pd.read_csv("datos_agrupados_precipitacion.csv")
    df = df.rename(columns={"PRECTOTCORR": "precipitacion"})  # Renombrar columna
    return df

@st.cache_data
def cargar_temperatura():
    df = pd.read_csv("datos_agrupados_temperature1.csv")
    df = df.rename(columns={"T2M": "temperatura"})  # Renombrar columna
    return df

df_humedad = cargar_humedad()
df_precipitacion = cargar_precipitacion()
df_temperatura = cargar_temperatura()
# Funciones de carga de datos
@st.cache_data
def cargar_datos():
    return pd.read_csv("datos_unificados (2).csv")
df_all = cargar_datos()

# Crear una nueva columna 'Fecha' combinando 'YEAR', 'MO', 'DY'
df_all['Fecha'] = pd.to_datetime(df_all.astype(str).loc[:, ["YEAR", "MO", "DY"]].agg('-'.join, axis=1))

# Función para crear mapas climáticos
def crear_mapa_clima(df, columna, titulo):
    max_row = df.loc[df[columna].idxmax()]
    map_center = [max_row["LAT"], max_row["LON"]]
    mapa = folium.Map(location=map_center, zoom_start=6)
    for _, row in df.iterrows():
        valor = row[columna]
        folium.CircleMarker(
            location=[row['LAT'], row['LON']],
            radius=valor * 0.1,
            color='green' if valor > df[columna].quantile(0.75) else 'orange' if valor > df[columna].quantile(0.5) else 'red',
            fill=True,
            fill_color='green' if valor > df[columna].quantile(0.75) else 'orange' if valor > df[columna].quantile(0.5) else 'red',
            fill_opacity=0.6,
            popup=f"{titulo}: {valor:.2f}"
        ).add_to(mapa)
# Menú de navegación en la barra lateral
menu = st.sidebar.selectbox("Selecciona una opción:", ["Inicio", "Datos", "Visualización", "Mapa Principal", "Mapas Climáticos", "Análisis Detallado", "Matriz de Correlación", "Percentiles"])

def get_region(lat, lon):
    if lat > 8: return "Caribe"
    elif lat < 2: return "Sur"
    elif lon < -75: return "Pacífico"
    return "Andina"

df_all['Region'] = df_all.apply(lambda x: get_region(x['LAT'], x['LON']), axis=1)

if menu == "Datos":
    st.subheader(" Datos Disponibles")
    st.dataframe(df_all)
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

    # Filtro por año
    año = st.sidebar.selectbox("Selecciona el año", df_all["YEAR"].unique())
    df_filtrado = df_all[df_all["YEAR"] == año]

    st.write(f"Mostrando datos para el año: {año}")
    
    # Filtro por rango de fechas
    fecha_inicio, fecha_fin = st.sidebar.date_input(
        "Selecciona el rango de fechas:",
        [df_filtrado["Fecha"].min(), df_filtrado["Fecha"].max()]
    )

    # Filtrar los datos según el rango de fechas
    df_filtrado = df_filtrado[(df_filtrado["Fecha"] >= pd.to_datetime(fecha_inicio)) & (df_filtrado["Fecha"] <= pd.to_datetime(fecha_fin))]

    # Filtro por latitud y longitud
    latitudes_disponibles = df_filtrado["LAT"].unique()
    longitudes_disponibles = df_filtrado["LON"].unique()
    
    lat = st.sidebar.selectbox("Selecciona la latitud", latitudes_disponibles)
    lon = st.sidebar.selectbox("Selecciona la longitud", longitudes_disponibles)

    # Filtrar los datos según la latitud y longitud seleccionadas
    df_filtrado_lat_lon = df_filtrado[(df_filtrado["LAT"] == lat) & (df_filtrado["LON"] == lon)]
    
    # Crear un mapa con folium centrado en la latitud y longitud seleccionadas
    mapa = folium.Map(location=[lat, lon], zoom_start=10)
    
    # Añadir un marcador en la ubicación seleccionada
    folium.Marker(
        location=[lat, lon],
        popup=f"Lat: {lat}, Lon: {lon}",
        icon=folium.Icon(color="blue")
    ).add_to(mapa)

    # Mostrar el mapa en Streamlit
    st.subheader("🌍 Mapa de Ubicación")
    st_folium(mapa, width=700, height=400)
    
    # Crear gráfico interactivo de líneas con Plotly
    fig = px.line(
        df_filtrado_lat_lon,
        x="Fecha",
        y=["ALLSKY_KT"],
        title=f"All Sky Surface Shortwave Downward Irradiance (kW/m²/day) en Lat: {lat} y Lon: {lon} en el año {año}",
        labels={"Fecha": "Fecha", "value": "Valor", "variable": "Variable"},
        line_shape='linear',  # Línea recta entre puntos
        template="plotly_dark"  # Establecer el tema oscuro
    )
    fig.update_traces(line=dict(color='red'))
    # Mostrar el gráfico interactivo
    st.plotly_chart(fig)

    # Crear gráfico interactivo de líneas con Plotly para ALLSKY_SFC_SW_DWN
    fig = px.line(
        df_filtrado_lat_lon,
        x="Fecha",
        y=["ALLSKY_SFC_SW_DWN"],
        title=f"All Sky Insolation Clearness Index en Lat: {lat} y Lon: {lon} en el año {año}",
        labels={"Fecha": "Fecha", "value": "Valor", "variable": "Variable"},
        line_shape='linear',  # Línea recta entre puntos
        template="plotly_dark"  # Establecer el tema oscuro
    )

    # Mostrar el gráfico interactivo
    st.plotly_chart(fig)
elif menu == "Mapa Principal":
    zoom_level = st.sidebar.slider("Nivel de Zoom", 4, 15, 6)
    st.subheader("🌍 Mapa de Calor de Radiación Solar en Colombia")
    fig = px.scatter_mapbox(
        df_all, lat='LAT', lon='LON', color='ALLSKY_KT',
        size=[3]*len(df_all), hover_name='LAT', zoom=zoom_level,
        color_continuous_scale='plasma', mapbox_style='open-street-map',
        center={'lat': 4.5709, 'lon': -74.2973},
        opacity=0.15  # Ajustando la opacidad directamente en scatter_mapbox
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=700)
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Mapa Principal":
    zoom_level = st.sidebar.slider("Nivel de Zoom", 4, 15, 6)
    st.subheader("🌍 Mapa de Calor de Radiación Solar en Colombia")
    fig = px.scatter_mapbox(
        df_all, lat='LAT', lon='LON', color='ALLSKY_KT',
        size=[3]*len(df_all), hover_name='LAT', zoom=zoom_level,
        color_continuous_scale='plasma', mapbox_style='open-street-map',
        center={'lat': 4.5709, 'lon': -74.2973},
        opacity=0.15  # Ajustando la opacidad directamente en scatter_mapbox
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
        st.metric(f"🥇 Ubicación {i+1}", f"{row['Viabilidad']:.2f} pts", f"Lat: {row['LAT']:.4f} Lon: {row['LON']:.4f}")

elif menu == "Matriz de Correlación":
    st.subheader(" Matriz de Correlación de Variables Climáticas")
    df_corr = pd.read_csv("datos_unificados_all.csv") #Se usa el mismo archivo que en el resto del código
    df = df_corr.rename(columns={"RH2M": "Humedad relativa", "T2M": "Temperatura", "ALLSKY_SFC_SW_DWN": "Indice de claridad", "ALLSKY_KT": "Irradiancia solar", "PRECTOTCORR": "Precipitacion"})
    columnas_deseadas = ["Irradiancia solar", "Indice de claridad", "Temperatura", "Humedad relativa", "Precipitacion"]
    df_seleccionado = df[columnas_deseadas]
    matriz_correlacion = df_seleccionado.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(matriz_correlacion, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
    plt.title('Matriz de Correlación')
    st.pyplot(plt)

elif menu == "Mapas Climáticos":
    st.subheader("️ Mapas de Humedad, Precipitación y Temperatura")
    tipo_mapa = st.selectbox("Selecciona el tipo de mapa:", ["Humedad", "Precipitación", "Temperatura"])

    if tipo_mapa == "Humedad":
        mapa = crear_mapa_clima(df_humedad, "humedad", "Humedad")
    elif tipo_mapa == "Precipitación":
        mapa = crear_mapa_clima(df_precipitacion, "precipitacion", "Precipitación")
    elif tipo_mapa == "Temperatura":
        mapa = crear_mapa_clima(df_temperatura, "temperatura", "Temperatura")

    if mapa:
        st_folium(mapa, width=700, height=400)
elif menu == "Percentiles":
    st.subheader("📊 Mapa con los valores más altos de All Sky Surface Shortwave Downward Irradiance")
    
    # Selector de percentil
    percentil_seleccionado = st.sidebar.radio("Selecciona el percentil:", ["75", "50"], index=0)
    percentil_valor = 0.75 if percentil_seleccionado == "75" else 0.50
    
    df_promedio = df_all.groupby(['LAT', 'LON'])['ALLSKY_KT'].mean().reset_index()
    percentil = df_all['ALLSKY_KT'].quantile(percentil_valor)
    df_puntos_altos = df_promedio[df_promedio['ALLSKY_KT'] > percentil]
    df_puntos_bajos = df_promedio[df_promedio['ALLSKY_KT'] <= percentil]
    
    mapa = folium.Map(location=[df_promedio['LAT'].mean(), df_promedio['LON'].mean()], zoom_start=6)
    
    for _, row in df_puntos_altos.iterrows():
        folium.CircleMarker(
            location=[row['LAT'], row['LON']],
            radius=8,  # Radio fijo para los puntos altos
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=0.6,
            popup=f"Lat: {row['LAT']} - Lon: {row['LON']}<br>Promedio ALLSKY_KT: {row['ALLSKY_KT']:.2f}",
        ).add_to(mapa)
    
    for _, row in df_puntos_bajos.iterrows():
        # Asignar tamaño proporcional al valor de ALLSKY_KT
        radius = 4 + (row['ALLSKY_KT'] / df_promedio['ALLSKY_KT'].max()) * 10  # Escala de tamaño
        
        folium.CircleMarker(
            location=[row['LAT'], row['LON']],
            radius=radius,
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=0.6,
            popup=f"Lat: {row['LAT']} - Lon: {row['LON']}<br>Promedio ALLSKY_KT: {row['ALLSKY_KT']:.2f}",
        ).add_to(mapa)
    
    st.subheader(f"🌍 Mapa de Puntos Mayores y Menores al Percentil {percentil_seleccionado}")
    st_folium(mapa, width=700, height=400)

elif menu == "Mapas Climáticos":
    st.subheader("️ Mapas de Humedad, Precipitación y Temperatura")
    tipo_mapa = st.selectbox("Selecciona el tipo de mapa:", ["Humedad", "Precipitación", "Temperatura"])
    if tipo_mapa == "Humedad":
        mapa = crear_mapa_clima(df_all, tipo_mapa, "RH2M")
    elif tipo_mapa == "Precipitación":
        mapa = crear_mapa_clima(df_all, tipo_mapa, "PRECTOTCORR")
    elif tipo_mapa == "Temperatura":
        mapa = crear_mapa_clima(df_all, tipo_mapa, "T2M")
    if mapa:
        st_folium(mapa, width=700, height=400)

if __name__ == "__main__":
    st.sidebar.info("Ejecuta este script con: streamlit run solaris_app.py.py")
