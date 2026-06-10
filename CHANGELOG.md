# Changelog

## Unreleased
- Fixed crash (`EOFError`) when running with stdin closed (CI, process managers); pymon now keeps watching with command input disabled.
- Fixed `-x` (exec mode) leaving the shell's child processes running after stop/restart; the whole process group is now terminated.
- Fixed zombie (defunct) processes accumulating on every restart; pymon now waits for the old process to exit (and force-kills it after 5s) before starting a new one.
- pymon now handles `SIGTERM` (sent by `kill` and process managers) like Ctrl+C, cleaning up the child process instead of orphaning it.
- Migrated packaging from `setup.py` to `pyproject.toml`; the version is now single-sourced from `pymon.__version__`.
- Declared `requires-python >= 3.9` (the code uses syntax unavailable before 3.9; the previous `>=3.6` claim was incorrect).
- CI now tests Python 3.9 through 3.13.

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

