"""Roles the linter knows. Assigned from an explicit field, a name, or a custom property."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from collection_linter.names import name_stem

if TYPE_CHECKING:
    from collection_linter.canon import CanonLike
    from collection_linter.scene import SceneObject

Role = Literal["human_figure", "airlock", "deck", "grid"]
ROLES: tuple[Role, ...] = ("human_figure", "airlock", "deck", "grid")

ROLE_PROP = "unit_canon.role"
EYE_PROP = "unit_canon.eye_height"
SHOULDER_PROP = "unit_canon.shoulder_width"

# ZeroMap Category token → role. First segment of Category_Subtype_Variant.
_CATEGORY_ROLE: dict[str, Role] = {
    "human": "human_figure",
    "humanfigure": "human_figure",
    "airlock": "airlock",
    "deck": "deck",
    "grid": "grid",
}

ROLE_DOCS: dict[Role, str] = {
    "human_figure": (
        "Scale mannequin. Standing height is the Z dimension; eye and shoulder "
        "must fit the canon figure. Name HumanFigure, human_figure_*, or Human_*."
    ),
    "airlock": (
        "Circular hatch / tube. XY diameter is canon.airlock_diameter (1.0 m). "
        "The figure's shoulders must pass through it. Name airlock_* or Airlock_*."
    ),
    "deck": (
        "Floor plate. Z location is an integer number of grid cells "
        "(n × meters_per_grid). Name deck_* or Deck_*."
    ),
    "grid": (
        "Snap reference. Location XYZ snaps to meters_per_grid. "
        "Name grid_* or Grid_*."
    ),
}


def infer_role(obj: SceneObject, canon: CanonLike) -> Role | None:
    """Resolve a role from the field, the canon asset name, or the object name."""
    if obj.role in ROLES:
        return obj.role
    stem = name_stem(obj.name)
    if stem == canon.human_figure.asset_name:
        return "human_figure"
    lowered = stem.lower()
    for role in ROLES:
        if lowered == role or lowered.startswith(f"{role}_"):
            return role
    category = stem.split("_", 1)[0].lower()
    return _CATEGORY_ROLE.get(category)
