import pandas as pd
import os
from fitparse import FitFile
import logging
import streamlit as st
from file_utils import get_user_path

logging.basicConfig(level=logging.INFO)

def extract_gps_from_fit(file_path: str, username: str, sport: str) -> int:
    activity_id = os.path.splitext(os.path.basename(file_path))[0]
    gps_csv_path = get_user_path(username, sport, file_type="gps")

    os.makedirs(os.path.dirname(gps_csv_path), exist_ok=True)

    # Load existing data if available
    if os.path.exists(gps_csv_path):
        df_existing = pd.read_csv(gps_csv_path, header=None, names=["lat", "lon", "activity_id"])
        if activity_id in df_existing["activity_id"].values:
            logging.info(f"Activity {activity_id} already exists in gps_points.csv. Skipping.")
            return 0
    else:
        df_existing = pd.DataFrame(columns=["lat", "lon", "activity_id"])

    # Extract GPS points from FIT file
    fitfile = FitFile(file_path)
    new_rows = []

    for record in fitfile.get_messages("record"):
        record_data = {d.name: d.value for d in record}
        lat_raw = record_data.get("position_lat")
        lon_raw = record_data.get("position_long")

        if lat_raw is not None and lon_raw is not None:
            lat = lat_raw * (180 / 2**31)
            lon = lon_raw * (180 / 2**31)
            new_rows.append([lat, lon, activity_id])

    # Append and write back to CSV
    if new_rows:
        df_new = pd.DataFrame(new_rows, columns=["lat", "lon", "activity_id"])
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.to_csv(gps_csv_path, index=False, header=False)
        logging.info(f"Wrote {len(new_rows)} points from activity {activity_id}")

    return len(new_rows)



def process_fit_folder(folder_path: str, username: str, sport: str):
    fit_files = [f for f in os.listdir(folder_path) if f.endswith(".fit")]
    total_files = len(fit_files)

    if total_files == 0:
        st.warning("No FIT files found to process.")
        return

    progress_bar = st.progress(0)
    status_text = st.empty()
    total_points = 0

    for i, filename in enumerate(fit_files):
        file_path = os.path.join(folder_path, filename)
        points = extract_gps_from_fit(file_path, username, sport)
        total_points += points
        progress_bar.progress((i + 1) / total_files)
        status_text.text(f"Processing {filename} ({i+1}/{total_files})")

    status_text.text(f"✅ Processed {total_files} activities and extracted {total_points} GPS points.")


