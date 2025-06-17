import subprocess
import pytest

def test_script_help():
    result = subprocess.run(
        ["python3", "port_manager.py", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()

def test_script_version():
    result = subprocess.run(
        ["python3", "port_manager.py", "--version"],
        capture_output=True,
        text=True
    )
    assert "Port Manager CLI v" in result.stdout
