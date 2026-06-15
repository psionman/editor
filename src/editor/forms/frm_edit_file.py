"""EditFrame for Editor launcher."""
import tkinter as tk
from tkinter import ttk
from pathlib import Path

from editor.constants import APP_TITLE, DEFAULT_GEOMETRY
from psiutils.constants import PAD, Pad
from psiutils.buttons import ButtonFrame, IconButton
from psiutils.utilities import window_resize


from editor.utilities import get_path
from editor.data_server import FileData
from editor.config import read_config
from editor.text import Text

txt = Text()

FRAME_TITLE = f'{APP_TITLE} - edit'


class EditFrame():
    def __init__(self, parent: tk.Frame) -> None:
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.config = read_config()
        self.file_data = parent.file_data
        # tk variables
        self.hint = tk.StringVar(value=self.file_data.hint)
        self.file_path = tk.StringVar(value=self.file_data.path)
        self.source_type = tk.StringVar(value=self.file_data.source_type)

        self.hint.trace_add('write', self._value_changed)
        self.file_path.trace_add('write', self._value_changed)
        self.source_type.trace_add('write', self._value_changed)


        self.show()

    def show(self) -> None:
        root = self.root
        try:
            root.geometry(self.config.geometry[Path(__file__).stem])
        except KeyError:
            root.geometry(DEFAULT_GEOMETRY)
        root.transient(self.parent.root)
        root.title(FRAME_TITLE)
        root.bind('<Configure>',
                  lambda event, arg=None: window_resize(self, __file__))

        root.bind('<Control-x>', self._dismiss)

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)
        self.button_frame = self._button_frame(root)
        self.button_frame.grid(row=8, column=0, columnspan=9,
                               sticky=tk.EW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        # frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        row = 0
        label = ttk.Label(frame, text="Hint")
        label.grid(row=row, column=0, sticky=tk.W, padx=PAD, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.hint)
        entry.grid(row=row, column=1, sticky=tk.EW, padx=PAD, pady=PAD)

        row += 1
        file_frame = self._file_frame(frame)
        file_frame.grid(row=row, column=0, columnspan=2, sticky=tk.EW, padx=PAD, pady=PAD)

        return frame

    def _file_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(1, weight=1)

        row = 0
        source_frame = self._source_frame(frame)
        source_frame.grid(row=row, column=1, sticky=tk.W, padx=PAD)

        row += 1
        label = ttk.Label(frame, text="Path")
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=Pad.S)

        entry = ttk.Entry(frame, textvariable=self.file_path)
        entry.grid(row=row, column=1, sticky=tk.EW)

        button = IconButton(frame, txt.OPEN, "open", self._get_path)
        button.grid(row=row, column=2, padx=PAD, pady=Pad.S)
        return frame

    def _source_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(1, weight=1)

        row = 0
        for column, source_type in enumerate(['file', 'dir']):
            radio = ttk.Radiobutton(
                frame, text=source_type, variable=self.source_type, value=source_type
            )
            radio.grid(row=row, column=column, sticky=tk.E, padx=PAD, pady=PAD)

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            frame.icon_button('save', self._save, True),
            frame.icon_button('exit', self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _get_path(self, *args) -> None:
        file_path = get_path(self.source_type.get())
        if file_path:
            self.file_path.set(file_path)
            self._value_changed()

    def _value_changed(self, *args) -> bool:
        """
        Determine whether any configuration value has changed.
        """
        changes = (
            self.file_data.hint != self.hint.get()
            or self.file_data.path != self.file_path.get()
            or self.file_data.source_type != self.source_type.get()
        )
        self.button_frame.enable(changes)

    def _save(self, *args) -> None:
        self.file_data.delete()
        file_data = FileData(hint=self.hint.get(), source_type=self.source_type.get(), path=self.file_path.get())
        file_data.append()
        self._dismiss()

    def _dismiss(self, *args) -> None:
        self.root.destroy()
