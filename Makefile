# Makefile for port-manager

PYTHON := python3
PIP := pip3

PACKAGE := port_manager
MAN := man/port-manager.1
MAN_GZ := /usr/share/man/man1/port-manager.1.gz

.PHONY: help install-dev manpage install-man test clean

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install-dev   Install dev dependencies"
	@echo "  install-man   Install manpage to system"
	@echo "  test          Run unit tests with pytest"
	@echo "  clean         Remove build artifacts"

install-dev:
	$(PIP) install .[dev]

install-man:
	@echo "Installing manpage system-wide..."
	sudo cp $(MAN) /usr/share/man/man1/
	sudo gzip -f /usr/share/man/man1/port-manager.1
	@echo "Done. You can now use 'man port-manager'."

test:
	@echo "Running tests..."
	pytest

clean:
	@echo "Cleaning up build artifacts..."
	rm -rf build dist *.egg-info __pycache__ .pytest_cache .mypy_cache
	find . -type f -name '*.pyc' -delete
