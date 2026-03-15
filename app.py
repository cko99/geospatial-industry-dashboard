import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# -----------------------------------------
# 1. PAGE CONFIGURATION & FIX VIEWPORT
# -----------------------------------------
st.set_page_config(
    page_title="Geospatial Industry Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS untuk paksa Full Screen tanpa scroll
custom_css = """
<style>
    /* 1. Sembunyikan scrollbar utama body */
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden;
        height: 100vh;
    }

    /* 2. Wallpaper Background */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1469474968028-56623f02e42e");
        background-size: cover;
        background-position: center;
    }

    /* 3. Header Styling */
    .fixed-header {
        text-align: center;
        font-size: 24px;
        font-weight: 700;
        color: white;
        background: rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(10px);
        padding: 10px 0;
        border-radius: 10px;
        margin-bottom: 10px;
    }

    /* 4. Kurangkan padding container Streamlit */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 0rem !important;
        max-height: 100vh;
    }

    /* 5. Styling untuk setiap panel supaya ada background gelap sikit (glassmorphism) */
    div[data-testid="stVerticalBlock"] > div {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        backdrop-filter: blur(5px);
    }

    /* 6. Fix ketinggian Plotly Chart */
    .js-plotly-plot {
        height: 30vh !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# -----------------------------------------
# 2. MOCK DATA
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
# 3. HEADER & FILTER (Kecilkan saiz)
# -----------------------------------------
st.markdown("<div class='fixed-header'>Geospatial Industry Dashboard</div>", unsafe_allow_html=True)

# Guna columns untuk filter supaya tak makan ruang vertikal
f1, f2, f3 = st.columns([1, 1, 2])
with f1:
    industries = ["All"] + sorted(df['industry'].unique().tolist())
    selected_industry = st.selectbox("Filter Industry", industries, label_visibility="collapsed")

filtered_df = df if selected_industry == "All" else df[df['industry'] == selected_industry]

# -----------------------------------------
# 4. MAIN LAYOUT (3 Columns)
# -----------------------------------------
# Kunci tinggi col_left dan col_right supaya fit skrin
col_left, col_map, col_right = st.columns([1, 2.2, 1.2], gap="small")

with col_left:
    st.caption("INDUSTRY DISTRIBUTION")
    fig_pie = px.pie(filtered_df, names='industry', hole=0.4)
    fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False, height=200, paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
    
    st.caption("COMPANY BY STATE")
    state_counts = filtered_df['state'].value_counts().reset_index()
    fig_bar = px.bar(state_counts, x='state', y='count')
    fig_bar.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=200, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

    st.caption("AI ASSISTANT")
    st.text_input("Ask:", placeholder="Search...", label_visibility="collapsed")

with col_map:
    # Set height map kepada 70-75% daripada view height
    m = folium.Map(location=[4.2, 108.0], zoom_start=5, tiles='CartoDB dark_matter')
    for _, row in filtered_df.iterrows():
        folium.Marker(
            [row['latitude'], row['longitude']], 
            popup=row['company'],
            tooltip=row['company']
        ).add_to(m)
    
    st_folium(m, width="100%", height=550, returned_objects=[])

with col_right:
    st.caption("COMPANY EXPLORER")
    selected_company = st.selectbox("Select", filtered_df['company'], label_visibility="collapsed")
    
    c_info = filtered_df[filtered_df['company'] == selected_company].iloc[0]
    
    # Guna container kecil untuk info
    st.image(c_info['logo'], width=80)
    st.markdown(f"**{c_info['company']}**")
    st.write(f"📍 {c_info['city']}, {c_info['state']}")
    st.write(f"📞 {c_info['phone']}")
    st.write(f"🌐 [{c_info['website']}](http://{c_info['website']})")
    st.info(c_info['description'])
