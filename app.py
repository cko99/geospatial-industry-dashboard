import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# PAGE CONFIG
st.set_page_config(layout="wide")

# BACKGROUND + TITLE STYLE
st.markdown("""
<style>

.stApp {
background-image: url("https://images.unsplash.com/photo-1500530855697-b586d89ba3ee");
background-size: cover;
}

h1 {
text-align: center;
color: white;
}

</style>
""", unsafe_allow_html=True)

# TITLE
st.title("Geospatial Industry Dashboard")

# GOOGLE SHEET CSV LINK
sheet_url = "https://docs.google.com/spreadsheets/d/1Yge8HlHEiQUTazaQ1yy0hYney22MFMYzlMBfjBoWHD8/export?format=csv"

# LOAD DATA
try:
    data = pd.read_csv(sheet_url)
data.columns = data.columns.str.strip().str.lower()
except:
    st.error("Failed to load Google Sheet data. Check sharing permission.")
    st.stop()

# DASHBOARD ANALYTICS
st.subheader("Industry Distribution")
industry_count = data["industry"].value_counts()
st.bar_chart(industry_count)

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

    question = st.text_input(
    "Ask about geospatial companies"
    )

    if question:
        st.write("Suggested companies:")
        st.write(data["company"].head(3))


# MAP PANEL
with col2:

    m = folium.Map(location=[4.5,102], zoom_start=6)

    # MARKER COLOUR BY INDUSTRY
    color_map = {
        "Hydrography": "blue",
        "GIS": "green",
        "Drone": "red",
        "Engineering Survey": "purple",
        "Remote Sensing": "orange",
        "Land Survey": "darkblue"
    }

    for i,row in data.iterrows():

        if pd.notna(row["latitude"]) and pd.notna(row["longitude"]):

            popup_text = f"""
            <b>{row['company']}</b><br>
            Industry: {row['industry']}<br>
            State: {row['state']}
            """

            folium.Marker(
            location=[row["latitude"],row["longitude"]],
            popup=popup_text,
            icon=folium.Icon(color=color_map.get(row["industry"],"gray"))
            ).add_to(m)

    st_folium(m,width=800)


# COMPANY INFO PANEL
with col3:

    st.header("Company Information")

    company = st.selectbox(
    "Select Company",
    data["company"]
    )

    info = data[data["company"] == company].iloc[0]

    if pd.notna(info["logo"]):
        st.image(info["logo"],width=150)

    st.write("City:",info["city"])
    st.write("State:",info["state"])
    st.write("Phone:",info["phone"])
    st.write("Email:",info["email"])
    st.write("Website:",info["website"])
