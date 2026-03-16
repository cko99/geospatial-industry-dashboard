import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import folium_static
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Geospatial Industry Dashboard",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for glassmorphism, background, header
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        background-image: url('https://images.unsplash.com/photo-1462331940025-496dfbfc7564?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        position: relative;
    }
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 0;
    }
    .css-1d391kg {
        padding-top: 0;
    }
    .header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 60px;
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 20px;
        z-index: 1000;
        color: white !important;
    }
    .header .logo { font-size: 20px; }
    .header .title { font-size: 24px; font-weight: 600; }
    .header button { background: rgba(255,255,255,0.2); border: none; color: white; padding: 8px 16px; border-radius: 20px; cursor: pointer; }
    .glass-card {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
        padding: 20px !important;
        margin: 10px 0 !important;
        color: white !important;
    }
    .kpi-metric { 
        background: rgba(255, 255, 255, 0.15) !important;
        text-align: center !important;
        padding: 20px !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s !important;
    }
    .kpi-number { font-size: 32px !important; font-weight: 700 !important; margin-bottom: 5px !important; }
    .kpi-label { font-size: 14px !important; opacity: 0.9 !important; }
    .stSelectbox > div > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        color: white !important;
    }
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    h3 { color: white !important; margin-bottom: 15px !important; font-size: 16px !important; font-weight: 600 !important; }
    .plotly-graph-div { border-radius: 16px !important; overflow: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header">
        <div class="logo">🗺️</div>
        <div class="title">Geospatial Industry Dashboard</div>
        <button onclick="window.location.reload()">🔄 Refresh</button>
    </div>
""", unsafe_allow_html=True)

# Sample data (expanded from previous)
@st.cache_data
def load_data():
    data = [
        {'name': 'Aerodyne Group', 'industry': 'Drone', 'lat': 2.923, 'lon': 101.653, 'city': 'Cyberjaya', 'state': 'Selangor', 'website': 'aerodyne.group', 'desc': 'Global drone technology company specializing in aerial data analytics.', 'phone': '+60 3-8322 8888', 'email': 'info@aerodyne.group'},
        {'name': 'Map2U', 'industry': 'GIS', 'lat': 3.073, 'lon': 101.519, 'city': 'Kuala Lumpur', 'state': 'Kuala Lumpur', 'website': 'map2u.com', 'desc': 'Urban observatory platform.', 'phone': '+60 3-1234 5678', 'email': 'contact@map2u.com'},
        {'name': 'SmartMap', 'industry': 'GIS', 'lat': 3.134, 'lon': 101.709, 'city': 'Shah Alam', 'state': 'Selangor', 'website': 'mysmartmap.com.my', 'desc': 'GIS solutions provider.', 'phone': '+60 3-5555 6666', 'email': 'info@mysmartmap.com.my'},
        {'name': 'MySpatial', 'industry': 'GIS', 'lat': 3.147, 'lon': 101.694, 'city': 'Petaling Jaya', 'state': 'Selangor', 'website': 'myspatial.com.my', 'desc': 'Geospatial mapping specialist.', 'phone': '+60 3-7777 8888', 'email': 'info@myspatial.com.my'},
        {'name': 'GeoInfo', 'industry': 'Land Survey', 'lat': 5.416, 'lon': 100.332, 'city': 'Penang', 'state': 'Penang', 'website': 'geoinfo.com.my', 'desc': 'Geoinfo services.', 'phone': '+60 4-123 4567', 'email': 'contact@geoinfo.com.my'},
        {'name': 'Spatialworks', 'industry': 'Remote Sensing', 'lat': 4.210, 'lon': 101.657, 'city': 'Ipoh', 'state': 'Perak', 'website': 'spatialworks.com', 'desc': 'Spatial data experts.', 'phone': '+60 5-234 5678', 'email': 'info@spatialworks.com'},
        # Add more for 128 total simulation
    ] * 20  # Multiply for demo
    df = pd.DataFrame(data)
    return df

df = load_data()

# Session state
if 'selected_company' not in st.session_state:
    st.session_state.selected_company = None
if 'filter_industry' not in st.session_state:
    st.session_state.filter_industry = 'All'
if 'show_markers' not in st.session_state:
    st.session_state.show_markers = True
if 'show_heatmap' not in st.session_state:
    st.session_state.show_heatmap = False

# KPIs Row
col1, col2, col3, col4 = st.columns(4)
total_companies = len(df)
unique_industries = df['industry'].nunique()
top_state = df['state'].value_counts().index[0]
top_industry = df['industry'].value_counts().index[0]

with col1:
    st.markdown("""
        <div class="kpi-metric glass-card">
            <div class="kpi-number">{}</div>
            <div class="kpi-label">Total Companies</div>
        </div>
    """.format(total_companies), unsafe_allow_html=True)
with col2:
    st.markdown("""
        <div class="kpi-metric glass-card">
            <div class="kpi-number">{}</div>
            <div class="kpi-label">Total Industries</div>
        </div>
    """.format(unique_industries), unsafe_allow_html=True)
with col3:
    st.markdown("""
        <div class="kpi-metric glass-card">
            <div class="kpi-number">{}</div>
            <div class="kpi-label">Top State</div>
        </div>
    """.format(top_state), unsafe_allow_html=True)
with col4:
    st.markdown("""
        <div class="kpi-metric glass-card">
            <div class="kpi-number">{}</div>
            <div class="kpi-label">Top Industry</div>
        </div>
    """.format(top_industry), unsafe_allow_html=True)

# Filter
st.session_state.filter_industry = st.selectbox(
    "Filter Industry",
    ['All', 'Drone', 'GIS', 'Hydrography', 'Remote Sensing', 'Engineering Survey', 'Land Survey'],
    key='industry_filter'
)

filtered_df = df if st.session_state.filter_industry == 'All' else df[df['industry'] == st.session_state.filter_industry]

# Three panel layout
left_col, map_col, right_col = st.columns([1, 2.2, 1.2])

with left_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3>Industry Distribution</h3>", unsafe_allow_html=True)
    
    industry_counts = filtered_df['industry'].value_counts()
    fig_pie = px.pie(
        values=industry_counts.values,
        names=industry_counts.index,
        hole=0.6,
        color_discrete_sequence=['red', 'green', 'blue', 'orange', 'purple', 'darkblue']
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        legend=dict(x=1, y=0.5),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("<h3>Company by State</h3>", unsafe_allow_html=True)
    state_counts = filtered_df['state'].value_counts().head(8)
    fig_bar = px.bar(
        x=state_counts.values,
        y=state_counts.index,
        orientation='h',
        color=state_counts.index,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_bar.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        showlegend=False,
        margin=dict(l=40, r=0, t=0, b=0),
        xaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("<h3>AI Career Assistant</h3>", unsafe_allow_html=True)
    ai_query = st.text_input("Ask about companies...", placeholder="e.g., Drone companies in KL?")
    if ai_query:
        suggestions = filtered_df[filtered_df['industry'].str.contains('Drone|GIS', case=False, na=False)]['name'].unique()[:3]
        for name in suggestions:
            if st.button(name, key=name):
                st.session_state.selected_company = name
    
    st.markdown('</div>', unsafe_allow_html=True)

with map_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3>Interactive Map</h3>", unsafe_allow_html=True)
    
    # Folium Map
    m = folium.Map(location=[4.5, 102], zoom_start=6, tiles='OpenStreetMap')
    
    # Basemap selector simulation via session state
    basemap_choice = st.selectbox("Basemap", ["OpenStreetMap", "Satellite", "Terrain"], key="basemap")
    if basemap_choice == "Satellite":
        m = folium.Map(location=[4.5, 102], zoom_start=6, tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="ESRI")
    elif basemap_choice == "Terrain":
        m = folium.Map(location=[4.5, 102], zoom_start=6, tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}", attr="ESRI")
    
    # Markers
    if st.button("Toggle Markers", key="markers"):
        st.session_state.show_markers = not st.session_state.show_markers
    
    if st.session_state.show_markers:
        color_map = {'Drone': 'red', 'GIS': 'green', 'Hydrography': 'blue', 'Remote Sensing': 'orange', 'Engineering Survey': 'purple', 'Land Survey': 'darkblue'}
        for idx, row in filtered_df.iterrows():
            color = color_map.get(row['industry'], 'gray')
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=8,
                popup=f"<b>{row['name']}</b><br>Industry: {row['industry']}<br>City: {row['city']}<br>State: {row['state']}<br>Website: {row['website']}",
                color='white', weight=2,
                fillColor=color, fillOpacity=0.8
            ).add_to(m)
    
    # Heatmap toggle
    if st.button("Toggle Heatmap", key="heatmap"):
        st.session_state.show_heatmap = not st.session_state.show_heatmap
    
    if st.session_state.show_heatmap:
        from folium.plugins import HeatMap
        heat_data = [[row['lat'], row['lon']] for idx, row in filtered_df.iterrows()]
        HeatMap(heat_data).add_to(m)
    
    folium_static(m, height=500, width="100%")
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3>Company Explorer</h3>", unsafe_allow_html=True)
    
    company_names = filtered_df['name'].unique()
    selected_company = st.selectbox("Select Company", [""] + list(company_names))
    
    if selected_company:
        st.session_state.selected_company = selected_company
        company_data = filtered_df[filtered_df['name'] == selected_company].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Logo")
            st.markdown("![Logo](https://via.placeholder.com/100x100/ffffff/000000?text={})".format(company_data['name'][:3]))
        with col2:
            st.markdown(f"**{company_data['name']}**")
            st.markdown(f"**Location:** {company_data['city']}, {company_data['state']}")
            st.markdown(f"**Phone:** {company_data['phone']}")
            st.markdown(f"**Email:** {company_data['email']}")
            st.markdown(f"[Website](https://{company_data['website']})")
        
        st.markdown(f"**Description:** {company_data['desc']}")
    
    st.markdown("<h3>Top Companies</h3>", unsafe_allow_html=True)
    top_df = filtered_df.groupby(['name', 'industry', 'state']).size().reset_index(name='count').sort_values('count', ascending=False).head(10)
    st.dataframe(top_df[['name', 'industry', 'state']], use_container_width=True, hide_index=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer note
st.markdown("---")
st.markdown("*Professional GIS Intelligence Platform for Malaysian Geospatial Industry* [web:1]")
