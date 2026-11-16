"""Main window: inputs on the left, live-rendered profile preview on the right."""

import os
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename

from PIL import ImageTk

from .bohrprofil import Bohrprofil, Layer
from .config import Config
from .config_frame import ConfigFrame
from .draw import BohrprofilDrawer
from .export import save_image
from .layer_list import LayerList
from .utils import get_pixels_per_cm, parse_depth

if sys.platform == "win32":
    import win32api

DEFAULT_TITLE = "Bohrprofil"
DEFAULT_HEIGHT = "375"
JSON_FILETYPES = [("JSON-Dateien", "*.json"), ("Alle Dateien", "*")]


class MainFrame(ttk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.create_menubar(master)
        self.drawer = BohrprofilDrawer()
        self.app_config = Config()

        self.grid(row=0, column=0, sticky="nwes", padx=8, pady=4)

        self.info_frame = ttk.Frame(self)
        self.info_frame.grid(row=0, column=0, sticky="nw")

        ttk.Label(self.info_frame, text="Titel:").grid(row=0, column=0, sticky="nw")
        self.title_name = tk.StringVar(value=DEFAULT_TITLE)
        self.title_entry = ttk.Entry(self.info_frame, textvariable=self.title_name)
        self.title_entry.grid(row=1, column=0, sticky="nw")

        ttk.Label(self.info_frame, text="Höhe:").grid(row=0, column=1, sticky="nw")
        self.height_name = tk.StringVar(value=DEFAULT_HEIGHT)
        self.height_entry = ttk.Entry(self.info_frame, textvariable=self.height_name)
        self.height_entry.grid(row=1, column=1, sticky="nw")

        self.add_layer_button = ttk.Button(self.info_frame, text="Schicht hinzufügen")
        self.add_layer_button.grid(row=2, column=0, sticky="nw")

        self.remove_layer_button = ttk.Button(self.info_frame, text="Schicht entfernen")
        self.remove_layer_button.grid(row=2, column=1, sticky="nw")

        self.layer_list = LayerList(self, self.redraw)
        self.layer_list.grid(row=2, column=0, sticky="nwes")
        self.layer_list.add_one_layer(False)

        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.grid(row=0, column=2, rowspan=3, sticky="nws")

        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=get_pixels_per_cm(7),
            height=get_pixels_per_cm(2),
            background="white",
        )
        self.canvas.grid(row=0, column=0, sticky="nw")

        self.scrollbar = ttk.Scrollbar(
            self.canvas_frame, orient="vertical", command=self.canvas.yview
        )
        self.scrollbar.grid(row=0, column=2, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        self.add_layer_button["command"] = self.layer_list.add_one_layer
        self.remove_layer_button["command"] = self.layer_list.remove_one_layer
        self.title_entry.bind("<KeyRelease>", self.redraw)
        self.height_entry.bind("<KeyRelease>", self.redraw)

        self.after(100, self.redraw)

    # ------------------------------------------------------------------
    # Model / rendering
    # ------------------------------------------------------------------

    def _collect_bohrprofil(self) -> Bohrprofil:
        """Build the data model from the current inputs. Raises ValueError on bad numbers."""
        self.layer_list.sort_layers()
        layers = [
            Layer(parse_depth(row.end_depth.get()), row.texture.get(), row.get_description())
            for row in self.layer_list.layers
        ]
        height_text = self.height_name.get().strip()
        height = parse_depth(height_text) if height_text else 0.0
        bohrprofil = Bohrprofil(self.title_name.get(), height, 0.0, layers)
        bohrprofil.sort_layers()
        bohrprofil.update_max_depth()
        return bohrprofil

    def redraw(self, event=None) -> None:
        try:
            self.bohrprofil = self._collect_bohrprofil()
        except ValueError:
            # Incomplete input while typing (e.g. empty depth) — keep the last preview.
            return
        self.layer_list.set_max_depth(self.bohrprofil.max_depth)

        width = self.app_config.get_width()
        height = (
            int(get_pixels_per_cm(self.bohrprofil.max_depth))
            + self.app_config.get_extra_height()
        )
        self.canvas.delete("all")
        self.canvas.configure(
            width=width,
            height=min(self.canvas_frame.winfo_height(), height),
            background="white",
            scrollregion=(0, 0, width, height),
        )
        self.image = self.drawer.draw_profile(self.bohrprofil, self.app_config)
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

    # ------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------

    def create_menubar(self, root: tk.Tk) -> None:
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Neu", command=self._new)
        filemenu.add_command(label="Öffnen", command=self._open)
        filemenu.add_command(label="Speichern", command=self._save)
        filemenu.add_separator()
        filemenu.add_command(label="Exportieren", command=self._export)
        filemenu.add_command(label="Drucken", command=self._print)
        filemenu.add_separator()
        filemenu.add_command(label="Beenden", command=root.quit)
        optionmenu = tk.Menu(menubar, tearoff=0)
        optionmenu.add_command(label="Konfigurieren", command=self.open_config_toplevel)
        menubar.add_cascade(label="Datei", menu=filemenu)
        menubar.add_cascade(label="Optionen", menu=optionmenu)
        root.configure(menu=menubar)

    def _new(self) -> None:
        self.title_name.set(DEFAULT_TITLE)
        self.height_name.set(DEFAULT_HEIGHT)
        self.layer_list.clear()
        self.redraw()

    def _open(self) -> None:
        filename = askopenfilename(filetypes=JSON_FILETYPES)
        if not filename:
            return
        try:
            bohrprofil = Bohrprofil.load(filename)
        except (OSError, ValueError, KeyError) as e:
            messagebox.showerror(
                "Öffnen fehlgeschlagen", f"Datei konnte nicht gelesen werden:\n{e}"
            )
            return
        self.title_name.set(bohrprofil.title)
        self.height_name.set(f"{bohrprofil.height:g}")
        self.layer_list.clear()
        for i, layer in enumerate(bohrprofil.layers):
            if i > 0:
                self.layer_list.add_one_layer(False)
            row = self.layer_list.layers[-1]
            row.set_all(f"{layer.end_depth:g}", layer.description)
            row.texture.set(layer.texture)
        self.redraw()

    def _save(self) -> None:
        filename = asksaveasfilename(defaultextension=".json", filetypes=JSON_FILETYPES)
        if not filename:
            return
        self.bohrprofil.save(filename)

    def _export(self) -> None:
        filename = asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF-Dateien", "*.pdf"), ("PNG-Dateien", "*.png"), ("Alle Dateien", "*")],
        )
        if not filename:
            return
        save_image(self.image, filename)

    def _print(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            filename = tmp.name
        save_image(self.image, filename)

        if sys.platform == "win32":
            try:
                win32api.ShellExecute(0, "print", filename, None, ".", 0)
            except Exception as e1:
                try:
                    os.startfile(filename, "print")
                except Exception as e2:
                    try:
                        os.startfile(filename)
                    except Exception as e3:
                        errorinfo = (
                            f"win32api:\n{e1}\nos.startfile(print):\n{e2}\nos.startfile:\n{e3}"
                        )
                        messagebox.showerror("Drucken fehlgeschlagen", errorinfo)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            try:
                subprocess.run([opener, filename], check=True)
            except Exception as e:
                messagebox.showerror(
                    "Drucken fehlgeschlagen", f"Fehler beim Öffnen der Datei:\n{e}"
                )

    # ------------------------------------------------------------------
    # Configuration dialog
    # ------------------------------------------------------------------

    def open_config_toplevel(self) -> None:
        if hasattr(self, "config_toplevel"):
            self.config_toplevel.destroy()
        self.config_toplevel = tk.Toplevel(self)
        self.config_toplevel.title("Konfiguration")
        self.config_toplevel.minsize(200, 600)
        self.config_toplevel.resizable(False, False)
        self.config_toplevel.columnconfigure(0, weight=1)
        self.config_toplevel.rowconfigure(0, weight=1)
        self.config_frame = ConfigFrame(
            self.config_toplevel, self.app_config, self.redraw, self.reset_config
        )
        self.config_toplevel.transient(self)
        self.config_toplevel.wait_window(self.config_toplevel)

    def reset_config(self) -> None:
        """Discard unsaved edits by re-reading config.ini, then reopen the dialog."""
        self.app_config = Config()
        self.redraw()
        self.open_config_toplevel()
