"""
This file is part of ShapeIO.

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

import os

import shapeio


@pytest.fixture(scope="module")
def global_storage():
    return {
        "shape": "./tests/data/DK10f_A1tPnt5dLft.s",
        "shape_decompressed": "./tests/data/DK10f_A1tPnt5dLft_decompressed.s",
        "shape_compressed": "./tests/data/DK10f_A1tPnt5dLft_compressed.s"
    }


# @pytest.mark.dependency(name="test_shape_compression")
# @pytest.mark.skipif(not os.path.exists("./TK.MSTS.Tokens.dll"), reason="requires TK.MSTS.Tokens.dll to be present in the file system")
# def test_shape_compression(global_storage):
#     shape_filepath = global_storage["shape"]
#     shape_output_filepath = global_storage["shape_compressed"]
#     shapeio.compress(shape_filepath, shape_output_filepath, "./TK.MSTS.Tokens.dll")
#     assert shapeio.is_compressed(shape_output_filepath)


# @pytest.mark.dependency(depends=["test_shape_compression"])
# @pytest.mark.skipif(not os.path.exists("./TK.MSTS.Tokens.dll"), reason="requires TK.MSTS.Tokens.dll to be present in the file system")
# def test_shape_decompression(global_storage):
#     shape_filepath = global_storage["shape_compressed"]
#     shape_output_filepath = global_storage["shape_decompressed"]
#     shapeio.decompress(shape_filepath, shape_output_filepath, "./TK.MSTS.Tokens.dll")
#     assert not shapeio.is_compressed(shape_output_filepath)
