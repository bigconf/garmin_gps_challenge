import os
import zipfile
import logging
from pathlib import Path
from typing import List

logging.basicConfig(level=logging.INFO)

def unzip_fit_files(sport: str) -> List[Path]:
    """
    Unzips all .fit files in the sport-specific folder into an 'unzipped' subfolder.
    Returns a list of unzipped file paths.
    """
    source_folder = Path(f"{sport}_fit_files")
    destination_folder = source_folder / "unzipped"
    destination_folder.mkdir(parents=True, exist_ok=True)

    unzipped_files = []

    for file_path in source_folder.glob("*.fit"):
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(destination_folder)
                logging.info(f"Unzipped {file_path.name} to {destination_folder}")
                unzipped_files.extend(destination_folder.glob("*.fit"))
        except zipfile.BadZipFile:
            logging.warning(f"{file_path.name} is not a zip file or is corrupted. Skipping.")

    logging.info(f"Total unzipped files: {len(unzipped_files)}")
    return unzipped_files
