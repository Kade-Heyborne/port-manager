#!/usr/bin/env python3
"""
╭────────────────────────────────────────────────────────────╮
│ 🔧 Port Manager CLI Tool                                   │
│ Author      : Your Name                                    │
│ Description : Check and kill processes bound to a TCP port│
│ Created     : 2025-06-17                                   │
│ Version     : 1.0.0                                        │
╰────────────────────────────────────────────────────────────╯
"""

import os
import sys
import json
import time
import psutil
import argparse
from typing import Optional

# ─── Terminal Colors ───────────────────────────────────────────
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"

# ─── Version ───────────────────────────────────────────────────
TOOL_VERSION = "1.0.0"

# ─── Default Constants ────────────────────────────────────────────
DEFAULT_GRACEFUL_TIMEOUT = 5.0
DEFAULT_FORCE_TIMEOUT = 1.0
DEFAULT_PORT_WAIT_TIMEOUT = 3.0
DEFAULT_PORT_CHECK_INTERVAL = 0.1


# ─── Core Logic ────────────────────────────────────────────────
def find_process_on_port(port: int) -> Optional[psutil.Process]:
    """Find the process that is listening on a given TCP port.

    This function iterates through all running processes and checks their network
    connections to find which process (if any) is listening on the specified port.

    Args:
        port: The TCP port number to search for (1-65535).

    Returns:
        The psutil.Process object for the process listening on the port,
        or None if no process is found listening on that port.

    Raises:
        This function handles internal psutil exceptions gracefully and continues
        searching other processes. It does not raise exceptions to the caller.
    """
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            for conn in proc.connections(kind="inet"):
                if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None


def wait_for_port_release(
    port: int,
    max_wait: float = DEFAULT_PORT_WAIT_TIMEOUT,
    check_interval: float = DEFAULT_PORT_CHECK_INTERVAL,
) -> bool:
    """Wait for a port to be released after process termination.

    Args:
        port: Port number to check
        max_wait: Maximum time to wait in seconds
        check_interval: Time between checks in seconds

    Returns:
        True if port becomes free, False if timeout
    """
    import sys

    start_time = time.time()
    check_count = 0

    print(
        f"{YELLOW}⏳ Waiting for port {port} to be released...{RESET}",
        end="",
        flush=True,
    )

    while time.time() - start_time < max_wait:
        if not find_process_on_port(port):
            print(f"{GREEN} ✓{RESET}")
            return True

        # Show progress indicator every few checks
        check_count += 1
        if check_count % 5 == 0:
            print(".", end="", flush=True)

        time.sleep(check_interval)

    print(f"{RED} ✗{RESET}")
    return False


def kill_process_by_pid(
    pid: int,
    force: bool = False,
    graceful_timeout: float = DEFAULT_GRACEFUL_TIMEOUT,
    force_timeout: float = DEFAULT_FORCE_TIMEOUT,
) -> bool:
    """Terminate a process by its PID using graceful or force methods.

    This function attempts to terminate a process, first using SIGTERM (graceful)
    and then SIGKILL (force) if the graceful method fails or times out.

    Args:
        pid: Process ID of the process to terminate.
        force: If True, use SIGKILL immediately instead of trying graceful termination first.
        graceful_timeout: Time to wait for graceful termination (SIGTERM) in seconds.
        force_timeout: Time to wait for force termination (SIGKILL) in seconds.

    Returns:
        True if the process was successfully terminated within the timeout periods,
        False if termination failed or timed out.

    Note:
        This function prints status messages to stdout/stderr during operation.
        For force=True, a timeout usually indicates a serious system issue.
    """
    # Use appropriate timeout based on kill type
    timeout = force_timeout if force else graceful_timeout

    try:
        proc = psutil.Process(pid)
        print(
            f"{YELLOW}🔍 Attempting to {'forcefully' if force else 'gracefully'} terminate PID {pid} ({proc.name()}){RESET}"
        )
        proc.kill() if force else proc.terminate()
        proc.wait(timeout=timeout)

        print(f"{GREEN}✅ Process {pid} terminated successfully.{RESET}")
        return True
    except psutil.TimeoutExpired:
        if not force:
            print(
                f"{YELLOW}⚠️ Graceful termination failed. Retrying forcefully...{RESET}"
            )
            return kill_process_by_pid(
                pid,
                force=True,
                graceful_timeout=graceful_timeout,
                force_timeout=force_timeout,
            )
        print(
            f"{RED}❌ Process {pid} did not respond to SIGKILL within {timeout}s. This may indicate a system issue or zombie process.{RESET}"
        )
        return False
    except psutil.NoSuchProcess:
        print(
            f"{RED}❌ No process with PID {pid} found. The process may have already exited.{RESET}"
        )
        return False
    except psutil.AccessDenied:
        print(
            f"{RED}🚫 Access denied to terminate PID {pid}. Try running with sudo: 'sudo port-manager kill-force {pid}'{RESET}"
        )
        return False
    except Exception as e:
        print(
            f"{RED}❌ Unexpected error while terminating process {pid}: {e}. Try using 'ps aux | grep {pid}' to check process status.{RESET}"
        )
        return False
    except psutil.NoSuchProcess:
        print(
            f"{RED}❌ No process with PID {pid} found. The process may have already exited.{RESET}"
        )
        return False
    except psutil.AccessDenied:
        print(
            f"{RED}🚫 Access denied to terminate PID {pid}. Try running with sudo: 'sudo port-manager kill-force {pid}'{RESET}"
        )
        return False
    except Exception as e:
        print(
            f"{RED}❌ Unexpected error while terminating process {pid}: {e}. Try using 'ps aux | grep {pid}' to check process status.{RESET}"
        )
        return False
    except psutil.NoSuchProcess:
        print(
            f"{RED}❌ No process with PID {pid} found. The process may have already exited.{RESET}"
        )
        return False
    except psutil.AccessDenied:
        print(
            f"{RED}🚫 Access denied to terminate PID {pid}. Try running with sudo: 'sudo port-manager kill-force {pid}'{RESET}"
        )
        return False
    except Exception as e:
        print(
            f"{RED}❌ Unexpected error while terminating process {pid}: {e}. Try using 'ps aux | grep {pid}' to check process status.{RESET}"
        )
        return False


# ─── CLI Interface ─────────────────────────────────────────────
def handle_check_command(port: int, proc: Optional[psutil.Process]) -> tuple[dict, str]:
    """Handle the check command logic.

    Returns:
        tuple: (result_dict, message_string)
    """
    result = {
        "command": "check",
        "port": port,
        "status": None,
        "process": None,
    }

    if proc:
        result["status"] = "in_use"
        result["process"] = {"pid": proc.pid, "name": proc.name()}
        msg = (
            f"{GREEN}✅ Port {port} is in use by PID {proc.pid} ({proc.name()}){RESET}"
        )
    else:
        result["status"] = "free"
        msg = f"{BLUE}✅ Port {port} is free.{RESET}"

    return result, msg


def handle_kill_command(
    port: int,
    proc: Optional[psutil.Process],
    force: bool,
    graceful_timeout: float = DEFAULT_GRACEFUL_TIMEOUT,
    force_timeout: float = DEFAULT_FORCE_TIMEOUT,
    port_wait_timeout: float = DEFAULT_PORT_WAIT_TIMEOUT,
    port_check_interval: float = DEFAULT_PORT_CHECK_INTERVAL,
) -> tuple[dict, str]:
    """Handle kill/kill-force command logic.

    Returns:
        tuple: (result_dict, message_string)
    """
    command = "kill-force" if force else "kill"
    result = {
        "command": command,
        "port": port,
        "status": None,
        "process": None,
    }

    if proc:
        # Double-check that the process still exists before attempting to kill it
        try:
            # This will raise NoSuchProcess if the process no longer exists
            proc.status()  # Quick check that process is still accessible
        except psutil.NoSuchProcess:
            result["status"] = "process_already_exited"
            msg = f"{YELLOW}⚠️ Process {proc.pid} ({proc.name()}) has already exited.{RESET}"
            return result, msg

        result["process"] = {"pid": proc.pid, "name": proc.name()}
        success = kill_process_by_pid(
            proc.pid,
            force=force,
            graceful_timeout=graceful_timeout,
            force_timeout=force_timeout,
        )
        # Always check if port becomes free, regardless of process termination status
        port_freed = wait_for_port_release(
            port, max_wait=port_wait_timeout, check_interval=port_check_interval
        )

        if success and port_freed:
            result["status"] = "terminated"
            msg = f"{GREEN}✅ Process {proc.pid} terminated successfully and port {port} is now free.{RESET}"
        elif success and not port_freed:
            result["status"] = "process_terminated_port_still_bound"
            msg = f"{YELLOW}⚠️ Process {proc.pid} terminated but port {port} is still bound (may take a moment to release).{RESET}"
        elif not success and port_freed:
            result["status"] = "terminated_with_warnings"
            msg = f"{YELLOW}⚠️ Process {proc.pid} may have terminated despite timeout, and port {port} is now free.{RESET}"
        else:
            result["status"] = "failed"
            msg = f"{RED}❌ Failed to terminate process {proc.pid} ({proc.name()}) and port {port} is still in use. Try with 'kill-force' or check process permissions.{RESET}"
    else:
        result["status"] = "not_found"
        msg = f"{RED}❌ No process found using port {port}. The port may already be free.{RESET}"

    return result, msg


def output_result(result: dict, message: str, json_output: bool) -> int:
    """Output the result and return appropriate exit code.

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    if json_output:
        print(json.dumps(result, indent=2))
    else:
        print(message)

    # Exit codes: 0 for success, 1 for errors
    status = result["status"]
    command = result["command"]
    if status in ["free", "terminated", "in_use", "process_already_exited"]:
        return 0
    elif status == "not_found":
        # For kill commands, not finding a process is an error
        return 1 if command in ["kill", "kill-force"] else 0
    else:
        return 1


def validate_port(value: str) -> int:
    """Validate and convert a port number string to integer.

    This function is used as an argparse type converter to ensure port numbers
    are valid TCP/UDP port numbers (1-65535).

    Args:
        value: String representation of the port number.

    Returns:
        Integer representation of the validated port number.

    Raises:
        argparse.ArgumentTypeError: If the value is not a valid port number
            (not numeric, or outside the range 1-65535).
    """
    try:
        port = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Port must be a number, got '{value}'")

    if not (1 <= port <= 65535):
        raise argparse.ArgumentTypeError(
            f"Port must be between 1 and 65535, got {port}"
        )

    return port


def parse_args():
    parser = argparse.ArgumentParser(
        description="🛠️  Manage processes on specific ports.",
        epilog="Example: ./port_manager.py check 8000",
    )
    parser.add_argument(
        "command", choices=["check", "kill", "kill-force"], help="Command to run"
    )
    parser.add_argument(
        "port", nargs="?", type=validate_port, help="Port number (1-65535)"
    )
    parser.add_argument(
        "-j", "--json", action="store_true", help="Output results as JSON"
    )
    parser.add_argument(
        "--version", action="store_true", help="Show version info and exit"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug output"
    )
    parser.add_argument(
        "--kill-timeout",
        type=float,
        default=DEFAULT_GRACEFUL_TIMEOUT,
        help=f"Timeout for graceful process termination in seconds (default: {DEFAULT_GRACEFUL_TIMEOUT})",
    )
    parser.add_argument(
        "--force-kill-timeout",
        type=float,
        default=DEFAULT_FORCE_TIMEOUT,
        help=f"Timeout for force process termination in seconds (default: {DEFAULT_FORCE_TIMEOUT})",
    )
    parser.add_argument(
        "--port-wait-timeout",
        type=float,
        default=DEFAULT_PORT_WAIT_TIMEOUT,
        help=f"Maximum time to wait for port release in seconds (default: {DEFAULT_PORT_WAIT_TIMEOUT})",
    )
    parser.add_argument(
        "--port-check-interval",
        type=float,
        default=DEFAULT_PORT_CHECK_INTERVAL,
        help=f"Time between port availability checks in seconds (default: {DEFAULT_PORT_CHECK_INTERVAL})",
    )

    return parser.parse_args()


def main():
    # Quick check for --version before full argument parsing
    if "--version" in sys.argv:
        print(f"Port Manager CLI v{TOOL_VERSION}")
        sys.exit(0)

    args = parse_args()

    if args.port is None:
        print(
            f"{RED}❌ Port number is required. Usage: port-manager <command> <port>{RESET}"
        )
        sys.exit(1)

    port = args.port
    command = args.command

    # Find the process using the port
    proc = find_process_on_port(port)

    # Handle the command
    if command == "check":
        result, message = handle_check_command(port, proc)
    elif command in ["kill", "kill-force"]:
        result, message = handle_kill_command(
            port,
            proc,
            force=(command == "kill-force"),
            graceful_timeout=args.kill_timeout,
            force_timeout=args.force_kill_timeout,
            port_wait_timeout=args.port_wait_timeout,
            port_check_interval=args.port_check_interval,
        )
    else:
        # This should never happen due to argparse choices, but just in case
        result = {
            "command": command,
            "port": port,
            "status": "error",
            "process": None,
        }
        message = f"{RED}❌ Invalid command: {command}{RESET}"

    # Output result and exit
    exit_code = output_result(result, message, args.json)
    sys.exit(exit_code)


# ─── Entrypoint ────────────────────────────────────────────────
if __name__ == "__main__":
    # Don't show warning for JSON output or version
    show_warning = "--json" not in sys.argv and "--version" not in sys.argv
    if show_warning and os.name == "posix" and os.geteuid() != 0:
        print(
            f"{YELLOW}⚠️  Run as root or use sudo for full access to ports and processes.{RESET}"
        )
    main()
