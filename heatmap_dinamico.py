import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
import numpy as np
from datetime import datetime

# Set page config
st.set_page_config(page_title="Colombian Solar Radiation Heatmap", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("datos_unificados_completos.csv")
    df['DATE'] = pd.to_datetime(df[['YEAR', 'MO', 'DY']].assign(
        YEAR=df['YEAR'].astype(str),
        MO=df['MO'].astype(str).str.zfill(2),
        DY=df['DY'].astype(str).str.zfill(2)
    ).agg('-'.join, axis=1))
    return df

# Load the data
df = load_data()

# Sidebar controls
st.sidebar.header("Filters")

# Year and month selection
years = sorted(df['YEAR'].unique())
selected_year = st.sidebar.selectbox('Select Year', years)

months = sorted(df[df['YEAR'] == selected_year]['MO'].unique())
selected_month = st.sidebar.selectbox('Select Month', months)

# Metric selection
metric_options = {
    'ALLSKY_KT': 'Sky Clarity Index',
    'ALLSKY_SFC_SW_DWN': 'Solar Radiation (kW/m²/day)'
}
selected_metric = st.sidebar.selectbox('Select Metric', list(metric_options.keys()), 
                                     format_func=lambda x: metric_options[x])

# Filter data
filtered_df = df[
    (df['YEAR'] == selected_year) &
    (df['MO'] == selected_month)
].copy()

# Calculate average for the selected period
agg_df = filtered_df.groupby(['LAT', 'LON'])[selected_metric].mean().reset_index()

# Main content
st.title("Colombian Solar Radiation Heatmap")
st.subheader(f"{metric_options[selected_metric]} - {selected_year}/{selected_month}")

# Create base map
m = folium.Map(
    location=[4.5709, -74.2973],  # Colombia center
    zoom_start=6,
    tiles="cartodbpositron"
)

# Prepare data for heatmap
heat_data = [[row['LAT'], row['LON'], row[selected_metric]] for index, row in agg_df.iterrows()]

# Add heatmap layer
HeatMap(
    heat_data,
    radius=15,
    blur=10,
    max_zoom=13,
    gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'yellow', 0.8: 'orange', 1: 'red'}
).add_to(m)

# Display map
folium_static(m, width=1000, height=600)

# Display statistics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Average Value",
        f"{agg_df[selected_metric].mean():.2f}"
    )

with col2:
    max_location = agg_df.loc[agg_df[selected_metric].idxmax()]
    st.metric(
        "Maximum Value",
        f"{max_location[selected_metric]:.2f}",
        f"Lat: {max_location['LAT']:.2f}, Lon: {max_location['LON']:.2f}"
    )

with col3:
    st.metric(
        "Number of Measurements",
        len(filtered_df)
    )

# Add a data table
st.subheader("Raw Data Sample")
st.dataframe(
    filtered_df[['LAT', 'LON', 'DATE', selected_metric]]
    .head(10)
    .style.format({selected_metric: '{:.2f}'})
)
