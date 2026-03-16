import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import requests
import io

# ─────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Geospatial Industry Dashboard — Malaysia",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTfyM6laDl4zieKhx6YjtG9GlGXFyMPuU-EMbvBuAgJiiPowTTOD0WhY0TmabGm-ibbTQuD1hL__v9X"
    "/pub?output=csv"
)

INDUSTRY_COLORS = {
    "Drone":              "#ff4d4d",
    "GIS":                "#4dff88",
    "Hydrography":        "#4da6ff",
    "Remote Sensing":     "#ff9944",
    "Engineering Survey": "#cc66ff",
    "Land Survey":        "#4477ff",
}
DEFAULT_COLOR = "#aaaaaa"

# Column name aliases (lowercase, stripped) → internal key
COL_ALIASES = {
    "name":     ["company", "name", "companyname"],
    "industry": ["industry", "sector", "category", "type"],
    "state":    ["state", "negeri", "province"],
    "city":     ["city", "bandar", "town", "municipality"],
    "country":  ["country", "negara"],
    "lat":      ["latitude", "lat"],
    "lng":      ["longitude", "lng", "long", "lon"],
    "web":      ["website", "web", "url", "link"],
    "logo":     ["logo", "logourl", "icon"],
    "phone":    ["phone", "tel", "telephone", "contact"],
    "email":    ["email", "emel", "mail"],
    "desc":     ["description", "desc", "about", "summary"],
}

# ─────────────────────────────────────────────
# DARK THEME CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base ───────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background: #020810 !important;
}
[data-testid="stAppViewContainer"] > .main {
    background: #020810;
}
[data-testid="stSidebar"] {
    background: rgba(4,10,22,0.97) !important;
    border-right: 1px solid rgba(100,200,255,0.12);
}
[data-testid="stSidebar"] * { color: #e8f4ff !important; }

/* ── Global text ───────────────────────── */
h1,h2,h3,h4,p,label,span,div {
    color: #e8f4ff;
    font-family: 'Space Grotesk', sans-serif;
}

/* ── Header banner ─────────────────────── */
.dash-header {
    background: rgba(4,10,22,0.97);
    border-bottom: 1px solid rgba(100,200,255,0.12);
    padding: 14px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    border-radius: 8px;
}
.dash-header-title {
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #e8f4ff;
    text-align: center;
    flex: 1;
}
.dash-header-title em { color: #00d4ff; font-style: normal; }
.dash-header-logo {
    font-size: 11px;
    font-weight: 600;
    color: #00d4ff;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 8px;
}
.live-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #00ff9d;
    animation: pulse 2s infinite;
    margin-right: 4px;
}
@keyframes pulse {
    0%,100% { box-shadow: 0 0 0 0 rgba(0,255,157,0.4); }
    50%      { box-shadow: 0 0 0 4px rgba(0,255,157,0); }
}

/* ── KPI cards ──────────────────────────── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 16px;
}
.kpi-card {
    background: rgba(0,30,60,0.5);
    border: 1px solid rgba(0,150,200,0.15);
    border-radius: 9px;
    padding: 12px 14px;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    gap: 12px;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, #00d4ff, transparent);
    opacity: 0.4;
}
.kpi-icon { font-size: 22px; }
.kpi-value {
    font-size: 22px;
    font-weight: 700;
    color: #e8f4ff;
    line-height: 1;
    font-family: 'JetBrains Mono', monospace;
}
.kpi-label {
    font-size: 9px;
    color: rgba(180,210,255,0.65);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 2px;
}

/* ── Section titles ─────────────────────── */
.sec-title {
    font-size: 9px;
    font-weight: 700;
    color: #00d4ff;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(100,200,255,0.12);
}

/* ── Company profile card ───────────────── */
.profile-card {
    background: rgba(0,25,55,0.4);
    border: 1px solid rgba(0,150,200,0.15);
    border-radius: 9px;
    padding: 14px;
    margin-top: 8px;
}
.profile-logo {
    width: 44px; height: 44px;
    border-radius: 8px;
    background: rgba(0,40,80,0.7);
    border: 1px solid rgba(0,150,200,0.25);
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; font-weight: 700;
    margin-bottom: 8px;
    float: left;
    margin-right: 12px;
}
.profile-name {
    font-size: 13px;
    font-weight: 600;
    color: #e8f4ff;
    line-height: 1.3;
}
.profile-badge {
    display: inline-block;
    font-size: 8px;
    padding: 2px 8px;
    border-radius: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 4px;
}
.detail-row {
    display: flex;
    gap: 8px;
    font-size: 10px;
    margin: 3px 0;
    clear: left;
}
.detail-label { color: rgba(120,160,200,0.5); min-width: 50px; }
.detail-value { color: rgba(180,210,255,0.7); }
.profile-desc {
    font-size: 10px;
    color: rgba(180,210,255,0.6);
    line-height: 1.6;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid rgba(100,200,255,0.1);
}

/* ── AI search results ──────────────────── */
.ai-result {
    background: rgba(0,30,60,0.5);
    border: 1px solid rgba(0,150,200,0.18);
    border-radius: 7px;
    padding: 8px 11px;
    margin-bottom: 5px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 9px;
}
.ai-result-name { font-size: 11px; font-weight: 500; color: #e8f4ff; }
.ai-result-meta { font-size: 9px; color: rgba(180,210,255,0.5); }

/* ── Top companies table ────────────────── */
.top-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 10px;
}
.top-table th {
    color: rgba(120,160,200,0.5);
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-size: 8px;
    padding: 4px 8px;
    border-bottom: 1px solid rgba(100,200,255,0.1);
    text-align: left;
}
.top-table td {
    padding: 5px 8px;
    border-bottom: 1px solid rgba(0,100,150,0.07);
    color: rgba(180,210,255,0.7);
}

/* ── Streamlit widget overrides ─────────── */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stMultiSelect > div > div {
    background: rgba(0,20,50,0.7) !important;
    border: 1px solid rgba(0,150,200,0.25) !important;
    color: #e8f4ff !important;
    border-radius: 6px !important;
}
.stButton > button {
    background: rgba(0,212,255,0.08) !important;
    border: 1px solid rgba(0,212,255,0.3) !important;
    color: #00d4ff !important;
    border-radius: 6px !important;
    font-size: 11px !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    background: rgba(0,212,255,0.18) !important;
    border-color: #00d4ff !important;
}
[data-testid="metric-container"] {
    background: rgba(0,30,60,0.5);
    border: 1px solid rgba(0,150,200,0.15);
    border-radius: 9px;
    padding: 10px 14px;
}
.stPlotlyChart, .stFoliumChart { border-radius: 8px; overflow: hidden; }
div[data-testid="column"] > div { gap: 0 !important; }
.block-container { padding-top: 1rem !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
def normalise_col(name: str) -> str:
    """Lowercase and strip non-alphanumeric chars for fuzzy header matching."""
    import re
    return re.sub(r"[^a-z0-9]", "", name.lower())


def find_col(headers_norm: list[str], aliases: list[str]) -> str | None:
    """Return the original header name that matches any alias, or None."""
    for alias in aliases:
        if alias in headers_norm:
            return headers_norm[alias]
    return None


def load_data(url: str) -> pd.DataFrame:
    """Fetch published Google Sheet CSV and return a clean DataFrame."""
    proxies = [
        url,
        f"https://corsproxy.io/?{requests.utils.quote(url)}",
        f"https://api.allorigins.win/raw?url={requests.utils.quote(url)}",
    ]
    text = None
    for proxy in proxies:
        try:
            r = requests.get(proxy, timeout=10,
                             headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200 and len(r.text) > 30:
                text = r.text
                break
        except Exception:
            continue

    if not text:
        st.error("❌ Tidak dapat fetch data. Pastikan spreadsheet dah di-publish (File → Share → Publish to web → CSV).")
        st.stop()

    df_raw = pd.read_csv(io.StringIO(text))

    # Build normalised header → original header map
    norm_map = {normalise_col(c): c for c in df_raw.columns}

    # Map columns using aliases
    rename = {}
    for internal_key, aliases in COL_ALIASES.items():
        original = find_col(norm_map, aliases)
        if original:
            rename[original] = internal_key

    df = df_raw.rename(columns=rename)

    # Ensure required columns exist
    for col in ("name", "lat", "lng"):
        if col not in df.columns:
            st.error(f"❌ Kolum '{col}' tidak dijumpai dalam spreadsheet. Semak nama header.")
            st.stop()

    # Coerce lat/lng to numeric, drop invalid rows
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], errors="coerce")
    df = df.dropna(subset=["lat", "lng", "name"])
    df = df[df["name"].str.strip() != ""]

    # Fill optional columns with empty strings
    for col in ("industry", "state", "city", "country", "web", "phone", "email", "desc", "logo"):
        if col not in df.columns:
            df[col] = ""
        else:
            df[col] = df[col].fillna("").astype(str).str.strip()

    df["industry"] = df["industry"].replace("", "Other")
    df = df.reset_index(drop=True)
    return df


@st.cache_data(ttl=900)   # cache 15 minutes
def get_data() -> pd.DataFrame:
    return load_data(CSV_URL)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def ind_color(industry: str) -> str:
    return INDUSTRY_COLORS.get(industry, DEFAULT_COLOR)


def make_initials(name: str) -> str:
    parts = name.strip().split()
    return "".join(p[0] for p in parts[:2]).upper() if parts else "?"


def profile_html(row: pd.Series) -> str:
    col = ind_color(row["industry"])
    initials = make_initials(row["name"])
    badge_style = (
        f"background:{col}22;color:{col};"
        f"border:1px solid {col}66;"
    )
    web = row.get("web", "")
    web_link = f'<a href="{"https://" + web if web and not web.startswith("http") else web}" '
    web_link += f'target="_blank" style="color:#00d4ff;text-decoration:none;">{web}</a>' if web else "—"

    return f"""
<div class="profile-card">
  <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:10px;">
    <div style="width:44px;height:44px;border-radius:8px;background:rgba(0,40,80,0.7);
         border:1px solid rgba(0,150,200,0.25);display:flex;align-items:center;
         justify-content:center;font-size:16px;font-weight:700;color:{col};flex-shrink:0;">
      {initials}
    </div>
    <div>
      <div class="profile-name">{row['name']}</div>
      <span class="profile-badge" style="{badge_style}">{row['industry']}</span>
    </div>
  </div>
  <div class="detail-row"><span class="detail-label">Location</span>
    <span class="detail-value">{(row.get('city','') + ', ' if row.get('city') else '') + row.get('state','')}</span></div>
  <div class="detail-row"><span class="detail-label">Phone</span>
    <span class="detail-value">{row.get('phone','') or '—'}</span></div>
  <div class="detail-row"><span class="detail-label">Email</span>
    <span class="detail-value">{row.get('email','') or '—'}</span></div>
  <div class="detail-row"><span class="detail-label">Web</span>
    <span class="detail-value">{web_link}</span></div>
  <div class="profile-desc">{row.get('desc','')}</div>
</div>
"""


# ─────────────────────────────────────────────
# MAP BUILDER
# ─────────────────────────────────────────────
def build_map(df: pd.DataFrame, basemap: str, show_heat: bool) -> folium.Map:
    tile_layers = {
        "Dark":      ("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
                      "© OpenStreetMap © CARTO"),
        "OSM":       ("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                      "© OpenStreetMap contributors"),
        "Satellite": ("https://server.arcgisonline.com/ArcGIS/rest/services/"
                      "World_Imagery/MapServer/tile/{z}/{y}/{x}",
                      "© Esri, USGS, NOAA"),
        "Terrain":   ("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
                      "© OpenTopoMap contributors"),
    }

    tile_url, attr = tile_layers.get(basemap, tile_layers["Dark"])

    fmap = folium.Map(
        location=[4.5, 109.5],
        zoom_start=5,
        tiles=tile_url,
        attr=attr,
        prefer_canvas=True,
    )

    # Hybrid: satellite + labels overlay
    if basemap == "Hybrid":
        folium.TileLayer(
            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="© Esri",
            name="Hybrid",
        ).add_to(fmap)
        folium.TileLayer(
            "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/"
            "World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
            attr="© Esri",
            opacity=0.85,
        ).add_to(fmap)

    # Train overlay on top of OSM
    if basemap == "Train":
        folium.TileLayer(
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            attr="© OpenStreetMap contributors",
        ).add_to(fmap)
        folium.TileLayer(
            "https://{s}.tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png",
            attr="© OpenRailwayMap contributors",
            opacity=0.85,
        ).add_to(fmap)

    # Heatmap layer
    if show_heat and not df.empty:
        heat_data = df[["lat", "lng"]].dropna().values.tolist()
        HeatMap(heat_data, radius=30, blur=20, min_opacity=0.3).add_to(fmap)

    # Markers
    for _, row in df.iterrows():
        color = ind_color(row["industry"])
        web = row.get("web", "")
        web_href = ("https://" + web) if web and not web.startswith("http") else web
        web_html = f'<a href="{web_href}" target="_blank" style="color:#00d4ff">{web} ↗</a>' if web else "—"

        desc_short = str(row.get("desc", ""))
        if len(desc_short) > 100:
            desc_short = desc_short[:100] + "…"

        popup_html = f"""
        <div style="font-family:sans-serif;min-width:200px;background:rgba(4,12,28,0.97);
             border-radius:8px;padding:12px;">
          <div style="font-size:13px;font-weight:700;color:#e8f4ff;margin-bottom:6px;">
            {row['name']}
          </div>
          <div style="font-size:10px;color:#aac8e8;margin:3px 0;">
            <b style="color:#6a8aaa;min-width:55px;display:inline-block;">Industry</b>{row['industry']}
          </div>
          <div style="font-size:10px;color:#aac8e8;margin:3px 0;">
            <b style="color:#6a8aaa;min-width:55px;display:inline-block;">Location</b>
            {(row.get('city','') + ', ' if row.get('city') else '') + row.get('state','')}
          </div>
          {"" if not row.get('phone') else f'<div style="font-size:10px;color:#aac8e8;margin:3px 0;"><b style="color:#6a8aaa;min-width:55px;display:inline-block;">Phone</b>{row["phone"]}</div>'}
          {"" if not desc_short else f'<div style="font-size:9px;color:#6a8aaa;margin-top:6px;line-height:1.5;">{desc_short}</div>'}
          <div style="margin-top:8px;">{web_html}</div>
        </div>
        """

        icon_html = f"""
        <div style="
            width:13px;height:13px;border-radius:50%;
            background:{color};
            border:2px solid rgba(255,255,255,0.4);
            box-shadow:0 0 8px {color}99,0 0 16px {color}44;
        "></div>
        """

        folium.Marker(
            location=[row["lat"], row["lng"]],
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=row["name"],
            icon=folium.DivIcon(html=icon_html, icon_size=(13, 13), icon_anchor=(6, 6)),
        ).add_to(fmap)

    return fmap


# ─────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────
def donut_chart(df: pd.DataFrame) -> go.Figure:
    counts = df["industry"].value_counts().reset_index()
    counts.columns = ["industry", "count"]
    colors = [ind_color(i) for i in counts["industry"]]

    fig = go.Figure(go.Pie(
        labels=counts["industry"],
        values=counts["count"],
        hole=0.62,
        marker=dict(colors=colors, line=dict(color="#020810", width=2)),
        textinfo="percent",
        textfont=dict(size=9, color="#e8f4ff"),
        hovertemplate="<b>%{label}</b><br>%{value} companies<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=4, b=4, l=4, r=4),
        showlegend=True,
        legend=dict(
            font=dict(color="#aac8e8", size=9),
            bgcolor="rgba(0,0,0,0)",
            orientation="v",
            x=1.02, y=0.5,
        ),
        height=165,
    )
    return fig


def bar_chart(df: pd.DataFrame) -> go.Figure:
    counts = df["state"].value_counts().head(7).reset_index()
    counts.columns = ["state", "count"]
    counts = counts.sort_values("count")

    bar_colors = ["#00d4ff" if i == len(counts) - 1 else "rgba(0,212,255,0.25)"
                  for i in range(len(counts))]

    fig = go.Figure(go.Bar(
        y=counts["state"],
        x=counts["count"],
        orientation="h",
        marker=dict(color=bar_colors, line=dict(width=0)),
        hovertemplate="<b>%{y}</b>: %{x} companies<extra></extra>",
        text=counts["count"],
        textposition="outside",
        textfont=dict(color="#aac8e8", size=8),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=4, b=4, l=4, r=40),
        height=185,
        xaxis=dict(
            showgrid=True, gridcolor="rgba(0,100,200,0.07)",
            tickfont=dict(color="#6a8aaa", size=8),
            zeroline=False,
        ),
        yaxis=dict(
            tickfont=dict(color="#aac8e8", size=9),
            showgrid=False,
        ),
        bargap=0.25,
    )
    return fig


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar(df: pd.DataFrame) -> tuple[str, str, str, bool]:
    with st.sidebar:
        st.markdown('<div class="sec-title">⚙ Dashboard Controls</div>', unsafe_allow_html=True)

        # Industry filter
        industries = ["All"] + sorted(df["industry"].unique().tolist())
        industry_filter = st.selectbox("Filter Industry", industries, key="industry_sel")

        # Basemap
        basemap = st.selectbox(
            "Base Map",
            ["Dark", "OSM", "Satellite", "Hybrid", "Train", "Terrain"],
            key="basemap_sel",
        )

        # Heatmap toggle
        show_heat = st.toggle("Show Heatmap", value=False, key="heat_tog")

        st.divider()

        # AI search
        st.markdown('<div class="sec-title">🔍 Search Companies</div>', unsafe_allow_html=True)
        search_q = st.text_input("", placeholder="Carian syarikat... e.g. drone mapping KL",
                                 label_visibility="collapsed", key="ai_search")

        # Quick query buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚁 Drone", use_container_width=True):
                st.session_state["ai_search"] = "drone"
                st.rerun()
            if st.button("🛰 Remote", use_container_width=True):
                st.session_state["ai_search"] = "remote sensing"
                st.rerun()
        with col2:
            if st.button("🗺 GIS", use_container_width=True):
                st.session_state["ai_search"] = "GIS"
                st.rerun()
            if st.button("📐 Survey", use_container_width=True):
                st.session_state["ai_search"] = "survey"
                st.rerun()

        st.divider()

        # Data source info
        st.markdown('<div class="sec-title">📡 Data Source</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:9px;color:rgba(120,160,200,0.5);word-break:break-all;">'
            f'{CSV_URL[:60]}…</div>',
            unsafe_allow_html=True,
        )
        if st.button("↻ Reload Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    return industry_filter, basemap, search_q, show_heat


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
def main():
    # Load data
    with st.spinner("Loading data from Google Sheets…"):
        df_all = get_data()

    # Sidebar controls
    industry_filter, basemap, search_q, show_heat = render_sidebar(df_all)

    # Apply industry filter
    df = df_all if industry_filter == "All" else df_all[df_all["industry"] == industry_filter]

    # ── Header ─────────────────────────────────
    st.markdown("""
    <div class="dash-header">
      <div class="dash-header-logo">🌐 GeoIntel MY</div>
      <div class="dash-header-title">
        <em>Geospatial</em> Industry Dashboard — Malaysia
      </div>
      <div style="font-size:10px;color:rgba(180,210,255,0.5);">
        <span class="live-dot"></span>LIVE
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Cards ──────────────────────────────
    top_state = df["state"].value_counts().idxmax() if not df.empty else "—"
    top_ind   = df["industry"].value_counts().idxmax() if not df.empty else "—"
    n_inds    = df_all["industry"].nunique()

    kpi_html = f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-icon">🏢</div>
        <div><div class="kpi-value">{len(df)}</div><div class="kpi-label">Total Companies</div></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon">📊</div>
        <div><div class="kpi-value">{n_inds}</div><div class="kpi-label">Industries</div></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon">📍</div>
        <div><div class="kpi-value" style="font-size:14px">{top_state}</div>
        <div class="kpi-label">Top State</div></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon">🚀</div>
        <div><div class="kpi-value" style="font-size:14px">{top_ind}</div>
        <div class="kpi-label">Top Industry</div></div>
      </div>
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)

    # ── Main 3-column layout ───────────────────
    left_col, map_col, right_col = st.columns([1, 2.4, 1.1], gap="small")

    # ────────────── LEFT PANEL ──────────────────
    with left_col:
        st.markdown('<div class="sec-title">Industry Distribution</div>', unsafe_allow_html=True)
        if not df.empty:
            st.plotly_chart(donut_chart(df), use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No data for selected filter.")

        st.markdown('<div class="sec-title">Companies by State</div>', unsafe_allow_html=True)
        if not df.empty:
            st.plotly_chart(bar_chart(df), use_container_width=True, config={"displayModeBar": False})

        # AI / keyword search results
        st.markdown('<div class="sec-title">🔍 Search Results</div>', unsafe_allow_html=True)
        if search_q and search_q.strip():
            words = [w.lower() for w in search_q.split() if len(w) > 1]
            mask = df_all.apply(
                lambda r: any(
                    w in " ".join([
                        str(r.get("name", "")), str(r.get("industry", "")),
                        str(r.get("city", "")),  str(r.get("state", "")),
                        str(r.get("desc", "")),
                    ]).lower()
                    for w in words
                ),
                axis=1,
            )
            results = df_all[mask].head(6)
            if results.empty:
                st.markdown(
                    '<div style="font-size:10px;color:rgba(120,160,200,0.5);padding:8px 0">No results. Try different keywords.</div>',
                    unsafe_allow_html=True,
                )
            else:
                for _, r in results.iterrows():
                    col = ind_color(r["industry"])
                    badge = f'<span style="background:{col}22;color:{col};border:1px solid {col}55;border-radius:8px;font-size:8px;padding:1px 6px;font-weight:700;text-transform:uppercase;">{r["industry"][:3]}</span>'
                    st.markdown(
                        f'<div class="ai-result">{badge}'
                        f'<div><div class="ai-result-name">{r["name"]}</div>'
                        f'<div class="ai-result-meta">{r.get("city","") } · {r.get("state","")}</div>'
                        f'</div></div>',
                        unsafe_allow_html=True,
                    )
        else:
            st.markdown(
                '<div style="font-size:9px;color:rgba(120,160,200,0.4);padding:4px 0">Taip nama syarikat, industri, atau lokasi untuk cari.</div>',
                unsafe_allow_html=True,
            )

    # ────────────── MAP PANEL ───────────────────
    with map_col:
        st.markdown('<div class="sec-title">Interactive Map</div>', unsafe_allow_html=True)
        fmap = build_map(df, basemap, show_heat)
        map_data = st_folium(
            fmap,
            use_container_width=True,
            height=520,
            returned_objects=["last_object_clicked_tooltip"],
            key=f"map_{industry_filter}_{basemap}_{show_heat}",
        )

        # Legend
        legend_items = "".join(
            f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:12px;'
            f'font-size:9px;color:rgba(180,210,255,0.6);">'
            f'<span style="width:9px;height:9px;border-radius:50%;background:{c};display:inline-block;'
            f'box-shadow:0 0 5px {c}88;"></span>{ind}</span>'
            for ind, c in INDUSTRY_COLORS.items()
        )
        st.markdown(
            f'<div style="margin-top:6px;padding:6px 8px;background:rgba(0,15,40,0.6);'
            f'border:1px solid rgba(0,150,200,0.12);border-radius:6px;">{legend_items}</div>',
            unsafe_allow_html=True,
        )

    # ────────────── RIGHT PANEL ─────────────────
    with right_col:
        st.markdown('<div class="sec-title">Company Explorer</div>', unsafe_allow_html=True)

        company_names = ["— Select Company —"] + df["name"].tolist()
        selected_name = st.selectbox("", company_names, label_visibility="collapsed", key="company_sel")

        # Auto-select if user clicked a marker on the map
        clicked = map_data.get("last_object_clicked_tooltip") if map_data else None
        if clicked and clicked in df["name"].values:
            selected_name = clicked

        if selected_name and selected_name != "— Select Company —":
            row = df[df["name"] == selected_name].iloc[0]
            st.markdown(profile_html(row), unsafe_allow_html=True)

        st.markdown('<div class="sec-title" style="margin-top:14px;">Top Companies</div>',
                    unsafe_allow_html=True)

        top_rows = df.head(10)
        rows_html = ""
        for i, (_, r) in enumerate(top_rows.iterrows(), 1):
            col = ind_color(r["industry"])
            badge = (
                f'<span style="background:{col}22;color:{col};border:1px solid {col}55;'
                f'border-radius:8px;font-size:7px;padding:1px 5px;font-weight:700;'
                f'text-transform:uppercase;">{r["industry"][:4]}</span>'
            )
            rows_html += (
                f'<tr>'
                f'<td style="color:rgba(120,160,200,0.4);font-family:monospace;font-size:8px">'
                f'{str(i).zfill(2)}</td>'
                f'<td style="font-size:9px;color:#e8f4ff;font-weight:500;max-width:90px;'
                f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{r["name"]}</td>'
                f'<td>{badge}</td>'
                f'<td style="font-size:8px;color:rgba(120,160,200,0.5);">{r.get("state","")}</td>'
                f'</tr>'
            )

        st.markdown(
            f'<table class="top-table"><thead><tr>'
            f'<th>#</th><th>Company</th><th>Industry</th><th>State</th>'
            f'</tr></thead><tbody>{rows_html}</tbody></table>',
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
