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

from shapeio.shape import UVPoint
from shapeio.decoder import _UVPointParser
from shapeio.encoder import _UVPointSerializer


@pytest.fixture
def serializer():
    return _UVPointSerializer()


@pytest.fixture
def parser():
    return _UVPointParser()


def test_serialize_uv_point(serializer):
    uv_point = UVPoint(1.2, 2.0)
    assert serializer.serialize(uv_point) == "uv_point ( 1.2 2 )"


def test_parse_uv_point(parser):
    text = "uv_point ( 1.0 2.0 )"
    uv_point = parser.parse(text)
    assert uv_point.u == 1.0
    assert uv_point.v == 2.0


def test_parse_uv_point_with_whitespace(parser):
    text = "  uv_point (   -1.5  0.0  )  "
    uv_point = parser.parse(text)
    assert uv_point.u == -1.5
    assert uv_point.v == 0.0


@pytest.mark.parametrize("bad_input", [
    "uv_point ( 1.0 )",         # Too few components
    "uv_point ( 1.0 2.0 3.0 )", # Too many components
    "uv_poin ( 1.0 2.0)",       # Incorrect keyword
    "point ( 1.0 2.0 )",        # Incorrect keyword
    "uv_point 1.0 2.0 3.0",     # Missing parentheses
])
def test_parse_invalid_uv_point_raises(parser, bad_input):
    with pytest.raises(ValueError):
        parser.parse(bad_input)


def test_serialize_uvpoint_with_depth_and_spaces():
    serializer = _UVPointSerializer(indent=2, use_tabs=False)
    uv_point = UVPoint(0.1, 0.2)
    result = serializer.serialize(uv_point, depth=3)
    expected = "      uv_point ( 0.1 0.2 )"
    assert result == expected
