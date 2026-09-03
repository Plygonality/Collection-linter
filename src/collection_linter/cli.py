"""CLI: lint a scene dump, emit a bpy dump-script, list roles."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from collection_linter.canon import load_canon
from collection_linter.checks import CHECKS
from collection_linter.dump import to_dump_script
from collection_linter.engine import DEFAULT_TOLERANCE_M, lint
from collection_linter.names import ZEROMAP_EXAMPLES
from collection_linter.report import (
    EXIT_BAD_INPUT,
    format_human,
    format_json,
    result_exit_code,
)
from collection_linter.roles import ROLE_DOCS, ROLES
from collection_linter.scene import SceneError, load_scene


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="collection-linter",
        description=(
            "Scene contract checker. Reads a JSON scene dump (or live bpy), "
            "assigns roles, and reports readable faults against Unit-canon."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    lint_parser = sub.add_parser("lint", help="Lint a dumped scene JSON against Unit-canon.")
    lint_parser.add_argument("scene", type=Path)
    lint_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of the human report.",
    )
    lint_parser.add_argument(
        "--allow-missing-roles",
        action="store_true",
        help="Do not fail when a canon role is absent from the scene.",
    )
    lint_parser.add_argument(
        "--canon",
        type=Path,
        default=None,
        help="Override canon.json (tests only; omit in production).",
    )
    lint_parser.add_argument(
        "--tolerance",
        type=float,
        default=None,
        help="Absolute tolerance in meters (default 0.01).",
    )

    dump_parser = sub.add_parser(
        "dump-script",
        help="Emit a bpy script Plygon-mcp can run to print scene.json.",
    )
    dump_parser.add_argument("-o", "--output", type=Path, default=None)
    dump_parser.add_argument(
        "--asset-name",
        default=None,
        help="Canon figure object name (default HumanFigure).",
    )

    roles_parser = sub.add_parser("roles", help="List canon roles and how they are assigned.")
    roles_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of the human listing.",
    )

    args = parser.parse_args(argv)

    if args.command == "dump-script":
        script = to_dump_script(asset_name=args.asset_name)
        if args.output:
            args.output.write_text(script, encoding="utf-8")
        else:
            sys.stdout.write(script)
        return 0

    if args.command == "roles":
        payload = _roles_payload()
        if args.json:
            json.dump(payload, sys.stdout, indent=2)
            sys.stdout.write("\n")
        else:
            sys.stdout.write(_format_roles(payload))
        return 0

    if args.command == "lint":
        try:
            canon = load_canon(args.canon)
            scene = load_scene(args.scene)
        except Exception as exc:
            # CanonError and SceneError are ValueError; also catch missing-file OS errors
            # already wrapped. Unknown failures still count as bad input for the CLI.
            if not isinstance(exc, (SceneError, OSError, ValueError, json.JSONDecodeError)):
                raise
            sys.stderr.write(f"collection-linter: {exc}\n")
            return EXIT_BAD_INPUT
        result = lint(
            scene,
            canon,
            require_roles=not args.allow_missing_roles,
            tolerance_m=args.tolerance if args.tolerance is not None else DEFAULT_TOLERANCE_M,
        )
        if args.json:
            sys.stdout.write(format_json(result))
        else:
            sys.stdout.write(format_human(result, source=str(args.scene)))
        return result_exit_code(result)

    parser.error(f"Unknown command {args.command}")
    return EXIT_BAD_INPUT


def _roles_payload() -> dict[str, object]:
    checks = [
        {
            "name": item.name,
            "code": item.code,
            "description": item.description,
            "fix": item.fix,
        }
        for item in CHECKS
    ]
    roles = [
        {
            "role": role,
            "description": ROLE_DOCS[role],
            "example": ZEROMAP_EXAMPLES[role],
            "assigned_by": [
                f"role field {role!r}",
                f"name {role}_*",
                f"ZeroMap category {ZEROMAP_EXAMPLES[role].split('_', 1)[0]}_*",
                f"custom property unit_canon.role = {role!r}",
            ],
        }
        for role in ROLES
    ]
    roles[0]["assigned_by"].append("name HumanFigure (canon.human_figure.asset_name)")
    return {"roles": roles, "checks": checks}


def _format_roles(payload: dict[str, object]) -> str:
    lines = ["Roles", ""]
    for item in payload["roles"]:
        lines.append(item["role"])
        lines.append(f"  {item['description']}")
        lines.append(f"  example: {item['example']}")
        lines.append("  assigned by:")
        for rule in item["assigned_by"]:
            lines.append(f"    - {rule}")
        lines.append("")
    lines.append("Checks")
    lines.append("")
    for item in payload["checks"]:
        lines.append(f"{item['code']}  {item['name']}")
        lines.append(f"  {item['description']}")
        lines.append(f"  fix: {item['fix']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
