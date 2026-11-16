"""A ttk frame with a vertical scrollbar.

Based on
https://web.archive.org/web/20170514022131id_/http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
"""

import tkinter as tk
from tkinter import ttk


class VerticalScrolledFrame(ttk.Frame):
    """Scrollable frame. Place child widgets inside ``self.interior``."""

    def __init__(self, parent, *args, **kw):
        super().__init__(parent, *args, **kw)

        vscrollbar = ttk.Scrollbar(self, orient="vertical")
        vscrollbar.pack(fill="y", side="right", expand=False)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        vscrollbar.configure(command=canvas.yview)

        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Frame inside the canvas which scrolls with it.
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor="nw")

        def _configure_interior(event):
            # Keep the scroll region and canvas width in sync with the inner frame.
            width, height = interior.winfo_reqwidth(), interior.winfo_reqheight()
            canvas.configure(scrollregion=f"0 0 {width} {height}")
            if width != canvas.winfo_width():
                canvas.configure(width=width)

        interior.bind("<Configure>", _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind("<Configure>", _configure_canvas)
