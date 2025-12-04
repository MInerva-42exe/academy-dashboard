import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Analytics Dashboard", layout="wide", page_icon="📊")

# --- 2. PASSWORD PROTECTION ---
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter Password:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password incorrect. Try again:", type="password", on_change=password_entered, key="password")
        return False
    else:
        return True

if check_password():
    # --- 3. DATA LOADING (Excel Version) ---
    @st.cache_data
    def load_data():
        file_path = "final_unified_master_with_segments.xlsx"
        
        try:
            # Read all sheets at once
            xls = pd.read_excel(file_path, sheet_name=None)
            
            # Map your Sheet Names to the App's Internal Keys
            data = {}
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
            st.error(f"Could not find file: {file_path}. Please make sure you uploaded the Excel file to GitHub.")
            return None
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")
            return None

    data = load_data()

    if data:
        # --- 4. DASHBOARD HEADER & KPIs ---
        st.title("📊 Course Enrollment & User Analytics")
        st.markdown(f"**Data Source:** *{pd.Timestamp.now().strftime('%Y-%m-%d')}*")
        st.markdown("---")

        # Calculate KPIs
        total_enrolls = data["Course"]["Sign Ups"].sum() if data.get("Course") is not None else 0
        total_unique = data["Monthly_Unique"]["Unique User Signups"].sum() if data.get("Monthly_Unique") is not None else 0
        
        # Calculate Email Quality Split
        biz_count = len(data["Business_Email"]) if data.get("Business_Email") is not None else 0
        gen_count = len(data["Generic_Email"]) if data.get("Generic_Email") is not None else 0
        blocked_count = len(data["Blocked_Email"]) if data.get("Blocked_Email") is not None else 0
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Enrollments", f"{total_enrolls:,}")
        kpi2.metric("Unique Users", f"{total_unique:,}")
        kpi3.metric("Business Users", f"{biz_count:,}")
        
        if data.get("Country") is not None:
            top_country = data["Country"].sort_values("Total Course Signups", ascending=False).iloc[0]["Country"]
            kpi4.metric("Top Region", top_country)

        # --- 5. TABS ---
        tab_growth, tab_geo, tab_content, tab_qual = st.tabs(["📈 Growth", "🌍 Geography", "📚 Content", "💎 User Quality"])

        # TAB 1: GROWTH
        with tab_growth:
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.subheader("Enrollment Trends")
                if data.get("Monthly_Enroll") is not None and data.get("Monthly_Unique") is not None:
                    df_enroll = data["Monthly_Enroll"].copy()
                    df_enroll['Month'] = pd.to_datetime(df_enroll['Month'])
                    df_unique = data["Monthly_Unique"].copy()
                    df_unique['Month'] = pd.to_datetime(df_unique['Month'])
                    
                    df_trend = pd.merge(df_enroll, df_unique, on="Month", how="outer").fillna(0)
                    df_trend = df_trend.sort_values("Month")
                    
                    fig_trend = go.Figure()
                    fig_trend.add_trace(go.Scatter(x=df_trend['Month'], y=df_trend['Enrollments'], name='Total Enrollments'))
                    fig_trend.add_trace(go.Scatter(x=df_trend['Month'], y=df_trend['Unique User Signups'], name='Unique Users'))
                    st.plotly_chart(fig_trend, use_container_width=True)

        # TAB 2: GEOGRAPHY
        with tab_geo:
            if data.get("Country") is not None:
                col_map, col_bar = st.columns([2, 1])
                with col_map:
                    st.subheader("Global Map")
                    fig_map = px.choropleth(data["Country"], locations="Country", locationmode='country names',
                                            color="Total Course Signups", color_continuous_scale="Viridis")
                    st.plotly_chart(fig_map, use_container_width=True)
                with col_bar:
                    st.subheader("Top Regions")
                    top_10 = data["Country"].sort_values("Total Course Signups", ascending=False).head(10)
                    fig_bar = px.bar(top_10, x="Total Course Signups", y="Country", orientation='h')
                    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_bar, use_container_width=True)

        # TAB 3: CONTENT
        with tab_content:
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.subheader("Popular Courses")
                if data.get("Course") is not None:
                    df_course = data["Course"].sort_values("Sign Ups", ascending=False).head(10)
                    fig_course = px.bar(df_course, x="Sign Ups", y="Course", orientation='h')
                    fig_course.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_course, use_container_width=True)
            
            with col_c2:
                st.subheader("Completion Rates")
                if data.get("Completion") is not None:
                    df_comp = data["Completion"].sort_values("Avg Completion %", ascending=True)
                    fig_comp = px.bar(df_comp, x="Avg Completion %", y="Starter Kit", orientation='h', color="Avg Completion %")
                    st.plotly_chart(fig_comp, use_container_width=True)

        # TAB 4: QUALITY
        with tab_qual:
            col_q1, col_q2 = st.columns(2)
            with col_q1:
                st.subheader("User Segments")
                fig_pie = px.pie(names=["Business", "Generic", "Blocked"], values=[biz_count, gen_count, blocked_count])
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col_q2:
                st.subheader("Starter vs Non-Starter")
                if data.get("Starter_vs_Non") is not None:
                    st.dataframe(data["Starter_vs_Non"], hide_index=True)

    else:
        st.warning("Awaiting data... Please upload 'final_unified_master_with_segments.xlsx' to GitHub.")
