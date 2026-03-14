import streamlit as st
import pandas as pd
import folium
import plotly.express as px
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>

.stApp{
background-image:url("https://images.unsplash.com/photo-1469474968028-56623f02e42e");
background-size:cover;
background-position:center;
background-attachment:fixed;
}

/* glass panel */
[data-testid="stVerticalBlock"]{
background:rgba(255,255,255,0.18);
backdrop-filter:blur(10px);
padding:12px;
border-radius:12px;
}

/* header */
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
color:white;
z-index:999;
}

.main .block-container{
padding-top:80px;
}

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="custom-header">Geospatial Industry Dashboard</div>', unsafe_allow_html=True)

# ---------------- DATA ----------------
sheet_url = "https://docs.google.com/spreadsheets/d/1Yge8HlHEiQUTazaQ1yy0hYney22MFMYzlMBfjBoWHD8/export?format=csv"

data = pd.read_csv(sheet_url, header=1)
data = data.loc[:, ~data.columns.str.contains("^Unnamed")]
data.columns = data.columns.str.strip().str.lower()

# ---------------- FILTER ----------------
industry_filter = st.selectbox(
"Filter Industry",
["All"] + sorted(data["industry"].dropna().unique())
)

if industry_filter != "All":
    data = data[data["industry"] == industry_filter]

# ---------------- DEVICE DETECT ----------------
is_mobile = st.sidebar.checkbox("Mobile View (for testing)", False)

# ---------------- LAYOUT ----------------
if is_mobile:
    left = st.container()
    map_col = st.container()
    right = st.container()
else:
    left, map_col, right = st.columns([1.2,2.8,1.2])

# ---------------- LEFT PANEL ----------------
with left:

    st.markdown("### Industry Distribution")

    industry_count = data["industry"].value_counts().reset_index()
    industry_count.columns = ["industry","count"]

    fig = px.pie(industry_count, values="count", names="industry")

    fig.update_layout(
        margin=dict(t=0,b=0,l=0,r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig,use_container_width=True)

    st.markdown("### Company by State")

    state_count = data["state"].value_counts()
    st.bar_chart(state_count)

    st.markdown("### AI Career Assistant")

    q = st.text_input("Ask about companies")

    if q:
        result = data[
        data["industry"].str.contains(q,case=False,na=False) |
        data["company"].str.contains(q,case=False,na=False)
        ]

        if len(result)>0:
            st.write(result["company"].head(5))
        else:
            st.write("No result found")

# ---------------- MAP ----------------
with map_col:

    m = folium.Map(location=[4.5,102],zoom_start=6,tiles=None)

    folium.TileLayer("OpenStreetMap",name="OpenStreetMap").add_to(m)

    folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="ESRI",
    name="Satellite"
    ).add_to(m)

    folium.TileLayer(
    tiles="https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
    attr="ESRI",
    name="Hybrid"
    ).add_to(m)

    folium.TileLayer(
    tiles="https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg",
    attr="Stamen",
    name="Terrain"
    ).add_to(m)

    marker_cluster = MarkerCluster().add_to(m)

    color_map = {
    "drone":"red",
    "gis":"green",
    "hydrography":"blue",
    "remote sensing":"orange",
    "engineering survey":"purple",
    "land survey":"darkblue"
    }

    heat_data=[]

    for _,row in data.iterrows():

        lat=row["latitude"]
        lon=row["longitude"]

        heat_data.append([lat,lon])

        popup=f"""
        <b>{row.get('company')}</b><br>
        Industry: {row.get('industry')}<br>
        City: {row.get('city')}<br>
        State: {row.get('state')}<br>
        <a href='{row.get('website')}' target='_blank'>Website</a>
        """

        folium.Marker(
        location=[lat,lon],
        popup=popup,
        icon=folium.Icon(
        color=color_map.get(str(row["industry"]).lower(),"gray")
        )
        ).add_to(marker_cluster)

    HeatMap(heat_data,radius=25).add_to(m)

    folium.LayerControl().add_to(m)

    legend_html="""
    <div style="
    position: fixed;
    bottom: 40px;
    left: 40px;
    background: rgba(255,255,255,0.7);
    padding:10px;
    border-radius:10px;
    z-index:9999;
    font-size:14px;
    ">
    <b>Industry</b><br>
    <span style='color:red'>●</span> Drone<br>
    <span style='color:green'>●</span> GIS<br>
    <span style='color:blue'>●</span> Hydrography<br>
    <span style='color:orange'>●</span> Remote Sensing<br>
    <span style='color:purple'>●</span> Engineering Survey<br>
    <span style='color:darkblue'>●</span> Land Survey
    </div>
    """

    m.get_root().html.add_child(folium.Element(legend_html))

    map_height = 500 if is_mobile else 650

    st_folium(m,width=None,height=map_height)

# ---------------- RIGHT PANEL ----------------
with right:

    st.markdown("### Company Information")

    company = st.selectbox("Select Company",data["company"])

    info = data[data["company"]==company].iloc[0]

    if "logo" in data.columns and pd.notna(info.get("logo")):
        st.image(info["logo"],width=160)

    st.write("Location:",info.get("city"),",",info.get("state"))

    if "phone" in data.columns:
        st.write("Phone:",info.get("phone"))

    if "email" in data.columns:
        st.write("Email:",info.get("email"))

    if "website" in data.columns:
        st.write("Website:",info.get("website"))

    st.markdown("### Description")

    if "description" in data.columns:
        st.write(info.get("description"))

    st.download_button(
    "Download CSV",
    data.to_csv(index=False),
    file_name="geospatial_companies.csv"
    )