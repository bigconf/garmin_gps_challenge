import os
import csv
from fitparse import FitFile
from typing import List, Tuple
import logging

logging.basicConfig(level=logging.INFO)

GPS_CSV_PATH = "gps_points.csv"

def is_activity_in_csv(activity_id: str) -> bool:
    """Check if the activity ID already exists in the GPS CSV."""
    if not os.path.exists(GPS_CSV_PATH):
        return False
    with open(GPS_CSV_PATH, 'r') as f:
        reader = csv.reader(f)
        return any(row[2] == activity_id for row in reader if len(row) == 3)

def extract_gps_from_fit(file_path: str) -> int:
    """Extract GPS points from a .fit file and append to CSV if not already present."""
    activity_id = os.path.splitext(os.path.basename(file_path))[0]

    if is_activity_in_csv(activity_id):
        logging.info(f"Activity {activity_id} already exists in gps_points.csv. Skipping.")
        return 0

    fitfile = FitFile(file_path)
    rows_to_write: List[Tuple[float, float, str]] = []

    for record in fitfile.get_messages("record"):
        record_data = {d.name: d.value for d in record}
        lat_raw = record_data.get("position_lat")
        lon_raw = record_data.get("position_long")

        if lat_raw is not None and lon_raw is not None:
            lat = lat_raw * (180 / 2**31)
            lon = lon_raw * (180 / 2**31)
            rows_to_write.append((lat, lon, activity_id))

    if rows_to_write:
        with open(GPS_CSV_PATH, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows_to_write)
        logging.info(f"Wrote {len(rows_to_write)} points from activity {activity_id}")
    return len(rows_to_write)

def process_fit_folder(folder_path: str):
    """Process all .fit files in a folder and extract GPS data."""
    counter = 0
    for filename in os.listdir(folder_path):
        if filename.endswith(".fit"):
            file_path = os.path.join(folder_path, filename)
            counter += extract_gps_from_fit(file_path)
    logging.info(f"Processed {counter} GPS points from folder {folder_path}")
