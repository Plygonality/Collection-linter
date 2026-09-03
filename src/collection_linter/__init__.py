"""Collection-linter: scene roles against Unit-canon.

Other repos import this package. The JSON dump is the inspectable error surface.
"""

from collection_linter.canon import expected_sizes, load_canon
from collection_linter.checks import CHECKS, CHECKS_BY_CODE, CHECKS_BY_NAME, Check
from collection_linter.dump import to_dump_script
from collection_linter.engine import LintResult, Violation, lint
from collection_linter.report import format_human, format_json
from collection_linter.roles import ROLE_PROP, ROLES, Role, infer_role
from collection_linter.scene import (
    FORMAT,
    FORMAT_VERSION,
    Scene,
    SceneError,
    SceneObject,
    load_scene,
)

__all__ = [
    "CHECKS",
    "CHECKS_BY_CODE",
    "CHECKS_BY_NAME",
    "FORMAT",
    "FORMAT_VERSION",
    "ROLE_PROP",
    "ROLES",
    "Check",
    "LintResult",
    "Role",
    "Scene",
    "SceneError",
    "SceneObject",
    "Violation",
    "expected_sizes",
    "format_human",
    "format_json",
    "infer_role",
    "lint",
    "load_canon",
    "load_scene",
    "to_dump_script",
]

__version__ = "0.1.0"
