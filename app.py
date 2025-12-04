import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Academy Analytics", layout="wide", page_icon="🎓")

# --- 2. INJECT CUSTOM CSS ---
st.markdown("""
<style>
  /* --- IMPORTED THEME CSS --- */
  @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

  /* Force Dark Background for the App */
  .stApp {
    background-color: #0f1115; /* Deep dark background */
    font-family: "Zoho Puvi", "Roboto", sans-serif;
  }

  /* --- YOUR PROVIDED STYLES (Adapted for Streamlit) --- */
  
  /* Widget Scope / Container */
  .me-widget-scope {
    font-family: "Zoho Puvi", system-ui, -apple-system, sans-serif !important;
    width: 100%;
    padding-bottom: 80px; 
  }

  /* KPI Cards (Styled like Nav Buttons) */
  .kpi-card {
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(12px);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    color: #fff;
    transition: all 0.3s ease;
  }
  .kpi-card:hover {
    border-color: #ff6600;
    box-shadow: 0 4px 12px rgba(255, 102, 0, 0.2);
    transform: translateY(-2px);
  }
  .kpi-value { font-size: 28px; font-weight: 700; color: #ff6600; }
  .kpi-label { font-size: 14px; color: #9CA3AF; margin-top: 5px; text-transform: uppercase; letter-spacing: 1px; }

  /* Headings */
  .me-featured-heading {
    font-size: 24px;
    font-weight: 400; 
    margin: 30px 0 20px 0;
    color: #FFFFFF; 
    border-left: 5px solid #ff6600; 
    padding-left: 15px;
  }

  /* --- COURSE CARD STYLES --- */
  .me-course-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 25px;
    padding-bottom: 20px;
  }

  .me-course-card {
    background: rgba(255, 255, 255, 0.03); /* Slightly transparent */
    border-radius: 16px;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    height: 100%;
    display: flex;
    flex-direction: column;
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  .me-course-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
    border-color: #ff6600;
  }

  .me-course-banner {
    height: 140px;
    background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .me-course-icon {
    font-size: 40px;
    opacity: 0.8;
  }

  .me-course-body {
    padding: 20px;
    display: flex;
    flex-direction: column;
    flex: 1;
    justify-content: space-between;
  }

  .me-course-title {
    font-size: 16px;
    line-height: 1.4;
    font-weight: 700;
    color: #fff;
    margin: 0 0 8px 0;
    min-height: 44px; /* Ensure alignment */
  }

  .me-course-subtitle {
    font-size: 13px;
    line-height: 1.6;
    color: #9CA3AF;
    margin-bottom: 16px;
  }

  .me-bundle-badge {
    background-color: rgba(255, 102, 0, 0.15); 
    color: #ff6600; 
    font-size: 11px;
    font-weight: 600;
    padding: 4px 8px;
    border-radius: 4px;
    text-transform: uppercase;
    border: 1px solid rgba(255, 102, 0, 0.3); 
    width: fit-content;
  }

  /* Streamlit Tweaks */
  div[data-testid="stMetricValue"] { color: #ff6600 !important; }
  
  /* Tabs */
  .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
  .stTabs [data-baseweb="tab"] {
    height: 50px;
    background-color: rgba(255,255,255,0.05);
    border-radius: 5px 5px 0 0;
    color: #9CA3AF;
    border: none;
  }
  .stTabs [data-baseweb="tab"][aria-selected="true"] {
    background-color: rgba(255, 102, 0, 0.1);
    color: #ff6600;
    border-bottom: 2px solid #ff6600;
  }
</style>
""", unsafe_allow_html=True)

# --- 3. PASSWORD PROTECTION ---
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
    # --- 4. DATA LOADING ---
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
            return data
        except FileNotFoundError:
            st.error(f"Could not find {file_path}. Please upload it to GitHub.")
            return None
        except Exception as e:
            st.error(f"Error reading file: {e}")
            return None

    data = load_data()

    if data:
        # --- 5. DASHBOARD LAYOUT ---
        
        # Header
        st.markdown('<div class="me-featured-heading">Academy Analytics Dashboard</div>', unsafe_allow_html=True)

        # Calculate KPIs
        total_enrolls = data["Course"]["Sign Ups"].sum() if data.get("Course") is not None else 0
        total_unique = data["Monthly_Unique"]["Unique User Signups"].sum() if data.get("Monthly_Unique") is not None else 0
        biz_count = len(data["Business_Email"]) if data.get("Business_Email") is not None else 0
        top_region = "N/A"
        if data.get("Country") is not None:
             top_region = data["Country"].sort_values("Total Course Signups", ascending=False).iloc[0]["Country"]

        # Custom KPI HTML Cards
        kpi_html = f"""
        <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 30px;">
            <div class="kpi-card" style="flex: 1;">
                <div class="kpi-value">{total_enrolls:,}</div>
                <div class="kpi-label">Total Enrollments</div>
            </div>
            <div class="kpi-card" style="flex: 1;">
                <div class="kpi-value">{total_unique:,}</div>
                <div class="kpi-label">Unique Learners</div>
            </div>
            <div class="kpi-card" style="flex: 1;">
                <div class="kpi-value">{biz_count:,}</div>
                <div class="kpi-label">Business Accounts</div>
            </div>
            <div class="kpi-card" style="flex: 1;">
                <div class="kpi-value">{top_region}</div>
                <div class="kpi-label">Top Region</div>
            </div>
        </div>
        """
        st.markdown(kpi_html, unsafe_allow_html=True)

        # Tabs
        tab_content, tab_growth, tab_geo, tab_qual = st.tabs(["📚 Course Catalog", "📈 Growth Trends", "🌍 Geography", "💎 User Quality"])

        # --- TAB 1: COURSE CATALOG (Using your CSS Cards) ---
        with tab_content:
            st.markdown('<div class="me-featured-heading">Top Performing Courses</div>', unsafe_allow_html=True)
            
            if data.get("Course") is not None:
                # Get Top Courses
                df_courses = data["Course"].sort_values("Sign Ups", ascending=False)
                
                # HTML Generation for Grid
                cards_html = '<div class="me-course-grid">'
                
                for index, row in df_courses.iterrows():
                    course_name = row['Course']
                    signups = row['Sign Ups']
                    
                    # Determine a badge based on signups
                    badge = "BESTSELLER" if signups > 100 else "POPULAR" if signups > 50 else "COURSE"
                    
                    cards_html += f"""
                    <div class="me-course-card">
                        <div class="me-course-banner">
                            <div class="me-course-icon">🎓</div>
                        </div>
                        <div class="me-course-body">
                            <div>
                                <div class="me-bundle-badge">{badge}</div>
                                <div class="me-course-title">{course_name}</div>
                                <div class="me-course-subtitle">Total Enrollments: {signups}</div>
                            </div>
                            <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 10px; margin-top: 10px; font-size: 12px; color: #6B7280;">
                                Academy Content
                            </div>
                        </div>
                    </div>
                    """
                
                cards_html += '</div>'
                st.markdown(cards_html, unsafe_allow_html=True)

        # --- TAB 2: GROWTH (Dark Mode Charts) ---
        with tab_growth:
            st.markdown('<div class="me-featured-heading">Enrollment Velocity</div>', unsafe_allow_html=True)
            
            if data.get("Monthly_Enroll") is not None and data.get("Monthly_Unique") is not None:
                df_enroll = data["Monthly_Enroll"].copy()
                df_enroll['Month'] = pd.to_datetime(df_enroll['Month'])
                df_unique = data["Monthly_Unique"].copy()
                df_unique['Month'] = pd.to_datetime(df_unique['Month'])
                
                df_trend = pd.merge(df_enroll, df_unique, on="Month", how="outer").fillna(0).sort_values("Month")
                
                # Plotly with Dark/Orange Theme
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(x=df_trend['Month'], y=df_trend['Enrollments'], 
                                             mode='lines+markers', name='Total Enrollments',
                                             line=dict(color='#ff6600', width=3)))
                fig_trend.add_trace(go.Scatter(x=df_trend['Month'], y=df_trend['Unique User Signups'], 
                                             mode='lines', name='Unique Users',
                                             line=dict(color='#ffffff', dash='dot')))
                
                fig_trend.update_layout(template="plotly_dark", 
                                      paper_bgcolor='rgba(0,0,0,0)', 
                                      plot_bgcolor='rgba(0,0,0,0)',
                                      height=500)
                st.plotly_chart(fig_trend, use_container_width=True)

        # --- TAB 3: GEOGRAPHY ---
        with tab_geo:
            col_map, col_bar = st.columns([2, 1])
            with col_map:
                st.markdown('<div class="me-featured-heading">Global Reach</div>', unsafe_allow_html=True)
                if data.get("Country") is not None:
                    fig_map = px.choropleth(data["Country"], locations="Country", locationmode='country names',
                                            color="Total Course Signups", 
                                            color_continuous_scale=["#2c2c2c", "#ff6600"])
                    fig_map.update_layout(template="plotly_dark", 
                                        paper_bgcolor='rgba(0,0,0,0)',
                                        geo=dict(bgcolor='rgba(0,0,0,0)', showframe=False))
                    st.plotly_chart(fig_map, use_container_width=True)
            
            with col_bar:
                st.markdown('<div class="me-featured-heading">Top Regions</div>', unsafe_allow_html=True)
                if data.get("Country") is not None:
                    top_10 = data["Country"].sort_values("Total Course Signups", ascending=False).head(10)
                    fig_bar = px.bar(top_10, x="Total Course Signups", y="Country", orientation='h')
                    fig_bar.update_traces(marker_color='#ff6600')
                    fig_bar.update_layout(template="plotly_dark", 
                                        paper_bgcolor='rgba(0,0,0,0)', 
                                        plot_bgcolor='rgba(0,0,0,0)',
                                        yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_bar, use_container_width=True)

        # --- TAB 4: QUALITY ---
        with tab_qual:
            st.markdown('<div class="me-featured-heading">User Segmentation</div>', unsafe_allow_html=True)
            col_q1, col_q2 = st.columns(2)
            
            with col_q1:
                labels = ["Business Emails", "Generic Emails", "Blocked/Spam"]
                values = [biz_count, gen_count, blocked_count]
                colors = ['#ff6600', '#ffffff', '#374151'] # Orange, White, Dark Grey
                
                fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5, marker=dict(colors=colors))])
                fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col_q2:
                st.markdown("### Business Accounts Preview")
                if data.get("Business_Email") is not None:
                    st.dataframe(data["Business_Email"][["Name", "Email", "Category"]].head(20), hide_index=True)

    else:
        st.warning("Please upload 'final_unified_master_with_segments.xlsx' to GitHub.")
