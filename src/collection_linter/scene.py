"""Scene dump. JSON in, frozen objects out. Blender is optional."""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from collection_linter.roles import ROLES, Role

FORMAT = "collection-linter"
FORMAT_VERSION = 1


class SceneError(ValueError):
    """The scene dump is missing, not JSON, or does not match the contract."""


@dataclass(frozen=True, slots=True)
class SceneObject:
    name: str
    collection: str
    dimensions: tuple[float, float, float]
    location: tuple[float, float, float]
    role: Role | None = None
    eye_height: float | None = None
    shoulder_width: float | None = None

    def standing_height(self) -> float:
        return self.dimensions[2]

    def width(self) -> float:
        if self.shoulder_width is not None:
            return self.shoulder_width
        return abs(self.dimensions[0])

    def diameter_xy(self) -> float:
        width, depth, _height = self.dimensions
        return (abs(width) + abs(depth)) / 2.0


@dataclass(frozen=True, slots=True)
class Scene:
    objects: tuple[SceneObject, ...] = ()

    def __iter__(self) -> Iterator[SceneObject]:
        return iter(self.objects)

    def __len__(self) -> int:
        return len(self.objects)

    @classmethod
    def from_dicts(cls, rows: Iterable[dict[str, Any]]) -> Scene:
        return cls(objects=tuple(_object_from_dict(row, index) for index, row in enumerate(rows)))


def load_scene(source: Path | str | dict[str, Any] | list[Any]) -> Scene:
    """Load a scene from a path, JSON text is not accepted: pass a path or a parsed object."""
    if isinstance(source, (str, Path)):
        path = Path(source)
        try:
            raw_text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise SceneError(f"Cannot read scene file: {path}") from exc
        try:
            data: Any = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise SceneError(f"Scene file is not valid JSON: {path}") from exc
        return scene_from_payload(data, where=str(path))
    return scene_from_payload(source)


def scene_from_payload(data: Any, *, where: str = "") -> Scene:
    suffix = f" ({where})" if where else ""
    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict):
        if "objects" not in data:
            raise SceneError(f"Scene JSON must have an 'objects' array{suffix}.")
        rows = data["objects"]
    else:
        raise SceneError(f"Scene JSON must be an object or an array{suffix}.")
    if not isinstance(rows, list):
        raise SceneError(f"Scene 'objects' must be an array{suffix}.")
    typed: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise SceneError(f"Scene object {index} must be an object{suffix}.")
        typed.append(row)
    return Scene.from_dicts(typed)


def _object_from_dict(row: dict[str, Any], index: int) -> SceneObject:
    if "name" not in row or not str(row["name"]).strip():
        raise SceneError(f"Scene object {index} is missing a name.")
    raw_role = row.get("role")
    role: Role | None
    if raw_role in ROLES:
        role = raw_role
    elif raw_role in (None, ""):
        role = None
    else:
        role = None
    return SceneObject(
        name=str(row["name"]),
        collection=str(row.get("collection", "")),
        dimensions=_vec3(row.get("dimensions", (0.0, 0.0, 0.0)), f"object {index} dimensions"),
        location=_vec3(row.get("location", (0.0, 0.0, 0.0)), f"object {index} location"),
        role=role,
        eye_height=_optional_float(row.get("eye_height"), f"object {index} eye_height"),
        shoulder_width=_optional_float(row.get("shoulder_width"), f"object {index} shoulder_width"),
    )


def _vec3(value: object, label: str) -> tuple[float, float, float]:
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
        raise SceneError(f"Expected 3 numbers for {label}, got {value!r}.")
    seq = tuple(value)
    if len(seq) != 3:
        raise SceneError(f"Expected 3 numbers for {label}, got {value!r}.")
    try:
        return (float(seq[0]), float(seq[1]), float(seq[2]))
    except (TypeError, ValueError) as exc:
        raise SceneError(f"Expected 3 numbers for {label}, got {value!r}.") from exc


def _optional_float(value: object, label: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SceneError(f"{label} must be a number, got {value!r}.")
    return float(value)
