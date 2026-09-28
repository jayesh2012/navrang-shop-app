import streamlit as st
import pandas as pd
import datetime as dt
import sqlite3
import urllib.parse
from pathlib import Path
import hashlib
import io
import json
import zipfile
import importlib.util

# ============================================================
# NAVRANG VYAPAR — ADVANCED SHOP MANAGEMENT
# Existing database compatible + Product Master + Smart Calculator
# ============================================================

APP_NAME = "Navrang Masala"
APP_DIR = Path(__file__).resolve().parent
DB_FILE = str(APP_DIR / "navrang_masala.db")
LOGO_FILE = APP_DIR / "logo1.png"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🟠",
    layout="wide",
    initial_sidebar_state="auto",
)

# ----------------------------- Theme -----------------------------
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False
dark_mode = st.sidebar.toggle("🌙 Dark Mode", key="dark_mode", help="Switch between light and dark display modes")

# ----------------------------- CSS -----------------------------
st.markdown("""
<style>
:root { --nv-orange:#e85d04; --nv-orange2:#ff8c42; --nv-ink:#17202a; --nv-muted:#667085; --nv-card:rgba(255,255,255,.88); }
.stApp { background: linear-gradient(135deg,#fffaf5 0%,#f7f9fc 48%,#eef5ff 100%); }
[data-testid="stHeader"] { background: rgba(255,255,255,.72); backdrop-filter: blur(14px); }
.block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1500px; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#171b24 0%,#222936 55%,#161a21 100%); border-right:1px solid rgba(255,255,255,.08); }
[data-testid="stSidebar"] * { color:#f7f8fa; }
[data-testid="stSidebar"] .stRadio label { border-radius:13px; padding:10px 12px; margin:4px 2px; transition:.2s ease; font-size:17px !important; font-weight:800 !important; line-height:1.35 !important; min-height:46px; }
[data-testid="stSidebar"] .stRadio label p { font-size:17px !important; font-weight:800 !important; line-height:1.35 !important; margin:0 !important; }
[data-testid="stSidebar"] .stRadio label span { font-size:17px !important; }
[data-testid="stSidebar"] .stRadio [role="radiogroup"] { gap:3px; }
[data-testid="stSidebar"] .stRadio label:hover { background:rgba(255,255,255,.09); transform:translateX(3px); }
.nv-brand { display:flex; align-items:center; gap:12px; padding:14px 14px 16px; margin-bottom:12px; border-radius:18px; background:linear-gradient(135deg,rgba(255,140,66,.20),rgba(232,93,4,.06)); border:1px solid rgba(255,255,255,.09); box-shadow:0 10px 30px rgba(0,0,0,.15); }
.nv-logo { width:48px;height:48px;border-radius:15px;display:flex;align-items:center;justify-content:center;font-size:27px;background:linear-gradient(135deg,#ffb36b,#e85d04); box-shadow:0 8px 22px rgba(232,93,4,.35); }
.nv-brand-title { font-size:20px;font-weight:850;letter-spacing:.2px; }
.nv-brand-sub { font-size:11px;color:#c9ced8; margin-top:2px; }
.nv-top { display:flex;justify-content:space-between;align-items:flex-start;gap:16px;margin-bottom:14px; }
.nv-title { font-size:32px;font-weight:900;letter-spacing:-.7px;line-height:1.05;color:#17202a; }
.nv-subtitle { color:#667085;font-size:14px;margin-top:5px; }
.nv-pill { display:inline-flex;align-items:center;gap:7px;padding:8px 12px;border-radius:999px;background:rgba(255,255,255,.78);border:1px solid rgba(23,32,42,.08);box-shadow:0 6px 18px rgba(20,30,50,.06);font-size:12px;font-weight:700; }
.nv-hero { position:relative; overflow:hidden; padding:22px 24px; border-radius:24px; color:white; background:linear-gradient(135deg,#1c2430 0%,#303b4c 54%,#e85d04 180%); box-shadow:0 18px 45px rgba(24,32,45,.16); margin:6px 0 18px; }
.nv-hero:after { content:""; position:absolute; width:240px;height:240px;right:-70px;top:-100px;border-radius:50%;background:rgba(255,255,255,.08); }
.nv-hero h2 { margin:0;font-size:25px;position:relative;z-index:1; }
.nv-hero p { margin:7px 0 0;color:#dce2eb;position:relative;z-index:1; }
.nv-hero-stat { text-align:right;position:relative;z-index:1; }
.nv-hero-stat .big { font-size:29px;font-weight:900; }
.nv-hero-stat .small { font-size:11px;color:#d7dde7; }
.nv-kpi { background:rgba(255,255,255,.88); border:1px solid rgba(18,28,45,.07); border-radius:18px; padding:17px 17px 15px; box-shadow:0 10px 28px rgba(26,35,50,.07); position:relative; overflow:hidden; transition:.22s ease; }
.nv-kpi:hover { transform:translateY(-3px); box-shadow:0 15px 32px rgba(26,35,50,.11); }
.nv-kpi:before { content:""; position:absolute;left:0;top:0;width:5px;height:100%;background:linear-gradient(180deg,#ff9a5c,#e85d04); }
.nv-kpi-label { color:#667085;font-size:12px;font-weight:800;letter-spacing:.25px; }
.nv-kpi-value { color:#17202a;font-size:25px;font-weight:900;margin-top:6px; }
.nv-kpi-note { color:#98a2b3;font-size:11px;margin-top:4px; }
.nv-section { font-size:20px;font-weight:900;color:#17202a;margin:8px 0 12px; }
.nv-card { background:rgba(255,255,255,.86); border:1px solid rgba(18,28,45,.07); border-radius:20px; padding:18px; box-shadow:0 10px 28px rgba(26,35,50,.06); margin-bottom:14px; }
.nv-card h3 { margin:0 0 8px; font-size:16px; }
.nv-mini { color:#667085;font-size:12px; }
.nv-good { color:#087f5b;font-weight:850; }
.nv-bad { color:#c2410c;font-weight:850; }
.nv-product { background:rgba(255,255,255,.92);border:1px solid rgba(23,32,42,.08);border-radius:18px;padding:17px;margin-bottom:12px;box-shadow:0 8px 22px rgba(20,30,50,.06);transition:.2s; }
.nv-product:hover { transform:translateY(-2px);box-shadow:0 13px 28px rgba(20,30,50,.10); }
.nv-product-name { font-size:18px;font-weight:900;color:#17202a; }
.nv-price { font-size:23px;font-weight:900;color:#e85d04; }
.nv-detail { font-size:12px;color:#667085;margin-top:5px; }
.nv-badge { display:inline-block;padding:4px 8px;border-radius:999px;background:#fff3e8;color:#b54708;font-size:11px;font-weight:800; }
.nv-product:nth-of-type(4n+1){border-left:5px solid #e85d04;}
.nv-product:nth-of-type(4n+2){border-left:5px solid #6f42c1;}
.nv-product:nth-of-type(4n+3){border-left:5px solid #0f9d8a;}
.nv-product:nth-of-type(4n+4){border-left:5px solid #2563eb;}
.nv-price { text-shadow:0 2px 10px rgba(232,93,4,.12); }
.nv-badge { box-shadow:0 3px 10px rgba(181,71,8,.10); }
.stTabs [aria-selected="true"] { background:linear-gradient(135deg,#fff0e5,#ffffff) !important; box-shadow:0 5px 14px rgba(232,93,4,.10); }
button[kind="primary"] { background:linear-gradient(135deg,#ff8a3d,#e85d04) !important; border:0 !important; }

.nv-table-wrap { overflow-x:auto;border-radius:14px; }
.nv-footer { text-align:center;color:#98a2b3;font-size:11px;padding:25px 0 5px; }
div[data-testid="stMetric"] { background:rgba(255,255,255,.86); border:1px solid rgba(18,28,45,.07); border-radius:16px; padding:13px; box-shadow:0 8px 22px rgba(20,30,50,.05); }
[data-testid="stMetricValue"] { font-weight:900 !important; }
.stButton > button, .stDownloadButton > button, button[kind="primary"] { border-radius:11px !important; font-weight:800 !important; min-height:42px; transition:.18s ease !important; }
.stButton > button:hover, .stDownloadButton > button:hover { transform:translateY(-1px); box-shadow:0 7px 18px rgba(20,30,50,.10); }
.stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] { border-radius:11px !important; }
.stTabs [data-baseweb="tab-list"] { gap:7px; padding:5px; background:rgba(255,255,255,.65);border-radius:13px; }
.stTabs [data-baseweb="tab"] { border-radius:9px; font-weight:750; }
div[data-testid="stExpander"] { border-radius:15px !important; border:1px solid rgba(18,28,45,.08) !important; background:rgba(255,255,255,.66); }


/* Classy save / error feedback */
.nv-toast {
    display:flex; align-items:center; gap:10px; padding:13px 17px; margin:0 0 16px;
    border-radius:13px; font-weight:800; font-size:14px; animation:nvSlideIn .28s ease;
    box-shadow:0 8px 22px rgba(15,23,42,.10);
}
.nv-toast-icon { width:25px; height:25px; border-radius:50%; display:flex; align-items:center; justify-content:center;
    color:#fff; font-weight:900; flex:0 0 25px; }
.nv-toast-success { background:linear-gradient(135deg,#ecfdf3,#d1fae5); color:#087f5b; border:1px solid #86efac; }
.nv-toast-success .nv-toast-icon { background:#16a34a; }
.nv-toast-error { background:linear-gradient(135deg,#fff1f2,#ffe4e6); color:#b42318; border:1px solid #fda4af; }
.nv-toast-error .nv-toast-icon { background:#dc2626; }
@keyframes nvSlideIn { from {opacity:0; transform:translateY(-7px)} to {opacity:1; transform:translateY(0)} }
[data-theme="dark"] .nv-toast-success { background:linear-gradient(135deg,#052e1b,#064e3b); color:#bbf7d0; border-color:#166534; }
[data-theme="dark"] .nv-toast-error { background:linear-gradient(135deg,#3b0a0a,#450a0a); color:#fecaca; border-color:#991b1b; }

/* Streamlit Dark Mode compatibility */
[data-theme="dark"] .stApp, body[data-theme="dark"] .stApp { background:linear-gradient(135deg,#0b1220 0%,#111827 52%,#0f172a 100%) !important; }
[data-theme="dark"] .nv-title, [data-theme="dark"] .nv-section, [data-theme="dark"] .nv-product-name, [data-theme="dark"] .nv-card h3 { color:#f8fafc !important; }
[data-theme="dark"] .nv-subtitle, [data-theme="dark"] .nv-mini, [data-theme="dark"] .nv-detail, [data-theme="dark"] .nv-kpi-label, [data-theme="dark"] .nv-kpi-note { color:#cbd5e1 !important; }
[data-theme="dark"] .nv-card, [data-theme="dark"] .nv-kpi, [data-theme="dark"] .nv-pill, [data-theme="dark"] .stTabs [data-baseweb="tab-list"] { background:rgba(17,24,39,.92) !important; border-color:#334155 !important; color:#f8fafc !important; }
[data-theme="dark"] .stTabs [aria-selected="true"] { background:linear-gradient(135deg,#3a2112,#1f2937) !important; color:#fff !important; }
[data-theme="dark"] .stTextInput input, [data-theme="dark"] .stNumberInput input, [data-theme="dark"] .stDateInput input, [data-theme="dark"] .stSelectbox div[data-baseweb="select"] { background:#111827 !important; color:#f8fafc !important; border-color:#475569 !important; }
[data-theme="dark"] .stTextInput label, [data-theme="dark"] .stNumberInput label, [data-theme="dark"] .stDateInput label, [data-theme="dark"] .stSelectbox label { color:#e5e7eb !important; }
[data-theme="dark"] div[data-testid="stDataFrame"] { border:1px solid #334155 !important; border-radius:14px; overflow:hidden; }
/* Strong Light/Dark theme readability */
[data-theme="dark"] .stMarkdown, [data-theme="dark"] .stText, [data-theme="dark"] label,
[data-theme="dark"] [data-testid="stCaptionContainer"], [data-theme="dark"] [data-testid="stText"],
[data-theme="dark"] .stRadio label, [data-theme="dark"] .stCheckbox label { color:#f1f5f9 !important; }
[data-theme="dark"] .stButton > button, [data-theme="dark"] .stDownloadButton > button { color:#f8fafc !important; background:#1e293b !important; border:1px solid #475569 !important; }
[data-theme="dark"] .stButton > button:hover, [data-theme="dark"] .stDownloadButton > button:hover { background:#334155 !important; border-color:#fb923c !important; box-shadow:0 8px 20px rgba(0,0,0,.35) !important; }
[data-theme="dark"] [data-testid="stDataFrame"] *, [data-theme="dark"] .stDataFrame { color:#f8fafc !important; }
[data-theme="dark"] .stSelectbox [data-baseweb="select"] *, [data-theme="dark"] .stMultiSelect [data-baseweb="select"] * { color:#f8fafc !important; }
[data-theme="dark"] [data-baseweb="popover"] { background:#111827 !important; border-color:#475569 !important; }
[data-theme="dark"] [role="option"] { color:#f8fafc !important; }
[data-theme="dark"] .stAlert { color:#f8fafc !important; }
[data-theme="dark"] div[data-testid="stMetric"] { background:#111827 !important; border-color:#334155 !important; }
[data-theme="dark"] [data-testid="stMetricLabel"], [data-theme="dark"] [data-testid="stMetricValue"], [data-theme="dark"] [data-testid="stMetricDelta"] { color:#f8fafc !important; }
[data-theme="dark"] .nv-product, [data-theme="dark"] .nv-card, [data-theme="dark"] .nv-kpi { box-shadow:0 12px 30px rgba(0,0,0,.25) !important; }
@media (max-width: 800px) {
 [data-testid="stSidebar"] .stRadio label, [data-testid="stSidebar"] .stRadio label p, [data-testid="stSidebar"] .stRadio label span { font-size:16px !important; }
 .block-container { padding: .55rem .65rem 1.5rem; }
 .nv-title { font-size:25px; }
 .nv-hero { padding:18px; border-radius:19px; }
 .nv-hero-stat { text-align:left; margin-top:10px; }
 .nv-kpi-value { font-size:21px; }
 .nv-card { padding:14px; border-radius:16px; }
 [data-testid="stSidebar"] { width: min(86vw, 320px) !important; min-width: 0 !important; max-width: 320px !important; }
}

/* ============================================================
   NAVRANG VYAPAR — MOBILE FIRST / THEME SAFE DESIGN
   ============================================================ */
[data-testid="stAppViewContainer"] { min-width: 0 !important; }
[data-testid="stMainBlockContainer"] { min-width: 0 !important; }
.stDataFrame, [data-testid="stDataFrame"] { max-width: 100% !important; }
.stTabs [data-baseweb="tab-list"] { overflow-x: auto !important; scrollbar-width: thin; flex-wrap: nowrap !important; }
.stTabs [data-baseweb="tab"] { flex: 0 0 auto !important; white-space: nowrap !important; }
.nv-tool-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin:6px 0 18px; }
.nv-tool-card { min-height:92px; padding:15px; border-radius:18px; background:linear-gradient(135deg,rgba(255,255,255,.96),rgba(248,250,252,.88)); border:1px solid #e5e7eb; box-shadow:0 8px 22px rgba(15,23,42,.06); }
.nv-tool-card .icon { font-size:25px; line-height:1; margin-bottom:8px; }
.nv-tool-card .name { font-weight:900; font-size:14px; color:#17202a; }
.nv-tool-card .desc { font-size:11px; color:#667085; margin-top:4px; line-height:1.35; }
.nv-mobile-note { display:none; }
[data-theme="dark"] .stApp,
[data-theme="dark"] [data-testid="stAppViewContainer"],
[data-theme="dark"] [data-testid="stMain"] { background:#0b1220 !important; color:#f8fafc !important; }
[data-theme="dark"] .nv-tool-card { background:linear-gradient(135deg,#111827,#172033) !important; border-color:#334155 !important; }
[data-theme="dark"] .nv-tool-card .name { color:#f8fafc !important; }
[data-theme="dark"] .nv-tool-card .desc { color:#cbd5e1 !important; }
[data-theme="dark"] .nv-pill { background:#111827 !important; border-color:#334155 !important; color:#f8fafc !important; }
[data-theme="dark"] .nv-product { background:#111827 !important; border-color:#334155 !important; }
[data-theme="dark"] div[data-testid="stMetric"] { background:#111827 !important; border-color:#334155 !important; }
[data-theme="dark"] div[data-testid="stMetric"] * { color:#f8fafc !important; }
[data-theme="dark"] [data-testid="stDataFrame"] { background:#111827 !important; }
[data-theme="dark"] .stAlert { border-color:#475569 !important; }
[data-theme="dark"] [data-baseweb="select"] > div,
[data-theme="dark"] [data-baseweb="input"] > div,
[data-theme="dark"] textarea,
[data-theme="dark"] input { background:#111827 !important; color:#f8fafc !important; border-color:#475569 !important; }
[data-theme="dark"] [data-baseweb="popover"] { background:#111827 !important; color:#f8fafc !important; }
[data-theme="dark"] [role="option"] { color:#f8fafc !important; background:#111827 !important; }
[data-theme="dark"] [role="option"]:hover { background:#1f2937 !important; }
[data-theme="dark"] .stTabs [data-baseweb="tab-list"] { background:#0f172a !important; border:1px solid #334155 !important; }
[data-theme="dark"] .stTabs [data-baseweb="tab"] { color:#cbd5e1 !important; }
[data-theme="dark"] .stTabs [aria-selected="true"] { color:#fff !important; background:#3a2112 !important; }
@media (max-width: 768px) {
  .block-container { padding: .55rem .65rem 1.25rem !important; max-width: 100% !important; }
  .nv-top { gap:8px; margin-bottom:10px; }
  .nv-title { font-size:24px; letter-spacing:-.35px; }
  .nv-subtitle { font-size:11px; }
  .nv-pill { font-size:10px; padding:6px 9px; }
  .nv-hero { padding:17px 16px; border-radius:18px; margin-top:2px; }
  .nv-hero h2 { font-size:20px; line-height:1.15; }
  .nv-hero p { font-size:12px; }
  .nv-kpi { padding:12px; border-radius:15px; }
  .nv-kpi-value { font-size:20px; }
  .nv-kpi-label { font-size:11px; }
  .nv-card { padding:13px; border-radius:16px; margin-bottom:10px; }
  .nv-section { font-size:18px; margin:5px 0 9px; }
  .nv-product-name { font-size:16px; }
  .nv-price { font-size:20px; }
  .stButton > button, .stDownloadButton > button { min-height:46px !important; font-size:14px !important; }
  .stTextInput input, .stNumberInput input, .stDateInput input { min-height:43px !important; font-size:15px !important; }
  [data-baseweb="select"] > div { min-height:43px !important; }
  .stTabs [data-baseweb="tab"] { min-height:42px !important; padding:8px 11px !important; font-size:13px !important; }
  .nv-tool-grid { grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; margin-bottom:12px; }
  .nv-tool-card { min-height:82px; padding:12px; border-radius:15px; }
  .nv-tool-card .icon { font-size:21px; margin-bottom:6px; }
  .nv-tool-card .name { font-size:12px; }
  .nv-tool-card .desc { font-size:10px; }
  .nv-mobile-note { display:block; font-size:11px; color:#667085; margin:-4px 0 10px; }
  .nv-table-wrap { width:100%; overflow-x:auto; -webkit-overflow-scrolling:touch; }
  [data-testid="stDataFrame"] { max-width:100vw !important; }
  [data-testid="stSidebar"] .stRadio label { font-size:16px !important; min-height:44px; padding:9px 10px; }
  [data-testid="stSidebar"] .stRadio label p { font-size:16px !important; }
}
@media (max-width: 420px) {
  .nv-title { font-size:21px; }
  .nv-subtitle { font-size:10px; }
  .nv-pill { display:none; }
  .nv-kpi-value { font-size:18px; }
  .nv-kpi-note { font-size:10px; }
  .nv-tool-grid { grid-template-columns:1fr 1fr; }
}


@media (max-width: 768px) {
  html, body { overflow-x:hidden !important; }
  .block-container { padding:.5rem .55rem 1rem !important; width:100% !important; max-width:100% !important; }
  [data-testid="stSidebar"] { width:min(86vw,320px) !important; max-width:320px !important; }
  [data-testid="stSidebar"] .stRadio label { min-height:46px !important; padding:10px 11px !important; }
  .stButton > button, .stDownloadButton > button { min-height:46px !important; width:100% !important; }
  .stTextInput input, .stNumberInput input, .stDateInput input, textarea { font-size:16px !important; }
  [data-baseweb="select"] > div { min-height:44px !important; }
  .stDataFrame, [data-testid="stDataFrame"] { width:100% !important; overflow-x:auto !important; }
  .nv-top { flex-wrap:wrap !important; }
  .nv-pill { margin-top:2px; }
}
@media (max-width: 480px) {
  .nv-title { font-size:21px !important; }
  .nv-subtitle { font-size:10px !important; }
  .nv-pill { display:none !important; }
  .nv-hero { padding:15px !important; }
  .nv-kpi-value { font-size:18px !important; }
  .nv-tool-grid { grid-template-columns:1fr 1fr !important; gap:7px !important; }
}
</style>
""", unsafe_allow_html=True)

if dark_mode:
    st.markdown("""
    <style>
      .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background:#0b1220 !important; color:#f8fafc !important; }
      [data-testid="stHeader"] { background:#0b1220 !important; }
      .block-container { color:#f8fafc !important; }
      .nv-title, .nv-section { color:#f8fafc !important; }
      .nv-subtitle, .nv-kpi-label, .nv-kpi-note { color:#cbd5e1 !important; }
      .nv-card, .nv-kpi { background:#111827 !important; border-color:#334155 !important; color:#f8fafc !important; }
      .nv-kpi-value, .nv-product-name, .nv-price, .nv-detail { color:#f8fafc !important; }
      .nv-pill { background:#111827 !important; border-color:#334155 !important; color:#f8fafc !important; }
      .nv-tool-card { background:#111827 !important; border-color:#334155 !important; }
      .nv-tool-card .name { color:#f8fafc !important; }
      .nv-tool-card .desc { color:#cbd5e1 !important; }
      [data-baseweb="input"] > div, [data-baseweb="select"] > div, textarea, input { background:#111827 !important; color:#f8fafc !important; border-color:#475569 !important; }
      [data-baseweb="select"] * { color:#f8fafc !important; }
      [data-baseweb="popover"], [role="listbox"], [role="option"] { background:#111827 !important; color:#f8fafc !important; }
      [role="option"]:hover { background:#1f2937 !important; }
      [data-testid="stDataFrame"] { border:1px solid #334155 !important; border-radius:12px; }
      .stTabs [data-baseweb="tab-list"] { background:#0f172a !important; border-color:#334155 !important; }
      .stTabs [data-baseweb="tab"] { color:#cbd5e1 !important; }
      .stTabs [aria-selected="true"] { color:#fff !important; background:#3a2112 !important; }
    </style>
    """, unsafe_allow_html=True)

# ----------------------------- DB helpers -----------------------------
def conn_db():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = conn_db(); cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, suraj_dana_chana REAL, durga_trading_company REAL,
        bharat_general REAL, jain_traders REAL, kk_traders REAL, jalaram_papad REAL, gulab_panipuri REAL,
        rais_ponga_wala REAL, delux_suppliers REAL, suhana_spices REAL, ram_bandhu_spices REAL,
        others REAL, total_purchase REAL)''')
    # Migrate existing purchase databases without losing old entries.
    cur.execute("PRAGMA table_info(purchases)")
    purchase_columns = {row[1] for row in cur.fetchall()}
    for col in ["raman_papad", "noodles_wala", "sairaj_traders"]:
        if col not in purchase_columns:
            cur.execute(f"ALTER TABLE purchases ADD COLUMN {col} REAL DEFAULT 0")

    cur.execute('''CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, shop_sale REAL, cart_sale REAL,
        online_collection REAL, total_sale REAL)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, electricity_bill REAL, shop_rent REAL,
        cart_rent REAL, other_expense REAL, other_expense_desc TEXT, total_expense REAL)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS supplier_udhaar (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, supplier_name TEXT, amount REAL, status TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS customer_udhaar (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, customer_name TEXT, phone_number TEXT,
        amount REAL, status TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS customer_directory (
        id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, phone_number TEXT UNIQUE,
        customer_type TEXT, address TEXT, notes TEXT)''')
    cur.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT, product_name TEXT NOT NULL UNIQUE, category TEXT DEFAULT '',
        purchase_price_kg REAL NOT NULL DEFAULT 0, sale_price_kg REAL NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, product_name TEXT, category TEXT,
        old_purchase_price REAL, old_sale_price REAL, new_purchase_price REAL, new_sale_price REAL,
        changed_at TEXT NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS app_security (
        id INTEGER PRIMARY KEY CHECK(id=1), pin_hash TEXT, updated_at TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, table_name TEXT, record_id INTEGER, details TEXT, changed_at TEXT NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS deleted_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT, table_name TEXT NOT NULL, record_id INTEGER, record_json TEXT NOT NULL, deleted_at TEXT NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS business_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, note_date TEXT NOT NULL, title TEXT, note TEXT NOT NULL, created_at TEXT NOT NULL)""")
    for table in ["purchases","sales","expenses","customer_udhaar","supplier_udhaar"]:
        existing=[r[1] for r in cur.execute(f"PRAGMA table_info({table})").fetchall()]
        if table in ("purchases","sales","expenses") and "notes" not in existing:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN notes TEXT DEFAULT ''")
        if table in ("customer_udhaar","supplier_udhaar") and "paid_amount" not in existing:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN paid_amount REAL DEFAULT 0")
        if table in ("customer_udhaar","supplier_udhaar") and "payment_date" not in existing:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN payment_date TEXT")
    # Remove legacy stock fields/system while preserving product data.
    cols = [r[1] for r in cur.execute("PRAGMA table_info(products)").fetchall()]
    if "stock_kg" in cols or "low_stock_kg" in cols:
        cur.execute("ALTER TABLE products RENAME TO products_legacy")
        cur.execute("""CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT, product_name TEXT NOT NULL UNIQUE, category TEXT DEFAULT '',
            purchase_price_kg REAL NOT NULL DEFAULT 0, sale_price_kg REAL NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL)""")
        cur.execute("INSERT INTO products(id,product_name,category,purchase_price_kg,sale_price_kg,created_at) SELECT id,product_name,category,purchase_price_kg,sale_price_kg,created_at FROM products_legacy")
        cur.execute("DROP TABLE products_legacy")
    cur.execute("DROP TABLE IF EXISTS stock_transactions")
    conn.commit(); conn.close()

init_db()

def qdf(sql, params=()):
    conn = conn_db(); df = pd.read_sql_query(sql, conn, params=params); conn.close(); return df

@st.cache_data(ttl=20, show_spinner=False)
def _load_all_cached():
    return (
        qdf("SELECT * FROM purchases ORDER BY date DESC, id DESC"),
        qdf("SELECT * FROM sales ORDER BY date DESC, id DESC"),
        qdf("SELECT * FROM expenses ORDER BY date DESC, id DESC"),
        qdf("SELECT * FROM supplier_udhaar ORDER BY date DESC, id DESC"),
        qdf("SELECT * FROM customer_udhaar ORDER BY date DESC, id DESC"),
        qdf("SELECT * FROM customer_directory ORDER BY customer_name"),
        qdf("SELECT * FROM products ORDER BY product_name"),
    )

def execute(sql, params=()):
    conn = conn_db(); cur = conn.cursor(); cur.execute(sql, params); last = cur.lastrowid
    try:
        first=(sql.strip().split()[0].upper() if sql.strip() else "SQL")
        table=""
        toks=sql.replace("("," ").replace(")"," ").replace(","," ").split()
        for i,t in enumerate(toks):
            if t.upper() in ("INTO","UPDATE","FROM","TABLE") and i+1<len(toks): table=toks[i+1].strip('`[]')
        if first in ("INSERT","UPDATE","DELETE") and table:
            cur.execute("INSERT INTO activity_log(action,table_name,record_id,details,changed_at) VALUES(?,?,?,?,?)",(first,table,last if last else None,sql[:180],dt.datetime.now().isoformat(timespec="seconds")))
    except Exception:
        pass
    conn.commit(); conn.close()
    try: _load_all_cached.clear()
    except Exception: pass
    return last

def archive_record(table_name, record_id):
    conn=conn_db(); cur=conn.cursor(); row=cur.execute(f"SELECT * FROM {table_name} WHERE id=?",(int(record_id),)).fetchone()
    if row is not None:
        cols=[d[0] for d in cur.description]
        cur.execute("INSERT INTO deleted_records(table_name,record_id,record_json,deleted_at) VALUES(?,?,?,?)",(table_name,int(record_id),json.dumps(dict(zip(cols,row)),default=str),dt.datetime.now().isoformat(timespec="seconds")))
        conn.commit()
    conn.close()
    try: _load_all_cached.clear()
    except Exception: pass

def money(v):
    try: return f"₹{float(v):,.2f}"
    except: return "₹0.00"


def hash_pin(pin):
    return hashlib.sha256(pin.encode("utf-8")).hexdigest()

def pin_is_set():
    x=qdf("SELECT pin_hash FROM app_security WHERE id=1")
    return not x.empty and bool(x.iloc[0].pin_hash)

def verify_pin(pin):
    x=qdf("SELECT pin_hash FROM app_security WHERE id=1")
    return not x.empty and bool(x.iloc[0].pin_hash) and x.iloc[0].pin_hash == hash_pin(pin)

def pdf_report(title, subtitle, df, summary_lines):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    out=io.BytesIO()
    doc=SimpleDocTemplate(out,pagesize=A4,rightMargin=12*mm,leftMargin=12*mm,topMargin=12*mm,bottomMargin=12*mm)
    styles=getSampleStyleSheet(); story=[Paragraph(title,styles["Title"]),Paragraph(subtitle,styles["Normal"]),Spacer(1,8)]
    for line in summary_lines: story.append(Paragraph(line,styles["Normal"]))
    story.append(Spacer(1,8))
    if df is not None and not df.empty:
        data=[list(df.columns)]+[[str(v) for v in row] for row in df.itertuples(index=False,name=None)]
        t=Table(data,repeatRows=1)
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e85d04")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.35,colors.grey),("FONTSIZE",(0,0),(-1,-1),7),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
        story.append(t)
    else: story.append(Paragraph("No records found for the selected period.",styles["Normal"]))
    doc.build(story); return out.getvalue()



def set_flash(message, kind="success"):
    st.session_state["nv_flash"] = {"message": message, "kind": kind}


def render_flash():
    flash = st.session_state.pop("nv_flash", None)
    if not flash:
        return
    cls = "nv-toast-success" if flash.get("kind") == "success" else "nv-toast-error"
    icon = "✓" if flash.get("kind") == "success" else "!"
    # Show a real Streamlit toast popup and a visible in-page success banner.
    try:
        st.toast(str(flash.get("message", "Done")), icon="✅" if flash.get("kind") == "success" else "❌")
    except Exception:
        pass
    st.markdown(
        f'<div class="nv-toast {cls}"><span class="nv-toast-icon">{icon}</span><span>{flash["message"]}</span></div>',
        unsafe_allow_html=True,
    )

def load_all():
    return _load_all_cached()

def dated(df):
    if df.empty or "date" not in df.columns: return df
    x=df.copy(); x["dt"]=pd.to_datetime(x["date"], errors="coerce"); return x

df_p, df_s, df_e, df_u, df_cu, df_cd, df_products = load_all()
for _n in ["df_p","df_s","df_e","df_u","df_cu"]:
    globals()[_n]=dated(globals()[_n])

# ----------------------------- Sidebar -----------------------------
# Quick-action navigation is handled through a pending value so Streamlit
# never tries to modify the `main_nav` widget after it has been instantiated.
if "pending_nav" in st.session_state:
    st.session_state["main_nav"] = st.session_state.pop("pending_nav")

st.sidebar.markdown("### NAVRANG MASALA")
st.sidebar.caption("Smart Shop Management")

menu = st.sidebar.radio("Navigation", [
    "🏠 Home", "🛒 Products", "➕ Data Entry",
    "📒 Supplier Khata", "👥 Customer Khata", "📇 Customers & WA", "📊 Reports", "🗓️ Festival Planning", "🧰 Tools", "🔐 Security", "📂 Backup"
], label_visibility="collapsed", key="main_nav")

st.sidebar.markdown("---")
st.sidebar.markdown("**⚡ Quick tools**")
st.sidebar.caption("• Product price calculator\n• Category-wise price list\n• Customer WhatsApp\n• Khata tracking\n• CSV + DB backup")
st.sidebar.markdown("---")
st.sidebar.caption(f"Database: `{DB_FILE}`")

# ----------------------------- Header -----------------------------
now = dt.datetime.now()
st.markdown(f"""
<div class="nv-top"><div><div class="nv-title">Navrang Masala</div><div class="nv-subtitle">Professional business control panel • {now.strftime('%d %b %Y')}</div></div><div class="nv-pill">🟢 Business dashboard</div></div>
""", unsafe_allow_html=True)

# ----------------------------- Flash feedback -----------------------------
render_flash()

# ----------------------------- Data Entry -----------------------------
def render_entry_filter(title, df, date_col="date", amount_col="Amount", key_prefix="entry"):
    """Safe mobile-friendly date filter used by purchase/sales history tables."""
    if df is None or df.empty:
        st.info(f"No {title.lower()} records available.")
        return pd.DataFrame(columns=list(df.columns) if df is not None else [])

    work = df.copy()
    # Accept either lower-case database column names or display columns such as Date.
    if date_col not in work.columns:
        for candidate in ("date", "Date", "dt", "_date"):
            if candidate in work.columns:
                date_col = candidate
                break
        else:
            st.warning(f"{title}: no date column was found, so date filtering is unavailable.")
            return work

    work["_date"] = pd.to_datetime(work[date_col], errors="coerce")
    work = work.dropna(subset=["_date"]).copy()

    f1, f2 = st.columns([1.15, 1.85])
    with f1:
        mode = st.selectbox(
            "View",
            ["All Time", "1 Day", "1 Month", "1 Year", "Specific Range"],
            key=f"{key_prefix}_mode",
        )

    today = dt.datetime.now().date()
    if mode == "1 Day":
        selected = st.date_input("Date", today, key=f"{key_prefix}_day")
        work = work[work["_date"].dt.date == selected]
    elif mode == "1 Month":
        with f2:
            c1, c2 = st.columns(2)
            with c1:
                year = st.number_input("Year", min_value=2000, max_value=2100, value=today.year, step=1, key=f"{key_prefix}_year")
            with c2:
                month = st.selectbox(
                    "Month", list(range(1, 13)), index=today.month - 1,
                    format_func=lambda x: dt.date(2000, x, 1).strftime("%B"),
                    key=f"{key_prefix}_month",
                )
        work = work[(work["_date"].dt.year == int(year)) & (work["_date"].dt.month == int(month))]
    elif mode == "1 Year":
        with f2:
            year = st.number_input("Year", min_value=2000, max_value=2100, value=today.year, step=1, key=f"{key_prefix}_only_year")
        work = work[work["_date"].dt.year == int(year)]
    elif mode == "Specific Range":
        with f2:
            c1, c2 = st.columns(2)
            with c1:
                from_d = st.date_input("From", today.replace(day=1), key=f"{key_prefix}_from")
            with c2:
                to_d = st.date_input("To", today, key=f"{key_prefix}_to")
        if from_d > to_d:
            st.error("From date cannot be after To date.")
            return work.iloc[0:0].copy()
        work = work[(work["_date"].dt.date >= from_d) & (work["_date"].dt.date <= to_d)]

    return work.drop(columns=["_date"], errors="ignore")

def purchase_history_table(pp, suppliers, cols_map, key_prefix="purchase_history"):
    if pp.empty:
        st.info("No purchase entries yet.")
        return
    rows=[]
    for _,r in pp.iterrows():
        for supplier in suppliers:
            col=cols_map[supplier]
            try: amount=float(r.get(col,0) or 0)
            except Exception: amount=0
            if amount>0:
                rows.append({"Date":str(r["date"]),"Supplier":supplier,"Purchase Amount":amount,"Entry ID":int(r["id"])})
    long=pd.DataFrame(rows,columns=["Date","Supplier","Purchase Amount","Entry ID"])
    if long.empty:
        st.info("No supplier-wise purchase amounts found.")
        return
    view=render_entry_filter("Purchase",long,date_col="Date",amount_col="Purchase Amount",key_prefix=key_prefix)
    suppliers_selected=st.multiselect("Supplier Filter",["All"]+suppliers,default=["All"],key=f"{key_prefix}_supplier")
    if "All" not in suppliers_selected:
        view=view[view["Supplier"].isin(suppliers_selected)]
    c1,c2,c3=st.columns(3)
    total=float(view["Purchase Amount"].sum()) if not view.empty else 0
    c1.metric("Filtered Purchase",money(total)); c2.metric("Entries",len(view)); c3.metric("Suppliers",view["Supplier"].nunique() if not view.empty else 0)
    st.dataframe(view.sort_values(["Date","Entry ID"],ascending=[False,False]).drop(columns=["Entry ID"],errors="ignore"),use_container_width=True,hide_index=True)

def sales_history_table(ss,key_prefix="sales_history"):
    if ss.empty:
        st.info("No sales entries yet.")
        return
    rows=[]
    channel_map={"Shop Sale":"shop_sale","Cart Sale":"cart_sale","Online Collection":"online_collection"}
    for _,r in ss.iterrows():
        for channel,col in channel_map.items():
            try: amount=float(r.get(col,0) or 0)
            except Exception: amount=0
            if amount>0:
                rows.append({"Date":str(r["date"]),"Sale Channel":channel,"Sale Amount":amount,"Entry ID":int(r["id"])})
    long=pd.DataFrame(rows,columns=["Date","Sale Channel","Sale Amount","Entry ID"])
    if long.empty:
        st.info("No channel-wise sales amounts found.")
        return
    view=render_entry_filter("Sales",long,date_col="Date",amount_col="Sale Amount",key_prefix=key_prefix)
    channels=st.multiselect("Sale Channel Filter",["All","Shop Sale","Cart Sale","Online Collection"],default=["All"],key=f"{key_prefix}_channel")
    if "All" not in channels:
        view=view[view["Sale Channel"].isin(channels)]
    c1,c2,c3=st.columns(3)
    total=float(view["Sale Amount"].sum()) if not view.empty else 0
    c1.metric("Filtered Sales",money(total)); c2.metric("Entries",len(view)); c3.metric("Channels",view["Sale Channel"].nunique() if not view.empty else 0)
    st.dataframe(view.sort_values(["Date","Entry ID"],ascending=[False,False]).drop(columns=["Entry ID"],errors="ignore"),use_container_width=True,hide_index=True)


# ----------------------------- Home -----------------------------
if menu == "🏠 Home":
    # Brand logo: shown on Home only; intentionally not placed in navigation.
    if LOGO_FILE.exists():
        logo_col, title_col = st.columns([0.18, 0.82], vertical_alignment="center")
        with logo_col:
            st.image(str(LOGO_FILE), width=82)
        with title_col:
            st.markdown(
                '<div style="font-size:30px;font-weight:900;line-height:1.05;">NAVRANG MASALA</div>'
                '<div style="font-size:13px;opacity:.72;margin-top:4px;">Smart Shop Management</div>',
                unsafe_allow_html=True
            )
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    sales_total = float(df_s.total_sale.sum()) if not df_s.empty else 0
    purchase_total = float(df_p.total_purchase.sum()) if not df_p.empty else 0
    expense_total = float(df_e.total_expense.sum()) if not df_e.empty else 0
    cust_due = float(df_cu.loc[df_cu.status.eq("Pending"),"amount"].sum()) if not df_cu.empty else 0
    supp_due = float(df_u.loc[df_u.status.eq("Pending"),"amount"].sum()) if not df_u.empty else 0
    net = sales_total - purchase_total - expense_total
    product_count = len(df_products)
    customer_count = len(df_cd)

    st.markdown(f"""
    <div class="nv-hero"><div style="position:relative;z-index:1"><div style="font-size:11px;color:#ffcfad;font-weight:800;letter-spacing:1px">TODAY'S CONTROL CENTER</div><h2>Welcome to Navrang Masala</h2><p>Purchases, expenses, khata and products — all in one place.</p></div></div>
    """, unsafe_allow_html=True)

    # Dashboard date filter
    f1,f2,f3 = st.columns([1,1,1])
    with f1: dash_from = st.date_input("From", now.date().replace(day=1), key="dash_from")
    with f2: dash_to = st.date_input("To", now.date(), key="dash_to")
    with f3:
        st.write("")
        st.write("")
        st.caption("📌 Home numbers can be filtered by date.")

    def period(df):
        if df.empty or "dt" not in df.columns: return df
        return df[(df.dt.dt.date >= dash_from) & (df.dt.dt.date <= dash_to)]
    ps, pp, pe = period(df_s), period(df_p), period(df_e)
    sales_p=float(ps.total_sale.sum()) if not ps.empty else 0
    purchase_p=float(pp.total_purchase.sum()) if not pp.empty else 0
    expense_p=float(pe.total_expense.sum()) if not pe.empty else 0
    profit_p=sales_p-purchase_p-expense_p

    kpis=[
        ("💰 Sales",money(sales_p),"Selected period"),
        ("🛒 Purchases",money(purchase_p),"Selected period"),
        ("🧾 Expenses",money(expense_p),"Operating cost"),
        ("💎 Net Result",money(profit_p),"Sales − purchase − expense"),
        ("👥 Customer Due",money(cust_due),"Pending khata"),
        ("📒 Supplier Due",money(supp_due),"Pending payable"),
    ]
    cols=st.columns(3)
    for i,(lab,val,note) in enumerate(kpis):
        with cols[i%3]: st.markdown(f'<div class="nv-kpi"><div class="nv-kpi-label">{lab}</div><div class="nv-kpi-value">{val}</div><div class="nv-kpi-note">{note}</div></div>',unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>",unsafe_allow_html=True)
    a,b=st.columns([1.55,1])
    with a:
        st.markdown('<div class="nv-card"><h3>📈 Sales vs Purchases Trend</h3><div class="nv-mini">Daily movement for selected period</div></div>',unsafe_allow_html=True)
        frames=[]
        if not ps.empty: frames.append(ps.groupby(ps.dt.dt.date).total_sale.sum().rename("Sales"))
        if not pp.empty: frames.append(pp.groupby(pp.dt.dt.date).total_purchase.sum().rename("Purchases"))
        if frames:
            chart=pd.concat(frames,axis=1).fillna(0).sort_index(); st.line_chart(chart, use_container_width=True)
        else: st.info("Add sales or purchases to see the trend.")
    with b:
        st.markdown('<div class="nv-card"><h3>💼 Business Mix</h3><div class="nv-mini">Selected period</div></div>',unsafe_allow_html=True)
        mix=pd.DataFrame({"Amount":[sales_p,purchase_p,expense_p]},index=["Sales","Purchases","Expenses"])
        st.bar_chart(mix, use_container_width=True)

    c,d=st.columns(2)
    with c:
        st.markdown('<div class="nv-card"><h3>📌 Money Position</h3></div>',unsafe_allow_html=True)
        st.metric("Customer receivable",money(cust_due)); st.metric("Supplier payable",money(supp_due)); st.metric("Net difference",money(cust_due-supp_due))
    with d:
        st.markdown('<div class="nv-card"><h3>🧩 Business Overview</h3></div>',unsafe_allow_html=True)
        o1,o2=st.columns(2); o1.metric("Products",product_count); o2.metric("Customers",customer_count)
        o3,o4=st.columns(2); o3.metric("Sales entries",len(df_s)); o4.metric("Purchase entries",len(df_p))

    st.markdown('<div class="nv-section">⚡ Quick Actions</div>',unsafe_allow_html=True)
    qa=st.columns(4)
    actions=[("🛒 Product Master","🛒 Products"),("➕ Add Entry","➕ Data Entry"),("👥 Customer Khata","👥 Customer Khata"),("📒 Supplier Khata","📒 Supplier Khata")]
    for col,(label,target) in zip(qa,actions):
        with col:
            if st.button(label,use_container_width=True,key="qa_"+target):
                st.session_state["pending_nav"] = target
                st.rerun()

    st.markdown('<div class="nv-section">🧮 Gram ↔ Amount — Quick Home Calculator</div>',unsafe_allow_html=True)
    calc_products = df_products.copy()
    if calc_products.empty:
        st.info("Add a product first to use the price calculator.")
    else:
        hc1,hc2,hc3 = st.columns([1.4,1,1])
        with hc1:
            calc_id = st.selectbox("Product", calc_products.id.tolist(), format_func=lambda x: calc_products.loc[calc_products.id==x,"product_name"].iloc[0], key="home_calc_product")
        calc_row = calc_products[calc_products.id==calc_id].iloc[0]
        with hc2:
            calc_mode = st.radio("Mode", ["Grams → Amount", "Amount → Grams"], horizontal=True, key="home_calc_mode")
        with hc3:
            if calc_mode == "Grams → Amount":
                g = st.number_input("Grams", min_value=0.0, value=100.0, step=10.0, key="home_calc_grams")
                st.success(f"{g:,.0f} g = {money(float(calc_row.sale_price_kg)*g/1000)}")
            else:
                a = st.number_input("Amount (₹)", min_value=0.0, value=50.0, step=1.0, key="home_calc_amount")
                g = (a/float(calc_row.sale_price_kg))*1000 if float(calc_row.sale_price_kg)>0 else 0
                st.success(f"{money(a)} = {g:,.0f} g")

    st.markdown('<div class="nv-section">🕘 Recent Activity</div>',unsafe_allow_html=True)
    recent=[]
    if not df_s.empty:
        for _,r in df_s.head(4).iterrows(): recent.append((str(r.date),"💰 Sale",money(r.total_sale)))
    if not df_p.empty:
        for _,r in df_p.head(4).iterrows(): recent.append((str(r.date),"🛒 Purchase",money(r.total_purchase)))
    if not df_e.empty:
        for _,r in df_e.head(4).iterrows(): recent.append((str(r.date),"🧾 Expense",money(r.total_expense)))
    if recent:
        rdf=pd.DataFrame(sorted(recent,key=lambda x:x[0],reverse=True)[:8],columns=["Date","Type","Amount"]); st.dataframe(rdf,use_container_width=True,hide_index=True)
    else: st.info("No activity yet. Use Quick Actions to start.")

# ----------------------------- Products -----------------------------
elif menu == "🛒 Products":
    st.markdown('<div class="nv-section">🛒 Product Master & Smart Price Center</div>',unsafe_allow_html=True)
    st.markdown('<div class="nv-hero"><div style="position:relative;z-index:1"><div style="font-size:11px;color:#ffd8c2;font-weight:800;letter-spacing:1px">PRODUCT CONTROL CENTER</div><h2>Manage products, categories & prices ✨</h2><p>Add, edit, delete, filter and manage your complete product price list.</p></div></div>',unsafe_allow_html=True)
    tab_add,tab_list,tab_manage=st.tabs(["➕ Add Product","📋 Price List","✏️ Edit / Delete"])
    categories=["Papad","Masala","Grocery","Other"]

    with tab_add:
        st.markdown('<div class="nv-card"><h3>✨ Add New Product</h3><div class="nv-mini">Create your own product master with a fixed category and per-KG prices.</div></div>',unsafe_allow_html=True)
        with st.form("add_product",clear_on_submit=True):
            a,b=st.columns(2)
            with a:
                pname=st.text_input("Product Name *",placeholder="Example: Khandeshi Masala")
                category=st.selectbox("Product Category *",categories)
                purchase=st.number_input("🔐 Purchase Price — ₹ per 1 KG",min_value=0.0,step=1.0)
            with b:
                sale=st.number_input("💰 Sale Price — ₹ per 1 KG",min_value=0.0,step=1.0)
                st.markdown('<div class="nv-card"><div class="nv-mini">💡 Sale price is visible normally. Purchase price remains protected until you choose Show Purchase Price.</div></div>',unsafe_allow_html=True)
            if st.form_submit_button("💾 Save Product",type="primary",use_container_width=True):
                if not pname.strip(): st.error("Product name required.")
                elif sale<=0: st.error("Sale price must be greater than 0.")
                else:
                    try:
                        execute("INSERT INTO products(product_name,category,purchase_price_kg,sale_price_kg,created_at) VALUES(?,?,?,?,?)",(pname.strip(),category,purchase,sale,dt.datetime.now().isoformat(timespec="seconds")))
                        set_flash(f"Product saved successfully • {pname.strip()}","success"); st.rerun()
                    except sqlite3.IntegrityError: st.error("This product already exists.")

    with tab_list:
        products=qdf("SELECT * FROM products ORDER BY category, product_name")
        if "show_purchase" not in st.session_state: st.session_state.show_purchase=False
        st.markdown('<div class="nv-card"><h3>📋 Complete Product Price List</h3><div class="nv-mini">Simple table view. Filter by category or search by product name.</div></div>',unsafe_allow_html=True)
        f1,f2,f3=st.columns([1.25,2.3,1.25])
        with f1: category_filter=st.selectbox("Category",["Show All","Papad","Masala","Grocery","Other"],key="product_category_filter")
        with f2: search=st.text_input("🔎 Search Product",placeholder="Type product name…",key="product_search")
        with f3:
            st.write("")
            if not pin_is_set():
                st.caption("🔐 Set an Owner PIN from Security to protect purchase prices.")
            if st.session_state.get("purchase_unlocked",False):
                if st.button("🙈 Hide Purchase",use_container_width=True,key="toggle_purchase_list"):
                    st.session_state.purchase_unlocked=False; st.session_state.show_purchase=False; st.rerun()
            else:
                if st.button("🔐 Unlock Purchase Price",use_container_width=True,key="toggle_purchase_list"):
                    if not pin_is_set():
                        st.error("Please set Owner PIN first from Security.")
                    else:
                        st.session_state["ask_purchase_pin"]=True
            if st.session_state.get("ask_purchase_pin",False) and not st.session_state.get("purchase_unlocked",False):
                ppin=st.text_input("Owner PIN",type="password",key="purchase_pin_input")
                if st.button("Unlock",key="unlock_purchase_btn"):
                    if verify_pin(ppin):
                        st.session_state.purchase_unlocked=True; st.session_state.show_purchase=True; st.session_state.ask_purchase_pin=False; st.rerun()
                    else: st.error("Incorrect PIN.")
        if products.empty: st.info("No products yet. Add your first product from Add Product.")
        else:
            if category_filter!="Show All": products=products[products.category.eq(category_filter)]
            if search.strip(): products=products[products.product_name.str.contains(search.strip(),case=False,na=False)]
            rows=[]
            for _,r in products.iterrows():
                rows.append({"Product":r.product_name,"Category":r.category or "Other","Sale / KG":money(r.sale_price_kg),"Purchase / KG":money(r.purchase_price_kg) if st.session_state.show_purchase else "🔒 Hidden"})
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

    with tab_manage:
        products=qdf("SELECT * FROM products ORDER BY product_name")
        if products.empty:
            st.info("No products available to edit or delete.")
        else:
            ids=products.id.tolist()
            pid=st.selectbox("Select Product",ids,format_func=lambda x: products.loc[products.id==x,"product_name"].iloc[0],key="manage_product_id")
            r=products[products.id==pid].iloc[0]
            with st.form("edit_product_form"):
                a,b=st.columns(2)
                with a:
                    epname=st.text_input("Product Name",value=str(r.product_name),key="epname")
                    ecat=st.selectbox("Category",categories,index=categories.index(r.category) if r.category in categories else 3,key="ecat")
                with b:
                    epurchase=st.number_input("Purchase Price / KG",value=float(r.purchase_price_kg),min_value=0.0,step=1.0,key="epurchase")
                    esale=st.number_input("Sale Price / KG",value=float(r.sale_price_kg),min_value=0.0,step=1.0,key="esale")
                if st.form_submit_button("💾 Update Product",type="primary",use_container_width=True):
                    if not epname.strip() or esale<=0: st.error("Product name and valid sale price are required.")
                    else:
                        try:
                            execute("UPDATE products SET product_name=?,category=?,purchase_price_kg=?,sale_price_kg=? WHERE id=?",(epname.strip(),ecat,epurchase,esale,int(pid)))
                            if float(r.purchase_price_kg)!=float(epurchase) or float(r.sale_price_kg)!=float(esale):
                                execute("INSERT INTO price_history(product_id,product_name,category,old_purchase_price,old_sale_price,new_purchase_price,new_sale_price,changed_at) VALUES(?,?,?,?,?,?,?,?)",(int(pid),epname.strip(),ecat,float(r.purchase_price_kg),float(r.sale_price_kg),float(epurchase),float(esale),dt.datetime.now().isoformat(timespec="seconds")))
                            set_flash(f"Product updated successfully • {epname.strip()}","success"); st.rerun()
                        except sqlite3.IntegrityError: st.error("Another product already has this name.")
            st.markdown("### 🗑️ Delete Product")
            confirm=st.checkbox(f"I confirm that I want to delete '{r.product_name}'.",key="confirm_delete_product")
            if st.button("🗑️ Delete Selected Product",type="secondary",disabled=not confirm,use_container_width=True,key="delete_product"):
                archive_record("products",int(pid)); execute("DELETE FROM products WHERE id=?",(int(pid),)); set_flash(f"Product deleted successfully • {r.product_name}","success"); st.rerun()

# ----------------------------- Data Entry -----------------------------
elif menu == "➕ Data Entry":
    st.markdown('<div class="nv-section">📝 Data Entry Center</div>',unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["🛒 Purchase","💰 Sales","🧾 Expenses"])
    suppliers=["Suraj Dana Chana","Durga Trading Company","Bharat General","Jain Traders","KK Traders","Jalaram Papad","Gulab Panipuri","Rais Ponga Wala","Delux Suppliers","Suhana Spices","Ram Bandhu Spices","Raman Papad","Noodles Wala","Sairaj Traders","Others"]
    cols_map={"Suraj Dana Chana":"suraj_dana_chana","Durga Trading Company":"durga_trading_company","Bharat General":"bharat_general","Jain Traders":"jain_traders","KK Traders":"kk_traders","Jalaram Papad":"jalaram_papad","Gulab Panipuri":"gulab_panipuri","Rais Ponga Wala":"rais_ponga_wala","Delux Suppliers":"delux_suppliers","Suhana Spices":"suhana_spices","Ram Bandhu Spices":"ram_bandhu_spices","Raman Papad":"raman_papad","Noodles Wala":"noodles_wala","Sairaj Traders":"sairaj_traders","Others":"others"}
    pcols=[cols_map[x] for x in suppliers]
    with t1:
        with st.form("purchase_form"):
            pdate=st.date_input("Date",now.date(),key="p_date"); vals={}; grid=st.columns(3)
            for i,s in enumerate(suppliers):
                with grid[i%3]: vals[cols_map[s]]=st.number_input(s+" (₹)",min_value=0.0,step=1.0,key="pur_"+cols_map[s])
            if st.form_submit_button("💾 Save Purchase",type="primary"):
                total=sum(vals.values()); execute("INSERT INTO purchases(date,"+",".join(pcols)+",total_purchase) VALUES("+",".join(["?"]*(len(pcols)+2))+")",(str(pdate),*[vals[x] for x in pcols],total)); set_flash(f"Purchase saved successfully • {money(total)}","success"); st.rerun()
        st.markdown("### ✏️ Edit / Delete Purchase Entry")
        pp=qdf("SELECT * FROM purchases ORDER BY date DESC,id DESC")
        if pp.empty: st.info("No purchase entries yet.")
        else:
            pr_id=st.selectbox("Select Purchase Entry",pp.id.tolist(),format_func=lambda x: f"#{x} • {pp.loc[pp.id==x,'date'].iloc[0]} • {money(pp.loc[pp.id==x,'total_purchase'].iloc[0])}",key="manage_purchase_id")
            pr=pp[pp.id==pr_id].iloc[0]
            with st.form("edit_purchase_form"):
                edate=st.date_input("Purchase Date",pd.to_datetime(pr.date).date(),key="edit_pdate")
                ev={}; grid=st.columns(3)
                for i,s in enumerate(suppliers):
                    with grid[i%3]: ev[cols_map[s]]=st.number_input(s+" (₹)",value=float(pr[cols_map[s]] or 0),min_value=0.0,step=1.0,key="edit_pur_"+cols_map[s])
                ca,cb=st.columns(2)
                with ca:
                    if st.form_submit_button("💾 Update Purchase",type="primary",use_container_width=True):
                        total=sum(ev.values()); execute("UPDATE purchases SET date=?,"+",".join([c+"=?" for c in pcols])+",total_purchase=? WHERE id=?",(str(edate),*[ev[x] for x in pcols],total,int(pr_id))); set_flash(f"Purchase updated successfully • {money(total)}","success"); st.rerun()
                with cb:
                    if st.form_submit_button("🗑️ Delete Purchase",use_container_width=True):
                        archive_record("purchases",int(pr_id)); execute("DELETE FROM purchases WHERE id=?",(int(pr_id),)); set_flash("Purchase deleted successfully","success"); st.rerun()
        st.markdown("---")
        st.markdown("### 📋 Complete Purchase History")
        st.caption("See exactly when, from which supplier, and how much was purchased.")
        purchase_history_table(pp,suppliers,cols_map,"purchase_history")
    with t2:
        with st.form("sales_form"):
            sdate=st.date_input("Date",now.date(),key="s_date"); a,b,c=st.columns(3)
            with a: shop=st.number_input("Shop Sale (₹)",min_value=0.0,step=1.0)
            with b: cart=st.number_input("Cart Sale (₹)",min_value=0.0,step=1.0)
            with c: online=st.number_input("Online Collection (₹)",min_value=0.0,step=1.0)
            if st.form_submit_button("💾 Save Sales",type="primary"):
                total=shop+cart+online; execute("INSERT INTO sales(date,shop_sale,cart_sale,online_collection,total_sale) VALUES(?,?,?,?,?)",(str(sdate),shop,cart,online,total)); set_flash(f"Sales saved successfully • {money(total)}","success"); st.rerun()
        st.markdown("### ✏️ Edit / Delete Sale Entry")
        ss=qdf("SELECT * FROM sales ORDER BY date DESC,id DESC")
        if ss.empty: st.info("No sales entries yet.")
        else:
            sr_id=st.selectbox("Select Sale Entry",ss.id.tolist(),format_func=lambda x: f"#{x} • {ss.loc[ss.id==x,'date'].iloc[0]} • {money(ss.loc[ss.id==x,'total_sale'].iloc[0])}",key="manage_sale_id")
            sr=ss[ss.id==sr_id].iloc[0]
            with st.form("edit_sale_form"):
                sdate2=st.date_input("Sale Date",pd.to_datetime(sr.date).date(),key="edit_sdate")
                a,b,c=st.columns(3)
                with a: eshop=st.number_input("Shop Sale (₹)",value=float(sr.shop_sale or 0),min_value=0.0,step=1.0,key="edit_shop")
                with b: ecart=st.number_input("Cart Sale (₹)",value=float(sr.cart_sale or 0),min_value=0.0,step=1.0,key="edit_cart")
                with c: eonline=st.number_input("Online Collection (₹)",value=float(sr.online_collection or 0),min_value=0.0,step=1.0,key="edit_online")
                ca,cb=st.columns(2)
                with ca:
                    if st.form_submit_button("💾 Update Sale",type="primary",use_container_width=True):
                        total=eshop+ecart+eonline; execute("UPDATE sales SET date=?,shop_sale=?,cart_sale=?,online_collection=?,total_sale=? WHERE id=?",(str(sdate2),eshop,ecart,eonline,total,int(sr_id))); set_flash(f"Sale updated successfully • {money(total)}","success"); st.rerun()
                with cb:
                    if st.form_submit_button("🗑️ Delete Sale",use_container_width=True):
                        archive_record("sales",int(sr_id)); execute("DELETE FROM sales WHERE id=?",(int(sr_id),)); set_flash("Sale deleted successfully","success"); st.rerun()
        st.markdown("---")
        st.markdown("### 📋 Complete Sales History")
        st.caption("See exactly when, through which channel, and how much was sold/collected.")
        sales_history_table(ss,"sales_history")
    with t3:
        with st.form("expense_form"):
            edate=st.date_input("Date",now.date(),key="e_date"); a,b=st.columns(2)
            with a: electricity=st.number_input("Electricity Bill (₹)",min_value=0.0,step=1.0); rent=st.number_input("Shop Rent (₹)",min_value=0.0,step=1.0)
            with b: cart_rent=st.number_input("Cart Rent (₹)",min_value=0.0,step=1.0); other=st.number_input("Other Expenses (₹)",min_value=0.0,step=1.0); desc=st.text_input("Other Expense Description")
            if st.form_submit_button("💾 Save Expense",type="primary"):
                total=electricity+rent+cart_rent+other; execute("INSERT INTO expenses(date,electricity_bill,shop_rent,cart_rent,other_expense,other_expense_desc,total_expense) VALUES(?,?,?,?,?,?,?)",(str(edate),electricity,rent,cart_rent,other,desc,total)); set_flash(f"Expense saved successfully • {money(total)}","success"); st.rerun()
        st.markdown("### ✏️ Edit / Delete Expense Entry")
        ee=qdf("SELECT * FROM expenses ORDER BY date DESC,id DESC")
        if not ee.empty:
            er_id=st.selectbox("Select Expense Entry",ee.id.tolist(),format_func=lambda x: f"#{x} • {ee.loc[ee.id==x,'date'].iloc[0]} • {money(ee.loc[ee.id==x,'total_expense'].iloc[0])}",key="manage_expense_id")
            er=ee[ee.id==er_id].iloc[0]
            with st.form("edit_expense_form"):
                erdate=st.date_input("Expense Date",pd.to_datetime(er.date).date(),key="edit_edate")
                a,b=st.columns(2)
                with a: eelectricity=st.number_input("Electricity Bill (₹)",value=float(er.electricity_bill or 0),min_value=0.0,step=1.0,key="edit_electricity"); erent=st.number_input("Shop Rent (₹)",value=float(er.shop_rent or 0),min_value=0.0,step=1.0,key="edit_rent")
                with b: ecart_rent=st.number_input("Cart Rent (₹)",value=float(er.cart_rent or 0),min_value=0.0,step=1.0,key="edit_cart_rent"); eother=st.number_input("Other Expenses (₹)",value=float(er.other_expense or 0),min_value=0.0,step=1.0,key="edit_other"); edesc=st.text_input("Other Expense Description",value=str(er.other_expense_desc or ""),key="edit_desc")
                ca,cb=st.columns(2)
                with ca:
                    if st.form_submit_button("💾 Update Expense",type="primary",use_container_width=True):
                        total=eelectricity+erent+ecart_rent+eother; execute("UPDATE expenses SET date=?,electricity_bill=?,shop_rent=?,cart_rent=?,other_expense=?,other_expense_desc=?,total_expense=? WHERE id=?",(str(erdate),eelectricity,erent,ecart_rent,eother,edesc,total,int(er_id))); set_flash(f"Expense updated successfully • {money(total)}","success"); st.rerun()
                with cb:
                    if st.form_submit_button("🗑️ Delete Expense",use_container_width=True):
                        archive_record("expenses",int(er_id)); execute("DELETE FROM expenses WHERE id=?",(int(er_id),)); set_flash("Expense deleted successfully","success"); st.rerun()

# ----------------------------- Supplier Khata -----------------------------
elif menu == "📒 Supplier Khata":
    st.markdown('<div class="nv-section">📒 Supplier Credit Khata</div>',unsafe_allow_html=True)
    suppliers=["Suraj Dana Chana","Durga Trading Company","Bharat General","Jain Traders","KK Traders","Jalaram Papad","Gulab Panipuri","Rais Ponga Wala","Delux Suppliers","Suhana Spices","Ram Bandhu Spices","Raman Papad","Noodles Wala","Sairaj Traders","Other"]
    with st.form("supplier_form"):
        a,b=st.columns(2)
        with a: udate=st.date_input("Date",now.date(),key="su_date"); supplier=st.selectbox("Supplier",suppliers); amount=st.number_input("Amount (₹)",min_value=0.0,step=1.0)
        with b: custom=st.text_input("If Other, supplier name"); st.caption("New entries are marked Pending automatically.")
        if st.form_submit_button("💾 Save Credit",type="primary"):
            name=custom.strip() if supplier=="Other" else supplier
            if not name: st.error("Supplier name required.")
            else: execute("INSERT INTO supplier_udhaar(date,supplier_name,amount,status) VALUES(?,?,?,?)",(str(udate),name,amount,"Pending")); set_flash("Supplier credit saved successfully","success"); st.rerun()
    x=qdf("SELECT * FROM supplier_udhaar ORDER BY date DESC,id DESC")
    if not x.empty:
        f=st.radio("Status",["All","Pending","Paid"],horizontal=True,key="sup_status"); view=x if f=="All" else x[x.status==f]
        st.dataframe(view,use_container_width=True,hide_index=True)
        for _,r in view.iterrows():
            if r.status=="Pending" and st.button(f"✅ Mark Paid • {r.supplier_name} • {money(r.amount)}",key=f"s_paid_{r.id}"):
                execute("UPDATE supplier_udhaar SET status='Paid' WHERE id=?",(int(r.id),)); set_flash("Supplier payment status updated successfully","success"); st.rerun()
    else: st.info("No supplier khata records.")

# ----------------------------- Customer Khata -----------------------------
elif menu == "👥 Customer Khata":
    st.markdown('<div class="nv-section">👥 Customer Credit Khata</div>',unsafe_allow_html=True)
    with st.form("customer_form"):
        a,b=st.columns(2)
        with a: cdate=st.date_input("Date",now.date(),key="cu_date"); ctype=st.selectbox("Type",["Retail","Wholesale"]); cname=st.text_input("Customer Name")
        with b: phone=st.text_input("Mobile (10 digits)"); camount=st.number_input("Amount (₹)",min_value=0.0,step=1.0)
        if st.form_submit_button("💾 Save Customer Credit",type="primary"):
            cp=phone.strip()
            if not cname.strip(): st.error("Customer name required.")
            elif not cp.isdigit() or len(cp)!=10: st.error("Enter exact 10-digit mobile number.")
            else:
                execute("INSERT OR IGNORE INTO customer_directory(customer_name,phone_number,customer_type,address,notes) VALUES(?,?,?,?,?)",(cname.strip(),cp,ctype,"","Added via Khata"))
                execute("INSERT INTO customer_udhaar(date,customer_name,phone_number,amount,status) VALUES(?,?,?,?,?)",(str(cdate),cname.strip(),cp,camount,"Pending")); set_flash("Customer credit saved successfully","success"); st.rerun()
    x=qdf("SELECT * FROM customer_udhaar ORDER BY date DESC,id DESC"); search=st.text_input("🔍 Search customer name / mobile",placeholder="Type here…")
    if not x.empty:
        if search.strip():
            q=search.strip().lower(); x=x[x.customer_name.str.lower().str.contains(q,na=False)|x.phone_number.astype(str).str.contains(q,na=False)]
        groups=x.groupby(["customer_name","phone_number"],dropna=False)
        for (name,phone),g in groups:
            due=float(g.loc[g.status.eq("Pending"),"amount"].sum()); wa=f"https://wa.me/91{phone}?text={urllib.parse.quote(f'Hello {name}, your pending balance with Navrang Masala is {money(due)}. Please make the payment.') }"
            st.markdown(f'<div class="nv-product"><div class="nv-product-name">👤 {name}</div><div class="nv-detail">📞 {phone} • 🔴 Pending: <b>{money(due)}</b></div></div>',unsafe_allow_html=True)
            b1,b2=st.columns(2)
            with b1:
                if due>0 and str(phone).isdigit() and len(str(phone))==10: st.markdown(f'<a href="{wa}" target="_blank"><button style="width:100%;background:#25D366;color:white;border:0;border-radius:10px;padding:10px;font-weight:800">💬 WhatsApp Reminder</button></a>',unsafe_allow_html=True)
            with b2:
                pending=g[g.status=="Pending"]
                if not pending.empty and st.button("✅ Mark Latest Paid",key=f"cu_paid_{name}_{phone}"):
                    execute("UPDATE customer_udhaar SET status='Paid' WHERE id=?",(int(pending.iloc[0].id),)); set_flash("Customer payment status updated successfully","success"); st.rerun()
    else: st.info("No customer credit records.")

# ----------------------------- Customers & WhatsApp -----------------------------
elif menu == "📇 Customers & WA":
    st.markdown('<div class="nv-section">📇 Customer Directory & WhatsApp Hub</div>',unsafe_allow_html=True)
    with st.form("directory_form"):
        a,b=st.columns(2)
        with a: dtype=st.selectbox("Category",["Retail","Wholesale"]); dname=st.text_input("Full Name"); dphone=st.text_input("Mobile (10 digits)")
        with b: daddr=st.text_input("Address / City"); dnotes=st.text_area("Notes")
        if st.form_submit_button("💾 Save Customer",type="primary"):
            cp=dphone.strip()
            if not dname.strip(): st.error("Name required.")
            elif not cp.isdigit() or len(cp)!=10: st.error("Enter 10-digit mobile number.")
            else:
                try: execute("INSERT INTO customer_directory(customer_name,phone_number,customer_type,address,notes) VALUES(?,?,?,?,?)",(dname.strip(),cp,dtype,daddr.strip(),dnotes.strip())); set_flash("Customer saved successfully","success"); st.rerun()
                except sqlite3.IntegrityError: st.error("Mobile number already registered.")
    x=qdf("SELECT * FROM customer_directory ORDER BY customer_name")
    search=st.text_input("🔎 Search directory",placeholder="Name or mobile")
    if search.strip(): x=x[x.customer_name.str.contains(search.strip(),case=False,na=False)|x.phone_number.astype(str).str.contains(search.strip(),na=False)]
    template=st.text_area("💬 WhatsApp message template",value="Hello {name}, new products and offers are available from Navrang Masala!")
    if not x.empty:
        tabs=st.tabs(["🛍️ Retail","📦 Wholesale"])
        for tab,typ in zip(tabs,["Retail","Wholesale"]):
            with tab:
                view=x[x.customer_type==typ]
                for _,r in view.iterrows():
                    msg=template.replace("{name}",str(r.customer_name)); link=f"https://wa.me/91{r.phone_number}?text={urllib.parse.quote(msg)}"
                    st.markdown(f'<div class="nv-product"><div class="nv-product-name">👤 {r.customer_name}</div><div class="nv-detail">📞 {r.phone_number} • {r.address or "Address not added"}</div></div>',unsafe_allow_html=True)
                    st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%;background:#25D366;color:white;border:0;border-radius:10px;padding:10px;font-weight:800">💬 Open WhatsApp</button></a>',unsafe_allow_html=True)
    else: st.info("No customers found.")

# ----------------------------- Reports -----------------------------
elif menu == "📊 Reports":
    st.markdown('<div class="nv-section">📊 Reports & Business Analysis</div>',unsafe_allow_html=True)
    st.markdown('<div class="nv-hero"><div style="position:relative;z-index:1"><div style="font-size:11px;color:#ffd8c2;font-weight:800;letter-spacing:1px">REPORT CONTROL CENTER</div><h2>Filter, review and manage your business data 📊</h2><p>Purchases and Sales have separate date, amount and type filters for faster checking.</p></div></div>',unsafe_allow_html=True)

    rt1,rt2,rt3,rt4,rt5,rt6,rt7,rt8=st.tabs(["💰 Sales Report","🛒 Purchase Report","🧾 Expense Report","📅 Daily Closing","📆 Monthly Summary","💰 Price History","👥 Customer Statement","📒 Supplier Statement"])

    def date_range_filter(df, prefix):
        if df.empty or "dt" not in df.columns:
            return df
        c1,c2=st.columns(2)
        with c1: from_d=st.date_input("From Date",now.date().replace(day=1),key=prefix+"_from")
        with c2: to_d=st.date_input("To Date",now.date(),key=prefix+"_to")
        if from_d>to_d:
            st.error("From Date cannot be after To Date.")
            return df.iloc[0:0]
        return df[(df.dt.dt.date>=from_d)&(df.dt.dt.date<=to_d)]

    with rt1:
        st.markdown('<div class="nv-card"><h3>💰 Sales Filters</h3><div class="nv-mini">Search sales by date range, sale channel and amount.</div></div>',unsafe_allow_html=True)
        fs=date_range_filter(df_s,"sales_report")
        c1,c2,c3=st.columns(3)
        with c1:
            sale_type=st.selectbox("Sale Type",["Show All","Shop Sale","Cart Sale","Online Collection"],key="sales_report_type")
        with c2:
            min_sale=st.number_input("Minimum Total Sale (₹)",min_value=0.0,value=0.0,step=100.0,key="sales_report_min")
        with c3:
            max_default=float(fs.total_sale.max()) if not fs.empty else 0.0
            max_sale=st.number_input("Maximum Total Sale (₹)",min_value=0.0,value=max_default,step=100.0,key="sales_report_max")
        if not fs.empty:
            fs=fs[(fs.total_sale>=min_sale)&(fs.total_sale<=max_sale)]
            if sale_type=="Shop Sale": fs=fs[fs.shop_sale>0]
            elif sale_type=="Cart Sale": fs=fs[fs.cart_sale>0]
            elif sale_type=="Online Collection": fs=fs[fs.online_collection>0]
        total=float(fs.total_sale.sum()) if not fs.empty else 0.0
        a,b,c=st.columns(3); a.metric("Matching Entries",len(fs)); b.metric("Total Sales",money(total)); c.metric("Average Sale",money(total/len(fs)) if len(fs) else money(0))
        if fs.empty: st.info("No sales found for the selected filters.")
        else:
            show=fs[["id","date","shop_sale","cart_sale","online_collection","total_sale"]].copy()
            show.columns=["ID","Date","Shop Sale","Cart Sale","Online Collection","Total Sale"]
            st.dataframe(show,use_container_width=True,hide_index=True)
            st.markdown("### 📈 Sales Trend")
            st.line_chart(fs.groupby(fs.dt.dt.date).total_sale.sum().rename("Sales"),use_container_width=True)

    with rt2:
        st.markdown('<div class="nv-card"><h3>🛒 Purchase Filters</h3><div class="nv-mini">Check purchases by date range, supplier and amount.</div></div>',unsafe_allow_html=True)
        fp=date_range_filter(df_p,"purchase_report")
        supplier_map={"Show All":"__all__","Suraj Dana Chana":"suraj_dana_chana","Durga Trading Company":"durga_trading_company","Bharat General":"bharat_general","Jain Traders":"jain_traders","KK Traders":"kk_traders","Jalaram Papad":"jalaram_papad","Gulab Panipuri":"gulab_panipuri","Rais Ponga Wala":"rais_ponga_wala","Delux Suppliers":"delux_suppliers","Suhana Spices":"suhana_spices","Ram Bandhu Spices":"ram_bandhu_spices","Raman Papad":"raman_papad","Noodles Wala":"noodles_wala","Sairaj Traders":"sairaj_traders","Others":"others"}
        c1,c2,c3=st.columns(3)
        with c1: supp=st.selectbox("Supplier",list(supplier_map),key="purchase_report_supplier")
        with c2: min_p=st.number_input("Minimum Total Purchase (₹)",min_value=0.0,value=0.0,step=100.0,key="purchase_report_min")
        with c3:
            max_p_default=float(fp.total_purchase.max()) if not fp.empty else 0.0
            max_p=st.number_input("Maximum Total Purchase (₹)",min_value=0.0,value=max_p_default,step=100.0,key="purchase_report_max")
        if not fp.empty:
            fp=fp[(fp.total_purchase>=min_p)&(fp.total_purchase<=max_p)]
            if supplier_map[supp]!="__all__": fp=fp[fp[supplier_map[supp]]>0]
        total=float(fp.total_purchase.sum()) if not fp.empty else 0.0
        a,b,c=st.columns(3); a.metric("Matching Entries",len(fp)); b.metric("Total Purchases",money(total)); c.metric("Average Purchase",money(total/len(fp)) if len(fp) else money(0))
        if fp.empty: st.info("No purchases found for the selected filters.")
        else:
            show_cols=["id","date"]+list(supplier_map.values())[1:]+["total_purchase"]
            show=fp[[c for c in show_cols if c in fp.columns]].copy()
            st.dataframe(show,use_container_width=True,hide_index=True)
            st.markdown("### 📈 Purchase Trend")
            st.line_chart(fp.groupby(fp.dt.dt.date).total_purchase.sum().rename("Purchases"),use_container_width=True)

    with rt3:
        st.markdown('<div class="nv-card"><h3>🧾 Expense Filters</h3><div class="nv-mini">Review expenses for any selected period.</div></div>',unsafe_allow_html=True)
        fe=date_range_filter(df_e,"expense_report")
        total=float(fe.total_expense.sum()) if not fe.empty else 0.0
        st.metric("Total Expenses",money(total))
        if fe.empty: st.info("No expenses found for the selected period.")
        else: st.dataframe(fe,use_container_width=True,hide_index=True)

    with rt4:
        st.markdown('<div class="nv-card"><h3>📅 Daily Closing</h3><div class="nv-mini">One-day business closing with sales, purchase, expenses and net result.</div></div>',unsafe_allow_html=True)
        close_date=st.date_input("Closing Date",now.date(),key="daily_closing_date")
        ds=df_s[df_s.dt.dt.date==close_date] if not df_s.empty else df_s
        dp=df_p[df_p.dt.dt.date==close_date] if not df_p.empty else df_p
        de=df_e[df_e.dt.dt.date==close_date] if not df_e.empty else df_e
        sv=float(ds.total_sale.sum()) if not ds.empty else 0; pv=float(dp.total_purchase.sum()) if not dp.empty else 0; ev=float(de.total_expense.sum()) if not de.empty else 0
        cols=st.columns(4)
        cols[0].metric("💰 Sales",money(sv)); cols[1].metric("🛒 Purchase",money(pv)); cols[2].metric("🧾 Expense",money(ev)); cols[3].metric("💵 Cash Summary",money(sv-pv-ev))
        st.markdown(f'<div class="nv-card"><b>Closing summary:</b> {close_date.strftime("%d %b %Y")} • Sales {money(sv)} • Purchase {money(pv)} • Expense {money(ev)} • Net {money(sv-pv-ev)}</div>',unsafe_allow_html=True)
        pdf=pdf_report("Navrang Masala — Daily Closing",str(close_date),pd.DataFrame({"Metric":["Sales","Purchase","Expense","Net Result"],"Amount":[money(sv),money(pv),money(ev),money(sv-pv-ev)]}),[])
        st.download_button("📄 Download Daily Closing PDF",pdf,f"daily_closing_{close_date}.pdf","application/pdf",use_container_width=True)

    with rt5:
        st.markdown('<div class="nv-card"><h3>📆 Monthly Business Summary</h3><div class="nv-mini">Month-wise sales, purchases, expenses and net result.</div></div>',unsafe_allow_html=True)
        if not df_s.empty or not df_p.empty or not df_e.empty:
            all_dates=pd.concat([x[["dt"]] for x in [df_s,df_p,df_e] if not x.empty],ignore_index=True)
            months=sorted(all_dates.dt.dropna().dt.to_period("M").astype(str).unique(),reverse=True)
            chosen_month=st.selectbox("Select Month",months,key="monthly_summary_month")
            ym=pd.Period(chosen_month)
            ms=df_s[df_s.dt.dt.to_period("M")==ym] if not df_s.empty else df_s
            mp=df_p[df_p.dt.dt.to_period("M")==ym] if not df_p.empty else df_p
            me=df_e[df_e.dt.dt.to_period("M")==ym] if not df_e.empty else df_e
            sv=float(ms.total_sale.sum()) if not ms.empty else 0; pv=float(mp.total_purchase.sum()) if not mp.empty else 0; ev=float(me.total_expense.sum()) if not me.empty else 0
            a,b,c,d=st.columns(4); a.metric("Sales",money(sv)); b.metric("Purchase",money(pv)); c.metric("Expense",money(ev)); d.metric("Net",money(sv-pv-ev))
            monthly=pd.DataFrame({"Metric":["Sales","Purchase","Expense","Net Result"],"Amount":[money(sv),money(pv),money(ev),money(sv-pv-ev)]}); st.dataframe(monthly,use_container_width=True,hide_index=True)
            pdf=pdf_report("Navrang Masala — Monthly Summary",chosen_month,monthly,[])
            st.download_button("📄 Download Monthly PDF",pdf,f"monthly_summary_{chosen_month}.pdf","application/pdf",use_container_width=True)
        else: st.info("No business records available.")

    with rt6:
        st.markdown('<div class="nv-card"><h3>💰 Product Price History</h3><div class="nv-mini">Every purchase/sale price change is recorded automatically.</div></div>',unsafe_allow_html=True)
        ph=qdf("SELECT * FROM price_history ORDER BY changed_at DESC,id DESC")
        if ph.empty: st.info("No price changes recorded yet. Edit a product price to create history.")
        else:
            pc=st.selectbox("Product",["Show All"]+sorted(ph.product_name.dropna().unique().tolist()),key="price_history_product")
            if pc!="Show All": ph=ph[ph.product_name.eq(pc)]
            show=ph[["changed_at","product_name","category","old_purchase_price","new_purchase_price","old_sale_price","new_sale_price"]].copy()
            show.columns=["Changed At","Product","Category","Old Purchase/KG","New Purchase/KG","Old Sale/KG","New Sale/KG"]
            for c in show.columns[3:]: show[c]=show[c].map(money)
            st.dataframe(show,use_container_width=True,hide_index=True)

    with rt7:
        st.markdown('<div class="nv-card"><h3>👥 Customer Statement</h3><div class="nv-mini">Complete customer Khata transaction history with WhatsApp sharing.</div></div>',unsafe_allow_html=True)
        cu=qdf("SELECT * FROM customer_udhaar ORDER BY date,id")
        if cu.empty: st.info("No customer transactions yet.")
        else:
            customers=sorted(cu.customer_name.dropna().unique().tolist()); cname=st.selectbox("Customer",customers,key="statement_customer")
            cg=cu[cu.customer_name.eq(cname)].copy(); cg["Debit"]=cg["amount"].where(cg.status.eq("Pending"),0); cg["Credit"]=cg["amount"].where(cg.status.eq("Paid"),0); cg["Balance"]=cg["Debit"].cumsum()-cg["Credit"].cumsum()
            show=cg[["date","customer_name","amount","status","Balance"]].copy(); show.columns=["Date","Customer","Amount","Status","Balance"]; show["Amount"]=show["Amount"].map(money); show["Balance"]=show["Balance"].map(money)
            st.dataframe(show,use_container_width=True,hide_index=True)
            due=float(cg.loc[cg.status.eq("Pending"),"amount"].sum()); st.metric("Pending Balance",money(due))
            phone=str(cg.phone_number.iloc[0]) if not cg.empty else ""
            if phone.isdigit() and len(phone)==10:
                msg=f"Hello {cname}, Navrang Masala statement: pending balance {money(due)}."; link=f"https://wa.me/91{phone}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%;background:#25D366;color:white;border:0;border-radius:10px;padding:10px;font-weight:800">💬 Send Statement on WhatsApp</button></a>',unsafe_allow_html=True)
            pdf=pdf_report(f"Customer Statement — {cname}","Navrang Masala",show,[])
            st.download_button("📄 Download Customer Statement PDF",pdf,f"customer_statement_{cname.replace(' ','_')}.pdf","application/pdf",use_container_width=True)

    with rt8:
        st.markdown('<div class="nv-card"><h3>📒 Supplier Statement</h3><div class="nv-mini">Complete supplier Khata transaction history with WhatsApp sharing.</div></div>',unsafe_allow_html=True)
        su=qdf("SELECT * FROM supplier_udhaar ORDER BY date,id")
        if su.empty: st.info("No supplier transactions yet.")
        else:
            suppliers=sorted(su.supplier_name.dropna().unique().tolist()); sname=st.selectbox("Supplier",suppliers,key="statement_supplier")
            sg=su[su.supplier_name.eq(sname)].copy(); sg["Debit"]=sg["amount"].where(sg.status.eq("Pending"),0); sg["Credit"]=sg["amount"].where(sg.status.eq("Paid"),0); sg["Balance"]=sg["Debit"].cumsum()-sg["Credit"].cumsum()
            show=sg[["date","supplier_name","amount","status","Balance"]].copy(); show.columns=["Date","Supplier","Amount","Status","Balance"]; show["Amount"]=show["Amount"].map(money); show["Balance"]=show["Balance"].map(money)
            st.dataframe(show,use_container_width=True,hide_index=True)
            due=float(sg.loc[sg.status.eq("Pending"),"amount"].sum()); st.metric("Pending Payable",money(due))
            supp_phone=st.text_input("Supplier Mobile for WhatsApp (optional)",placeholder="10-digit mobile number",key="supplier_statement_phone")
            if supp_phone.strip().isdigit() and len(supp_phone.strip())==10:
                msg=f"Hello {sname}, Navrang Masala statement: pending payable {money(due)}."; link=f"https://wa.me/91{supp_phone.strip()}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%;background:#25D366;color:white;border:0;border-radius:10px;padding:10px;font-weight:800">💬 Send Supplier Statement on WhatsApp</button></a>',unsafe_allow_html=True)
            pdf=pdf_report(f"Supplier Statement — {sname}","Navrang Masala",show,[])
            st.download_button("📄 Download Supplier Statement PDF",pdf,f"supplier_statement_{sname.replace(' ','_')}.pdf","application/pdf",use_container_width=True)

# ----------------------------- Festival & Purchase Planning -----------------------------
elif menu == "🗓️ Festival Planning":
    st.markdown('<div class="nv-section">🗓️ Festival & Purchase Planning</div>',unsafe_allow_html=True)
    st.markdown('<div class="nv-hero"><div style="position:relative;z-index:1"><div style="font-size:11px;color:#ffd8c2;font-weight:800;letter-spacing:1px">BUSINESS PLANNING CALENDAR</div><h2>Plan purchases around upcoming festivals 🛒</h2><p>Important festivals for the current and next month, with dates and advance planning guidance.</p></div></div>',unsafe_allow_html=True)

    # 2026 India/Gujarat-oriented major festival dates. These are planning dates,
    # not a replacement for local panchang/holiday notifications.
    festival_2026 = [
        ("2026-09-04","Janmashtami","High","Grocery, Masala"),
        ("2026-09-14","Ganesh Chaturthi","High","Grocery, Masala, Other"),
        ("2026-09-25","Anant Chaturdashi / Ganesh Visarjan","Medium","Grocery, Masala, Other"),
        ("2026-10-02","Gandhi Jayanti","Medium","Grocery, Other"),
        ("2026-10-10","Sarva Pitru Amavasya","Medium","Grocery, Masala"),
        ("2026-10-11","Navratri Begins","Very High","Grocery, Masala, Papad"),
        ("2026-10-16","Saraswati Avahan","Medium","Grocery, Other"),
        ("2026-10-17","Saraswati Puja","Medium","Grocery, Other"),
        ("2026-10-19","Durga Ashtami / Maha Navami","Very High","Grocery, Masala, Papad"),
        ("2026-10-20","Vijayadashami / Dussehra","Very High","Grocery, Masala, Papad, Other"),
        ("2026-10-25","Sharad Purnima / Kojagara Puja","High","Grocery, Masala"),
        ("2026-10-29","Karwa Chauth","Medium","Grocery, Masala, Other"),
        ("2026-11-07","Chhoti Diwali","Very High","Grocery, Masala, Papad, Other"),
        ("2026-11-08","Diwali / Lakshmi Puja","Very High","Grocery, Masala, Papad, Other"),
        ("2026-11-10","Govardhan Puja","High","Grocery, Masala"),
        ("2026-11-11","Bhai Dooj","High","Grocery, Masala, Other"),
        ("2026-11-15","Chhath Puja","Medium","Grocery, Other"),
        ("2026-11-24","Guru Nanak Jayanti","High","Grocery, Masala"),
    ]
    fdf=pd.DataFrame(festival_2026,columns=["date","festival","priority","suggested_categories"])
    fdf["date"]=pd.to_datetime(fdf["date"])
    today=dt.date.today()
    current_start=dt.date(today.year,today.month,1)
    next_month=1 if today.month==12 else today.month+1
    next_year=today.year+1 if today.month==12 else today.year
    next_start=dt.date(next_year,next_month,1)
    next_end=dt.date(next_year+1,1,1) if next_month==12 else dt.date(next_year,next_month+1,1)

    if today.year != 2026:
        st.warning("Festival planning dates are currently prepared for 2026. For another year, update the festival list from the latest India/Gujarat calendar.")

    current=fdf[(fdf.date.dt.year==current_start.year)&(fdf.date.dt.month==current_start.month)].copy()
    nxt=fdf[(fdf.date.dt.year==next_year)&(fdf.date.dt.month==next_month)].copy()
    current["Days Left"]=(current.date.dt.date-today).apply(lambda x:x.days)
    nxt["Days Left"]=(nxt.date.dt.date-today).apply(lambda x:x.days)
    for d in (current,nxt):
        d["Date"]=d["date"].dt.strftime("%d %b %Y")
        d.drop(columns=["date"],inplace=True)
        d["Planning"] = d["Days Left"].apply(lambda x:"Start now" if x<=7 else ("Order in 7 days" if x<=14 else "Plan order"))

    c1,c2=st.columns(2)
    with c1:
        st.markdown(f'<div class="nv-card"><h3>📍 Current Month — {current_start.strftime("%B %Y")}</h3><div class="nv-mini">Festival planning based on the current date.</div></div>',unsafe_allow_html=True)
        if current.empty: st.info("No major festivals are listed for this month.")
        else: st.dataframe(current[["Date","festival","Days Left","priority","suggested_categories","Planning"]].rename(columns={"festival":"Festival","priority":"Priority","suggested_categories":"Suggested Categories"}),use_container_width=True,hide_index=True)
    with c2:
        st.markdown(f'<div class="nv-card"><h3>🔜 Next Month — {next_start.strftime("%B %Y")}</h3><div class="nv-mini">Plan purchases in advance for the next month.</div></div>',unsafe_allow_html=True)
        if nxt.empty: st.info("No major festivals are listed for next month.")
        else: st.dataframe(nxt[["Date","festival","Days Left","priority","suggested_categories","Planning"]].rename(columns={"festival":"Festival","priority":"Priority","suggested_categories":"Suggested Categories"}),use_container_width=True,hide_index=True)

    st.markdown("### 🛒 Purchase Planning Helper")
    st.caption("Suggested categories are planning guidance. Decide order quantities using your actual sales history.")
    if not nxt.empty:
        pick=st.selectbox("Select Festival",nxt["festival"].tolist(),key="festival_pick")
        fr=nxt[nxt.festival.eq(pick)].iloc[0]
        days=max(0,int(fr["Days Left"]))
        st.info(f"📅 **{pick}** — {fr['Date']} • {days} days remaining\n\n🛒 Suggested categories: **{fr['suggested_categories']}**\n\n⏰ Planning: **{fr['Planning']}**")
        lead=st.number_input("How many days before the festival would you like to order?",min_value=1,max_value=60,value=7,step=1,key="festival_lead")
        order_date=dt.datetime.strptime(str(fr["Date"]), "%d %b %Y").date()-dt.timedelta(days=int(lead))
        if order_date <= today:
            st.success(f"🟢 Order planning date: **{order_date.strftime('%d %b %Y')}** — you can plan the order now.")
        else:
            st.warning(f"🟡 Suggested order date: **{order_date.strftime('%d %b %Y')}**")

    st.markdown("### 📊 Your Business Data se Planning")
    # Show recent category sales if product-wise sales exist in future; current sales
    # table is aggregate, so we avoid pretending it has category-level demand.
    st.info("💡 The Sales table currently stores Shop, Cart and Online totals, not product-category sales. Quantity is therefore not estimated here. Product-wise sales can support automatic festival demand estimates in the future.")

# ----------------------------- Tools & Control Center -----------------------------
elif menu == "🧰 Tools":
    st.markdown('<div class="nv-section">🧰 Tools & Control Center</div>',unsafe_allow_html=True)
    st.markdown("""<div class="nv-tool-grid">
      <div class="nv-tool-card"><div class="icon">🔍</div><div class="name">Global Search</div><div class="desc">Find products, khata and entries quickly.</div></div>
      <div class="nv-tool-card"><div class="icon">🧠</div><div class="name">Smart Insights</div><div class="desc">Quick business numbers and trends.</div></div>
      <div class="nv-tool-card"><div class="icon">📅</div><div class="name">Calendar</div><div class="desc">See daily sales, purchase and expense activity.</div></div>
      <div class="nv-tool-card"><div class="icon">📤</div><div class="name">Export & Safety</div><div class="desc">Excel/CSV export, restore and activity log.</div></div>
    </div>
    <div class="nv-mobile-note">📱 Mobile mode: swipe the tool tabs left/right to open each tool.</div>""",unsafe_allow_html=True)
    tt=st.tabs(["🔍 Global Search","🧠 Smart Insights","📅 Calendar","📤 Excel Export","↩️ Restore","📝 Activity Log","💰 Payments","🗒️ Notes"])

    with tt[0]:
        q=st.text_input("🔍 Search everything",placeholder="Product, customer, supplier, date, note…",key="global_search")
        if q.strip():
            needle=f"%{q.strip()}%"; results=[]
            searches=[("Products","SELECT id,product_name,category,sale_price_kg FROM products WHERE product_name LIKE ? OR category LIKE ?",(needle,needle)),("Purchases","SELECT id,date,total_purchase,notes FROM purchases WHERE date LIKE ? OR notes LIKE ?",(needle,needle)),("Sales","SELECT id,date,total_sale,notes FROM sales WHERE date LIKE ? OR notes LIKE ?",(needle,needle)),("Expenses","SELECT id,date,total_expense,other_expense_desc,notes FROM expenses WHERE date LIKE ? OR other_expense_desc LIKE ? OR notes LIKE ?",(needle,needle,needle)),("Customers","SELECT id,customer_name,phone_number,address,notes FROM customer_directory WHERE customer_name LIKE ? OR phone_number LIKE ? OR address LIKE ? OR notes LIKE ?",(needle,needle,needle,needle)),("Customer Khata","SELECT id,date,customer_name,amount,status FROM customer_udhaar WHERE customer_name LIKE ? OR phone_number LIKE ? OR date LIKE ?",(needle,needle,needle)),("Supplier Khata","SELECT id,date,supplier_name,amount,status FROM supplier_udhaar WHERE supplier_name LIKE ? OR date LIKE ?",(needle,needle))]
            for name,sql,params in searches:
                try:
                    d=qdf(sql,params)
                    if not d.empty: results.append((name,d))
                except Exception: pass
            if not results: st.info("No matching records found.")
            for name,d in results:
                st.markdown(f"### {name} • {len(d)} match(es)"); st.dataframe(d,use_container_width=True,hide_index=True)
        else: st.caption("Search across products, purchases, sales, expenses, customers and khata.")

    with tt[1]:
        st.markdown("### 🧠 Business Smart Insights")
        today=now.date(); month_start=today.replace(day=1)
        ms=df_s[df_s.dt.dt.date>=month_start] if not df_s.empty else df_s
        mp=df_p[df_p.dt.dt.date>=month_start] if not df_p.empty else df_p
        me=df_e[df_e.dt.dt.date>=month_start] if not df_e.empty else df_e
        st.session_state.setdefault("_insight_seen",True)
        sales=float(ms.total_sale.sum()) if not ms.empty else 0; purch=float(mp.total_purchase.sum()) if not mp.empty else 0; exp=float(me.total_expense.sum()) if not me.empty else 0
        a,b,c,d=st.columns(4); a.metric("This Month Sales",money(sales)); b.metric("Purchases",money(purch)); c.metric("Expenses",money(exp)); d.metric("Net Result",money(sales-purch-exp))
        if sales+purch+exp==0: st.info("Add business entries to generate insights.")
        else:
            if sales>purch+exp: st.success("Current month sales are higher than combined purchases and expenses.")
            else: st.warning("Current month purchases + expenses are currently at or above sales.")
            if not ms.empty:
                day_sales=ms.groupby(ms.dt.dt.date).total_sale.sum().sort_values(ascending=False)
                if not day_sales.empty: st.info(f"Highest recorded sales day this month: {day_sales.index[0]} • {money(day_sales.iloc[0])}")
            if not df_products.empty:
                cat=df_products.groupby("category").size().sort_values(ascending=False)
                if not cat.empty: st.info(f"Product catalog: {len(df_products)} products • Largest category by count: {cat.index[0]} ({int(cat.iloc[0])})")
            cust=df_cu.groupby("customer_name").amount.sum().sort_values(ascending=False) if not df_cu.empty else pd.Series(dtype=float)
            if not cust.empty: st.info(f"Largest customer-credit total recorded: {cust.index[0]} • {money(cust.iloc[0])}")

    with tt[2]:
        st.markdown("### 📅 Business Calendar")
        cal_month=st.date_input("Select Month",now.date(),key="calendar_month")
        start=cal_month.replace(day=1); end=(start+dt.timedelta(days=32)).replace(day=1)-dt.timedelta(days=1)
        days=pd.date_range(start,end)
        rows=[]
        for day in days:
            ds=df_s[df_s.dt.dt.date==day.date()].total_sale.sum() if not df_s.empty else 0
            dp=df_p[df_p.dt.dt.date==day.date()].total_purchase.sum() if not df_p.empty else 0
            de=df_e[df_e.dt.dt.date==day.date()].total_expense.sum() if not df_e.empty else 0
            rows.append({"Date":day.date(),"Sales":ds,"Purchase":dp,"Expenses":de,"Net":ds-dp-de,"Activity":("🟢" if ds or dp or de else "—")})
        caldf=pd.DataFrame(rows); st.dataframe(caldf,use_container_width=True,hide_index=True)
        selected=st.date_input("Open date details",start,key="calendar_detail")
        dayrow=caldf[caldf.Date==selected]
        if not dayrow.empty: st.metric(f"{selected} Net Result",money(dayrow.iloc[0].Net))

    with tt[3]:
        st.markdown("### 📤 Excel Export Center")
        exp_from=st.date_input("From Date",now.date().replace(day=1),key="excel_from"); exp_to=st.date_input("To Date",now.date(),key="excel_to")
        if exp_from>exp_to: st.error("From Date cannot be after To Date.")
        else:
            def rng(d,col):
                if d.empty or col not in d.columns:
                    return d.copy()
                if not pd.api.types.is_datetime64_any_dtype(d[col]):
                    temp=pd.to_datetime(d[col],errors="coerce")
                else:
                    temp=d[col]
                return d[temp.dt.date.ge(exp_from) & temp.dt.date.le(exp_to)].copy()

            ep,es,ee=rng(df_p,"dt"),rng(df_s,"dt"),rng(df_e,"dt")
            st.caption("Excel export uses XlsxWriter when available. No openpyxl installation is required.")
            if st.button("📊 Prepare Excel Report",type="primary",use_container_width=True,key="prepare_excel_report"):
                try:
                    frames={
                        "Purchases":ep.drop(columns=["dt"],errors="ignore"),
                        "Sales":es.drop(columns=["dt"],errors="ignore"),
                        "Expenses":ee.drop(columns=["dt"],errors="ignore"),
                        "Products":df_products.copy(),
                        "Customer Khata":df_cu.copy(),
                        "Supplier Khata":df_u.copy(),
                    }
                    if importlib.util.find_spec("xlsxwriter") is not None:
                        out=io.BytesIO()
                        with pd.ExcelWriter(out,engine="xlsxwriter") as writer:
                            for sheet_name,frame in frames.items():
                                frame.to_excel(writer,index=False,sheet_name=sheet_name)
                        st.download_button(
                            "📥 Download Excel Report (.xlsx)",
                            out.getvalue(),
                            f"navrang_vyapar_{exp_from}_{exp_to}.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                            key="download_excel_report",
                        )
                        st.success("Excel report is ready.")
                    else:
                        # Safe fallback: downloadable ZIP containing CSV files.
                        # This keeps the app usable even when no Excel engine is installed.
                        zip_out=io.BytesIO()
                        with zipfile.ZipFile(zip_out,"w",compression=zipfile.ZIP_DEFLATED) as zf:
                            for sheet_name,frame in frames.items():
                                safe_name=sheet_name.replace(" ","_").replace("/","-")
                                zf.writestr(f"{safe_name}.csv",frame.to_csv(index=False).encode("utf-8-sig"))
                        st.download_button(
                            "📦 Download Business Data (CSV ZIP)",
                            zip_out.getvalue(),
                            f"navrang_vyapar_{exp_from}_{exp_to}_csv.zip",
                            "application/zip",
                            use_container_width=True,
                            key="download_csv_zip",
                        )
                        st.info("XlsxWriter is not installed, so a CSV ZIP backup is provided instead. The app itself will continue without an Excel dependency.")
                except Exception as ex:
                    st.error(f"Excel export failed safely: {ex}")

    with tt[4]:
        st.markdown("### ↩️ Recently Deleted • Restore")
        deleted=qdf("SELECT * FROM deleted_records ORDER BY id DESC")
        if deleted.empty: st.info("No deleted records available for restore.")
        else:
            for _,r in deleted.head(30).iterrows():
                label=f"#{r.id} • {r.table_name} • Record {r.record_id} • {r.deleted_at}"
                if st.button("↩️ Restore " + label,key=f"restore_{r.id}"):
                    try:
                        data=json.loads(r.record_json); cols=list(data.keys()); vals=[data[c] for c in cols]
                        placeholders=','.join(['?']*len(cols)); execute(f"INSERT INTO {r.table_name} ({','.join(cols)}) VALUES ({placeholders})",vals)
                        execute("DELETE FROM deleted_records WHERE id=?",(int(r.id),)); set_flash(f"{r.table_name} record restored successfully","success"); st.rerun()
                    except Exception as ex: st.error(f"Restore failed: {ex}")

    with tt[5]:
        st.markdown("### 📝 Activity Log")
        logs=qdf("SELECT changed_at,action,table_name,record_id,details FROM activity_log ORDER BY id DESC LIMIT 200")
        st.dataframe(logs,use_container_width=True,hide_index=True) if not logs.empty else st.info("No activity recorded yet.")

    with tt[6]:
        st.markdown("### 💰 Payment Tracking")
        pay_type=st.selectbox("Account Type",["Customer","Supplier"],key="pay_type")
        table="customer_udhaar" if pay_type=="Customer" else "supplier_udhaar"; namecol="customer_name" if pay_type=="Customer" else "supplier_name"
        pay=qdf(f"SELECT * FROM {table} ORDER BY date DESC,id DESC")
        if not pay.empty:
            pay["paid_amount"]=pd.to_numeric(pay.get("paid_amount",0),errors="coerce").fillna(0); pay["Balance"]=pay["amount"]-pay["paid_amount"]
            st.dataframe(pay[["id","date",namecol,"amount","paid_amount","Balance","status"]],use_container_width=True,hide_index=True)
            pid=st.selectbox("Select account entry",pay.id.tolist(),format_func=lambda x:f"#{x} • {pay.loc[pay.id==x,namecol].iloc[0]} • {money(pay.loc[pay.id==x,'Balance'].iloc[0])} balance",key="pay_entry")
            row=pay[pay.id==pid].iloc[0]; bal=max(0,float(row.amount)-float(row.paid_amount)); amount=st.number_input("Payment received / paid now (₹)",min_value=0.0,max_value=bal,value=0.0,step=1.0,key="pay_amount")
            if st.button("💾 Record Payment",type="primary"):
                newpaid=float(row.paid_amount)+amount; status="Paid" if newpaid>=float(row.amount) else ("Pending" if newpaid<=0 else "Partial")
                execute(f"UPDATE {table} SET paid_amount=?,status=?,payment_date=? WHERE id=?",(newpaid,status,dt.date.today().isoformat(),int(pid))); set_flash("Payment recorded successfully","success"); st.rerun()
        else: st.info("No khata entries found.")

    with tt[7]:
        st.markdown("### 🗒️ Notes & Remarks")
        with st.form("notes_form"):
            nd=st.date_input("Date",now.date(),key="note_date"); title=st.text_input("Title"); note=st.text_area("Note / Remark",placeholder="Important follow-up, supplier detail, customer note…")
            if st.form_submit_button("💾 Save Note",type="primary"):
                if note.strip(): execute("INSERT INTO business_notes(note_date,title,note,created_at) VALUES(?,?,?,?)",(str(nd),title.strip(),note.strip(),dt.datetime.now().isoformat(timespec="seconds"))); set_flash("Note saved successfully","success"); st.rerun()
        notes=qdf("SELECT * FROM business_notes ORDER BY note_date DESC,id DESC")
        st.dataframe(notes,use_container_width=True,hide_index=True) if not notes.empty else st.info("No notes yet.")

# ----------------------------- Security -----------------------------
elif menu == "🔐 Security":
    st.markdown('<div class="nv-section">🔐 Owner Security & Purchase Price PIN</div>',unsafe_allow_html=True)
    st.markdown('<div class="nv-card"><h3>Protect Sensitive Purchase Prices</h3><div class="nv-mini">Purchase prices are stored securely; the PIN is stored as a SHA-256 hash, not as plain text.</div></div>',unsafe_allow_html=True)
    if pin_is_set():
        st.success("Owner PIN is active. Purchase prices require the PIN to unlock.")
        with st.form("change_pin_form"):
            old=st.text_input("Current PIN",type="password"); new=st.text_input("New PIN",type="password"); confirm=st.text_input("Confirm New PIN",type="password")
            if st.form_submit_button("🔄 Change PIN",type="primary"):
                if not verify_pin(old): st.error("Current PIN is incorrect.")
                elif len(new)<4: st.error("PIN should be at least 4 digits/characters.")
                elif new!=confirm: st.error("New PINs do not match.")
                else:
                    execute("UPDATE app_security SET pin_hash=?,updated_at=? WHERE id=1",(hash_pin(new),dt.datetime.now().isoformat(timespec="seconds"))); st.session_state.purchase_unlocked=False; st.success("Owner PIN changed successfully.")
    else:
        st.info("No Owner PIN is configured yet.")
        with st.form("set_pin_form"):
            new=st.text_input("Create Owner PIN",type="password"); confirm=st.text_input("Confirm PIN",type="password")
            if st.form_submit_button("🔐 Set Owner PIN",type="primary"):
                if len(new)<4: st.error("PIN should be at least 4 digits/characters.")
                elif new!=confirm: st.error("PINs do not match.")
                else:
                    execute("INSERT OR REPLACE INTO app_security(id,pin_hash,updated_at) VALUES(1,?,?)",(hash_pin(new),dt.datetime.now().isoformat(timespec="seconds"))); st.success("Owner PIN set successfully. Purchase prices are now protected."); st.rerun()

# ----------------------------- Backup -----------------------------
elif menu == "📂 Backup":
    st.markdown('<div class="nv-section">📂 Export, Backup & Data Safety</div>',unsafe_allow_html=True)
    st.info("Keep a regular database backup. CSV exports are useful for Excel/reporting; the DB backup preserves the full application data structure.")
    conn=conn_db()
    tables=["purchases","sales","expenses","supplier_udhaar","customer_udhaar","customer_directory","products","price_history","app_security"]
    csv_cols=st.columns(2)
    for i,t in enumerate(tables):
        d=qdf(f"SELECT * FROM {t}")
        with csv_cols[i%2]:
            st.download_button(f"📥 {t}.csv",d.to_csv(index=False).encode("utf-8"),f"{t}.csv","text/csv",use_container_width=True)
    conn.close()
    try:
        db_bytes=Path(DB_FILE).read_bytes()
        st.download_button("🗄️ Download Full SQLite Database Backup",db_bytes,f"navrang_vyapar_backup_{dt.datetime.now().strftime('%Y%m%d_%H%M')}.db","application/x-sqlite3",use_container_width=True)
    except FileNotFoundError: st.warning("Database file not found.")

st.markdown('<div class="nv-footer">Navrang Masala • Simple for daily use, powerful for business control</div>',unsafe_allow_html=True)
