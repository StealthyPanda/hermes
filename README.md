
# Hermes⚡


A python based light-weight build system for C/C++, with an emphasis on simplicity and ease of use. The aim is to maintain transparency, but abstract away the tedious parts of building a project.


<div align = "center">

[![GitHub Stars](https://img.shields.io/github/stars/stealthypanda/hermes.svg)](https://github.com/stealthypanda/hermes/stargazers)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)![GitHub release (latest by date)](https://img.shields.io/github/v/release/stealthypanda/hermes)

</div>

## Setup

### Dependencies

Requires python, and `pip` and `pyinstaller` installed. To install `pyinstaller`, run:
```
$ pip install pyinstaller
```

### Installation
Download this repo as a zip file or clone it to you machine. In the main project directory, run:
```
$ pyinstaller hermes.py
```
or
```
$ python -m pyinstaller hermes.py
```
Next, add the generated dist/hemes folder to the system's `PATH` environment variable. Hermes is now set up.


# Usage

Any project can be turned into a hermes project by creating a single `hermes.json` JSON file in the root folder of the project. This file is the single source of controlling the build system, and contains all the build information.

In the root folder of the project, open a terminal and run:
```
$ hermes
```
or simply create an empty `hermes.json` file. To build the project, simply run `hermes` in terminal.
<br>
<br>

The JSON file the following (and only) settings for building the project:

- `"compiler"` : The compiler used for building; defaults to `g++` (not included) or uses the full path provided to compiler binary.
- `"inputs"` : Input files for the project; list of paths to the `.cpp` files. Can be absolute or relative paths, and to include all files in a folder use `"folderpath/*"` syntax.
- `"includes"` : List of all the include files; syntax follows that of `"inputs"`
- `"output"` : Output file name; defaults to `*first_input_file_name*_output.exe`
- `"run"` : Optional setting, if set `true` the build output is automatically launched after building; defaults to `false`
- `"flags"` : List of any additional flags; these flags are added to the final compiler command as is.

Finally, to get verbose output, run:

```
$ hermes -v
```
and see the final compiler command.
<br>
<br>

And that's it! The build system is meant to be as non-opaque as possible, while still automating and speeding up only most tedious part of the building process, while still giving you complete control.



<br>
<br>

[![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)