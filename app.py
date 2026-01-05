import os
import datetime as dt
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Optional, List, Tuple

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# =========================
# 0) CACHE / VERSIONING
# =========================
CACHE_VERSION = "2026-01-05.dashboard.v4"
CACHE_TTL_SECONDS = 3600  # 1 hour


# =========================
# 1) PAGE CONFIGURATION
# =========================
st.set_page_config(page_title="ManageEngine User Academy Dashboard", layout="wide")

st.markdown(
    """
<style>
:root { --accent:#FF6600; --text-muted:#9CA3AF; --text-primary:#F9FAFB; }
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
.stApp, .stApp * { font-family:'Inter', sans-serif !important; }
.stApp { background: radial-gradient(circle at 50% 50%, rgba(16,16,24,1), #000); background-attachment: fixed; color: var(--text-primary); }
.main .block-container { padding:1.6rem 2.2rem !important; max-width:1650px !important; }
h1 { background: linear-gradient(135deg,#FFF 0%, var(--accent) 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-weight:900 !important; font-size:2.3rem !important; margin-bottom: 0.2rem !important; }
h2,h3 { color: var(--text-primary) !important; }
.small-muted { color: var(--text-muted); font-size: 0.9rem; }
.section-title { margin-top: 0.6rem; margin-bottom: 0.2rem; font-weight: 800; font-size: 1.15rem; }
.section-divider { height: 1px; background: rgba(255,255,255,0.08); margin: 0.8rem 0 0.9rem 0; border-radius: 999px; }
.stTabs [data-baseweb="tab-list"] { display:flex; width:100%; gap:8px; background: rgba(255,255,255,0.03); padding:8px; border-radius: 14px; }
.stTabs [data-baseweb="tab"] { flex-grow:1; justify-content:center; background:transparent; color:var(--text-muted); font-weight:700; border-radius: 10px; border:none; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { background: var(--accent); color:white; box-shadow:0 4px 12px rgba(255,102,0,0.28); }
div[data-testid="stPlotlyChart"] { background: rgba(20,20,30,0.42); border-radius: 16px; padding: 0.75rem; border: 1px solid rgba(255,255,255,0.05); }
div[data-testid="metric-container"] { background: rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); border-radius: 14px; padding: 0.9rem; }
div[data-testid="stMetricValue"] { color: var(--accent) !important; }
.stAlert { background: rgba(30,41,59,0.75); border:1px solid rgba(255,255,255,0.10); color:#E2E8F0; font-size:0.92rem; }
</style>
""",
    unsafe_allow_html=True,
)


# =========================
# 2) CONSTANTS
# =========================
FILE_PATH = "ManageEngine User Academy Stats - Single Source of Truth.xlsx"

ACCENT = "#ff6600"
BLUE = "#3B82F6"
DARK = "#333"
SOFT_GRAY = "#9e9e9e"
LILAC = "#A5B4FC"
MID_GRAY_1 = "#666"
MID_GRAY_2 = "#999"
INK = "#111827"

DARK_LAYOUT = dict(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
CHART_CONFIG = {"scrollZoom": True, "displayModeBar": True}

SHORTNAME_MAX_LEN = 35
DEFAULT_RANGE_MONTHS = 12
DEFAULT_PAGE_SIZE = 50

# If your funnel stages are stable, set canonical order here.
# If not, sheet order is used, and we compute stage-to-stage drop%.
FUNNEL_STAGE_ORDER = ["Enrolled", "Started", "In Progress", "Completed"]

TOOLTIPS = {
    "mau": "Monthly Active Users: unique users who engaged with the academy in a given month.",
    "activation": "D30 Activation: % of new signups who hit an activation event within 30 days.",
    "funnel": "Drop-off Funnel: shows how users progress through key stages (and where they drop).",
    "enrollment_trend": "Enrollments over time (monthly).",
    "signup_trend": "Unique sign-ups over time (monthly).",
    "geo": "Global distribution of users by country.",
    "popular": "Courses with the highest cumulative sign-ups.",
    "segmentation": "Users bucketed by email type: Business vs Generic vs Invalid.",
    "engagement": "How deep users go: distribution by number of courses enrolled.",
    "completion": "Average completion % per course.",
    "compare": "Compare Mode overlays the previous period (same length) to show directionality and magnitude.",
}

SHEET_MAP = {
    "Monthly_Enroll": "Monthly Enrollments",
    "Monthly_Unique": "Monthly User Sign-Ups",
    "Country": "Country Breakdown",
    "Course": "Course Sign-Up Sheet",
    "Completion": "Completion Percentage",
    "MAU": "MAU",
    "Activation": "Activation Rate (D30)",
    "DropOff_Split": "Drop-off Stage Split",
    "Course_DropOff": "Course Drop-off (All)",
    "User_Engagement": "User and Course Engagement",
    "Badges_Issued": "Badges Issued",
    "User_Segmentation": "User Segmentation",
}

PRESETS = {
    "Default": dict(months_back=12, segment="All", compare=False, top_countries=10, top_courses=15),
    "Executive Summary": dict(months_back=6, segment="All", compare=True, top_countries=10, top_courses=10),
    "Content Team": dict(months_back=12, segment="All", compare=True, top_countries=10, top_courses=25),
    "Geo Team": dict(months_back=12, segment="All", compare=False, top_countries=25, top_courses=10),
    "Business-only": dict(months_back=12, segment="Business", compare=True, top_countries=10, top_courses=15),
}


# =========================
# 3) UTILS
# =========================
def is_valid_df(df: Optional[pd.DataFrame]) -> bool:
    return df is not None and isinstance(df, pd.DataFrame) and not df.empty

def has_cols(df: pd.DataFrame, cols: List[str]) -> bool:
    return all(c in df.columns for c in cols)

def to_num_series(s: pd.Series, default: float = 0.0) -> pd.Series:
    out = pd.to_numeric(s, errors="coerce")
    return out.fillna(default)

def to_int_safe(x, default: int = 0) -> int:
    try:
        if pd.isna(x):
            return default
        return int(float(x))
    except (ValueError, TypeError, OverflowError):
        return default

def month_end_from_mmm_yyyy(series: pd.Series) -> pd.Series:
    dt0 = pd.to_datetime(series, format="%b %Y", errors="coerce")
    return dt0 + pd.offsets.MonthEnd(0)

def build_shortname(course_series: pd.Series, max_len: int = SHORTNAME_MAX_LEN) -> pd.Series:
    s = course_series.astype(str).fillna("")
    return s.where(s.str.len().le(max_len), s.str.slice(0, max_len) + "...")

def file_mtime_seconds(path: str) -> int:
    try:
        return int(os.path.getmtime(path))
    except OSError:
        return 0

def mtime_rounded_minute(mtime_sec: int) -> int:
    return (mtime_sec // 60) * 60 if mtime_sec > 0 else 0

def info_expander(title: str, body: str):
    with st.expander(f"ⓘ {title}", expanded=False):
        st.write(body)

def percent_delta(curr: float, prev: float) -> str:
    # safe, readable formatting for deltas
    if prev == 0:
        return "—"
    return f"{((curr - prev) / prev) * 100:.1f}%"

@lru_cache(maxsize=2048)
def period_to_month_end_ts(p: pd.Period) -> pd.Timestamp:
    # end-of-month timestamp for filtering
    return (p.to_timestamp(how="end")).normalize() + pd.offsets.MonthEnd(0)

def get_metric_value(df: Optional[pd.DataFrame], metric_name, col_name="Metric", value_col="Count") -> int:
    if not is_valid_df(df) or col_name not in df.columns or value_col not in df.columns:
        return 0
    try:
        row = df.loc[df[col_name].eq(metric_name), value_col]
        if row.empty:
            return 0
        return to_int_safe(row.iloc[0], 0)
    except (KeyError, IndexError, ValueError, TypeError):
        return 0


# =========================
# 4) AUTH
# =========================
def check_password() -> bool:
    if st.session_state.get("password_correct"):
        return True

    secret_pw = st.secrets.get("password", None)
    if not secret_pw:
        st.error("Missing `password` in Streamlit secrets. Add it to `.streamlit/secrets.toml`.")
        return False

    def password_entered():
        st.session_state["password_correct"] = (st.session_state.get("password", "") == secret_pw)
        if "password" in st.session_state:
            del st.session_state["password"]

    prompt = "Enter Password:" if "password_correct" not in st.session_state else "Password incorrect."
    st.text_input(prompt, type="password", on_change=password_entered, key="password")
    return False


# =========================
# 5) DATA MODEL
# =========================
@dataclass
class Bundle:
    data: Dict[str, Optional[pd.DataFrame]]
    month_periods: List[pd.Period]
    updated_str: str

    total_enrolls: int
    total_unique: int
    total_badges: int
    current_mau: int


# =========================
# 6) LOAD RAW (CHEAP + CACHED)
# =========================
@st.cache_data(show_spinner=False, ttl=CACHE_TTL_SECONDS)
def load_raw(file_path: str, mtime_key_minute: int, cache_version: str) -> Optional[Bundle]:
    if not os.path.exists(file_path):
        return None

    xls = pd.ExcelFile(file_path)
    sheet_names = set(xls.sheet_names)

    data: Dict[str, Optional[pd.DataFrame]] = {}
    missing = []
    for key, sheet_name in SHEET_MAP.items():
        if sheet_name in sheet_names:
            data[key] = pd.read_excel(xls, sheet_name=sheet_name)
        else:
            data[key] = None
            missing.append(sheet_name)

    if missing:
        st.warning("Missing sheets in workbook: " + ", ".join(missing))

    # Standardize columns + add dt cols once
    if is_valid_df(data.get("Monthly_Enroll")):
        df = data["Monthly_Enroll"]
        df.rename(columns={"Number of enrollments": "Enrollments"}, inplace=True)
        if "Month" in df.columns:
            df["Month_dt"] = month_end_from_mmm_yyyy(df["Month"])

    if is_valid_df(data.get("Monthly_Unique")):
        df = data["Monthly_Unique"]
        df.rename(columns={"Number of Sign Ups": "Unique User Signups"}, inplace=True)
        if "Month" in df.columns:
            df["Month_dt"] = month_end_from_mmm_yyyy(df["Month"])

    if is_valid_df(data.get("MAU")):
        df = data["MAU"]
        if "Month" in df.columns:
            df["Month_dt"] = month_end_from_mmm_yyyy(df["Month"])

    if is_valid_df(data.get("Activation")):
        df = data["Activation"]
        if "Cohort" in df.columns:
            df["Cohort_dt"] = month_end_from_mmm_yyyy(df["Cohort"])

    if is_valid_df(data.get("Course")):
        df = data["Course"]
        df.rename(columns={"Course Name": "Course", "Course Sign-Ups": "Sign Ups"}, inplace=True)
        if "Course" in df.columns:
            df["ShortName"] = build_shortname(df["Course"])

    if is_valid_df(data.get("Completion")):
        df = data["Completion"]
        df.rename(columns={"Avg %": "Avg Completion %"}, inplace=True)
        if "Avg Completion %" in df.columns:
            df["Avg Completion %"] = to_num_series(df["Avg Completion %"], 0.0)

    # Month periods: break early when found
    month_periods: List[pd.Period] = []
    for key, col in [
        ("Monthly_Unique", "Month_dt"),
        ("Monthly_Enroll", "Month_dt"),
        ("MAU", "Month_dt"),
        ("Activation", "Cohort_dt"),
    ]:
        df = data.get(key)
        if is_valid_df(df) and col in df.columns:
            s = df[col].dropna()
            if not s.empty:
                month_periods = s.dt.to_period("M").sort_values().unique().tolist()
                break

    # KPIs (cheap)
    total_enrolls = 0
    if is_valid_df(data.get("Course")) and "Sign Ups" in data["Course"].columns:
        total_enrolls = to_int_safe(to_num_series(data["Course"]["Sign Ups"], 0).sum(), 0)

    total_unique = get_metric_value(data.get("User_Segmentation"), "Total Users")
    if total_unique == 0 and is_valid_df(data.get("Monthly_Unique")) and "Unique User Signups" in data["Monthly_Unique"].columns:
        total_unique = to_int_safe(to_num_series(data["Monthly_Unique"]["Unique User Signups"], 0).sum(), 0)

    current_mau = 0
    if is_valid_df(data.get("MAU")) and "MAU" in data["MAU"].columns:
        current_mau = to_int_safe(data["MAU"].iloc[-1]["MAU"], 0)

    total_badges = 0
    df_b = data.get("Badges_Issued")
    if is_valid_df(df_b):
        if has_cols(df_b, ["Metric", "Count"]):
            total_badges = get_metric_value(df_b, "Total Sent")
        else:
            try:
                c0, c1 = df_b.columns[0], df_b.columns[1]
                match = df_b.loc[df_b[c0].astype(str).eq("Total Sent"), c1]
                if not match.empty:
                    total_badges = to_int_safe(match.iloc[0], 0)
            except (IndexError, KeyError, ValueError, TypeError):
                total_badges = 0

    updated_str = (
        dt.datetime.fromtimestamp(mtime_key_minute).strftime("%Y-%m-%d %H:%M")
        if mtime_key_minute
        else dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    )

    return Bundle(
        data=data,
        month_periods=month_periods,
        updated_str=updated_str,
        total_enrolls=total_enrolls,
        total_unique=total_unique,
        total_badges=total_badges,
        current_mau=current_mau,
    )


# =========================
# 7) LAZY COMPUTES (TAB-SCOPED CACHE)
# =========================
@st.cache_data(show_spinner=False, ttl=CACHE_TTL_SECONDS)
def compute_geo_top(df_country: pd.DataFrame, top_n: int, cache_version: str) -> Optional[pd.DataFrame]:
    if not is_valid_df(df_country) or not has_cols(df_country, ["Country", "Total Course Signups"]):
        return None
    out = df_country[["Country", "Total Course Signups"]].copy()
    out["Total Course Signups"] = to_num_series(out["Total Course Signups"], 0)
    return out.nlargest(top_n, "Total Course Signups")

@st.cache_data(show_spinner=False, ttl=CACHE_TTL_SECONDS)
def compute_course_top(df_course: pd.DataFrame, top_n: int, cache_version: str) -> Optional[pd.DataFrame]:
    if not is_valid_df(df_course) or not has_cols(df_course, ["Course", "ShortName", "Sign Ups"]):
        return None
    out = df_course[["Course", "ShortName", "Sign Ups"]].copy()
    out["Sign Ups"] = to_num_series(out["Sign Ups"], 0)
    return out.nlargest(top_n, "Sign Ups")

@st.cache_data(show_spinner=False, ttl=CACHE_TTL_SECONDS)
def compute_course_perf(df_course: pd.DataFrame, df_completion: pd.DataFrame, cache_version: str) -> Optional[pd.DataFrame]:
    if not is_valid_df(df_course) or not is_valid_df(df_completion):
        return None
    if "Course" not in df_course.columns or "Course" not in df_completion.columns:
        return None
    left_cols = [c for c in ["Course", "ShortName", "Sign Ups"] if c in df_course.columns]
    right_cols = ["Course"]
    if "Avg Completion %" in df_completion.columns:
        right_cols.append("Avg Completion %")
    perf = pd.merge(df_course[left_cols], df_completion[right_cols], on="Course", how="left")
    if "Sign Ups" in perf.columns:
        perf["Sign Ups"] = to_num_series(perf["Sign Ups"], 0)
    if "Avg Completion %" in perf.columns:
        perf["Avg Completion %"] = to_num_series(perf["Avg Completion %"], 0.0)
    return perf

@st.cache_data(show_spinner=False, ttl=CACHE_TTL_SECONDS)
def compute_funnel(df_split: pd.DataFrame, stage_order: Tuple[str, ...], cache_version: str) -> Tuple[Optional[pd.DataFrame], Optional[str], Optional[pd.DataFrame]]:
    """
    Returns:
      - funnel df with pct and labels
      - warning (if stage order mismatch)
      - stage-to-stage drop table (diagnostic)
    """
    if not is_valid_df(df_split) or not has_cols(df_split, ["Stage", "All Count"]):
        return None, None, None

    df_f = df_split[["Stage", "All Count"]].copy()
    df_f["All Count"] = to_num_series(df_f["All Count"], 0)

    stage_lower = df_f["Stage"].astype(str).str.lower()
    stage_map = {s.lower(): i for i, s in enumerate(stage_order)}
    warning = None

    if stage_lower.isin(stage_map.keys()).all():
        df_f["_ord"] = stage_lower.map(stage_map)
        df_f.sort_values("_ord", inplace=True)
        df_f.drop(columns=["_ord"], inplace=True)
    else:
        warning = "Funnel stages don't fully match configured order; using sheet order."

    base = to_int_safe(df_f["All Count"].iloc[0], 0)
    if base <= 0:
        base = to_int_safe(df_f["All Count"].max(), 0)

    if base > 0:
        df_f["pct_of_base"] = (df_f["All Count"] / base * 100).round(1)
    else:
        df_f["pct_of_base"] = 0.0

    counts_str = df_f["All Count"].round(0).astype(int).map(str)
    pct_str = df_f["pct_of_base"].map(lambda v: f"{v:g}")
    df_f["text_label"] = counts_str + " (" + pct_str + "%)"

    # Stage-to-stage drop diagnostic
    drops = []
    for i in range(1, len(df_f)):
        prev_stage = str(df_f.iloc[i - 1]["Stage"])
        curr_stage = str(df_f.iloc[i]["Stage"])
        prev_val = float(df_f.iloc[i - 1]["All Count"])
        curr_val = float(df_f.iloc[i]["All Count"])
        drop_abs = prev_val - curr_val
        drop_pct = (drop_abs / prev_val * 100) if prev_val > 0 else 0.0
        drops.append(
            {
                "From → To": f"{prev_stage} → {curr_stage}",
                "Drop (users)": int(round(drop_abs)),
                "Drop (%)": round(drop_pct, 1),
            }
        )
    df_drop = pd.DataFrame(drops) if drops else None
    return df_f, warning, df_drop


# =========================
# 8) CHART BUILDERS
# =========================
def filter_range(df: pd.DataFrame, dt_col: str, start_dt: pd.Timestamp, end_dt: pd.Timestamp) -> pd.DataFrame:
    if not is_valid_df(df) or dt_col not in df.columns:
        return df
    m = df[dt_col].notna() & (df[dt_col] >= start_dt) & (df[dt_col] <= end_dt)
    return df.loc[m].sort_values(dt_col)

def create_line_compare_chart(
    df_cur: pd.DataFrame,
    x_col: str,
    y_col: str,
    df_prev: Optional[pd.DataFrame],
    name: str,
    color: str,
    height: int,
    compare_on: bool,
) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_cur[x_col], y=df_cur[y_col], mode="lines+markers", name=name,
                             line=dict(color=color, width=3)))
    if compare_on and df_prev is not None and is_valid_df(df_prev):
        fig.add_trace(go.Scatter(x=df_prev[x_col], y=df_prev[y_col], mode="lines", name="Previous period",
                                 line=dict(color=color, width=2, dash="dash"), opacity=0.7))
    fig.update_layout(**DARK_LAYOUT, height=height, xaxis=dict(fixedrange=False), dragmode="pan",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
    return fig

def create_sparkline(df: pd.DataFrame, x_col: str, y_col: str, color: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[x_col], y=df[y_col], mode="lines", line=dict(color=color, width=2)))
    fig.update_layout(
        **DARK_LAYOUT,
        height=90,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig

def create_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, color: str, text_col: Optional[str], height: int, x_title: Optional[str] = None) -> go.Figure:
    fig = px.bar(df, x=x_col, y=y_col, orientation="h", text=text_col)
    fig.update_traces(marker_color=color, textposition="outside")
    fig.update_layout(
        **DARK_LAYOUT,
        height=height,
        dragmode="pan",
        yaxis={"categoryorder": "total ascending", "automargin": True},
        xaxis_title=(x_title if x_title else x_col),
    )
    return fig


# =========================
# 9) COMPARE MODE HELPERS
# =========================
def previous_period_window(periods: List[pd.Period], start_p: pd.Period, end_p: pd.Period) -> Tuple[Optional[pd.Period], Optional[pd.Period]]:
    """
    Same-length window immediately preceding the selected window.
    Returns (prev_start, prev_end) or (None, None) if not enough history.
    """
    try:
        i0 = periods.index(start_p)
        i1 = periods.index(end_p)
    except ValueError:
        return None, None
    if i1 < i0:
        i0, i1 = i1, i0
    length = (i1 - i0) + 1
    prev_end_idx = i0 - 1
    prev_start_idx = prev_end_idx - (length - 1)
    if prev_start_idx < 0:
        return None, None
    return periods[prev_start_idx], periods[prev_end_idx]


# =========================
# 10) MAIN APP
# =========================
if not check_password():
    st.stop()

# Sidebar: global controls, saved views, and "progressive disclosure" knobs
with st.sidebar:
    st.markdown("### Dashboard Controls")

    # Presets
    preset = st.selectbox("Saved views", list(PRESETS.keys()), index=0)

    # Apply presets into session state (once per preset selection)
    if "preset_applied" not in st.session_state or st.session_state.get("preset_applied") != preset:
        cfg = PRESETS[preset]
        st.session_state["months_back"] = cfg["months_back"]
        st.session_state["segment"] = cfg["segment"]
        st.session_state["compare_mode"] = cfg["compare"]
        st.session_state["top_countries"] = cfg["top_countries"]
        st.session_state["top_courses"] = cfg["top_courses"]
        st.session_state["preset_applied"] = preset

    # Global filters
    months_back = st.slider("Default range (months)", 3, 24, int(st.session_state.get("months_back", 12)), 1)
    st.session_state["months_back"] = months_back

    segment = st.selectbox("Segment", ["All", "Business", "Generic", "Invalid"], index=["All", "Business", "Generic", "Invalid"].index(st.session_state.get("segment", "All")))
    st.session_state["segment"] = segment

    compare_mode = st.toggle("Compare mode (previous period)", value=bool(st.session_state.get("compare_mode", False)))
    st.session_state["compare_mode"] = compare_mode

    st.markdown("---")
    top_countries = st.number_input("Top countries", min_value=5, max_value=50, value=int(st.session_state.get("top_countries", 10)), step=1)
    top_courses = st.number_input("Top courses", min_value=5, max_value=50, value=int(st.session_state.get("top_courses", 15)), step=1)
    st.session_state["top_countries"] = int(top_countries)
    st.session_state["top_courses"] = int(top_courses)

    chart_height = st.slider("Chart height", 280, 520, 380, 10)

    # Global search
    course_search = st.text_input("Course search (global)", value=st.session_state.get("course_search", ""), placeholder="Filter course tables…")
    st.session_state["course_search"] = course_search

    # Refresh cache (scoped)
    if st.button("Refresh dashboard cache"):
        load_raw.clear()
        compute_geo_top.clear()
        compute_course_top.clear()
        compute_course_perf.clear()
        compute_funnel.clear()
        st.rerun()

mtime_key_minute = mtime_rounded_minute(file_mtime_seconds(FILE_PATH))
bundle = load_raw(FILE_PATH, mtime_key_minute, CACHE_VERSION)
if not bundle:
    st.error("Could not load data. Ensure the Excel file exists and is readable.")
    st.stop()

data = bundle.data

# Header
st.title("ManageEngine User Academy Dashboard")
st.markdown(f"<div class='small-muted'>Data updated: <b>{bundle.updated_str}</b> • Preset: <b>{preset}</b> • Segment: <b>{segment}</b></div>", unsafe_allow_html=True)
st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# Tabs (10 changes implemented across these)
tab_exec, tab_growth, tab_geo, tab_courses, tab_users = st.tabs(
    ["Executive Summary", "Growth & Retention", "Geography", "Course Performance", "User Insights"]
)

# Global date selection (Period slider): consistent and shared
all_periods = bundle.month_periods
if not all_periods:
    st.warning("No month/cohort data found to build time filters.")
    st.stop()

default_end = all_periods[-1]
default_start = all_periods[max(0, len(all_periods) - int(months_back))]

# Persist selected range across tabs
if "selected_range" not in st.session_state:
    st.session_state["selected_range"] = (default_start, default_end)

with st.sidebar:
    st.markdown("---")
    st.markdown("### Date Range (global)")
    selected_range = st.select_slider(
        "Select range",
        options=all_periods,
        value=st.session_state["selected_range"],
        format_func=lambda p: p.strftime("%b %Y"),
    )
    st.session_state["selected_range"] = selected_range

start_p, end_p = st.session_state["selected_range"]
start_dt = period_to_month_end_ts(start_p)
end_dt = period_to_month_end_ts(end_p)

prev_start_p, prev_end_p = previous_period_window(all_periods, start_p, end_p) if compare_mode else (None, None)
prev_start_dt = period_to_month_end_ts(prev_start_p) if prev_start_p else None
prev_end_dt = period_to_month_end_ts(prev_end_p) if prev_end_p else None

# =========================
# 11) EXEC SUMMARY (Change #1 + #4 + #10)
# =========================
with tab_exec:
    st.markdown("<div class='section-title'>Executive Summary</div>", unsafe_allow_html=True)
    info_expander("How to read this", "This tab is optimized for quick decisions: KPI movement + sparklines + the three most important insights.")
    info_expander("Compare mode", TOOLTIPS["compare"])

    # KPI snapshots + (optional) deltas vs previous period (computed from monthly frames when possible)
    kpi_cols = st.columns(4)

    # Helper to compute period sums from a monthly frame
    def sum_in_window(df: Optional[pd.DataFrame], dt_col: str, val_col: str, s_dt: pd.Timestamp, e_dt: pd.Timestamp) -> float:
        if not is_valid_df(df) or dt_col not in df.columns or val_col not in df.columns:
            return 0.0
        dfw = filter_range(df, dt_col, s_dt, e_dt)
        if not is_valid_df(dfw):
            return 0.0
        return float(to_num_series(dfw[val_col], 0).sum())

    # Current/previous sums for a few KPI-style signals (if available)
    cur_enroll_sum = sum_in_window(data.get("Monthly_Enroll"), "Month_dt", "Enrollments", start_dt, end_dt)
    prev_enroll_sum = sum_in_window(data.get("Monthly_Enroll"), "Month_dt", "Enrollments", prev_start_dt, prev_end_dt) if (compare_mode and prev_start_dt and prev_end_dt) else 0.0

    cur_signup_sum = sum_in_window(data.get("Monthly_Unique"), "Month_dt", "Unique User Signups", start_dt, end_dt)
    prev_signup_sum = sum_in_window(data.get("Monthly_Unique"), "Month_dt", "Unique User Signups", prev_start_dt, prev_end_dt) if (compare_mode and prev_start_dt and prev_end_dt) else 0.0

    # MAU "latest in window"
    def last_in_window(df: Optional[pd.DataFrame], dt_col: str, val_col: str, s_dt: pd.Timestamp, e_dt: pd.Timestamp) -> float:
        if not is_valid_df(df) or dt_col not in df.columns or val_col not in df.columns:
            return 0.0
        dfw = filter_range(df, dt_col, s_dt, e_dt)
        if not is_valid_df(dfw):
            return 0.0
        return float(to_num_series(dfw[val_col], 0).iloc[-1])

    mau_col = "Business MAU" if (segment == "Business" and is_valid_df(data.get("MAU")) and "Business MAU" in data["MAU"].columns) else "MAU"
    cur_mau_last = last_in_window(data.get("MAU"), "Month_dt", mau_col, start_dt, end_dt)
    prev_mau_last = last_in_window(data.get("MAU"), "Month_dt", mau_col, prev_start_dt, prev_end_dt) if (compare_mode and prev_start_dt and prev_end_dt) else 0.0

    # Activation "latest in window"
    act_col = "Business Activation Rate %" if (segment == "Business" and is_valid_df(data.get("Activation")) and "Business Activation Rate %" in data["Activation"].columns) else "All Activation Rate %"
    cur_act_last = last_in_window(data.get("Activation"), "Cohort_dt", act_col, start_dt, end_dt)
    prev_act_last = last_in_window(data.get("Activation"), "Cohort_dt", act_col, prev_start_dt, prev_end_dt) if (compare_mode and prev_start_dt and prev_end_dt) else 0.0

    # KPI Cards
    with kpi_cols[0]:
        st.metric("Enrollments (in range)", f"{int(round(cur_enroll_sum)):,}", delta=(percent_delta(cur_enroll_sum, prev_enroll_sum) if compare_mode and prev_enroll_sum else None))
    with kpi_cols[1]:
        st.metric("Signups (in range)", f"{int(round(cur_signup_sum)):,}", delta=(percent_delta(cur_signup_sum, prev_signup_sum) if compare_mode and prev_signup_sum else None))
    with kpi_cols[2]:
        st.metric(f"{mau_col} (latest)", f"{int(round(cur_mau_last)):,}", delta=(percent_delta(cur_mau_last, prev_mau_last) if compare_mode and prev_mau_last else None))
    with kpi_cols[3]:
        st.metric(f"{act_col} (latest)", f"{cur_act_last:.1f}%", delta=(f"{(cur_act_last - prev_act_last):+.1f} pts" if compare_mode and prev_act_last else None))

    # Sparklines row (Change #1)
    spark_cols = st.columns(4)
    df_e = data.get("Monthly_Enroll")
    df_s = data.get("Monthly_Unique")
    df_m = data.get("MAU")
    df_a = data.get("Activation")

    def spark_from(df: Optional[pd.DataFrame], dt_col: str, x_label_col: str, val_col: str, color: str):
        if not is_valid_df(df) or dt_col not in df.columns or x_label_col not in df.columns or val_col not in df.columns:
            return None
        d = filter_range(df, dt_col, start_dt, end_dt)
        if not is_valid_df(d):
            return None
        # Use label col for x (Month/Cohort) for consistent ticks, but hide axes anyway.
        return create_sparkline(d, x_label_col, val_col, color)

    with spark_cols[0]:
        fig = spark_from(df_e, "Month_dt", "Month", "Enrollments", ACCENT)
        if fig: st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    with spark_cols[1]:
        fig = spark_from(df_s, "Month_dt", "Month", "Unique User Signups", BLUE)
        if fig: st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    with spark_cols[2]:
        fig = spark_from(df_m, "Month_dt", "Month", mau_col, LILAC)
        if fig: st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    with spark_cols[3]:
        fig = spark_from(df_a, "Cohort_dt", "Cohort", act_col, SOFT_GRAY)
        if fig: st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # Key Insights row (Change #10)
    st.markdown("<div class='section-title'>Key Insights</div>", unsafe_allow_html=True)

    # Insight computations
    # Growth driver: top course by sign-ups (overall), and top country by signups (cumulative)
    top_course_df = compute_course_top(data.get("Course"), 1, CACHE_VERSION) if is_valid_df(data.get("Course")) else None
    top_geo_df = compute_geo_top(data.get("Country"), 1, CACHE_VERSION) if is_valid_df(data.get("Country")) else None

    growth_driver = "—"
    if is_valid_df(top_course_df):
        growth_driver = f"Top course: **{top_course_df.iloc[0]['Course']}** ({int(top_course_df.iloc[0]['Sign Ups']):,} sign-ups)"
    elif is_valid_df(data.get("Course")):
        growth_driver = "Top course: (course sheet present, but schema mismatch)"

    geo_driver = "—"
    if is_valid_df(top_geo_df):
        geo_driver = f"Top country: **{top_geo_df.iloc[0]['Country']}** ({int(top_geo_df.iloc[0]['Total Course Signups']):,} sign-ups)"

    # Risk: biggest stage-to-stage drop in funnel
    funnel_df, funnel_warn, funnel_drops = compute_funnel(data.get("DropOff_Split"), tuple(FUNNEL_STAGE_ORDER), CACHE_VERSION) if is_valid_df(data.get("DropOff_Split")) else (None, None, None)
    risk = "—"
    if is_valid_df(funnel_drops):
        worst = funnel_drops.sort_values("Drop (%)", ascending=False).iloc[0]
        risk = f"Biggest drop: **{worst['From → To']}** (−{int(worst['Drop (users)']):,}, {float(worst['Drop (%)']):.1f}%)"

    # Opportunity: high signups, low completion
    perf = compute_course_perf(data.get("Course"), data.get("Completion"), CACHE_VERSION) if (is_valid_df(data.get("Course")) and is_valid_df(data.get("Completion"))) else None
    opportunity = "—"
    if is_valid_df(perf) and has_cols(perf, ["Course", "Sign Ups", "Avg Completion %"]):
        perf2 = perf.copy()
        perf2["Sign Ups"] = to_num_series(perf2["Sign Ups"], 0)
        perf2["Avg Completion %"] = to_num_series(perf2["Avg Completion %"], 0.0)
        # pick from top 20% signups but bottom completion
        cutoff = perf2["Sign Ups"].quantile(0.80) if len(perf2) >= 10 else perf2["Sign Ups"].median()
        high = perf2[perf2["Sign Ups"] >= cutoff]
        if not high.empty:
            cand = high.sort_values(["Avg Completion %", "Sign Ups"], ascending=[True, False]).iloc[0]
            opportunity = f"Improve completion: **{cand['Course']}** ({int(cand['Sign Ups']):,} sign-ups, {float(cand['Avg Completion %']):.1f}% completion)"

    insight_cols = st.columns(3)
    with insight_cols[0]:
        st.markdown("**Growth driver**")
        st.write(growth_driver)
        st.write(geo_driver)
    with insight_cols[1]:
        st.markdown("**Biggest risk**")
        st.write(risk)
        if funnel_warn:
            st.caption(f"Note: {funnel_warn}")
    with insight_cols[2]:
        st.markdown("**Opportunity**")
        st.write(opportunity)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # What changed (Change #4)
    st.markdown("<div class='section-title'>What changed?</div>", unsafe_allow_html=True)
    bullets = []
    if compare_mode and prev_start_dt and prev_end_dt:
        bullets.append(f"Enrollments: **{int(round(cur_enroll_sum)):,}** ({percent_delta(cur_enroll_sum, prev_enroll_sum)} vs previous period)")
        bullets.append(f"Signups: **{int(round(cur_signup_sum)):,}** ({percent_delta(cur_signup_sum, prev_signup_sum)} vs previous period)")
        if prev_mau_last:
            bullets.append(f"{mau_col}: **{int(round(cur_mau_last)):,}** ({percent_delta(cur_mau_last, prev_mau_last)} vs previous period)")
        if prev_act_last:
            bullets.append(f"{act_col}: **{cur_act_last:.1f}%** ({(cur_act_last - prev_act_last):+.1f} pts vs previous period)")
    else:
        bullets.append("Enable **Compare mode** in the sidebar to see deltas vs the previous period.")
    st.write("\n".join([f"• {b}" for b in bullets]))


# =========================
# 12) GROWTH & RETENTION (Change #2 + #3 + #7 + #6)
# =========================
with tab_growth:
    st.markdown("<div class='section-title'>Growth & Retention</div>", unsafe_allow_html=True)
    info_expander("What this means", "Use this tab to understand volume + activation. Compare mode overlays the prior period so you can see if growth is accelerating or decelerating.")
    st.caption(f"Range: {start_p.strftime('%b %Y')} → {end_p.strftime('%b %Y')}" + (f" | Compare: {prev_start_p.strftime('%b %Y')} → {prev_end_p.strftime('%b %Y')}" if compare_mode and prev_start_p else ""))

    # Enrollment + table (Change #3)
    st.markdown("#### Enrollment trends")
    info_expander("Definition", TOOLTIPS["enrollment_trend"])
    col1, col2 = st.columns([2, 1])

    df_en = data.get("Monthly_Enroll")
    df_en_cur = filter_range(df_en, "Month_dt", start_dt, end_dt) if (is_valid_df(df_en) and "Month_dt" in df_en.columns) else None
    df_en_prev = filter_range(df_en, "Month_dt", prev_start_dt, prev_end_dt) if (compare_mode and prev_start_dt and prev_end_dt and is_valid_df(df_en) and "Month_dt" in df_en.columns) else None

    with col1:
        if is_valid_df(df_en_cur) and has_cols(df_en_cur, ["Month", "Enrollments"]):
            fig = create_line_compare_chart(df_en_cur, "Month", "Enrollments", df_en_prev, "Enrollments", ACCENT, chart_height, compare_mode)
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.warning("Enrollment Trends: data not available or required columns missing.")

    with col2:
        if is_valid_df(df_en_cur) and has_cols(df_en_cur, ["Month", "Enrollments"]):
            tbl = df_en_cur[["Month", "Enrollments"]].copy()
            tbl["Enrollments"] = to_num_series(tbl["Enrollments"], 0).astype(int)
            tbl["MoM Δ"] = tbl["Enrollments"].diff().fillna(0).astype(int)
            st.dataframe(tbl.tail(12), use_container_width=True, hide_index=True)
        else:
            st.info("No table available.")

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # Signups + table
    st.markdown("#### Signup trends")
    info_expander("Definition", TOOLTIPS["signup_trend"])
    col1, col2 = st.columns([2, 1])

    df_su = data.get("Monthly_Unique")
    df_su_cur = filter_range(df_su, "Month_dt", start_dt, end_dt) if (is_valid_df(df_su) and "Month_dt" in df_su.columns) else None
    df_su_prev = filter_range(df_su, "Month_dt", prev_start_dt, prev_end_dt) if (compare_mode and prev_start_dt and prev_end_dt and is_valid_df(df_su) and "Month_dt" in df_su.columns) else None

    with col1:
        if is_valid_df(df_su_cur) and has_cols(df_su_cur, ["Month", "Unique User Signups"]):
            fig = create_line_compare_chart(df_su_cur, "Month", "Unique User Signups", df_su_prev, "Signups", BLUE, chart_height, compare_mode)
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.warning("User Sign Up Trends: data not available or required columns missing.")

    with col2:
        if is_valid_df(df_su_cur) and has_cols(df_su_cur, ["Month", "Unique User Signups"]):
            tbl = df_su_cur[["Month", "Unique User Signups"]].copy()
            tbl["Unique User Signups"] = to_num_series(tbl["Unique User Signups"], 0).astype(int)
            tbl["MoM Δ"] = tbl["Unique User Signups"].diff().fillna(0).astype(int)
            st.dataframe(tbl.tail(12), use_container_width=True, hide_index=True)
        else:
            st.info("No table available.")

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # MAU + Activation, with segment-aware series (Change #2)
    st.markdown("#### Engagement and activation")
    colA, colB = st.columns(2)

    with colA:
        st.markdown("**Monthly Active Users (MAU)**")
        info_expander("Definition", TOOLTIPS["mau"])
        df_m = data.get("MAU")
        if is_valid_df(df_m) and "Month_dt" in df_m.columns and "Month" in df_m.columns:
            mau_col = "Business MAU" if (segment == "Business" and "Business MAU" in df_m.columns) else "MAU"
            if mau_col in df_m.columns:
                cur = filter_range(df_m, "Month_dt", start_dt, end_dt)
                prev = filter_range(df_m, "Month_dt", prev_start_dt, prev_end_dt) if (compare_mode and prev_start_dt and prev_end_dt) else None
                if is_valid_df(cur):
                    fig = create_line_compare_chart(cur, "Month", mau_col, prev, mau_col, LILAC, chart_height, compare_mode)
                    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
                else:
                    st.info("No MAU data in selected range.")
            else:
                st.warning("MAU: required column missing.")
        else:
            st.warning("MAU: data not available / columns missing.")

    with colB:
        st.markdown("**Activation Rate (D30)**")
        info_expander("Definition", TOOLTIPS["activation"])
        df_a = data.get("Activation")
        if is_valid_df(df_a) and "Cohort_dt" in df_a.columns and "Cohort" in df_a.columns:
            act_col = "Business Activation Rate %" if (segment == "Business" and "Business Activation Rate %" in df_a.columns) else "All Activation Rate %"
            if act_col in df_a.columns:
                cur = filter_range(df_a, "Cohort_dt", start_dt, end_dt)
                prev = filter_range(df_a, "Cohort_dt", prev_start_dt, prev_end_dt) if (compare_mode and prev_start_dt and prev_end_dt) else None
                if is_valid_df(cur):
                    fig = create_line_compare_chart(cur, "Cohort", act_col, prev, act_col, SOFT_GRAY, chart_height, compare_mode)
                    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
                else:
                    st.info("No activation data in selected range.")
            else:
                st.warning("Activation: required column missing.")
        else:
            st.warning("Activation: data not available / columns missing.")


# =========================
# 13) GEOGRAPHY (Change #3 + #8)
# =========================
with tab_geo:
    st.markdown("<div class='section-title'>Geography</div>", unsafe_allow_html=True)
    info_expander("Definition", TOOLTIPS["geo"])

    df_geo = data.get("Country")
    top_geo = compute_geo_top(df_geo, int(top_countries), CACHE_VERSION) if is_valid_df(df_geo) else None

    colM, colN = st.columns([2, 1])
    with colM:
        if is_valid_df(df_geo) and has_cols(df_geo, ["Country", "Total Course Signups"]):
            geo_map = df_geo[["Country", "Total Course Signups"]].copy()
            geo_map["Total Course Signups"] = to_num_series(geo_map["Total Course Signups"], 0)
            fig = px.choropleth(
                geo_map,
                locations="Country",
                locationmode="country names",
                color="Total Course Signups",
                color_continuous_scale=["#1e1e1e", ACCENT],
            )
            fig.update_layout(**DARK_LAYOUT, geo=dict(bgcolor="rgba(0,0,0,0)"), height=max(420, chart_height + 80))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Geography map: data not available / columns missing.")

    with colN:
        st.markdown(f"#### Top {int(top_countries)} Countries")
        if is_valid_df(top_geo):
            st.dataframe(top_geo, use_container_width=True, hide_index=True)
        else:
            st.info("Top countries not available.")


# =========================
# 14) COURSE PERFORMANCE (Change #3 + #5 + #8 + #9)
# =========================
with tab_courses:
    st.markdown("<div class='section-title'>Course Performance</div>", unsafe_allow_html=True)
    info_expander("Definition", "This tab is built for action: find high-impact courses, see completion, and diagnose drop-offs.")
    info_expander("Popular courses", TOOLTIPS["popular"])
    info_expander("Completion rates", TOOLTIPS["completion"])

    df_course = data.get("Course")
    df_comp = data.get("Completion")
    perf = compute_course_perf(df_course, df_comp, CACHE_VERSION) if (is_valid_df(df_course) and is_valid_df(df_comp)) else None

    # Popular + Completion: 1 chart + 1 table each (Change #3)
    colA, colB = st.columns(2)

    with colA:
        st.markdown("#### Popular courses")
        top_courses_df = compute_course_top(df_course, int(top_courses), CACHE_VERSION) if is_valid_df(df_course) else None
        if is_valid_df(top_courses_df):
            fig = create_bar_chart(top_courses_df, "Sign Ups", "ShortName", ACCENT, text_col="Sign Ups", height=max(360, chart_height + 40))
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
            with st.expander("Details (table)", expanded=False):
                st.dataframe(top_courses_df, use_container_width=True, hide_index=True)
        else:
            st.warning("Popular courses: data not available / columns missing.")

    with colB:
        st.markdown("#### Completion rates (top by volume)")
        if is_valid_df(perf) and has_cols(perf, ["ShortName", "Sign Ups", "Avg Completion %"]):
            top_perf = perf.nlargest(int(top_courses), "Sign Ups")
            fig = create_bar_chart(top_perf, "Avg Completion %", "ShortName", BLUE, text_col="Avg Completion %", height=max(360, chart_height + 40), x_title="Avg Completion %")
            fig.update_traces(texttemplate="%{text:.1f}%")
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
            with st.expander("Details (table)", expanded=False):
                st.dataframe(top_perf.sort_values("Avg Completion %"), use_container_width=True, hide_index=True)
        else:
            st.warning("Completion rates: data not available / columns missing.")

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # Funnel + diagnostic table (Change #5)
    st.markdown("#### Drop-off funnel (diagnostic)")
    info_expander("Definition", TOOLTIPS["funnel"])
    colF, colT = st.columns([2, 1])

    funnel_df, funnel_warn, funnel_drops = compute_funnel(data.get("DropOff_Split"), tuple(FUNNEL_STAGE_ORDER), CACHE_VERSION) if is_valid_df(data.get("DropOff_Split")) else (None, None, None)
    with colF:
        if funnel_warn:
            st.warning(funnel_warn)
        if is_valid_df(funnel_df):
            fig = go.Figure(
                go.Bar(
                    x=funnel_df["All Count"],
                    y=funnel_df["Stage"],
                    orientation="h",
                    text=funnel_df["text_label"],
                    textposition="auto",
                    marker={"color": [DARK, MID_GRAY_1, MID_GRAY_2, ACCENT]},
                )
            )
            fig.update_layout(**DARK_LAYOUT, height=max(360, chart_height + 40), yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.warning("Funnel: data not available / columns missing.")

    with colT:
        st.markdown("**Stage-to-stage drop**")
        if is_valid_df(funnel_drops):
            st.dataframe(funnel_drops.sort_values("Drop (%)", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("No stage drop table available.")

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # Progressive disclosure for heavy tables (Change #8) + pagination (Change #6)
    st.markdown("#### All course performance")
    if is_valid_df(perf):
        df_table = perf.copy()
        if st.session_state["course_search"].strip():
            q = st.session_state["course_search"].strip().lower()
            df_table = df_table[df_table["Course"].astype(str).str.lower().str.contains(q, na=False)]

        if "Sign Ups" in df_table.columns:
            df_table = df_table.sort_values("Sign Ups", ascending=False)

        # show top 20 by default
        st.markdown("**Top 20 (quick view)**")
        st.dataframe(df_table.head(20), use_container_width=True, hide_index=True)

        with st.expander("View full table (paginated)", expanded=False):
            page_size = st.number_input("Rows per page", min_value=25, max_value=200, value=DEFAULT_PAGE_SIZE, step=25)
            total_rows = len(df_table)
            total_pages = max(1, (total_rows + int(page_size) - 1) // int(page_size))
            page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
            start = (int(page) - 1) * int(page_size)
            end = start + int(page_size)
            st.caption(f"Showing rows {start+1}-{min(end, total_rows)} of {total_rows}")
            st.dataframe(df_table.iloc[start:end], use_container_width=True, hide_index=True, height=560)
    else:
        st.info("Course performance table not available.")

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # Keep detailed course drop-off sheet behind expander (Change #8)
    st.markdown("#### Course drop-off sheet (raw)")
    df_cd = data.get("Course_DropOff")
    with st.expander("Show raw course drop-off data", expanded=False):
        if is_valid_df(df_cd):
            st.dataframe(df_cd, use_container_width=True)
        else:
            st.info("Course drop-off sheet not available.")


# =========================
# 15) USER INSIGHTS (Change #2 + #3 + #4)
# =========================
with tab_users:
    st.markdown("<div class='section-title'>User Insights</div>", unsafe_allow_html=True)
    info_expander("What this means", "Use this tab to understand composition (segmentation) and depth of engagement.")

    colU, colV = st.columns(2)

    with colU:
        st.markdown("#### User segmentation")
        info_expander("Definition", TOOLTIPS["segmentation"])
        df_seg = data.get("User_Segmentation")
        if is_valid_df(df_seg):
            biz = get_metric_value(df_seg, "Business Users")
            gen = get_metric_value(df_seg, "Generic Users")
            inv = get_metric_value(df_seg, "Invalid Users")

            if biz + gen + inv > 0:
                fig = go.Figure(
                    data=[
                        go.Pie(
                            labels=["Business", "Generic", "Invalid"],
                            values=[biz, gen, inv],
                            hole=0.5,
                            marker=dict(colors=[ACCENT, SOFT_GRAY, DARK]),
                        )
                    ]
                )
                fig.update_layout(**DARK_LAYOUT, height=max(320, chart_height))
                st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

                # Insight card (Change #4)
                total = biz + gen + inv
                st.caption(f"Business share: {biz/total*100:.1f}% • Generic: {gen/total*100:.1f}% • Invalid: {inv/total*100:.1f}%")
            else:
                st.info("Segmentation counts not available.")
        else:
            st.warning("User Segmentation: data not available / columns missing.")

    with colV:
        st.markdown("#### Engagement depth")
        info_expander("Definition", TOOLTIPS["engagement"])
        df_eng = data.get("User_Engagement")
        if is_valid_df(df_eng) and has_cols(df_eng, ["Metric", "Count"]):
            mask = df_eng["Metric"].astype(str).str.contains("Users with", na=False)
            df_plot = df_eng.loc[mask, ["Metric", "Count"]].copy()
            if is_valid_df(df_plot):
                df_plot["Count"] = to_num_series(df_plot["Count"], 0)
                fig = px.bar(df_plot, x="Metric", y="Count", color="Metric")
                fig.update_layout(**DARK_LAYOUT, showlegend=False, height=max(320, chart_height))
                st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

                # Quick narrative (Change #4)
                top_row = df_plot.sort_values("Count", ascending=False).iloc[0]
                st.caption(f"Highest concentration: {top_row['Metric']} ({int(top_row['Count']):,} users).")
            else:
                st.info("No engagement-depth rows found.")
        else:
            st.warning("User Engagement: data not available / columns missing.")

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    st.markdown("#### Badges")
    df_b = data.get("Badges_Issued")
    st.caption("This section is informational. If you want this to be actionable, we can add 'issuance velocity' and a claim-rate proxy (if you have those events).")
    if is_valid_df(df_b):
        st.dataframe(df_b, use_container_width=True, hide_index=True)
    else:
        st.info("Badges sheet not available.")
