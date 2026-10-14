"""
Simple dashboard for Arduino pressure readings.

Install:
    pip install streamlit pandas

Run from the project folder:
    streamlit run files/dashboard.py
"""

from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Pressure Monitor", layout="wide")
st.title("Compressed Air Pressure Monitor")

# The logger may save the CSV beside this file or in the project folder.
script_folder = Path(__file__).resolve().parent
project_folder = script_folder.parent
csv_file = script_folder / "pressure_log.csv"

if not csv_file.exists():
    csv_file = project_folder / "pressure_log.csv"

st.write("This dashboard reads pressure_log.csv created by simple_logger.py.")

try:
    # The logger writes five values on each line and does not write a header.
    data = pd.read_csv(
        csv_file,
        header=None,
        names=["time_ms", "V1", "P1_psi", "V2", "P2_psi"],
    )
except FileNotFoundError:
    st.error(
        f"Could not find {csv_file}. Start simple_logger.py first "
        "and check that the Arduino is connected."
    )
    st.stop()
except pd.errors.EmptyDataError:
    st.warning("The pressure log is empty. Wait for the logger to record readings.")
    st.stop()

# Convert the CSV values to numbers and remove any incomplete rows.
for column in ["time_ms", "V1", "P1_psi", "V2", "P2_psi"]:
    data[column] = pd.to_numeric(data[column], errors="coerce")

data = data.dropna().copy()

if data.empty:
    st.error(
        "There are no valid readings in the CSV. "
        "Each row should contain: time_ms, V1, P1_psi, V2, P2_psi."
    )
    st.stop()

# The Arduino time is in milliseconds. Convert it to seconds for the chart
# and pressure decay calculation.
data["time_s"] = data["time_ms"] / 1000

# Pressure decay = pressure lost divided by time passed.
# A rising pressure is shown as 0 decay instead of a negative decay value.
seconds_between_readings = data["time_s"].diff()
seconds_between_readings = seconds_between_readings.where(
    seconds_between_readings > 0
)
data["decay_P1"] = (
    (data["P1_psi"].shift(1) - data["P1_psi"])
    / seconds_between_readings
).clip(lower=0)
data["decay_P2"] = (
    (data["P2_psi"].shift(1) - data["P2_psi"])
    / seconds_between_readings
).clip(lower=0)

# Get the latest sensor readings.
latest = data.iloc[-1]
pressure_1 = latest["P1_psi"]
pressure_2 = latest["P2_psi"]
pressure_difference = abs(pressure_1 - pressure_2)

if len(data) >= 5:
    pressure_drop_1 = pressure_1 - data["P1_psi"].iloc[-5]
    pressure_drop_2 = pressure_2 - data["P2_psi"].iloc[-5]
else:
    pressure_drop_1 = 0
    pressure_drop_2 = 0

if (
    pressure_1 < 30
    or pressure_2 < 30
    or pressure_drop_1 < -10
    or pressure_drop_2 < -10
):
    st.error("System status: ALARM")
elif pressure_1 < 45 or pressure_2 < 45 or pressure_difference > 8:
    st.warning("System status: WARNING")
else:
    st.success("System status: NORMAL")

st.subheader("Current pressure")
pressure_col1, pressure_col2, difference_col = st.columns(3)

with pressure_col1:
    st.metric("Sensor 1", f"{pressure_1:.2f} PSI")

with pressure_col2:
    st.metric("Sensor 2", f"{pressure_2:.2f} PSI")

with difference_col:
    st.metric("Difference", f"{pressure_difference:.2f} PSI")

st.subheader("Current pressure decay")
decay_col1, decay_col2 = st.columns(2)

with decay_col1:
    decay_1 = latest["decay_P1"]
    if pd.isna(decay_1):
        st.metric("Sensor 1 decay", "Not available yet")
    else:
        st.metric("Sensor 1 decay", f"{decay_1:.3f} PSI/second")

with decay_col2:
    decay_2 = latest["decay_P2"]
    if pd.isna(decay_2):
        st.metric("Sensor 2 decay", "Not available yet")
    else:
        st.metric("Sensor 2 decay", f"{decay_2:.3f} PSI/second")

st.subheader("Pressure over time")
st.line_chart(data.set_index("time_s")[["P1_psi", "P2_psi"]])

st.subheader("Most recent readings")
st.dataframe(
    data[
        ["time_ms", "P1_psi", "P2_psi", "decay_P1", "decay_P2"]
    ].tail(10),
    hide_index=True,
)
