"""Roles listing is the contract other repos read."""

from __future__ import annotations

from collection_linter.checks import CHECKS_BY_CODE
from collection_linter.roles import ROLE_DOCS, ROLES


def test_four_roles() -> None:
    assert ROLES == ("human_figure", "airlock", "deck", "grid")
    for role in ROLES:
        assert ROLE_DOCS[role]


def test_named_checks_cover_the_contract() -> None:
    for code in (
        "HUMAN_HEIGHT",
        "EYE_HEIGHT",
        "AIRLOCK_DIAMETER",
        "AIRLOCK_SHOULDER",
        "DECK_SPACING",
        "GRID_SNAP",
        "ZEROMAP_NAME",
        "MISSING_ROLE",
    ):
        assert code in CHECKS_BY_CODE
        assert CHECKS_BY_CODE[code].fix
