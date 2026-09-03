"""Rule engine. JSON scenes in, named violations out. No bpy."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from collection_linter.canon import CanonLike, expected_sizes, load_canon
from collection_linter.checks import (
    AIRLOCK_DIAMETER,
    AIRLOCK_SHOULDER,
    DECK_GRID_CELLS,
    EYE_BELOW_STANDING,
    HUMAN_STANDING_HEIGHT,
    LOCATION_GRID_SNAP,
    REQUIRED_ROLE,
    ZEROMAP_NAME,
    Check,
    format_fix,
)
from collection_linter.names import ZEROMAP_EXAMPLES, is_zeromap_name
from collection_linter.roles import ROLES, Role, infer_role
from collection_linter.scene import Scene, SceneObject

DEFAULT_TOLERANCE_M = 0.01


@dataclass(frozen=True, slots=True)
class Violation:
    check: str
    code: str
    message: str
    fix: str
    object_name: str | None = None
    expected: float | None = None
    actual: float | None = None
    axis: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "check": self.check,
            "code": self.code,
            "message": self.message,
            "fix": self.fix,
            "object_name": self.object_name,
            "expected": self.expected,
            "actual": self.actual,
            "axis": self.axis,
        }


@dataclass(frozen=True, slots=True)
class LintResult:
    violations: tuple[Violation, ...]
    checked: int

    @property
    def ok(self) -> bool:
        return not self.violations

    def by_code(self, code: str) -> tuple[Violation, ...]:
        return tuple(item for item in self.violations if item.code == code)

    def by_check(self, name: str) -> tuple[Violation, ...]:
        return tuple(item for item in self.violations if item.check == name)

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "checked": self.checked,
            "violations": [item.to_dict() for item in self.violations],
        }


def lint(
    scene: Scene | Sequence[SceneObject],
    canon: CanonLike | None = None,
    *,
    tolerance_m: float = DEFAULT_TOLERANCE_M,
    require_roles: bool = True,
) -> LintResult:
    """Lint a scene against Unit-canon. Each hit is a named check with a fix string."""
    canon = canon or load_canon()
    objects = scene.objects if isinstance(scene, Scene) else tuple(scene)
    sizes = expected_sizes(canon)
    violations: list[Violation] = []

    seen: set[Role] = set()
    checked = 0
    resolved: list[tuple[SceneObject, Role]] = []
    for obj in objects:
        role = infer_role(obj, canon)
        if role is None:
            continue
        seen.add(role)
        checked += 1
        resolved.append((obj, role))
        violations.extend(_lint_object(obj, role, canon, sizes, tolerance_m))

    if require_roles:
        for role in ROLES:
            if role not in seen:
                example = ZEROMAP_EXAMPLES[role]
                violations.append(
                    _hit(
                        REQUIRED_ROLE,
                        message=(
                            f"No object with role {role!r}. "
                            "Collection-linter expects a scale reference "
                            "for every canon measure."
                        ),
                        role=role,
                        example=example,
                    )
                )

    figures = [(obj, role) for obj, role in resolved if role == "human_figure"]
    airlocks = [(obj, role) for obj, role in resolved if role == "airlock"]
    for obj, _role in figures:
        violations.extend(_shoulder_clearance(obj, airlocks, canon))

    return LintResult(violations=tuple(violations), checked=checked)


def _lint_object(
    obj: SceneObject,
    role: Role,
    canon: CanonLike,
    sizes: dict[str, float],
    tolerance_m: float,
) -> list[Violation]:
    hits: list[Violation] = []
    if not is_zeromap_name(obj.name, asset_name=canon.human_figure.asset_name):
        example = ZEROMAP_EXAMPLES[role]
        hits.append(
            _hit(
                ZEROMAP_NAME,
                object_name=obj.name,
                message=(
                    f"{obj.name} does not follow ZeroMap Category_Subtype_Variant."
                ),
                example=example,
            )
        )

    if role == "human_figure":
        hits.extend(
            _close(
                obj,
                HUMAN_STANDING_HEIGHT,
                sizes["human_figure"],
                obj.standing_height(),
                tolerance_m,
                f"{obj.name} standing height is {{actual}} m, "
                f"canon expects {{expected}} m.",
            )
        )
        standing = obj.standing_height()
        eye = obj.eye_height if obj.eye_height is not None else canon.human_figure.eye_height
        if eye >= standing:
            hits.append(
                _hit(
                    EYE_BELOW_STANDING,
                    object_name=obj.name,
                    expected=standing,
                    actual=eye,
                    message=(
                        f"{obj.name} eye height {eye:g} m is not below "
                        f"standing height {standing:g} m."
                    ),
                )
            )
        hits.extend(_snap_location(obj, canon.meters_per_grid, tolerance_m))
        return hits

    if role == "airlock":
        hits.extend(
            _close(
                obj,
                AIRLOCK_DIAMETER,
                sizes["airlock"],
                obj.diameter_xy(),
                tolerance_m,
                f"{obj.name} diameter is {{actual}} m, canon expects {{expected}} m.",
            )
        )
        hits.extend(_snap_location(obj, canon.meters_per_grid, tolerance_m))
        return hits

    if role == "deck":
        hits.extend(
            _multiple(
                obj,
                DECK_GRID_CELLS,
                obj.location[2],
                canon.meters_per_grid,
                tolerance_m,
                "Z",
                (
                    f"{obj.name} Z location {{actual}} m is not an integer number of "
                    f"grid cells ({{step}} m)."
                ),
            )
        )
        hits.extend(_snap_location(obj, canon.meters_per_grid, tolerance_m, axes="XY"))
        return hits

    if role == "grid":
        hits.extend(_snap_location(obj, canon.meters_per_grid, tolerance_m))
        return hits

    return hits


def _shoulder_clearance(
    figure: SceneObject,
    airlocks: list[tuple[SceneObject, Role]],
    canon: CanonLike,
) -> list[Violation]:
    shoulder = figure.width()
    limits = [canon.airlock_diameter]
    limits.extend(obj.diameter_xy() for obj, _role in airlocks)
    limit = min(limits)
    # Shoulders must be strictly inside the hatch, not merely within tolerance of the rim.
    if shoulder < limit - 1e-12:
        return []
    return [
        _hit(
            AIRLOCK_SHOULDER,
            object_name=figure.name,
            expected=limit,
            actual=shoulder,
            message=(
                f"{figure.name} shoulder width {shoulder:g} m does not fit "
                f"through airlock diameter {limit:g} m."
            ),
        )
    ]


def _snap_location(
    obj: SceneObject,
    step: float,
    tolerance_m: float,
    axes: str = "XYZ",
) -> list[Violation]:
    hits: list[Violation] = []
    values = dict(zip("XYZ", obj.location, strict=True))
    for axis in axes:
        hits.extend(
            _multiple(
                obj,
                LOCATION_GRID_SNAP,
                values[axis],
                step,
                tolerance_m,
                axis,
                (
                    f"{obj.name} {axis} location {{actual}} m is not a multiple of "
                    f"canon step {{step}} m."
                ),
            )
        )
    return hits


def _close(
    obj: SceneObject,
    check: Check,
    expected: float,
    actual: float,
    tolerance_m: float,
    message: str,
) -> list[Violation]:
    if abs(actual - expected) <= tolerance_m:
        return []
    return [
        _hit(
            check,
            object_name=obj.name,
            expected=expected,
            actual=actual,
            message=message.format(actual=f"{actual:g}", expected=f"{expected:g}"),
        )
    ]


def _multiple(
    obj: SceneObject,
    check: Check,
    actual: float,
    step: float,
    tolerance_m: float,
    axis: str,
    message: str,
) -> list[Violation]:
    if step <= 0:
        return []
    remainder = abs(actual / step - round(actual / step)) * step
    if remainder <= tolerance_m:
        return []
    return [
        _hit(
            check,
            object_name=obj.name,
            expected=step,
            actual=actual,
            axis=axis,
            step=step,
            message=message.format(actual=f"{actual:g}", step=f"{step:g}"),
        )
    ]


def _hit(
    check: Check,
    *,
    message: str,
    object_name: str | None = None,
    expected: float | None = None,
    actual: float | None = None,
    axis: str | None = None,
    role: str | None = None,
    step: float | None = None,
    example: str | None = None,
) -> Violation:
    return Violation(
        check=check.name,
        code=check.code,
        message=message,
        fix=format_fix(
            check,
            object_name=object_name,
            expected=expected if expected is None else f"{expected:g}",
            actual=actual if actual is None else f"{actual:g}",
            axis=axis,
            role=role,
            step=step if step is None else f"{step:g}",
            example=example,
        ),
        object_name=object_name,
        expected=expected,
        actual=actual,
        axis=axis,
    )
