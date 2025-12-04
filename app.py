import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION (Must be first) ---
st.set_page_config(page_title="Course Analytics Dashboard", layout="wide", page_icon="📊")

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
    # --- 3. DATA LOADING ---
    @st.cache_data
    def load_data():
        # Mapping your specific filenames to easy-to-use keys
        files = {
            "Master": "final_unified_master_with_segments.xlsx - Master.csv",
            "Monthly_Enroll": "final_unified_master_with_segments.xlsx - Monthly Enrollments.csv",
            "Monthly_Unique": "final_unified_master_with_segments.xlsx - Unique Monthly Users.csv",
            "Country": "final_unified_master_with_segments.xlsx - Country Breakdown.csv",
            "Course": "final_unified_master_with_segments.xlsx - Course Breakdown.csv",
            "Completion": "final_unified_master_with_segments.xlsx - Starter Completion Avg.csv",
            "Business_Email": "final_unified_master_with_segments.xlsx - Business Emails.csv",
            "Generic_Email": "final_unified_master_with_segments.xlsx - Generic Emails.csv",
            "Blocked_Email": "final_unified_master_with_segments.xlsx - Blocked Emails.csv"
        }
        
        data = {}
        for key, filename in files.items():
            try:
                data[key] = pd.read_csv(filename)
            except FileNotFoundError:
                st.warning(f"File not found: {filename}")
        return data

    data = load_data()

    if data:
        # --- 4. DASHBOARD HEADER & KPIs ---
        st.title("📊 Course Enrollment & User Analytics")
        st.markdown(f"**Data loaded successfully.** *Last update: {pd.Timestamp.now().strftime('%Y-%m-%d')}*")
        st.markdown("---")

        # Calculate KPIs
        total_enrolls = data["Course"]["Sign Ups"].sum() if "Course" in data else 0
        total_unique = data["Monthly_Unique"]["Unique User Signups"].sum() if "Monthly_Unique" in data else 0
        
        # Calculate Email Quality Split
        biz_count = len(data["Business_Email"]) if "Business_Email" in data else 0
        gen_count = len(data["Generic_Email"]) if "Generic_Email" in data else 0
        blocked_count = len(data["Blocked_Email"]) if "Blocked_Email" in data else 0
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Course Enrollments", f"{total_enrolls:,}")
        kpi1.caption("Total seats taken")
        
        kpi2.metric("Total Unique Users", f"{total_unique:,}")
        kpi2.caption("Distinct individuals")
        
        kpi3.metric("Business Users", f"{biz_count:,}")
        kpi3.caption(f"{(biz_count/(biz_count+gen_count+blocked_count+1))*100:.1f}% of total")
        
        top_country = data["Country"].sort_values("Total Course Signups", ascending=False).iloc[0]["Country"]
        kpi4.metric("Top Region", top_country)

        # --- 5. TABS ---
        tab_growth, tab_geo, tab_content, tab_qual = st.tabs(["📈 Growth Trends", "🌍 Geography", "📚 Content Analysis", "💎 User Quality"])

        # TAB 1: GROWTH
        with tab_growth:
            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                st.subheader("Enrollments vs. Unique Users")
                # Prepare data
                df_enroll = data["Monthly_Enroll"].copy()
                df_enroll['Month'] = pd.to_datetime(df_enroll['Month'])
                df_unique = data["Monthly_Unique"].copy()
                df_unique['Month'] = pd.to_datetime(df_unique['Month'])
                
                # Merge for single chart
                df_trend = pd.merge(df_enroll, df_unique, on="Month", how="outer").fillna(0)
                df_trend = df_trend.sort_values("Month")
                
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(x=df_trend['Month'], y=df_trend['Enrollments'], mode='lines+markers', name='Total Enrollments'))
                fig_trend.add_trace(go.Scatter(x=df_trend['Month'], y=df_trend['Unique User Signups'], mode='lines', name='Unique Users', line=dict(dash='dash')))
                st.plotly_chart(fig_trend, use_container_width=True)

            with col_g2:
                st.subheader("Monthly Growth Table")
                df_display = df_trend.copy()
                df_display['Month'] = df_display['Month'].dt.date
                st.dataframe(df_display, hide_index=True, use_container_width=True)

        # TAB 2: GEOGRAPHY
        with tab_geo:
            col_map, col_bar = st.columns([2, 1])
            with col_map:
                st.subheader("Global User Distribution")
                fig_map = px.choropleth(data["Country"], locations="Country", locationmode='country names',
                                        color="Total Course Signups", color_continuous_scale="Viridis",
                                        hover_name="Country")
                st.plotly_chart(fig_map, use_container_width=True)
            
            with col_bar:
                st.subheader("Top 15 Countries")
                top_countries = data["Country"].sort_values("Total Course Signups", ascending=False).head(15)
                fig_bar_geo = px.bar(top_countries, x="Total Course Signups", y="Country", orientation='h', color="Total Course Signups")
                fig_bar_geo.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_bar_geo, use_container_width=True)

        # TAB 3: CONTENT
        with tab_content:
            col_c1, col_c2 = st.columns(2)
            
            with col_c1:
                st.subheader("Most Popular Courses")
                df_course = data["Course"].sort_values("Sign Ups", ascending=False).head(10)
                fig_course = px.bar(df_course, x="Sign Ups", y="Course", orientation='h', color_discrete_sequence=['#636EFA'])
                fig_course.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_course, use_container_width=True)
                
            with col_c2:
                st.subheader("Completion Rates (Starter Kits)")
                if "Completion" in data:
                    df_comp = data["Completion"].sort_values("Avg Completion %", ascending=True)
                    fig_comp = px.bar(df_comp, x="Avg Completion %", y="Starter Kit", orientation='h', 
                                      color="Avg Completion %", color_continuous_scale="RdYlGn")
                    st.plotly_chart(fig_comp, use_container_width=True)
                else:
                    st.info("Completion data not available.")

        # TAB 4: USER QUALITY
        with tab_qual:
            col_q1, col_q2 = st.columns(2)
            with col_q1:
                st.subheader("User Account Types")
                labels = ["Business Emails", "Generic Emails", "Blocked/Spam"]
                values = [biz_count, gen_count, blocked_count]
                fig_pie = px.pie(names=labels, values=values, hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with col_q2:
                st.subheader("Email List Preview (Business)")
                if "Business_Email" in data:
                    st.dataframe(data["Business_Email"][["Name", "Email", "Category"]].head(50), hide_index=True)

    else:
        st.error("No data loaded. Please check CSV filenames.")
