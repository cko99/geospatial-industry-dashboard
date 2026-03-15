import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# -----------------------------------------
# 1. PAGE CONFIGURATION & CSS
# -----------------------------------------
st.set_page_config(
    page_title="Geospatial Industry Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Background, Fixed Header, and Transparent Containers
custom_css = """
<style>
    /* Full-page fixed background wallpaper */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1469474968028-56623f02e42e");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Fixed Header adapting to Light/Dark mode using Streamlit CSS variables */
    .fixed-header {
        position: fixed;
        top: 2rem;
        left: 0;
        width: 100%;
        text-align: center;
        font-size: 26px;
        font-weight: 700;
        color: var(--text-color);
        background: rgba(15, 15, 15, 0.4);
        backdrop-filter: blur(10px);
        padding: 15px 0;
        z-index: 999999;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Make background panels transparent for charts and text */
    [data-testid="stVerticalBlock"] {
        background-color: transparent !important;
    }
    
    /* Push content down to avoid overlapping with fixed header */
    .main-content-padding {
        padding-top: 80px; 
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
st.markdown("<div class='fixed-header'>Geospatial Industry Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='main-content-padding'></div>", unsafe_allow_html=True)

# -----------------------------------------
# 2. DATA LOADING
# -----------------------------------------
@st.cache_data
def load_data(url):
    try:
        # Load from Google Sheet CSV link (Header=1 drops the empty row 1)
        data = pd.read_csv(url, header=1)
        # Drop empty 'Unnamed' columns
        data = data.loc[:, ~data.columns.str.contains("^Unnamed")]
        # Strip whitespace and lowercase column names for consistency
        data.columns = data.columns.str.strip().str.lower()
        
        # Ensure latitude/longitude are numeric
        data['latitude'] = pd.to_numeric(data['latitude'], errors='coerce')
        data['longitude'] = pd.to_numeric(data['longitude'], errors='coerce')
        data = data.dropna(subset=['latitude', 'longitude'])
        
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # Returning an empty dataframe with expected columns as a fallback
        cols = ['company', 'industry', 'state', 'city', 'country', 'latitude', 'longitude', 'website', 'logo', 'phone', 'email', 'description']
        return pd.DataFrame(columns=cols)

# Replace this with your actual Google Sheet CSV export link
SHEET_URL = "YOUR_GOOGLE_SHEET_CSV_URL_HERE" 

# Uncomment to load real data once the URL is provided
# df = load_data(SHEET_URL)

# --- MOCK DATA FOR DEMONSTRATION PURPOSES (Remove when using live URL) ---
mock_data = {
    'company': ['Aerodyne Group', 'Ground Data Solutions', 'Geospatial Info', 'SkyBugs', 'Topo Survey'],
    'industry': ['Drone', 'Remote Sensing', 'GIS', 'Drone', 'Land Survey'],
    'state': ['Selangor', 'Kuala Lumpur', 'Selangor', 'Penang', 'Johor'],
    'city': ['Cyberjaya', 'KL City', 'Shah Alam', 'Georgetown', 'JB'],
    'country': ['Malaysia']*5,
    'latitude': [2.9228, 3.1390, 3.0738, 5.4141, 1.4927],
    'longitude': [101.6572, 101.6869, 101.5183, 100.3288, 103.7414],
    'website': ['aerodyne.group', 'gds.com', 'geo-info.my', 'skybugs.my', 'toposurvey.my'],
    'logo': ['https://via.placeholder.com/150'] * 5,
    'phone': ['+603-1234567', '+603-7654321', '+603-9998887', '+604-1231231', '+607-4445555'],
    'email': ['hello@aerodyne.group', 'info@gds.com', 'admin@geo.my', 'fly@skybugs.my', 'hello@topo.my'],
    'description': ['Global drone data analytics.', 'LiDAR and remote sensing.', 'GIS software solutions.', 'Custom drone mapping.', 'Land boundary mapping.']
}
df = pd.DataFrame(mock_data)
# -------------------------------------------------------------------------

# -----------------------------------------
# 3. GLOBAL FILTER SECTION
# -----------------------------------------
# Placed above the columns or inside the layout. We will place it top-center.
industries = ["All"] + sorted(df['industry'].dropna().unique().tolist())
selected_industry = st.selectbox("Filter Industry", industries)

if selected_industry != "All":
    filtered_df = df[df['industry'] == selected_industry]
else:
    filtered_df = df

# -----------------------------------------
# 4. LAYOUT STRUCTURE (3 Columns)
# -----------------------------------------
col_left, col_map, col_right = st.columns([1, 2, 1], gap="medium")

# -----------------------------------------
# 5. LEFT PANEL (Analytics & Assistant)
# -----------------------------------------
with col_left:
    st.markdown("### Industry Distribution")
    
    # Pie Chart
    if not filtered_df.empty:
        industry_counts = filtered_df['industry'].value_counts().reset_index()
        industry_counts.columns = ['Industry', 'Count']
        
        fig_pie = px.pie(industry_counts, values='Count', names='Industry', hole=0.4)
        fig_pie.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=st.get_option("theme.textColor")),
            legend=dict(orientation="v", yanchor="auto", y=0.5, xanchor="left", x=1.0)
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("### Company by State")
    
    # Bar Chart
    if not filtered_df.empty:
        state_counts = filtered_df['state'].value_counts().reset_index()
        state_counts.columns = ['State', 'Count']
        
        fig_bar = px.bar(state_counts, x='State', y='Count')
        fig_bar.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=st.get_option("theme.textColor"))
        )
        fig_bar.update_traces(marker_color='rgba(50, 171, 96, 0.7)', marker_line_color='rgba(50, 171, 96, 1)', marker_line_width=1.5)
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

    # AI Career Assistant
    st.markdown("### AI Career Assistant")
    search_query = st.text_input("Ask a question:", placeholder="e.g., Which GIS companies are in KL?")
    if search_query:
        # Basic keyword-based search across dataframe
        mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
        search_results = df[mask]
        
        if not search_results.empty:
            st.success(f"Found {len(search_results)} relevant companies:")
            for _, row in search_results.iterrows():
                st.markdown(f"**{row['company']}** ({row['industry']}) - {row['city']}, {row['state']}")
        else:
            st.warning("No companies matched your query. Try different keywords.")

# -----------------------------------------
# 6. CENTER PANEL (Folium Map)
# -----------------------------------------
with col_map:
    # Initialize Map
    m = folium.Map(location=[4.5, 102.0], zoom_start=6, tiles=None)

    # Basemap Options
    folium.TileLayer('openstreetmap', name='OpenStreetMap').add_to(m)
    
    # Esri Satellite
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite imagery',
        overlay=False
    ).add_to(m)
    
    # Esri Hybrid (Satellite + Labels)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Hybrid Labels',
        overlay=True
    ).add_to(m)
    
    # OpenTopoMap (Terrain)
    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        attr='Map data: &copy; OpenStreetMap contributors, SRTM | Map style: &copy; OpenTopoMap',
        name='Terrain',
        overlay=False
    ).add_to(m)

    # Marker Colors Mapping
    color_map = {
        'Drone': 'red',
        'GIS': 'green',
        'Hydrography': 'blue',
        'Remote Sensing': 'orange',
        'Engineering Survey': 'purple',
        'Land Survey': 'darkblue'
    }

    # Add Markers
    for _, row in filtered_df.iterrows():
        # HTML formatting for Popup
        popup_html = f"""
        <div style="font-family: Arial; min-width: 200px;">
            <h4 style="margin-bottom: 5px;">{row['company']}</h4>
            <b>Industry:</b> {row['industry']}<br>
            <b>City:</b> {row['city']}<br>
            <b>State:</b> {row['state']}<br>
            <b>Website:</b> <a href="http://{row['website']}" target="_blank">{row['website']}</a>
        </div>
        """
        
        marker_color = color_map.get(row['industry'], 'gray') # Default to gray if missing
        
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row['company'],
            icon=folium.Icon(color=marker_color, icon='info-sign')
        ).add_to(m)

    # Add Layer Control to toggle basemaps
    folium.LayerControl().add_to(m)

    # Render Map in Streamlit (responsive width)
    st_folium(m, width="100%", height=650, returned_objects=[])

# -----------------------------------------
# 7. RIGHT PANEL (Company Explorer)
# -----------------------------------------
with col_right:
    st.markdown("### Company Information")
    
    # Dropdown to select a specific company
    company_list = filtered_df['company'].sort_values().tolist()
    if company_list:
        selected_company = st.selectbox("Select Company", company_list)
        
        # Fetch company details
        company_info = filtered_df[filtered_df['company'] == selected_company].iloc[0]
        
        # Display Info (Styling with markdown blockquotes for structure)
        if pd.notna(company_info['logo']):
            st.image(company_info['logo'], width=150)
            
        st.markdown(f"**Location:** {company_info['city']}, {company_info['state']}")
        st.markdown(f"**Phone:** {company_info['phone']}")
        st.markdown(f"**Email:** {company_info['email']}")
        st.markdown(f"**Website:** [{company_info['website']}](http://{company_info['website']})")
        
        st.markdown("---")
        st.markdown("**Description:**")
        st.markdown(f"> {company_info['description']}")
    else:
        st.info("No companies found for this selection.")
