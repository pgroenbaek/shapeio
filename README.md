# shapeio

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/pgroenbaek/shapeio?style=flat&label=Latest%20Version)](https://github.com/pgroenbaek/shapeio/releases)
[![Python 3.6+](https://img.shields.io/badge/Python-3.6%2B-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License GNU GPL v3](https://img.shields.io/badge/License-%20%20GNU%20GPL%20v3%20-lightgrey?style=flat&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA2NDAgNTEyIj4KICA8IS0tIEZvbnQgQXdlc29tZSBGcmVlIDYuNy4yIGJ5IEBmb250YXdlc29tZSAtIGh0dHBzOi8vZm9udGF3ZXNvbWUuY29tIExpY2Vuc2UgLSBodHRwczovL2ZvbnRhd2Vzb21lLmNvbS9saWNlbnNlL2ZyZWUgQ29weXJpZ2h0IDIwMjUgRm9udGljb25zLCBJbmMuIC0tPgogIDxwYXRoIGZpbGw9IndoaXRlIiBkPSJNMzg0IDMybDEyOCAwYzE3LjcgMCAzMiAxNC4zIDMyIDMycy0xNC4zIDMyLTMyIDMyTDM5OC40IDk2Yy01LjIgMjUuOC0yMi45IDQ3LjEtNDYuNCA1Ny4zTDM1MiA0NDhsMTYwIDBjMTcuNyAwIDMyIDE0LjMgMzIgMzJzLTE0LjMgMzItMzIgMzJsLTE5MiAwLTE5MiAwYy0xNy43IDAtMzItMTQuMy0zMi0zMnMxNC4zLTMyIDMyLTMybDE2MCAwIDAtMjk0LjdjLTIzLjUtMTAuMy00MS4yLTMxLjYtNDYuNC01Ny4zTDEyOCA5NmMtMTcuNyAwLTMyLTE0LjMtMzItMzJzMTQuMy0zMiAzMi0zMmwxMjggMGMxNC42LTE5LjQgMzcuOC0zMiA2NC0zMnM0OS40IDEyLjYgNjQgMzJ6bTU1LjYgMjg4bDE0NC45IDBMNTEyIDE5NS44IDQzOS42IDMyMHpNNTEyIDQxNmMtNjIuOSAwLTExNS4yLTM0LTEyNi03OC45Yy0yLjYtMTEgMS0yMi4zIDYuNy0zMi4xbDk1LjItMTYzLjJjNS04LjYgMTQuMi0xMy44IDI0LjEtMTMuOHMxOS4xIDUuMyAyNC4xIDEzLjhsOTUuMiAxNjMuMmM1LjcgOS44IDkuMyAyMS4xIDYuNyAzMi4xQzYyNy4yIDM4MiA1NzQuOSA0MTYgNTEyIDQxNnpNMTI2LjggMTk1LjhMNTQuNCAzMjBsMTQ0LjkgMEwxMjYuOCAxOTUuOHpNLjkgMzM3LjFjLTIuNi0xMSAxLTIyLjMgNi43LTMyLjFsOTUuMi0xNjMuMmM1LTguNiAxNC4yLTEzLjggMjQuMS0xMy44czE5LjEgNS4zIDI0LjEgMTMuOGw5NS4yIDE2My4yYzUuNyA5LjggOS4zIDIxLjEgNi43IDMyLjFDMjQyIDM4MiAxODkuNyA0MTYgMTI2LjggNDE2UzExLjcgMzgyIC45IDMzNy4xeiIvPgo8L3N2Zz4=&logoColor=%23ffffff)](/LICENSE)

This Python module provides functions to decode MSTS/ORTS shape files into Python objects and to encode them back into the shape file format.

The API is very similar to that of the `json` module and includes functions for handling shape compression and decompression.

When modifying shapes using this module, there are no built-in safeguards beyond the structure of the data itself. If you don't know what you're doing, your changes may result in invalid shape files that won't work with Open Rails or MSTS.

List of companion modules:
- [shapeedit](https://github.com/pgroenbaek/shapeedit) - provides a wrapper for modifying the shape data structure safely.
- [trackshape-utils](https://github.com/pgroenbaek/trackshape-utils) - offers additional utilities for working with track shapes.


## Prerequisites

The following platform dependencies are **only required for shape compression and decompression**. Other parts of the module will function correctly without them.

You can skip this section if you compress and decompress shapes manually using other tools, such as *ffeditc\_unicode.exe* through the [Shape File Manager](https://www.trainsim.com/forums/filelib-search-fileid?fid=78928) or the [FFEDIT\_Sub v1.2](https://www.trainsim.com/forums/filelib-search-fileid?fid=40291) utility by Ged Saunders.

This module uses the `TK.MSTS.Tokens.dll` library by Okrasa Ghia to perform shape file compression and decompression. Therefore, a Common Language Runtime (CLR) is required if you wish to compress and decompress shapes programmatically through the module. You can use the Mono runtime on Linux and macOS, or the .NET Framework on Windows.

The `TK.MSTS.Tokens.dll` library is not included with the Python module. It can be downloaded as part of the TK\_Utils package from [the-train.de](https://the-train.de/downloads/entry/9385-tk-utils-updated/). Only the DLL file itself is needed from that package.

See the [Usage section](#compress-or-decompress-a-shape-on-disk) for more details on how to compress and decompress shape files using the module.

Steps to install a CLR on your operating system:

#### Linux

```bash
sudo apt update
sudo apt install mono-complete
```

#### macOS

```bash
brew install mono
```

#### Windows

Download and install the [.NET Framework 4.0 or later](https://dotnet.microsoft.com/en-us/download/dotnet-framework) from Microsoft.

The .NET Framework is typically already installed on most Windows systems.


## Installation

The Python module itself can be installed in the following ways:

### Install from PyPI

```sh
pip install --upgrade shapeio
```

### Install from wheel

If you have downloaded a `.whl` file from the [Releases](https://github.com/pgroenbaek/shapeio/releases) page, install it with:

```sh
pip install path/to/shapeio‑<version>‑py3‑none‑any.whl
```

Replace `<version>` with the actual version number in the filename. For example:

```sh
pip install path/to/shapeio-0.5.0b0-py3-none-any.whl
```

### Install from source

```sh
git clone https://github.com/pgroenbaek/shapeio.git
pip install --upgrade ./shapeio
```

## Usage

### Load a shape from a file

To load a shape from disk, use the `shapeio.load` function. Note that the shape file must be uncompressed beforehand. Otherwise, you will get a `ShapeCompressedError`. See the [Compression section](#compress-or-decompress-a-shape-on-disk) for instructions on how to decompress a shape.

```python
import shapeio

my_shape = shapeio.load("./path/to/example.s")

print(my_shape)
```

### Save a shape to a file

To save a shape to disk, you can use the `shapeio.dump` function. This will serialize the shape object, including any changes made to it, into the structured text format and save it to the specified path.

```python
import shapeio

shapeio.dump(my_shape, "./path/to/output.s")
```

### Serialize a shape to a string

If you want to serialize the object into a string without saving it to a file on disk, you can use `shapeio.dumps`.

```python
import shapeio

shape_string = shapeio.dumps(my_shape)
print(shape_string)
```

### Parse a shape from a string

Similarly, you can use `shapeio.loads` to parse a shape from a string instead of reading it from a file on disk.

```python
import shapeio

shape_text = """
SIMISA@@@@@@@@@@JINX0s1t______

shape (
	shape_header ( 00000000 00000000 )
	volumes ( 12
		vol_sphere (
			vector ( -1.23867 3.5875 40 ) 42.452
		)
		vol_sphere (
			vector ( -1.23867 0.495151 40 ) 40.1839
		)
        ...
"""
shape = shapeio.loads(shape_text)
```

### Check if a shape is compressed on disk

To check whether a shape file on disk is compressed, you can use `shapeio.is_compressed`. This function returns `True` if the shape is compressed and `False` if it is not. If the file is empty, not a shape file, or its state cannot be determined, the function will return `None`.

```python
import shapeio

is_comp = shapeio.is_compressed("./path/to/example.s")
if is_comp is True:
    print("Compressed")
elif is_comp is False:
    print("Uncompressed")
else:
    print("Could not determine (possibly empty file)")
```

### Compress or decompress a shape on disk

The compression and decompression functions in this module use the `TK.MSTS.Tokens.dll` library by Okrasa Ghia. This library is not included with the Python module. You will also need a CLR installed to load this file.

See the [Prerequisites section](#prerequisites) for instructions on how to obtain the `TK.MSTS.Tokens.dll` library and set up a CLR on your operating system.

Alternatively, you can manually compress and decompress shapes using other tools, such as *ffeditc\_unicode.exe* through the [Shape File Manager](https://www.trainsim.com/forums/filelib-search-fileid?fid=78928) or the [FFEDIT\_Sub v1.2](https://www.trainsim.com/forums/filelib-search-fileid?fid=40291) utility by Ged Saunders.

```python
import shapeio

tkutils_dll_path = "./path/to/TK.MSTS.Tokens.dll"

# Compress and decompress in-place.
shapeio.compress(tkutils_dll_path, "./path/to/example.s")
shapeio.decompress(tkutils_dll_path, "./path/to/example.s")

# Compress and decompress to an output file.
shapeio.compress(tkutils_dll_path, "./path/to/example.s", "./path/to/output.s")
shapeio.decompress(tkutils_dll_path, "./path/to/example.s", "./path/to/output.s")
```

### Accessing shape data

The functions that load shapes return a `Shape` object, allowing you to access all the data defined in the shape file.

To explore the full data structure, see [shape.py](/shapeio/shape.py). You can also print the objects to view their attributes.

```python
import shapeio

my_shape = shapeio.load("./path/to/example.s")

# Print the point in index 17.
print(my_shape.points[17])

# Iterate over points, print uv_point in index 10.
for idx, uv_point in enumerate(my_shape.uv_points):
    if idx == 10:
        print(uv_point)
```

### Modifying shape data

You can modify values, add or remove items from lists, and reorder items in the lists. The serialized shape data will reflect any changes you make.

```python
import shapeio
from shapeio import shape

my_shape = shapeio.load("./path/to/example.s")

# Modify an existing point.
my_shape.points[1].x = 17

# Add a new uv_point.
new_uv_point = shape.UVPoint(0.2, 0.5)
my_shape.uv_points.append(new_uv_point)

shapeio.dump(my_shape, "./path/to/output.s")
```

When using this module on its own, there are no built-in safeguards beyond the structure of the data itself to ensure that modifications will result in a shape usable in MSTS or Open Rails. See [shapeedit](https://github.com/pgroenbaek/shapeedit) for a wrapper that allows you to perform complex operations on the data structure safely.

However, the module does ensure that list counts in the serialized data are correct. It also enforces strict type checking during serialization, preventing you from adding items to lists and setting values of attributes that are not of the expected type.

For example, if you attempt to add a `shape.UVPoint` to the `shape.points` list, a TypeError will be raised when you try to serialize the shape.

## Running Tests

You can run tests manually or use `tox` to test across multiple Python versions.

### Run Tests Manually
First, install the required dependencies:

```sh
pip install pytest
pip install pytest-dependency
```

Then, run tests with:

```sh
pytest
```


## Run Tests with `tox`

`tox` allows you to test across multiple Python environments.

### **1. Install `tox`**
```sh
pip install tox
```

### **2. Run Tests**
```sh
tox
```

This will execute tests in all specified Python versions.

### **3. `tox.ini` Configuration**
The `tox.ini` file should be in your project root:

```ini
[tox]
envlist = py36, py37, py38, py39, py310

[testenv]
deps = pytest
commands = pytest
```

Modify `envlist` to match the Python versions you want to support.

## License

This Python module was created by Peter Grønbæk Andersen and is licensed under [GNU GPL v3](/LICENSE).
