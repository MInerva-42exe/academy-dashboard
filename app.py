import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION & THEME ---
st.set_page_config(page_title="Analytics Dashboard", layout="wide")

# Minimal CSS to force Black Background & Orange Highlights
st.markdown("""
<style>
    /* Main Background - Pure Black */
    .stApp {
        background-color: #000000;
        color: #fafafa;
    }
    /* Metric/KPI Values - Orange */
    div[data-testid="stMetricValue"] {
        color: #ff6600 !important;
    }
    /* Tabs active line - Orange */
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        border-bottom-color: #ff6600 !important;
    }
    /* Multiselect Tag Color */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #333333 !important;
        color: #ffa500 !important;
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
        
        # Counts for Quality Tab
        biz_count = len(data["Business_Email"]) if data.get("Business_Email") is not None else 0
        gen_count = len(data["Generic_Email"]) if data.get("Generic_Email") is not None else 0
        blocked_count = len(data["Blocked_Email"]) if data.get("Blocked_Email") is not None else 0
        
        top_region = "N/A"
        if data.get("Country") is not None:
             top_region = data["Country"].sort_values("Total Course Signups", ascending=False).iloc[0]["Country"]

        # KPI Row
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
                
                df_trend = pd.merge(df_enroll, df_unique, on="Month", how="outer").fillna(0)
                df_trend = df_trend.sort_values("Month")
                
                df_trend['Month_Label'] = df_trend['Month'].dt.strftime('%b %Y')
                all_months = df_trend['Month_Label'].unique().tolist()
                filter_options = ["All Months"] + all_months
                
                default_months = df_trend[df_trend['Month'].dt.year >= 2025]['Month_Label'].unique().tolist()
                current_default = default_months if default_months else ["All Months"]

                selected_options = st.multiselect(
                    "Select Timeframe:",
                    options=filter_options,
                    default=current_default
                )
                
                if "All Months" in selected_options:
                    df_filtered = df_trend
                else:
                    df_filtered = df_trend[df_trend['Month_Label'].isin(selected_options)]
                    df_filtered = df_filtered.sort_values("Month")

                if not df_filtered.empty:
                    fig_trend = go.Figure()
                    fig_trend.add_trace(go.Scatter(x=df_filtered['Month'], y=df_filtered['Enrollments'], 
                                                 mode='lines+markers', name='Net User Enrollments',
                                                 line=dict(color='#ff6600', width=3))) 
                    fig_trend.add_trace(go.Scatter(x=df_filtered['Month'], y=df_filtered['Unique User Signups'], 
                                                 mode='lines', name='Unique Users',
                                                 line=dict(color='#ffffff', dash='dot'))) 
                    
                    fig_trend.update_layout(
                        template="plotly_dark", 
                        paper_bgcolor='rgba(0,0,0,0)', 
                        plot_bgcolor='rgba(0,0,0,0)', 
                        height=450,
                        margin=dict(l=0, r=0, t=20, b=0)
                    )
                    st.plotly_chart(fig_trend, use_container_width=True)
                    
                    st.markdown("### Detailed Data")
                    display_table = df_filtered[['Month_Label', 'Enrollments', 'Unique User Signups']].rename(
                        columns={'Month_Label': 'Month', 'Enrollments': 'Net User Enrollments'}
                    )
                    st.dataframe(display_table, use_container_width=True, hide_index=True)
                else:
                    st.info("Please select 'All Months' or specific months to view data.")

        # TAB 2: GEOGRAPHY (SINGLE TITLE)
        with tab_geo:
            st.subheader("Users by Country")  # Single Unified Title
            
            col_map, col_tree = st.columns([1, 1])
            with col_map:
                if data.get("Country") is not None:
                    fig_map = px.choropleth(data["Country"], locations="Country", locationmode='country names',
                                            color="Total Course Signups", 
                                            color_continuous_scale=["#1e1e1e", "#ff6600"])
                    fig_map.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', geo=dict(bgcolor='rgba(0,0,0,0)'))
                    st.plotly_chart(fig_map, use_container_width=True)
            
            with col_tree:
                if data.get("Country") is not None:
                    df_tree = data["Country"].sort_values("Total Course Signups", ascending=False).head(30)
                    
                    fig_tree = px.treemap(
                        df_tree, 
                        path=['Country'], 
                        values='Total Course Signups',
                        color='Total Course Signups',
                        color_continuous_scale=[[0, "#444"], [1, "#ff6600"]]
                    )
                    
                    fig_tree.update_layout(
                        template="plotly_dark",
                        paper_bgcolor='rgba(0,0,0,0)', # Transparent
                        plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(t=0, l=0, r=0, b=0), # Tight fit
                        height=450,
                        # VISIBLE BORDER AROUND TREEMAP
                        shapes=[dict(
                            type="rect", 
                            xref="paper", yref="paper",
                            x0=0, y0=0, x1=1, y1=1,
                            line=dict(color="#333", width=2)
                        )]
                    )
                    # Clean black borders between blocks
                    fig_tree.update_traces(
                        hovertemplate='<b>%{label}</b><br>Signups: %{value}',
                        marker=dict(line=dict(color='#000000', width=1)) 
                    )
                    
                    st.plotly_chart(fig_tree, use_container_width=True)

        # TAB 3: CONTENT
        with tab_content:
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.subheader("Popular Courses")
                if data.get("Course") is not None:
                    df_course = data["Course"].sort_values("Sign Ups", ascending=False).head(10)
                    fig_course = px.bar(df_course, x="Sign Ups", y="Course", orientation='h')
                    fig_course.update_traces(marker_color='#ff6600') 
                    fig_course.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_course, use_container_width=True)
            
            with col_c2:
                st.subheader("Completion Rates")
                if data.get("Completion") is not None:
                    df_comp = data["Completion"].sort_values("Avg Completion %", ascending=True)
                    fig_comp = px.bar(df_comp, x="Avg Completion %", y="Starter Kit", orientation='h')
                    fig_comp.update_traces(marker=dict(color=df_comp["Avg Completion %"], colorscale=[[0, "#333"], [1, "#ff6600"]]))
                    fig_comp.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_comp, use_container_width=True)

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
