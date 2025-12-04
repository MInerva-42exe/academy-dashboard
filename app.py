import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION & THEME ---
st.set_page_config(page_title="Analytics Dashboard", layout="wide")

# CSS: Import Google Fonts (Lato), Black Background, & Styling
st.markdown("""
<style>
    /* --- FONTS --- */
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Lato', sans-serif !important;
    }

    /* --- GLOBAL THEME --- */
    .stApp {
        background-color: #000000;
        color: #fafafa;
    }
    
    div[data-testid="stMetricValue"] {
        color: #ff6600 !important;
    }

    .stMultiSelect [data-baseweb="tag"] {
        background-color: #333333 !important;
        color: #ffa500 !important;
    }

    /* --- TAB STYLING --- */
    .stTabs [data-baseweb="tab-list"] {
        width: 100%;
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        flex-grow: 1;
        text-align: center;
        height: 50px;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 5px 5px 0 0;
        color: #9CA3AF;
        border: none;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(255, 102, 0, 0.15);
        color: #ff6600;
        border-bottom: 3px solid #ff6600;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255, 255, 255, 0.1);
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

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
        
        biz_count = len(data["Business_Email"]) if data.get("Business_Email") is not None else 0
        gen_count = len(data["Generic_Email"]) if data.get("Generic_Email") is not None else 0
        blocked_count = len(data["Blocked_Email"]) if data.get("Blocked_Email") is not None else 0
        
        top_region = "N/A"
        if data.get("Country") is not None:
             top_region = data["Country"].sort_values("Total Course Signups", ascending=False).iloc[0]["Country"]

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Net User Enrollments", f"{total_enrolls:,}")
        kpi2.metric("Unique Users", f"{total_unique:,}")
        kpi3.metric("Business Accounts", f"{biz_count:,}")
        kpi4.metric("Top Region", top_region)

        # --- 5. TABS ---
        tab_growth, tab_geo, tab_content, tab_qual = st.tabs(["Growth", "Geography", "Courses", "Quality"])

        # TAB 1: GROWTH
        with tab_growth:
            st.subheader("Enrollment Trends")
            if data.get("Monthly_Enroll") is not None and data.get("Monthly_Unique") is not None:
                df_enroll = data["Monthly_Enroll"].copy()
                df_enroll['Month'] = pd.to_datetime(df_enroll['Month'])
                df_unique = data["Monthly_Unique"].copy()
                df_unique['Month'] = pd.to_datetime(df_unique['Month'])
                
                df_trend = pd.merge(df_enroll, df_unique, on="Month", how="outer").fillna(0).sort_values("Month")
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
                    fig_trend = go.Figure()
                    fig_trend.add_trace(go.Scatter(x=df_filtered['Month'], y=df_filtered['Enrollments'], 
                                                 mode='lines+markers', name='Net User Enrollments',
                                                 line=dict(color='#ff6600', width=3))) 
                    fig_trend.add_trace(go.Scatter(x=df_filtered['Month'], y=df_filtered['Unique User Signups'], 
                                                 mode='lines', name='Unique Users',
                                                 line=dict(color='#ffffff', dash='dot'))) 
                    fig_trend.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                          height=450, margin=dict(l=0, r=0, t=20, b=0))
                    st.plotly_chart(fig_trend, use_container_width=True)
                    
                    st.markdown("### Detailed Data")
                    display_table = df_filtered[['Month_Label', 'Enrollments', 'Unique User Signups']].rename(
                        columns={'Month_Label': 'Month', 'Enrollments': 'Net User Enrollments'}
                    )
                    st.dataframe(display_table, use_container_width=True, hide_index=True)
                else:
                    st.info("Please select 'All Months' or specific months.")

        # TAB 2: GEOGRAPHY (LOCKED MAP)
        with tab_geo:
            st.subheader("Users by Country")
            
            if data.get("Country") is not None:
                # Filter Logic
                all_regions = sorted(data["Country"]["Region"].unique().tolist())
                filter_options_geo = ["All"] + all_regions
                selected_regions = st.multiselect("Select Region:", options=filter_options_geo, default=["All"])
                
                if "All" in selected_regions:
                    df_geo_filtered = data["Country"]
                else:
                    df_geo_filtered = data["Country"][data["Country"]["Region"].isin(selected_regions)]

                col_map, col_tree = st.columns([1, 1])
                with col_map:
                    # --- LOCKED MAP CONFIGURATION ---
                    fig_map = px.choropleth(df_geo_filtered, locations="Country", locationmode='country names',
                                            color="Total Course Signups", 
                                            color_continuous_scale=["#1e1e1e", "#ff6600"])
                    
                    fig_map.update_layout(
                        template="plotly_dark", 
                        paper_bgcolor='rgba(0,0,0,0)', 
                        geo=dict(
                            bgcolor='rgba(0,0,0,0)',
                            projection_type="natural earth", 
                        ),
                        dragmode="pan", 
                        height=500,     
                        margin=dict(l=0, r=0, t=0, b=0)
                    )
                    
                    config = {
                        'scrollZoom': True,       
                        'displayModeBar': False,   
                        'showTips': False
                    }
                    
                    st.plotly_chart(fig_map, use_container_width=True, config=config)
                
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

        # TAB 3: CONTENT (UPDATED WITH ALL VALUES TABLE)
        with tab_content:
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.subheader("Popular Courses")
                if data.get("Course") is not None:
                    # Chart: Top 10
                    df_course_top = data["Course"].sort_values("Sign Ups", ascending=False).head(10)
                    fig_course = px.bar(df_course_top, x="Sign Ups", y="Course", orientation='h')
                    fig_course.update_traces(marker_color='#ff6600') 
                    fig_course.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_course, use_container_width=True)
                    
                    # Table: All Values
                    st.markdown("#### All Courses")
                    df_course_all = data["Course"].sort_values("Sign Ups", ascending=False)
                    st.dataframe(df_course_all, use_container_width=True, hide_index=True)
            
            with col_c2:
                st.subheader("Completion Rates")
                if data.get("Completion") is not None:
                    # Chart: All (or filtered if preferred, but usually small list)
                    df_comp = data["Completion"].sort_values("Avg Completion %", ascending=True)
                    fig_comp = px.bar(df_comp, x="Avg Completion %", y="Starter Kit", orientation='h')
                    fig_comp.update_traces(marker=dict(color=df_comp["Avg Completion %"], colorscale=[[0, "#333"], [1, "#ff6600"]]))
                    fig_comp.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_comp, use_container_width=True)
                    
                    # Table: All Values
                    st.markdown("#### Detailed Completion Stats")
                    # Display sorted high-to-low for table readability
                    st.dataframe(df_comp.sort_values("Avg Completion %", ascending=False), use_container_width=True, hide_index=True)

        # TAB 4: QUALITY
        with tab_qual:
            st.subheader("User Segmentation")
            labels = ["Business", "Generic", "Blocked"]
            values = [biz_count, gen_count, blocked_count]
            colors = ['#ff6600', '#9e9e9e', '#424242'] 
            
            fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5, marker=dict(colors=colors))])
            fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                st.plotly_chart(fig_pie, use_container_width=True)

    else:
        st.warning("Please upload 'final_unified_master_with_segments.xlsx' to GitHub.")
