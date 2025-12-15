import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. PAGE CONFIGURATION & THEME ---
st.set_page_config(page_title="ManageEngine User Academy Dashboard", layout="wide")

st.markdown("""
<style>
/* --------------------------------
   0. DESIGN TOKENS & GLOBAL RESET
-------------------------------- */
:root {
    --accent: #FF6600;
    --accent-soft: rgba(255, 102, 0, 0.24);
    --bg-main: #020617;
    --text-primary: #F9FAFB;
    --text-muted: #9CA3AF;
}

/* Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

.stApp, .stApp * {
    font-family: 'Inter', sans-serif !important;
}

/* --------------------------------
   1. RESPONSIVE LAYOUT
-------------------------------- */
.stApp {
    background: radial-gradient(circle at 50% 50%, rgba(16, 16, 24, 1), #000000);
    background-attachment: fixed;
    color: var(--text-primary);
}

.main .block-container {
    padding: 2rem 3rem !important;
    max-width: 1600px !important;
}

/* --------------------------------
   2. TYPOGRAPHY
-------------------------------- */
h1 {
    background: linear-gradient(135deg, #FFFFFF 0%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
    font-size: 2.5rem !important;
}

h2, h3 {
    color: var(--text-primary) !important;
}

/* --------------------------------
   3. EQUAL WIDTH TABS
-------------------------------- */
.stTabs [data-baseweb="tab-list"] {
    display: flex;
    width: 100%;
    gap: 8px;
    background: rgba(255, 255, 255, 0.03);
    padding: 8px;
    border-radius: 12px;
}

.stTabs [data-baseweb="tab"] {
    flex-grow: 1; /* Forces equal width */
    justify-content: center;
    background: transparent;
    color: var(--text-muted);
    font-weight: 600;
    border-radius: 8px;
    border: none;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: var(--accent);
    color: white;
    box-shadow: 0 4px 12px rgba(255, 102, 0, 0.3);
}

/* --------------------------------
   4. INFO BOXES (TOOLTIPS)
-------------------------------- */
.stAlert {
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #E2E8F0;
    font-size: 0.9rem;
}

/* --------------------------------
   5. CHART CONTAINERS & METRICS
-------------------------------- */
div[data-testid="stPlotlyChart"] {
    background: rgba(20, 20, 30, 0.5);
    border-radius: 16px;
    padding: 1rem;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

div[data-testid="metric-container"] {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1rem;
}
div[data-testid="stMetricValue"] {
    color: #FF6600 !important;
}
</style>
""", unsafe_allow_html=True)

# --- TOOLTIP DEFINITIONS ---
TOOLTIPS = {
    "mau": "**Monthly Active Users (MAU)**: Unique users who engaged with the academy (logged in or made progress) in a given month.",
    "activation": "**D30 Activation Rate**: Percentage of new signups who completed a key action within their first 30 days.",
    "funnel": "**Drop-off Funnel**: Visualizes user progression from Enrollment to Completion.",
    "enrollment_trend": "**Enrollment Trends**: The number of course enrollments over time.",
    "signup_trend": "**Sign Up Trends**: The number of new unique user registrations over time.",
    "geo": "**Global Distribution**: Where users are located based on their IP.",
    "popular": "**Popular Courses**: Courses with the highest cumulative sign-up counts.",
    "segmentation": "**User Segmentation**: Breakdown of users by email domain type (Business vs Generic vs Invalid).",
    "engagement": "**Engagement Depth**: Distribution of users based on how many courses they have enrolled in.",
    "completion": "**Average Completion %**: The average percentage of users who've enrolled in a specific course and completed it 100%."
}

# --- HELPER FUNCTIONS ---
def truncate_label(text, max_len=35):
    """Truncates long labels for charts."""
    if isinstance(text, str) and len(text) > max_len:
        return text[:max_len] + "..."
    return text

def check_password():
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
    # --- DATA LOADING ---
    @st.cache_data
    def load_data():
        file_path = "ManageEngine User Academy Stats - Single Source of Truth.xlsx"
        
        if not os.path.exists(file_path):
            return None

        try:
            xls = pd.ExcelFile(file_path)
            data = {}
            sheet_map = {
                # Removed: Master, Business, Generic, Invalid
                "Monthly_Enroll": "Monthly Enrollments",
                "Monthly_Unique": "Monthly User Sign Ups",
                "Country": "Country Breakdown",
                "Course": "Course Sign-Up Sheet",
                "Completion": "Completion Percentage",
                "MAU": "Monthly Active Users (MAU)",
                "Activation": "Activation Rate D30",
                "DropOff_Split": "Drop-off Stage Split",
                "Course_DropOff": "Course-level Drop-off (All)",
                "User_Engagement": "User and Course Engagement",
                "Badges_Issued": "Badges Issued",
                "User_Segmentation": "User Segmentation"
            }

            for key, sheet_name in sheet_map.items():
                if sheet_name in xls.sheet_names:
                    data[key] = pd.read_excel(xls, sheet_name=sheet_name)
                else:
                    data[key] = None

            # CLEANING
            if data["Monthly_Enroll"] is not None:
                data["Monthly_Enroll"].rename(columns={"Number of enrollments": "Enrollments"}, inplace=True)

            if data["Monthly_Unique"] is not None:
                data["Monthly_Unique"].rename(columns={"Number of Sign Ups": "Unique User Signups"}, inplace=True)
                
            if data["Course"] is not None:
                data["Course"].rename(columns={"Course Name": "Course", "Course Sign-Ups": "Sign Ups"}, inplace=True)
                data["Course"]["ShortName"] = data["Course"]["Course"].apply(lambda x: truncate_label(x))
            
            if data["Completion"] is not None:
                data["Completion"].rename(columns={"Avg %": "Avg Completion %"}, inplace=True)

            return data
        
        except Exception as e:
            st.error(f"Error loading Excel file: {e}")
            return None

    data = load_data()

    # --- DASHBOARD UI ---
    if data:
        st.title("ManageEngine User Academy Dashboard")
        st.markdown(f"*Data updated: {pd.Timestamp.now().strftime('%Y-%m-%d')}*")
        st.markdown("---")

        # --- KPI SECTION ---
        # 1. Net Enrollments
        total_enrolls = data["Course"]["Sign Ups"].sum() if data.get("Course") is not None else 0
        
        # 2. Unique Users (UPDATED LOGIC: FROM USER SEGMENTATION SHEET)
        total_unique = 0
        if data.get("User_Segmentation") is not None:
            df_seg = data["User_Segmentation"]
            # Look for row where Segment == "Total Users"
            row_u = df_seg[df_seg['Segment'] == 'Total Users']
            if not row_u.empty:
                total_unique = row_u.iloc[0]['Count']
            else:
                # Fallback to sum if row not found, though ideally should exist
                total_unique = data["Monthly_Unique"]["Unique User Signups"].sum() if data.get("Monthly_Unique") is not None else 0
        else:
            total_unique = data["Monthly_Unique"]["Unique User Signups"].sum() if data.get("Monthly_Unique") is not None else 0

        # 3. Badges Issued (FROM BADGES ISSUED SHEET)
        total_badges = 0
        if data.get("Badges_Issued") is not None:
            df_badges = data["Badges_Issued"]
            row_b = df_badges[df_badges.iloc[:, 0] == "Total Sent"]
            if not row_b.empty:
                total_badges = row_b.iloc[0, 1]

        # 4. MAU
        current_mau = 0
        if data.get("MAU") is not None and not data["MAU"].empty:
            current_mau = data["MAU"].iloc[-1]["MAU"]

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Net User Enrollments", f"{total_enrolls:,}")
        kpi2.metric("Unique Users", f"{total_unique:,}")
        kpi3.metric("Badges Issued", f"{total_badges:,}")
        kpi4.metric("Current MAU", f"{current_mau:,}", delta="Active Users")

        # Equal Tabs
        tab_growth, tab_geo, tab_content, tab_business = st.tabs([
            "Growth & Retention", 
            "Geography", 
            "Course Performance", 
            "User Insights"
        ])

        # === TAB 1: GROWTH & RETENTION ===
        with tab_growth:
            st.subheader("Time Period Filter")
            
            all_months_dt = pd.period_range(start='2023-06', end='2025-12', freq='M')
            all_months_str = all_months_dt.strftime('%b %Y').tolist()
            
            try:
                default_start = all_months_str.index("Jun 2024")
                default_end = all_months_str.index("Dec 2025")
            except ValueError:
                default_start, default_end = 0, len(all_months_str)-1

            select_range = st.select_slider(
                "Select Range for Growth Charts:",
                options=all_months_str,
                value=(all_months_str[default_start], all_months_str[default_end])
            )
            
            def filter_by_date(df, date_col, start_str, end_str):
                if df is None or df.empty: return df
                temp_df = df.copy()
                temp_df['__dt'] = pd.to_datetime(temp_df[date_col], format='%b %Y', errors='coerce')
                
                if date_col == 'Cohort':
                     temp_df['__dt'] = pd.to_datetime(temp_df[date_col], format='%b %Y', errors='coerce')

                s_dt = pd.to_datetime(start_str, format='%b %Y')
                e_dt = pd.to_datetime(end_str, format='%b %Y') + pd.offsets.MonthEnd(0)
                
                return temp_df[(temp_df['__dt'] >= s_dt) & (temp_df['__dt'] <= e_dt)].sort_values('__dt')

            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                st.subheader("Enrollment Trends")
                st.info(TOOLTIPS["enrollment_trend"])
                if data.get("Monthly_Enroll") is not None:
                    df_enroll = filter_by_date(data["Monthly_Enroll"], 'Month', select_range[0], select_range[1])
                    if not df_enroll.empty:
                        fig_trend = go.Figure()
                        fig_trend.add_trace(go.Scatter(
                            x=df_enroll['Month'], y=df_enroll['Enrollments'], 
                            mode='lines+markers', name='Enrollments',
                            line=dict(color='#ff6600', width=3)
                        ))
                        fig_trend.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', height=350,
                                              xaxis=dict(fixedrange=False), dragmode="pan") 
                        st.plotly_chart(fig_trend, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})
            
            with col_g2:
                st.subheader("User Sign Up Trends") 
                st.info(TOOLTIPS["signup_trend"])
                if data.get("Monthly_Unique") is not None:
                    df_signup = filter_by_date(data["Monthly_Unique"], 'Month', select_range[0], select_range[1])
                    if not df_signup.empty:
                        fig_signup = go.Figure()
                        fig_signup.add_trace(go.Scatter(
                            x=df_signup['Month'], y=df_signup['Unique User Signups'],
                            mode='lines+markers', name='Sign Ups',
                            line=dict(color='#3B82F6', width=3)
                        ))
                        fig_signup.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', height=350,
                                               xaxis=dict(fixedrange=False), dragmode="pan")
                        st.plotly_chart(fig_signup, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})

            col_g3, col_g4 = st.columns(2)
            
            with col_g3:
                st.subheader("Monthly Active Users (MAU)")
                st.info(TOOLTIPS["mau"])
                if data.get("MAU") is not None:
                    df_mau = filter_by_date(data["MAU"], 'Month', select_range[0], select_range[1])
                    if not df_mau.empty:
                        fig_mau = px.bar(df_mau, x='Month', y=['MAU', 'Business MAU'], barmode='group',
                                       color_discrete_map={'MAU': '#ff6600', 'Business MAU': '#333'})
                        fig_mau.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', height=350,
                                            xaxis=dict(fixedrange=False), dragmode="pan")
                        st.plotly_chart(fig_mau, use_container_width=True, config={'scrollZoom': True})

            with col_g4:
                st.subheader("Activation Rate (D30)")
                st.info(TOOLTIPS["activation"])
                if data.get("Activation") is not None:
                    df_act = filter_by_date(data["Activation"], 'Cohort', select_range[0], select_range[1])
                    if not df_act.empty:
                        fig_act = px.line(df_act, x='Cohort', y=['All Activation Rate %', 'Business Activation Rate %'], markers=True,
                                        color_discrete_map={'All Activation Rate %': '#A5B4FC', 'Business Activation Rate %': '#ff6600'})
                        fig_act.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', height=350,
                                            xaxis=dict(fixedrange=False), dragmode="pan")
                        st.plotly_chart(fig_act, use_container_width=True, config={'scrollZoom': True})

        # === TAB 2: GEOGRAPHY ===
        with tab_geo:
            st.subheader("Global User Distribution")
            st.info(TOOLTIPS["geo"])
            
            col_geo1, col_geo2 = st.columns([2, 1])
            
            if data.get("Country") is not None:
                df_geo = data["Country"]
                with col_geo1:
                    fig_map = px.choropleth(df_geo, locations="Country", locationmode='country names',
                                          color="Total Course Signups", 
                                          color_continuous_scale=["#1e1e1e", "#ff6600"])
                    fig_map.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', 
                                        geo=dict(bgcolor='rgba(0,0,0,0)'), height=500)
                    st.plotly_chart(fig_map, use_container_width=True)
                
                with col_geo2:
                    st.markdown("#### Top 10 Countries")
                    top_10 = df_geo.sort_values("Total Course Signups", ascending=False).head(10)
                    st.dataframe(
                        top_10[["Country", "Total Course Signups"]], 
                        use_container_width=True, 
                        hide_index=True
                    )

        # === TAB 3: COURSE PERFORMANCE ===
        with tab_content:
            col_c1, col_c2 = st.columns([1, 1])
            
            with col_c1:
                st.subheader("Drop-off Funnel")
                st.info(TOOLTIPS["funnel"])
                if data.get("DropOff_Split") is not None:
                    df_funnel = data["DropOff_Split"]
                    
                    # Create custom text labels with count and %
                    total_start = df_funnel['All Count'].max()
                    df_funnel['pct'] = (df_funnel['All Count'] / total_start * 100).fillna(0).round(1).astype(str) + '%'
                    df_funnel['text_label'] = df_funnel['All Count'].astype(str) + " (" + df_funnel['pct'] + ")"
                    
                    fig_funnel = go.Figure(go.Bar(
                        x=df_funnel['All Count'],
                        y=df_funnel['Stage'],
                        orientation='h',
                        text=df_funnel['text_label'],
                        textposition='auto',
                        marker={"color": ["#333", "#666", "#999", "#ff6600"]}
                    ))
                    
                    fig_funnel.update_layout(
                        template="plotly_dark", 
                        paper_bgcolor='rgba(0,0,0,0)', 
                        height=400,
                        yaxis=dict(autorange="reversed") 
                    )
                    st.plotly_chart(fig_funnel, use_container_width=True)

            with col_c2:
                st.subheader("Popular Courses")
                st.info(TOOLTIPS["popular"])
                if data.get("Course") is not None:
                    df_course_top = data["Course"].sort_values("Sign Ups", ascending=False).head(15)
                    fig_course = px.bar(df_course_top, x="Sign Ups", y="ShortName", orientation='h',
                                      text="Sign Ups")
                    fig_course.update_traces(marker_color='#ff6600', textposition='outside')
                    fig_course.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', 
                                           yaxis={'categoryorder':'total ascending', 'automargin': True}, 
                                           height=400, dragmode="pan")
                    st.plotly_chart(fig_course, use_container_width=True, config={'scrollZoom': True})

            st.subheader("Course Completion Rates (Top 15 by Volume)")
            st.info(TOOLTIPS["completion"])
            
            if data.get("Course") is not None and data.get("Completion") is not None:
                df_merged = pd.merge(
                    data["Course"], 
                    data["Completion"][["Course", "Avg Completion %"]], 
                    on="Course", 
                    how="left"
                ).fillna(0)
                
                df_chart_data = df_merged.sort_values("Sign Ups", ascending=False).head(15)
                
                if not df_chart_data.empty:
                    fig_comp = px.bar(df_chart_data, x="Avg Completion %", y="ShortName", orientation='h',
                                    text="Avg Completion %")
                    fig_comp.update_traces(marker_color='#3B82F6', texttemplate='%{text:.1f}%', textposition='outside')
                    fig_comp.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
                                         yaxis={'categoryorder':'total ascending', 'automargin': True}, 
                                         height=400, dragmode="pan", xaxis_title="Average Completion Percentage")
                    st.plotly_chart(fig_comp, use_container_width=True, config={'scrollZoom': True})

            st.subheader("Detailed Course Drop-off Analysis")
            if data.get("Course_DropOff") is not None:
                st.dataframe(data["Course_DropOff"], use_container_width=True)
            
            st.subheader("All Course Performance Data")
            if data.get("Course") is not None and data.get("Completion") is not None:
                df_full = pd.merge(
                    data["Course"][["Course", "Sign Ups"]], 
                    data["Completion"][["Course", "Avg Completion %"]], 
                    on="Course", 
                    how="left"
                )
                df_full["Avg Completion %"] = df_full["Avg Completion %"].fillna(0).round(2)
                
                st.dataframe(
                    df_full.sort_values("Sign Ups", ascending=False),
                    use_container_width=True,
                    hide_index=True
                )

        # === TAB 4: USER INSIGHTS ===
        with tab_business:
            col_b1, col_b2 = st.columns(2)
            
            with col_b1:
                st.subheader("User Segmentation")
                st.info(TOOLTIPS["segmentation"])
                
                if data.get("User_Segmentation") is not None:
                    df_seg = data["User_Segmentation"]
                    try:
                        biz_c = df_seg[df_seg['Segment'] == 'Business Users']['Count'].iloc[0]
                        gen_c = df_seg[df_seg['Segment'] == 'Generic Users']['Count'].iloc[0]
                        blk_c = df_seg[df_seg['Segment'] == 'Invalid Users']['Count'].iloc[0]
                    except:
                        biz_c, gen_c, blk_c = 0, 0, 0

                    labels = ["Business", "Generic", "Blocked"]
                    values = [biz_c, gen_c, blk_c]
                    fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5, 
                                                   marker=dict(colors=['#ff6600', '#9e9e9e', '#333']))])
                    fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_pie, use_container_width=True)
                
            with col_b2:
                st.subheader("User Engagement Depth")
                st.info(TOOLTIPS["engagement"])
                if data.get("User_Engagement") is not None:
                    df_eng = data["User_Engagement"]
                    df_eng_plot = df_eng[df_eng['Metric'].str.contains("Users with", na=False)]
                    
                    fig_eng = px.bar(df_eng_plot, x='Metric', y='Count', color='Metric',
                                   color_discrete_sequence=['#ff6600', '#cc5200', '#993d00'])
                    fig_eng.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
                    st.plotly_chart(fig_eng, use_container_width=True)
            
            st.subheader("Badge Statistics")
            if data.get("Badges_Issued") is not None:
                st.dataframe(data["Badges_Issued"], use_container_width=True, hide_index=True)

    else:
        st.error("Could not load data. Please ensure the Excel file is present.")
