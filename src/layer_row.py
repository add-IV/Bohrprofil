"""One editable row (depth, texture, description) in the layer list."""

import tkinter as tk
from os import path
from tkinter import ttk

from .texture_hover_preview import TextureHoverPreview
from .utils import get_external_dir, get_textures


class LayerRow:
    """The input widgets for a single layer, gridded into ``master`` at ``rownumber``."""

    def __init__(self, master, rownumber: int, change_callback=None):
        self.end_depth = tk.StringVar()
        self.end_depth_entry = ttk.Entry(master, textvariable=self.end_depth, width=10)
        self.end_depth_entry.bind("<KeyRelease>", change_callback)

        self.texture = tk.StringVar()
        self.texture_combobox = ttk.Combobox(
            master, state="readonly", textvariable=self.texture
        )
        self.texture_combobox.bind("<<ComboboxSelected>>", change_callback)
        self.combobox_set_textures()
        TextureHoverPreview(self.texture_combobox, path.join(get_external_dir(), "patterns"))

        self.description_text = tk.Text(master, width=38, height=4)
        self.description_text.bind("<KeyRelease>", change_callback)

        self.grid(rownumber)

    def grid(self, row: int) -> None:
        self.end_depth_entry.grid(row=row, column=0, sticky="nw")
        self.texture_combobox.grid(row=row, column=1, sticky="nw")
        self.description_text.grid(row=row, column=2, sticky="nw")

    def forget(self) -> None:
        self.end_depth_entry.grid_forget()
        self.texture_combobox.grid_forget()
        self.description_text.grid_forget()

    def set_all(self, end_depth: str, description: str) -> None:
        self.end_depth.set(end_depth)
        self.description_text.delete("1.0", tk.END)
        self.description_text.insert("1.0", description)

    def get_description(self) -> str:
        # Text widgets always append a trailing newline; drop it.
        return self.description_text.get("1.0", "end-1c")

    def combobox_set_textures(self) -> None:
        self.texture_combobox["values"] = get_textures()
        if len(self.texture_combobox["values"]) > 0:
            self.texture_combobox.current(0)
