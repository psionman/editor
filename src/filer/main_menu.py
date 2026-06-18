"""Main menu for Editor launcher."""

import tkinter as tk
import webbrowser
from tkinter import messagebox

from psiutils.menus import Menu, MenuItem

from filer._version import __version__
from filer.config import config
from filer.constants import APP_TITLE, AUTHOR, HELP_URI
from filer.forms.frm_config import ConfigFrame
from filer.text import Text

txt = Text()
SPACES = 30


class MainMenu:
    def __init__(self, parent):
        self.parent = parent
        self.root = parent.root

    def create(self):
        menubar = tk.Menu()
        self.root["menu"] = menubar

        # File menu
        file_menu = Menu(menubar, self._file_menu_items())
        menubar.add_cascade(menu=file_menu, label="File")

        # Help menu
        help_menu = Menu(menubar, self._help_menu_items())
        menubar.add_cascade(menu=help_menu, label="Help")

    def _file_menu_items(self) -> list:
        return [
            MenuItem(f"{txt.CONFIG}{txt.ELLIPSIS}", self._show_config_frame),
            MenuItem(txt.CLOSE, self._dismiss),
        ]

    def _show_config_frame(self):
        """Display the config frame."""
        dlg = ConfigFrame(self)
        self.root.wait_window(dlg.root)

    def _help_menu_items(self) -> list:
        return [
            MenuItem(f"On line help{txt.ELLIPSIS}", self._show_help),
            MenuItem(
                f"Data directory location{txt.ELLIPSIS}",
                self._show_data_directory,
            ),
            MenuItem(f"About{txt.ELLIPSIS}", self._show_about),
        ]

    def _show_help(self):
        """Open online help in default browser."""
        try:
            webbrowser.open(HELP_URI)
        except Exception as e:
            messagebox.showwarning(
                "Help Error", f"Could not open help page:\n{e}"
            )

    def _show_data_directory(self):
        dir = f"Data directory: {config.data_directory:<{SPACES}}"
        messagebox.showinfo(title="Data directory", message=dir)

    def _show_about(self):
        about = (
            f"{APP_TITLE}\nVersion: {__version__}\nAuthor: {AUTHOR:<{SPACES}}"
        )
        messagebox.showinfo(title=f"About {APP_TITLE}", message=about)

    def _dismiss(self, event: object = None):
        self.root.destroy()
