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
import shapeio


def test_is_compressed_uncompressed_shape(global_storage):
    shape_path = global_storage["shape_path"]
    is_compressed = shapeio.is_compressed(shape_path)
    assert not is_compressed


def test_is_compressed_compressed_shape(global_storage):
    shape_compressed_path = global_storage["shape_compressed_path"]
    is_compressed = shapeio.is_compressed(shape_compressed_path)
    assert is_compressed


def test_is_compressed_uncompressed_notashape(global_storage):
    notashape_path = global_storage["notashape_path"]
    is_compressed = shapeio.is_compressed(notashape_path)
    assert not is_compressed


def test_is_compressed_compressed_notashape(global_storage):
    notashape_compressed_path = global_storage["notashape_compressed_path"]
    is_compressed = shapeio.is_compressed(notashape_compressed_path)
    assert is_compressed


def test_is_compressed_emptyfile(global_storage):
    empty_path = global_storage["empty_path"]
    is_compressed = shapeio.is_compressed(empty_path)
    assert is_compressed is None


def test_is_shape_uncompressed_shape(global_storage):
    shape_path = global_storage["shape_path"]
    is_shape = shapeio.is_shape(shape_path)
    assert is_shape


def test_is_shape_compressed_shape(global_storage):
    shape_compressed_path = global_storage["shape_compressed_path"]
    is_shape = shapeio.is_shape(shape_compressed_path)
    assert is_shape


def test_is_shape_uncompressed_notashape(global_storage):
    notashape_path = global_storage["notashape_path"]
    is_shape = shapeio.is_shape(notashape_path)
    assert not is_shape


def test_is_shape_compressed_notashape(global_storage):
    notashape_compressed_path = global_storage["notashape_compressed_path"]
    is_shape = shapeio.is_shape(notashape_compressed_path)
    assert not is_shape


def test_is_shape_emptyfile(global_storage):
    empty_path = global_storage["empty_path"]
    is_shape = shapeio.is_shape(empty_path)
    assert not is_shape