import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- CONFIG ---
st.set_page_config(layout="wide", page_title="Geospatial Industry Dashboard")

# OPTIONAL: simple background / style
st.markdown(
    """
    <style>
    .stApp { background-color: #0f1720; }
    h1 { text-align:center; color: #ffffff; margin-top: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Geospatial Industry Dashboard")

# -------------------------
# GOOGLE SHEET CSV (update jika perlu)
# Jika header anda berada pada row ke-2 (seperti screenshot), gunakan header=1
SHEET_ID = "1Yge8HlHEiQUTazaQ1yy0hYney22MFMYzlMBfjBoWHD8"
sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"
# Jika sheet tidak bernama "Sheet1", tukar nama setelah &sheet=

# -------------------------
# LOAD & CLEAN DATA
try:
    # Use header=1 if your actual header row is the second row in the sheet (index 1).
    # If your header is the first row, change header=0.
    data = pd.read_csv(sheet_url, header=1)
    # normalize column names
    data.columns = data.columns.astype(str).str.strip().str.lower()

except Exception as e:
    st.error("Gagal load Google Sheet. Pastikan Share permission 'Anyone with the link' dan link CSV betul.")
    st.write("Error detail:", e)
    st.stop()

# Minimal required columns for basic functionality
required_min = ["company", "latitude", "longitude"]
missing_min = [c for c in required_min if c not in data.columns]

if missing_min:
    st.error(f"Column(s) wajib tak ditemui: {missing_min}. Pastikan header Google Sheet EXACTLY seperti yang diperlukan.")
    st.info("Contoh header yang disarankan: company, industry, state, city, country, latitude, longitude, website, logo, phone, email, description")
    st.stop()

# Ensure industry/state exist (create fallback columns if not present)
if "industry" not in data.columns:
    data["industry"] = "unknown"
else:
    data["industry"] = data["industry"].fillna("unknown").astype(str).str.strip()

if "state" not in data.columns:
    data["state"] = "unknown"
else:
    data["state"] = data["state"].fillna("unknown").astype(str).str.strip()

# Parse lat/lon to numeric and drop rows without coords
data["latitude"] = pd.to_numeric(data["latitude"], errors="coerce")
data["longitude"] = pd.to_numeric(data["longitude"], errors="coerce")

# Drop rows that don't have proper coordinates
before = len(data)
data = data.dropna(subset=["latitude", "longitude"]).reset_index(drop=True)
after = len(data)
if after == 0:
    st.error("Tiada row dengan latitude/longitude yang sah. Sila semak nilai lat/lon di Google Sheet.")
    st.stop()

# Optional: show which columns detected (help debugging)
# st.write("Columns detected:", list(data.columns))

# -------------------------
# DASHBOARD: Charts + Filters
st.subheader("Industry Distribution")
industry_count = data["industry"].value_counts()
st.bar_chart(industry_count)

st.subheader("Company by State")
state_count = data["state"].value_counts()
st.bar_chart(state_count)

# Industry filter
industry_choices = ["All"] + sorted(data["industry"].dropna().unique().tolist())
industry_filter = st.selectbox("Filter Industry", industry_choices)

if industry_filter != "All":
    data = data[data["industry"] == industry_filter].reset_index(drop=True)

# -------------------------
# LAYOUT: left = AI, center = map, right = info
col1, col2, col3 = st.columns([1, 2, 1])

# LEFT: simple AI assistant input (placeholder)
with col1:
    st.header("AI Career Assistant")
    q = st.text_input("Tanya (contoh: 'cadangkan syarikat drone di Selangor')")
    if q:
        # simple heuristic reply: show top 5 companies matching keyword
        kw = q.lower().strip()
        matches = data[data.apply(lambda r: kw in str(r["industry"]).lower() or kw in str(r.get("description","")).lower() or kw in str(r["company"]).lower(), axis=1)]
        if len(matches) == 0:
            st.write("Tiada cadangan khusus. Cuba guna kata kunci lain.")
        else:
            st.write("Cadangan (dari data):")
            st.write(matches[["company","industry","state","city"]].head(10))

# CENTER: interactive map
with col2:
    st.header("")  # keeps spacing aligned

    # colour mapping by industry (use lowercase keys)
    color_map = {
        "hydrography": "blue",
        "gis": "green",
        "drone": "red",
        "engineering survey": "purple",
        "remote sensing": "orange",
        "land survey": "darkblue",
        "unknown": "gray"
    }

    m = folium.Map(location=[4.5, 102], zoom_start=6, control_scale=True)

    for _, row in data.iterrows():
        lat = float(row["latitude"])
        lon = float(row["longitude"])
        industry_key = str(row.get("industry","unknown")).lower()
        color = color_map.get(industry_key, "gray")

        # popup with HTML (logo if available)
        logo_html = ""
        if "logo" in data.columns and pd.notna(row.get("logo")) and str(row.get("logo")).strip() != "-":
            logo = str(row.get("logo")).strip()
            logo_html = f'<img src="{logo}" alt="logo" style="width:120px;"><br>'

        popup_html = f"""
        {logo_html}
        <b>{row.get('company','')}</b><br>
        Industry: {row.get('industry','')}<br>
        State: {row.get('state','')}<br>
        City: {row.get('city','')}
        """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color=color)
        ).add_to(m)

    st_folium(m, width=800, returned_objects=[])

# RIGHT: company information panel
with col3:
    st.header("Company Information")
    companies = data["company"].fillna("Unnamed").astype(str).tolist()
    chosen = st.selectbox("Select Company", companies)

    info = data[data["company"].astype(str) == chosen]
    if not info.empty:
        r = info.iloc[0]
        if "logo" in data.columns and pd.notna(r.get("logo")) and str(r.get("logo")).strip() != "-":
            try:
                st.image(r.get("logo"), width=180)
            except:
                st.write("Logo tidak boleh dipaparkan.")
        st.write("Company:", r.get("company",""))
        if "city" in data.columns:
            st.write("City:", r.get("city",""))
        st.write("State:", r.get("state",""))
        if "phone" in data.columns:
            st.write("Phone:", r.get("phone",""))
        if "email" in data.columns:
            st.write("Email:", r.get("email",""))
        if "website" in data.columns:
            st.write("Website:", r.get("website",""))
        if "description" in data.columns:
            st.write("Description:", r.get("description",""))
    else:
        st.write("No info available for selected company.")
