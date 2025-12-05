import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION & THEME ---
st.set_page_config(page_title="Analytics Dashboard", layout="wide")

st.markdown("""
<style>
/* --------------------------------
   1. FONTS & GLOBAL RESET
-------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* --------------------------------
   2. DYNAMIC ANIMATED BACKGROUND
   - flowing radial gradients
   - 25s smooth animation
-------------------------------- */
.stApp {
    background:
        radial-gradient(ellipse at 10% 0%, rgba(255, 102, 0, 0.09), transparent 55%),
        radial-gradient(ellipse at 90% 100%, rgba(255, 102, 0, 0.08), transparent 55%),
        radial-gradient(circle at 50% 50%, rgba(16, 16, 24, 1), #000000);
    background-attachment: fixed;
    color: #F8FAFC;
    min-height: 100vh;
    position: relative;
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background:
        radial-gradient(circle at 20% 30%, rgba(255, 102, 0, 0.06), transparent 45%),
        radial-gradient(circle at 80% 70%, rgba(255, 102, 0, 0.05), transparent 45%);
    animation: bgFlow 25s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
}

@keyframes bgFlow {
    0% {
        opacity: 0.4;
        transform: scale(1) translate3d(0, 0, 0);
    }
    50% {
        opacity: 0.7;
        transform: scale(1.06) translate3d(12px, -10px, 0);
    }
    100% {
        opacity: 0.4;
        transform: scale(1) translate3d(0, 0, 0);
    }
}

/* Main content container */
.main .block-container {
    padding: 2.6rem 3rem !important;
    max-width: 1500px !important;
    position: relative;
    z-index: 1;
}

/* --------------------------------
   3. PREMIUM TITLE ANIMATION
   - blur → focus, glow, accents
-------------------------------- */
.main h1 {
    position: relative;
    display: inline-block;
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.04em !important;
    margin-bottom: 0.6rem !important;

    background: linear-gradient(135deg, #FFFFFF 0%, #FF6600 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;

    opacity: 0;
    filter: blur(6px);
    transform: translateY(-10px) scale(0.96);
    text-shadow:
        0 0 22px rgba(0, 0, 0, 0.9),
        0 0 28px rgba(255, 102, 0, 0.5);
    animation: titleReveal 1s cubic-bezier(0.19, 1, 0.22, 1) forwards;
}

@keyframes titleReveal {
    0% {
        opacity: 0;
        filter: blur(6px);
        transform: translateY(-10px) scale(0.96);
    }
    60% {
        opacity: 1;
        filter: blur(0px);
        transform: translateY(2px) scale(1.04);
    }
    100% {
        opacity: 1;
        filter: blur(0px);
        transform: translateY(0) scale(1);
    }
}

/* Left accent bar */
.main h1::before {
    content: "";
    position: absolute;
    left: -12px;
    top: 22%;
    width: 3px;
    height: 56%;
    background: linear-gradient(180deg, #FF6600, transparent);
    box-shadow: 0 0 18px rgba(255, 102, 0, 0.9);
    transform-origin: bottom;
    transform: scaleY(0);
    animation: titleBar 0.7s 0.25s cubic-bezier(0.19, 1, 0.22, 1) forwards;
}

/* Right underline */
.main h1::after {
    content: "";
    position: absolute;
    left: 0;
    bottom: -10px;
    width: 70px;
    height: 3px;
    background: linear-gradient(90deg, #FF6600, transparent);
    border-radius: 999px;
    box-shadow: 0 0 18px rgba(255, 102, 0, 0.8);
    transform-origin: left;
    transform: scaleX(0);
    animation: titleLine 0.6s 0.4s cubic-bezier(0.19, 1, 0.22, 1) forwards;
}

@keyframes titleBar {
    0% { transform: scaleY(0); opacity: 0; }
    100% { transform: scaleY(1); opacity: 1; }
}

@keyframes titleLine {
    0% { transform: scaleX(0); }
    100% { transform: scaleX(1); }
}

/* Subtext under title */
.main p {
    color: #94A3B8 !important;
    font-size: 0.94rem !important;
    line-height: 1.7 !important;
}

/* Section headings */
.main h2, .main h3 {
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #F8FAFC !important;
    margin-top: 2rem !important;
    margin-bottom: 1rem !important;
}

/* --------------------------------
   4. NEXT-LEVEL KPI CARDS
   - glassmorphism
   - staggered float-in
   - animated borders
-------------------------------- */
div[data-testid="metric-container"] {
    background: radial-gradient(circle at 0 0,
        rgba(31, 31, 45, 0.98),
        rgba(5, 5, 10, 0.98));
    border-radius: 20px;
    padding: 1.6rem 1.5rem !important;
    border: 1px solid rgba(255, 255, 255, 0.07);
    box-shadow:
        0 26px 70px rgba(0, 0, 0, 0.98),
        0 0 0 1px rgba(15, 23, 42, 0.9);
    backdrop-filter: blur(18px);
    position: relative;
    overflow: hidden;

    opacity: 0;
    transform: translateY(18px) scale(0.95) rotateX(5deg);
    animation: metricFloat 0.7s cubic-bezier(0.19, 1, 0.22, 1) forwards;
}

/* Stagger animation for 4 KPIs */
div[data-testid="metric-container"]:nth-of-type(1) { animation-delay: 0.15s; }
div[data-testid="metric-container"]:nth-of-type(2) { animation-delay: 0.25s; }
div[data-testid="metric-container"]:nth-of-type(3) { animation-delay: 0.35s; }
div[data-testid="metric-container"]:nth-of-type(4) { animation-delay: 0.45s; }

@keyframes metricFloat {
    0% {
        opacity: 0;
        transform: translateY(18px) scale(0.93) rotateX(8deg);
    }
    65% {
        opacity: 1;
        transform: translateY(-3px) scale(1.02) rotateX(0deg);
    }
    100% {
        opacity: 1;
        transform: translateY(0) scale(1) rotateX(0deg);
    }
}

/* Animated gradient border overlay */
div[data-testid="metric-container"]::before {
    content: "";
    position: absolute;
    inset: -1px;
    border-radius: inherit;
    padding: 1px;
    background: conic-gradient(
        from 180deg,
        rgba(255, 102, 0, 0.9),
        rgba(255, 255, 255, 0.12),
        rgba(255, 102, 0, 0.4),
        rgba(255, 102, 0, 0.9)
    );
    -webkit-mask: 
        linear-gradient(#000 0 0) content-box, 
        linear-gradient(#000 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    opacity: 0;
    animation: borderSweep 5s linear infinite;
    pointer-events: none;
}

@keyframes borderSweep {
    0%   { opacity: 0.08; transform: rotate(0deg); }
    50%  { opacity: 0.25; transform: rotate(180deg); }
    100% { opacity: 0.08; transform: rotate(360deg); }
}

/* Diagonal shine on hover */
div[data-testid="metric-container"]::after {
    content: "";
    position: absolute;
    top: -140%;
    left: -60%;
    width: 220%;
    height: 220%;
    background: linear-gradient(
        130deg,
        transparent 0%,
        rgba(255, 255, 255, 0.20) 18%,
        rgba(255, 255, 255, 0.05) 55%,
        transparent 100%
    );
    opacity: 0;
    transform: translate3d(-15%, 0, 0);
    transition: opacity 0.6s ease-out, transform 0.8s ease-out;
    pointer-events: none;
}

div[data-testid="metric-container"]:hover::after {
    opacity: 1;
    transform: translate3d(8%, 0, 0);
}

/* 3D hover lift */
div[data-testid="metric-container"]:hover {
    transform: translateY(-4px) scale(1.02) rotateX(0deg);
    border-color: rgba(255, 102, 0, 0.7);
    box-shadow:
        0 32px 80px rgba(0, 0, 0, 1),
        0 0 0 1px rgba(255, 102, 0, 0.65);
}

/* Metric label & value */
div[data-testid="stMetricLabel"] {
    font-size: 0.76rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.14em !important;
    color: #9CA3AF !important;
}

div[data-testid="stMetricValue"] {
    font-size: 2.1rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    background: linear-gradient(135deg, #FFFFFF 0%, #FF6600 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow:
        0 0 18px rgba(255, 102, 0, 0.6),
        0 0 30px rgba(0, 0, 0, 1);
    animation: valuePulse 3s ease-in-out infinite;
}

@keyframes valuePulse {
    0%   { text-shadow: 0 0 14px rgba(255, 102, 0, 0.6); }
    50%  { text-shadow: 0 0 26px rgba(255, 102, 0, 0.9); }
    100% { text-shadow: 0 0 14px rgba(255, 102, 0, 0.6); }
}

div[data-testid="stMetricDelta"] {
    font-size: 0.78rem !important;
    color: #A5B4FC !important;
}

/* --------------------------------
   5. FUTURISTIC TABS
-------------------------------- */
.stTabs [data-baseweb="tab-list"] {
    width: 100%;
    gap: 0.6rem;
    background: rgba(7, 7, 12, 0.85);
    padding: 0.55rem;
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: 0 18px 50px rgba(0, 0, 0, 0.9);
}

.stTabs [data-baseweb="tab"] {
    flex-grow: 1;
    height: 48px;
    padding: 0 1.4rem;
    border-radius: 10px;
    border: none;
    background: transparent;
    color: #9CA3AF;
    font-weight: 600;
    font-size: 0.78rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;

    position: relative;
    overflow: hidden;

    transition:
        color 0.18s cubic-bezier(0.19, 1, 0.22, 1),
        background 0.18s cubic-bezier(0.19, 1, 0.22, 1),
        transform 0.18s cubic-bezier(0.19, 1, 0.22, 1),
        box-shadow 0.18s cubic-bezier(0.19, 1, 0.22, 1),
        border-color 0.18s cubic-bezier(0.19, 1, 0.22, 1);
}

/* Hover radial orange glow */
.stTabs [data-baseweb="tab"]::before {
    content: "";
    position: absolute;
    inset: -40%;
    background: radial-gradient(circle at 20% 0,
        rgba(255, 102, 0, 0.23),
        transparent 65%);
    opacity: 0;
    transform: scale(0.75);
    transition: opacity 0.25s ease-out, transform 0.25s ease-out;
    pointer-events: none;
}

.stTabs [data-baseweb="tab"]:hover::before {
    opacity: 0.7;
    transform: scale(1);
}

.stTabs [data-baseweb="tab"]:hover {
    color: #FFFFFF;
    background: rgba(255, 255, 255, 0.02);
    transform: translateY(-1px);
    box-shadow: 0 16px 45px rgba(0, 0, 0, 0.9);
}

/* Active tab */
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(
        135deg,
        rgba(255, 102, 0, 0.28),
        rgba(0, 0, 0, 1)
    );
    color: #FF6600;
    box-shadow:
        0 20px 55px rgba(0, 0, 0, 1),
        0 0 0 1px rgba(255, 102, 0, 0.9);
    transform: translateY(-1px) scale(1.01);
}

/* Pulsing bottom line */
.stTabs [data-baseweb="tab"][aria-selected="true"]::after {
    content: "";
    position: absolute;
    left: 16%;
    right: 16%;
    bottom: -3px;
    height: 2px;
    background: linear-gradient(90deg, transparent, #FF6600, transparent);
    box-shadow: 0 0 16px rgba(255, 102, 0, 0.9);
    animation: tabPulse 1.4s ease-in-out infinite alternate;
}

@keyframes tabPulse {
    0%   { opacity: 0.5; transform: scaleX(0.93); }
    100% { opacity: 1;   transform: scaleX(1.05); }
}

/* --------------------------------
   6. ENHANCED INFO BOXES (st.info)
-------------------------------- */
.stAlert {
    background: radial-gradient(circle at 0 0,
        rgba(15, 23, 42, 1),
        rgba(0, 0, 0, 1));
    border-radius: 18px;
    border: 1px solid rgba(148, 163, 184, 0.5);
    color: #E5E7EB;
    padding: 1rem 1.1rem !important;
    font-size: 0.86rem !important;
    line-height: 1.6;
    position: relative;
    overflow: hidden;

    box-shadow:
        0 22px 65px rgba(0, 0, 0, 0.98),
        0 0 0 1px rgba(15, 23, 42, 0.95);

    transform: translateX(-10px);
    opacity: 0;
    animation: infoSlide 0.45s ease-out forwards;
}

@keyframes infoSlide {
    0%   { opacity: 0; transform: translateX(-10px); }
    100% { opacity: 1; transform: translateX(0); }
}

/* Pulsing orange left bar */
.stAlert::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: linear-gradient(
        180deg,
        #FF6600,
        rgba(255, 102, 0, 0.05),
        #FF6600
    );
    box-shadow: 0 0 18px rgba(255, 102, 0, 0.9);
    animation: borderGlow 2s ease-in-out infinite alternate;
}

@keyframes borderGlow {
    0%   { opacity: 0.6; }
    100% { opacity: 1; }
}

/* Floating corner glow */
.stAlert::after {
    content: "";
    position: absolute;
    right: -20%;
    top: -20%;
    width: 45%;
    height: 45%;
    background: radial-gradient(circle,
        rgba(255, 255, 255, 0.08),
        transparent 75%);
    opacity: 0.7;
    filter: blur(2px);
}

/* --------------------------------
   7. CHART CONTAINERS (Plotly)
   - glow, lift, frosted glass
-------------------------------- */
div[data-testid="stPlotlyChart"] {
    background: radial-gradient(circle at 0 0,
        rgba(20, 20, 30, 0.98),
        rgba(5, 5, 10, 0.98));
    border-radius: 20px;
    padding: 1.3rem 1.3rem 1.0rem 1.3rem;
    border: 1px solid rgba(255, 255, 255, 0.06);
    box-shadow:
        0 26px 75px rgba(0, 0, 0, 1),
        0 0 0 1px rgba(15, 23, 42, 0.95);
    backdrop-filter: blur(18px);

    position: relative;
    overflow: hidden;
    transition:
        transform 0.2s ease-out,
        box-shadow 0.2s ease-out,
        border-color 0.2s ease-out;
}

/* Subtle orange radial glow */
div[data-testid="stPlotlyChart"]::before {
    content: "";
    position: absolute;
    inset: -20%;
    background: radial-gradient(circle at 0 0,
        rgba(255, 102, 0, 0.24),
        transparent 65%);
    opacity: 0.3;
    mix-blend-mode: screen;
    pointer-events: none;
    transition: opacity 0.25s ease-out, transform 0.25s ease-out;
}

div[data-testid="stPlotlyChart"]:hover::before {
    opacity: 0.55;
    transform: scale(1.03);
}

/* Hover lift + scale */
div[data-testid="stPlotlyChart"]:hover {
    transform: translateY(-3px) scale(1.01);
    box-shadow:
        0 30px 85px rgba(0, 0, 0, 1),
        0 0 0 1px rgba(255, 102, 0, 0.6);
    border-color: rgba(255, 102, 0, 0.9);
}

/* --------------------------------
   8. PREMIUM DATA TABLES
-------------------------------- */
.stDataFrame {
    border-radius: 18px !important;
    overflow: hidden !important;
    box-shadow:
        0 24px 70px rgba(0, 0, 0, 1),
        0 0 0 1px rgba(15, 23, 42, 0.95) !important;
}

.stDataFrame table {
    border-collapse: collapse !important;
    background-color: #020617 !important;
    border: 1px solid rgba(31, 41, 55, 0.9) !important;
}

/* Headers */
.stDataFrame th {
    background: linear-gradient(
        135deg,
        rgba(15, 23, 42, 1),
        rgba(3, 7, 18, 1)
    ) !important;
    color: #E2E8F0 !important;
    font-weight: 700 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.16em !important;
    padding: 0.85rem 1rem !important;
    border-bottom: 1px solid rgba(55, 65, 81, 0.95) !important;
    border-top: 1px solid rgba(255, 102, 0, 0.4) !important;
}

/* Cells */
.stDataFrame td {
    color: #CBD5E1 !important;
    padding: 0.75rem 1rem !important;
    font-size: 0.82rem !important;
    border-bottom: 1px solid rgba(31, 41, 55, 0.9) !important;
}

/* Zebra striping */
.stDataFrame tbody tr:nth-child(even) {
    background-color: #020617 !important;
}
.stDataFrame tbody tr:nth-child(odd) {
    background-color: #030712 !important;
}

/* Row hover: orange side + gentle highlight */
.stDataFrame tbody tr:hover td {
    background: linear-gradient(90deg,
        rgba(255, 102, 0, 0.12),
        rgba(15, 23, 42, 0.98)) !important;
    border-left: 2px solid #FF6600 !important;
}

/* --------------------------------
   9. CUSTOM SCROLLBARS
-------------------------------- */
::-webkit-scrollbar {
    width: 9px;
    height: 9px;
}

::-webkit-scrollbar-track {
    background: #020617;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #FF6600, #7C2D12);
    border-radius: 999px;
    box-shadow: 0 0 10px rgba(255, 102, 0, 0.7);
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #FF6600, #EA580C);
    box-shadow:
        0 0 14px rgba(255, 102, 0, 0.9),
        0 0 22px rgba(0, 0, 0, 0.9);
}
</style>
""", unsafe_allow_html=True)

# --- TOOLTIP DEFINITIONS ---
METRIC_TOOLTIPS = {
    "growth_trend": """
    **Net User Enrollments vs Unique Users**
    
    **Metric:** Comparison of total activity volume versus actual head count.
    
    **Calculation:**
    • **Net Enrollments:** Sum of all course signups (one user can have multiple).
    • **Unique Users:** Count of distinct email addresses active in that month.
    """,
    "mom_growth": """
    **Month-over-Month (MoM) Growth Velocity**
    
    **Metric:** The percentage rate at which your user base is expanding (or shrinking) compared to the previous month.
    
    **Calculation:** ((Current Unique Users - Previous Unique Users) / Previous Unique Users) * 100
    """,
    "unique_users_bar": """
    **Monthly Unique User Signups**
    
    **Metric:** Absolute count of unique users acquired per month (Headcount).
    
    **Why it matters:** Unlike the trend line (which mixes enrollments), this isolates pure user base growth.
    """,
    "geo_users": """
    **Global User Distribution**
    
    **Metric:** Total enrollment volume aggregated by country.
    
    **Calculation:** Sum of 'Total Course Signups' grouped by Country. Filtered by the 'Region' dropdown logic.
    """,
    "popular_courses": """
    **Top 30 Most Popular Courses**
    
    **Metric:** The specific courses driving the most interest.
    
    **Calculation:** Total raw signup count per course, sorted from highest to lowest. Limited to top 30.
    """,
    "badges": """
    **Badges Issued (Certifications)**
    
    **Metric:** Volume of users who successfully completed a course and earned a badge.
    
    **Calculation:** Sum of the 'Number of Badges' column from the Badges Issued sheet, aggregated by month.
    """,
    "completion": """
    **Course Completion Rates**
    
    **Metric:** The percentage of enrolled users who actually finish the material.
    
    **Calculation:** Pre-calculated average from the 'Starter Completion Avg' sheet. 
    (Usually: Badges Issued / Total Enrollments * 100).
    """,
    "segmentation": """
    **User Quality Segmentation**
    
    **Metric:** Breakdown of the user base by email domain quality.
    
    **Calculation:** • **Business:** Professional domains (excluding public providers).
    • **Generic:** Public providers (Gmail, Yahoo, etc.).
    • **Blocked:** Known spam or internal test accounts.
    """,
    "leads": """
    **Marketing Leads Generated**
    
    **Metric:** Top-of-funnel marketing performance tracking new potential customers.
    
    **Calculation:** Sum of 'Number of Leads Gen' from the Leads Generated sheet, aggregated by month.
    """
}

# --- 2. PASSWORD PROTECTION ---
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter Password:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password incorrect.", type="password", on_change=password_entered, key="password")
        return False
    else:
        return True

if check_password():
    # --- 3. DATA LOADING ---
    @st.cache_data
    def load_data():
        # ORIGINAL FILENAME
        file_path = "final_unified_master_with_segments.xlsx"
        try:
            xls = pd.read_excel(file_path, sheet_name=None)
            data = {}
            # Map sheets to keys
            data["Master"] = xls.get("Master")
            data["Monthly_Enroll"] = xls.get("Monthly Enrollments")
            data["Monthly_Unique"] = xls.get("Unique Monthly Users")
            data["Country"] = xls.get("Country Breakdown")
            data["Course"] = xls.get("Course Breakdown")
            data["Completion"] = xls.get("Starter Completion Avg")
            data["Business_Email"] = xls.get("Business Emails")
            data["Generic_Email"] = xls.get("Generic Emails")
            data["Blocked_Email"] = xls.get("Blocked Emails")
            data["Starter_vs_Non"] = xls.get("Starter_vs_NonStarter")
            data["Badges"] = xls.get("Badges Issued")
            data["Leads"] = xls.get("Leads Generated")
            
            # --- CONTINENT MAPPING LOGIC ---
            if data["Country"] is not None:
                country_to_cont = {
                    'ALGERIA': 'Africa', 'EGYPT': 'Africa', 'ESWATINI': 'Africa', 'ETHIOPIA': 'Africa', 
                    'IVORY COAST': 'Africa', 'LESOTHO': 'Africa', 'MOROCCO': 'Africa', 'MOZAMBIQUE': 'Africa', 
                    'NAMIBIA': 'Africa', 'NIGERIA': 'Africa', 'SENEGAL': 'Africa', 'SOUTH AFRICA': 'Africa', 
                    'TANZANIA': 'Africa', 'UGANDA': 'Africa', 'ZAMBIA': 'Africa', 'ZIMBABWE': 'Africa', 
                    'AZERBAIJAN': 'Asia', 'BAHRAIN': 'Asia', 'BANGLADESH': 'Asia', 'BRUNEI': 'Asia', 
                    'HONG KONG': 'Asia', 'INDIA': 'Asia', 'INDONESIA': 'Asia', 'IRAN': 'Asia', 'IRAQ': 'Asia', 
                    'ISRAEL': 'Asia', 'JAPAN': 'Asia', 'JORDAN': 'Asia', 'KUWAIT': 'Asia', 'MALAYSIA': 'Asia', 
                    'NEPAL': 'Asia', 'OMAN': 'Asia', 'PAKISTAN': 'Asia', 'PHILIPPINES': 'Asia', 'QATAR': 'Asia', 
                    'SAUDI ARABIA': 'Asia', 'SINGAPORE': 'Asia', 'SOUTH KOREA': 'Asia', 'SRI LANKA': 'Asia', 
                    'TAIWAN': 'Asia', 'THAILAND': 'Asia', 'TURKEY': 'Asia', 'UNITED ARAB EMIRATES': 'Asia', 
                    'VIETNAM': 'Asia', 'ALBANIA': 'Europe', 'AUSTRIA': 'Europe', 'BELGIUM': 'Europe', 
                    'BULGARIA': 'Europe', 'DENMARK': 'Europe', 'FINLAND': 'Europe', 'FRANCE': 'Europe', 
                    'GERMANY': 'Europe', 'GREECE': 'Europe', 'HUNGARY': 'Europe', 'ICELAND': 'Europe', 
                    'IRELAND': 'Europe', 'ITALY': 'Europe', 'LUXEMBOURG': 'Europe', 'MOLDOVA': 'Europe', 
                    'NETHERLANDS': 'Europe', 'NORTH MACEDONIA': 'Europe', 'NORWAY': 'Europe', 'POLAND': 'Europe', 
                    'PORTUGAL': 'Europe', 'ROMANIA': 'Europe', 'RUSSIA': 'Europe', 'SERBIA': 'Europe', 
                    'SLOVENIA': 'Europe', 'SPAIN': 'Europe', 'SWEDEN': 'Europe', 'SWITZERLAND': 'Europe', 
                    'UKRAINE': 'Europe', 'UNITED KINGDOM': 'Europe', 'BARBADOS': 'North America', 
                    'CANADA': 'North America', 'COSTA RICA': 'North America', 'CURACAO': 'North America', 
                    'GUATEMALA': 'North America', 'MEXICO': 'North America', 'NICARAGUA': 'North America', 
                    'PANAMA': 'North America', 'TRINIDAD AND TOBAGO': 'North America', 'UNITED STATES': 'North America', 
                    'AUSTRALIA': 'Oceania', 'FIJI': 'Oceania', 'GUAM': 'Oceania', 'NEW ZEALAND': 'Oceania', 
                    'BRAZIL': 'South America', 'CHILE': 'South America', 'COLOMBIA': 'South America', 
                    'ECUADOR': 'South America', 'PERU': 'South America'
                }
                data["Country"]["Region"] = data["Country"]["Country"].map(country_to_cont).fillna("Other")

            return data
        except FileNotFoundError:
            st.error(f"Could not find {file_path}. Please upload it to GitHub.")
            return None
        except Exception as e:
            st.error(f"Error reading file: {e}")
            return None

    data = load_data()

    if data:
        # --- 4. DASHBOARD HEADER & KPIs ---
        st.title("Academy Analytics")
        st.markdown(f"*Data updated: {pd.Timestamp.now().strftime('%Y-%m-%d')}*")
        st.markdown("---")

        # Calculate KPIs
        total_enrolls = data["Course"]["Sign Ups"].sum() if data.get("Course") is not None else 0
        total_unique = data["Monthly_Unique"]["Unique User Signups"].sum() if data.get("Monthly_Unique") is not None else 0
        total_badges = data["Badges"]["Number of Badges"].sum() if data.get("Badges") is not None else 0
        total_leads = data["Leads"]["Number of Leads Gen"].sum() if data.get("Leads") is not None else 0

        biz_count = len(data["Business_Email"]) if data.get("Business_Email") is not None else 0
        gen_count = len(data["Generic_Email"]) if data.get("Generic_Email") is not None else 0
        blocked_count = len(data["Blocked_Email"]) if data.get("Blocked_Email") is not None else 0
        
        top_region = "N/A"
        if data.get("Country") is not None:
             top_region = data["Country"].sort_values("Total Course Signups", ascending=False).iloc[0]["Country"]

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Net User Enrollments", f"{total_enrolls:,}")
        kpi2.metric("Unique Users", f"{total_unique:,}")
        kpi3.metric("Badges Issued", f"{total_badges:,}")
        kpi4.metric("Leads Generated", f"{total_leads:,}")

        # --- 5. TABS ---
        tab_growth, tab_geo, tab_content, tab_business = st.tabs(["Growth", "Geography", "Courses", "Business"])

        # TAB 1: GROWTH
        with tab_growth:
            # --- HEADER ---
            st.subheader("Enrollment Trends")
            st.info(METRIC_TOOLTIPS["growth_trend"]) # VISIBLE INFO BOX
            
            if data.get("Monthly_Enroll") is not None and data.get("Monthly_Unique") is not None:
                # 1. Prepare Data
                df_enroll = data["Monthly_Enroll"].copy()
                df_enroll['Month'] = pd.to_datetime(df_enroll['Month'])
                df_unique = data["Monthly_Unique"].copy()
                df_unique['Month'] = pd.to_datetime(df_unique['Month'])
                
                # Merge into one clean table
                df_trend = pd.merge(df_enroll, df_unique, on="Month", how="outer").fillna(0)
                df_trend = df_trend.sort_values("Month")
                
                # --- CALCULATION CHANGE: MoM based on UNIQUE USERS now ---
                df_trend['MoM_Growth'] = df_trend['Unique User Signups'].pct_change() * 100
                
                # Labels & Filters
                df_trend['Month_Label'] = df_trend['Month'].dt.strftime('%b %Y')
                all_months = df_trend['Month_Label'].unique().tolist()
                filter_options = ["All Months"] + all_months
                default_months = df_trend[df_trend['Month'].dt.year >= 2025]['Month_Label'].unique().tolist()
                current_default = default_months if default_months else ["All Months"]

                selected_options = st.multiselect("Select Timeframe:", options=filter_options, default=current_default)
                
                if "All Months" in selected_options:
                    df_filtered = df_trend
                else:
                    df_filtered = df_trend[df_trend['Month_Label'].isin(selected_options)].sort_values("Month")

                if not df_filtered.empty:
                    # Main Chart
                    fig_trend = go.Figure()
                    fig_trend.add_trace(go.Scatter(x=df_filtered['Month'], y=df_filtered['Enrollments'], 
                                                 mode='lines+markers', name='Net User Enrollments',
                                                 line=dict(color='#ff6600', width=3))) 
                    fig_trend.add_trace(go.Scatter(x=df_filtered['Month'], y=df_filtered['Unique User Signups'], 
                                                 mode='lines', name='Unique Users',
                                                 line=dict(color='#ffffff', dash='dot'))) 
                    fig_trend.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                          height=400, margin=dict(l=0, r=0, t=20, b=0))
                    # FIX: Force X-Axis to be monthly ticks
                    fig_trend.update_xaxes(dtick="M1", tickformat="%b %Y")
                    st.plotly_chart(fig_trend, use_container_width=True)
                    
                    # MoM Chart with VISIBLE DEFAULT EXPLANATION
                    st.markdown("#### MoM Growth Rate (%)")
                    st.info(METRIC_TOOLTIPS["mom_growth"]) # VISIBLE INFO BOX
                    
                    fig_mom = go.Figure()
                    fig_mom.add_trace(go.Bar(
                        x=df_filtered['Month'], 
                        y=df_filtered['MoM_Growth'],
                        marker=dict(color=df_filtered['MoM_Growth'].apply(lambda x: '#00cc96' if x >= 0 else '#ef553b')),
                        name='MoM Growth',
                        # --- CUSTOM TOOLTIP LOGIC ---
                        customdata=df_filtered['Unique User Signups'],
                        hovertemplate='%{x|%b %Y}<br>Growth: %{y:.2f}%<br>Users: %{customdata:,} <extra></extra>'
                    ))
                    fig_mom.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300)
                    # FIX: Force X-Axis to be monthly ticks
                    fig_mom.update_xaxes(dtick="M1", tickformat="%b %Y")
                    st.plotly_chart(fig_mom, use_container_width=True)

                    # --- NEW: MONTHLY UNIQUE USER SIGNUPS (HORIZONTAL BAR) ---
                    st.markdown("#### Monthly Unique Signups")
                    st.info(METRIC_TOOLTIPS["unique_users_bar"]) # VISIBLE INFO BOX

                    # Sort for display (chronological)
                    # We use the filtered dataframe which is already sorted by Month
                    fig_unique = px.bar(
                        df_filtered,
                        x='Unique User Signups',
                        y='Month_Label', # Use Label for category
                        orientation='h',
                        text='Unique User Signups'
                    )
                    fig_unique.update_traces(marker_color='#ff6600', textposition='auto')
                    fig_unique.update_layout(
                        template="plotly_dark",
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        height=400,
                        # IMPORTANT: Ensure Y-axis follows the dataframe order (Chronological)
                        yaxis={'categoryorder':'array', 'categoryarray': df_filtered['Month_Label']}
                    )
                    st.plotly_chart(fig_unique, use_container_width=True)

                    st.markdown("### Detailed Data")
                    display_table = df_filtered[['Month_Label', 'Enrollments', 'Unique User Signups', 'MoM_Growth']].rename(
                        columns={'Month_Label': 'Month', 'Enrollments': 'Net User Enrollments', 'MoM_Growth': 'MoM Growth %'}
                    )
                    st.dataframe(display_table.style.format({'MoM Growth %': '{:.2f}%'}), use_container_width=True, hide_index=True)
                else:
                    st.info("Please select 'All Months' or specific months.")

        # TAB 2: GEOGRAPHY
        with tab_geo:
            # --- HEADER ---
            st.subheader("Users by Country")
            st.info(METRIC_TOOLTIPS["geo_users"]) # VISIBLE INFO BOX
            
            if data.get("Country") is not None:
                all_regions = sorted(data["Country"]["Region"].unique().tolist())
                filter_options_geo = ["All"] + all_regions
                selected_regions = st.multiselect("Select Region:", options=filter_options_geo, default=["All"])
                
                if "All" in selected_regions:
                    df_geo_filtered = data["Country"]
                else:
                    df_geo_filtered = data["Country"][data["Country"]["Region"].isin(selected_regions)]

                col_map, col_tree = st.columns([1, 1])
                with col_map:
                    fig_map = px.choropleth(df_geo_filtered, locations="Country", locationmode='country names',
                                            color="Total Course Signups", 
                                            color_continuous_scale=["#1e1e1e", "#ff6600"])
                    fig_map.update_layout(
                        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', 
                        geo=dict(bgcolor='rgba(0,0,0,0)', projection_type="natural earth"),
                        dragmode="pan", height=500, margin=dict(l=0, r=0, t=0, b=0)
                    )
                    st.plotly_chart(fig_map, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': False})
                
                with col_tree:
                    df_tree = df_geo_filtered.sort_values("Total Course Signups", ascending=False).head(30)
                    fig_tree = px.treemap(
                        df_tree, path=['Country'], values='Total Course Signups',
                        color='Total Course Signups', color_continuous_scale=[[0, "#444"], [1, "#ff6600"]]
                    )
                    fig_tree.update_layout(
                        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(t=10, l=10, r=10, b=10), height=500, 
                        shapes=[dict(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=1, y1=1, line=dict(color="#333", width=2))]
                    )
                    fig_tree.update_traces(hovertemplate='<b>%{label}</b><br>Signups: %{value}', marker=dict(line=dict(color='#000000', width=1)))
                    st.plotly_chart(fig_tree, use_container_width=True)
                
                st.markdown("### Detailed Regional Data")
                st.dataframe(df_geo_filtered.sort_values("Total Course Signups", ascending=False), use_container_width=True, hide_index=True)

        # TAB 3: CONTENT
        with tab_content:
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                # --- HEADER ---
                st.subheader("Popular Courses")
                st.info(METRIC_TOOLTIPS["popular_courses"]) # VISIBLE INFO BOX
                
                if data.get("Course") is not None:
                    # --- INCREASED TO TOP 30 ---
                    df_course_top = data["Course"].sort_values("Sign Ups", ascending=False).head(30)
                    
                    fig_course = px.bar(df_course_top, x="Sign Ups", y="Course", orientation='h')
                    fig_course.update_traces(marker_color='#ff6600') 
                    fig_course.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending'}, height=800)
                    st.plotly_chart(fig_course, use_container_width=True)
                    st.markdown("#### All Courses")
                    st.dataframe(data["Course"].sort_values("Sign Ups", ascending=False), use_container_width=True, hide_index=True)
            
            with col_c2:
                # --- HEADER ---
                st.subheader("Badges Issued")
                st.info(METRIC_TOOLTIPS["badges"]) # VISIBLE INFO BOX
                
                if data.get("Badges") is not None:
                    df_badges = data["Badges"].copy().sort_values("Month")
                    fig_badges = px.line(df_badges, x="Month", y="Number of Badges", markers=True)
                    fig_badges.update_traces(line_color='#ff6600', line_width=3)
                    fig_badges.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
                    
                    # --- FIX: FORCE X-AXIS FORMATTING ---
                    fig_badges.update_xaxes(dtick="M1", tickformat="%b %Y")
                    
                    st.plotly_chart(fig_badges, use_container_width=True)
                    st.markdown("#### Badges Data")
                    st.dataframe(df_badges, use_container_width=True, hide_index=True)

                # --- HEADER ---
                st.subheader("Completion Rates")
                st.info(METRIC_TOOLTIPS["completion"]) # VISIBLE INFO BOX
                
                if data.get("Completion") is not None:
                    df_comp = data["Completion"].sort_values("Avg Completion %", ascending=True)
                    fig_comp = px.bar(df_comp, x="Avg Completion %", y="Starter Kit", orientation='h')
                    fig_comp.update_traces(marker=dict(color=df_comp["Avg Completion %"], colorscale=[[0, "#333"], [1, "#ff6600"]]))
                    fig_comp.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_comp, use_container_width=True)
                    st.markdown("#### Completion Data")
                    st.dataframe(df_comp.sort_values("Avg Completion %", ascending=False), use_container_width=True, hide_index=True)

        # TAB 4: BUSINESS
        with tab_business:
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                # --- HEADER ---
                st.subheader("User Segmentation")
                st.info(METRIC_TOOLTIPS["segmentation"]) # VISIBLE INFO BOX
                
                labels = ["Business", "Generic", "Blocked"]
                values = [biz_count, gen_count, blocked_count]
                colors = ['#ff6600', '#9e9e9e', '#424242'] 
                fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5, marker=dict(colors=colors))])
                fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col_b2:
                # --- HEADER ---
                st.subheader("Leads Generated")
                st.info(METRIC_TOOLTIPS["leads"]) # VISIBLE INFO BOX
                
                if data.get("Leads") is not None:
                    df_leads = data["Leads"].copy().sort_values("Month")
                    fig_leads = px.line(df_leads, x="Month", y="Number of Leads Gen", markers=True)
                    fig_leads.update_traces(line_color='#ff6600', line_width=3)
                    fig_leads.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
                    
                    # --- FIX: FORCE X-AXIS FORMATTING ---
                    fig_leads.update_xaxes(dtick="M1", tickformat="%b %Y")
                    
                    st.plotly_chart(fig_leads, use_container_width=True)
                    st.markdown("#### Leads Data")
                    st.dataframe(df_leads, use_container_width=True, hide_index=True)
                else:
                    st.info("Leads data not available.")

    else:
        st.warning("Please upload 'final_unified_master_with_segments.xlsx' to GitHub.")
