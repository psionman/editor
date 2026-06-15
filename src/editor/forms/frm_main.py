
"""AppFrame for Editor launcher."""
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
from pathlib import Path
from editor.utilities import open_in_kate

from editor.constants import APP_TITLE, EDITOR, ICON_DIR
from psiutils.constants import PAD, Pad
from psiutils.buttons import ButtonFrame, IconButton
from psiutils.utilities import window_resize
from psiutils.treeview import sort_treeview, TreeColumn
from psiutils.menus import Menu, MenuItem

from editor.config import read_config
from editor.data_server import FileData, load_files
from editor.text import Text
from editor.utilities import get_path
from editor.forms.frm_edit_file import EditFrame

from editor.main_menu import MainMenu
# from editor.forms.frm

txt = Text()

TREE_COLUMNS = (
    TreeColumn('hint', 'Hint', 175, tk.W),
    TreeColumn('source_type', 'Source Type', 100, tk.W),
    TreeColumn('path', 'Path', 200, tk.W),
)

class AppFrame():
    """Create AppFrame for Editor launcher application."""
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.config = read_config()
        self.files = []
        self.file_to_edit = None
        self.file_hint = None

        # tk variables
        self.file_path = tk.StringVar()
        self.selected_file = tk.BooleanVar()
        self.source_type = tk.StringVar(value='file')


        # Trace
        self.file_path.trace_add('write', self._value_changed)

        self.context_menu = self._context_menu()
        self._show()
        self._populate_tree()

    def _show(self):
        # pylint: disable=no-member)
        root = self.root
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.title(APP_TITLE)

        root.bind('<Control-x>', self._dismiss)
        root.bind('<Configure>',
                  lambda event, arg=None: window_resize(self, __file__))

        main_menu = MainMenu(self)
        main_menu.create()

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
        frame.columnconfigure(0, weight=1)

        row = 0
        file_frame = self._file_frame(frame)
        file_frame.grid(row=row, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        row += 1
        frame.rowconfigure(row, weight=1)
        self.tree = self._tree_frame(frame)
        self.tree.grid(row=row, column=0, sticky=tk.NSEW)

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

        self.save_button = IconButton(
            frame, txt.APPEND, "append", self._append_file, True, icon_path=ICON_DIR
        )
        self.save_button.disable()
        self.save_button.grid(row=row, column=3, padx=PAD, pady=Pad.S)

        return frame

    def _tree_frame(self, master: tk.Frame) -> ttk.Treeview:
        """Return  a tree widget."""
        tree = ttk.Treeview(
            master,
            selectmode='browse',
            show='headings',
            )
        tree.bind('<<TreeviewSelect>>', self._tree_clicked)
        tree.bind('<Button-3>', self._show_context_menu)
        tree.bind('<Double-Button-1>', self._double_click)

        col_list = tuple(col.key for col in TREE_COLUMNS)
        tree['columns'] = col_list
        for col in TREE_COLUMNS:
            (col_key, col_text, col_width) = (col.key, col.heading, col.width)
            tree.heading(col_key, text=col_text,
                         command=lambda c=col_key:
                         sort_treeview(tree, c, False))
            tree.column(col_key, width=col_width, anchor=tk.W)
            tree.column(col.key, stretch=tk.NO)
        tree.column(col.key, stretch=tk.YES)  # stretch last column
        # tree.column(<'right-align-column-name'>, stretch=0, anchor=tk.E)
        #tree.configure(yscrollcommand=v_scroll.set)
        return tree

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
            frame.icon_button('edit', self._open_editor, True),
            frame.icon_button('close', self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _populate_tree(self) -> None:
        self.files = load_files()
        self.files.sort(key=lambda f: f.hint.lower())
        self.tree.delete(*self.tree.get_children())
        for file in self.files:
            values = (file.hint, file.source_type, file.short_path)
            self.tree.insert('', 'end', values=values)

    def _tree_clicked(self, *args) -> None:
        self.selected_item = self.tree.selection()
        if not self.selected_item:
            return

        item: tuple = self.tree.item(self.tree.selection(), 'values')
        self.file_data = FileData(item[0], item[1], item[2].replace('~', str(Path.home())))
        self.file_hint = item[0]
        self.file_to_edit = FileData(
            item[0], item[1], item[2].replace('~', str(Path.home())))

        self.button_frame.enable(True)
        self.context_menu.enable(True)

    def _double_click(self, *args) -> None:
        self.selected_item = self.tree.selection()
        if self.selected_item:
            item: tuple = self.tree.item(self.tree.selection(), 'values')
            self.file_to_edit = FileData(
                item[0], item[1], item[2].replace('~', str(Path.home())))
            self._open_editor()

    def _show_context_menu(self, event) -> None:
        self.context_menu.tk_popup(event.x_root, event.y_root)
        selected_item = self.tree.identify_row(event.y)
        self.tree.selection_set(selected_item)

    def _context_menu(self) -> tk.Menu:
        menu_items = [
            MenuItem('Open Editor', self._open_editor, dimmable=True),
            MenuItem('Edit item', self.edit_item, dimmable=True),
            MenuItem('Delete item', self._delete_item, dimmable=True),
        ]
        context_menu = Menu(self.root, menu_items)
        context_menu.enable(False)
        return context_menu

    def _value_changed(self, *args) -> bool:
        """
        Determine whether any configuration value has changed.
        """
        enable = (
            self.selected_file.get()
        )
        self.button_frame.enable(enable)

        save_enable = self.file_path.get() != ""
        self.save_button.enable(save_enable)

    def _get_path(self, *args) -> None:
        file_path = get_path(self.source_type.get())
        if file_path:
            self.file_path.set(file_path)
            self._value_changed()

    def _append_file(self, *args) -> None:
        dlg = simpledialog.askstring("Save File", "Enter hint")
        if dlg:
            # Save the file with the hint
            file_data = FileData(hint=dlg, source_type=self.source_type.get(), path=self.file_path.get())
            file_data.append()
            self._populate_tree()

    def _open_editor(self, *args) -> None:
        open_in_kate(self.file_to_edit.path)

    def edit_item(self, *args) -> None:
        dlg = EditFrame(self)
        self.root.wait_window(dlg.root)
        self._populate_tree()

    def _delete_item(self, *args) -> None:
        response = messagebox.askyesno("Delete Item", "Are you sure you want to delete this item?")
        if response:
            # Delete the item
            file_data = FileData(hint=self.file_hint, source_type=self.source_type.get(), path=self.file_path.get())
            file_data.delete()
            self._populate_tree()

        
    def _dismiss(self, *args) -> None:
        self.root.destroy()
