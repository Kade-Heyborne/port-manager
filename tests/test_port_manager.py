import subprocess
import pytest
from unittest.mock import Mock, patch
from port_manager.cli import (
    find_process_on_port,
    kill_process_by_pid,
    wait_for_port_release,
)


def test_script_help():
    result = subprocess.run(
        ["python", "-m", "port_manager.cli", "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_script_version():
    result = subprocess.run(
        ["python", "-m", "port_manager.cli", "--version"],
        capture_output=True,
        text=True,
    )
    assert "Port Manager CLI v" in result.stdout


class TestPortManagerFunctions:
    """Functional tests for core port manager functions."""

    def test_find_process_on_port_no_process(self, monkeypatch):
        """Test finding process on port when no process is listening."""
        mock_proc_iter = Mock(return_value=[])
        monkeypatch.setattr("psutil.process_iter", mock_proc_iter)

        result = find_process_on_port(8080)
        assert result is None

    def test_find_process_on_port_with_process(self, monkeypatch):
        """Test finding process on port when a process is listening."""
        # Mock process
        mock_proc = Mock()
        mock_proc.pid = 1234
        mock_proc.name.return_value = "test_server"

        # Mock connection
        mock_conn = Mock()
        mock_conn.laddr.port = 8080
        mock_conn.status = "LISTEN"

        mock_proc.connections.return_value = [mock_conn]

        # Mock process iterator
        mock_proc_iter = Mock(return_value=[mock_proc])
        monkeypatch.setattr("psutil.process_iter", mock_proc_iter)

        result = find_process_on_port(8080)
        assert result == mock_proc

    def test_find_process_on_port_different_port(self, monkeypatch):
        """Test finding process on port when process is listening on different port."""
        # Mock process listening on port 8081, not 8080
        mock_proc = Mock()
        mock_conn = Mock()
        mock_conn.laddr.port = 8081
        mock_conn.status = "LISTEN"
        mock_proc.connections.return_value = [mock_conn]

        mock_proc_iter = Mock(return_value=[mock_proc])
        monkeypatch.setattr("psutil.process_iter", mock_proc_iter)

        result = find_process_on_port(8080)
        assert result is None

    def test_kill_process_by_pid_successful_graceful(self, monkeypatch, capsys):
        """Test successful graceful process termination."""
        mock_proc = Mock()
        mock_proc.pid = 1234
        mock_proc.name.return_value = "test_proc"

        mock_process = Mock(return_value=mock_proc)
        monkeypatch.setattr("psutil.Process", mock_process)

        result = kill_process_by_pid(1234, force=False)

        assert result is True
        mock_proc.terminate.assert_called_once()
        mock_proc.wait.assert_called_once_with(timeout=5.0)

        # Check output
        captured = capsys.readouterr()
        assert "gracefully terminate" in captured.out
        assert "terminated successfully" in captured.out

    def test_kill_process_by_pid_successful_force(self, monkeypatch, capsys):
        """Test successful force process termination."""
        mock_proc = Mock()
        mock_proc.pid = 1234
        mock_proc.name.return_value = "test_proc"

        mock_process = Mock(return_value=mock_proc)
        monkeypatch.setattr("psutil.Process", mock_process)

        result = kill_process_by_pid(1234, force=True)

        assert result is True
        mock_proc.kill.assert_called_once()
        mock_proc.wait.assert_called_once_with(timeout=1.0)

        # Check output
        captured = capsys.readouterr()
        assert "forcefully terminate" in captured.out
        assert "terminated successfully" in captured.out

    def test_wait_for_port_release_immediate(self, monkeypatch):
        """Test port release check when port is immediately free."""
        mock_find_process = Mock(return_value=None)
        monkeypatch.setattr("port_manager.cli.find_process_on_port", mock_find_process)

        result = wait_for_port_release(8080)
        assert result is True
        mock_find_process.assert_called_once_with(8080)

    def test_wait_for_port_release_timeout(self, monkeypatch):
        """Test port release check timeout when port never becomes free."""
        mock_proc = Mock()
        mock_find_process = Mock(return_value=mock_proc)  # Always returns a process
        monkeypatch.setattr("port_manager.cli.find_process_on_port", mock_find_process)

        # Mock time to control the loop
        time_values = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2]  # Simulate time progression
        mock_time = Mock(side_effect=time_values)
        monkeypatch.setattr("time.time", mock_time)

        mock_time_sleep = Mock()
        monkeypatch.setattr("time.sleep", mock_time_sleep)

        result = wait_for_port_release(8080, max_wait=1.0, check_interval=0.2)

        assert result is False
        # Should check multiple times until timeout
        assert mock_find_process.call_count >= 4  # At least 4 calls before timeout


class TestPerformance:
    """Performance tests to ensure operations complete within reasonable time."""

    def test_find_process_on_port_performance(self, monkeypatch):
        """Test that finding a process on port completes quickly."""
        import time

        # Mock empty process list for fast execution
        mock_proc_iter = Mock(return_value=[])
        monkeypatch.setattr("psutil.process_iter", mock_proc_iter)

        start_time = time.time()
        result = find_process_on_port(8080)
        end_time = time.time()

        # Should complete in well under 1 second
        assert end_time - start_time < 0.1
        assert result is None

    def test_wait_for_port_release_timeout_performance(self, monkeypatch):
        """Test that port release wait times out within expected duration."""
        import time

        mock_proc = Mock()
        mock_find_process = Mock(return_value=mock_proc)
        monkeypatch.setattr("port_manager.cli.find_process_on_port", mock_find_process)

        mock_time = Mock(
            side_effect=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        )  # More time checks to avoid StopIteration
        monkeypatch.setattr("time.time", mock_time)

        mock_time_sleep = Mock()
        monkeypatch.setattr("time.sleep", mock_time_sleep)

        start_time = time.time()
        result = wait_for_port_release(8080, max_wait=0.5, check_interval=0.1)
        end_time = time.time()

        # Should complete in reasonable time (mocked time doesn't affect real sleeps)
        assert end_time - start_time < 2.0  # Allow some time for execution
        assert result is False

    def test_kill_process_by_pid_fast_failure(self, monkeypatch, capsys):
        """Test that kill_process_by_pid fails quickly for non-existent process."""
        import time

        mock_process = Mock(side_effect=Exception("No such process"))
        monkeypatch.setattr("psutil.Process", mock_process)

        start_time = time.time()
        result = kill_process_by_pid(99999, force=True)
        end_time = time.time()

        # Should complete very quickly
        assert end_time - start_time < 0.01
        assert result is False

    def test_cli_check_command_performance(self):
        """Test that CLI check command responds within reasonable time."""
        import time
        import subprocess

        start_time = time.time()
        result = subprocess.run(
            ["python", "-m", "port_manager.cli", "check", "9999"],
            capture_output=True,
            text=True,
            timeout=10,  # Fail if it takes more than 10 seconds
        )
        end_time = time.time()

        # Should complete in under 5 seconds (allowing for some system variability)
        assert end_time - start_time < 5.0
        assert result.returncode == 0


class TestCLIIntegration:
    """Integration tests for complete CLI workflows."""

    def test_check_free_port(self):
        """Test checking a port that should be free."""
        result = subprocess.run(
            ["python", "-m", "port_manager.cli", "check", "9998"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Port 9998 is free" in result.stdout

    def test_check_invalid_command(self):
        """Test invalid command returns error."""
        result = subprocess.run(
            ["python", "-m", "port_manager.cli", "invalid", "8080"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2  # argparse error
        assert "invalid choice" in result.stderr

    def test_kill_no_process(self):
        """Test killing when no process is using the port."""
        result = subprocess.run(
            ["python", "-m", "port_manager.cli", "kill", "9997"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1  # Should return error code for kill commands
        assert "No process found" in result.stdout

    def test_json_output_check(self):
        """Test JSON output for check command."""
        result = subprocess.run(
            ["python", "-m", "port_manager.cli", "check", "9996", "--json"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        import json

        data = json.loads(result.stdout.strip())
        assert "status" in data
        assert data["port"] == 9996
        assert data["status"] == "free"

    def test_missing_port_argument(self):
        """Test that missing port argument shows error."""
        result = subprocess.run(
            ["python", "-m", "port_manager.cli", "check"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1  # Custom error handling
        assert "Port number is required" in result.stdout
