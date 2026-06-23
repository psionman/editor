import os
import subprocess
import threading
from pathlib import Path
from tkinter import filedialog
from typing import Any


def open_in_kate(file_path: str) -> None:
    """Open a file in Kate, or a directory in Dolphin."""
    env = os.environ.copy()
    env["QT_LOGGING_RULES"] = "*.debug=false;*.warning=false"

    if Path(file_path).is_dir():
        subprocess.Popen(
            ["dolphin", file_path],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return

    _call_process(["kate", file_path])
    _activate_kate(file_path)


def _activate_kate(file_path: str) -> None:
    subprocess.run(
        [
            "gdbus",
            "call",
            "--session",
            "--dest",
            "org.kde.kate",
            "--object-path",
            "/MainApplication",
            "--method",
            "org.kde.Kate.Application.activate",
            f"file://{file_path}",
        ],
        check=False,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        [
            "kdotool",
            "search",
            "--name",
            "kate",
            "windowactivate",
        ],
        check=False,
    )


def _call_process(process: list) -> Any:
    threading.Thread(
        target=_call_process_worker,
        args=(process,),
        daemon=True,
    ).start()


def _call_process_worker(process: list) -> None:
    proc = subprocess.Popen(
        process,
        stdout=subprocess.PIPE,
        text=True,
    )

    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        error = "None"
        if stderr:
            error = stderr.strip().split("\n")[-1]
        logger.error("Process failed", process=process, error=error)


def get_path(source_type: str) -> str:
    if source_type == "file":
        return _get_file_path()
    else:
        return _get_directory_path()


def _get_file_path() -> str:
    file_path = filedialog.askopenfilename(
        title="Select a file",
        initialdir=Path.home(),
        filetypes=[("All files", "*.*")],
    )
    return file_path


def _get_directory_path() -> str:
    dir_path = filedialog.askdirectory(
        title="Select a directory",
        initialdir=Path.home(),
    )
    return dir_path
