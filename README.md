
<h1 align = "center">Hermes⚡</h1>

<div align = "center">

A python based light-weight build system for C/C++, with an emphasis on simplicity and ease of use. The aim is to maintain transparency, but abstract away the tedious parts of building a project.

</div>


## Setup

### Dependencies

Requires python, install from [here](https://www.python.org/downloads/).

### Installation

Install using `pip`:
```bash
pip install git+https://github.com/StealthyPanda/hermes.git
```


# Usage

Any project can be turned into a hermes project by creating a single `hermes.json` JSON file in the root folder of the project. This file is the single source of controlling the build system, and contains all the build information.

In the root folder of the project, open a terminal and run:
```bash
hermes init
```
or simply create an empty `hermes.json` file. To build the project, simply run `hermes build` in terminal.
<br>
<br>

The JSON file controls the following (and only) settings for building the project:

- `"name"`: Name of the hermes module.
- `"compiler"` : The compiler used for building; defaults to `clang` (not included) or uses the full path provided to compiler binary.
- `"inputs"` : Input files for the project (all `.c` or `.cpp` files)
    - `"exe"`: files for final executable
    - `"lib"`: files for making static lib
- `"libs"`: names of static libs to include
- `"libdirs"`: dirs to find these libs in
- `"libincdirs"`: dirs to find headers for these libs in
- `"target"`: info for target
    - `"type"`: `"exe"` or `"lib"`
    - `"run"`: `true` or `false`. whether to run the final executable after building
    - `"exeout"`: path for executable output
    - `"libout"`: path for static lib output
    - `"incdirs"`: dirs containing header files when compiling as a static lib
- `"submodules"`: other hermes modules to use in this module. just provide root of the module (containing `hermes.json`). there are 2 ways to do so:
    - `"assrcs"`: modules to include as source. this won't compile submodules as static lib files, and instead treat sources in submodule as part of this module. if unsure, use this method.
    - `"aslibs"`: modules to include as static libs. this will compile submodules as static lib files (respecting their own lib include methods and stuff), and automatically link them in this module.

- `"copts"`: additional compilation options 
- `"lopts"`: additional linker options 

Rule of thumb, if you include anything within "", it is tracked for changes and treated as part of the codebase, and anything within <> is treated as external headers (untracked).

# Building

To build, run 

```bash
hermes build
```

Use `--debug` for debug output, and `--verbose` for verbose.


And that's it! The build system is meant to be as non-opaque as possible, while still automating and speeding up only most tedious part of the building process and giving you complete control.


## Authors
[![Foo](https://img.shields.io/badge/Made_with_❤️_by-@stealthypanda🐼-orange?style=for-the-badge&logo=python&link=)](https://sites.google.com/iitj.ac.in/stealthypanda/home)


<br>
<br>


![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)
