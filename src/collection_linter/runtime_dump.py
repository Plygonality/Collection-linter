"""Self-contained bpy scene dump.

This module has no collection-linter imports so it can be exec'd inside Blender
via Plygon-mcp ``execute_blender_code``. The JSON is the source of truth;
the .blend is the cache.
"""

from __future__ import annotations

FORMAT = "collection-linter"
FORMAT_VERSION = 1
ROLE_PROP = "unit_canon.role"
EYE_PROP = "unit_canon.eye_height"
SHOULDER_PROP = "unit_canon.shoulder_width"
CANON_ASSET_NAME = "HumanFigure"


def _axis3(value):
    if hasattr(value, "x"):
        return [float(value.x), float(value.y), float(value.z)]
    return [float(value[0]), float(value[1]), float(value[2])]


def _id_get(obj, key):
    getter = getattr(obj, "get", None)
    if callable(getter):
        return getter(key)
    props = getattr(obj, "properties", None)
    if isinstance(props, dict):
        return props.get(key)
    try:
        return obj[key]
    except (KeyError, TypeError, AttributeError):
        return None


def _collection_name(obj) -> str:
    collections = getattr(obj, "users_collection", None) or ()
    if not collections:
        return ""
    first = collections[0]
    return getattr(first, "name", str(first))


def dump_scene_dict(bpy, *, asset_name: str = CANON_ASSET_NAME) -> dict:
    """Dump every object in the current Blender file as a collection-linter scene."""
    objects = []
    for obj in bpy.data.objects:
        role = _id_get(obj, ROLE_PROP)
        if not role and obj.name == asset_name:
            role = "human_figure"
        row = {
            "name": obj.name,
            "collection": _collection_name(obj),
            "dimensions": _axis3(obj.dimensions),
            "location": _axis3(obj.location),
        }
        if role:
            row["role"] = role
        eye = _id_get(obj, EYE_PROP)
        if eye is not None:
            row["eye_height"] = float(eye)
        shoulder = _id_get(obj, SHOULDER_PROP)
        if shoulder is not None:
            row["shoulder_width"] = float(shoulder)
        objects.append(row)
    return {
        "format": FORMAT,
        "version": FORMAT_VERSION,
        "objects": objects,
    }


def dump_scene_json(bpy, *, asset_name: str = CANON_ASSET_NAME) -> str:
    import json

    return json.dumps(dump_scene_dict(bpy, asset_name=asset_name), indent=2)
