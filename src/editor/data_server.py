# data_server.py
from dataclasses import dataclass
from pathlib import Path
import csv
from editor.constants import USER_DATA_DIR

#/home/jeff/.config/ai_api/config.toml

FIELD_NAMES = ["hint", "path"]
PATH = Path(USER_DATA_DIR, 'files.csv')

class FileData:
    def __init__(self, hint: str = "", path: str = ""):
        self.hint = hint
        self.path = path

    def __repr__(self):
        return f"FileData(hint='{self.hint}', path='{self.path}')"

    @property
    def short_path(self):
        return self.path.replace(str(Path.home()), "~")

    def serialize(self):
        return {"hint": self.hint, "path": self.path}

    def deserialize(self, data: dict):
        self.hint = data["hint"]
        self.path = data["path"]

    def save(self):
        self._write_csv_file()

    def _write_csv_file(self):
        write_header = not PATH.exists()
        with open(PATH, "a", newline="", encoding="utf-8") as f_csv:
            writer = csv.DictWriter(f_csv, fieldnames=FIELD_NAMES)
            if write_header:
                writer.writeheader()
            writer.writerow(self.serialize())



def load_files():
    """Load files data from the CSV file."""
    if not PATH.exists():
        return []

    files = []
    with open(PATH, newline="", encoding="utf-8") as f_csv:
        reader = csv.DictReader(f_csv)
        for row in reader:
            file_data = FileData()
            file_data.deserialize(row)
            files.append(file_data)

    return files
