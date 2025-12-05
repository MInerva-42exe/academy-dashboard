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
       1. FONTS
    -------------------------------- */
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Lato', sans-serif !important;
    }

    /* --------------------------------
       2. GLOBAL THEME & LAYOUT
    -------------------------------- */
    .stApp {
        /* Keep pure black as base, add subtle vignette for depth */
        background:
            radial-gradient(circle at 0% 0%, #181818 0, #000000 45%),
            radial-gradient(circle at 100% 100%, #141414 0, #000000 45%);
        color: #fafafa;
    }

    /* Widen main container & add breathing room */
    .main .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1300px !important;
    }

    /* Headings – sharper, more "dashboard" feel */
    .main h1 {
        font-weight: 700 !important;
        letter-spacing: 0.18em !important;
        text-transform: uppercase !important;
        font-size: 1.2rem !important;
        color: #e5e7eb !important;
        opacity: 0;
        animation: fadeDown 0.6s ease-out forwards;
    }

    .main h2, .main h3 {
        font-weight: 600 !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase;
        font-size: 0.9rem !important;
        color: #d1d5db !important;
    }

    .main p {
        color: #9ca3af !important;
    }

    /* --------------------------------
       3. KPI METRICS – GLASS CARDS
    -------------------------------- */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg,
            rgba(255, 255, 255, 0.04),
            rgba(255, 102, 0, 0.05)
        );
        border-radius: 18px;
        padding: 1.1rem 1.4rem !important;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow:
            0 18px 45px rgba(0, 0, 0, 0.85),
            0 0 0 1px rgba(15, 23, 42, 0.5);
        backdrop-filter: blur(10px);
        transition:
            transform 0.18s ease-out,
            box-shadow 0.18s ease-out,
            border-color 0.18s ease-out,
            background 0.18s ease-out;
        position: relative;
        overflow: hidden;
    }

    /* Subtle animated highlight sweep */
    div[data-testid="metric-container"]::before {
        content: "";
        position: absolute;
        inset: -20%;
        background: radial-gradient(circle at 0 0,
            rgba(255, 255, 255, 0.09),
            transparent 55%);
        opacity: 0;
        transform: translate3d(-20%, -20%, 0);
        transition: opacity 0.25s ease-out, transform 0.25s ease-out;
        pointer-events: none;
    }

    div[data-testid="metric-container"]:hover::before {
        opacity: 1;
        transform: translate3d(0, 0, 0);
    }

    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow:
            0 26px 65px rgba(0, 0, 0, 0.95),
            0 0 0 1px rgba(255, 102, 0, 0.5);
        border-color: rgba(255, 102, 0, 0.8);
        background: linear-gradient(135deg,
            rgba(255, 255, 255, 0.06),
            rgba(255, 102, 0, 0.08)
        );
    }

    div[data-testid="stMetricLabel"] {
        color: #e5e7eb !important;
        font-size: 0.78rem !important;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        opacity: 0.9;
    }

    div[data-testid="stMetricValue"] {
        color: #ff6600 !important; /* preserve brand orange */
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }

    div[data-testid="stMetricDelta"] {
        font-size: 0.8rem !important;
        color: #a5b4fc !important;
    }

    /* --------------------------------
       4. TABS – FULL-WIDTH, LIFT & GLOW
    -------------------------------- */
    .stTabs [data-baseweb="tab-list"] {
        width: 100%;
        gap: 8px;
        border-bottom: 1px solid rgba(31, 41, 55, 0.9);
        margin-bottom: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        flex-grow: 1;
        text-align: center;
        height: 48px;
        background: radial-gradient(circle at 0 0,
            rgba(255, 255, 255, 0.04),
            rgba(15, 23, 42, 0.9));
        border-radius: 10px 10px 0 0;
        color: #9CA3AF;
        border: none;
        font-weight: 600;
        font-size: 0.8rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        transition:
            color 0.18s ease-out,
            background 0.18s ease-out,
            transform 0.18s ease-out,
            box-shadow 0.18s ease-out;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(
            135deg,
            rgba(255, 102, 0, 0.18),
            rgba(17, 24, 39, 0.95)
        );
        color: #ff6600;
        box-shadow:
            0 10px 30px rgba(0, 0, 0, 0.85),
            0 -1px 0 rgba(255, 102, 0, 0.8);
        transform: translateY(1px);
        border-bottom: 3px solid #ff6600;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: radial-gradient(circle at 50% 0,
            rgba(148, 163, 184, 0.2),
            rgba(15, 23, 42, 0.95));
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.7);
    }

    /* --------------------------------
       5. INFO BOX (st.info) – NEAT PANELS
    -------------------------------- */
    .stAlert {
        background: radial-gradient(circle at 0 0,
            rgba(15, 23, 42, 0.95),
            rgba(0, 0, 0, 0.98));
        border-radius: 14px;
        border: 1px solid rgba(148, 163, 184, 0.35);
        color: #d1d5db;
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.9);
        padding: 0.9rem 1rem !important;
        font-size: 0.86rem !important;
        line-height: 1.5;
        position: relative;
        overflow: hidden;
        animation: fadeIn 0.4s ease-out;
    }

    .stAlert::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 3px;
        background: linear-gradient(
            180deg,
            #ff6600,
            rgba(255, 102, 0, 0.1)
        );
    }

    .stAlert code {
        background-color: rgba(15, 23, 42, 0.8);
        padding: 0.15rem 0.35rem;
        border-radius: 4px;
        color: #fde68a;
    }

    /* --------------------------------
       6. MULTISELECT & INPUTS
    -------------------------------- */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #333333 !important;
        color: #ffa500 !important;
        border-radius: 999px;
        border: 1px solid rgba(156, 163, 175, 0.6);
    }

    .stMultiSelect [data-baseweb="select"] > div {
        background: rgba(15, 23, 42, 0.9) !important;
        border-radius: 999px !important;
        border: 1px solid rgba(55, 65, 81, 0.9) !important;
    }

    .stMultiSelect input {
        color: #e5e7eb !important;
    }

    /* Generic text inputs */
    input, textarea {
        background-color: rgba(15, 23, 42, 0.9) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(55, 65, 81, 0.9) !important;
        color: #f9fafb !important;
    }

    /* --------------------------------
       7. CHART & TABLE WRAPPERS
    -------------------------------- */
    /* Plotly charts get card treatment */
    div[data-testid="stPlotlyChart"] {
        background: radial-gradient(circle at 0 0,
            rgba(15, 23, 42, 0.96),
            rgba(0, 0, 0, 1));
        border-radius: 18px;
        padding: 1.1rem 1.1rem 0.8rem 1.1rem;
        border: 1px solid rgba(31, 41, 55, 0.85);
        box-shadow:
            0 20px 50px rgba(0, 0, 0, 0.95),
            0 0 0 1px rgba(15, 23, 42, 0.9);
        transition:
            transform 0.18s ease-out,
            box-shadow 0.18s ease-out,
            border-color 0.18s ease-out;
    }

    div[data-testid="stPlotlyChart"]:hover {
        transform: translateY(-2px);
        box-shadow:
            0 26px 70px rgba(0, 0, 0, 1),
            0 0 0 1px rgba(255, 102, 0, 0.45);
        border-color: rgba(255, 102, 0, 0.7);
    }

    /* DataFrames: dark grid with subtle separation */
    .stDataFrame {
        border-radius: 14px !important;
        overflow: hidden !important;
        box-shadow:
            0 18px 45px rgba(0, 0, 0, 0.95),
            0 0 0 1px rgba(15, 23, 42, 0.9);
    }

    .stDataFrame table {
        border-collapse: collapse !important;
        background-color: #020617 !important;
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
        border-bottom: 1px solid rgba(55, 65, 81, 0.9) !important;
        text-transform: uppercase;
        font-size: 0.72rem !important;
        letter-spacing: 0.14em;
    }

    .stDataFrame td {
        border-bottom: 1px solid rgba(31, 41, 55, 0.85) !important;
        color: #d1d5db !important;
        font-size: 0.8rem !important;
    }

    .stDataFrame tbody tr:hover td {
        background-color: rgba(15, 23, 42, 0.95) !important;
    }

    /* --------------------------------
       8. SCROLLBARS (Subtle, Dark)
    -------------------------------- */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #020617;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #374151, #111827);
        border-radius: 999px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #4b5563, #111827);
    }

    /* --------------------------------
       9. BASIC ANIMATIONS
    -------------------------------- */
    @keyframes fadeDown {
        0% {
            opacity: 0;
            transform: translateY(-6px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeIn {
        0% {
            opacity: 0;
            transform: translateY(4px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
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
