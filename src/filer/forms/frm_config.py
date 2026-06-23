"""ConfigFrame for Editor launcher."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from psiutils.buttons import ButtonFrame, IconButton
from psiutils.constants import PAD
from psiutils.utilities import window_resize

from filer import logger
from filer.config import read_config
from filer.constants import APP_TITLE
from filer.text import Text

txt = Text()

FIELDS = {
    "data_directory": tk.StringVar,
    "my_int": tk.IntVar,
    "my_bool": tk.BooleanVar,
}


class ConfigFrame:
    """
    A configuration dialog for editing application settings.
    """

    data_directory: tk.StringVar
    my_int: tk.IntVar
    my_bool: tk.BooleanVar

    def __init__(self, parent: tk.Frame) -> None:
        # pylint: disable=no-member)
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        config = read_config()
        self.config = config
        self.dialog_opened = False
        self.save_button = None

        # tk variables and trace
        for field, f_type in FIELDS.items():
            if f_type is tk.StringVar:
                setattr(self, field, self._stringvar(getattr(config, field)))
            elif f_type is tk.IntVar:
                setattr(self, field, self._intvar(getattr(config, field)))
            elif f_type is tk.BooleanVar:
                setattr(self, field, self._boolvar(getattr(config, field)))

        self._show()

    def _stringvar(self, value: str) -> tk.StringVar:
        stringvar = tk.StringVar(value=value)
        stringvar.trace_add("write", self._check_value_changed)
        return stringvar

    def _intvar(self, value: int) -> tk.IntVar:
        intvar = tk.IntVar(value=value)
        intvar.trace_add("write", self._check_value_changed)
        return intvar

    def _boolvar(self, value: bool) -> tk.BooleanVar:
        boolvar = tk.BooleanVar(value=value)
        boolvar.trace_add("write", self._check_value_changed)
        return boolvar

    def _show(self) -> None:
        """
        Initialize and display the configuration form GUI.
        """
        # pylint: disable=no-member)
        root = self.root
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.transient(self.parent.root)
        root.title(f"{APP_TITLE} - {txt.CONFIG}")

        root.bind("<Control-x>", self._dismiss)
        root.bind("<Control-s>", self._save_config)
        root.bind(
            "<Configure>",
            lambda event, arg=None: window_resize(self, __file__),
        )
        root.bind("<FocusIn>", self._set_config)

        root.rowconfigure(1, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)
        self.button_frame = self._button_frame(root)
        self.button_frame.grid(
            row=8, column=0, columnspan=9, sticky=tk.EW, padx=PAD, pady=PAD
        )

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        """
        Create and return the main frame containing form input widgets.
        """
        frame = ttk.Frame(master)
        frame.columnconfigure(1, weight=1)

        row = 0
        label = ttk.Label(frame, text="label text")
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.data_directory)
        entry.grid(row=row, column=1, sticky=tk.EW)

        button = IconButton(frame, txt.OPEN, "open", self._get_data_directory)
        button.grid(row=row, column=2, padx=PAD)

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        """
        Create and return the button frame for the form.
        """
        frame = ButtonFrame(master, tk.HORIZONTAL)
        self.save_button = IconButton(
            frame, txt.SAVE, "save", self._save_config, True
        )
        frame.buttons = [
            self.save_button,
            frame.icon_button("exit", self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _check_value_changed(self, *args) -> bool:
        """
        Enable or disable form buttons based on changes in configuration.
        """
        enable = bool(self._config_changes())
        self.button_frame.enable(enable)

    def _get_data_directory(self, *args) -> None:
        directory = self._get_directory(self.data_directory.get())
        if directory:
            self.data_directory.set(directory)

    def _get_directory(self, default: str) -> str:
        """
        Prompt the user to select a new data directory and update the value.
        """
        self.dialog_opened = True
        return filedialog.askdirectory(
            initialdir=Path(default),
            parent=self.root,
        )

    def _save_config(self):
        changes = {
            field: f"(old value={change[0]}, new_value={change[1]})"
            for field, change in self._config_changes().items()
        }

        for field in FIELDS:
            self.config.update(field, getattr(self, field).get())

        logger.info("Config saved", changes=changes)
        self.save_button.disable()
        return self.config.save()

    def _config_changes(self) -> dict:
        stored = self.config.config
        return {
            field: (stored[field], getattr(self, field).get())
            for field in FIELDS
            if stored[field] != getattr(self, field).get()
        }

    def _set_config(self, *args) -> None:
        if self.dialog_opened:
            self.dialog_opened = False
            return
        self.config = read_config()
        for field in FIELDS:
            getattr(self, field).set(self.config.config[field])

    def _dismiss(self, *args) -> None:
        """
        Close the configuration window and terminate the application.
        """
        self.root.destroy()
