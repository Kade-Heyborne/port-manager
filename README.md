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

You can install the CLI using `pip` directly from the source:

```bash
pip install .
```

Or, for development:

```bash
pip install .[dev]
```

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
>
> ```bash
> sudo port-manager kill 8000
> ```

---

## 🧪 Running Tests

Install test dependencies and run `pytest`:

```bash
pip install .[test]
pytest
```

---

## 🧰 Development Setup

To get started with development:

```bash
git clone https://github.com/Kade-Heyborne/port-manager.git
cd port-manager
pip install .[dev]
```

You can now use the CLI locally:

```bash
python -m port_manager.cli check 8000
```

Or install as an editable CLI tool:

```bash
pip install -e .[dev]
port-manager check 8000
```

---

## 📄 Manpage

### Installing the manpage

To install the manpage system-wide (Linux):

```bash
sudo install -Dm644 man/port-manager.1 /usr/share/man/man1/port-manager.1
sudo mandb
```

You can view the CLI manual with:

```bash
man port-manager
```

---

## 🙋 Contributing

Contributions are welcome! Please ensure your code passes linting and tests before submitting a PR.

---

## 📜 License

MIT License.
