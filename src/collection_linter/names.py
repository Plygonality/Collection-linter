"""ZeroMap names: Category_Subtype_Variant."""

from __future__ import annotations

import re

# Three underscore-separated tokens. Category and Subtype are PascalCase.
# Variant is PascalCase or starts with a digit (Main, Canon, 01, 0).
ZEROMAP_RE = re.compile(
    r"^[A-Z][A-Za-z0-9]*_[A-Z][A-Za-z0-9]*_[A-Z0-9][A-Za-z0-9]*$"
)
_BLENDER_DUP = re.compile(r"\.\d{3}$")

ZEROMAP_EXAMPLES: dict[str, str] = {
    "human_figure": "Human_Figure_Canon",
    "airlock": "Airlock_Hatch_Main",
    "deck": "Deck_Floor_0",
    "grid": "Grid_Snap_Origin",
}


def name_stem(name: str) -> str:
    """Strip a Blender .001 duplicate suffix."""
    return _BLENDER_DUP.sub("", name.strip())


def is_zeromap_name(name: str, *, asset_name: str | None = None) -> bool:
    stem = name_stem(name)
    if not stem:
        return False
    if asset_name and stem == asset_name:
        return True
    return ZEROMAP_RE.fullmatch(stem) is not None
