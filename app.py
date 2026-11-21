
from pathlib import Path
import subprocess
import sys
import uuid

import streamlit as st
import pandas as pd
import plotly.express as px


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Smart Traffic AI Dashboard",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

PROJECT_DIR = Path(__file__).resolve().parent

CSV_PATH = (
    PROJECT_DIR / "outputs" / "reports" / "traffic_report.csv"
)

BACKEND_PATH = (
    PROJECT_DIR / "src" / "counting.py"
)

UPLOAD_DIR = (
    PROJECT_DIR / "dataset" / "traffic_videos" / "uploads"
)

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CSV_PATH.parent.mkdir(parents=True, exist_ok=True)


# ==================================================
# 2. SESSION STATE
# ==================================================

defaults = {
    "analysis_started": False,
    "analysis_success": False,
    "analysis_output": "",
    "selected_page": "Overview",
    "dashboard_notice": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==================================================
# 3. ADVANCED DARK BLUE THEME
# ==================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #080f1e;
    color: #e2e8f0;
}

.block-container {
    max-width: 1550px;
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}

header[data-testid="stHeader"] {
    background: transparent;
}

section[data-testid="stSidebar"] {
    background: #0d1729;
    border-right: 1px solid #263c59;
}

section[data-testid="stSidebar"] * {
    color: #e2e8f0;
}

.main-title {
    font-size: 30px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.7px;
}

.sub-title {
    color: #94a3b8;
    font-size: 14px;
    margin-top: 6px;
    margin-bottom: 22px;
}

.section-title {
    color: #f8fafc;
    font-size: 20px;
    font-weight: 700;
    margin-top: 24px;
    margin-bottom: 16px;
}

.top-banner {
    background: linear-gradient(110deg, #10233f, #12345b);
    border: 1px solid #28517c;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 20px;
}

.top-banner-title {
    font-size: 22px;
    font-weight: 800;
    color: #ffffff;
}

.top-banner-text {
    font-size: 13px;
    color: #bfdbfe;
    margin-top: 7px;
}

.kpi-card {
    background: linear-gradient(145deg, #172b47, #101d31);
    border: 1px solid #294664;
    border-radius: 15px;
    padding: 18px;
    min-height: 130px;
}

.kpi-icon {
    font-size: 24px;
}

.kpi-label {
    color: #a5b8d0;
    font-size: 13px;
    margin-top: 10px;
}

.kpi-value {
    color: #ffffff;
    font-size: 29px;
    font-weight: 800;
    margin-top: 6px;
    overflow-wrap: anywhere;
}

.panel {
    background: #101d31;
    border: 1px solid #29415f;
    border-radius: 15px;
    padding: 20px;
}

.upload-panel {
    background: linear-gradient(145deg, #122944, #101d31);
    border: 1px solid #3474b9;
    border-radius: 16px;
    padding: 22px;
}

.status-panel {
    background: #142943;
    border: 1px solid #294664;
    border-radius: 13px;
    padding: 20px;
    text-align: center;
}

.stButton > button {
    background: linear-gradient(90deg, #2563eb, #0891b2);
    color: white;
    border: none;
    border-radius: 9px;
    min-height: 43px;
    font-weight: 700;
    width: 100%;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #1d4ed8, #0e7490);
    color: white;
    border: none;
}

.stDownloadButton > button {
    background: #16395c;
    color: white;
    border: 1px solid #3474b9;
    border-radius: 9px;
    width: 100%;
}

[data-testid="stFileUploader"] {
    background: #101d31;
    border: 1px dashed #3b82f6;
    border-radius: 12px;
    padding: 12px;
}

div[data-testid="stMetric"] {
    background: #14243c;
    border: 1px solid #294664;
    border-radius: 12px;
    padding: 15px;
}

div[data-testid="stMetricLabel"] {
    color: #a5b8d0;
}

div[data-testid="stMetricValue"] {
    color: #ffffff;
}

hr {
    border-color: #263c59;
}

.footer {
    text-align: center;
    color: #64748b;
    font-size: 12px;
    padding: 35px 0 10px;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# 4. HELPER FUNCTIONS
# ==================================================

def load_report():

    if not CSV_PATH.exists():
        return pd.DataFrame(), {}

    try:
        df = pd.read_csv(CSV_PATH)

        if not {"Metric", "Value"}.issubset(df.columns):
            return df, {}

        metrics = {}

        for _, row in df.iterrows():
            metrics[str(row["Metric"]).strip()] = row["Value"]

        return df, metrics

    except Exception:
        return pd.DataFrame(), {}


def get_number(metrics, name):

    try:
        return int(float(metrics.get(name, 0)))
    except (ValueError, TypeError):
        return 0


def get_decimal(metrics, name):

    try:
        return float(metrics.get(name, 0))
    except (ValueError, TypeError):
        return 0.0


def show_kpi(label, value, icon):

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def chart_layout(fig):

    fig.update_layout(
        paper_bgcolor="#101d31",
        plot_bgcolor="#101d31",
        font_color="#e2e8f0",
        margin=dict(l=15, r=15, t=35, b=15),
        legend=dict(
            font=dict(color="#cbd5e1")
        )
    )

    fig.update_xaxes(
        gridcolor="#263c59",
        zerolinecolor="#263c59"
    )

    fig.update_yaxes(
        gridcolor="#263c59",
        zerolinecolor="#263c59"
    )

    return fig


# ==================================================
# 5. BACKEND EXECUTION
# ==================================================

def run_traffic_analysis(video_path):

    if not BACKEND_PATH.exists():
        raise FileNotFoundError(
            f"Backend file not found: {BACKEND_PATH}"
        )

    command = [
        sys.executable,
        str(BACKEND_PATH),
        "--video",
        str(video_path.resolve()),
        "--no-display"
    ]

    result = subprocess.run(
        command,
        cwd=str(PROJECT_DIR),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    return result


# ==================================================
# 6. SIDEBAR NAVIGATION
# ==================================================

with st.sidebar:

    st.markdown("""
    <div style="text-align:center;padding:20px 0;">
        <div style="font-size:45px;">🚦</div>
        <div style="font-size:21px;font-weight:800;color:#60a5fa;">
            SMART TRAFFIC
        </div>
        <div style="font-size:11px;color:#94a3b8;">
            AI MONITORING SYSTEM
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### Navigation")
    key="main_navigation"
    page = st.radio(
    "Navigation",
    ["Overview", "Vehicle Analytics", "Traffic Analytics", "CSV Reports"],
    key="main_navigation"
    )

    # page = st.radio(
    #     "Dashboard Pages",
    #     [
    #         "Overview",
    #         "Vehicle Analytics",
    #         "Traffic Analytics",
    #         "CSV Reports"
    #     ],
    #     label_visibility="collapsed"
    # )

    st.divider()

    st.markdown("### System Information")

    st.caption("Detection: YOLO11")
    st.caption("Tracking: ByteTrack")
    st.caption("Processing: OpenCV")
    st.caption("Dashboard: Streamlit")

    st.divider()

    if st.button("↻ Refresh Dashboard"):
        st.rerun()

    st.caption("AI Traffic Management System")


# ==================================================
# 7. MAIN HEADER
# ==================================================

st.markdown("""
<div class="main-title">
    AI-Powered Smart Traffic Management
</div>

<div class="sub-title">
    Intelligent Vehicle Detection | Tracking | Counting | Analytics
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="top-banner">
    <div class="top-banner-title">
        Welcome to Smart Traffic Analytics
    </div>
    <div class="top-banner-text">
        Monitor vehicles, process traffic videos and analyze
        traffic conditions through Artificial Intelligence.
    </div>
</div>
""", unsafe_allow_html=True)


# ==================================================
# 8. VIDEO UPLOAD AND PROCESSING
# ==================================================

st.markdown(
    '<div class="section-title">🎥 Upload and Analyze Traffic Video</div>',
    unsafe_allow_html=True
)

with st.container(border=True):

    upload_col, info_col = st.columns([1.5, 1])

    with upload_col:

        uploaded_video = st.file_uploader(
            "Choose a traffic video from your computer",
            type=["mp4", "avi", "mov", "mkv"],
            help="Select a road or highway traffic video."
        )

        if uploaded_video is not None:

            st.success(
                f"Selected video: {uploaded_video.name}"
            )

            st.caption(
                f"File size: {uploaded_video.size / (1024 * 1024):.2f} MB"
            )

            if st.button(
                "▶ RUN TRAFFIC ANALYSIS",
                type="primary"
            ):

                unique_name = (
                    f"{uuid.uuid4().hex[:10]}_"
                    f"{Path(uploaded_video.name).name}"
                )

                saved_video_path = UPLOAD_DIR / unique_name

                try:

                    saved_video_path.write_bytes(
                        uploaded_video.getvalue()
                    )

                    st.session_state.analysis_started = True
                    st.session_state.analysis_success = False
                    st.session_state.analysis_output = ""

                    with st.spinner(
                        "AI is analyzing your video. "
                        "Please wait..."
                    ):

                        result = run_traffic_analysis(
                            saved_video_path
                        )

                    st.session_state.analysis_output = (
                        "----- STANDARD OUTPUT -----\n"
                        + (result.stdout or "")
                        + "\n----- ERROR OUTPUT -----\n"
                        + (result.stderr or "")
                    )

                    if result.returncode == 0:

                        st.session_state.analysis_success = True

                        st.session_state.dashboard_notice = (
                            "New traffic analysis completed successfully."
                        )

                    else:

                        st.session_state.analysis_success = False

                except Exception as error:

                    st.session_state.analysis_success = False
                    st.session_state.analysis_output = str(error)

                st.rerun()

    with info_col:

        st.markdown("""
        <div style="padding:15px;">
            <h3 style="color:#60a5fa;">AI Video Processing</h3>
            <p style="color:#cbd5e1;font-size:14px;">
                Upload your video and let the AI system
                automatically detect, track and count vehicles.
            </p>
            <p style="color:#94a3b8;font-size:13px;">
                Supported formats: MP4, AVI, MOV, MKV
            </p>
            <p style="color:#94a3b8;font-size:13px;">
                Detection model: YOLO11
            </p>
            <p style="color:#94a3b8;font-size:13px;">
                Object tracking: ByteTrack
            </p>
        </div>
        """, unsafe_allow_html=True)


# ==================================================
# 9. PROCESSING MESSAGES
# ==================================================

if st.session_state.analysis_success:

    st.success(
        "Traffic analysis completed successfully!"
    )

    if st.session_state.analysis_output:

        with st.expander("View Backend Processing Log"):

            st.code(
                st.session_state.analysis_output,
                language="text"
            )

elif st.session_state.analysis_started:

    if st.session_state.analysis_output:

        st.error(
            "Traffic processing failed. Check the error details."
        )

        with st.expander(
            "View Backend Error Details",
            expanded=True
        ):

            st.code(
                st.session_state.analysis_output,
                language="text"
            )


if st.session_state.dashboard_notice:

    st.info(st.session_state.dashboard_notice)


st.divider()


# ==================================================
# 10. LOAD REPORT
# ==================================================

df, metrics = load_report()

if df.empty or not metrics:

    st.markdown(
        '<div class="section-title">Traffic Dashboard</div>',
        unsafe_allow_html=True
    )

    st.info(
        "No traffic report is available yet. "
        "Upload a video above and run traffic analysis."
    )

    st.stop()


# ==================================================
# 11. EXTRACT ANALYTICS
# ==================================================

total = get_number(metrics, "Total Vehicles")

cars = get_number(metrics, "Car")
motorcycles = get_number(metrics, "Motorcycle")
buses = get_number(metrics, "Bus")
trucks = get_number(metrics, "Truck")

flow = get_decimal(metrics, "Traffic Flow")

density = get_decimal(
    metrics,
    "Average Visible Vehicles"
)

traffic_status = str(
    metrics.get("Traffic Status", "Not Available")
)

report_date = str(
    metrics.get("Date", "Not Available")
)


# ==================================================
# 12. DASHBOARD HEADER
# ==================================================

st.markdown(
    '<div class="section-title">📊 Traffic Dashboard</div>',
    unsafe_allow_html=True
)

st.caption(f"Last report generated: {report_date}")


# ==================================================
# 13. CLEAR DASHBOARD DISPLAY
# ==================================================

clear_col, report_col = st.columns([1, 4])

with clear_col:

    if st.button("Clear Dashboard View"):

        st.session_state.analysis_started = False
        st.session_state.analysis_success = False
        st.session_state.analysis_output = ""
        st.session_state.dashboard_notice = ""

        st.rerun()

with report_col:

    st.caption(
        "Clearing the dashboard view does not delete your CSV report."
    )


# ==================================================
# 14. OVERVIEW PAGE
# ==================================================

if page == "Overview":

    st.markdown(
        '<div class="section-title">Vehicle Overview</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        show_kpi("Total Vehicles", total, "🚘")

    with c2:
        show_kpi("Cars", cars, "🚗")

    with c3:
        show_kpi("Motorcycles", motorcycles, "🏍️")

    with c4:
        show_kpi("Buses", buses, "🚌")

    with c5:
        show_kpi("Trucks", trucks, "🚚")

    st.markdown(
        '<div class="section-title">Traffic Insights</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns([1.5, 1])

    with left:

        st.markdown(
            '<div class="panel">',
            unsafe_allow_html=True
        )

        st.markdown("### Vehicle Distribution")

        chart_data = pd.DataFrame({
            "Vehicle": [
                "Cars",
                "Motorcycles",
                "Buses",
                "Trucks"
            ],
            "Count": [
                cars,
                motorcycles,
                buses,
                trucks
            ]
        })

        chart_data = chart_data[
            chart_data["Count"] > 0
        ]

        if not chart_data.empty:

            fig = px.pie(
                chart_data,
                names="Vehicle",
                values="Count",
                hole=0.65,
                color_discrete_sequence=[
                    "#3b82f6",
                    "#06b6d4",
                    "#8b5cf6",
                    "#f59e0b"
                ]
            )

            fig.update_layout(
                paper_bgcolor="#101d31",
                font_color="#e2e8f0",
                margin=dict(t=15, b=15, l=10, r=10),
                annotations=[
                    dict(
                        text=f"<b>{total}</b><br>Vehicles",
                        x=0.5,
                        y=0.5,
                        showarrow=False,
                        font_size=20,
                        font_color="white"
                    )
                ]
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No vehicle counts available.")

        st.markdown("</div>", unsafe_allow_html=True)

    with right:

        st.markdown(
            '<div class="panel">',
            unsafe_allow_html=True
        )

        st.markdown("### Traffic Condition")

        colors = {
            "Low Traffic": "#34d399",
            "Moderate Traffic": "#fbbf24",
            "Heavy Traffic": "#f87171"
        }

        status_color = colors.get(
            traffic_status,
            "#94a3b8"
        )

        st.markdown(f"""
        <div class="status-panel">
            <div style="font-size:12px;color:#94a3b8;">
                CURRENT TRAFFIC STATUS
            </div>
            <div style="
                font-size:25px;
                font-weight:800;
                color:{status_color};
                margin-top:12px;
            ">
                {traffic_status}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Traffic Metrics")

        st.metric(
            "Traffic Flow",
            f"{flow:.2f} vehicles/min"
        )

        st.metric(
            "Average Visible Vehicles",
            f"{density:.2f}"
        )

        st.markdown("</div>", unsafe_allow_html=True)


# ==================================================
# 15. VEHICLE ANALYTICS PAGE
# ==================================================

elif page == "Vehicle Analytics":

    st.markdown(
        '<div class="section-title">Vehicle Analytics</div>',
        unsafe_allow_html=True
    )

    chart_data = pd.DataFrame({
        "Vehicle Type": [
            "Car",
            "Motorcycle",
            "Bus",
            "Truck"
        ],
        "Count": [
            cars,
            motorcycles,
            buses,
            trucks
        ]
    })

    left, right = st.columns(2)

    with left:

        st.markdown(
            '<div class="panel">',
            unsafe_allow_html=True
        )

        st.markdown("### Vehicle Category Comparison")

        fig = px.bar(
            chart_data,
            x="Vehicle Type",
            y="Count",
            color="Vehicle Type",
            text="Count",
            color_discrete_sequence=[
                "#3b82f6",
                "#06b6d4",
                "#8b5cf6",
                "#f59e0b"
            ]
        )

        fig.update_traces(
            textposition="outside"
        )

        fig = chart_layout(fig)

        fig.update_layout(
            showlegend=False,
            xaxis_title="",
            yaxis_title="Vehicle Count"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with right:

        st.markdown(
            '<div class="panel">',
            unsafe_allow_html=True
        )

        st.markdown("### Vehicle Statistics")

        st.dataframe(
            chart_data,
            use_container_width=True,
            hide_index=True
        )

        st.metric(
            "Total Counted Vehicles",
            f"{total:,}"
        )

        st.markdown("</div>", unsafe_allow_html=True)


# ==================================================
# 16. TRAFFIC ANALYTICS PAGE
# ==================================================

elif page == "Traffic Analytics":

    st.markdown(
        '<div class="section-title">Traffic Monitoring Analytics</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        show_kpi("Traffic Flow", f"{flow:.2f}", "📈")

    with c2:
        show_kpi("Average Visible Vehicles", f"{density:.2f}", "🚘")

    with c3:
        show_kpi("Traffic Status", traffic_status, "🚦")

    st.markdown(
        '<div class="section-title">Traffic Analysis Summary</div>',
        unsafe_allow_html=True
    )

    traffic_df = pd.DataFrame({
        "Metric": [
            "Total Vehicles",
            "Cars",
            "Motorcycles",
            "Buses",
            "Trucks",
            "Traffic Flow",
            "Average Visible Vehicles",
            "Traffic Status"
        ],
        "Value": [
            total,
            cars,
            motorcycles,
            buses,
            trucks,
            flow,
            density,
            traffic_status
        ]
    })

    st.dataframe(
        traffic_df,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Average visible vehicles is an occupancy proxy, "
        "not a calibrated physical traffic density measurement."
    )


# ==================================================
# 17. CSV REPORTS PAGE
# ==================================================

elif page == "CSV Reports":

    st.markdown(
        '<div class="section-title">Traffic Reports</div>',
        unsafe_allow_html=True
    )

    st.success("Traffic report loaded successfully.")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        label="⬇ Download Traffic Report",
        data=CSV_PATH.read_bytes(),
        file_name="traffic_report.csv",
        mime="text/csv"
    )


# ==================================================
# 18. FOOTER
# ==================================================

st.divider()

st.markdown("""
<div class="footer">
    AI-POWERED SMART TRAFFIC MANAGEMENT SYSTEM
    <br><br>
    Python · YOLO11 · OpenCV · ByteTrack · Streamlit
    <br><br>
    Developed by Muhammad Fahad
</div>
""", unsafe_allow_html=True)

from pathlib import Path
import subprocess
import sys
import uuid

import streamlit as st
import pandas as pd
import plotly.express as px


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Smart Traffic AI Dashboard",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

PROJECT_DIR = Path(__file__).resolve().parent

CSV_PATH = (
    PROJECT_DIR / "outputs" / "reports" / "traffic_report.csv"
)

BACKEND_PATH = (
    PROJECT_DIR / "src" / "counting.py"
)

UPLOAD_DIR = (
    PROJECT_DIR / "dataset" / "traffic_videos" / "uploads"
)

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CSV_PATH.parent.mkdir(parents=True, exist_ok=True)


# ==================================================
# 2. SESSION STATE
# ==================================================

defaults = {
    "analysis_started": False,
    "analysis_success": False,
    "analysis_output": "",
    "selected_page": "Overview",
    "dashboard_notice": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==================================================
# 3. ADVANCED DARK BLUE THEME
# ==================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #080f1e;
    color: #e2e8f0;
}

.block-container {
    max-width: 1550px;
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}

header[data-testid="stHeader"] {
    background: transparent;
}

section[data-testid="stSidebar"] {
    background: #0d1729;
    border-right: 1px solid #263c59;
}

section[data-testid="stSidebar"] * {
    color: #e2e8f0;
}

.main-title {
    font-size: 30px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.7px;
}

.sub-title {
    color: #94a3b8;
    font-size: 14px;
    margin-top: 6px;
    margin-bottom: 22px;
}

.section-title {
    color: #f8fafc;
    font-size: 20px;
    font-weight: 700;
    margin-top: 24px;
    margin-bottom: 16px;
}

.top-banner {
    background: linear-gradient(110deg, #10233f, #12345b);
    border: 1px solid #28517c;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 20px;
}

.top-banner-title {
    font-size: 22px;
    font-weight: 800;
    color: #ffffff;
}

.top-banner-text {
    font-size: 13px;
    color: #bfdbfe;
    margin-top: 7px;
}

.kpi-card {
    background: linear-gradient(145deg, #172b47, #101d31);
    border: 1px solid #294664;
    border-radius: 15px;
    padding: 18px;
    min-height: 130px;
}

.kpi-icon {
    font-size: 24px;
}

.kpi-label {
    color: #a5b8d0;
    font-size: 13px;
    margin-top: 10px;
}

.kpi-value {
    color: #ffffff;
    font-size: 29px;
    font-weight: 800;
    margin-top: 6px;
    overflow-wrap: anywhere;
}

.panel {
    background: #101d31;
    border: 1px solid #29415f;
    border-radius: 15px;
    padding: 20px;
}

.upload-panel {
    background: linear-gradient(145deg, #122944, #101d31);
    border: 1px solid #3474b9;
    border-radius: 16px;
    padding: 22px;
}

.status-panel {
    background: #142943;
    border: 1px solid #294664;
    border-radius: 13px;
    padding: 20px;
    text-align: center;
}

.stButton > button {
    background: linear-gradient(90deg, #2563eb, #0891b2);
    color: white;
    border: none;
    border-radius: 9px;
    min-height: 43px;
    font-weight: 700;
    width: 100%;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #1d4ed8, #0e7490);
    color: white;
    border: none;
}

.stDownloadButton > button {
    background: #16395c;
    color: white;
    border: 1px solid #3474b9;
    border-radius: 9px;
    width: 100%;
}

[data-testid="stFileUploader"] {
    background: #101d31;
    border: 1px dashed #3b82f6;
    border-radius: 12px;
    padding: 12px;
}

div[data-testid="stMetric"] {
    background: #14243c;
    border: 1px solid #294664;
    border-radius: 12px;
    padding: 15px;
}

div[data-testid="stMetricLabel"] {
    color: #a5b8d0;
}

div[data-testid="stMetricValue"] {
    color: #ffffff;
}

hr {
    border-color: #263c59;
}

.footer {
    text-align: center;
    color: #64748b;
    font-size: 12px;
    padding: 35px 0 10px;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# 4. HELPER FUNCTIONS
# ==================================================

def load_report():

    if not CSV_PATH.exists():
        return pd.DataFrame(), {}

    try:
        df = pd.read_csv(CSV_PATH)

        if not {"Metric", "Value"}.issubset(df.columns):
            return df, {}

        metrics = {}

        for _, row in df.iterrows():
            metrics[str(row["Metric"]).strip()] = row["Value"]

        return df, metrics

    except Exception:
        return pd.DataFrame(), {}


def get_number(metrics, name):

    try:
        return int(float(metrics.get(name, 0)))
    except (ValueError, TypeError):
        return 0


def get_decimal(metrics, name):

    try:
        return float(metrics.get(name, 0))
    except (ValueError, TypeError):
        return 0.0


def show_kpi(label, value, icon):

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def chart_layout(fig):

    fig.update_layout(
        paper_bgcolor="#101d31",
        plot_bgcolor="#101d31",
        font_color="#e2e8f0",
        margin=dict(l=15, r=15, t=35, b=15),
        legend=dict(
            font=dict(color="#cbd5e1")
        )
    )

    fig.update_xaxes(
        gridcolor="#263c59",
        zerolinecolor="#263c59"
    )

    fig.update_yaxes(
        gridcolor="#263c59",
        zerolinecolor="#263c59"
    )

    return fig


# ==================================================
# 5. BACKEND EXECUTION
# ==================================================

def run_traffic_analysis(video_path):

    if not BACKEND_PATH.exists():
        raise FileNotFoundError(
            f"Backend file not found: {BACKEND_PATH}"
        )

    command = [
        sys.executable,
        str(BACKEND_PATH),
        "--video",
        str(video_path.resolve()),
        "--no-display"
    ]

    result = subprocess.run(
        command,
        cwd=str(PROJECT_DIR),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    return result


# ==================================================
# 6. SIDEBAR NAVIGATION
# ==================================================

with st.sidebar:

    st.markdown("""
    <div style="text-align:center;padding:20px 0;">
        <div style="font-size:45px;">🚦</div>
        <div style="font-size:21px;font-weight:800;color:#60a5fa;">
            SMART TRAFFIC
        </div>
        <div style="font-size:11px;color:#94a3b8;">
            AI MONITORING SYSTEM
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### Navigation")

    page = st.radio(
        "Dashboard Pages",
        [
            "Overview",
            "Vehicle Analytics",
            "Traffic Analytics",
            "CSV Reports"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### System Information")

    st.caption("Detection: YOLO11")
    st.caption("Tracking: ByteTrack")
    st.caption("Processing: OpenCV")
    st.caption("Dashboard: Streamlit")

    st.divider()

    if st.button("↻ Refresh Dashboard"):
        st.rerun()

    st.caption("AI Traffic Management System")


# ==================================================
# 7. MAIN HEADER
# ==================================================

st.markdown("""
<div class="main-title">
    AI-Powered Smart Traffic Management
</div>

<div class="sub-title">
    Intelligent Vehicle Detection | Tracking | Counting | Analytics
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="top-banner">
    <div class="top-banner-title">
        Welcome to Smart Traffic Analytics
    </div>
    <div class="top-banner-text">
        Monitor vehicles, process traffic videos and analyze
        traffic conditions through Artificial Intelligence.
    </div>
</div>
""", unsafe_allow_html=True)


# ==================================================
# 8. VIDEO UPLOAD AND PROCESSING
# ==================================================

st.markdown(
    '<div class="section-title">🎥 Upload and Analyze Traffic Video</div>',
    unsafe_allow_html=True
)

with st.container(border=True):

    upload_col, info_col = st.columns([1.5, 1])

    with upload_col:

        uploaded_video = st.file_uploader(
            "Choose a traffic video from your computer",
            type=["mp4", "avi", "mov", "mkv"],
            help="Select a road or highway traffic video."
        )

        if uploaded_video is not None:

            st.success(
                f"Selected video: {uploaded_video.name}"
            )

            st.caption(
                f"File size: {uploaded_video.size / (1024 * 1024):.2f} MB"
            )

            if st.button(
                "▶ RUN TRAFFIC ANALYSIS",
                type="primary"
            ):

                unique_name = (
                    f"{uuid.uuid4().hex[:10]}_"
                    f"{Path(uploaded_video.name).name}"
                )

                saved_video_path = UPLOAD_DIR / unique_name

                try:

                    saved_video_path.write_bytes(
                        uploaded_video.getvalue()
                    )

                    st.session_state.analysis_started = True
                    st.session_state.analysis_success = False
                    st.session_state.analysis_output = ""

                    with st.spinner(
                        "AI is analyzing your video. "
                        "Please wait..."
                    ):

                        result = run_traffic_analysis(
                            saved_video_path
                        )

                    st.session_state.analysis_output = (
                        "----- STANDARD OUTPUT -----\n"
                        + (result.stdout or "")
                        + "\n----- ERROR OUTPUT -----\n"
                        + (result.stderr or "")
                    )

                    if result.returncode == 0:

                        st.session_state.analysis_success = True

                        st.session_state.dashboard_notice = (
                            "New traffic analysis completed successfully."
                        )

                    else:

                        st.session_state.analysis_success = False

                except Exception as error:

                    st.session_state.analysis_success = False
                    st.session_state.analysis_output = str(error)

                st.rerun()

    with info_col:

        st.markdown("""
        <div style="padding:15px;">
            <h3 style="color:#60a5fa;">AI Video Processing</h3>
            <p style="color:#cbd5e1;font-size:14px;">
                Upload your video and let the AI system
                automatically detect, track and count vehicles.
            </p>
            <p style="color:#94a3b8;font-size:13px;">
                Supported formats: MP4, AVI, MOV, MKV
            </p>
            <p style="color:#94a3b8;font-size:13px;">
                Detection model: YOLO11
            </p>
            <p style="color:#94a3b8;font-size:13px;">
                Object tracking: ByteTrack
            </p>
        </div>
        """, unsafe_allow_html=True)


# ==================================================
# 9. PROCESSING MESSAGES
# ==================================================

if st.session_state.analysis_success:

    st.success(
        "Traffic analysis completed successfully!"
    )

    if st.session_state.analysis_output:

        with st.expander("View Backend Processing Log"):

            st.code(
                st.session_state.analysis_output,
                language="text"
            )

elif st.session_state.analysis_started:

    if st.session_state.analysis_output:

        st.error(
            "Traffic processing failed. Check the error details."
        )

        with st.expander(
            "View Backend Error Details",
            expanded=True
        ):

            st.code(
                st.session_state.analysis_output,
                language="text"
            )


if st.session_state.dashboard_notice:

    st.info(st.session_state.dashboard_notice)


st.divider()


# ==================================================
# 10. LOAD REPORT
# ==================================================

df, metrics = load_report()

if df.empty or not metrics:

    st.markdown(
        '<div class="section-title">Traffic Dashboard</div>',
        unsafe_allow_html=True
    )

    st.info(
        "No traffic report is available yet. "
        "Upload a video above and run traffic analysis."
    )

    st.stop()


# ==================================================
# 11. EXTRACT ANALYTICS
# ==================================================

total = get_number(metrics, "Total Vehicles")

cars = get_number(metrics, "Car")
motorcycles = get_number(metrics, "Motorcycle")
buses = get_number(metrics, "Bus")
trucks = get_number(metrics, "Truck")

flow = get_decimal(metrics, "Traffic Flow")

density = get_decimal(
    metrics,
    "Average Visible Vehicles"
)

traffic_status = str(
    metrics.get("Traffic Status", "Not Available")
)

report_date = str(
    metrics.get("Date", "Not Available")
)


# ==================================================
# 12. DASHBOARD HEADER
# ==================================================

st.markdown(
    '<div class="section-title">📊 Traffic Dashboard</div>',
    unsafe_allow_html=True
)

st.caption(f"Last report generated: {report_date}")


# ==================================================
# 13. CLEAR DASHBOARD DISPLAY
# ==================================================

clear_col, report_col = st.columns([1, 4])

with clear_col:

    if st.button("Clear Dashboard View"):

        st.session_state.analysis_started = False
        st.session_state.analysis_success = False
        st.session_state.analysis_output = ""
        st.session_state.dashboard_notice = ""

        st.rerun()

with report_col:

    st.caption(
        "Clearing the dashboard view does not delete your CSV report."
    )


# ==================================================
# 14. OVERVIEW PAGE
# ==================================================

if page == "Overview":

    st.markdown(
        '<div class="section-title">Vehicle Overview</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        show_kpi("Total Vehicles", total, "🚘")

    with c2:
        show_kpi("Cars", cars, "🚗")

    with c3:
        show_kpi("Motorcycles", motorcycles, "🏍️")

    with c4:
        show_kpi("Buses", buses, "🚌")

    with c5:
        show_kpi("Trucks", trucks, "🚚")

    st.markdown(
        '<div class="section-title">Traffic Insights</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns([1.5, 1])

    with left:

        st.markdown(
            '<div class="panel">',
            unsafe_allow_html=True
        )

        st.markdown("### Vehicle Distribution")

        chart_data = pd.DataFrame({
            "Vehicle": [
                "Cars",
                "Motorcycles",
                "Buses",
                "Trucks"
            ],
            "Count": [
                cars,
                motorcycles,
                buses,
                trucks
            ]
        })

        chart_data = chart_data[
            chart_data["Count"] > 0
        ]

        if not chart_data.empty:

            fig = px.pie(
                chart_data,
                names="Vehicle",
                values="Count",
                hole=0.65,
                color_discrete_sequence=[
                    "#3b82f6",
                    "#06b6d4",
                    "#8b5cf6",
                    "#f59e0b"
                ]
            )

            fig.update_layout(
                paper_bgcolor="#101d31",
                font_color="#e2e8f0",
                margin=dict(t=15, b=15, l=10, r=10),
                annotations=[
                    dict(
                        text=f"<b>{total}</b><br>Vehicles",
                        x=0.5,
                        y=0.5,
                        showarrow=False,
                        font_size=20,
                        font_color="white"
                    )
                ]
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No vehicle counts available.")

        st.markdown("</div>", unsafe_allow_html=True)

    with right:

        st.markdown(
            '<div class="panel">',
            unsafe_allow_html=True
        )

        st.markdown("### Traffic Condition")

        colors = {
            "Low Traffic": "#34d399",
            "Moderate Traffic": "#fbbf24",
            "Heavy Traffic": "#f87171"
        }

        status_color = colors.get(
            traffic_status,
            "#94a3b8"
        )

        st.markdown(f"""
        <div class="status-panel">
            <div style="font-size:12px;color:#94a3b8;">
                CURRENT TRAFFIC STATUS
            </div>
            <div style="
                font-size:25px;
                font-weight:800;
                color:{status_color};
                margin-top:12px;
            ">
                {traffic_status}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Traffic Metrics")

        st.metric(
            "Traffic Flow",
            f"{flow:.2f} vehicles/min"
        )

        st.metric(
            "Average Visible Vehicles",
            f"{density:.2f}"
        )

        st.markdown("</div>", unsafe_allow_html=True)


# ==================================================
# 15. VEHICLE ANALYTICS PAGE
# ==================================================

elif page == "Vehicle Analytics":

    st.markdown(
        '<div class="section-title">Vehicle Analytics</div>',
        unsafe_allow_html=True
    )

    chart_data = pd.DataFrame({
        "Vehicle Type": [
            "Car",
            "Motorcycle",
            "Bus",
            "Truck"
        ],
        "Count": [
            cars,
            motorcycles,
            buses,
            trucks
        ]
    })

    left, right = st.columns(2)

    with left:

        st.markdown(
            '<div class="panel">',
            unsafe_allow_html=True
        )

        st.markdown("### Vehicle Category Comparison")

        fig = px.bar(
            chart_data,
            x="Vehicle Type",
            y="Count",
            color="Vehicle Type",
            text="Count",
            color_discrete_sequence=[
                "#3b82f6",
                "#06b6d4",
                "#8b5cf6",
                "#f59e0b"
            ]
        )

        fig.update_traces(
            textposition="outside"
        )

        fig = chart_layout(fig)

        fig.update_layout(
            showlegend=False,
            xaxis_title="",
            yaxis_title="Vehicle Count"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with right:

        st.markdown(
            '<div class="panel">',
            unsafe_allow_html=True
        )

        st.markdown("### Vehicle Statistics")

        st.dataframe(
            chart_data,
            use_container_width=True,
            hide_index=True
        )

        st.metric(
            "Total Counted Vehicles",
            f"{total:,}"
        )

        st.markdown("</div>", unsafe_allow_html=True)


# ==================================================
# 16. TRAFFIC ANALYTICS PAGE
# ==================================================

elif page == "Traffic Analytics":

    st.markdown(
        '<div class="section-title">Traffic Monitoring Analytics</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        show_kpi("Traffic Flow", f"{flow:.2f}", "📈")

    with c2:
        show_kpi("Average Visible Vehicles", f"{density:.2f}", "🚘")

    with c3:
        show_kpi("Traffic Status", traffic_status, "🚦")

    st.markdown(
        '<div class="section-title">Traffic Analysis Summary</div>',
        unsafe_allow_html=True
    )

    traffic_df = pd.DataFrame({
        "Metric": [
            "Total Vehicles",
            "Cars",
            "Motorcycles",
            "Buses",
            "Trucks",
            "Traffic Flow",
            "Average Visible Vehicles",
            "Traffic Status"
        ],
        "Value": [
            total,
            cars,
            motorcycles,
            buses,
            trucks,
            flow,
            density,
            traffic_status
        ]
    })

    st.dataframe(
        traffic_df,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Average visible vehicles is an occupancy proxy, "
        "not a calibrated physical traffic density measurement."
    )


# ==================================================
# 17. CSV REPORTS PAGE
# ==================================================

elif page == "CSV Reports":

    st.markdown(
        '<div class="section-title">Traffic Reports</div>',
        unsafe_allow_html=True
    )

    st.success("Traffic report loaded successfully.")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        label="⬇ Download Traffic Report",
        data=CSV_PATH.read_bytes(),
        file_name="traffic_report.csv",
        mime="text/csv"
    )


# ==================================================
# 18. FOOTER
# ==================================================

st.divider()

st.markdown("""
<div class="footer">
    AI-POWERED SMART TRAFFIC MANAGEMENT SYSTEM
    <br><br>
    Python · YOLO11 · OpenCV · ByteTrack · Streamlit
    <br><br>
    Developed by Muhammad Fahad
</div>
""", unsafe_allow_html=True)
