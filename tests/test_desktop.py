"""Tests for the desktop wrapper module."""


def test_desktop_module_import():
    """Test that the desktop module can be imported."""
    from docling_serve import desktop

    assert desktop is not None
    assert hasattr(desktop, "run_desktop")
    assert hasattr(desktop, "start_server")


def test_desktop_command_exists():
    """Test that the desktop command is registered in the CLI."""
    from typer.testing import CliRunner

    from docling_serve.__main__ import app

    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "desktop" in result.stdout


def test_pyproject_has_desktop_extra():
    """Test that pyproject.toml has the desktop extra dependency."""
    from pathlib import Path

    import tomllib

    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)

    assert "desktop" in pyproject["project"]["optional-dependencies"]
    desktop_deps = pyproject["project"]["optional-dependencies"]["desktop"]
    assert any("pywebview" in dep for dep in desktop_deps)
