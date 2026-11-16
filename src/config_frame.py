"""Dialog for live-editing the layout configuration."""

from collections.abc import Callable
from tkinter import ttk

from .config import Config

SECTIONS = (
    "Abstände und Längen",
    "Farben",
    "Schriften",
    "Schriften Abstände",
    "Linien",
)


class ConfigFrame(ttk.Frame):
    def __init__(
        self,
        master,
        app_config: Config,
        on_change: Callable[[], None],
        on_reset: Callable[[], None],
    ):
        super().__init__(master)
        self.app_config = app_config
        self._on_change = on_change
        self._on_reset = on_reset

        self.grid(row=0, column=1, sticky="nwes", padx=8, pady=4)

        self.current_row = 0

        for section in SECTIONS:
            self.create_section_title(section)
            self.create_config_section(section, self.app_config.get_section(section))
            self.create_separator()

        self.reset_button = ttk.Button(self, text="Zurücksetzen", command=self._on_reset)
        self.reset_button.grid(row=self.current_row, column=0, sticky="nw")

        self.save_button = ttk.Button(self, text="Speichern", command=self.save)
        self.save_button.grid(row=self.current_row, column=1, sticky="nw")

    def save(self) -> None:
        self.app_config.save()

    def create_section_title(self, title: str) -> None:
        label = ttk.Label(self, text=title)
        label.grid(row=self.current_row, column=0, sticky="nw")
        self.current_row += 1

    def create_separator(self) -> None:
        separator = ttk.Separator(self, orient="horizontal")
        separator.grid(row=self.current_row, column=0, sticky="we")
        self.current_row += 1

    def create_config_section(self, section: str, options) -> None:
        for key, value in options.items():
            self.create_config_option(section, key, value)

    def create_config_option(self, section: str, key: str, value: str) -> None:
        label = ttk.Label(self, text=f"{key}:")
        label.grid(row=self.current_row, column=0, sticky="nw")

        entry = ttk.Entry(self)
        entry.grid(row=self.current_row, column=1, sticky="nwe")
        entry.insert(0, value)

        self.current_row += 1

        entry.bind("<KeyRelease>", lambda e: self.set_value(section, key, entry.get()))

    def set_value(self, section: str, key: str, value: str) -> None:
        self.app_config.set(section, key, value)
        self._on_change()
