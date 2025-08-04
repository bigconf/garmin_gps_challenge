import streamlit as st
from pathlib import Path
import zipfile
import logging

def unzip_fit_files(sport: str, username: str) -> list:
    """
     Unzips all .fit files in the sport-specific folder into an 'unzipped' subfolder.
     Returns a list of unzipped file paths.
    """
    source_folder = Path(f"user_data/{username}/{sport}_fit_files")
    destination_folder = source_folder / "unzipped"
    destination_folder.mkdir(parents=True, exist_ok=True)

    fit_files = list(source_folder.glob("*.fit"))
    total_files = len(fit_files)

    if total_files == 0:
        st.warning("No FIT files found to unzip.")
        return []

    progress_bar = st.progress(0)
    status_text = st.empty()
    unzipped_files = []

    for i, file_path in enumerate(fit_files):
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(destination_folder)
                logging.info(f"Unzipped {file_path.name} to {destination_folder}")
                unzipped_files.extend(destination_folder.glob("*.fit"))
        except zipfile.BadZipFile:
            logging.warning(f"{file_path.name} is not a zip file or is corrupted. Skipping.")

        progress_bar.progress((i + 1) / total_files)
        status_text.text(f"Unzipping {file_path.name} ({i+1}/{total_files})")

    status_text.text("✅ All files unzipped.")
    return unzipped_files




