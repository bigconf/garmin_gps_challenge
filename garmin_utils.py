import os
import csv
import logging
from typing import Optional
import pandas as pd
import garth
from garth.exc import GarthException
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)


logging.basicConfig(level=logging.INFO)

def login(username: str, password: str):
    """Login to Garmin and save session for the given user."""
    garth.login(username, password)  # Remove input() for MFA unless handled via Streamlit
    session_dir = os.path.join("garmin_sessions", username)
    os.makedirs(session_dir, exist_ok=True)
    garth.save(session_dir)
    logging.info(f"Logged in and session saved for {username}")


def resume_session(username: str, password: str = None):
    """Resume Garmin session for the given user or prompt login if missing/expired."""
    session_dir = os.path.join("garmin_sessions", username)

    if not os.path.exists(session_dir):
        logging.warning(f"No session found for {username}. Logging in.")
        if password is None:
            raise ValueError("Password required for login.")
        login(username, password)
        return

    try:
        garth.resume(session_dir)
        _ = garth.client.username
        logging.info(f"Session resumed for {username}")
    except GarthException:
        logging.warning(f"Session expired for {username}. Logging in again.")
        if password is None:
            raise ValueError("Password required for login.")
        login(username, password)



def download_activities(n: Optional[int] = None) -> pd.DataFrame:
    """Download all or latest n activities with GPS data."""
    all_activities = []
    start = 0
    limit = 100

    while True:
        batch = garth.connectapi(
            "/activitylist-service/activities/search/activities",
            params={"start": start, "limit": limit if n is None else min(limit, n - len(all_activities))}
        )
        if not batch:
            break
        all_activities.extend(batch)
        start += limit
        if n is not None and len(all_activities) >= n:
            break

    df = pd.json_normalize(all_activities)
    df = df[df['hasPolyline'] == True]  # Only GPS-enabled
    virtual_keywords = ['virtual_ride', 'indoor_cycling']
    mask = df['activityType.typeKey'].str.contains('|'.join(virtual_keywords), case=False, na=False)
    return df[~mask].reset_index(drop=True)

def filter_cycling_activities(df: pd.DataFrame) -> pd.DataFrame:
    """Filter DataFrame to include only cycling-related activities."""
    cycling_types = ['cycling', 'road_biking', 'gravel_cycling']
    return df[df['activityType.typeKey'].isin(cycling_types)].reset_index(drop=True)

def download_fit_files(sport: str, df: pd.DataFrame, username: str):
    folder_name = f"user_data/{username}/{sport}_fit_files"
    os.makedirs(folder_name, exist_ok=True)

    activity_ids_path = os.path.join(f"user_data/{username}", "activity_ids.csv")
    os.makedirs(os.path.dirname(activity_ids_path), exist_ok=True)

    existing_ids = set()
    if os.path.exists(activity_ids_path):
        with open(activity_ids_path, 'r') as f:
            reader = csv.reader(f)
            existing_ids = {row[0] for row in reader}

    with open(activity_ids_path, 'a', newline='') as f:
        writer = csv.writer(f)
        for activity_id in df['activityId']:
            if str(activity_id) in existing_ids:
                logging.info(f"Activity {activity_id} already exists. Skipping.")
                continue

            file_path = os.path.join(folder_name, f"{activity_id}.fit")
            try:
                fit_data = garth.download(f"/download-service/files/activity/{activity_id}")
                with open(file_path, "wb") as fit_file:
                    fit_file.write(fit_data)
                logging.info(f"Downloaded FIT file for activity {activity_id}")
                writer.writerow([activity_id])
            except Exception as e:
                logging.error(f"Failed to download FIT file for activity {activity_id}: {e}")




