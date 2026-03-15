import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# -----------------------------------------
# 1. PAGE CONFIGURATION & NO-SCROLL CSS
# -----------------------------------------
st.set_page_config(
    page_title="Geospatial Industry Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        /* Paksa skrin statik & buang scrollbar utama */
        html, body, [data-testid="stAppViewContainer"] {
            overflow: hidden;
            height: 100vh;
        }
        
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1469474968028-56623f02e42e");
            background-size: cover;
            background-position: center;
        }

        /* Container utama */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }

        /* Glassmorphism effect untuk setiap panel */
        div[data-testid="stVerticalBlock"] > div {
            background: rgba(15, 15, 15, 0.5);
            padding: 12px;
            border-radius: 12px;
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
        }

        .header-text {
            text-align: center;
            font-size: 28px;
            font-weight: 800;
            margin-bottom: 10px;
            color: white;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        /* Kecilkan jarak antara widget */
        .stSelectbox, .stTextInput {
            margin-bottom: -15px;
        }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------
# 2. DATA (Mock Data)
# -----------------------------------------
mock_data = {
    'company': ['Aerodyne Group', 'Ground Data Solutions', 'Geospatial Info', 'SkyBugs', 'Topo Survey'],
    'industry': ['Drone', 'Remote Sensing', 'GIS', 'Drone', 'Land Survey'],
    'state': ['Selangor', 'Kuala Lumpur', 'Selangor', 'Penang', 'Johor'],
    'city': ['Cyberjaya', 'KL City', 'Shah Alam', 'Georgetown', 'JB'],
    'latitude': [2.9228, 3.1390, 3.0738, 5.4141, 1.4927],
    'longitude': [101.6572, 101.6869, 101.5183, 100.3288, 103.7414],
    'website': ['aerodyne.group', 'gds.com', 'geo-info.my', 'skybugs.my', 'toposurvey.my'],
    'logo': ['https://via.placeholder.com/150'] * 5,
    'phone': ['+603-1234567', '+603-7654321', '+603-9998887', '+604-1231231', '+607-4445555'],
    'email': ['hello@aerodyne.group', 'info@gds.com', 'admin@geo.my', 'fly@skybugs.my', 'hello@topo.my'],
    'description': ['Global drone data analytics.', 'LiDAR and remote sensing.', 'GIS software solutions.', 'Custom drone mapping.', 'Land boundary mapping.']
}
df = pd.DataFrame(mock_data)

# -----------------------------------------
# 3. HEADER & FILTER
# -----------------------------------------
st.markdown("<div class='header-text'>Geospatial Industry Dashboard</div>", unsafe_allow_html=True)

# Filter diletakkan dalam columns supaya jimat ruang vertikal
_, f_col, _ = st.columns([1, 2, 1])
with f_col:
    industries = ["All"] + sorted(df['industry'].unique().tolist())
    selected_industry = st.selectbox("Industry Filter", industries, label_visibility="collapsed")

filtered_df = df if selected_industry == "All" else df[df['industry'] == selected_industry]

# -----------------------------------------
# 4. MAIN LAYOUT (3 Columns)
# -----------------------------------------
col_left, col_map, col_right = st.columns([1, 2.2, 1.2], gap="small")

# --- LEFT PANEL ---
with col_left:
    st.markdown("### Industry Distribution")
    fig_pie = px.pie(filtered_df, names='industry', hole=0.4)
    fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False, height=220, paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("### Company by State")
    state_counts = filtered_df['state'].value_counts().reset_index()
    fig_bar = px.bar(state_counts, x='state', y='count')
    fig_bar.update_layout(margin=dict(t=10, b=0, l=0, r=0), height=200, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

    st.markdown("### AI Assistant")
    st.text_input("Ask:", placeholder="Search company...", label_visibility="collapsed")

# --- CENTER PANEL (Using your Folium Code) ---
with col_map:
    m = folium.Map(location=[4.2, 102.0], zoom_start=6, tiles=None)

    # Basemap Options (Original Code)
    folium.TileLayer('openstreetmap', name='OpenStreetMap').add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri', name='Satellite imagery', overlay=False
    ).add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
        attr='Esri', name='Hybrid Labels', overlay=True
    ).add_to(m)
    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        attr='Map data: &copy; OpenStreetMap contributors | Map style: &copy; OpenTopoMap',
        name='Terrain', overlay=False
    ).add_to(m)

    color_map = {'Drone': 'red', 'GIS': 'green', 'Hydrography': 'blue', 'Remote Sensing': 'orange', 'Engineering Survey': 'purple', 'Land Survey': 'darkblue'}

    for _, row in filtered_df.iterrows():
        popup_html = f"""<div style='font-family: Arial; min-width: 150px;'>
            <h5 style='margin-bottom:5px;'>{row['company']}</h5>
            <b>Industry:</b> {row['industry']}<br>
            <a href='http://{row['website']}' target='_blank'>Visit Website</a></div>"""
        
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=row['company'],
            icon=folium.Icon(color=color_map.get(row['industry'], 'gray'), icon='info-sign')
        ).add_to(m)

    folium.LayerControl().add_to(m)
    
    # Height diselaraskan kepada 620px supaya muat skrin laptop/desktop tanpa scroll
    st_folium(m, width="100%", height=620, returned_objects=[])

# --- RIGHT PANEL ---
with col_right:
    st.markdown("### Company Information")
    company_list = filtered_df['company'].sort_values().tolist()
    if company_list:
        sel_comp = st.selectbox("Select Company", company_list, label_visibility="collapsed")
        info = filtered_df[filtered_df['company'] == sel_comp].iloc[0]
        
        st.image(info['logo'], width=100)
        st.write(f"**Location:** {info['city']}, {info['state']}")
        st.write(f"**Email:** {info['email']}")
        st.write(f"**Website:** [{info['website']}](http://{info['website']})")
        st.markdown(f"> {info['description']}")
    else:
        st.info("No data.")
