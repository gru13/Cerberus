"""Intent: Check Python files against the project rules in docs/code-style.md.

Why: Ruff checks signatures and docstring syntax; this script checks the rules that are ours.
"""

import ast
import sys
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

SIZE_WARN_LINES = 200
SIZE_LIMIT_LINES = 300
FUNCTION_LINES_MAX = 70
FUNCTIONS_PER_FILE_WARN = 12
SHORT_FUNCTION_LINES_MAX = 3
GENERIC_FILE_NAMES = frozenset({"utils", "helpers", "misc", "common"})
# fmt: off
BUILTIN_ERRORS = frozenset({
    "Exception", "BaseException", "ValueError", "TypeError", "RuntimeError", "KeyError",
    "IndexError", "AttributeError", "LookupError", "NotImplementedError", "OSError", "IOError",
    "AssertionError",
})
# fmt: on
type FunctionNode = ast.FunctionDef | ast.AsyncFunctionDef


class Finding(BaseModel):
    """One rule result for one location in a file."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    level: Literal["FAIL", "WARN"]
    path: str
    line: int
    message: str


def functions_in(tree: ast.Module) -> list[FunctionNode]:
    """Return every function and method in a module, in source order."""
    nodes = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)]
    return sorted(nodes, key=lambda n: n.lineno)


def check_module(path: Path, tree: ast.Module, source: str) -> list[Finding]:
    """Check the file-level rules: Intent line, size flags, breadth, and mixed layers.

    Functional: Fails a file without an Intent line or above 300 lines without a Why line.
    Technical: Reads the module docstring with ast; counts lines, functions, and imports.
    Limits: Warn above 200 lines or 12 functions; fail above 300 lines.
    """
    found: list[Finding] = []

    def add(level: Literal["FAIL", "WARN"], message: str) -> None:
        """Record one finding for this file at line 1."""
        found.append(Finding(level=level, path=str(path), line=1, message=message))

    doc = ast.get_docstring(tree) or ""
    intent = doc.splitlines()[0] if doc else ""
    if not intent.startswith("Intent:"):
        add("FAIL", "The file has no Intent line at the top.")
    if " and " in intent:
        add("WARN", "The Intent line contains 'and'. The file can have two intents.")
    if path.stem in GENERIC_FILE_NAMES:
        add("WARN", f"The file name '{path.stem}' is generic. Name the file by its intent.")
    line_count = len(source.splitlines())
    if line_count > SIZE_LIMIT_LINES and "Why:" not in doc:
        add("FAIL", f"The file has {line_count} lines. Split it or add a Why line.")
    elif line_count > SIZE_WARN_LINES:
        add("WARN", f"The file has {line_count} lines. Think about a split.")
    function_count = len(functions_in(tree))
    if function_count > FUNCTIONS_PER_FILE_WARN:
        add("WARN", f"The file has {function_count} functions. Think about a split.")
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) for a in n.names}
    modules = {n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    if "APIRouter" in imported and any(m.startswith("sqlalchemy") for m in modules):
        add("WARN", "The file has HTTP routes and database queries. Split the layers.")
    return found


def code_line_count(node: FunctionNode) -> int:
    """Return the number of lines in a function body after its docstring.

    Functional: Lets short helpers skip the Functional and Technical lines.
    Technical: Measures from the first statement after the docstring to the end line.
    """
    body = node.body
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        body = body[1:]
    if not body:
        return 0
    end_line = node.end_lineno or body[-1].lineno
    return end_line - body[0].lineno + 1


def check_function(path: Path, node: FunctionNode) -> list[Finding]:
    """Check one function: length limit, summary line, and header tags.

    Functional: Fails functions above 70 lines or without a correct header.
    Technical: Reads the docstring with ast; tags must start a line after the summary.
    Limits: 70 lines per function; tags are optional at 3 code lines or fewer.
    """
    found: list[Finding] = []
    where = {"path": str(path), "line": node.lineno}
    length = (node.end_lineno or node.lineno) - node.lineno + 1
    if length > FUNCTION_LINES_MAX:
        found.append(
            Finding(level="FAIL", message=f"'{node.name}' has {length} lines (max 70).", **where)
        )
    doc = ast.get_docstring(node)
    if not doc:
        found.append(Finding(level="FAIL", message=f"'{node.name}' has no docstring.", **where))
        return found
    if not doc.splitlines()[0].rstrip().endswith("."):
        message = f"The summary line of '{node.name}' does not end with a full stop."
        found.append(Finding(level="FAIL", message=message, **where))
    if code_line_count(node) > SHORT_FUNCTION_LINES_MAX:
        tags = {line.strip().split(":", 1)[0] for line in doc.splitlines()[1:]}
        for tag in ("Functional", "Technical"):
            if tag not in tags:
                message = f"'{node.name}' has no {tag} line."
                found.append(Finding(level="FAIL", message=message, **where))
    return found


def check_raises(path: Path, tree: ast.Module) -> list[Finding]:
    """Fail every raise of a built-in exception.

    Functional: Keeps all errors in the CerberusError tree with fixed codes.
    Technical: Finds `raise X(...)` and `raise X` nodes and compares the class name.
    """
    found: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Raise) or node.exc is None:
            continue
        target = node.exc.func if isinstance(node.exc, ast.Call) else node.exc
        name = target.id if isinstance(target, ast.Name) else getattr(target, "attr", "")
        if name in BUILTIN_ERRORS:
            message = f"The code raises the built-in '{name}'. Raise a CerberusError subclass."
            found.append(Finding(level="FAIL", path=str(path), line=node.lineno, message=message))
    return found


def check_file(path: Path) -> list[Finding]:
    """Check one Python file against all rules.

    Functional: Test files get only the Intent check; source files get every check.
    Technical: Parses the file once with ast and runs the module, function, and raise checks.
    """
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    found = check_module(path, tree, source)
    if "tests" in path.parts:
        return found
    for node in functions_in(tree):
        found += check_function(path, node)
    return found + check_raises(path, tree)


def outline(paths: list[Path]) -> None:
    """Print each file's Intent line and each function's summary line.

    Functional: Gives people and agents a map of the code without reading bodies.
    Technical: Reads docstrings with ast; prints `path:line name: summary`.
    """
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        doc = ast.get_docstring(tree) or ""
        print(f"{path}: {doc.splitlines()[0] if doc else '(no Intent line)'}")
        for node in functions_in(tree):
            summary = (ast.get_docstring(node) or "(no docstring)").splitlines()[0]
            print(f"  {path}:{node.lineno} {node.name}: {summary}")


def main(argv: list[str]) -> int:
    """Run the style check (or the outline) and return the process exit code.

    Functional: `style_check.py [--outline] [paths...]`; exit 1 when a FAIL is found.
    Technical: Collects `*.py` files under the paths (default: src, scripts, tests).
    """
    show_outline = "--outline" in argv
    default_roots = [Path(p) for p in ("src", "scripts", "tests")]
    roots = [Path(a) for a in argv if a != "--outline"] or default_roots
    paths = sorted(p for root in roots for p in ([root] if root.is_file() else root.rglob("*.py")))
    if show_outline:
        outline(paths)
        return 0
    findings = [f for p in paths for f in check_file(p)]
    for f in findings:
        print(f"{f.level} {f.path}:{f.line} {f.message}")
    failures = sum(1 for f in findings if f.level == "FAIL")
    print(f"The style check finds {failures} failures and {len(findings) - failures} warnings.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
