"""Scrollable list of LayerRow widgets."""

from tkinter import ttk

from .layer_row import LayerRow
from .utils import parse_depth
from .vertical_scrolled_frame import VerticalScrolledFrame


class LayerList(VerticalScrolledFrame):
    def __init__(self, parent, change_callback=None):
        super().__init__(parent)
        self.max_depth = 0.0
        self.layers: list[LayerRow] = []
        self.change_callback = change_callback

        for column, text in enumerate(("Endtiefe", "Symbol", "Beschreibung")):
            ttk.Label(self.interior, text=text).grid(row=0, column=column, sticky="nw")

    def add_one_layer(self, do_callback: bool = True) -> None:
        layer = LayerRow(self.interior, len(self.layers) + 1, self.change_callback)
        self.layers.append(layer)
        layer.set_all(f"{int(self.max_depth) + 1}", f"Beschreibung {len(self.layers)}")
        if do_callback:
            self.change_callback()

    def remove_one_layer(self, do_callback: bool = True) -> None:
        if not self.layers:
            return
        self.layers.pop().forget()

        if self.layers:
            try:
                self.set_max_depth(parse_depth(self.layers[-1].end_depth.get()))
            except ValueError:
                pass
        else:
            self.set_max_depth(0.0)
            self.add_one_layer(False)

        if do_callback:
            self.change_callback()

    def sort_layers(self) -> None:
        """Sort rows by depth and re-grid them. Raises ValueError on unparsable depths."""
        self.layers.sort(key=lambda row: parse_depth(row.end_depth.get()))
        for i, layer in enumerate(self.layers):
            layer.grid(i + 1)

    def clear(self) -> None:
        for _ in range(len(self.layers)):
            self.remove_one_layer(do_callback=False)

    def set_max_depth(self, max_depth: float) -> None:
        self.max_depth = max_depth
