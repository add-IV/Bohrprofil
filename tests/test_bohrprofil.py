import json

from src.bohrprofil import Bohrprofil, Layer


def make_profile() -> Bohrprofil:
    return Bohrprofil(
        title="Bohrung B1",
        height=412.5,
        max_depth=0.0,
        layers=[
            Layer(2.6, "Kies sandig", "Kies"),
            Layer(0.3, "Humus", "Oberboden"),
            Layer(1.4, "Löß", "Löß, kalkhaltig"),
        ],
    )


def test_sort_layers_orders_by_depth():
    bp = make_profile()
    bp.sort_layers()
    assert [layer.end_depth for layer in bp.layers] == [0.3, 1.4, 2.6]


def test_update_max_depth_uses_deepest_layer():
    bp = make_profile()
    bp.sort_layers()
    bp.update_max_depth()
    assert bp.max_depth == 2.6


def test_update_max_depth_without_layers():
    bp = Bohrprofil("leer", 0.0, 5.0, [])
    bp.update_max_depth()
    assert bp.max_depth == 0.0


def test_marshal_unmarshal_roundtrip():
    bp = make_profile()
    assert Bohrprofil.unmarshal(bp.marshal()) == bp


def test_unmarshal_accepts_numeric_strings():
    # Older save files stored the height as a string.
    data = {
        "title": "Alt",
        "height": "375",
        "max_depth": 1.0,
        "layers": [{"end_depth": 1.0, "texture": "Asphalt", "description": "x"}],
    }
    bp = Bohrprofil.unmarshal(data)
    assert bp.height == 375.0
    assert bp.layers[0].end_depth == 1.0


def test_save_load_roundtrip_preserves_umlauts(tmp_path):
    bp = make_profile()
    file = tmp_path / "profil.json"
    bp.save(str(file))

    raw = file.read_text(encoding="utf-8")
    assert "Löß" in raw  # written as UTF-8, not \u escapes
    assert json.loads(raw)["title"] == "Bohrung B1"

    assert Bohrprofil.load(str(file)) == bp


def test_example_file_loads():
    bp = Bohrprofil.load("examples/beispiel.json")
    assert bp.layers
    assert bp.max_depth == bp.layers[-1].end_depth
