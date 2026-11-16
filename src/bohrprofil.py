"""Data model for a borehole profile and its JSON (de)serialization."""

import json
from dataclasses import dataclass, field


@dataclass
class Layer:
    """A single soil/rock layer, reaching from the previous layer down to ``end_depth``."""

    end_depth: float
    texture: str
    description: str


@dataclass
class Bohrprofil:
    title: str
    height: float
    max_depth: float
    layers: list[Layer] = field(default_factory=list)

    def sort_layers(self) -> None:
        self.layers.sort(key=lambda layer: layer.end_depth)

    def update_max_depth(self) -> None:
        self.max_depth = self.layers[-1].end_depth if self.layers else 0.0

    def marshal(self) -> dict:
        return {
            "title": self.title,
            "height": self.height,
            "max_depth": self.max_depth,
            "layers": [
                {
                    "end_depth": layer.end_depth,
                    "texture": layer.texture,
                    "description": layer.description,
                }
                for layer in self.layers
            ],
        }

    @staticmethod
    def unmarshal(data: dict) -> "Bohrprofil":
        return Bohrprofil(
            data["title"],
            float(data["height"]),
            float(data["max_depth"]),
            [
                Layer(float(layer["end_depth"]), layer["texture"], layer["description"])
                for layer in data["layers"]
            ],
        )

    def save(self, filename: str) -> None:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.marshal(), f, ensure_ascii=False, indent=2)

    @staticmethod
    def load(filename: str) -> "Bohrprofil":
        with open(filename, encoding="utf-8") as f:
            return Bohrprofil.unmarshal(json.load(f))
