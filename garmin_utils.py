import os
import csv
import logging
from typing import Optional
import pandas as pd
import garth
from garth.exc import GarthException
from dotenv import load_dotenv
import streamlit as st
import garth
from file_utils import get_user_path


logging.basicConfig(level=logging.INFO)

SPORT_TYPE_GROUPS = {
    "cycling": ["cycling", "road_biking", "gravel_cycling", "mountain_biking", "e_biking"],
    "running": ["running", "trail_running", "treadmill_running"],
    "walking": ["walking", "hiking", "indoor_walking"],
}

def login(username: str, password: str):
    """Login to Garmin and save session for the given user."""
    garth.login(username, password)  # Remove input() for MFA unless handled via Streamlit
    session_dir = os.path.join("garmin_sessions", username)
    os.makedirs(session_dir, exist_ok=True)
    garth.save(session_dir)
    logging.info(f"Logged in and session saved for {username}")


def resume_session(username: str, password: Optional[str] = None):
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


def filter_activities_by_sport(df, sport: str):
    """
    Filters Garmin activities by sport category using predefined type groups.
    """
    sport_types = SPORT_TYPE_GROUPS.get(sport.lower(), [sport.lower()])
    return df[df["activityType.typeKey"].str.lower().isin(sport_types)]


def download_fit_files(sport: str, df: pd.DataFrame, username: str):
    gps_csv_path = get_user_path(username, file_type="gps")
    existing_ids = set()

    if gps_csv_path.exists():
        df_gps = pd.read_csv(gps_csv_path, header=None, names=["lat", "lon", "activity_id", "sport"])
        existing_ids = set(df_gps[df_gps["sport"] == sport]["activity_id"].astype(str).unique())

    fit_folder = get_user_path(username, sport, file_type="fit")
    fit_folder.mkdir(parents=True, exist_ok=True)

    progress_bar = st.progress(0)
    status_text = st.empty()

    downloaded = 0
    skipped = 0
    total = len(df)

    for i, activity_id in enumerate(df['activityId']):
        activity_id_str = str(activity_id)
        if activity_id_str in existing_ids:
            logging.info(f"GPS data for activity {activity_id_str} already exists. Skipping download.")
            skipped += 1
        else:
            file_path = fit_folder / f"{activity_id_str}.fit"
            try:
                fit_data = garth.download(f"/download-service/files/activity/{activity_id_str}")
                with open(file_path, "wb") as fit_file:
                    fit_file.write(fit_data)
                logging.info(f"Downloaded FIT file for activity {activity_id_str}")
                downloaded += 1
            except Exception as e:
                logging.error(f"Failed to download FIT file for activity {activity_id_str}: {e}")

        progress_bar.progress((i + 1) / total)
        status_text.text(f"Downloading {i + 1}/{total} FIT files")

    status_text.text("✅ FIT file download complete.")
    st.success(
        f"Out of {total} {sport} activities, {downloaded} .fit files have been downloaded. "
        f"For the remaining {skipped} {sport} activities, GPS data already exists in gps_points.csv."
    )
