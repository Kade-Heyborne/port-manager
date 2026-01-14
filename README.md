# 🛠️ Port Manager

A simple and powerful command-line tool to inspect and kill processes listening on specific ports. Built with `psutil` and packaged as a modern Python CLI tool.

---

## 🚀 Features

- ✅ Check which process is using a given port
- 🧯 Gracefully or forcefully kill the process
- 🔐 Permission warning if not run as root on POSIX systems
- 🧪 Tested with `pytest`

---

## 📦 Installation

### Install from PyPI (when available)
```bash
pip install port-manager
```

### Build and Install from Source
```bash
# Clone the repository
git clone https://github.com/Kade-Heyborne/port-manager.git
cd port-manager

# Install with all development dependencies (recommended)
make install-dev

# Or install just the package
pip install .
```

For development installations:
```bash
pip install -e .[dev]
```

---

## 🔨 Building

The project uses Python's modern build system. To build the package:

```bash
python -m build
```

This will create distributable packages in the `dist/` directory.

---

## 🔧 Usage

### Basic Command Format
```bash
port-manager <command> <port_number>
```

### Commands
| Command      | Description                                  |
| ------------ | -------------------------------------------- |
| `check`      | Check if a port is in use                    |
| `kill`       | Gracefully terminate the process on the port |
| `kill-force` | Forcefully kill the process on the port      |

### Examples
```bash
# Check if port 8000 is in use
port-manager check 8000

# Gracefully terminate process using port 8000
port-manager kill 8000

# Force kill process using port 8000
port-manager kill-force 8000
```

> ℹ️ On POSIX systems, root privileges may be required to detect or kill certain processes. Use `sudo` when necessary:
> ```bash
> sudo port-manager kill 8000
> ```

---

## 🛠️ Makefile Targets

The project includes a Makefile with useful targets:

| Target         | Description                              |
|----------------|------------------------------------------|
| `install-dev`  | Install package with development deps    |
| `install-man`  | Install the manpage system-wide          |
| `test`         | Run unit tests                           |
| `clean`        | Remove build artifacts                   |

Usage:
```bash
make <target>
```

---

## 📄 Manpage

### Building and Installing
The manpage can be built and installed using the Makefile:
```bash
# Install the manpage system-wide (requires sudo)
make install-man
```

Or manually:
```bash
sudo cp man/port-manager.1 /usr/share/man/man1/
sudo gzip -f /usr/share/man/man1/port-manager.1
sudo mandb
```

View the manual with:
```bash
man port-manager
```

---

## 🧪 Running Tests

Install test dependencies and run `pytest`:
```bash
make install-dev
make test

# Or directly:
pytest
```

---

## 🧰 Development Setup

1. Clone the repository:
```bash
git clone https://github.com/Kade-Heyborne/port-manager.git
cd port-manager
```

2. Set up development environment:
```bash
make install-dev
```

3. Use the CLI locally:
```bash
python -m port_manager.cli check 8000
```

Or install as an editable CLI tool:
```bash
pip install -e .[dev]
port-manager check 8000
```

---

## 🙋 Contributing

Contributions are welcome! Please ensure your code passes linting and tests before submitting a PR.

1. Set up development environment:
```bash
make install-dev
```

2. Run tests:
```bash
make test
```

3. Clean up before submitting:
```bash
make clean
```

---

## 🐛 Troubleshooting

### Common Issues and Solutions

#### Permission Denied Errors
**Error:** `🚫 Access denied to terminate PID XXX. Use sudo.`

**Solution:** Run the command with `sudo`:
```bash
sudo port-manager kill 8080
```

**Why this happens:** The process belongs to another user or requires elevated privileges to terminate.

#### Port Still in Use After Kill
**Error:** Process terminated but port still shows as bound.

**Solution:**
1. Wait a few seconds for the OS to release the port binding
2. Check if another process has taken the port
3. Use `netstat -tlnp | grep :PORT` or `ss -tlnp | grep :PORT` to see current port usage

#### Process Doesn't Respond to SIGKILL
**Error:** `❌ Process XXX did not respond to SIGKILL within Xs.`

**Solution:** This indicates a serious system issue:
1. The process might be in uninterruptible sleep (D state)
2. Check system logs: `dmesg | tail`
3. Try again after a system reboot
4. Check for kernel bugs or hardware issues

#### No Process Found on Port
**Error:** `❌ No process found using port XXX.`

**Solution:**
1. Verify the port number is correct
2. Check if the service is actually running: `ps aux | grep service_name`
3. Use `netstat -tlnp | grep :PORT` to see what's actually listening
4. The port might be bound by the kernel or a different type of socket

#### JSON Output Shows Extra Warnings
**Issue:** JSON output includes ANSI color codes or warning messages.

**Solution:** The tool suppresses warnings when `--json` flag is used. If you still see them, ensure you're using the latest version.

#### Force Kill Takes Longer Than Expected
**Issue:** `kill-force` command seems slow or shows progress indicator.

**Solution:** This is normal behavior. The tool waits up to 3 seconds for the port to be released after killing the process. Use `--port-wait-timeout` to adjust this.

---

## 📜 License

MIT License.