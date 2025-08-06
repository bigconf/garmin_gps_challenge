import os
import shutil
import logging
import streamlit as st
from pathlib import Path
import zipfile
from typing import Optional

def cleanup_fit_folder(username: str, sport: str = "cycling"):
    """
    Deletes the folder containing downloaded and unzipped FIT files for a given user and sport.
    """
    fit_folder = get_user_path(username, sport, file_type="fit")
    if os.path.exists(fit_folder):
        shutil.rmtree(fit_folder)
        logging.info(f"Cleaned up FIT files at {fit_folder}")
    else:
        logging.info(f"No FIT folder found to clean for user {username}")


def unzip_fit_files(sport: str, username: str) -> list:
    source_folder = get_user_path(username, sport, file_type="fit")
    destination_folder = get_user_path(username, sport, file_type="fit", subfolder="unzipped")
    destination_folder.mkdir(parents=True, exist_ok=True)

    fit_files = list(source_folder.glob("*.fit"))  # or "*.fit" if zipped FIT files
    total_files = len(fit_files)

    if total_files == 0:
        st.warning("No FIT files found to unzip.")
        return []

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, file_path in enumerate(fit_files):
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(destination_folder)
                logging.info(f"Unzipped {file_path.name} to {destination_folder}")
        except zipfile.BadZipFile:
            logging.warning(f"{file_path.name} is not a zip file or is corrupted. Skipping.")

        progress_bar.progress((i + 1) / total_files)
        status_text.text(f"Unzipping {file_path.name} ({i+1}/{total_files})")

    # Scan once after all files are unzipped
    unzipped_files = list(destination_folder.glob("*.fit"))
    status_text.text("✅ All files unzipped.")
    return unzipped_files


def get_user_path(username: str, sport: Optional[str] = None, file_type: str = "gps", subfolder: str = "") -> Path:
    """
    Constructs user-specific paths for different file types and sports.

    Args:
        username (str): Garmin username.
        sport (str): Sport type (e.g., 'cycling').
        file_type (str): Type of file ('gps', 'fit', 'activity_ids').
        subfolder (str): Optional subfolder (e.g., 'unzipped').

    Returns:
        Path: Constructed path as a Path object.
    """
    base = Path("user_data") / username

    if file_type == "gps":
        return base / f"{sport}_gps_points.csv" if sport else base / "gps_points.csv"

    if file_type == "fit":
        path = base / f"{sport}_fit_files"
        return path / subfolder if subfolder else path

    if file_type == "activity_ids":
        return base / "activity_ids.csv"

    raise ValueError(f"Unknown file_type: {file_type}")

