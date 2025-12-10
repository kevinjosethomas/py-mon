# py-mon [![](https://img.shields.io/pypi/v/py-mon?color=3776AB&logo=python&style=for-the-badge)](https://pypi.org/project/py-mon/) [![](https://img.shields.io/pypi/dm/py-mon?color=3776AB&logo=python&style=for-the-badge)](https://pypi.org/project/py-mon/)
A modern, easy-to-use package to automatically restart a Python application when file changes are detected!

## Quickstart
I wanted to make this package as easy as possible to use. Here's a quick start, it's all you'll need 😼

### Installation
```
pip install -U py-mon
```
### Execution
```
pymon filename.py
```

That's pretty much it! 😌 

If you have a more sophisticated use-case, here are the available command line options:
- `--watch` (`-w`) to specify paths or patterns to watch. Examples: `src/*.py`, `data/**/*.json`. Default: `*.py`
- `--ignore` (`-i`) to specify patterns of files/paths to ignore. Use once for each pattern.
- `--exec` (`-x`) to execute a shell command instead of running a Python file.
- `--debug` (`-d`) to log detected file changes to the terminal.
- `--clean` (`-c`) to run pymon in clean mode (no logs, no commands).

#### Examples:
- `pymon test.py -w "*.json"` will monitor changes in Python (default) and JSON files in the current directory
- `pymon test.py -w "src/*.py" -w "data/*.json"` will monitor Python files in the src directory and JSON files in the data directory
- `pymon test.py -i "*.log" -i "*__pycache__*"` will ignore changes in log files and __pycache__ directories
- `pymon "python3 -m http.server" -x` will run the server and restart it when files change
- `pymon "npm run dev" -x -w "src/*.js" -w "src/*.jsx"` will run a Node.js dev server and monitor JavaScript files

### Command Input
When running pymon, you can use these commands:
- Type `rs` to manually restart the process
- Type `stop` to terminate pymon

### Config File
You can create a `.pymonrc` or `pymon.json` file in your project root to define default settings:

```json
{
  "watch": ["*.py", "config/*.yaml"],
  "ignore": ["*__pycache__*", "*.log"],
  "debug": false,
  "clean": false,
  "exec": false
}
```

Command line arguments will always override config file settings.

### Tests
Run the test suite locally with pytest:
```
pip install -e ".[dev]"
pytest
```

Anyway that's basically it! Thanks for everything, I would appreciate it if you could leave a follow or star this repository ❣️ If you have any feature requests, read below!

## Contributing
This package is open source so anyone with adequate Python experience can contribute to this project!

### Report Issues
If you find any issues with the package or in the code, please [create an issue and report it here](https://github.com/kevinjosethomas/py-mon/issues)!

### Fix/Edit Content
If you want to contribute to this package, fork the repository, clone it, make your changes and then [proceed to create a pull request here](https://github.com/kevinjosethomas/py-mon/pulls)

## Inspiration
Back when I was 13, I spent a lot of time developing discord bots and it was a hassle to constantly `Ctrl+C` and then run the bot again on my terminal. Since I had just gotten started with web development back then, I decided to make something like  [nodemon](https://github.com/remy/nodemon) but for Python so I randomly created this package one evening! I looked back at it a few weeks ago (I'm now 16) and realized over a thousand people download it every month so I quickly rewrote it (v2) to clean it up and add some new features!

![](https://media1.tenor.com/images/5d6cd0c6b0a0ae3c193e766fb8f1ed1f/tenor.gif?itemid=14057131)
