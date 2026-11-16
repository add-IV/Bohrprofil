import pytest
from PIL import Image

from src.bohrprofil import Bohrprofil, Layer
from src.config import Config
from src.draw import BohrprofilDrawer
from src.export import image_to_pdf_bytes, save_image
from src.utils import get_pixels_per_cm


@pytest.fixture
def profile() -> Bohrprofil:
    return Bohrprofil(
        title="Test",
        height=375.0,
        max_depth=3.5,
        layers=[
            Layer(1.0, "Humus", "Oberboden"),
            Layer(2.0, "Kies sandig", "Kies,\nsandig"),
            Layer(3.5, "Kalkstein", "Fels"),
        ],
    )


@pytest.fixture
def config() -> Config:
    return Config()


def test_render_has_expected_size(profile, config):
    image = BohrprofilDrawer().draw_profile(profile, config)
    assert isinstance(image, Image.Image)
    assert image.width == config.get_width()
    assert image.height == int(get_pixels_per_cm(3.5) + config.get_extra_height())


def test_render_draws_something(profile, config):
    image = BohrprofilDrawer().draw_profile(profile, config)
    # Not just a blank background.
    assert image.convert("L").getextrema()[0] < 128


def test_deeper_profile_renders_taller(profile, config):
    drawer = BohrprofilDrawer()
    short = drawer.draw_profile(profile, config).height
    profile.layers.append(Layer(6.0, "Ton", "Ton"))
    profile.update_max_depth()
    assert drawer.draw_profile(profile, config).height > short


def test_pdf_is_well_formed():
    pdf = image_to_pdf_bytes(Image.new("RGB", (300, 600), "white"))
    assert pdf.startswith(b"%PDF-1.4")
    assert pdf.rstrip().endswith(b"%%EOF")
    # startxref must point at the xref table.
    xref_pos = int(pdf.rsplit(b"startxref\n", 1)[1].split(b"\n", 1)[0])
    assert pdf[xref_pos:].startswith(b"xref")


def test_pdf_places_image_at_physical_size():
    # 300 px at 300 DPI = 1 inch = 72 pt
    pdf = image_to_pdf_bytes(Image.new("RGB", (300, 600), "white"))
    assert b"q 72.00 0 0 144.00" in pdf


@pytest.mark.parametrize("suffix", [".png", ".pdf", ".PDF"])
def test_save_image_picks_format_by_extension(tmp_path, suffix):
    file = tmp_path / f"out{suffix}"
    save_image(Image.new("RGB", (10, 10), "white"), str(file))
    head = file.read_bytes()[:8]
    if suffix.lower() == ".pdf":
        assert head.startswith(b"%PDF")
    else:
        assert head.startswith(b"\x89PNG")
