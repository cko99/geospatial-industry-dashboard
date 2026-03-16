Geospatial Industry Dashboard — Malaysia
Streamlit Version
🚀 Cara Install & Run
1. Install dependencies
```bash
pip install -r requirements.txt
```
2. Run the app
```bash
streamlit run app.py
```
Browser akan buka automatik di `http://localhost:8501`
---
☁️ Deploy ke Streamlit Cloud (free)
Push fail `app.py` dan `requirements.txt` ke GitHub repo
Pergi ke share.streamlit.io
Log in dengan GitHub → klik New app
Pilih repo dan branch → klik Deploy
---
📊 Format Spreadsheet Google Sheets
Pastikan sheet kamu ada kolum ini (nama kolum flexible, case-insensitive):
Kolum	Nama yang diterima
Nama syarikat	`company`, `name`
Industri	`industry`, `sector`, `category`
Negeri	`state`, `negeri`
Bandar	`city`, `bandar`, `town`
Latitud	`latitude`, `lat`  ← WAJIB
Longitud	`longitude`, `lng`, `long` ← WAJIB
Website	`website`, `web`, `url`
Telefon	`phone`, `tel`
Email	`email`
Penerangan	`description`, `desc`, `about`
Cara publish Google Sheet sebagai CSV:
Buka spreadsheet → File → Share → Publish to web
Pilih sheet tab yang betul
Format: Comma-separated values (.csv)
Klik Publish → copy URL
Paste URL ke dalam `CSV_URL` dalam `app.py`
---
🗺 Basemap tersedia
Dark — Carto Dark Matter (default)
OSM — OpenStreetMap standard
Satellite — ESRI World Imagery
Hybrid — Satellite + label overlay
Train — OpenRailwayMap overlay
Terrain — OpenTopoMap
🏭 Industri yang disupport
Industri	Warna
Drone	🔴 Merah
GIS	🟢 Hijau
Hydrography	🔵 Biru
Remote Sensing	🟠 Oren
Engineering Survey	🟣 Ungu
Land Survey	💙 Biru tua
