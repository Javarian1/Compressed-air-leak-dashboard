"""
dashboard.py
Simple Streamlit dashboard to visualize logged pressure data.
This is where pandas is genuinely useful: reading the CSV and
reshaping it for plotting.

Install once:
    pip install streamlit pandas

Run with:
    streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Pressure Monitor", layout="wide")
st.title("Compressed Air Pressure Monitor")

# Use a logger-created file beside this script, or the demo file in the project folder.
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
CSV_FILE = SCRIPT_DIR / "pressure_log.csv"
if not CSV_FILE.exists():
    CSV_FILE = PROJECT_DIR / "pressure_log.csv"

DATA_SOURCES = {
    "Current log": CSV_FILE,
    "Normal example": PROJECT_DIR / "test_data" / "pressure_normal.csv",
    "Warning example": PROJECT_DIR / "test_data" / "pressure_warning.csv",
    "Alarm example": PROJECT_DIR / "test_data" / "pressure_alarm.csv",
}
selected_source = st.selectbox("Data source", DATA_SOURCES)
CSV_FILE = DATA_SOURCES[selected_source]

# Auto-refresh every 2 seconds so the dashboard updates while simple_logger.py runs
st_autorefresh = st.empty()

try:
    df = pd.read_csv(
        CSV_FILE,
        names=["time_ms", "V1", "P1_psi", "V2", "P2_psi"],
        header=0,  # first row from the Arduino is a header line
    )
    df["time_s"] = df["time_ms"].astype(float) / 1000

    latest = df.iloc[-1]
    p1 = float(latest["P1_psi"])
    p2 = float(latest["P2_psi"])
    delta = abs(p1 - p2)

    if len(df) >= 5:
        recent_drop_1 = p1 - float(df["P1_psi"].iloc[-5])
        recent_drop_2 = p2 - float(df["P2_psi"].iloc[-5])
    else:
        recent_drop_1 = 0
        recent_drop_2 = 0

    if p1 < 30 or p2 < 30 or recent_drop_1 < -10 or recent_drop_2 < -10:
        status = "ALARM"
        color = "#c62828"
    elif p1 < 45 or p2 < 45 or delta > 8:
        status = "WARNING"
        color = "#ef6c00"
    else:
        status = "NORMAL"
        color = "#2e7d32"

    st.markdown(
        f"""
        <div style="
            background-color:{color};
            color:white;
            padding:15px;
            border-radius:10px;
            font-size:22px;
            font-weight:bold;
            text-align:center;
            margin-bottom:20px;
        ">
            System Status: {status}
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sensor 1 pressure (PSI)", f"{p1:.2f}")
    with col2:
        st.metric("Sensor 2 pressure (PSI)", f"{p2:.2f}")
    with col3:
        st.metric("Pressure Difference (PSI)", f"{delta:.2f}")

    st.subheader("Pressure vs. Time")
    st.line_chart(
        df.set_index("time_s")[["P1_psi", "P2_psi"]]
    )

    st.subheader("Raw data (most recent samples)")
    st.dataframe(df.tail(20))

except FileNotFoundError:
    st.warning(f"Selected data source was not found: {CSV_FILE}")
except Exception as e:
    st.error(f"Error reading data: {e}")
