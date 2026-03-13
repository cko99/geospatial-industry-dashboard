import streamlit as st
import pandas as pd
import folium
import plotly.express as px
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.markdown("""
<style>

/* wallpaper */
.stApp{
background-image:url("https://images.unsplash.com/photo-1469474968028-56623f02e42e");
background-size:cover;
background-position:center;
background-attachment:fixed;
}

/* transparent container */
.block-container{
background:transparent;
}

/* FIXED HEADER */
.custom-header{
position:fixed;
top:0;
left:0;
width:100%;
height:60px;
display:flex;
align-items:center;
justify-content:center;
font-size:26px;
font-weight:700;
color:var(--text-color);
z-index:999;
}

/* push page content down */
.main .block-container{
padding-top:80px;
}

</style>
""", unsafe_allow_html=True)

st.markdown(
'<div class="custom-header">Geospatial Industry Dashboard</div>',
unsafe_allow_html=True
)

# =========================
# HEADER TITLE IN TOOLBAR (center, auto light/dark)
# =========================
st.markdown("""
<style>
header[data-testid="stHeader"]{ position:relative; }
header[data-testid="stHeader"]::before{
    content:"Geospatial Industry Dashboard";
    position:absolute;
    left:50%;
    transform:translateX(-50%);
    font-size:26px;
    font-weight:700;
    color:var(--text-color);
}
</style>
""", unsafe_allow_html=True)

# =========================
# GOOGLE SHEET DATA (header starts at B2 -> header=1)
# =========================
sheet_url = "https://docs.google.com/spreadsheets/d/1Yge8HlHEiQUTazaQ1yy0hYney22MFMYzlMBfjBoWHD8/export?format=csv"

try:
    data = pd.read_csv(sheet_url, header=1)
    # buang kolum kosong dari A
    data = data.loc[:, ~data.columns.str.contains("^Unnamed")]
    # kemaskan nama kolum
    data.columns = data.columns.str.strip().str.lower()
except Exception as e:
    st.error("Google Sheet failed to load")
    st.write(e)
    st.stop()

# =========================
# FILTER
# =========================
industry_filter = st.selectbox(
    "Filter Industry",
    ["All"] + sorted(data["industry"].dropna().unique().tolist())
)
if industry_filter != "All":
    data = data[data["industry"] == industry_filter]

# =========================
# LAYOUT
# =========================
col_left, col_map, col_right = st.columns([1, 2, 1])

# =========================
# LEFT PANEL
# =========================
with col_left:
    st.subheader("Industry Distribution")

    industry_count = data["industry"].value_counts().reset_index()
    industry_count.columns = ["industry", "count"]

    fig = px.pie(industry_count, values="count", names="industry")
    fig.update_layout(legend=dict(orientation="v", y=0.5, x=1))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Company by State")
    state_count = data["state"].value_counts()
    st.bar_chart(state_count)

    st.subheader("AI Career Assistant")
    question = st.text_input("Ask about geospatial companies")
    if question:
        st.write("Suggested companies:")
        st.write(data["company"].head(5))

# =========================
# MAP PANEL (NO NEATLINE / GRIDLINE)
# =========================
with col_map:

    m = folium.Map(
        location=[4.5,102],
        zoom_start=6,
        tiles=None
    )

    # OpenStreetMap
    folium.TileLayer(
        "OpenStreetMap",
        name="OpenStreetMap"
    ).add_to(m)

    # Satellite (Google Earth style)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="ESRI Satellite",
        name="Satellite",
        overlay=False,
        control=True
    ).add_to(m)

    # Hybrid (Satellite + label)
    folium.TileLayer(
        tiles="https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
        attr="ESRI Labels",
        name="Hybrid Labels",
        overlay=True,
        control=True
    ).add_to(m)

    # Terrain style
    folium.TileLayer(
        "Stamen Terrain",
        name="Terrain"
    ).add_to(m)

    # Marker colours
    color_map = {
        "hydrography": "blue",
        "gis": "green",
        "drone": "red",
        "engineering survey": "purple",
        "remote sensing": "orange",
        "land survey": "darkblue"
    }

    for _, row in data.iterrows():

        popup_text = f"""
        <b>{row.get('company','')}</b><br>
        Industry: {row.get('industry','')}<br>
        State: {row.get('state','')}<br>
        City: {row.get('city','')}
        """

        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=popup_text,
            icon=folium.Icon(color=color_map.get(str(row.get("industry","")).lower(),"gray"))
        ).add_to(m)

    # Basemap switcher
    folium.LayerControl().add_to(m)

    st_folium(m, width=800)

# =========================
# RIGHT PANEL
# =========================
with col_right:
    st.subheader("Company Information")

    company = st.selectbox("Select Company", data["company"])
    info = data[data["company"] == company].iloc[0]

    if "logo" in data.columns and pd.notna(info.get("logo")):
        st.image(info["logo"], width=150)

    st.write("Location:", info.get("city",""), ",", info.get("state",""))
    if "phone" in data.columns:
        st.write("Phone:", info.get("phone",""))
    if "email" in data.columns:
        st.write("Email:", info.get("email",""))
    if "website" in data.columns:
        st.write("Website:", info.get("website",""))

    st.subheader("Description")
    if "description" in data.columns:
        st.write(info.get("description",""))
