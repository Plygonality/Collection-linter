"""Named checks. Each violation carries a fix string."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Check:
    name: str
    code: str
    description: str
    fix: str


HUMAN_STANDING_HEIGHT = Check(
    name="human_standing_height",
    code="HUMAN_HEIGHT",
    description="Figure standing height equals canon.human_figure.standing_height.",
    fix=(
        "Set {object_name} Z dimension to {expected} m "
        "(unit_canon.human_figure.standing_height)."
    ),
)

EYE_BELOW_STANDING = Check(
    name="eye_below_standing",
    code="EYE_HEIGHT",
    description="Eye height is strictly below standing height.",
    fix=(
        "Lower the eye on {object_name} below standing height {expected} m "
        "(eye is {actual} m)."
    ),
)

AIRLOCK_DIAMETER = Check(
    name="airlock_diameter",
    code="AIRLOCK_DIAMETER",
    description="Airlock XY diameter equals canon.airlock_diameter (1.0 m on the default file).",
    fix="Set {object_name} X and Y to {expected} m (unit_canon.airlock_diameter).",
)

AIRLOCK_SHOULDER = Check(
    name="airlock_shoulder_clearance",
    code="AIRLOCK_SHOULDER",
    description="Figure shoulder width is strictly less than the airlock diameter.",
    fix=(
        "Narrow {object_name} shoulders to under {expected} m "
        "(unit_canon.airlock_diameter), or widen the airlock. Shoulders are {actual} m."
    ),
)

DECK_GRID_CELLS = Check(
    name="deck_grid_cells",
    code="DECK_SPACING",
    description="Deck Z is an integer number of grid cells (n × meters_per_grid).",
    fix=(
        "Move {object_name} Z to an integer multiple of {step} m "
        "(unit_canon.meters_per_grid). Now {actual} m."
    ),
)

LOCATION_GRID_SNAP = Check(
    name="location_grid_snap",
    code="GRID_SNAP",
    description="Locations snap to meters_per_grid on every axis.",
    fix=(
        "Snap {object_name} {axis} to a multiple of {step} m "
        "(unit_canon.meters_per_grid). Now {actual} m."
    ),
)

ZEROMAP_NAME = Check(
    name="zeromap_name",
    code="ZEROMAP_NAME",
    description="Names follow ZeroMap Category_Subtype_Variant.",
    fix=(
        "Rename {object_name} to Category_Subtype_Variant "
        "(three PascalCase tokens, e.g. {example})."
    ),
)

REQUIRED_ROLE = Check(
    name="required_role",
    code="MISSING_ROLE",
    description="The scene includes one object for every canon role.",
    fix=(
        "Add an object with role {role}: set custom property unit_canon.role, "
        "or name it {role}_* / {example}."
    ),
)

CHECKS: tuple[Check, ...] = (
    HUMAN_STANDING_HEIGHT,
    EYE_BELOW_STANDING,
    AIRLOCK_DIAMETER,
    AIRLOCK_SHOULDER,
    DECK_GRID_CELLS,
    LOCATION_GRID_SNAP,
    ZEROMAP_NAME,
    REQUIRED_ROLE,
)

CHECKS_BY_NAME: dict[str, Check] = {item.name: item for item in CHECKS}
CHECKS_BY_CODE: dict[str, Check] = {item.code: item for item in CHECKS}


def format_fix(check: Check, **kwargs: object) -> str:
    values = {
        "object_name": "",
        "expected": "",
        "actual": "",
        "axis": "",
        "role": "",
        "step": "",
        "example": "Airlock_Hatch_Main",
    }
    for key, value in kwargs.items():
        if value is not None:
            values[key] = value
    return check.fix.format(**values)
