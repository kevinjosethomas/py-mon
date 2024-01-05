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

If you have a more sophisticated use-case, there are three other arguments you can utilize:
- ``--patterns`` (``-p``) to specify what file patterns to monitor. default: ``*.py``
- ``--watch`` (``-w``) to specify what directory to monitor for changes. default: ``.``
- ``--args`` (``-a``) to pass arguments to the execute script.

#### Examples:
- ``pymon test.py -p "*.json"`` will monitor changes in python and json files
- ``pymon test.py -p "*.json" -w "./data"`` will only monitor changes in python and json files within the ``data`` directory
- ``pymon test.py --args "dev mode"`` will essentially run the program ``python3 test.py dev mode``


Anyway thats basically it! Thanks for everything, I would appreciate it if you could leave a follow or star this repository ❣️ If you have any feature requests, read below!

## Contributing
This package is open source so anyone with adequate Python experience can contribute to this project!

### Report Issues
If you find any issues with the package or in the code, please [create an issue and report it here](https://github.com/kevinjosethomas/py-mon/issues)!

### Fix/Edit Content
If you want to contribute to this package, fork the repository, clone it, make your changes and then [proceed to create a pull request here](https://github.com/kevinjosethomas/py-mon/pulls)

## Inspiration
Back when I was 13, I spent a lot of time developing discord bots and it was a hassle to constantly ``Ctrl+C`` and then run the bot again on my terminal. Since I had just gotten started with web development back then, I decided to make something like  [nodemon](https://github.com/remy/nodemon) but for Python so I randomly created this package one evening! I looked back at it a few weeks ago (I'm now 16) and realized over a thousand people download it every month so I quickly rewrote it (v2) to clean it up and add some new features!

![](https://media1.tenor.com/images/5d6cd0c6b0a0ae3c193e766fb8f1ed1f/tenor.gif?itemid=14057131)
