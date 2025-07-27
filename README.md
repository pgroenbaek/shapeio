# shapeio

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/pgroenbaek/shapeio?style=flat&label=Latest%20Version)](https://github.com/pgroenbaek/shapeio/releases)
[![Python 3.6+](https://img.shields.io/badge/Python-3.6%2B-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License GNU GPL v3](https://img.shields.io/badge/License-%20%20GNU%20GPL%20v3%20-lightgrey?style=flat&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA2NDAgNTEyIj4KICA8IS0tIEZvbnQgQXdlc29tZSBGcmVlIDYuNy4yIGJ5IEBmb250YXdlc29tZSAtIGh0dHBzOi8vZm9udGF3ZXNvbWUuY29tIExpY2Vuc2UgLSBodHRwczovL2ZvbnRhd2Vzb21lLmNvbS9saWNlbnNlL2ZyZWUgQ29weXJpZ2h0IDIwMjUgRm9udGljb25zLCBJbmMuIC0tPgogIDxwYXRoIGZpbGw9IndoaXRlIiBkPSJNMzg0IDMybDEyOCAwYzE3LjcgMCAzMiAxNC4zIDMyIDMycy0xNC4zIDMyLTMyIDMyTDM5OC40IDk2Yy01LjIgMjUuOC0yMi45IDQ3LjEtNDYuNCA1Ny4zTDM1MiA0NDhsMTYwIDBjMTcuNyAwIDMyIDE0LjMgMzIgMzJzLTE0LjMgMzItMzIgMzJsLTE5MiAwLTE5MiAwYy0xNy43IDAtMzItMTQuMy0zMi0zMnMxNC4zLTMyIDMyLTMybDE2MCAwIDAtMjk0LjdjLTIzLjUtMTAuMy00MS4yLTMxLjYtNDYuNC01Ny4zTDEyOCA5NmMtMTcuNyAwLTMyLTE0LjMtMzItMzJzMTQuMy0zMiAzMi0zMmwxMjggMGMxNC42LTE5LjQgMzcuOC0zMiA2NC0zMnM0OS40IDEyLjYgNjQgMzJ6bTU1LjYgMjg4bDE0NC45IDBMNTEyIDE5NS44IDQzOS42IDMyMHpNNTEyIDQxNmMtNjIuOSAwLTExNS4yLTM0LTEyNi03OC45Yy0yLjYtMTEgMS0yMi4zIDYuNy0zMi4xbDk1LjItMTYzLjJjNS04LjYgMTQuMi0xMy44IDI0LjEtMTMuOHMxOS4xIDUuMyAyNC4xIDEzLjhsOTUuMiAxNjMuMmM1LjcgOS44IDkuMyAyMS4xIDYuNyAzMi4xQzYyNy4yIDM4MiA1NzQuOSA0MTYgNTEyIDQxNnpNMTI2LjggMTk1LjhMNTQuNCAzMjBsMTQ0LjkgMEwxMjYuOCAxOTUuOHpNLjkgMzM3LjFjLTIuNi0xMSAxLTIyLjMgNi43LTMyLjFsOTUuMi0xNjMuMmM1LTguNiAxNC4yLTEzLjggMjQuMS0xMy44czE5LjEgNS4zIDI0LjEgMTMuOGw5NS4yIDE2My4yYzUuNyA5LjggOS4zIDIxLjEgNi43IDMyLjFDMjQyIDM4MiAxODkuNyA0MTYgMTI2LjggNDE2UzExLjcgMzgyIC45IDMzNy4xeiIvPgo8L3N2Zz4=&logoColor=%23ffffff)](/LICENSE)

This Python module provides functions to decode MSTS/ORTS shape files into Python objects and to encode them back into the shape file format.

The API is very similar to that of the `json` module and includes functions for handling shape compression and decompression.

When modifying shapes using this module, there are no safeguards other than the data structure itself. If you don't know what you're doing, your changes may result in invalid shape files that won't work with Open Rails or MSTS.

See also:
- [shapemod](https://github.com/pgroenbaek/shapemod) - provides functions for modifying shapes while keeping them error-free, valid and usable in MSTS/ORTS.
- [trackshape-utils](https://github.com/pgroenbaek/trackshape-utils) - offers additional utilities for working with track shapes.

## Installation

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
```python
import shapeio

with open("./path/to/example.s", "r") as f:
    my_shape = shapeio.load(f)

print(my_shape)
```

### Save a shape to a file

```python
import shapeio

with open("./path/to/output.s", "w") as f:
    shapeio.dump(my_shape, f)
```

### Serialize a shape to a string

```python
import shapeio

shape_string = shapeio.dumps(my_shape)
print(shape_string)
```

### Parse a shape from a string

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

```python
import shapeio

ffeditc_path = "C:/path/to/ffeditc_unicode.exe"

shapeio.compress("./path/to/example.s", ffeditc_path)
shapeio.decompress("./path/to/example.s", ffeditc_path)
```

### Accessing shape data

```python
import shapeio

with open("./path/to/example.s", "r") as f:
    my_shape = shapeio.load(f)

# Print the point in index 17.
print(my_shape.points[17])

# Iterate over points, print point in index 17.
for idx, point in enumerate(my_shape.points):
    if idx == 17:
        print(point)
```

### Modifying shape data

```python
import shapeio
from shapeio import shape

with open("./path/to/example.s", "r") as f:
    my_shape = shapeio.load(f)

# Modify an existing point.
my_shape.points[1].x = 17

# Add a new point.
new_point = shape.Point(0.0, 5.0, 2.2)
my_shape.points.append(new_point)
```

## Running Tests

You can run tests manually or use `tox` to test across multiple Python versions.

### Run Tests Manually
First, install the required dependencies:

```sh
pip install pytest
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

This project was created by Peter Grønbæk Andersen and is licensed under [GNU GPL v3](/LICENSE).
