"""Rule engine reads fixtures. No Blender."""

from __future__ import annotations

from pathlib import Path

from collection_linter import expected_sizes, lint, load_scene
from collection_linter.canon import load_canon
from collection_linter.checks import CHECKS
from tests.conftest import fixture_path

_PASSING = (
    "clean.json",
    "canon_asset_name.json",
    "unwrapped_objects.json",
    "bare_array.json",
    "deck_on_grid_cell.json",
    "inferred_roles.json",
    "blender_suffix.json",
)

_CODE_FIXTURES = (
    ("human_height.json", "HUMAN_HEIGHT"),
    ("eye_height.json", "EYE_HEIGHT"),
    ("airlock_diameter.json", "AIRLOCK_DIAMETER"),
    ("airlock_shoulder.json", "AIRLOCK_SHOULDER"),
    ("deck_z.json", "DECK_SPACING"),
    ("grid_snap.json", "GRID_SNAP"),
    ("location_snap.json", "GRID_SNAP"),
    ("zeromap_name.json", "ZEROMAP_NAME"),
    ("missing_roles.json", "MISSING_ROLE"),
)


def test_every_check_has_a_fix() -> None:
    assert CHECKS
    for check in CHECKS:
        assert check.name
        assert check.code
        assert check.description
        assert check.fix


def test_expected_sizes_read_canon() -> None:
    canon = load_canon()
    sizes = expected_sizes()
    assert sizes["grid"] == canon.meters_per_grid
    assert sizes["deck"] == canon.deck_height
    assert sizes["airlock"] == canon.airlock_diameter
    assert sizes["human_figure"] == canon.human_figure.standing_height


def test_passing_fixtures(fixtures: Path) -> None:
    for name in _PASSING:
        result = lint(load_scene(fixtures / name))
        assert result.ok, (name, [item.to_dict() for item in result.violations])
        assert result.checked >= 4


def test_violation_fixtures_carry_fix_strings() -> None:
    canon = load_canon()
    for name, code in _CODE_FIXTURES:
        result = lint(load_scene(fixture_path(name)))
        assert not result.ok, name
        hits = result.by_code(code)
        assert hits, (name, [item.code for item in result.violations])
        for hit in hits:
            assert hit.fix
            assert hit.check
        if code == "HUMAN_HEIGHT":
            assert hits[0].expected == canon.human_figure.standing_height
        if code == "AIRLOCK_DIAMETER":
            assert hits[0].expected == canon.airlock_diameter
        if code == "GRID_SNAP":
            assert hits[0].expected == canon.meters_per_grid
        if code == "DECK_SPACING":
            assert hits[0].expected == canon.meters_per_grid
        if code == "MISSING_ROLE":
            assert len(hits) == 4


def test_missing_roles_can_be_suppressed() -> None:
    result = lint(load_scene(fixture_path("missing_roles.json")), require_roles=False)
    assert result.ok
    assert result.checked == 0
