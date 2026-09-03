"""Minimal in-memory bpy stand-in for dump-script tests."""

from __future__ import annotations

from typing import Any


class FakeVector:
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __getitem__(self, index: int) -> float:
        return (self.x, self.y, self.z)[index]


class FakeCollection:
    def __init__(self, name: str) -> None:
        self.name = name


class FakeObject:
    def __init__(
        self,
        name: str,
        *,
        dimensions: FakeVector,
        location: FakeVector,
        collections: tuple[FakeCollection, ...] = (),
        properties: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.dimensions = dimensions
        self.location = location
        self.users_collection = collections
        self._properties = dict(properties or {})

    def get(self, key: str, default: Any = None) -> Any:
        return self._properties.get(key, default)


class FakeData:
    def __init__(self, objects: list[FakeObject]) -> None:
        self.objects = objects


class FakeBpy:
    def __init__(self, objects: list[FakeObject]) -> None:
        self.data = FakeData(objects)
