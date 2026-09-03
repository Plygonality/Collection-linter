"""Canon numbers. Always read Unit-canon. Never copy lengths into this package."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class HumanFigureLike(Protocol):
    asset_name: str
    standing_height: float
    eye_height: float
    shoulder_width: float


class CanonLike(Protocol):
    meters_per_grid: float
    deck_height: float
    airlock_diameter: float
    human_figure: HumanFigureLike


def load_canon(path: Path | str | None = None) -> CanonLike:
    from unit_canon.load import load

    return load(path)


def expected_sizes(canon: CanonLike | None = None) -> dict[str, float]:
    """Role → length the linter compares against. Reads the canon file."""
    canon = canon or load_canon()
    return {
        "grid": canon.meters_per_grid,
        "deck": canon.deck_height,
        "airlock": canon.airlock_diameter,
        "human_figure": canon.human_figure.standing_height,
    }
