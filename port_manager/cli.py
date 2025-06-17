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

# ─── Core Logic ────────────────────────────────────────────────
def find_process_on_port(port: int) -> Optional[psutil.Process]:
    """Return process listening on given port, or None."""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.connections(kind='inet'):
                if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None

def kill_process_by_pid(pid: int, force: bool = False) -> bool:
    """Kill process by PID. Returns True if successful."""
    try:
        proc = psutil.Process(pid)
        print(f"{YELLOW}🔍 Attempting to {'forcefully' if force else 'gracefully'} terminate PID {pid} ({proc.name()}){RESET}")
        proc.kill() if force else proc.terminate()
        proc.wait(timeout=5)
        print(f"{GREEN}✅ Process {pid} terminated successfully.{RESET}")
        return True
    except psutil.TimeoutExpired:
        if not force:
            print(f"{YELLOW}⚠️ Graceful termination failed. Retrying forcefully...{RESET}")
            return kill_process_by_pid(pid, force=True)
        print(f"{RED}❌ Process {pid} did not terminate.{RESET}")
        return False
    except psutil.NoSuchProcess:
        print(f"{RED}❌ No process with PID {pid} found.{RESET}")
        return False
    except psutil.AccessDenied:
        print(f"{RED}🚫 Access denied to terminate PID {pid}. Use sudo.{RESET}")
        return False
    except Exception as e:
        print(f"{RED}❌ Unexpected error: {e}{RESET}")
        return False

# ─── CLI Interface ─────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(
        description="🛠️  Manage processes on specific ports.",
        epilog="Example: ./port_manager.py check 8000"
    )
    parser.add_argument("command", choices=["check", "kill", "kill-force"], help="Command to run")
    parser.add_argument("port", nargs="?", type=int, help="Port number")
    parser.add_argument("-j", "--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--version", action="store_true", help="Show version info and exit")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")

    return parser.parse_args()

def main():
    args = parse_args()

    if args.version:
        print(f"Port Manager CLI v{TOOL_VERSION}")
        sys.exit(0)

    if args.port is None:
        print(f"{RED}❌ Port number is required.{RESET}")
        sys.exit(1)

    port = args.port
    command = args.command

    result = {
        "command": command,
        "port": port,
        "status": None,
        "process": None,
    }

    proc = find_process_on_port(port)

    if command == "check":
        if proc:
            result["status"] = "in_use"
            result["process"] = {"pid": proc.pid, "name": proc.name()}
            msg = f"{GREEN}✅ Port {port} is in use by PID {proc.pid} ({proc.name()}){RESET}"
        else:
            result["status"] = "free"
            msg = f"{BLUE}✅ Port {port} is free.{RESET}"

    elif command in ["kill", "kill-force"]:
        if proc:
            result["process"] = {"pid": proc.pid, "name": proc.name()}
            success = kill_process_by_pid(proc.pid, force=(command == "kill-force"))
            result["status"] = "terminated" if success else "failed"
            proc_check = find_process_on_port(port)
            if not proc_check:
                msg = f"{GREEN}✅ Port {port} is now free.{RESET}"
            else:
                msg = f"{RED}❌ Port {port} is still in use.{RESET}"
        else:
            result["status"] = "not_found"
            msg = f"{RED}❌ No process found using port {port}.{RESET}"

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(msg)

    sys.exit(0 if result["status"] in ["free", "terminated", "in_use", "not_found"] else 1)

# ─── Entrypoint ────────────────────────────────────────────────
if __name__ == "__main__":
    if os.name == "posix" and os.geteuid() != 0:
        print(f"{YELLOW}⚠️  Run as root or use sudo for full access to ports and processes.{RESET}")
    main()
