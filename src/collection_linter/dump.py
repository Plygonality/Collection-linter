"""Plygon-mcp dump script. Blender does not need this package installed."""

from __future__ import annotations

from pathlib import Path

_RUNTIME_PATH = Path(__file__).with_name("runtime_dump.py")


def to_dump_script(*, asset_name: str | None = None) -> str:
    """Self-contained bpy script that prints a scene dump as JSON."""
    runtime = _RUNTIME_PATH.read_text(encoding="utf-8")
    name_arg = f", asset_name={asset_name!r}" if asset_name else ""
    call = (
        "import json\n"
        f"result = dump_scene_dict(__import__('bpy'){name_arg})\n"
        "print(json.dumps(result, indent=2))\n"
    )
    return runtime + "\n\n" + call
