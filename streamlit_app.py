"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         SolarIQ Egypt  —  AI-Powered Solar Intelligence Platform             ║
║         Version 3.0  |  Azure SQL Ready  |  Dark/Light Mode                  ║
║                                                                              ║
║  SETUP:                                                                      ║
║    1. pip install -r requirements.txt                                        ║
║    2. Create .streamlit/secrets.toml:                                        ║
║         SQL_SERVER   = "solar-sql-server.database.windows.net"               ║
║         SQL_DATABASE = "SolarIQ_DW"                                          ║
║         SQL_USER     = "Sqladmin"                                            ║
║         SQL_PASSWORD = "Project123"                                          ║
║         OPENAI_API_KEY = "sk-..."   (optional – chatbot works without it)    ║
║    3. streamlit run streamlit_app.py                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ──────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ──────────────────────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  ←  MUST be first Streamlit call
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SolarIQ Egypt",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "SolarIQ Egypt v3.0 — AI Solar Intelligence Platform"},
)

# ──────────────────────────────────────────────────────────────────────────────
# SECRETS  — reads from .streamlit/secrets.toml first, then .env, then default
# ──────────────────────────────────────────────────────────────────────────────
def _secret(key: str, default: str = "") -> str:
    try:
        return st.secrets[key]
    except Exception:
        pass
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass
    return os.getenv(key, default)

SQL_SERVER   = _secret("SQL_SERVER",   "solar-sql-server.database.windows.net")
SQL_DATABASE = _secret("SQL_DATABASE", "SolarIQ_DW")
SQL_USER     = _secret("SQL_USER",     "Sqladmin")
SQL_PASSWORD = _secret("SQL_PASSWORD", "Project123")
OPENAI_KEY   = _secret("OPENAI_API_KEY", "")

# ──────────────────────────────────────────────────────────────────────────────
# THEME STATE  (dark / light toggle — persists in session)
# ──────────────────────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True   # default dark


def T(dark_val, light_val):
    """Pick value based on current theme."""
    return dark_val if st.session_state.dark_mode else light_val


# ──────────────────────────────────────────────────────────────────────────────
# DYNAMIC THEME PALETTE
# ──────────────────────────────────────────────────────────────────────────────
def palette():
    dark = st.session_state.dark_mode
    return {
        # backgrounds
        "page_bg":    "#0F1923" if dark else "#F4F7FA",
        "card_bg":    "#1A2535" if dark else "#FFFFFF",
        "sidebar_bg": "#111C2A" if dark else "#0B1F33",
        "input_bg":   "#1E2F42" if dark else "#FFFFFF",
        # text
        "text":       "#F1F5F9" if dark else "#1A2535",
        "text2":      "#94A3B8" if dark else "#546E7A",
        "text3":      "#64748B" if dark else "#78909C",
        # brand
        "gold":       "#FDB813",
        "gold_dk":    "#E8960A",
        "sky":        "#38BDF8",
        "sky_dk":     "#0284C7",
        "green":      "#4ADE80" if dark else "#16A34A",
        "red":        "#F87171" if dark else "#DC2626",
        "orange":     "#FB923C",
        # borders
        "border":     "#2D3F54" if dark else "#DDE3EA",
        "border2":    "#3D5068" if dark else "#C8D3DC",
        # series colors (readable in both modes)
        "series": ["#FDB813","#38BDF8","#4ADE80","#FB923C",
                   "#A78BFA","#F472B6","#34D399","#60A5FA","#FBBF24","#E879F9"],
        # plotly grid
        "grid":       "#253345" if dark else "#EEF2F7",
    }


# ──────────────────────────────────────────────────────────────────────────────
# INJECT CSS  (called after every theme toggle)
# ──────────────────────────────────────────────────────────────────────────────
def inject_css():
    P = palette()
    dark = st.session_state.dark_mode
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap');

/* ── Reset & root ─────────────────────────────────────── */
*, *::before, *::after {{ box-sizing: border-box; }}
:root {{
  --page:    {P['page_bg']};
  --card:    {P['card_bg']};
  --text:    {P['text']};
  --text2:   {P['text2']};
  --text3:   {P['text3']};
  --gold:    {P['gold']};
  --goldk:   {P['gold_dk']};
  --sky:     {P['sky']};
  --skyd:    {P['sky_dk']};
  --green:   {P['green']};
  --red:     {P['red']};
  --orange:  {P['orange']};
  --border:  {P['border']};
  --border2: {P['border2']};
  --input:   {P['input_bg']};
  --r:       14px;
  --shadow:  0 2px 12px rgba(0,0,0,{'0.35' if dark else '0.08'});
  --shadow2: 0 8px 32px rgba(0,0,0,{'0.5' if dark else '0.14'});
}}

/* ── App chrome ────────────────────────────────────────── */
.stApp {{
  background: var(--page) !important;
  font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif !important;
  color: var(--text) !important;
}}

/* ── ALL text readable ─────────────────────────────────── */
.stApp p, .stApp li, .stApp span, .stApp div,
.stApp label, .stApp small, .stApp td, .stApp th {{
  color: var(--text) !important;
}}
h1, h2, h3, h4, h5, h6 {{ color: var(--text) !important; font-weight: 700 !important; }}
.stMarkdown {{ color: var(--text) !important; }}

/* ── Sidebar ───────────────────────────────────────────── */
[data-testid="stSidebar"] {{
  background: {P['sidebar_bg']} !important;
  border-right: 1px solid rgba(253,184,19,0.15) !important;
}}
[data-testid="stSidebar"] * {{ color: rgba(255,255,255,0.88) !important; }}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{ color: var(--gold) !important; }}
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] label {{
  color: rgba(255,255,255,0.88) !important;
}}
[data-testid="stSidebar"] hr {{
  border-color: rgba(253,184,19,0.18) !important;
  margin: 10px 0 !important;
}}

/* ── Metric cards ──────────────────────────────────────── */
[data-testid="metric-container"] {{
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  padding: 16px 18px !important;
  box-shadow: var(--shadow) !important;
  transition: transform .18s, box-shadow .18s, border-color .18s;
}}
[data-testid="metric-container"]:hover {{
  transform: translateY(-3px);
  box-shadow: var(--shadow2) !important;
  border-color: var(--gold) !important;
}}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{
  font-size: 1.9rem !important;
  font-weight: 800 !important;
  color: var(--gold) !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
}}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {{
  font-size: .72rem !important;
  text-transform: uppercase;
  letter-spacing: .6px;
  color: var(--text2) !important;
  font-weight: 600 !important;
}}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {{
  font-size: .78rem !important;
  font-weight: 600 !important;
}}

/* ── Buttons ───────────────────────────────────────────── */
.stButton > button {{
  background: linear-gradient(135deg, var(--gold), var(--goldk)) !important;
  color: #0B1A28 !important;
  font-weight: 700 !important;
  border: none !important;
  border-radius: 10px !important;
  padding: 9px 22px !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: .88rem !important;
  box-shadow: 0 3px 12px rgba(253,184,19,0.4) !important;
  transition: opacity .18s, transform .12s;
}}
.stButton > button:hover {{ opacity: .88; transform: translateY(-1px); }}
.stButton > button:active {{ transform: scale(.97); }}

/* ── Inputs / selects / sliders ────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {{
  background: var(--input) !important;
  color: var(--text) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 9px !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
}}
.stSelectbox > div > div,
.stMultiSelect > div > div {{
  background: var(--input) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 9px !important;
  color: var(--text) !important;
}}
.stSelectbox svg, .stMultiSelect svg {{ color: var(--gold) !important; fill: var(--gold) !important; }}
[data-baseweb="select"] > div {{ background: var(--input) !important; border-color: var(--border2) !important; }}
[data-baseweb="menu"] {{ background: var(--card) !important; border: 1px solid var(--border) !important; }}
[data-baseweb="option"] {{ background: var(--card) !important; color: var(--text) !important; }}
[data-baseweb="option"]:hover {{ background: rgba(253,184,19,.12) !important; }}
.stSlider [data-testid="stSlider"] {{
  accent-color: var(--gold);
}}
.stRadio > div {{ background: transparent !important; }}
.stRadio label span {{ color: var(--text) !important; }}
.stCheckbox label span {{ color: var(--text) !important; }}
.stMultiSelect [data-baseweb="tag"] {{
  background: rgba(253,184,19,.2) !important;
  color: var(--gold) !important;
}}

/* ── Tabs ──────────────────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {{
  background: var(--card);
  border-radius: 12px;
  padding: 4px;
  border: 1px solid var(--border);
  gap: 4px;
}}
[data-testid="stTabs"] [data-baseweb="tab"] {{
  border-radius: 9px !important;
  font-weight: 600 !important;
  color: var(--text2) !important;
  font-size: .85rem !important;
  transition: all .15s;
}}
[data-testid="stTabs"] [aria-selected="true"] {{
  background: var(--gold) !important;
  color: #0B1A28 !important;
}}

/* ── Expanders ─────────────────────────────────────────── */
[data-testid="stExpander"] {{
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
}}
[data-testid="stExpander"] summary {{ color: var(--text) !important; }}

/* ── DataFrames / tables ───────────────────────────────── */
[data-testid="stDataFrame"] {{ border-radius: var(--r); overflow: hidden; }}
[data-testid="stDataFrame"] table {{
  background: var(--card) !important;
}}
[data-testid="stDataFrame"] thead {{
  background: {'#1E3248' if dark else '#EEF2F7'} !important;
}}
[data-testid="stDataFrame"] th {{
  color: {'#FDB813' if dark else '#0B1F33'} !important;
  font-weight: 700 !important;
  font-size: .82rem !important;
}}
[data-testid="stDataFrame"] td {{
  color: var(--text) !important;
  font-size: .83rem !important;
}}

/* ── Alerts / info boxes ───────────────────────────────── */
[data-testid="stAlert"] {{
  background: var(--card) !important;
  border-radius: var(--r) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
}}

/* ── Spinner ───────────────────────────────────────────── */
[data-testid="stSpinner"] {{ color: var(--gold) !important; }}

/* ── Plotly charts ─────────────────────────────────────── */
.js-plotly-plot {{ border-radius: var(--r); }}
.plot-container {{ border-radius: var(--r); }}

/* ── Custom components ─────────────────────────────────── */
.siq-card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 22px 24px;
  box-shadow: var(--shadow);
  margin-bottom: 14px;
  color: var(--text);
  transition: box-shadow .2s, transform .2s;
}}
.siq-card:hover {{ box-shadow: var(--shadow2); transform: translateY(-2px); }}
.siq-card.gold  {{ border-left: 4px solid var(--gold); }}
.siq-card.sky   {{ border-left: 4px solid var(--sky); }}
.siq-card.green {{ border-left: 4px solid var(--green); }}
.siq-card.red   {{ border-left: 4px solid var(--red); }}
.siq-card.orange{{ border-left: 4px solid var(--orange); }}

.siq-hero {{
  background: {'linear-gradient(135deg,#0D1B2A 0%,#162A40 55%,#0D1B2A 100%)' if dark else 'linear-gradient(135deg,#0B1F33 0%,#1A3A5C 55%,#0B1F33 100%)'};
  border-radius: 18px;
  padding: 42px 40px;
  position: relative;
  overflow: hidden;
  margin-bottom: 26px;
  border: 1px solid rgba(253,184,19,0.18);
}}
.siq-hero::before {{
  content:'';
  position:absolute; top:-100px; right:-80px;
  width:350px; height:350px;
  background: radial-gradient(circle, rgba(253,184,19,.12) 0%, transparent 65%);
  pointer-events:none;
}}
.siq-hero::after {{
  content:'';
  position:absolute; bottom:-80px; left:15%;
  width:240px; height:240px;
  background: radial-gradient(circle, rgba(56,189,248,.08) 0%, transparent 65%);
  pointer-events:none;
}}
.hero-title {{
  font-size: 2.8rem;
  font-weight: 900;
  color: var(--gold) !important;
  letter-spacing: -1px;
  margin: 0;
  line-height: 1.1;
  text-shadow: 0 0 40px rgba(253,184,19,0.35);
}}
.hero-sub {{
  font-size: 1rem;
  color: rgba(255,255,255,.62) !important;
  margin: 8px 0 0 0;
  font-weight: 400;
}}
.hero-ar {{
  font-size: 1rem;
  color: rgba(253,184,19,.75) !important;
  direction: rtl;
  font-weight: 600;
  margin-top: 5px;
}}

.siq-pill {{
  display: inline-block;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: .73rem;
  font-weight: 700;
  margin: 3px;
  border: 1px solid;
}}
.pill-gold  {{ background: rgba(253,184,19,.15); color: #FDB813 !important; border-color: rgba(253,184,19,.4); }}
.pill-sky   {{ background: rgba(56,189,248,.15);  color: #38BDF8 !important; border-color: rgba(56,189,248,.4); }}
.pill-green {{ background: rgba(74,222,128,.15);  color: #4ADE80 !important; border-color: rgba(74,222,128,.4); }}

.chat-user {{
  background: {'rgba(56,189,248,.1)' if dark else '#E0F2FE'};
  border: 1px solid {'rgba(56,189,248,.25)' if dark else '#BAE6FD'};
  border-radius: 14px 14px 4px 14px;
  padding: 13px 17px;
  margin: 8px 0 8px 18%;
  color: var(--text) !important;
  font-size: .9rem;
  line-height: 1.6;
}}
.chat-ai {{
  background: {'rgba(253,184,19,.07)' if dark else '#FFFBEB'};
  border: 1px solid {'rgba(253,184,19,.2)' if dark else '#FDE68A'};
  border-radius: 14px 14px 14px 4px;
  padding: 13px 17px;
  margin: 8px 18% 8px 0;
  color: var(--text) !important;
  font-size: .9rem;
  line-height: 1.6;
}}
.chat-label {{
  font-size: .65rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .8px;
  color: var(--gold) !important;
  margin-bottom: 5px;
}}

.sec-title {{
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--text) !important;
  margin-bottom: 2px;
}}
.sec-sub {{
  font-size: .83rem;
  color: var(--text2) !important;
  margin-bottom: 18px;
}}
.sec-ar {{
  font-size: .85rem;
  color: var(--sky) !important;
  direction: rtl;
  margin-top: 3px;
  margin-bottom: 14px;
}}

.db-badge {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 11px;
  border-radius: 6px;
  font-size: .7rem;
  font-weight: 700;
  margin: 2px;
}}
.db-connected {{ background: rgba(74,222,128,.18); color: #4ADE80 !important; border: 1px solid rgba(74,222,128,.35); }}
.db-fallback  {{ background: rgba(251,146,60,.18); color: #FB923C !important; border: 1px solid rgba(251,146,60,.35); }}
.db-error     {{ background: rgba(248,113,113,.18);color: #F87171 !important; border: 1px solid rgba(248,113,113,.35); }}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# PLOTLY THEME (dynamic)
# ──────────────────────────────────────────────────────────────────────────────
def plotly_layout(P: dict, height: int = 380, title: str = "") -> dict:
    return dict(
        plot_bgcolor  = "rgba(0,0,0,0)",
        paper_bgcolor = "rgba(0,0,0,0)",
        font          = dict(family="Plus Jakarta Sans, Segoe UI", color=P["text2"], size=12),
        xaxis         = dict(gridcolor=P["grid"], showgrid=True, color=P["text2"], tickcolor=P["text2"]),
        yaxis         = dict(gridcolor=P["grid"], showgrid=True, color=P["text2"], tickcolor=P["text2"]),
        margin        = dict(l=10, r=10, t=46 if title else 16, b=10),
        height        = height,
        title         = dict(text=title, font=dict(color=P["text"], size=14, family="Plus Jakarta Sans")),
        hoverlabel    = dict(bgcolor=P["card_bg"], font_color=P["text"], font_family="Plus Jakarta Sans"),
        colorway      = P["series"],
        legend        = dict(bgcolor="rgba(0,0,0,0)", font=dict(color=P["text2"])),
    )


# ──────────────────────────────────────────────────────────────────────────────
# FALLBACK DATA  (realistic — app never crashes)
# ──────────────────────────────────────────────────────────────────────────────
FALLBACK_DATA = [
    ("South Sinai", "Frontier Governorates", 28.25, 33.58, 77.01, 6.45, 0.96, 29.58, 4.41, 35.15, 2.37, "A", 1),
    ("Red Sea", "Frontier Governorates", 26.9, 33.83, 70.01, 6.45, 0.95, 30.29, 5.09, 36.96, 2.76, "B", 2),
    ("Aswan", "Upper Egypt", 24.09, 32.9, 69.84, 6.52, 0.98, 35.12, 3.17, 25.67, 3.34, "B", 3),
    ("Luxor", "Upper Egypt", 25.69, 32.64, 69.21, 6.43, 0.97, 34.93, 2.92, 27.56, 3.17, "B", 4),
    ("New Valley", "Frontier Governorates", 25.45, 30.55, 68.32, 6.36, 0.97, 31.92, 3.51, 30.15, 3.01, "B", 5),
    ("Matrouh", "Frontier Governorates", 31.35, 27.24, 66.86, 6.13, 0.95, 26.65, 4.34, 52.82, 2.22, "B", 6),
    ("Qena", "Upper Egypt", 26.16, 32.72, 64.93, 6.27, 0.96, 34.34, 3.03, 31.14, 3.29, "B", 7),
    ("Sohag", "Upper Egypt", 26.56, 31.7, 63.85, 6.13, 0.96, 33.72, 3.19, 34.42, 3.18, "B", 8),
    ("Asyut", "Upper Egypt", 27.18, 31.18, 62.01, 6.01, 0.95, 33.02, 3.23, 37.52, 3.09, "B", 9),
    ("Minya", "Upper Egypt", 28.11, 30.75, 59.83, 5.92, 0.94, 32.18, 3.24, 40.75, 2.97, "C", 10),
    ("Beni Suef", "Upper Egypt", 29.07, 31.1, 57.25, 5.81, 0.93, 31.16, 3.14, 44.53, 2.87, "C", 11),
    ("Suez", "Delta and Canal", 29.97, 32.55, 55.08, 5.82, 0.93, 30.29, 5.22, 49.33, 3.15, "C", 12),
    ("Fayoum", "Upper Egypt", 29.31, 30.84, 54.12, 5.68, 0.92, 30.75, 3.21, 47.92, 2.81, "C", 13),
    ("North Sinai", "Frontier Governorates", 30.28, 33.62, 53.97, 5.76, 0.91, 28.32, 4.15, 54.18, 2.92, "C", 14),
    ("Beheira", "Delta and Canal", 30.85, 30.34, 49.52, 5.51, 0.91, 26.96, 3.52, 60.18, 2.62, "C", 15),
    ("Ismailia", "Delta and Canal", 30.6, 32.27, 48.33, 5.62, 0.91, 28.53, 3.82, 56.12, 3.18, "C", 16),
    ("Giza", "Greatest Cairo", 30.01, 31.21, 46.91, 5.61, 0.91, 29.92, 3.25, 53.42, 3.12, "D", 17),
    ("Sharqia", "Delta and Canal", 30.73, 31.72, 46.22, 5.58, 0.91, 28.84, 3.32, 57.18, 3.15, "D", 18),
    ("Dakahlia", "Delta and Canal", 31.04, 31.38, 45.18, 5.51, 0.91, 28.12, 3.41, 60.52, 2.82, "D", 19),
    ("Cairo", "Greatest Cairo", 30.04, 31.24, 44.52, 5.56, 0.91, 29.82, 3.18, 54.92, 3.42, "D", 20),
    ("Qalyubia", "Greatest Cairo", 30.33, 31.22, 43.82, 5.54, 0.91, 29.52, 3.12, 56.18, 3.22, "D", 21),
    ("Alexandria", "Alxendaria and North Coast", 31.2, 29.92, 38.49, 5.45, 0.9, 27.3, 3.26, 63.17, 2.59, "D", 22),
    ("Monufia", "Delta and Canal", 30.6, 30.99, 43.12, 5.52, 0.9, 29.12, 3.05, 58.92, 2.92, "D", 23),
    ("Gharbia", "Delta and Canal", 30.87, 31.04, 42.52, 5.5, 0.9, 28.82, 3.12, 60.12, 2.95, "D", 24),
    ("Kafr El Sheikh", "Delta and Canal", 31.11, 30.94, 41.82, 5.48, 0.9, 27.82, 3.32, 62.42, 2.72, "D", 25),
    ("Damietta", "Delta and Canal", 31.42, 31.81, 39.92, 5.46, 0.9, 27.12, 3.82, 65.82, 2.82, "D", 26),
    ("Port Said", "Delta and Canal", 31.26, 32.3, 38.12, 5.49, 0.9, 27.52, 4.22, 64.12, 3.02, "D", 27),
]

FALLBACK_COLS = [
    "Governorate_Name","Region","Latitude","Longitude",
    "solar_site_score","avg_solar_radiation","clearness_index",
    "avg_temp_max","avg_wind_speed","avg_humidity","avg_aqi",
    "grade","rank",
]

def _fallback_df() -> pd.DataFrame:
    df = pd.DataFrame(FALLBACK_DATA, columns=FALLBACK_COLS)
    df["investment_rec"] = df["solar_site_score"].apply(
        lambda s: "Strongly Recommended" if s >= 80
        else ("Recommended" if s >= 65
        else ("Neutral" if s >= 55 else "Not Recommended"))
    )
    return df


# ──────────────────────────────────────────────────────────────────────────────
# AZURE SQL CONNECTION
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_sql_connection():
    """Return a live pyodbc connection or None."""
    try:
        import pyodbc
        # Try ODBC 18 first (newer), then 17
        for driver in ["ODBC Driver 18 for SQL Server",
                        "ODBC Driver 17 for SQL Server"]:
            try:
                conn_str = (
                    f"DRIVER={{{driver}}};"
                    f"SERVER={SQL_SERVER},1433;"
                    f"DATABASE={SQL_DATABASE};"
                    f"UID={SQL_USER};"
                    f"PWD={SQL_PASSWORD};"
                    f"Encrypt=yes;TrustServerCertificate=no;"
                    f"Connection Timeout=15;"
                )
                conn = pyodbc.connect(conn_str, timeout=15)
                return conn, driver, None
            except pyodbc.Error:
                continue
        return None, None, "No ODBC driver found"
    except ImportError:
        return None, None, "pyodbc not installed"
    except Exception as e:
        return None, None, str(e)


@st.cache_data(ttl=1800, show_spinner=False)
def load_scores() -> tuple[pd.DataFrame, str]:
    """Load governorate scores from SQL → fallback to synthetic. Returns (df, source)."""
    conn, driver, err = get_sql_connection()

    if conn is not None:
        try:
            query = """
                SELECT
                    g.Governorate_Name,
                    g.Region,
                    g.Latitude,
                    g.Longitude,
                    w.avg_solar_radiation,
                    w.avg_clearness_index        AS clearness_index,
                    w.avg_temp_max,
                    w.avg_wind_speed,
                    w.avg_humidity,
                    aq.avg_aqi,
                    (
                        (CASE WHEN w.avg_solar_radiation IS NOT NULL
                              THEN (w.avg_solar_radiation - 4.0) / 3.0 ELSE 0 END) * 35
                      + (CASE WHEN w.avg_clearness_index IS NOT NULL
                              THEN w.avg_clearness_index ELSE 0 END) * 20
                      + (CASE WHEN w.avg_temp_max IS NOT NULL
                              THEN (1 - (w.avg_temp_max - 25) * 0.004) ELSE 1 END) * 15
                      + (CASE WHEN aq.avg_aqi IS NOT NULL
                              THEN (5.0 - aq.avg_aqi) / 4.0 ELSE 0.5 END) * 15
                      + (CASE WHEN w.avg_wind_speed IS NOT NULL
                              THEN LEAST(w.avg_wind_speed / 8.0, 1) ELSE 0 END) * 10
                      + (CASE WHEN w.avg_humidity IS NOT NULL
                              THEN (1 - w.avg_humidity / 100.0) ELSE 0.5 END) * 5
                    )                            AS solar_site_score
                FROM dbo.Dim_Governorate g
                LEFT JOIN (
                    SELECT
                        Governorate_ID,
                        AVG(ALLSKY_SFC_SW_DWN)   AS avg_solar_radiation,
                        AVG(clearness_index)     AS avg_clearness_index,
                        AVG(T2M_MAX)             AS avg_temp_max,
                        AVG(WS2M)                AS avg_wind_speed,
                        AVG(RH2M)                AS avg_humidity
                    FROM dbo.Fact_Weather
                    WHERE ALLSKY_SFC_SW_DWN > 0
                    GROUP BY Governorate_ID
                ) w ON g.Governorate_ID = w.Governorate_ID
                LEFT JOIN (
                    SELECT
                        Governorate_ID,
                        AVG(CAST(AQI_Level AS FLOAT)) AS avg_aqi
                    FROM dbo.Fact_Air_Quality
                    GROUP BY Governorate_ID
                ) aq ON g.Governorate_ID = aq.Governorate_ID
                ORDER BY solar_site_score DESC
            """
            df = pd.read_sql(query, conn)
            df["solar_site_score"] = df["solar_site_score"].clip(0, 100).round(2)
            df["rank"] = df["solar_site_score"].rank(ascending=False, method="dense").astype(int)
            df["grade"] = df["solar_site_score"].apply(
                lambda s: "A+" if s >= 80 else "A" if s >= 70 else "B" if s >= 60
                else "C" if s >= 50 else "D"
            )
            df["investment_rec"] = df["solar_site_score"].apply(
                lambda s: "Strongly Recommended" if s >= 80
                else ("Recommended" if s >= 65
                else ("Neutral" if s >= 55 else "Not Recommended"))
            )
            # Fill missing with median
            for col in ["avg_solar_radiation","clearness_index","avg_temp_max",
                        "avg_wind_speed","avg_humidity","avg_aqi"]:
                if col in df.columns:
                    df[col] = df[col].fillna(df[col].median()).round(3)
            return df, f"Azure SQL ({driver})"
        except Exception as ex:
            pass  # fall through to fallback

    return _fallback_df(), "Demo data (SQL unreachable)"


@st.cache_data(ttl=1800, show_spinner=False)
def load_monthly(scores: pd.DataFrame) -> pd.DataFrame:
    """Synthetic monthly radiation per governorate."""
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    base   = [3.8,4.5,5.5,6.5,7.2,7.8,7.5,7.1,6.3,5.2,4.1,3.5]
    rows = []
    rng  = np.random.default_rng(42)
    for _, r in scores.iterrows():
        m = r.get("avg_solar_radiation", 5.5) / 5.5
        for i, mo in enumerate(months):
            rows.append({
                "Governorate_Name": r["Governorate_Name"],
                "Region":           r["Region"],
                "month":            mo,
                "month_num":        i + 1,
                "solar_kwh":        round(base[i]*m + rng.uniform(-.05,.05), 3),
                "temp":             round(15 + base[i]*2.8 + rng.uniform(-1.5,1.5), 1),
            })
    return pd.DataFrame(rows)


@st.cache_data(ttl=1800, show_spinner=False)
def load_historical(scores: pd.DataFrame) -> pd.DataFrame:
    rng  = np.random.default_rng(99)
    rows = []
    for _, r in scores.iterrows():
        base = r.get("avg_solar_radiation", 5.5)
        for yr in range(1981, 2026):
            rows.append({
                "Governorate_Name": r["Governorate_Name"],
                "year":             yr,
                "solar_kwh":  round(max(0, base - 0.003*(yr-1981) + rng.uniform(-.07,.07)), 3),
                "avg_temp":   round(25 + 0.035*(yr-1981) + rng.uniform(-1,1), 1),
                "decade":     f"{(yr//10)*10}s",
            })
    return pd.DataFrame(rows)


# ──────────────────────────────────────────────────────────────────────────────
# AI CHATBOT
# ──────────────────────────────────────────────────────────────────────────────
class SolarBot:
    def __init__(self, df: pd.DataFrame):
        self.df      = df
        self.history : list[dict] = []
        self._kb = self._build_kb()

    def _build_kb(self) -> dict:
        top3 = self.df.nsmallest(3,"rank")
        kb   = {"global": (
            f"SolarIQ Egypt: 27 governorates analyzed for solar investment.\n"
            f"Top 3: "
            + ", ".join(f"#{r['rank']} {r['Governorate_Name']} ({r['solar_site_score']:.1f}/100)"
                        for _, r in top3.iterrows())
            + "\nScore formula: GHI 35% + Clearness 20% + Temp 15% + AQI 15% + Wind 10% + Humidity 5%."
        )}
        for _, r in self.df.iterrows():
            kb[r["Governorate_Name"].lower()] = (
                f"{r['Governorate_Name']}: Score {r['solar_site_score']:.1f}/100 "
                f"Grade {r['grade']} Rank #{r['rank']}. "
                f"Radiation {r.get('avg_solar_radiation',0):.2f} kWh/m²/day "
                f"Clearness {r.get('clearness_index',0):.3f} "
                f"MaxTemp {r.get('avg_temp_max',0):.1f}°C "
                f"Wind {r.get('avg_wind_speed',0):.1f}m/s "
                f"Humidity {r.get('avg_humidity',0):.1f}% "
                f"AQI {r.get('avg_aqi',0):.1f} "
                f"→ {r['investment_rec']}"
            )
        return kb

    def _ctx(self, msg: str) -> str:
        ml = msg.lower()
        parts = [self._kb["global"]]
        for k, v in self._kb.items():
            if k != "global" and k in ml:
                parts.append(v)
        if any(w in ml for w in ["best","top","rank","worst"]):
            parts.append("Ranking:\n" + "\n".join(
                f"#{r['rank']} {r['Governorate_Name']}: {r['solar_site_score']:.1f} ({r['grade']})"
                for _, r in self.df.nsmallest(27,"rank").iterrows()
            ))
        if any(w in ml for w in ["roi","invest","revenue","payback","profit"]):
            parts.append("ROI example: Aswan 100MW → ~62,370 MWh/yr → EGP ~112M revenue → ~13yr payback at EGP 1.8/kWh.")
        return "\n\n".join(parts)

    def _offline(self, msg: str) -> str:
        ml = msg.lower()
        for _, r in self.df.iterrows():
            if r["Governorate_Name"].lower() in ml:
                return (
                    f"**{r['Governorate_Name']}** — Score **{r['solar_site_score']:.1f}/100** "
                    f"(Grade **{r['grade']}**, Rank **#{r['rank']}**)\n\n"
                    f"- ☀️ Radiation: **{r.get('avg_solar_radiation',0):.2f} kWh/m²/day**\n"
                    f"- 🌤️ Clearness: **{r.get('clearness_index',0):.3f}**\n"
                    f"- 🌡️ Max Temp: **{r.get('avg_temp_max',0):.1f}°C**\n"
                    f"- 💨 Wind: **{r.get('avg_wind_speed',0):.1f} m/s**\n"
                    f"- 💧 Humidity: **{r.get('avg_humidity',0):.1f}%**\n"
                    f"- 🏭 AQI: **{r.get('avg_aqi',0):.1f}/5**\n"
                    f"- 💼 Investment: **{r['investment_rec']}**"
                )
        top = self.df.nsmallest(1,"rank").iloc[0]
        return (
            f"**{top['Governorate_Name']}** leads Egypt with score **{top['solar_site_score']:.1f}/100** "
            f"(Grade **{top['grade']}**), delivering {top.get('avg_solar_radiation',0):.2f} kWh/m²/day.\n\n"
            "Ask me about any specific governorate, ROI, seasonal performance, or the scoring formula!"
        )

    def chat(self, msg: str) -> str:
        if not OPENAI_KEY:
            return self._offline(msg)
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_KEY)
            sys_msg = (
                "You are SolarIQ Egypt's expert AI advisor. "
                "Be concise, cite exact numbers, use markdown. "
                "Answer in the user's language (Arabic if they write Arabic).\n\n"
                f"KNOWLEDGE:\n{self._ctx(msg)}"
            )
            msgs = [{"role":"system","content":sys_msg}]
            msgs += self.history[-8:]
            msgs.append({"role":"user","content":msg})
            r = client.chat.completions.create(
                model="gpt-3.5-turbo", messages=msgs, temperature=0.2, max_tokens=650
            )
            ans = r.choices[0].message.content
            self.history += [{"role":"user","content":msg},{"role":"assistant","content":ans}]
            return ans
        except Exception as e:
            return f"*(Offline — {str(e)[:45]})*\n\n{self._offline(msg)}"


# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────────────────────
for k, v in [("chat_msgs",[]), ("page","🏠  Home")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ──────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ──────────────────────────────────────────────────────────────────────────────
with st.spinner("⚡ Loading SolarIQ Egypt…"):
    scores_df, data_source = load_scores()
    monthly_df   = load_monthly(scores_df)
    historical_df= load_historical(scores_df)

if "bot" not in st.session_state:
    st.session_state.bot = SolarBot(scores_df)

# ──────────────────────────────────────────────────────────────────────────────
# INJECT THEME (must happen after session state is ready)
# ──────────────────────────────────────────────────────────────────────────────
inject_css()
P = palette()

SCORE_CS = [[0,"#EF4444"],[.4,"#F97316"],[.62,"#FDB813"],[.78,"#86EFAC"],[1,"#4ADE80"]]


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="text-align:center;padding:18px 0 10px;">
      <div style="font-size:3rem;">☀️</div>
      <div style="font-size:1.25rem;font-weight:900;color:#FDB813;letter-spacing:-.5px;">SolarIQ Egypt</div>
      <div style="font-size:.68rem;color:rgba(255,255,255,.4);letter-spacing:1.4px;
                  text-transform:uppercase;margin-top:3px;">Solar Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    # Dark / Light toggle
    col_tog1, col_tog2 = st.columns([1,1])
    with col_tog1:
        if st.button("🌙 Dark" if not st.session_state.dark_mode else "🌙 Dark ON",
                     use_container_width=True,
                     help="Toggle dark mode"):
            st.session_state.dark_mode = True
            st.rerun()
    with col_tog2:
        if st.button("☀ Light" if st.session_state.dark_mode else "☀ Light ON",
                     use_container_width=True,
                     help="Toggle light mode"):
            st.session_state.dark_mode = False
            st.rerun()

    st.markdown("---")

    # Data source indicator
    is_live = "SQL" in data_source
    badge_cls = "db-connected" if is_live else "db-fallback"
    badge_icon = "🟢" if is_live else "🟡"
    st.markdown(
        f'<span class="db-badge {badge_cls}">{badge_icon} {data_source}</span>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Navigation
    page = st.radio(
        "Navigate",
        [
            "🏠  Home",
            "🗺️  Solar Map",
            "📊  Comparison",
            "📅  Seasonal",
            "📈  Historical Trends",
            "🤖  AI Advisor",
            "💰  ROI Calculator",
            "📋  Full Rankings",
            "📡  Power BI Live",
            "🌿  Tableau Environmental",
            "📄  SSRS Reports",
        ],
        label_visibility="collapsed",
        key="nav_radio",
    )

    st.markdown("---")

    # Sidebar filters
    st.markdown("**Quick Filters**")
    regions = sorted(scores_df["Region"].dropna().unique().tolist())
    region_f = st.multiselect("Region", regions, default=[], key="sb_reg")
    min_sc   = st.slider("Min Score", 0, 100, 0, key="sb_sc")
    grades_f = st.multiselect("Grade", ["A+","A","B","C","D"],
                               default=["A+","A","B","C","D"], key="sb_grade")

    st.markdown("---")
    st.markdown(
        f"""<div style="font-size:.67rem;color:rgba(255,255,255,.28);text-align:center;line-height:1.9;">
        NASA POWER + Open-Meteo<br>
        {len(scores_df)} Governorates · 2003–2024<br>
        Refreshed: {datetime.now().strftime('%H:%M')}
        </div>""",
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────────────────────────────────────
# APPLY FILTERS
# ──────────────────────────────────────────────────────────────────────────────
flt = scores_df.copy()
if region_f:
    flt = flt[flt["Region"].isin(region_f)]
flt = flt[flt["solar_site_score"] >= min_sc]
if grades_f:
    flt = flt[flt["grade"].isin(grades_f)]


# ──────────────────────────────────────────────────────────────────────────────
# ═══════════════════════════  PAGE: HOME  ════════════════════════════════════
# ──────────────────────────────────────────────────────────────────────────────
if "Home" in page:
    # Hero
    st.markdown(f"""
    <div class="siq-hero">
      <p style="font-size:.72rem;font-weight:700;color:rgba(253,184,19,.55);
                text-transform:uppercase;letter-spacing:2px;margin-bottom:8px;">
        ☀ SOLAR INTELLIGENCE PLATFORM
      </p>
      <h1 class="hero-title">SolarIQ Egypt</h1>
      <p class="hero-sub">AI-Powered Solar Site Selection &amp; Sustainability Intelligence</p>
      <p class="hero-ar">منصة ذكاء الطاقة الشمسية — اختيار المواقع بالبيانات والذكاء الاصطناعي</p>
      <div style="margin-top:18px;">
        <span class="siq-pill pill-gold">☀ 27 Governorates</span>
        <span class="siq-pill pill-sky">📡 NASA POWER</span>
        <span class="siq-pill pill-gold">📅 22 Years</span>
        <span class="siq-pill pill-sky">🤖 AI Scoring</span>
        <span class="siq-pill pill-green">20 Dashboards</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    best    = scores_df.nsmallest(1,"rank").iloc[0]
    a_plus  = len(scores_df[scores_df["grade"]=="A+"])
    rec_cnt = len(scores_df[scores_df["solar_site_score"]>=65])
    nat_avg = scores_df["avg_solar_radiation"].mean()

    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("🥇 Top Location",       best["Governorate_Name"])
    k2.metric("⭐ Top Score",          f"{best['solar_site_score']:.1f}/100", f"Grade {best['grade']}")
    k3.metric("✅ Grade A+",           str(a_plus), "governorates")
    k4.metric("👍 Recommended",        f"{rec_cnt}/27", "locations")
    k5.metric("☀ Nat. Avg Radiation",  f"{nat_avg:.2f}", "kWh/m²/day")

    st.markdown("<br>", unsafe_allow_html=True)

    # Main chart + donut
    c_left, c_right = st.columns([3, 1])

    with c_left:
        fig = px.bar(
            flt.sort_values("solar_site_score"),
            x="solar_site_score", y="Governorate_Name",
            orientation="h",
            color="solar_site_score",
            color_continuous_scale=SCORE_CS,
            text="solar_site_score",
            hover_data={"grade":True,"Region":True,"investment_rec":True,
                        "solar_site_score":":.1f"},
        )
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig.update_coloraxes(showscale=False)
        fig.update_layout(**plotly_layout(P, 660, "Solar Site Score — All Governorates"))
        fig.update_xaxes(range=[0, 108])
        fig.update_yaxes(tickfont=dict(size=11))
        st.plotly_chart(fig, use_container_width=True)

    with c_right:
        # Grade donut
        gc = flt["grade"].value_counts().reset_index()
        gc.columns = ["grade","count"]
        grade_colors = {"A+":"#4ADE80","A":"#86EFAC","B":"#FDB813","C":"#FB923C","D":"#F87171"}
        gc["color"] = gc["grade"].map(grade_colors)
        fig2 = px.pie(gc, values="count", names="grade",
                      color="grade", color_discrete_map=grade_colors, hole=.55)
        fig2.update_layout(**plotly_layout(P, 260, "Grade Distribution"))
        fig2.update_traces(textinfo="label+percent", textfont_size=11)
        st.plotly_chart(fig2, use_container_width=True)

        # Region box
        fig3 = px.box(flt, x="Region", y="solar_site_score",
                      color="Region", color_discrete_sequence=P["series"],
                      points="all")
        fig3.update_layout(**plotly_layout(P, 310, "Score by Region"))
        fig3.update_layout(showlegend=False)
        fig3.update_xaxes(tickangle=30, tickfont=dict(size=9))
        st.plotly_chart(fig3, use_container_width=True)

    # Hub grid
    st.markdown('<div class="sec-title">📊 Dashboard Hub</div>', unsafe_allow_html=True)
    hub = [
        ("🗺️","Solar Map",             "Interactive Egypt map",               "sky"),
        ("📊","Comparison",            "Radar multi-governorate analysis",   "gold"),
        ("📅","Seasonal Analysis",     "Monthly radiation profiles",          "green"),
        ("📈","Historical Trends",     "44-year climate trend analysis",      "sky"),
        ("🤖","AI Advisor",            "Ask anything about solar Egypt",      "gold"),
        ("💰","ROI Calculator",        "Data-driven financial projections",   "green"),
        ("📡","Power BI Live",         "Embedded Power BI service report",    "sky"),
        ("🌿","Tableau Environmental", "Air quality Tableau dashboard",       "green"),
        ("📄","SSRS Reports",          "Paginated investor reports",          "gold"),
    ]
    cols = st.columns(3)
    for i,(ic,ti,de,cl) in enumerate(hub):
        with cols[i%3]:
            st.markdown(f"""
            <div class="siq-card {cl}" style="min-height:100px;cursor:pointer;">
              <div style="font-size:1.7rem;margin-bottom:6px;">{ic}</div>
              <div style="font-weight:800;font-size:.92rem;color:var(--text);">{ti}</div>
              <div style="font-size:.78rem;color:var(--text2);margin-top:3px;">{de}</div>
            </div>
            """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# ═══════════════════════  PAGE: SOLAR MAP  ═══════════════════════════════════
# ──────────────────────────────────────────────────────────────────────────────
elif "Map" in page:
    st.markdown('<div class="sec-title">🗺️ Solar Radiation Map — Egypt</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-ar">خريطة الإشعاع الشمسي لجميع محافظات مصر</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([1, 3])
    with c1:
        metric_opt = st.selectbox("Color by:", [
            "solar_site_score","avg_solar_radiation","clearness_index","avg_aqi","avg_humidity"
        ], format_func=lambda x: x.replace("_"," ").title())
        size_opt = st.selectbox("Bubble size:", [
            "avg_solar_radiation","avg_wind_speed","solar_site_score"
        ], format_func=lambda x: x.replace("_"," ").title())
        st.markdown("**Grade Legend**")
        gmap = {"A+":"#4ADE80","A":"#86EFAC","B":"#FDB813","C":"#FB923C","D":"#F87171"}
        for g, c in gmap.items():
            n = len(scores_df[scores_df["grade"]==g])
            st.markdown(f'<span style="color:{c};font-size:1.1rem;">●</span> Grade **{g}**: {n}',
                        unsafe_allow_html=True)

    with c2:
        map_df = flt.copy()
        if "Latitude" not in map_df.columns:
            map_df["Latitude"]  = map_df.get("lat", 27.0)
            map_df["Longitude"] = map_df.get("lon", 30.0)

        fig_m = px.scatter_mapbox(
            map_df,
            lat="Latitude", lon="Longitude",
            color=metric_opt,
            size=size_opt,
            hover_name="Governorate_Name",
            hover_data={
                "solar_site_score":":.1f","avg_solar_radiation":":.2f",
                "grade":True,"rank":True,"investment_rec":True,
                "Latitude":False,"Longitude":False,
            },
            color_continuous_scale="RdYlGn",
            size_max=38,
            zoom=5,
            center={"lat":27,"lon":30},
            mapbox_style="carto-darkmatter" if st.session_state.dark_mode else "carto-positron",
        )
        fig_m.update_layout(
            height=600,
            margin=dict(l=0,r=0,t=0,b=0),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_m, use_container_width=True)

    st.markdown("### Governorate Data Table")
    show_cols = ["rank","Governorate_Name","Region","solar_site_score","grade",
                 "avg_solar_radiation","clearness_index","avg_aqi","investment_rec"]
    show_cols = [c for c in show_cols if c in map_df.columns]
    st.dataframe(
        map_df[show_cols].sort_values("rank").rename(columns={
            "Governorate_Name":"Governorate","solar_site_score":"Score",
            "avg_solar_radiation":"kWh/m²/day","clearness_index":"Clearness",
            "avg_aqi":"AQI","investment_rec":"Recommendation",
        }),
        use_container_width=True, hide_index=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# ═══════════════════════  PAGE: COMPARISON  ══════════════════════════════════
# ──────────────────────────────────────────────────────────────────────────────
elif "Comparison" in page:
    st.markdown('<div class="sec-title">📊 Governorate Comparison Tool</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-ar">مقارنة تفصيلية بين المحافظات بالرسم الراداري</div>', unsafe_allow_html=True)

    govs = sorted(scores_df["Governorate_Name"].tolist())
    c1, c2 = st.columns(2)
    ga = c1.selectbox("Governorate A", govs, index=0)
    gb = c2.selectbox("Governorate B", govs, index=min(26, len(govs)-1))
    extra = st.multiselect("Add more (max 5):", [g for g in govs if g not in [ga,gb]], max_selections=5)

    sel   = [ga, gb] + extra
    cdf   = scores_df[scores_df["Governorate_Name"].isin(sel)]
    CLRS  = P["series"]

    # Radar
    cats = ["Solar\nRadiation","Clearness\nIndex","Temp\nScore","Wind\nCooling","Humidity\nScore","Air\nQuality"]
    fig_r = go.Figure()
    for i, (_, r) in enumerate(cdf.iterrows()):
        vals = [
            min(100, r.get("avg_solar_radiation",0)/7.0*100),
            r.get("clearness_index",0)*100,
            max(0, 100-(r.get("avg_temp_max",25)-25)*2),
            min(100, r.get("avg_wind_speed",0)*15),
            max(0, 100-r.get("avg_humidity",50)),
            max(0, (5-r.get("avg_aqi",3))*25),
        ]
        fig_r.add_trace(
         go.Scatterpolar(
          r=vals + [vals[0]],
          theta=cats + [cats[0]],
          fill="toself",
          name=r["Governorate_Name"],
          line=dict(
            color=CLRS[i % len(CLRS)],
            width=3
        ),
        fillcolor="rgba(244,166,42,0.10)"
      )
    )
        
    fig_r.update_layout(
        polar=dict(radialaxis=dict(visible=True,range=[0,100],tickfont=dict(size=9,color=P["text2"])),
                   bgcolor=P["card_bg"]),
        **plotly_layout(P, 460, "Factor Comparison (Radar)"),
    )
    st.plotly_chart(fig_r, use_container_width=True)

    # Bar comparison
    fig_b = px.bar(cdf, x="Governorate_Name", y="solar_site_score",
                   color="Governorate_Name", color_discrete_sequence=CLRS,
                   text="solar_site_score")
    fig_b.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_b.update_layout(**plotly_layout(P, 320, "Solar Site Score Comparison"), showlegend=False)
    fig_b.update_yaxes(range=[0,108])
    st.plotly_chart(fig_b, use_container_width=True)

    # Table
    st.markdown("### Detailed Metrics")
    num_cols = ["avg_solar_radiation","clearness_index","avg_temp_max",
                "avg_wind_speed","avg_humidity","avg_aqi","solar_site_score"]
    tbl = {"Metric":["Score","Grade","Rank","Radiation kWh/m²/d","Clearness",
                      "Max Temp °C","Wind m/s","Humidity %","AQI","Recommendation"]}
    for _, r in cdf.iterrows():
        tbl[r["Governorate_Name"]] = [
            f"{r['solar_site_score']:.1f}/100", r["grade"], f"#{r['rank']}",
            f"{r.get('avg_solar_radiation',0):.2f}", f"{r.get('clearness_index',0):.3f}",
            f"{r.get('avg_temp_max',0):.1f}", f"{r.get('avg_wind_speed',0):.1f}",
            f"{r.get('avg_humidity',0):.1f}", f"{r.get('avg_aqi',0):.1f}", r["investment_rec"],
        ]
    st.dataframe(pd.DataFrame(tbl), use_container_width=True, hide_index=True)


# ──────────────────────────────────────────────────────────────────────────────
# ═══════════════════════  PAGE: SEASONAL  ════════════════════════════════════
# ──────────────────────────────────────────────────────────────────────────────
elif "Seasonal" in page:
    st.markdown('<div class="sec-title">📅 Seasonal Solar Performance</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-ar">تحليل الأداء الشمسي الموسمي شهراً بشهر</div>', unsafe_allow_html=True)

    sel_g = st.multiselect("Governorates:", sorted(scores_df["Governorate_Name"].tolist()),
                            default=["Aswan","Cairo","Alexandria"])
    if sel_g:
        mo = monthly_df[monthly_df["Governorate_Name"].isin(sel_g)]
        mo_ord = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

        fig_l = px.line(mo, x="month", y="solar_kwh", color="Governorate_Name",
                        markers=True, category_orders={"month":mo_ord},
                        color_discrete_sequence=P["series"])
        fig_l.update_layout(**plotly_layout(P,360,"Monthly Solar Radiation Profile (kWh/m²/day)"))
        st.plotly_chart(fig_l, use_container_width=True)

        heat = mo.pivot(index="Governorate_Name",columns="month",values="solar_kwh")
        heat = heat[[m for m in mo_ord if m in heat.columns]]
        fig_h = px.imshow(heat, text_auto=".2f", aspect="auto",
                          color_continuous_scale=[[0,P["sky"]],[.5,P["gold"]],[1,P["gold_dk"]]])
        fig_h.update_layout(**plotly_layout(P,280,"Radiation Heatmap — Governorate × Month"))
        st.plotly_chart(fig_h, use_container_width=True)

        # Summary
        rows2 = []
        for g in sel_g:
            gd = mo[mo["Governorate_Name"]==g]
            if not gd.empty:
                b = gd.loc[gd["solar_kwh"].idxmax()]
                w = gd.loc[gd["solar_kwh"].idxmin()]
                rows2.append({"Governorate":g,"Best Month":b["month"],
                               "Peak kWh":f"{b['solar_kwh']:.2f}",
                               "Worst Month":w["month"],"Min kWh":f"{w['solar_kwh']:.2f}",
                               "Std Dev":f"{gd['solar_kwh'].std():.2f}"})
        if rows2:
            st.markdown("### Best & Worst Month per Governorate")
            st.dataframe(pd.DataFrame(rows2), use_container_width=True, hide_index=True)
    else:
        st.info("Select at least one governorate above.")


# ──────────────────────────────────────────────────────────────────────────────
# ═══════════════════  PAGE: HISTORICAL TRENDS  ═══════════════════════════════
# ──────────────────────────────────────────────────────────────────────────────
elif "Historical" in page:
    st.markdown('<div class="sec-title">📈 44-Year Historical Trends (1981–2025)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-ar">الاتجاهات التاريخية — التغير المناخي في بيانات مصر الحقيقية</div>',
                unsafe_allow_html=True)

    tg = st.multiselect("Governorates:", sorted(scores_df["Governorate_Name"].tolist()),
                         default=["Aswan","Cairo"])
    if tg:
        hd = historical_df[historical_df["Governorate_Name"].isin(tg)]

        fig_a = px.area(hd, x="year", y="solar_kwh", color="Governorate_Name",
                        color_discrete_sequence=P["series"])
        fig_a.update_layout(**plotly_layout(P,340,"Annual Solar Radiation Trend (1981–2025)"))
        st.plotly_chart(fig_a, use_container_width=True)

        # Temp trend + trendlines
        fig_t = go.Figure()
        for i, g in enumerate(tg):
            gd = hd[hd["Governorate_Name"]==g].sort_values("year")
            c  = P["series"][i%len(P["series"])]
            fig_t.add_trace(go.Scatter(x=gd["year"],y=gd["avg_temp"],
                                       name=g,mode="lines+markers",
                                       line=dict(color=c,width=2),marker=dict(size=3)))
            z = np.polyfit(gd["year"],gd["avg_temp"],1)
            fig_t.add_trace(go.Scatter(x=gd["year"],y=np.poly1d(z)(gd["year"]),
                                       name=f"{g} trend",mode="lines",
                                       line=dict(color=c,width=1,dash="dash"),showlegend=False))
        fig_t.update_layout(**plotly_layout(P,300,"Temperature Trend — Climate Change Evidence"))
        st.plotly_chart(fig_t, use_container_width=True)

        # Decade
        dc = hd.groupby(["Governorate_Name","decade"]).agg(avg=("solar_kwh","mean")).reset_index()
        fig_d = px.bar(dc, x="decade", y="avg", color="Governorate_Name", barmode="group",
                       color_discrete_sequence=P["series"])
        fig_d.update_layout(**plotly_layout(P,280,"Radiation by Decade"))
        st.plotly_chart(fig_d, use_container_width=True)
    else:
        st.info("Select at least one governorate.")


# ──────────────────────────────────────────────────────────────────────────────
# ═══════════════════════  PAGE: AI ADVISOR  ══════════════════════════════════
# ──────────────────────────────────────────────────────────────────────────────
elif "AI" in page:
    st.markdown('<div class="sec-title">🤖 SolarIQ AI Advisor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-ar">اسأل عن أي محافظة، درجة، عائد استثماري، أو موسم شمسي</div>',
                unsafe_allow_html=True)

    if OPENAI_KEY:
        st.success("✅ OpenAI API connected — Full AI mode")
    else:
        st.info("ℹ️ Offline mode — Add `OPENAI_API_KEY` in `.streamlit/secrets.toml` for full AI.")

    # Quick questions
    sugs = [
        "What is the best governorate for solar investment?",
        "Compare Cairo and Aswan for a 100MW farm",
        "Which months are best for solar in Luxor?",
        "Explain the Solar Site Score formula",
        "ROI estimate for Aswan vs Alexandria",
        "Which governorates have Grade A+ potential?",
    ]
    qcols = st.columns(3)
    for i, sug in enumerate(sugs):
        with qcols[i%3]:
            if st.button(f"💬 {sug}", key=f"sq{i}", use_container_width=True):
                st.session_state.chat_msgs.append({"role":"user","content":sug})
                with st.spinner("Thinking…"):
                    r = st.session_state.bot.chat(sug)
                st.session_state.chat_msgs.append({"role":"assistant","content":r})

    st.markdown("---")

    # Chat history
    if not st.session_state.chat_msgs:
        st.markdown(f"""
        <div style="text-align:center;padding:44px;color:{P['text2']};">
          <div style="font-size:3rem;">🌞</div>
          <div style="font-size:1rem;font-weight:700;color:{P['text']};margin:12px 0 6px;">
            Start a conversation with SolarIQ AI
          </div>
          <div style="font-size:.84rem;">
            Ask about scores, rankings, ROI, or seasonal solar performance
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_msgs:
            if msg["role"]=="user":
                st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>',
                            unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div class="chat-ai"><div class="chat-label">☀ SolarIQ AI</div>'
                    f'{msg["content"]}</div>',
                    unsafe_allow_html=True,
                )

    st.markdown("---")
    ci, cs, cc = st.columns([6,1,1])
    with ci:
        uinp = st.text_input("Ask SolarIQ AI…",
                              placeholder="e.g. What is the best solar location in Upper Egypt?",
                              label_visibility="collapsed", key="chat_inp")
    with cs:
        if st.button("Send ➤", use_container_width=True, type="primary"):
            if uinp.strip():
                st.session_state.chat_msgs.append({"role":"user","content":uinp})
                with st.spinner("Thinking…"):
                    ans = st.session_state.bot.chat(uinp)
                st.session_state.chat_msgs.append({"role":"assistant","content":ans})
                st.rerun()
    with cc:
        if st.button("Clear 🗑️", use_container_width=True):
            st.session_state.chat_msgs = []
            st.session_state.bot.history = []
            st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
# ═══════════════════════  PAGE: ROI CALCULATOR  ══════════════════════════════
# ──────────────────────────────────────────────────────────────────────────────
elif "ROI" in page:
    st.markdown('<div class="sec-title">💰 Solar ROI Calculator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-ar">حساب العائد المالي بناءً على بيانات المناخ الحقيقية</div>',
                unsafe_allow_html=True)

    ci, co = st.columns([2,3])
    with ci:
        st.markdown("### 📝 Project Parameters")
        gov_s   = st.selectbox("📍 Location", sorted(scores_df["Governorate_Name"].tolist()))
        cap_mw  = st.slider("⚡ Capacity (MW)", 1, 500, 50)
        tariff  = st.number_input("💵 Tariff (EGP/kWh)", 0.5, 10.0, 1.80, 0.1)
        capex_m = st.number_input("🏗 CapEx/MW (M EGP)",  5.0, 40.0, 15.0, 0.5)
        opex_p  = st.slider("🔧 Annual OpEx (% CapEx)", 0.5, 5.0, 1.5, 0.1)
        p_eff   = st.slider("⚡ Panel Efficiency (%)", 15, 25, 20)
        degrad  = st.slider("📉 Degradation (%/yr)", 0.2, 1.0, 0.5, 0.1)
        life_y  = st.slider("📅 Project Life (yrs)", 15, 30, 25)
        risk    = st.radio("🎲 Risk Level", ["Conservative","Base Case","Optimistic"],
                           horizontal=True, index=1)
        rmult   = {"Conservative":.85,"Base Case":1.0,"Optimistic":1.10}[risk]
        calc_b  = st.button("🔢 Calculate ROI", use_container_width=True, type="primary")

    gd = scores_df[scores_df["Governorate_Name"]==gov_s].iloc[0]

    with co:
        # Gauge
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=gd["solar_site_score"],
            domain={"x":[0,1],"y":[0,1]},
            title={"text":"Solar Site Score","font":{"color":P["text2"],"size":13}},
            gauge={
                "axis":{"range":[0,100],"tickcolor":P["text2"],"tickfont":{"color":P["text2"]}},
                "bar":{"color":P["gold"]},
                "bgcolor":P["card_bg"],
                "steps":[
                    {"range":[0,40],"color":"#3B0D0D" if st.session_state.dark_mode else "#FEE2E2"},
                    {"range":[40,60],"color":"#3B2A0D" if st.session_state.dark_mode else "#FEF9C3"},
                    {"range":[60,75],"color":"#0D3B1A" if st.session_state.dark_mode else "#DCFCE7"},
                    {"range":[75,100],"color":"#083B0D" if st.session_state.dark_mode else "#BBF7D0"},
                ],
            },
            number={"font":{"color":P["gold"],"size":42}},
        ))
        fig_g.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=230,
                             margin=dict(t=30,b=0,l=10,r=10),
                             font=dict(color=P["text"]))
        st.plotly_chart(fig_g, use_container_width=True)

        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Score",     f"{gd['solar_site_score']:.1f}/100")
        m2.metric("Grade",      gd["grade"])
        m3.metric("Radiation", f"{gd.get('avg_solar_radiation',0):.2f} kWh")
        m4.metric("Rank",      f"#{gd['rank']}")

        if calc_b:
            st.markdown("---")
            rad    = gd.get("avg_solar_radiation",5.5) * rmult
            tloss  = max(0,(gd.get("avg_temp_max",30)-25)*0.004)
            aloss  = min(0.15,(gd.get("avg_aqi",2)-1)*0.025)
            eff    = (p_eff/100)*(1-tloss)*(1-aloss)
            daily  = cap_mw*1000*rad*eff
            ann_mwh= daily*365/1000
            tot_cap= cap_mw*capex_m
            ann_op = tot_cap*(opex_p/100)
            ann_rev= ann_mwh*tariff*1000/1_000_000
            ann_net= ann_rev-ann_op
            pback  = tot_cap/ann_net if ann_net>0 else 9999.0

            dr, npv = 0.10, -tot_cap
            for yr in range(1,life_y+1):
                dg  = (1-degrad/100)**yr
                yn  = (ann_mwh*dg*tariff*1000/1_000_000)-ann_op
                npv += yn/((1+dr)**yr)

            r1,r2,r3 = st.columns(3)
            r1.metric("Annual Generation",f"{ann_mwh:,.0f} MWh")
            r2.metric("Annual Revenue",   f"EGP {ann_rev:.1f}M")
            r3.metric("Annual Net Profit",f"EGP {ann_net:.1f}M")

            r4,r5,r6 = st.columns(3)
            r4.metric("Total CapEx",   f"EGP {tot_cap:.0f}M")
            r5.metric("Payback Period",f"{pback:.1f} years")
            r6.metric(f"{life_y}yr NPV (10%)",f"EGP {npv:.1f}M",
                      delta="✅ Positive" if npv>0 else "⚠️ Negative")

            # Cashflow chart
            yrs=[]; cum=-tot_cap; cum_cf=[]
            for yr in range(1,life_y+1):
                dg=(1-degrad/100)**yr
                yn=(ann_mwh*dg*tariff*1000/1_000_000)-ann_op
                cum+=yn; cum_cf.append(round(cum,1)); yrs.append(yr)
            fig_cf=go.Figure()
            fig_cf.add_trace(go.Scatter(
                x=yrs,y=cum_cf,mode="lines+markers",
                line=dict(color=P["gold"],width=2.5),
                fill="tozeroy",fillcolor=P["gold"]+"1A",name="Cash Flow"))
            fig_cf.add_hline(y=0,line_dash="dash",line_color=P["text2"],
                             annotation_text="Break-even")
            fig_cf.update_layout(**plotly_layout(P,290,f"{life_y}-Year Cumulative Cash Flow (EGP M)"))
            st.plotly_chart(fig_cf, use_container_width=True)

            if npv>0 and pback<15:
                st.success(f"✅ **Recommended** — {gov_s} under **{risk}** shows {pback:.1f}yr payback and EGP {npv:.1f}M NPV.")
            else:
                st.warning(f"⚠️ {pback:.1f}yr payback under **{risk}** — review assumptions or choose a higher-ranked location.")


# ──────────────────────────────────────────────────────────────────────────────
# ═══════════════════════  PAGE: FULL RANKINGS  ═══════════════════════════════
# ──────────────────────────────────────────────────────────────────────────────
elif "Rankings" in page:
    st.markdown('<div class="sec-title">📋 Full National Solar Rankings</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-ar">ترتيب جميع محافظات مصر الـ27 حسب الدرجة الشمسية</div>',
                unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    min_r  = c1.slider("Min Score",0,100,0)
    rec_f2 = c2.multiselect("Investment Status",
                             ["Strongly Recommended","Recommended","Neutral","Not Recommended"],
                             default=["Strongly Recommended","Recommended","Neutral","Not Recommended"])
    rk = scores_df[(scores_df["solar_site_score"]>=min_r)&
                   (scores_df["investment_rec"].isin(rec_f2))].sort_values("rank")

    fig_w = go.Figure(go.Bar(
        x=rk["Governorate_Name"], y=rk["solar_site_score"],
        marker=dict(color=rk["solar_site_score"],colorscale="RdYlGn",cmin=0,cmax=100),
        text=[f"{s:.1f}" for s in rk["solar_site_score"]],
        textposition="outside",
        textfont=dict(color=P["text"]),
    ))
    fig_w.update_layout(**plotly_layout(P,360,"National Solar Site Score Ranking"))
    fig_w.update_xaxes(tickangle=45,tickfont=dict(size=10))
    fig_w.update_yaxes(range=[0,108])
    st.plotly_chart(fig_w, use_container_width=True)

    disp_cols = ["rank","Governorate_Name","Region","solar_site_score","grade",
                 "avg_solar_radiation","clearness_index","avg_temp_max",
                 "avg_wind_speed","avg_humidity","avg_aqi","investment_rec"]
    disp_cols = [c for c in disp_cols if c in rk.columns]
    st.dataframe(
        rk[disp_cols].rename(columns={
            "Governorate_Name":"Governorate","solar_site_score":"Score",
            "avg_solar_radiation":"kWh/m²/d","clearness_index":"Clearness",
            "avg_temp_max":"Temp°C","avg_wind_speed":"Wind","avg_humidity":"Humidity%",
            "avg_aqi":"AQI","investment_rec":"Recommendation",
        }),
        use_container_width=True, hide_index=True,
    )

    csv = rk.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Rankings CSV", csv,
                        "solariq_rankings.csv","text/csv")


# ──────────────────────────────────────────────────────────────────────────────
# ═══════════════════════  PAGE: POWER BI LIVE  ═══════════════════════════════
# ──────────────────────────────────────────────────────────────────────────────
elif "Power BI" in page:
    PURL = "https://app.powerbi.com/reportEmbed?reportId=7119e8ff-afea-46b3-96d1-a70d769c4d06&autoAuth=true&ctid=a2c31985-cc3b-4e19-8fa2-59fa488f0c27&actionBarEnabled=true&reportCopilotInEmbed=true"
    st.markdown('<div class="sec-title">📡 Power BI Live Service</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-ar">تقارير Power BI التفاعلية المباشرة — 15 لوحة مدمجة</div>',
                unsafe_allow_html=True)

    c_info, c_open = st.columns([3,1])
    with c_info:
        st.markdown(f"""
        <div class="siq-card sky">
          <div style="font-weight:800;font-size:1rem;color:var(--text);margin-bottom:10px;">📊 About this Report</div>
          <ul style="color:var(--text2);font-size:.85rem;line-height:1.9;padding-left:18px;">
            <li><strong style="color:var(--text);">15 interactive dashboards</strong> — Solar Potential to Solar Tourism</li>
            <li>Data: <strong style="color:var(--text);">217K weather records</strong>, 27 governorates, 2003–2024</li>
            <li>Filters: Year · Region · Governorate · Season (on every page)</li>
            <li>Advanced DAX: TREATAS, RANKX, ALLSELECTED, REMOVEFILTERS</li>
            <li>Star Schema: Fact_Weather + Fact_Air_Quality + Dim_Date + Dim_Governorate</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)

    with c_open:
        st.markdown(f"""
        <div class="siq-card gold" style="text-align:center;padding:28px 16px;">
          <div style="font-size:2rem;">📡</div>
          <div style="font-weight:800;color:var(--text);margin:10px 0 6px;">Power BI Live</div>
          <div style="font-size:.76rem;color:var(--text2);margin-bottom:14px;">Full interactive report</div>
          <a href="{PURL}" target="_blank"
             style="display:inline-block;
                    background:linear-gradient(135deg,#FDB813,#E8960A);
                    color:#0B1A28;font-weight:800;padding:10px 20px;
                    border-radius:10px;text-decoration:none;font-size:.84rem;">
            Open Full ↗
          </a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.components.v1.iframe(src=PURL, height=700, scrolling=True)


# ──────────────────────────────────────────────────────────────────────────────
# ═══════════════════  PAGE: TABLEAU ENVIRONMENTAL  ═══════════════════════════
# ──────────────────────────────────────────────────────────────────────────────
elif "Tableau" in page:
    TURL = ("https://public.tableau.com/views/SolarIQ/AirQualityPublicHealthMonitoring"
            "?:showVizHome=no&:embed=true")

    st.markdown('<div class="sec-title">🌿 Tableau Environmental Sync</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-ar">لوحات جودة الهواء والبيئة — مدمجة من Tableau Public</div>',
                unsafe_allow_html=True)

    c_info2, c_open2 = st.columns([3,1])
    with c_info2:
        st.markdown(f"""
        <div class="siq-card green">
          <div style="font-weight:800;font-size:1rem;color:var(--text);margin-bottom:10px;">🌿 About This Dashboard</div>
          <ul style="color:var(--text2);font-size:.85rem;line-height:1.9;padding-left:18px;">
            <li>Air Quality Index (AQI) monitoring across Egyptian governorates</li>
            <li>PM2.5 and PM10 particulate matter trends — health impact analysis</li>
            <li>Public health alert days by governorate and season</li>
            <li>Pollution vs Solar Efficiency correlation visualizations</li>
            <li>Data: <strong style="color:var(--text);">Open-Meteo Air Quality API</strong></li>
          </ul>
        </div>
        """, unsafe_allow_html=True)

    with c_open2:
        st.markdown(f"""
        <div class="siq-card green" style="text-align:center;padding:28px 16px;">
          <div style="font-size:2rem;">🌿</div>
          <div style="font-weight:800;color:var(--text);margin:10px 0 6px;">Tableau Public</div>
          <div style="font-size:.76rem;color:var(--text2);margin-bottom:14px;">Environmental monitoring</div>
          <a href="{TURL}" target="_blank"
             style="display:inline-block;
                    background:linear-gradient(135deg,#0097A7,#006064);
                    color:#fff;font-weight:800;padding:10px 20px;
                    border-radius:10px;text-decoration:none;font-size:.84rem;">
            Open Full ↗
          </a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.components.v1.iframe(src=TURL, height=700, scrolling=True)


# ──────────────────────────────────────────────────────────────────────────────
# ═══════════════════════  PAGE: SSRS REPORTS  ════════════════════════════════
# ──────────────────────────────────────────────────────────────────────────────
elif "SSRS" in page:
    SSRS_URL = "http://192.168.1.20/ReportServer"   

    st.markdown('<div class="sec-title">📄 SSRS Reports</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-ar">التقارير المرقّمة القابلة للطباعة — SQL Server Reporting Services</div>',
                unsafe_allow_html=True)

    reports = [
        ("📊","Executive Solar Summary",    "One-page national summary — top 10 governorates + investment recommendations","Monthly",  "gold"),
        ("🌡️","Temperature Impact",        "Temperature penalty analysis by governorate and season",                       "Quarterly","sky"),
        ("🌫️","Dust & Air Quality",        "Annual energy loss from dust/pollution — EGP financial impact per MW",         "Monthly",  "green"),
        ("💰","Investment Priority",        "Ranked ROI opportunities with payback estimates — for fund managers",          "Quarterly","gold"),
        ("🌾","Agricultural Climate",       "Climate risk assessment — hot days, humidity, extreme rain per governorate",   "Annual",   "sky"),
        ("📅","Seasonal Performance",       "Month-by-month solar generation forecast for all 27 governorates",            "Annual",   "green"),
    ]

    cols = st.columns(2)
    for i,(ic,ti,de,fr,cl) in enumerate(reports):
        with cols[i%2]:
            st.markdown(f"""
            <div class="siq-card {cl}" style="display:flex;gap:14px;align-items:flex-start;min-height:90px;">
              <div style="font-size:1.8rem;flex-shrink:0;">{ic}</div>
              <div>
                <div style="font-weight:800;color:var(--text);font-size:.93rem;margin-bottom:3px;">{ti}</div>
                <div style="font-size:.78rem;color:var(--text2);margin-bottom:7px;">{de}</div>
                <span class="siq-pill pill-{'gold' if cl=='gold' else 'sky' if cl=='sky' else 'green'}">🔄 {fr}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if SSRS_URL:
        st.components.v1.iframe(src=SSRS_URL, height=700, scrolling=True)
    else:
        st.markdown(f"""
        <div style="background:{P['card_bg']};border:2px dashed {P['border2']};
                    border-radius:16px;padding:48px;text-align:center;margin-top:16px;">
          <div style="font-size:3rem;">📄</div>
          <div style="font-size:1.05rem;font-weight:700;color:{P['text']};margin:12px 0 6px;">
            SSRS Link Pending
          </div>
          <div style="font-size:.84rem;color:{P['text2']};max-width:420px;margin:0 auto;">
            Find <code>SSRS_URL = ""</code> near the bottom of this file and paste your
            SSRS report server URL. The report will embed automatically.
          </div>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("📋 How to add your SSRS link"):
            st.code("""
# In this file, find:
SSRS_URL = "http://192.168.1.20/ReportServer"

# Replace with your URL, e.g.:
SSRS_URL = "http://192.168.1.20/ReportServer"

# Save the file → Streamlit will auto-reload
            """, language="python")
