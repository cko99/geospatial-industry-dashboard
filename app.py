import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

# =========================
# TITLE
# =========================

st.markdown("""
<style>

/* center title in streamlit toolbar */
header[data-testid="stHeader"]{
    position:relative;
}

/* dashboard title */
header[data-testid="stHeader"]::before{
    content:"Geospatial Industry Dashboard";
    position:absolute;
    left:50%;
    transform:translateX(-50%);
    font-size:26px;
    font-weight:700;
    color:var(--text-color);
    pointer-events:none;
}

</style>
""", unsafe_allow_html=True)





# =========================
# GOOGLE SHEET
# =========================

sheet_url = "https://docs.google.com/spreadsheets/d/1Yge8HlHEiQUTazaQ1yy0hYney22MFMYzlMBfjBoWHD8/export?format=csv"

try:
    data = pd.read_csv(sheet_url, header=1)

    # remove unnamed columns
    data = data.loc[:, ~data.columns.str.contains("^Unnamed")]

    # clean column names
    data.columns = data.columns.str.strip().str.lower()

except Exception as e:

    st.error("Google Sheet failed to load")
    st.write(e)
    st.stop()

# =========================
# INDUSTRY STATS
# =========================

industry_count = data["industry"].value_counts()

# =========================
# STATE STATS
# =========================

state_count = data["state"].value_counts()

# =========================
# INDUSTRY FILTER
# =========================

industry_filter = st.selectbox(
"Filter Industry",
["All"] + list(data["industry"].unique())
)

if industry_filter != "All":
    data = data[data["industry"] == industry_filter]

# =========================
# LAYOUT
# =========================

col_left, col_map, col_right = st.columns([1,2,1])

# =========================
# LEFT PANEL
# =========================

with col_left:

st.subheader("Industry Distribution")

industry_count = data["industry"].value_counts().reset_index()
industry_count.columns = ["industry","count"]

fig = px.pie(
    industry_count,
    values="count",
    names="industry",
    title="",
)

fig.update_layout(
    legend=dict(
        orientation="v",
        y=0.5,
        x=1
    )
)

st.plotly_chart(fig, use_container_width=True)

    st.subheader("Company by State")
    st.bar_chart(state_count)

    st.subheader("AI Career Assistant")

    question = st.text_input("Ask about geospatial companies")

    if question:

        st.write("Suggested companies:")

        st.write(data["company"].head(5))


# =========================
# NEATLINE FUNCTION
# =========================

def draw_neatline(m):

    north = 7.5
    south = 1.0
    west = 95.0
    east = 110.0

    steps = 10

    lat_step = (north - south) / steps
    lon_step = (east - west) / steps

    # LEFT & RIGHT (horizontal ticks)

    for i in range(steps + 1):

        lat = south + i * lat_step

        folium.PolyLine(
        [(lat, west),(lat, west + 0.3)],
        color="black",
        weight=2
        ).add_to(m)

        folium.PolyLine(
        [(lat, east - 0.3),(lat, east)],
        color="black",
        weight=2
        ).add_to(m)

    # TOP & BOTTOM (vertical ticks)

    for i in range(steps + 1):

        lon = west + i * lon_step

        folium.PolyLine(
        [(north - 0.3, lon),(north, lon)],
        color="black",
        weight=2
        ).add_to(m)

        folium.PolyLine(
        [(south, lon),(south + 0.3, lon)],
        color="black",
        weight=2
        ).add_to(m)

    # outer frame

    folium.Rectangle(
        bounds=[[south,west],[north,east]],
        color="black",
        weight=3,
        fill=False
    ).add_to(m)


# =========================
# MAP PANEL
# =========================

with col_map:

    m = folium.Map(location=[4.5,102], zoom_start=6)

    draw_neatline(m)

    color_map = {
        "hydrography":"blue",
        "gis":"green",
        "drone":"red",
        "engineering survey":"purple",
        "remote sensing":"orange",
        "land survey":"darkblue"
    }

    for _,row in data.iterrows():

        popup_text = f"""
        <b>{row['company']}</b><br>
        Industry: {row['industry']}<br>
        State: {row['state']}<br>
        City: {row['city']}
        """

        folium.Marker(
        location=[row["latitude"],row["longitude"]],
        popup=popup_text,
        icon=folium.Icon(
        color=color_map.get(row["industry"].lower(),"gray")
        )
        ).add_to(m)

    st_folium(m,width=800)


# =========================
# RIGHT PANEL
# =========================

with col_right:

    st.subheader("Company Information")

    company = st.selectbox(
    "Select Company",
    data["company"]
    )

    info = data[data["company"] == company].iloc[0]

    if pd.notna(info["logo"]):

        st.image(info["logo"],width=150)

    st.write("Location:",info["city"],",",info["state"])

    st.write("Phone:",info["phone"])

    st.write("Email:",info["email"])

    st.write("Website:",info["website"])

    st.subheader("Description")

    st.write(info["description"])
