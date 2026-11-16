"""Unit conversion and path helpers shared across the app."""

import sys
from glob import glob
from os import path

basedir = path.dirname(__file__)

DPI = 300
PIXEL_PER_MM = DPI / 25.4
PIXEL_PER_CM = PIXEL_PER_MM * 10


def get_pixels_per_cm(cm: float) -> float:
    """Convert centimetres to pixels at the render resolution (300 DPI)."""
    return cm * PIXEL_PER_CM


def parse_depth(text: str) -> float:
    """Parse a user-entered depth, accepting a German decimal comma.

    Raises ValueError for empty or non-numeric input.
    """
    return float(text.strip().replace(",", "."))


# Both helpers currently resolve to the same directory (Nuitka places every
# file flat next to the exe). They are kept separate so that read-only bundled
# assets and user-editable files can be relocated independently.


def get_external_dir() -> str:
    """Directory for user-editable files (patterns, config.ini) — next to the exe when frozen."""
    if getattr(sys, "frozen", False):
        return path.dirname(sys.executable)
    return path.join(basedir, "..")


def get_bundle_dir() -> str:
    """Directory for read-only bundled files (font, icon) — next to the exe when frozen."""
    if getattr(sys, "frozen", False):
        return path.dirname(sys.executable)
    return path.join(basedir, "..")


def get_textures() -> list[str]:
    """Names of all available texture patterns (PNG files in ``patterns/``), sorted."""
    patterns_dir = path.join(get_external_dir(), "patterns")
    return sorted(path.splitext(file)[0] for file in glob("*.png", root_dir=patterns_dir))
