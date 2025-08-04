import pandas as pd
import os
from fitparse import FitFile
import logging
import streamlit as st

logging.basicConfig(level=logging.INFO)

def extract_gps_from_fit(file_path: str, username: str) -> int:
    activity_id = os.path.splitext(os.path.basename(file_path))[0]
    gps_csv_path = os.path.join("user_data", username, "gps_points.csv")
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



def process_fit_folder(folder_path: str, username: str):
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
        points = extract_gps_from_fit(file_path, username)
        total_points += points
        progress_bar.progress((i + 1) / total_files)
        status_text.text(f"Processing {filename} ({i+1}/{total_files})")

    status_text.text(f"✅ Processed {total_files} activities and extracted {total_points} GPS points.")


# import os
# import csv
# from fitparse import FitFile
# from typing import List, Tuple
# import logging
# import streamlit as st

# logging.basicConfig(level=logging.INFO)

# GPS_CSV_PATH = "gps_points.csv"

# def is_activity_in_csv(activity_id: str) -> bool:
#     """Check if the activity ID already exists in the GPS CSV."""
#     if not os.path.exists(GPS_CSV_PATH):
#         return False
#     with open(GPS_CSV_PATH, 'r') as f:
#         reader = csv.reader(f)
#         return any(row[2] == activity_id for row in reader if len(row) == 3)

# def extract_gps_from_fit(file_path: str, username: str) -> int:
#     activity_id = os.path.splitext(os.path.basename(file_path))[0]
#     gps_csv_path = os.path.join("user_data", username, "gps_points.csv")
#     os.makedirs(os.path.dirname(gps_csv_path), exist_ok=True)

#     existing_ids = set()
#     if os.path.exists(gps_csv_path):
#         with open(gps_csv_path, 'r') as f:
#             reader = csv.reader(f)
#             for row in reader:
#                 if len(row) == 3:
#                     existing_ids.add(row[2])

#     if activity_id in existing_ids:
#         logging.info(f"Activity {activity_id} already exists in gps_points.csv. Skipping.")
#         return 0

#     fitfile = FitFile(file_path)
#     rows_to_write = []

#     for record in fitfile.get_messages("record"):
#         record_data = {d.name: d.value for d in record}
#         lat_raw = record_data.get("position_lat")
#         lon_raw = record_data.get("position_long")

#         if lat_raw is not None and lon_raw is not None:
#             lat = lat_raw * (180 / 2**31)
#             lon = lon_raw * (180 / 2**31)
#             rows_to_write.append([lat, lon, activity_id])

#     if rows_to_write:
#         with open(gps_csv_path, 'a', newline='') as f:
#             writer = csv.writer(f)
#             writer.writerows(rows_to_write)
#         logging.info(f"Wrote {len(rows_to_write)} points from activity {activity_id}")
#     return len(rows_to_write)


# import streamlit as st

# def process_fit_folder(folder_path: str, username: str):
#     fit_files = [f for f in os.listdir(folder_path) if f.endswith(".fit")]
#     total_files = len(fit_files)

#     if total_files == 0:
#         st.warning("No FIT files found to process.")
#         return

#     progress_bar = st.progress(0)
#     status_text = st.empty()

#     for i, filename in enumerate(fit_files):
#         file_path = os.path.join(folder_path, filename)
#         status_text.text(f"Processing {filename} ({i+1}/{total_files})")
#         extract_gps_from_fit(file_path, username)
#         progress_bar.progress((i + 1) / total_files)

#     status_text.text("✅ All FIT files processed.")


# def process_fit_folder(folder_path: str, username: str):
#     fit_files = [f for f in os.listdir(folder_path) if f.endswith(".fit")]
#     total_files = len(fit_files)

#     if total_files == 0:
#         st.warning("No FIT files found to process.")
#         return

#     progress_bar = st.progress(0)
#     status_text = st.empty()

#     for i, filename in enumerate(fit_files):
#         file_path = os.path.join(folder_path, filename)
#         status_text.text(f"Processing {filename} ({i+1}/{total_files})")
#         extract_gps_from_fit(file_path, username)
#         progress_bar.progress((i + 1) / total_files)

#     status_text.text("✅ All FIT files processed.")


# def process_fit_folder(folder_path: str, username: str):
#     for filename in os.listdir(folder_path):
#         if filename.endswith(".fit"):
#             file_path = os.path.join(folder_path, filename)
#             extract_gps_from_fit(file_path, username)



# def extract_gps_from_fit(file_path: str) -> int:
#     """Extract GPS points from a .fit file and append to CSV if not already present."""
#     activity_id = os.path.splitext(os.path.basename(file_path))[0]

#     if is_activity_in_csv(activity_id):
#         logging.info(f"Activity {activity_id} already exists in gps_points.csv. Skipping.")
#         return 0

#     fitfile = FitFile(file_path)
#     rows_to_write: List[Tuple[float, float, str]] = []

#     for record in fitfile.get_messages("record"):
#         record_data = {d.name: d.value for d in record}
#         lat_raw = record_data.get("position_lat")
#         lon_raw = record_data.get("position_long")

#         if lat_raw is not None and lon_raw is not None:
#             lat = lat_raw * (180 / 2**31)
#             lon = lon_raw * (180 / 2**31)
#             rows_to_write.append((lat, lon, activity_id))

#     if rows_to_write:
#         with open(GPS_CSV_PATH, 'a', newline='') as f:
#             writer = csv.writer(f)
#             writer.writerows(rows_to_write)
#         logging.info(f"Wrote {len(rows_to_write)} points from activity {activity_id}")
#     return len(rows_to_write)

# def process_fit_folder(folder_path: str):
#     """Process all .fit files in a folder and extract GPS data."""
#     counter = 0
#     for filename in os.listdir(folder_path):
#         if filename.endswith(".fit"):
#             file_path = os.path.join(folder_path, filename)
#             counter += extract_gps_from_fit(file_path)
#     logging.info(f"Processed {counter} GPS points from folder {folder_path}")
