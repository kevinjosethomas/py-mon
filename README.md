# py-mon [![](https://img.shields.io/pypi/v/py-mon?color=3776AB&logo=python&style=for-the-badge)](https://pypi.org/project/py-mon/) [![](https://img.shields.io/pypi/dm/py-mon?color=3776AB&logo=python&style=for-the-badge)](https://pypi.org/project/py-mon/)
A modern, easy-to-use package to automatically restart a Python application when file changes are detected!

## Quickstart (10s)
```bash
pip install -U py-mon
pymon app.py
```
Zero-config reloads for Python files by default. Requires Python 3.9+.

### Why py-mon?
- Works for Python files or any shell command (`-x "npm run dev"`).
- Simple patterns for watch/ignore; sane defaults.
- Clean/quiet mode available when you don’t want prompts.

### Core flags
- `-w / --watch <pattern>`: what to watch (default `*.py`).
- `-i / --ignore <pattern>`: what to ignore.
- `-x / --exec`: run a shell command instead of `python <file>`.
- `-d / --debug`: print changed paths.
- `-c / --clean`: no logs, no stdin commands.

### Command Input
When running pymon, you can use these commands:
- Type `rs` to manually restart the process
- Type `stop` to terminate pymon

### Optional Config File
Put a `.pymonrc` or `pymon.json` in your project root to keep team settings consistent:

```json
{
  "watch": ["*.py", "config/*.yaml"],
  "ignore": ["*__pycache__*", "*.log"],
  "debug": false,
  "clean": false,
  "exec": false,
  "delay": 250
}
```

Command line arguments will always override config file settings.

Anyway that's basically it! Thanks for everything, I would appreciate it if you could leave a follow or star this repository ❣️ If you have any feature requests, read below!

## Contributing
This package is open source so anyone with adequate Python experience can contribute to this project!

### Report Issues
If you find any issues with the package or in the code, please [create an issue and report it here](https://github.com/kevinjosethomas/py-mon/issues)!

### Fix/Edit Content
If you want to contribute to this package, fork the repository, clone it, make your changes and then [proceed to create a pull request here](https://github.com/kevinjosethomas/py-mon/pulls)

### Tests
Run the test suite locally with pytest:
```
pip install -e ".[dev]"
pytest
```