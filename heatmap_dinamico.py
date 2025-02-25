import pandas as pd
import plotly.express as px
import folium
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_folium import st_folium  # Se eliminará su uso, pero si queremos evitar la dependencia, usaremos folium directamente
from branca.element import Template, MacroElement

# Nota: La librería 'streamlit_folium' se utiliza únicamente para mostrar el mapa en Streamlit.
# Como ahora no se usa Streamlit, reemplazamos su funcionalidad generando el mapa y guardándolo como HTML.

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
    
    # Añadir leyenda personalizada
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

def main():
    # Aquí se simula una navegación secuencial mediante la consola.
    print("Bienvenido al Proyecto Solaris (versión sin Streamlit)")
    print("Opciones disponibles:")
    print("1. Mostrar Datos")
    print("2. Generar Visualización Temporal (Plotly)")
    print("3. Generar Mapa Principal (Plotly Density Mapbox)")
    print("4. Generar Mapas Climáticos (Folium)")
    print("5. Análisis Detallado por Región (Barras)")
    print("6. Matriz de Correlación")
    print("7. Percentiles de Potencial Solar")
    opcion = input("Seleccione una opción (1-7): ")
    
    if opcion == "1":
        # Mostrar datos en consola (primeras filas)
        print("Mostrando las primeras 5 filas del dataset:")
        print(df_all.head())
    
    elif opcion == "2":
        # Visualización temporal: Se requiere elegir año, latitud y longitud.
        años = sorted(df_all["YEAR"].unique())
        print("Años disponibles:", años)
        año = int(input("Seleccione un año: "))
        
        lats = sorted(df_all["LAT"].unique())
        print("Latitudes disponibles:", lats)
        lat = float(input("Seleccione una latitud: "))
        
        lons = sorted(df_all["LON"].unique())
        print("Longitudes disponibles:", lons)
        lon = float(input("Seleccione una longitud: "))
        
        df_filtrado = df_all[
            (df_all["YEAR"] == año) &
            (df_all["LAT"] == lat) &
            (df_all["LON"] == lon)
        ]
        
        if df_filtrado.empty:
            print("No hay datos para la combinación seleccionada.")
        else:
            fig = px.line(
                df_filtrado,
                x='Fecha',
                y=['ALLSKY_KT', 'ALLSKY_SFC_SW_DWN'],
                title=f"Comportamiento temporal en {lat}, {lon}",
                labels={'value': 'Valor', 'variable': 'Indicador'},
                height=500
            )
            fig.write_html("visualizacion_temporal.html")
            print("El gráfico se guardó como 'visualizacion_temporal.html'. Ábrelo en tu navegador.")
    
    elif opcion == "3":
        # Mapa Principal con Plotly Density Mapbox
        zoom_level = int(input("Seleccione nivel de zoom (por ejemplo, 6): "))
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
        fig.write_html("mapa_principal.html")
        print("El mapa se guardó como 'mapa_principal.html'. Ábrelo en tu navegador.")
    
    elif opcion == "4":
        # Mapas Climáticos con Folium
        variables = ["humedad", "precipitacion", "temperatura", "ALLSKY_KT"]
        print("Variables disponibles:", variables)
        variable = input("Seleccione la variable: ")
        if variable not in variables:
            print("Variable no válida.")
        else:
            mapa = crear_mapa_clima(df_all, variable, variable.capitalize())
            mapa.save("mapa_climatico.html")
            print("El mapa climático se guardó como 'mapa_climatico.html'. Ábrelo en tu navegador.")
    
    elif opcion == "5":
        # Análisis Detallado: Comparación Regional
        df_region = df_all.groupby('Region').agg({
            'ALLSKY_KT': 'mean',
            'temperatura': 'mean',
            'precipitacion': 'mean',
            'humedad': 'mean'
        }).reset_index()
        
        print("Comparación Regional (valores promedio):")
        print(df_region)
        
        # Permitir seleccionar variables a comparar
        print("Variables disponibles: ALLSKY_KT, temperatura, precipitacion, humedad")
        vars_seleccionadas = input("Ingrese variables separadas por coma (por ejemplo, ALLSKY_KT,humedad): ")
        variables_mostrar = [var.strip() for var in vars_seleccionadas.split(",")]
        
        if not variables_mostrar:
            print("Debe seleccionar al menos una variable.")
        else:
            fig = px.bar(
                df_region.melt(id_vars='Region', value_vars=variables_mostrar),
                x='Region',
                y='value',
                color='variable',
                barmode='group',
                title="Indicadores Promedio por Región",
                labels={'value': 'Valor Promedio', 'variable': 'Indicador'}
            )
            fig.write_html("analisis_detallado.html")
            print("El gráfico se guardó como 'analisis_detallado.html'. Ábrelo en tu navegador.")
    
    elif opcion == "6":
        # Matriz de Correlación
        cols_corr = [
            'ALLSKY_KT',
            'ALLSKY_SFC_SW_DWN',
            'temperatura',
            'humedad',
            'precipitacion'
        ]
        corr_matrix = df_all[cols_corr].corr()
        print("Matriz de Correlación:")
        print(corr_matrix)
        
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            color_continuous_scale='RdBu',
            range_color=[-1, 1],
            title="Matriz de Correlación"
        )
        fig.write_html("matriz_correlacion.html")
        print("El gráfico se guardó como 'matriz_correlacion.html'. Ábrelo en tu navegador.")
    
    elif opcion == "7":
        # Percentiles
        percentil_input = float(input("Seleccione percentil (entre 70 y 95, sin %): "))
        percentil = percentil_input / 100
        threshold = df_all['ALLSKY_KT'].quantile(percentil)
        df_top = df_all[df_all['ALLSKY_KT'] > threshold]
        
        print(f"Se muestran ubicaciones con índice de claridad solar > {threshold:.3f} (percentil {percentil_input})")
        
        # Estadísticas por región para zonas de alto potencial
        regiones_count = df_top.groupby('Region').size().reset_index(name='Conteo')
        fig_regiones = px.pie(
            regiones_count, 
            values='Conteo', 
            names='Region',
            title="Distribución de zonas de alto potencial por región"
        )
        fig_regiones.write_html("percentiles_potencial.html")
        print("El gráfico se guardó como 'percentiles_potencial.html'. Ábrelo en tu navegador.")
    
    else:
        print("Opción no válida.")

if __name__ == "__main__":
    main()
