import os
import csv
import logging
from typing import Optional
import pandas as pd
import garth
from garth.exc import GarthException
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

def login():
    """Login to Garmin using credentials from .env and save session."""
    from dotenv import load_dotenv
    load_dotenv()
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    garth.login(email, password, prompt_mfa=lambda: input("Enter MFA code: "))
    garth.save("~/.garth")
    logging.info("Logged in and session saved.")

def resume_session():
    """Resume Garmin session or prompt for re-login if expired."""
    try:
        garth.resume("~/.garth")
        _ = garth.client.username  # Trigger session check
        logging.info("Session resumed.")
    except GarthException:
        logging.warning("Session expired. Please log in again.")
        login()

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

def download_fit_files(sport: str, df: pd.DataFrame):
    """Download .fit files for new activities and track them in activity_ids.csv."""
    folder_name = f"{sport}_fit_files"
    os.makedirs(folder_name, exist_ok=True)

    existing_ids = set()
    if os.path.exists('activity_ids.csv'):
        with open('activity_ids.csv', 'r') as f:
            reader = csv.reader(f)
            existing_ids = {row[0] for row in reader}

    with open('activity_ids.csv', 'a', newline='') as f:
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
