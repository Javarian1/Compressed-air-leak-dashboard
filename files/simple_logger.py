"""
simple_logger.py
Reads the Arduino's serial output (from PressureLogger.ino) and saves
each sample to a CSV file in real time. Uses the built-in csv module —
no pandas needed for this step.

Install once:
    pip install pyserial
"""

import serial
import csv
import time

# ---- USER SETTINGS ----
PORT = "/dev/tty.usbmodemXXXX"   # Change to your Arduino's port (see note below)
BAUD = 115200                     # Must match Serial.begin() in the .ino file
OUTFILE = "pressure_log.csv"
# ------------------------

# How to find PORT on a Mac:
#   1. Plug in the Arduino
#   2. Open Terminal and run: ls /dev/tty.*
#   3. Look for something like /dev/tty.usbmodem14201 or /dev/tty.usbserial-XXXX

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # give the Arduino a moment to reset after the serial connection opens

with open(OUTFILE, mode="w", newline="") as f:
    writer = csv.writer(f)

    print(f"Logging to {OUTFILE}. Press Ctrl+C to stop.\n")

    try:
        while True:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                continue

            row = line.split(",")
            writer.writerow(row)
            f.flush()  # write to disk immediately, don't wait for buffer to fill

            print(row)  # live feedback in the terminal

    except KeyboardInterrupt:
        print("\nStopped. Data saved to", OUTFILE)

    finally:
        ser.close()
