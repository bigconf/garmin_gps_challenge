import os
import shutil
import logging

def cleanup_fit_folder(username: str, sport: str = "cycling"):
    """
    Deletes the folder containing downloaded and unzipped FIT files for a given user and sport.
    """
    fit_folder = os.path.join("user_data", username, f"{sport}_fit_files")
    if os.path.exists(fit_folder):
        shutil.rmtree(fit_folder)
        logging.info(f"Cleaned up FIT files at {fit_folder}")
    else:
        logging.info(f"No FIT folder found to clean for user {username}")
