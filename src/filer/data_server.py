# data_server.py
import csv
from pathlib import Path

from filer.constants import USER_DATA_DIR

# /home/jeff/.config/ai_api/config.toml

FIELD_NAMES = ["hint", "type", "path"]
PATH = Path(USER_DATA_DIR, "files.csv")


class FileData:
    def __init__(
        self, hint: str = "", source_type: str = "file", path: str = ""
    ):
        self.hint = hint
        self.source_type = source_type
        self.path = path

    def __repr__(self):
        return f"FileData(hint='{self.hint}', path='{self.path}')"

    @property
    def short_path(self):
        return self.path.replace(str(Path.home()), "~")

    def serialize(self):
        return {"hint": self.hint, "type": self.source_type, "path": self.path}

    def deserialize(self, data: dict):
        self.hint = data["hint"]
        self.source_type = data["type"]
        self.path = data["path"]

    def append(self):
        self._write_csv_file()

    def _write_csv_file(self):
        write_header = not PATH.exists()
        with open(PATH, "a", newline="", encoding="utf-8") as f_csv:
            writer = csv.DictWriter(f_csv, fieldnames=FIELD_NAMES)
            if write_header:
                writer.writeheader()
            writer.writerow(self.serialize())

    def delete(self):
        if not PATH.exists():
            return
        rows = []
        with open(PATH, newline="", encoding="utf-8") as f_csv:
            reader = csv.DictReader(f_csv)
            rows = [row for row in reader if row["hint"] != self.hint]
        with open(PATH, "w", newline="", encoding="utf-8") as f_csv:
            writer = csv.DictWriter(f_csv, fieldnames=FIELD_NAMES)
            writer.writeheader()
            writer.writerows(rows)


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
