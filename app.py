"""Entry point for the Bohrprofil desktop application."""

import sys
import tkinter as tk
from os import path

from src.main_frame import MainFrame
from src.utils import get_bundle_dir

APP_USER_MODEL_ID = "addiv.bohrprofil.1.0"


def main() -> None:
    if sys.platform == "win32":
        # Give the app its own taskbar identity/icon instead of python.exe's.
        from ctypes import windll

        windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)

    root = tk.Tk()
    root.title("Bohrprofil")
    root.minsize(1600, 800)
    root.geometry("1600x800")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    MainFrame(root)

    if sys.platform == "win32":
        if getattr(sys, "frozen", False):
            root.iconbitmap(sys.executable)
        else:
            root.iconbitmap(path.join(get_bundle_dir(), "mu.ico"))

    root.mainloop()


if __name__ == "__main__":
    main()
