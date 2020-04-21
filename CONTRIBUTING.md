# Contributing

## Obtaining the code

To edit the source code, you need to install [Python 3.6](https://www.python.org/downloads/) or newer.

After setting it up, clone the project by doing

    git clone https://github.com/Bentroen/NewNoteBlockStudio.git

or by using your preferred Git tool.

It's **highly** recommended that you work inside a virtual environment. This way your Python installation will be isolated in a self-contained environment which won't interfere with other packages you have installed.
Python 3.3+ offers a native way to create one out of the box with [venv](https://docs.python.org/3/library/venv.html). Navigate to the project's root folder and run:

    python3 -m venv <name>

(or, alternatively, you can use `virtualenv` or other external packages.)

After that, just activate the newly created environment by running:
* Windows: `<name>\Scripts\activate`
* Mac/Linux: `source <name>/bin/activate`

Once in the virtual environment, install the project dependencies:

    pip install -r requirements.txt

At this point you can already test if everything is working by running:

    python3 main.py
    
If you see a beautiful window pop up in your screen, everything is working as expected.

You're good to go! Now it is a good idea to set up your IDE to make it easier to work with the files. Set `main.py` as the entry point for the application.

# Installing Qt Designer

Some parts of the application are created with [Qt Designer](https://doc.qt.io/qt-5/qtdesigner-manual.html), a visual GUI creation tool that's included in the Qt framework. PyQt, however, doesn't include it. So, in order to edit `.ui` files you need to obtain Qt Designer, through either:
1. [pyqt5-tools](https://pypi.org/project/pyqt5-tools/)
1. this unofficial [standalone executable](https://build-system.fman.io/qt-designer-download)

## Code style

## Building

The project uses [PyInstaller](https://www.pyinstaller.org/) as a packaging tool. You should have obtained it from installing the project dependencies.
