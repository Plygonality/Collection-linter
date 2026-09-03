"""JSON and human reports. This is the inspectable error surface."""

from __future__ import annotations

import json

from collection_linter.engine import LintResult

EXIT_CLEAN = 0
EXIT_VIOLATIONS = 1
EXIT_BAD_INPUT = 2


def result_exit_code(result: LintResult) -> int:
    return EXIT_CLEAN if result.ok else EXIT_VIOLATIONS


def format_json(result: LintResult) -> str:
    return json.dumps(result.to_dict(), indent=2) + "\n"


def format_human(result: LintResult, *, source: str | None = None) -> str:
    where = f"  {source}" if source else ""
    if result.ok:
        return f"collection-linter  ok  {result.checked} checked, 0 violations{where}\n"
    lines = [
        (
            f"collection-linter  FAIL  {len(result.violations)} violation(s), "
            f"{result.checked} checked{where}"
        ),
        "",
    ]
    for item in result.violations:
        target = item.object_name or item.check
        lines.append(f"{item.code}  {target}")
        lines.append(f"  {item.message}")
        lines.append(f"  fix: {item.fix}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
