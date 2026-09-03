# Collection-linter

Scene contract checker. Reads a JSON scene dump (or live bpy), assigns roles, and reports readable faults against [Unit-canon](https://github.com/Plygonality/Unit-canon). This is the inspectable error surface your process actually persists on.

Other repos import this package. Do not copy canon numbers here. Change them in `unit_canon/canon.json`.

```
Plygon-mcp dump-script  →  scene.json  →  collection-linter lint  →  named faults + fix strings
```

| Role | Job |
|---|---|
| **This library** | Assign `human_figure`, `airlock`, `deck`, `grid`. Run named checks. JSON + human report |
| **[Unit-canon](https://github.com/Plygonality/Unit-canon)** | Meters per grid, deck height, airlock diameter, human figure |
| **[Plygon-mcp](https://github.com/Plygonality/Plygon-mcp)** | Run `dump-script` in Blender, screenshot after a fix |
| **The `.blend`** | Working cache, never the source of truth |

## Install

```bash
pip install -e ".[dev]"
```

Python 3.11+. No Blender required to lint a dump.

```bash
collection-linter lint examples/scene.json
collection-linter lint examples/scene.json --json
collection-linter dump-script
collection-linter roles
pytest -q
```

## CLI

```bash
collection-linter lint examples/scene.json      # human report
collection-linter lint examples/scene.json --json
collection-linter dump-script          # bpy script Plygon-mcp can run to print scene.json
collection-linter roles                # roles, how they are assigned, named checks
```

Exit codes: **0** clean, **1** violations, **2** bad input (missing file, invalid JSON, broken schema).

```python
from collection_linter import Scene, lint, load_scene, to_dump_script

result = lint(load_scene("examples/scene.json"))
if not result.ok:
    for hit in result.violations:
        print(hit.code, hit.message, hit.fix)

# Plygon-mcp: execute_blender_code(to_dump_script()) → write scene.json → lint
```

## Scene JSON

Dump objects with a `role` of `human_figure`, `airlock`, `deck`, or `grid`. Names follow ZeroMap `Category_Subtype_Variant`. Objects named `HumanFigure` (or `airlock_*`, `deck_*`, `grid_*`, `Human_*`, `Airlock_*`, …) get a role even without the field. Custom property `unit_canon.role` is what the Blender dump reads.

```json
{
  "format": "collection-linter",
  "version": 1,
  "objects": [
    {
      "name": "Human_Figure_Canon",
      "collection": "canon",
      "dimensions": [0.45, 0.30, 1.8],
      "location": [0, 0, 0],
      "role": "human_figure",
      "eye_height": 1.65
    }
  ]
}
```

`collection-linter dump-script` prints a self-contained bpy script. Paste it into Plygon-mcp `execute_blender_code`. Blender does not need this package installed.

## Checks

Each hit is a named check with a **fix** string.

| Check | Code | Rule |
|---|---|---|
| `human_standing_height` | `HUMAN_HEIGHT` | Figure Z == `canon.human_figure.standing_height` |
| `eye_below_standing` | `EYE_HEIGHT` | Eye < standing |
| `airlock_diameter` | `AIRLOCK_DIAMETER` | XY diameter == `canon.airlock_diameter` (1.0 m on the default file) |
| `airlock_shoulder_clearance` | `AIRLOCK_SHOULDER` | Figure shoulders fit through the airlock |
| `deck_grid_cells` | `DECK_SPACING` | Deck Z is an integer number of grid cells |
| `location_grid_snap` | `GRID_SNAP` | Locations snap to `meters_per_grid` |
| `zeromap_name` | `ZEROMAP_NAME` | `Category_Subtype_Variant` |
| `required_role` | `MISSING_ROLE` | One object for every canon role |

Human report:

```
collection-linter  FAIL  1 violation(s), 4 checked  scene.json

HUMAN_HEIGHT  Human_Figure_Canon
  Human_Figure_Canon standing height is 2.5 m, canon expects 1.8 m.
  fix: Set Human_Figure_Canon Z dimension to 1.8 m (unit_canon.human_figure.standing_height).
```

## Tests

The rule engine is fixture-only. No Blender.

```bash
pip install -e ".[dev]"
pytest -q
```

Fixtures live in `tests/fixtures/`.
