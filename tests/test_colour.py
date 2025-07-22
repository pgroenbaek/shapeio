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

from shapeio.shape import Colour
from shapeio.decoder import _ColourParser
from shapeio.encoder import _ColourSerializer


@pytest.fixture
def serializer():
    return _ColourSerializer()


@pytest.fixture
def parser():
    return _ColourParser()


def test_serialize_colour(serializer):
    colour = Colour(1.0, 2.0, 3.0, 4.0)
    assert serializer.serialize(colour) == "colour ( 1.0 2.0 3.0 4.0 )"


def test_parse_colour(parser):
    text = "colour ( 1.0 2.0 3.0 4.0 )"
    colour = parser.parse(text)
    assert colour.a == 1.0
    assert colour.r == 2.0
    assert colour.g == 3.0
    assert colour.b == 4.0


def test_parse_colour_with_whitespace(parser):
    text = "  colour (   -1.5  0.0   42.75 13.37   )  "
    colour = parser.parse(text)
    assert colour.a == -1.5
    assert colour.r == 0.0
    assert colour.g == 42.75
    assert colour.b == 13.37


@pytest.mark.parametrize("bad_input", [
    "colour ( 1.0 2.0 3.0 )",          # Too few components
    "colour ( 1.0 2.0 3.0 4.0 5.0 )",  # Too many components
    "color ( 1.0 2.0 3.0 4.0 )",       # Incorrect keyword
    "colour 1.0 2.0 3.0 4.0",          # Missing parentheses
])
def test_parse_invalid_colour_raises(parser, bad_input):
    with pytest.raises(ValueError):
        parser.parse(bad_input)


def test_serialize_colour_with_depth_and_tabs():
    serializer = _ColourSerializer(indent=1, use_tabs=True)
    colour = Colour(1.0, 2.0, 3.0, 4.0)
    result = serializer.serialize(colour, depth=2)
    expected = "\t\tcolour ( 1.0 2.0 3.0 4.0 )"
    assert result == expected
