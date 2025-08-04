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

from shapeio.shape import CullablePrims, Point
from shapeio.decoder import _CullablePrimsParser, BlockFormatError
from shapeio.encoder import _CullablePrimsSerializer


@pytest.fixture
def serializer():
    return _CullablePrimsSerializer()


@pytest.fixture
def parser():
    return _CullablePrimsParser()


def test_serialize_cullable_prims(serializer):
    cullable_prims = CullablePrims(3, 5, 9)
    assert serializer.serialize(cullable_prims) == "cullable_prims ( 3 5 9 )"


def test_parse_cullable_prims(parser):
    text = "cullable_prims ( 3 5 9 )"
    cullable_prims = parser.parse(text)
    assert cullable_prims.num_prims == 3
    assert cullable_prims.num_flat_sections == 5
    assert cullable_prims.num_prim_indices == 9


def test_parse_cullable_prims_with_whitespace(parser):
    text = "  cullable_prims (   10   20   30   ) "
    cullable_prims = parser.parse(text)
    assert cullable_prims.num_prims == 10
    assert cullable_prims.num_flat_sections == 20
    assert cullable_prims.num_prim_indices == 30


@pytest.mark.parametrize("bad_input", [
    "cullable_prims ( 1 2 )",              # Too few numbers
    "cullable_prims ( 1 2 3 4 )",          # Too many numbers
    "cullableprim ( 1 2 3 )",              # Incorrect keyword
    "cullable_prims 1 2 3",                # Missing parentheses
])
def test_parse_invalid_cullable_prims_raises(parser, bad_input):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_input)


@pytest.mark.parametrize("bad_input", [
    Point(1.0, 2.0, 3.0),  # Wrong type
])
def test_serialize_invalid_type_raises(serializer, bad_input):
    with pytest.raises(TypeError):
        serializer.serialize(bad_input)


def test_serialize_cullable_prims_with_depth_and_spaces():
    serializer = _CullablePrimsSerializer(indent=2, use_tabs=False)
    cullable_prims = CullablePrims(7, 8, 9)
    result = serializer.serialize(cullable_prims, depth=2)
    expected = "    cullable_prims ( 7 8 9 )"
    assert result == expected

