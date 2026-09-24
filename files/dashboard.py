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
CSV_FILE = Path(__file__).resolve().parent / "pressure_log.csv"
if not CSV_FILE.exists():
    CSV_FILE = CSV_FILE.parent.parent / "pressure_log.csv"

# Auto-refresh every 2 seconds so the dashboard updates while simple_logger.py runs
st_autorefresh = st.empty()

try:
    df = pd.read_csv(
        CSV_FILE,
        names=["time_ms", "V1", "P1_psi", "V2", "P2_psi"],
        header=0,  # first row from the Arduino is a header line
    )
    df["time_s"] = df["time_ms"].astype(float) / 1000

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Sensor 1 pressure (PSI)", f"{df['P1_psi'].iloc[-1]:.2f}")
    with col2:
        st.metric("Sensor 2 pressure (PSI)", f"{df['P2_psi'].iloc[-1]:.2f}")

    st.subheader("Pressure vs. Time")
    st.line_chart(
        df.set_index("time_s")[["P1_psi", "P2_psi"]]
    )

    st.subheader("Raw data (most recent samples)")
    st.dataframe(df.tail(20))

except FileNotFoundError:
    st.warning(f"Waiting for {CSV_FILE} — add pressure_log.csv or start simple_logger.py first.")
except Exception as e:
    st.error(f"Error reading data: {e}")
