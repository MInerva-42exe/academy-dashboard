import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. PAGE CONFIGURATION & THEME ---
st.set_page_config(page_title="Academy Analytics Pro", layout="wide")

st.markdown("""
<style>
/* --------------------------------
   0. DESIGN TOKENS & GLOBAL RESET
-------------------------------- */
:root {
    /* Brand & accents */
    --accent: #FF6600;
    --accent-soft: rgba(255, 102, 0, 0.24);
    --accent-soft-strong: rgba(255, 102, 0, 0.4);

    /* Backgrounds */
    --bg-main: #020617;
    --bg-main-soft: #030712;
    --bg-card: #050510;
    --bg-card-deep: #05050A;
    --bg-elevated: #0B0F19;

    /* Text */
    --text-primary: #F9FAFB;
    --text-muted: #9CA3AF;
    --text-subtle: #6B7280;

    /* Borders & lines */
    --border-subtle: rgba(148, 163, 184, 0.45);
    --border-strong: rgba(15, 23, 42, 0.95);

    /* Shadows */
    --shadow-deep: 0 26px 70px rgba(0, 0, 0, 1);
    --shadow-medium: 0 20px 55px rgba(0, 0, 0, 0.9);
}

/* Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* Scope typography and smoothing to app */
.stApp, .stApp * {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* --------------------------------
   1. RESPONSIVE LAYOUT & CONTAINER
-------------------------------- */
.stApp {
    background:
        radial-gradient(ellipse at 10% 0%, rgba(255, 102, 0, 0.09), transparent 55%),
        radial-gradient(ellipse at 90% 100%, rgba(255, 102, 0, 0.08), transparent 55%),
        radial-gradient(circle at 50% 50%, rgba(16, 16, 24, 1), #000000);
    background-attachment: fixed;
    color: var(--text-primary);
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
    animation: bgFlow 22s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
}

@keyframes bgFlow {
    0% { opacity: 0.35; transform: scale(1) translate3d(0, 0, 0); }
    50% { opacity: 0.6; transform: scale(1.04) translate3d(10px, -8px, 0); }
    100% { opacity: 0.35; transform: scale(1) translate3d(0, 0, 0); }
}

/* Main content container with responsive padding */
.main .block-container {
    padding: 2.6rem 3rem !important;
    max-width: 1500px !important;
    position: relative;
    z-index: 1;
}

/* --------------------------------
   2. TYPOGRAPHY & HIERARCHY
-------------------------------- */
.main h1 {
    position: relative;
    display: inline-block;
    font-size: 2.3rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.04em !important;
    margin-bottom: 0.6rem !important;
    background: linear-gradient(135deg, #FFFFFF 0%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 18px rgba(0, 0, 0, 0.9), 0 0 22px rgba(255, 102, 0, 0.45);
}

.main h2, .main h3 {
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: var(--text-primary) !important;
    margin-top: 2.1rem !important;
    margin-bottom: 1rem !important;
}

/* --------------------------------
   3. KPI CARDS (st.metric)
-------------------------------- */
div[data-testid="metric-container"] {
    background: radial-gradient(circle at 0 0, rgba(31, 31, 45, 0.98), rgba(5, 5, 10, 0.98));
    border-radius: 20px;
    padding: 1.5rem 1.4rem !important;
    border: 1px solid rgba(255, 255, 255, 0.06);
    box-shadow: var(--shadow-deep), 0 0 0 1px var(--border-strong);
    backdrop-filter: blur(14px);
    transition: transform 0.2s ease-out;
}

div[data-testid="metric-container"]:hover {
    transform: translateY(-3px) scale(1.01);
    border-color: rgba(255, 102, 0, 0.65);
    box-shadow: 0 30px 80px rgba(0, 0, 0, 1), 0 0 0 1px rgba(255, 102, 0, 0.6);
}

div[data-testid="stMetricLabel"] {
    font-size: 0.76rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.14em !important;
    color: var(--text-subtle) !important;
}

div[data-testid="stMetricValue"] {
    font-size: 2.05rem !important;
    font-weight: 800 !important;
    color: #fff;
    text-shadow: 0 0 10px rgba(255, 102, 0, 0.5);
}

/* --------------------------------
   4. FUTURISTIC TABS (NAV)
-------------------------------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.6rem;
    background: rgba(7, 7, 12, 0.9);
    padding: 0.55rem;
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: var(--shadow-medium);
    position: sticky;
    top: 0.75rem;
    z-index: 9;
    backdrop-filter: blur(10px);
}

.stTabs [data-baseweb="tab"] {
    height: 48px;
    border-radius: 10px;
    background: transparent;
    color: var(--text-muted);
    font-weight: 600;
    text-transform: uppercase;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, rgba(255, 102, 0, 0.26), rgba(0, 0, 0, 1));
    color: var(--accent);
    box-shadow: 0 20px 55px rgba(0, 0, 0, 1), 0 0 0 1px rgba(255, 102, 0, 0.9);
}

/* --------------------------------
   5. ENHANCED INFO BOXES (.stAlert)
-------------------------------- */
.stAlert {
    background: radial-gradient(circle at 0 0, var(--bg-elevated), #000000);
    border-radius: 18px;
    border: 1px solid var(--border-subtle);
    color: #E5E7EB;
}

/* --------------------------------
   6. CHART CONTAINERS
-------------------------------- */
div[data-testid="stPlotlyChart"] {
    background: radial-gradient(circle at 0 0, rgba(20, 20, 30, 0.98), rgba(5, 5, 10, 0.98));
    border-radius: 20px;
    padding: 1.3rem;
    border: 1px solid rgba(255, 255, 255, 0.06);
    box-shadow: var(--shadow-deep);
}

/* --------------------------------
   7. DATATAFRAMES
-------------------------------- */
.stDataFrame {
    border-radius: 18px !important;
    box-shadow: 0 24px 70px rgba(0, 0, 0, 1), 0 0 0 1px var(--border-strong) !important;
}
.stDataFrame thead th {
    background: #0F172A !important;
    color: #E2E8F0 !important;
}
.stDataFrame tbody td {
    color: #E5E7EB !important;
}
</style>
""", unsafe_allow_html=True)

# --- TOOLTIPS ---
TOOLTIPS = {
    "mau": """
    **Monthly Active Users (MAU)**
    Unique users who engaged with the academy (logged in or made progress) in a given month.
    """,
    "activation": """
    **D30 Activation Rate**
    Percentage of new signups who completed a key action (e.g., finishing a lesson) within their first 30 days.
    """,
    "funnel": """
    **Drop-off Funnel**
    Visualizes where users stop progressing:
    1. **Enrolled:** Signed up but no progress.
    2. **Early Drop-off:** Started but quit early.
    3. **Mid Funnel:** Quit halfway through.
    4. **Completed:** Finished the course.
    """
}

# --- 2. DATA LOADING & MAPPING ---
@st.cache_data
def load_data():
    base_name = "ManageEngine User Academy Stats - Single Source of Truth.xlsx - "
    
    # File Mappings
    files = {
        "Master": f"{base_name}Master.csv",
        "Monthly_Enroll": f"{base_name}Monthly Enrollments.csv",
        "Monthly_Unique": f"{base_name}Monthly User Sign Ups.csv",
        "Country": f"{base_name}Country Breakdown.csv",
        "Course": f"{base_name}Course Sign-Up Sheet.csv",
        "Completion": f"{base_name}Completion Percentage.csv",
        "Business_Email": f"{base_name}Business.csv",
        "Generic_Email": f"{base_name}Generic.csv",
        "Blocked_Email": f"{base_name}Invalid.csv",
        # NEW FILES
        "MAU": f"{base_name}Monthly Active Users (MAU).csv",
        "Activation": f"{base_name}Activation Rate D30.csv",
        "DropOff_Split": f"{base_name}Drop-off Stage Split.csv",
        "Course_DropOff": f"{base_name}Course-level Drop-off (All).csv",
        "User_Engagement": f"{base_name}User and Course Engagement.csv"
    }

    data = {}
    for key, filename in files.items():
        if os.path.exists(filename):
            data[key] = pd.read_csv(filename)
        else:
            data[key] = None

    # --- DATA CLEANING & RENAMING ---
    
    # 1. Monthly Enrollments
    if data["Monthly_Enroll"] is not None:
        data["Monthly_Enroll"].rename(columns={"Number of enrollments": "Enrollments"}, inplace=True)

    # 2. Monthly Unique Users
    if data["Monthly_Unique"] is not None:
        data["Monthly_Unique"].rename(columns={"Number of Sign Ups": "Unique User Signups"}, inplace=True)
        
    # 3. Course Breakdown
    if data["Course"] is not None:
        data["Course"].rename(columns={"Course Name": "Course", "Course Sign-Ups": "Sign Ups"}, inplace=True)
        
    # 4. Completion
    if data["Completion"] is not None:
        data["Completion"].rename(columns={"Course": "Starter Kit", "Avg %": "Avg Completion %"}, inplace=True)

    # 5. Badges (Calculated from Master)
    if data["Master"] is not None:
        try:
            df_m = data["Master"]
            badges = df_m[df_m['Completed Percentage'] == 100].copy()
            if not badges.empty:
                badges['Completion Date'] = pd.to_datetime(badges['Course/Bundle Completed Date'], errors='coerce')
                badges_grouped = badges.groupby(badges['Completion Date'].dt.to_period('M')).size().reset_index(name='Number of Badges')
                badges_grouped['Month'] = badges_grouped['Completion Date'].dt.strftime('%b %Y')
                data["Badges"] = badges_grouped
            else:
                data["Badges"] = pd.DataFrame(columns=["Month", "Number of Badges"])
        except:
            data["Badges"] = pd.DataFrame(columns=["Month", "Number of Badges"])

    # 6. Region Logic
    if data["Country"] is not None:
        country_to_cont = {
            'INDIA': 'Asia', 'USA': 'North America', 'UNITED STATES': 'North America',
            'UK': 'Europe', 'UNITED KINGDOM': 'Europe', 'AUSTRALIA': 'Oceania',
            'GERMANY': 'Europe', 'FRANCE': 'Europe', 'CANADA': 'North America'
            # (Add truncated list for brevity, logic remains same as before)
        }
        # Simple fallback for demo
        data["Country"]["Region"] = data["Country"]["Country"].apply(lambda x: country_to_cont.get(str(x).upper(), "Other"))

    return data

data = load_data()

# --- 3. DASHBOARD LAYOUT ---
if data:
    st.title("Academy Analytics Pro")
    st.markdown(f"*Data updated: {pd.Timestamp.now().strftime('%Y-%m-%d')}*")
    st.markdown("---")

    # --- KPIs ---
    total_enrolls = data["Course"]["Sign Ups"].sum() if data.get("Course") is not None else 0
    total_unique = data["Monthly_Unique"]["Unique User Signups"].sum() if data.get("Monthly_Unique") is not None else 0
    total_badges = data["Badges"]["Number of Badges"].sum() if data.get("Badges") is not None else 0
    
    # New KPI: Current MAU (Most recent month)
    current_mau = 0
    if data.get("MAU") is not None and not data["MAU"].empty:
        current_mau = data["MAU"].iloc[-1]["MAU"]

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Net User Enrollments", f"{total_enrolls:,}")
    kpi2.metric("Unique Users", f"{total_unique:,}")
    kpi3.metric("Badges Issued", f"{total_badges:,}")
    kpi4.metric("Current MAU", f"{current_mau:,}", delta="Active Users")

    # --- TABS ---
    tab_growth, tab_geo, tab_content, tab_business = st.tabs(["Growth & Retention", "Geography", "Course Performance", "User Insights"])

    # === TAB 1: GROWTH & RETENTION ===
    with tab_growth:
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.subheader("Enrollment Trends")
            if data.get("Monthly_Enroll") is not None:
                df_enroll = data["Monthly_Enroll"].copy()
                df_enroll['Month'] = pd.to_datetime(df_enroll['Month'])
                df_enroll = df_enroll.sort_values("Month")
                
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(x=df_enroll['Month'], y=df_enroll['Enrollments'], 
                                             mode='lines+markers', name='Enrollments',
                                             line=dict(color='#ff6600', width=3)))
                fig_trend.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', 
                                      height=350, margin=dict(t=20, l=0, r=0, b=0))
                st.plotly_chart(fig_trend, use_container_width=True)

        with col_g2:
            st.subheader("Monthly Active Users (MAU)")
            st.info(TOOLTIPS["mau"])
            if data.get("MAU") is not None:
                df_mau = data["MAU"].copy()
                df_mau['Month_Dt'] = pd.to_datetime(df_mau['Month'], format='%b %Y')
                df_mau = df_mau.sort_values("Month_Dt")
                
                fig_mau = px.bar(df_mau, x='Month', y=['MAU', 'Business MAU'], barmode='group',
                               color_discrete_map={'MAU': '#ff6600', 'Business MAU': '#333'})
                fig_mau.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', 
                                    plot_bgcolor='rgba(0,0,0,0)', height=350)
                st.plotly_chart(fig_mau, use_container_width=True)

        # New Row: Activation
        st.subheader("Activation Rate (D30)")
        st.info(TOOLTIPS["activation"])
        if data.get("Activation") is not None:
            df_act = data["Activation"].copy()
            # Convert Cohort to datetime for sorting
            df_act['Cohort_Dt'] = pd.to_datetime(df_act['Cohort'], format='%b %Y', errors='coerce')
            df_act = df_act.sort_values("Cohort_Dt")
            
            fig_act = px.line(df_act, x='Cohort', y=['All Activation Rate %', 'Business Activation Rate %'], markers=True,
                            color_discrete_map={'All Activation Rate %': '#A5B4FC', 'Business Activation Rate %': '#ff6600'})
            fig_act.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', height=350)
            st.plotly_chart(fig_act, use_container_width=True)

    # === TAB 2: GEOGRAPHY ===
    with tab_geo:
        st.subheader("Global User Distribution")
        if data.get("Country") is not None:
            df_geo = data["Country"]
            fig_map = px.choropleth(df_geo, locations="Country", locationmode='country names',
                                    color="Total Course Signups", 
                                    color_continuous_scale=["#1e1e1e", "#ff6600"])
            fig_map.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', 
                                geo=dict(bgcolor='rgba(0,0,0,0)'), height=500)
            st.plotly_chart(fig_map, use_container_width=True)

    # === TAB 3: COURSE PERFORMANCE ===
    with tab_content:
        col_c1, col_c2 = st.columns([1, 1])
        
        with col_c1:
            st.subheader("Drop-off Funnel (All Courses)")
            st.info(TOOLTIPS["funnel"])
            if data.get("DropOff_Split") is not None:
                df_funnel = data["DropOff_Split"]
                # Define order
                stages = ["Enrolled – No Progress", "Early Drop-off", "Mid Funnel", "Completed"]
                
                fig_funnel = go.Figure(go.Funnel(
                    y=df_funnel['Stage'],
                    x=df_funnel['All Count'],
                    textinfo="value+percent initial",
                    marker={"color": ["#333", "#666", "#999", "#ff6600"]}
                ))
                fig_funnel.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', height=400)
                st.plotly_chart(fig_funnel, use_container_width=True)

        with col_c2:
            st.subheader("Popular Courses")
            if data.get("Course") is not None:
                df_course_top = data["Course"].sort_values("Sign Ups", ascending=False).head(15)
                fig_course = px.bar(df_course_top, x="Sign Ups", y="Course", orientation='h')
                fig_course.update_traces(marker_color='#ff6600')
                fig_course.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', 
                                       yaxis={'categoryorder':'total ascending'}, height=400)
                st.plotly_chart(fig_course, use_container_width=True)

        st.subheader("Detailed Course Drop-off Analysis")
        if data.get("Course_DropOff") is not None:
            st.dataframe(data["Course_DropOff"], use_container_width=True)

    # === TAB 4: USER INSIGHTS ===
    with tab_business:
        col_b1, col_b2 = st.columns(2)
        
        with col_b1:
            st.subheader("User Segmentation")
            biz_c = len(data["Business_Email"]) if data.get("Business_Email") is not None else 0
            gen_c = len(data["Generic_Email"]) if data.get("Generic_Email") is not None else 0
            blk_c = len(data["Blocked_Email"]) if data.get("Blocked_Email") is not None else 0
            
            labels = ["Business", "Generic", "Blocked"]
            values = [biz_c, gen_c, blk_c]
            fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5, marker=dict(colors=['#ff6600', '#9e9e9e', '#333']))])
            fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_b2:
            st.subheader("User Engagement Depth")
            st.caption("How many courses do users typically take?")
            if data.get("User_Engagement") is not None:
                df_eng = data["User_Engagement"]
                # Filter rows that look like "Users with X Course"
                df_eng_plot = df_eng[df_eng['Metric'].str.contains("Users with")]
                
                fig_eng = px.bar(df_eng_plot, x='Metric', y='Count', color='Metric',
                               color_discrete_sequence=['#ff6600', '#cc5200', '#993d00'])
                fig_eng.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
                st.plotly_chart(fig_eng, use_container_width=True)

else:
    st.error("Data files not found. Please ensure all CSVs are in the working directory.")
