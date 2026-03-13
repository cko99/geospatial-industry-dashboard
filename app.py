import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# PAGE CONFIG
st.set_page_config(layout="wide")

# TITLE
st.title("Geospatial Industry Dashboard")

# GOOGLE SHEET CSV
sheet_url = "https://docs.google.com/spreadsheets/d/1Yge8HlHEiQUTazaQ1yy0hYney22MFMYzlMBfjBoWHD8/export?format=csv"

# LOAD DATA
try:
    data = pd.read_csv(sheet_url)

    # CLEAN COLUMN NAMES
    data.columns = data.columns.str.strip().str.lower()

except Exception as e:
    st.error("Failed to load Google Sheet data.")
    st.write(e)
    st.stop()

# DEBUG: TUNJUK COLUMN UNTUK CHECK
st.write("Columns detected:", data.columns)

# CHECK REQUIRED COLUMN
required_cols = ["company","industry","state","latitude","longitude"]

for col in required_cols:
    if col not in data.columns:
        st.error(f"Column '{col}' not found in Google Sheet.")
        st.stop()

# INDUSTRY CHART
st.subheader("Industry Distribution")

industry_count = data["industry"].value_counts()

st.bar_chart(industry_count)

# STATE CHART
st.subheader("Company by State")

state_count = data["state"].value_counts()

st.bar_chart(state_count)

# INDUSTRY FILTER
industry_filter = st.selectbox(
    "Filter Industry",
    ["All"] + list(data["industry"].dropna().unique())
)

if industry_filter != "All":
    data = data[data["industry"] == industry_filter]

# LAYOUT
col1, col2, col3 = st.columns([1,2,1])

# AI PANEL
with col1:

    st.header("AI Career Assistant")

    question = st.text_input("Ask about geospatial companies")

    if question:
        st.write("Suggested companies:")
        st.write(data["company"].head(3))


# MAP
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

        if pd.notna(row["latitude"]) and pd.notna(row["longitude"]):

            popup = f"""
            <b>{row['company']}</b><br>
            Industry: {row['industry']}<br>
            State: {row['state']}
            """

            folium.Marker(
                [row["latitude"], row["longitude"]],
                popup=popup,
                icon=folium.Icon(color=color_map.get(str(row["industry"]).lower(),"gray"))
            ).add_to(m)

    st_folium(m,width=800)

# COMPANY INFO
with col3:

    st.header("Company Information")

    company = st.selectbox("Select Company", data["company"])

    info = data[data["company"] == company].iloc[0]

    if "logo" in data.columns and pd.notna(info["logo"]):
        st.image(info["logo"],width=150)

    if "city" in data.columns:
        st.write("City:", info["city"])

    st.write("State:", info["state"])

    if "phone" in data.columns:
        st.write("Phone:", info["phone"])

    if "email" in data.columns:
        st.write("Email:", info["email"])

    if "website" in data.columns:
        st.write("Website:", info["website"])
