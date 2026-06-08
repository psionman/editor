"""Read and write user data file."""
from pathlib import Path
import csv


from editor.constants import USER_DATA_DIR, USER_DATA_FILE
from editor import logger

PATH = Path(USER_DATA_DIR, USER_DATA_FILE)

class DataFile:
    """Utility to retrieve and save user data file."""
    def __init__(self, content: dict = None):
        self.content = content or []

    def save(self):
        self._write_csv_file()

    def _write_csv_file(self):
        write_header = not PATH.exists()
        with open(PATH, "a", newline="", encoding="utf-8") as f_csv:
            writer = csv.DictWriter(f_csv, fieldnames=FIELD_NAMES)
            if write_header:
                writer.writeheader()
            writer.writerow(self.serialize())
