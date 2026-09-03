"""Bad scene dumps are input errors, not lint violations."""

from __future__ import annotations

import pytest

from collection_linter.scene import SceneError, load_scene
from tests.conftest import fixture_path


@pytest.mark.parametrize(
    "name",
    ["bad_not_json.txt", "bad_schema.json", "bad_missing_name.json"],
)
def test_bad_fixtures_raise(name: str) -> None:
    with pytest.raises(SceneError):
        load_scene(fixture_path(name))


def test_missing_file_raises() -> None:
    with pytest.raises(SceneError, match="Cannot read"):
        load_scene(fixture_path("does-not-exist.json"))
