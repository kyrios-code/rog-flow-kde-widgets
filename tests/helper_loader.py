"""Load baseline helper definitions without their import-time command dispatch.

The shipped scripts intentionally remain byte-for-byte unchanged. Only known
constant assignments, imports, and definitions are compiled. The top-level
try/except blocks that query hardware or launch a session are never executed.
"""

import ast
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
HELPERS = {
    "control": ROOT / "widgets/rog-control/scripts/rog-control-helper.py",
    "gaming": ROOT / "widgets/rog-gaming/scripts/rog-gaming-helper.py",
}
CONSTANTS = {"control": {"FW"}, "gaming": {"HOME", "STEAM"}}


def load_helper(name):
    """Return a fresh module of the real helper definitions for each test."""
    path = HELPERS[name]
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    declarations = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef)):
            declarations.append(node)
        elif isinstance(node, ast.Assign) and all(
            isinstance(target, ast.Name) and target.id in CONSTANTS[name]
            for target in node.targets
        ):
            declarations.append(node)
    module = ModuleType("baseline_" + name)
    module.__file__ = str(path)
    exec(compile(ast.Module(body=declarations, type_ignores=[]), str(path), "exec"), module.__dict__)
    return module
