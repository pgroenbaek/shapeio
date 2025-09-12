"""
This file is part of ShapeEdit.

Copyright (C) 2025 Peter Grønbæk Andersen <peter@grnbk.io>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import pytest


def load_shape(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-16-le') as f:
        return f.read()


@pytest.fixture(scope="session")
def global_storage():
    data = {
        "shape_path": "./tests/data/DK10f_A1tPnt5dLft.s",
        "shape_compressed_path": "./tests/data/DK10f_A1tPnt5dLft_compressed.s",
        "notashape_path": "./tests/data/w-005655+015119.w",
        "notashape_compressed_path": "./tests/data/w-005655+015119_compressed.w",
        "empty_path": "./tests/data/empty.txt"
    }
    data["shape"] = load_shape(data["shape_path"])
    return data