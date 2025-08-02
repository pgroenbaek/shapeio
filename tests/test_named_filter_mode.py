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
from shapeio.decoder import _NamedFilterModeParser, BlockFormatError
from shapeio.encoder import _NamedFilterModeSerializer


@pytest.fixture
def serializer():
    return _NamedFilterModeSerializer()


@pytest.fixture
def parser():
    return _NamedFilterModeParser()


def test_serialize_named_filter_mode(serializer):
    mode = "MipLinear"
    result = serializer.serialize(mode)
    assert result == "named_filter_mode ( MipLinear )"


def test_parse_named_filter_mode(parser):
    text = "named_filter_mode ( LinearMipLinear )"
    mode = parser.parse(text)
    assert mode == "LinearMipLinear"


def test_parse_named_filter_mode_with_whitespace(parser):
    text = "  named_filter_mode (   LinearMipLinear   )  "
    mode = parser.parse(text)
    assert mode == "LinearMipLinear"


@pytest.mark.parametrize("bad_input", [
    "namedfilter_mode ( MipLinear )",         # Incorrect keyword
    "named_filter_mode MipLinear",            # Missing parentheses
    "named_filter_mode ( )",                  # Empty value
    "named_filter_mode ()",                   # Also empty
])
def test_parse_invalid_named_filter_mode_raises(parser, bad_input):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_input)


@pytest.mark.parametrize("bad_input", [
    Point(1.0, 2.2, 3.2),
])
def test_serialize_invalid_type_raises(serializer, bad_input):
    with pytest.raises(TypeError):
        serializer.serialize(bad_input)


def test_serialize_named_filter_mode_with_depth_and_spaces():
    serializer = _NamedFilterModeSerializer(indent=2, use_tabs=False)
    mode = "LinearMipLinear"
    result = serializer.serialize(mode, depth=2)
    expected = "    named_filter_mode ( LinearMipLinear )"
    assert result == expected

