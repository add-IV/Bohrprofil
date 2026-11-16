import pytest

from src.config import Config
from src.utils import PIXEL_PER_CM, get_pixels_per_cm, get_textures, parse_depth


def test_pixels_per_cm_is_300_dpi():
    assert get_pixels_per_cm(2.54) == pytest.approx(300)
    assert PIXEL_PER_CM == pytest.approx(118.11, abs=0.01)


@pytest.mark.parametrize(
    ("text", "expected"),
    [("1.5", 1.5), ("1,5", 1.5), (" 3 ", 3.0), ("0", 0.0)],
)
def test_parse_depth(text, expected):
    assert parse_depth(text) == expected


@pytest.mark.parametrize("text", ["", "abc", "1,2,3"])
def test_parse_depth_rejects_invalid(text):
    with pytest.raises(ValueError):
        parse_depth(text)


@pytest.fixture
def config(tmp_path):
    ini = tmp_path / "config.ini"
    ini.write_text(
        "[Test]\n"
        "Länge = 2cm\n"
        "Positiv = 42\n"
        "Negativ = -5\n"
        "Mitvorzeichen = +7\n"
        "Text = black\n"
        "[Abstände und Längen]\n"
        "Links Abstand = 100\n",
        encoding="utf-8",
    )
    return Config(str(ini))


def test_get_converts_cm_to_pixels(config):
    assert config.get("Test", "Länge") == int(get_pixels_per_cm(2))


def test_get_parses_signed_integers(config):
    assert config.get("Test", "Positiv") == 42
    assert config.get("Test", "Negativ") == -5
    assert config.get("Test", "Mitvorzeichen") == 7


def test_get_returns_plain_strings(config):
    assert config.get("Test", "Text") == "black"


def test_file_overrides_defaults_and_keeps_the_rest(config):
    assert config.x1() == 100
    # Not in the file → built-in default (Maßstab Länge = 160)
    assert config.x2() == 100 + 160


def test_column_positions_are_increasing():
    config = Config()
    xs = [config.x1(), config.x2(), config.x3(), config.x4(),
          config.x5(), config.x6(), config.x7(), config.x8()]
    assert xs == sorted(xs)
    assert config.get_width() == config.x8()


def test_set_and_save_roundtrip(config, tmp_path):
    config.set("Farben", "Linienfarbe", "red")
    out = tmp_path / "out.ini"
    config.write_file(str(out))
    assert Config(str(out)).get("Farben", "Linienfarbe") == "red"


def test_textures_are_discovered():
    textures = get_textures()
    assert "Humus" in textures
    assert textures == sorted(textures)
