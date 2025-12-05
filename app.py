import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION & THEME ---
st.set_page_config(page_title="Analytics Dashboard", layout="wide")

# CSS: Import Google Fonts (Lato), Black Background, & Styling
st.markdown("""
<style>
/* --------------------------------
   1. GLOBAL FONTS
-------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Lato', sans-serif !important;
}

/* --------------------------------
   2. DYNAMIC ANIMATED BACKGROUND
   - Flowing radial gradients
   - 25s smooth cycle
   - Layered depth
-------------------------------- */
.stApp {
    background:
        radial-gradient(circle at 0% 0%, rgba(255, 102, 0, 0.18), transparent 40%),
        radial-gradient(circle at 100% 0%, rgba(255, 102, 0, 0.10), transparent 45%),
        radial-gradient(circle at 0% 100%, rgba(255, 255, 255, 0.04), transparent 40%),
        radial-gradient(circle at 50% 30%, rgba(255, 102, 0, 0.15), #000000 70%);
    color: #fafafa;
    background-color: #000000; /* keep solid black as core */
    background-blend-mode: screen, screen, soft-light, normal;
    animation: bgFlow 25s ease-in-out infinite alternate;
}

@keyframes bgFlow {
    0% {
        background-position: 0% 0%, 100% 0%, 0% 100%, 50% 30%;
    }
    50% {
        background-position: 10% 5%, 90% 10%, 5% 90%, 55% 35%;
    }
    100% {
        background-position: 20% 10%, 80% 15%, 10% 85%, 60% 40%;
    }
}

.main .block-container {
    padding-top: 3rem !important;
    padding-bottom: 3rem !important;
    max-width: 1320px !important;
}

/* --------------------------------
   3. PREMIUM TITLE ANIMATION
   - Blur to focus
   - Glow shadow
   - Left bar + right line accents
-------------------------------- */
.main h1 {
    position: relative;
    display: inline-block;
    font-weight: 800 !important;
    letter-spacing: 0.24em !important;
    text-transform: uppercase !important;
    font-size: 1.35rem !important;
    color: #f9fafb !important;
    padding-left: 14px;
    padding-right: 70px;
    filter: blur(6px);
    opacity: 0;
    transform: translateY(-10px) scale(0.96);
    text-shadow:
        0 0 22px rgba(0, 0, 0, 0.9),
        0 0 28px rgba(255, 102, 0, 0.6);
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
        transform: translateY(2px) scale(1.05);
    }
    100% {
        opacity: 1;
        filter: blur(0px);
        transform: translateY(0) scale(1);
    }
}

/* Left vertical bar */
.main h1::before {
    content: "";
    position: absolute;
    left: 0;
    top: 25%;
    width: 3px;
    height: 50%;
    background: linear-gradient(180deg, #ff6600, transparent);
    box-shadow: 0 0 18px rgba(255, 102, 0, 0.9);
    transform-origin: bottom;
    transform: scaleY(0);
    animation: titleBar 0.7s 0.2s cubic-bezier(0.19, 1, 0.22, 1) forwards;
}

/* Right accent line */
.main h1::after {
    content: "";
    position: absolute;
    right: 0;
    top: 50%;
    width: 58px;
    height: 2px;
    background: linear-gradient(90deg, #ff6600, transparent);
    box-shadow: 0 0 18px rgba(255, 102, 0, 0.8);
    transform-origin: left;
    transform: translateY(-50%) scaleX(0);
    animation: titleLine 0.7s 0.4s cubic-bezier(0.19, 1, 0.22, 1) forwards;
}

@keyframes titleBar {
    0% { transform: scaleY(0); opacity: 0; }
    100% { transform: scaleY(1); opacity: 1; }
}

@keyframes titleLine {
    0% { transform: translateY(-50%) scaleX(0); }
    100% { transform: translateY(-50%) scaleX(1); }
}

.main h2, .main h3 {
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase;
    font-size: 0.9rem !important;
    color: #e5e7eb !important;
    margin-top: 1.5rem !important;
    margin-bottom: 0.6rem !important;
}

.main p {
    color: #9ca3af !important;
}

/* --------------------------------
   4. NEXT-LEVEL KPI CARDS
   - Glass morph
   - Staggered float + slight rotation
   - Pulsing borders & shine
-------------------------------- */
div[data-testid="metric-container"] {
    background: radial-gradient(circle at 0 0,
        rgba(255, 255, 255, 0.09),
        rgba(0, 0, 0, 0.98));
    border-radius: 22px;
    padding: 1.25rem 1.6rem !important;
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow:
        0 28px 70px rgba(0, 0, 0, 0.98),
        0 0 0 1px rgba(15, 23, 42, 0.9);
    backdrop-filter: blur(18px);
    position: relative;
    overflow: hidden;
    transform: translateY(12px) scale(0.96) rotateX(4deg);
    opacity: 0;
    animation: metricFloat 0.7s cubic-bezier(0.19, 1, 0.22, 1) forwards;
}

/* Staggered timings */
div[data-testid="metric-container"]:nth-of-type(1) { animation-delay: 0.15s; }
div[data-testid="metric-container"]:nth-of-type(2) { animation-delay: 0.25s; }
div[data-testid="metric-container"]:nth-of-type(3) { animation-delay: 0.35s; }
div[data-testid="metric-container"]:nth-of-type(4) { animation-delay: 0.45s; }

@keyframes metricFloat {
    0% {
        opacity: 0;
        transform: translateY(14px) scale(0.94) rotateX(6deg);
    }
    65% {
        opacity: 1;
        transform: translateY(-2px) scale(1.02) rotateX(0deg);
    }
    100% {
        opacity: 1;
        transform: translateY(0) scale(1) rotateX(0deg);
    }
}

/* Pulsing gradient border via overlay */
div[data-testid="metric-container"]::after {
    content: "";
    position: absolute;
    inset: -1px;
    border-radius: inherit;
    background: linear-gradient(135deg,
        rgba(255, 102, 0, 0.9),
        rgba(255, 255, 255, 0.15),
        rgba(255, 102, 0, 0.6));
    opacity: 0;
    mix-blend-mode: screen;
    pointer-events: none;
    animation: borderPulse 3.5s ease-in-out infinite;
}

@keyframes borderPulse {
    0% { opacity: 0.0; }
    30% { opacity: 0.25; }
    60% { opacity: 0.08; }
    100% { opacity: 0.0; }
}

/* Diagonal shine on hover */
div[data-testid="metric-container"]::before {
    content: "";
    position: absolute;
    top: -150%;
    left: -80%;
    width: 260%;
    height: 260%;
    background: linear-gradient(
        130deg,
        transparent 0%,
        rgba(255, 255, 255, 0.22) 20%,
        rgba(255, 255, 255, 0.05) 55%,
        transparent 100%
    );
    opacity: 0;
    transform: translate3d(-20%, 0, 0);
    transition: opacity 0.5s ease-out, transform 0.7s ease-out;
    pointer-events: none;
}

div[data-testid="metric-container"]:hover::before {
    opacity: 1;
    transform: translate3d(10%, 0, 0);
}

/* 3D hover lift */
div[data-testid="metric-container"]:hover {
    transform: translateY(-4px) scale(1.02) rotateX(0deg);
    box-shadow:
        0 32px 80px rgba(0, 0, 0, 1),
        0 0 0 1px rgba(255, 102, 0, 0.7);
    border-color: rgba(255, 102, 0, 0.85);
}

/* Metric text styling */
div[data-testid="stMetricLabel"] {
    color: #e5e7eb !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    opacity: 0.9;
}

div[data-testid="stMetricValue"] {
    color: #ff6600 !important; /* keep core orange */
    font-size: 2.0rem !important;
    font-weight: 800 !important;
    text-shadow:
        0 0 18px rgba(255, 102, 0, 0.7),
        0 0 34px rgba(0, 0, 0, 1);
    animation: valuePulse 2.8s ease-in-out infinite;
}

@keyframes valuePulse {
    0%   { text-shadow: 0 0 14px rgba(255, 102, 0, 0.6); }
    50%  { text-shadow: 0 0 26px rgba(255, 102, 0, 0.9); }
    100% { text-shadow: 0 0 14px rgba(255, 102, 0, 0.6); }
}

div[data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
    color: #a5b4fc !important;
}

/* --------------------------------
   5. FUTURISTIC TABS
   - Gradient/bg glow
   - Pulsing bottom line
-------------------------------- */
.stTabs [data-baseweb="tab-list"] {
    width: 100%;
    gap: 10px;
    border-bottom: none;
    margin-bottom: 1rem;
}

.stTabs [data-baseweb="tab"] {
    flex-grow: 1;
    text-align: center;
    height: 52px;
    background: linear-gradient(
        135deg,
        rgba(15, 23, 42, 0.95),
        rgba(0, 0, 0, 1)
    );
    border-radius: 16px;
    color: #9CA3AF;
    border: 1px solid rgba(31, 41, 55, 0.95);
    font-weight: 600;
    font-size: 0.78rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    transition:
        color 0.18s cubic-bezier(0.19, 1, 0.22, 1),
        background 0.18s cubic-bezier(0.19, 1, 0.22, 1),
        transform 0.18s cubic-bezier(0.19, 1, 0.22, 1),
        box-shadow 0.18s cubic-bezier(0.19, 1, 0.22, 1),
        border-color 0.18s cubic-bezier(0.19, 1, 0.22, 1);
    position: relative;
    overflow: hidden;
}

/* Hover glow */
.stTabs [data-baseweb="tab"]::before {
    content: "";
    position: absolute;
    inset: -40%;
    background: radial-gradient(circle at 20% 0,
        rgba(255, 102, 0, 0.25),
        transparent 60%);
    opacity: 0;
    transform: scale(0.6);
    transition: opacity 0.25s ease-out, transform 0.25s ease-out;
    pointer-events: none;
}

.stTabs [data-baseweb="tab"]:hover::before {
    opacity: 0.7;
    transform: scale(1);
}

.stTabs [data-baseweb="tab"]:hover {
    background: linear-gradient(
        135deg,
        rgba(148, 163, 184, 0.25),
        rgba(0, 0, 0, 1)
    );
    color: #ffffff;
    transform: translateY(-2px);
    box-shadow:
        0 18px 45px rgba(0, 0, 0, 1),
        0 0 0 1px rgba(148, 163, 184, 0.8);
    border-color: rgba(148, 163, 184, 0.9);
}

/* Active tab */
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: radial-gradient(circle at 10% 0,
        rgba(255, 102, 0, 0.35),
        #000000);
    color: #ff6600;
    box-shadow:
        0 22px 60px rgba(0, 0, 0, 1),
        0 0 0 1px rgba(255, 102, 0, 0.95);
    transform: translateY(-1px) scale(1.01);
    border-color: rgba(255, 102, 0, 0.95);
}

/* Pulsing bottom line */
.stTabs [data-baseweb="tab"][aria-selected="true"]::after {
    content: "";
    position: absolute;
    left: 18%;
    right: 18%;
    bottom: -3px;
    height: 2px;
    background: linear-gradient(90deg, transparent, #ff6600, transparent);
    box-shadow: 0 0 18px rgba(255, 102, 0, 0.9);
    animation: tabPulse 1.4s ease-in-out infinite alternate;
}

@keyframes tabPulse {
    0%   { opacity: 0.5; transform: scaleX(0.95); }
    100% { opacity: 1;   transform: scaleX(1.05); }
}

/* --------------------------------
   6. ENHANCED INFO BOXES (st.info)
   - Slide-in, pulsing border, floating glow
-------------------------------- */
.stAlert {
    background: radial-gradient(circle at 0 0,
        rgba(15, 23, 42, 1),
        rgba(0, 0, 0, 1));
    border-radius: 18px;
    border: 1px solid rgba(148, 163, 184, 0.5);
    color: #d1d5db;
    box-shadow:
        0 24px 70px rgba(0, 0, 0, 1),
        0 0 0 1px rgba(15, 23, 42, 0.95);
    padding: 1rem 1.2rem !important;
    font-size: 0.86rem !important;
    line-height: 1.6;
    position: relative;
    overflow: hidden;
    transform: translateX(-10px);
    opacity: 0;
    animation: infoSlide 0.45s ease-out forwards;
}

@keyframes infoSlide {
    0%   { opacity: 0; transform: translateX(-10px); }
    100% { opacity: 1; transform: translateX(0); }
}

/* Pulsing orange left border */
.stAlert::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: linear-gradient(
        180deg,
        #ff6600,
        rgba(255, 102, 0, 0.05),
        #ff6600
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
        transparent 70%);
    opacity: 0.6;
    filter: blur(2px);
}

/* Inline code inside info */
.stAlert code {
    background-color: rgba(15, 23, 42, 0.9);
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    color: #fde68a;
}

/* --------------------------------
   7. CHART CONTAINERS (Plotly)
   - Glow, lift, frosted glass
-------------------------------- */
div[data-testid="stPlotlyChart"] {
    background: radial-gradient(circle at 0 0,
        rgba(15, 23, 42, 1),
        rgba(0, 0, 0, 1));
    border-radius: 22px;
    padding: 1.15rem 1.2rem 0.9rem 1.2rem;
    border: 1px solid rgba(31, 41, 55, 0.95);
    box-shadow:
        0 28px 80px rgba(0, 0, 0, 1),
        0 0 0 1px rgba(15, 23, 42, 0.95);
    transition:
        transform 0.2s ease-out,
        box-shadow 0.2s ease-out,
        border-color 0.2s ease-out;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(16px);
}

/* Subtle orange glow */
div[data-testid="stPlotlyChart"]::before {
    content: "";
    position: absolute;
    inset: -20%;
    background: radial-gradient(circle at 0 0,
        rgba(255, 102, 0, 0.22),
        transparent 65%);
    opacity: 0.32;
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
        0 32px 90px rgba(0, 0, 0, 1),
        0 0 0 1px rgba(255, 102, 0, 0.55);
    border-color: rgba(255, 102, 0, 0.85);
}

/* --------------------------------
   8. PREMIUM DATA TABLES
   - Orange borders, smooth hover
-------------------------------- */
.stDataFrame {
    border-radius: 18px !important;
    overflow: hidden !important;
    box-shadow:
        0 24px 70px rgba(0, 0, 0, 1),
        0 0 0 1px rgba(15, 23, 42, 0.95);
}

.stDataFrame table {
    border-collapse: collapse !important;
    background-color: #020617 !important;
    border: 1px solid rgba(31, 41, 55, 0.9) !important;
}

.stDataFrame tbody tr:nth-child(even) {
    background-color: #020617 !important;
}

.stDataFrame tbody tr:nth-child(odd) {
    background-color: #030712 !important;
}

.stDataFrame th {
    background: linear-gradient(
        135deg,
        rgba(15, 23, 42, 1),
        rgba(3, 7, 18, 1)
    ) !important;
    color: #e5e7eb !important;
    border-bottom: 1px solid rgba(55, 65, 81, 0.95) !important;
    text-transform: uppercase;
    font-size: 0.72rem !important;
    letter-spacing: 0.16em;
    padding: 0.65rem 0.75rem !important;
    border-top: 1px solid rgba(255, 102, 0, 0.4) !important;
}

.stDataFrame td {
    border-bottom: 1px solid rgba(31, 41, 55, 0.95) !important;
    color: #d1d5db !important;
    font-size: 0.8rem !important;
    padding: 0.55rem 0.75rem !important;
}

/* Row hover with orange side highlight */
.stDataFrame tbody tr:hover td {
    background: linear-gradient(90deg,
        rgba(255, 102, 0, 0.12),
        rgba(15, 23, 42, 0.98)) !important;
    border-left: 2px solid #ff6600 !important;
}

/* --------------------------------
   9. CUSTOM SCROLLBARS
   - Orange gradient, glow on hover
-------------------------------- */
::-webkit-scrollbar {
    width: 9px;
    height: 9px;
}

::-webkit-scrollbar-track {
    background: #020617;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #ff6600, #7c2d12);
    border-radius: 999px;
    box-shadow: 0 0 10px rgba(255, 102, 0, 0.7);
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #ff6600, #ea580c);
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
