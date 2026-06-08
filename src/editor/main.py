"""
 A tkinter application for Editor launcher.
"""

import sys
import argparse
import tkinter as tk
from tkinter import messagebox

from psiutils.widgets import get_styles
from psiutils.utilities import display_icon
from psiutils.icecream_init import ic_init

from editor.constants import ICON_FILE, APP_TITLE
from editor.module_caller import ModuleCaller

from forms.frm_main import AppFrame

from editor import logger

ic_init()


def main() -> None:
    parser = argparse.ArgumentParser(description="Editor launcher")
    parser.add_argument(
        "module", nargs="?", default=None, help="Module to load")
    args = parser.parse_args()

    root = tk.Tk()
    root.title(APP_TITLE)
    display_icon(root, ICON_FILE, ignore_error=True)

    root.protocol("WM_DELETE_WINDOW", root.destroy)

    get_styles()

    if args.module:
        try:
            dlg = ModuleCaller(root, args.module)
            if dlg.invalid:
                logger.error(f"Invalid module", module=args.module)
                AppFrame(root)
        except Exception as e:
            logger.error(f"Failed to load module '{args.module}'", error=e)
            AppFrame(root)
    else:
        AppFrame(root)

    root.mainloop()


if __name__ == '__main__':
    main()
