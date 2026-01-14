# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-01-14

### Added
- **Force-Kill Timing Fix**: Resolved race condition between process termination and port verification
- **Progress Indicators**: Added visual progress indicators for long-running port release checks
- **Configurable Timeouts**: Added command-line options to configure timeout values:
  - `--kill-timeout`: Timeout for graceful process termination
  - `--force-kill-timeout`: Timeout for force process termination
  - `--port-wait-timeout`: Maximum time to wait for port release
  - `--port-check-interval`: Time between port availability checks
- **Enhanced Error Messages**: Improved error messages to be more actionable and user-friendly
- **Process Existence Validation**: Added validation to ensure processes still exist before attempting operations
- **Comprehensive Test Suite**: Added functional tests with psutil mocking for reliable testing
- **Input Validation**: Added proper port number validation (range 1-65535)
- **Troubleshooting Documentation**: Added comprehensive troubleshooting section in README

### Changed
- **Code Refactoring**: Broke down large main() function into smaller, single-responsibility functions
- **Exit Code Logic**: Improved exit codes to better reflect operation success/failure
- **JSON Output**: Clean JSON output without ANSI color codes or warnings
- **Constants**: Replaced magic numbers with named constants

### Fixed
- **Test Suite**: Fixed broken test paths and added comprehensive test coverage
- **Version Flag**: Fixed `--version` flag to work without requiring command argument
- **Deprecation Warning**: Addressed psutil `connections()` deprecation warning

### Technical Improvements
- **Reliability**: Enhanced error handling and edge case management
- **Maintainability**: Improved code structure and documentation
- **User Experience**: Better feedback and progress indication
- **Testing**: Added integration tests for CLI workflows

## [1.0.0] - 2025-01-14

### Added
- Initial release of port-manager CLI tool
- Basic functionality: check, kill, and kill-force commands
- Process discovery by port number
- Graceful and forceful process termination
- JSON output support
- Basic test suite
- Man page documentation

### Features
- Find processes listening on specific TCP ports
- Terminate processes gracefully (SIGTERM) or forcefully (SIGKILL)
- Cross-platform support (Linux, macOS)
- Permission checking and sudo recommendations</content>
<parameter name="filePath">/mnt/storage/home/universal/Programs/port-manager/CHANGELOG.md