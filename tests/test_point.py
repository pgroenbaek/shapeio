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

from shapeio.shape import Point
from shapeio.decoder import _PointParser
from shapeio.encoder import _PointSerializer


@pytest.fixture
def serializer():
    return _PointSerializer()


@pytest.fixture
def parser():
    return _PointParser()


def test_serialize_point(serializer):
    point = Point(1.2, 2.0, 3.0)
    assert serializer.serialize(point) == "point ( 1.2 2 3 )"


def test_parse_point(parser):
    text = "point ( 1.0 2.0 3.0 )"
    point = parser.parse(text)
    assert point.x == 1.0
    assert point.y == 2.0
    assert point.z == 3.0


def test_parse_point_with_whitespace(parser):
    text = "  point (   -1.5  0.0   42.75 )  "
    point = parser.parse(text)
    assert point.x == -1.5
    assert point.y == 0.0
    assert point.z == 42.75


@pytest.mark.parametrize("bad_input", [
    "point ( 1.0 2.0 )",          # Too few components
    "point ( 1.0 2.0 3.0 4.0 )",  # Too many components
    "poin ( 1.0 2.0 3.0 )",       # Incorrect keyword
    "point 1.0 2.0 3.0",          # Missing parentheses
])
def test_parse_invalid_point_raises(parser, bad_input):
    with pytest.raises(ValueError):
        parser.parse(bad_input)


def test_serialize_point_with_depth_and_spaces():
    serializer = _PointSerializer(indent=2, use_tabs=False)
    point = Point(1.2, 2, 3)
    result = serializer.serialize(point, depth=2)
    expected = "    point ( 1.2 2 3 )"
    assert result == expected
