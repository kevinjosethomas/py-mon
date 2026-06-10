# Changelog

## Unreleased
- Fixed watch patterns leaking across directories: each `-w` path now only reacts to its own pattern instead of every pattern from every flag.
- Restarts are now debounced (default 250ms, configurable via `--delay` or the `delay` config key, in milliseconds), so editor save bursts cause a single restart. This implements the previously documented `delay` config option.
- `__pycache__`, `.pyc`/`.pyo` files and `.git` internals are ignored by default.
- Watching a nonexistent directory now prints a friendly error and exits instead of dumping a traceback.
- A single watchdog observer is used for all watch paths instead of one thread per path.

## 2.2.0
- Added `--version` / `-V` to print the installed version.
- Added config file support (`.pymonrc`, `pymon.json`).
- Added GitHub Actions CI to run tests on push/PR.
- Expanded docs: config file usage, test instructions.

## 2.1.0
- Refreshed codebase and options (watch/ignore/exec/debug/clean).
- Added colored logging and command input helpers (`rs`, `stop`).

## 2.0.x and earlier
- Initial rewrite with auto-reload for Python scripts and shell commands.

