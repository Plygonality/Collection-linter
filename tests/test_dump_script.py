"""Dump-script is a bpy program. Exec it against an in-memory stand-in, not Blender."""

from __future__ import annotations

from collection_linter.dump import to_dump_script
from collection_linter.runtime_dump import dump_scene_dict
from tests.fake_bpy import FakeBpy, FakeCollection, FakeObject, FakeVector


def test_dump_script_compiles() -> None:
    script = to_dump_script()
    compile(script, "<dump>", "exec")
    assert "dump_scene_dict" in script
    named = to_dump_script(asset_name="HumanFigure")
    compile(named, "<dump>", "exec")
    assert "HumanFigure" in named


def test_runtime_dump_without_blender() -> None:
    bpy = FakeBpy(
        objects=[
            FakeObject(
                "HumanFigure",
                dimensions=FakeVector(0.45, 0.3, 1.8),
                location=FakeVector(0, 0, 0),
                collections=(FakeCollection("canon"),),
                properties={"unit_canon.eye_height": 1.65},
            ),
            FakeObject(
                "Airlock_Hatch_Main",
                dimensions=FakeVector(1.0, 1.0, 2.0),
                location=FakeVector(0, 0, 0),
                collections=(FakeCollection("canon"),),
                properties={"unit_canon.role": "airlock"},
            ),
        ]
    )
    payload = dump_scene_dict(bpy)
    assert payload["format"] == "collection-linter"
    assert payload["version"] == 1
    by_name = {row["name"]: row for row in payload["objects"]}
    assert by_name["HumanFigure"]["role"] == "human_figure"
    assert by_name["HumanFigure"]["eye_height"] == 1.65
    assert by_name["Airlock_Hatch_Main"]["role"] == "airlock"
    assert by_name["Airlock_Hatch_Main"]["dimensions"] == [1.0, 1.0, 2.0]
