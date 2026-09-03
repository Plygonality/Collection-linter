"""CLI: exit 0 clean, 1 violations, 2 bad input. JSON and human report."""

from __future__ import annotations

import json
from pathlib import Path

from collection_linter.cli import main
from tests.conftest import fixture_path


def test_lint_clean_human(capsys) -> None:
    assert main(["lint", str(fixture_path("clean.json"))]) == 0
    out = capsys.readouterr().out
    assert "ok" in out
    assert "0 violations" in out


def test_lint_clean_json(capsys) -> None:
    assert main(["lint", str(fixture_path("clean.json")), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["checked"] >= 4
    assert payload["violations"] == []


def test_lint_violations_human_and_json(capsys) -> None:
    scene = str(fixture_path("human_height.json"))
    assert main(["lint", scene]) == 1
    human = capsys.readouterr().out
    assert "FAIL" in human
    assert "HUMAN_HEIGHT" in human
    assert "fix:" in human

    assert main(["lint", scene, "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["violations"][0]["code"] == "HUMAN_HEIGHT"
    assert payload["violations"][0]["fix"]
    assert payload["violations"][0]["check"] == "human_standing_height"


def test_lint_allow_missing_roles(capsys) -> None:
    assert main(["lint", str(fixture_path("missing_roles.json")), "--allow-missing-roles"]) == 0
    capsys.readouterr()
    assert main(["lint", str(fixture_path("missing_roles.json")), "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert any(item["code"] == "MISSING_ROLE" for item in payload["violations"])


def test_bad_input_exit_2(capsys) -> None:
    missing = Path("/tmp/collection-linter-does-not-exist.json")
    assert main(["lint", str(missing)]) == 2
    err = capsys.readouterr().err
    assert "Cannot read" in err or "scene" in err.lower()

    assert main(["lint", str(fixture_path("bad_not_json.txt"))]) == 2
    assert main(["lint", str(fixture_path("bad_schema.json"))]) == 2
    assert main(["lint", str(fixture_path("bad_missing_name.json"))]) == 2


def test_dump_script(capsys, tmp_path: Path) -> None:
    assert main(["dump-script"]) == 0
    script = capsys.readouterr().out
    compile(script, "<dump>", "exec")
    assert "dump_scene_dict" in script
    assert "unit_canon.role" in script

    out = tmp_path / "dump.py"
    assert main(["dump-script", "-o", str(out)]) == 0
    assert "dump_scene_dict" in out.read_text(encoding="utf-8")


def test_roles_human_and_json(capsys) -> None:
    assert main(["roles"]) == 0
    human = capsys.readouterr().out
    assert "human_figure" in human
    assert "airlock" in human
    assert "deck" in human
    assert "grid" in human
    assert "HUMAN_HEIGHT" in human
    assert "Category_Subtype_Variant" in human or "ZeroMap" in human

    assert main(["roles", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    roles = [item["role"] for item in payload["roles"]]
    assert roles == ["human_figure", "airlock", "deck", "grid"]
    names = [item["name"] for item in payload["checks"]]
    assert "human_standing_height" in names
    assert "zeromap_name" in names
