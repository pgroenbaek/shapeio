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

from shapeio.shape import DistanceLevelsHeader, Point
from shapeio.decoder import _DistanceLevelsHeaderParser, BlockFormatError
from shapeio.encoder import _DistanceLevelsHeaderSerializer


@pytest.fixture
def serializer():
    return _DistanceLevelsHeaderSerializer()


@pytest.fixture
def parser():
    return _DistanceLevelsHeaderParser()


def test_serialize_distance_levels_header(serializer):
    header = DistanceLevelsHeader(0)
    result = serializer.serialize(header)
    assert result == "distance_levels_header ( 0 )"


def test_parse_distance_levels_header(parser):
    text = "distance_levels_header ( 123 )"
    header = parser.parse(text)
    assert header.dlevel_bias == 123


def test_parse_distance_levels_header_with_whitespace(parser):
    text = "   distance_levels_header (    456    )   "
    header = parser.parse(text)
    assert header.dlevel_bias == 456


@pytest.mark.parametrize("bad_input", [
    "distance_levels_header ()",                 # Missing number
    "distance_levels_header ( abc )",            # Not a number
    "distance_levels_header ( 123 456 )",        # Too many numbers
    "distancelevels_header ( 123 )",             # Wrong keyword
    "distance_levels_header 123",                # Missing parentheses
])
def test_parse_invalid_distance_levels_header_raises(parser, bad_input):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_input)


@pytest.mark.parametrize("bad_input", [
    Point(1.0, 2.0, 3.0),
])
def test_serialize_invalid_type_raises(serializer, bad_input):
    with pytest.raises(TypeError):
        serializer.serialize(bad_input)


def test_serialize_distance_levels_header_with_depth_and_spaces():
    serializer = _DistanceLevelsHeaderSerializer(indent=2, use_tabs=False)
    header = DistanceLevelsHeader(789)
    result = serializer.serialize(header, depth=1)
    expected = "  distance_levels_header ( 789 )"
    assert result == expected

