
<h1 align = "center">Hermes⚡</h1>

<div align = "center">

A python based light-weight build system for C/C++, with an emphasis on simplicity and ease of use. The aim is to maintain transparency, but abstract away the tedious parts of building a project.

</div>


## Setup

### Dependencies

Requires python, and `pip` and `pyinstaller` installed. To install `pyinstaller`, run:
```
$ pip install pyinstaller
```

### Installation

*For windows x86_64, direct binaries can be downloaded from [here](https://github.com/StealthyPanda/hermes/releases/tag/v1.1)*

Download this repo as a zip file or clone it to you machine. In the main project directory, run:
```
$ pyinstaller hermes.py
```
or
```
$ python -m pyinstaller hermes.py
```
Next, add the generated `dist/hermes` folder to the system's `PATH` environment variable. Hermes is now set up.


# Usage

Any project can be turned into a hermes project by creating a single `hermes.json` JSON file in the root folder of the project. This file is the single source of controlling the build system, and contains all the build information.

In the root folder of the project, open a terminal and run:
```
$ hermes
```
or simply create an empty `hermes.json` file. To build the project, simply run `hermes` in terminal.
<br>
<br>

The JSON file controls the following (and only) settings for building the project:

- `"compiler"` : The compiler used for building; defaults to `c++` (not included) or uses the full path provided to compiler binary.
- `"inputs"` : Input files for the project; list of paths to the `.cpp` files. Can be absolute or relative paths, and to include all files in a folder use `"folderpath/*"` syntax; this contains all `.cpp` files both internal and external to the project directory.
- `"includes"` : List of all the include files' folder paths; syntax follows that of `"inputs"`; this contains header files outside of your project directory.
- `"output"` : Output file name; defaults to `*first_input_file_name*_output.exe`
- `"run"` : Optional setting, if set `true` the build output is automatically launched after building; defaults to `false`
- `"flags"` : List of any additional flags; these flags are added to the final compiler command as is.

Finally, to get verbose output, run:

```
$ hermes -v (for verbose) | -vv (for super verbose)
```
and see the final compiler command.

Hermes also has a global config file, which is stored at `C:\hermes` or `/etc/hermes`. To interact with this file through the terminal, use:
```
$ hermes global <operation> <key> <value>
```
where

- operations:
    - `change` - changes value at `key` to given `value`
    - `append` - appends the given `value` at `key` (only for lists)
    - `show` - display the current globals config

Note: `show` requires no `key`/`value`, and a `value` of `.` sets it to empty.

### Build optimizations

While these can be added as `flags`, optimizations can also be enabled for a single compilation by running:
```
$ hermes <opt>
```
where `<opt>` can be
- `-b` for O1 level
- `-bb` for O2 level
- `-bbb` for O3 level
- `-saikou` for Ofast level
*Note: Not all these optimization levels are available in all compilers; refer to docs*

<br>
<br>

All input files (`*.c`, `*.cxx` etc) are tracked automatically, and when hermes is called, only files with changes are recompiled to update object files, reducing build times. To force recompilation of all files, use `-redo` to simply update all object files, or `-force` to simple compile the entire application in a single compile command, original style.

<br>
<br>

And that's it! The build system is meant to be as non-opaque as possible, while still automating and speeding up only most tedious part of the building process, while still giving you complete control.


## Authors
[![Foo](https://img.shields.io/badge/Made_with_❤️_by-@stealthypanda🐼-orange?style=for-the-badge&logo=python&link=)](https://sites.google.com/iitj.ac.in/stealthypanda/home)


<br>
<br>


![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)
