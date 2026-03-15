import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px
from sklearn.cluster import KMeans

# --------------------------------------
# PAGE CONFIG
# --------------------------------------

st.set_page_config(
    page_title="Geospatial Industry Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------
# CSS
# --------------------------------------

st.markdown("""
<style>

html, body, [data-testid="stAppViewContainer"]{
height:100vh;
overflow:hidden;
}

.stApp{
background-image:url("https://images.unsplash.com/photo-1469474968028-56623f02e42e");
background-size:cover;
background-position:center;
}

.block-container{
padding-top:0.5rem;
padding-bottom:0rem;
padding-left:2rem;
padding-right:2rem;
}

div[data-testid="stVerticalBlock"] > div{
background:rgba(20,20,20,0.55);
padding:14px;
border-radius:14px;
backdrop-filter:blur(10px);
border:1px solid rgba(255,255,255,0.1);
color:white;
}

.header-text{
text-align:center;
font-size:28px;
font-weight:800;
color:white;
margin-bottom:6px;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------
# LOAD DATA (CACHE)
# --------------------------------------

@st.cache_data
def load_data():

    sheet_url = "https://docs.google.com/spreadsheets/d/1Yge8HlHEiQUTazaQ1yy0hYney22MFMYzlMBfjBoWHD8/export?format=csv"

    df = pd.read_csv(sheet_url, header=1)

    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.columns = df.columns.str.strip().str.lower()

    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    df["industry"] = df["industry"].fillna("Unknown")

    df = df.dropna(subset=["latitude","longitude"])

    return df

data = load_data()

# --------------------------------------
# HEADER
# --------------------------------------

st.markdown(
'<div class="header-text">Geospatial Industry Dashboard</div>',
unsafe_allow_html=True
)

# --------------------------------------
# KPI
# --------------------------------------

k1,k2,k3,k4 = st.columns(4)

k1.metric("Total Companies", len(data))
k2.metric("Total Industries", data["industry"].nunique())
k3.metric("Top State", data["state"].mode()[0])
k4.metric("Top Industry", data["industry"].mode()[0])

# --------------------------------------
# FILTER
# --------------------------------------

industries = ["All"] + sorted(data["industry"].unique())

_,fcol,_ = st.columns([1,2,1])

with fcol:

    selected_industry = st.selectbox(
        "Industry Filter",
        industries,
        label_visibility="collapsed"
    )

if selected_industry == "All":
    df = data.copy()
else:
    df = data[data["industry"] == selected_industry].copy()

# --------------------------------------
# CLUSTER ANALYSIS
# --------------------------------------

coords = df[["latitude","longitude"]]

if len(coords) >= 3:

    kmeans = KMeans(n_clusters=3, random_state=0)

    df["cluster"] = kmeans.fit_predict(coords)

else:

    df["cluster"] = 0

# --------------------------------------
# MAIN LAYOUT
# --------------------------------------

col_left, col_map, col_right = st.columns([1,2.2,1.2], gap="small")

# --------------------------------------
# LEFT PANEL
# --------------------------------------

with col_left:

    st.markdown("### Industry Distribution")

    fig_pie = px.pie(
        df,
        names="industry",
        hole=0.45
    )

    fig_pie.update_layout(
        height=220,
        margin=dict(t=0,b=0,l=0,r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True,
        config={"displayModeBar":False}
    )

    st.markdown("### Company by State")

    state_counts = df["state"].value_counts().reset_index()
    state_counts.columns = ["state","count"]

    fig_bar = px.bar(
        state_counts,
        x="state",
        y="count"
    )

    fig_bar.update_layout(
        height=200,
        margin=dict(t=10,b=0,l=0,r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True,
        config={"displayModeBar":False}
    )

    st.markdown("### AI Career Assistant")

    query = st.text_input(
        "Ask",
        placeholder="Which drone companies exist?"
    )

    if query:

        result = data[
            data["industry"].str.contains(query, case=False, na=False) |
            data["company"].str.contains(query, case=False, na=False)
        ]

        if not result.empty:

            for c in result["company"].head(5):

                st.write("•",c)

        else:

            st.write("No company found")

# --------------------------------------
# MAP PANEL
# --------------------------------------

with col_map:

    m = folium.Map(
        location=[4.5,102],
        zoom_start=6,
        tiles=None
    )

    folium.TileLayer("openstreetmap", name="OpenStreetMap").add_to(m)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite imagery",
        overlay=False
    ).add_to(m)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Hybrid",
        overlay=True
    ).add_to(m)

    folium.TileLayer(
        tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        attr="OpenTopoMap",
        name="Terrain"
    ).add_to(m)

    # Heatmap

    heat_data = df[["latitude","longitude"]].values.tolist()

    HeatMap(
        heat_data,
        radius=18,
        blur=15
    ).add_to(m)

    color_map = {
        "Drone":"red",
        "GIS":"green",
        "Hydrography":"blue",
        "Remote Sensing":"orange",
        "Engineering Survey":"purple",
        "Land Survey":"darkblue"
    }

    for _,row in df.iterrows():

        if pd.isna(row["latitude"]) or pd.isna(row["longitude"]):
            continue

        popup_html=f"""
        <b>{row['company']}</b><br>
        Industry: {row['industry']}<br>
        {row['city']}, {row['state']}<br>
        <a href='http://{row['website']}' target='_blank'>Website</a>
        """

        folium.Marker(
            location=[row["latitude"],row["longitude"]],
            tooltip=row["company"],
            popup=popup_html,
            icon=folium.Icon(
                color=color_map.get(row["industry"],"gray")
            )
        ).add_to(m)

    folium.LayerControl().add_to(m)

    st_folium(
        m,
        width="100%",
        height=600
    )

# --------------------------------------
# RIGHT PANEL
# --------------------------------------

with col_right:

    st.markdown("### Company Explorer")

    companies = df["company"].sort_values().tolist()

    if companies:

        selected_company = st.selectbox(
            "Select Company",
            companies,
            label_visibility="collapsed"
        )

        info = df[df["company"] == selected_company].iloc[0]

        if pd.notna(info["logo"]):
            st.image(info["logo"], width=120)

        st.write(f"**Location:** {info['city']}, {info['state']}")
        st.write(f"**Phone:** {info['phone']}")
        st.write(f"**Email:** {info['email']}")
        st.write(f"**Website:** {info['website']}")

        st.markdown(
        f"> {info['description']}"
        )

    st.markdown("### Top Companies")

    rank = df[["company","industry","state"]].copy()

    rank["score"] = range(len(rank),0,-1)

    st.dataframe(
        rank.head(10),
        use_container_width=True,
        height=220
    )
