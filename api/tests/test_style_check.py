"""Intent: Test the project style checker on small sample files."""

from pathlib import Path

import style_check


def write(tmp_path: Path, name: str, source: str) -> Path:
    path = tmp_path / name
    path.write_text(source, encoding="utf-8")
    return path


def test_good_file_passes(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        "good.py",
        '"""Intent: Add numbers."""\n\n\ndef add(a: int, b: int) -> int:\n'
        '    """Return the sum of two numbers."""\n    return a + b\n',
    )

    assert style_check.check_file(path) == []


def test_missing_intent_and_tags_fail(tmp_path: Path) -> None:
    body = "\n".join(f"    x{i} = {i}" for i in range(5))
    path = write(tmp_path, "bad.py", f'def work() -> None:\n    """Do some work."""\n{body}\n')

    messages = [f.message for f in style_check.check_file(path)]

    assert "The file has no Intent line at the top." in messages
    assert "'work' has no Functional line." in messages
    assert "'work' has no Technical line." in messages


def test_builtin_raise_fails(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        "raises.py",
        '"""Intent: Raise an error."""\n\n\ndef boom() -> None:\n'
        '    """Raise a built-in error."""\n    raise ValueError\n',
    )

    findings = style_check.check_file(path)

    assert [f.level for f in findings] == ["FAIL"]
    assert "built-in 'ValueError'" in findings[0].message


def test_long_function_fails(tmp_path: Path) -> None:
    body = "\n".join(f"    x{i} = {i}" for i in range(75))
    source = (
        '"""Intent: Hold a long function."""\n\n\ndef long() -> None:\n'
        '    """Do many steps.\n\n    Functional: Many steps.\n'
        '    Technical: Many lines.\n    """\n'
        f"{body}\n"
    )
    path = write(tmp_path, "long.py", source)

    messages = [f.message for f in style_check.check_file(path)]

    assert any("max 70" in m for m in messages)
