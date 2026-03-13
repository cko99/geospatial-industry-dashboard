import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

st.title("Geospatial Industry Dashboard")

# GOOGLE SHEET CSV LINK
sheet_url = "https://docs.google.com/spreadsheets/d/1Yge8HlHEiQUTazaQ1yy0hYney22MFMYzlMBfjBoWHD8/export?format=csv"

# LOAD DATA
try:
    data = pd.read_csv(sheet_url, header=1)

    # buang column kosong dari column A
    data = data.loc[:, ~data.columns.str.contains("^Unnamed")]

    # kemaskan nama column
    data.columns = data.columns.str.strip().str.lower()

except Exception as e:
    st.error("Failed to load Google Sheet")
    st.write(e)
    st.stop()

# ======================
# DASHBOARD ANALYTICS
# ======================

st.subheader("Industry Distribution")
industry_count = data["industry"].value_counts()
st.bar_chart(industry_count)

st.subheader("Company by State")
state_count = data["state"].value_counts()
st.bar_chart(state_count)

# ======================
# FILTER
# ======================

industry_filter = st.selectbox(
    "Filter Industry",
    ["All"] + list(data["industry"].unique())
)

if industry_filter != "All":
    data = data[data["industry"] == industry_filter]

# ======================
# LAYOUT
# ======================

col1, col2, col3 = st.columns([1,2,1])

# ======================
# AI PANEL
# ======================

with col1:

    st.header("AI Career Assistant")

    question = st.text_input("Ask about geospatial companies")

    if question:
        st.write("Suggested companies:")
        st.write(data["company"].head(3))


# ======================
# MAP
# ======================

with col2:

    m = folium.Map(location=[4.5,102], zoom_start=6)

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
        <b>{row['company']}</b><br>
        Industry: {row['industry']}<br>
        State: {row['state']}<br>
        City: {row['city']}
        """

        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=popup_text,
            icon=folium.Icon(color=color_map.get(row["industry"].lower(),"gray"))
        ).add_to(m)

    st_folium(m,width=800)


# ======================
# COMPANY INFO
# ======================

with col3:

    st.header("Company Information")

    company = st.selectbox(
        "Select Company",
        data["company"]
    )

    info = data[data["company"] == company].iloc[0]

    if pd.notna(info["logo"]):
        st.image(info["logo"], width=150)

    st.write("Location:", info["city"], ",", info["state"])
    st.write("Phone:", info["phone"])
    st.write("Email:", info["email"])
    st.write("Website:", info["website"])
