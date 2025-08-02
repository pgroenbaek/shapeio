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

from shapeio.shape import (
    UVOpCopy,
    UVOpReflectMapFull,
    UVOpReflectMap,
    UVOpUniformScale,
    UVOpNonUniformScale
)
from shapeio.decoder import _UVOpParser, BlockFormatError
from shapeio.encoder import _UVOpSerializer


@pytest.fixture
def serializer():
    return _UVOpSerializer()


@pytest.fixture
def parser():
    return _UVOpParser()


@pytest.mark.parametrize("text, expected_type, expected_values", [
    ("uv_op_copy ( 1 2 )", UVOpCopy, (1, 2)),
    ("uv_op_reflectmapfull ( 3 )", UVOpReflectMapFull, (3,)),
    ("uv_op_reflectmap ( 4 )", UVOpReflectMap, (4,)),
    ("uv_op_uniformscale ( 5 6 7 8 )", UVOpUniformScale, (5, 6, 7, 8)),
    ("uv_op_nonuniformscale ( 9 10 11 12 )", UVOpNonUniformScale, (9, 10, 11, 12)),
])
def test_parse_uv_op(parser, text, expected_type, expected_values):
    uv_op = parser.parse(text)
    assert isinstance(uv_op, expected_type)
    assert list(vars(uv_op).values()) == list(expected_values)


@pytest.mark.parametrize("uv_op, expected", [
    (UVOpCopy(1, 2), "uv_op_copy ( 1 2 )"),
    (UVOpReflectMapFull(3), "uv_op_reflectmapfull ( 3 )"),
    (UVOpReflectMap(4), "uv_op_reflectmap ( 4 )"),
    (UVOpUniformScale(5, 6, 7, 8), "uv_op_uniformscale ( 5 6 7 8 )"),
    (UVOpNonUniformScale(9, 10, 11, 12), "uv_op_nonuniformscale ( 9 10 11 12 )"),
])
def test_serialize_uv_op(serializer, uv_op, expected):
    result = serializer.serialize(uv_op, depth=0)
    assert result.strip() == expected


@pytest.mark.parametrize("bad_text", [
    "uv_op_copy ( 1 )",  # Too few args
    "uv_op_reflectmapfull ( )",  # No args
    "uv_op_uniformscale ( 1 2 3 )",  # Too few
    "uv_op_unknown ( 1 2 )",  # Unknown op
    "uv_op_copy 1 2",  # Missing parentheses
])
def test_parse_invalid_uv_op_raises(parser, bad_text):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_text)
