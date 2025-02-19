import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import numpy as np

# Configure the page for optimal web viewing
st.set_page_config(
    page_title="Colombian Solar Radiation Analysis",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS to improve web appearance
st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# Create an efficient data loading function with caching
@st.cache_data(ttl=3600)  # Cache data for one hour
def load_solar_data():
    try:
        df = pd.read_csv("datos_unificados_completos.csv")
        # Convert date components to datetime for better handling
        df['DATE'] = pd.to_datetime(
            df[['YEAR', 'MO', 'DY']].assign(
                YEAR=df['YEAR'].astype(str),
                MO=df['MO'].astype(str).str.zfill(2),
                DY=df['DY'].astype(str).str.zfill(2)
            ).agg('-'.join, axis=1)
        )
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Create the main application interface
def main():
    # Add a descriptive header
    st.title("🌞 Colombian Solar Radiation Analysis")
    st.markdown("Interactive visualization of solar radiation patterns across Colombia")
    
    # Load the data
    df = load_solar_data()
    
    if df is not None:
        # Create sidebar controls
        with st.sidebar:
            st.header("📊 Analysis Controls")
            
            # Add metric selection
            metric = st.selectbox(
                "Select Measurement",
                ["ALLSKY_KT", "ALLSKY_SFC_SW_DWN"],
                format_func=lambda x: "Sky Clarity Index" if x == "ALLSKY_KT" 
                                    else "Solar Radiation (kW/m²/day)"
            )
            
            # Add time period selection
            year = st.selectbox("Select Year", sorted(df['YEAR'].unique()))
            month = st.selectbox(
                "Select Month",
                sorted(df[df['YEAR'] == year]['MO'].unique())
            )
            
            # Add helpful information
            st.info("💡 The heatmap updates automatically when you change selections")
        
        # Filter the data based on user selection
        filtered_df = df[
            (df['YEAR'] == year) &
            (df['MO'] == month)
        ].copy()
        
        # Calculate aggregated values for the heatmap
        agg_df = filtered_df.groupby(['LAT', 'LON'])[metric].mean().reset_index()
        
        # Create the base map
        m = folium.Map(
            location=[4.5709, -74.2973],  # Center of Colombia
            zoom_start=6,
            tiles='cartodbpositron'
        )
        
        # Prepare heatmap data
        heat_data = [[row['LAT'], row['LON'], row[metric]] 
                    for _, row in agg_df.iterrows()]
        
        # Add the heatmap layer with an optimized gradient
        HeatMap(
            heat_data,
            radius=15,
            blur=10,
            max_zoom=13,
            gradient={
                0.0: '#313695',  # Deep blue
                0.2: '#4575b4',  # Light blue
                0.4: '#74add1',  # Very light blue
                0.6: '#fed976',  # Light yellow
                0.8: '#feb24c',  # Orange
                1.0: '#f03b20'   # Red
            }
        ).add_to(m)
        
        # Display the map using st_folium
        st_folium(m, width=1000, height=600)
        
        # Add summary statistics in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Average Value",
                f"{agg_df[metric].mean():.2f}"
            )
        
        with col2:
            max_val = agg_df[metric].max()
            st.metric(
                "Maximum Value",
                f"{max_val:.2f}",
                f"+{((max_val/agg_df[metric].mean()-1)*100):.1f}%"
            )
        
        with col3:
            st.metric(
                "Number of Measurements",
                len(filtered_df)
            )
        
        # Add a data preview section
        with st.expander("📋 View Raw Data Sample"):
            st.dataframe(
                filtered_df[['LAT', 'LON', 'DATE', metric]]
                .head(10)
                .style.format({metric: '{:.2f}'})
            )

if __name__ == "__main__":
    main()
