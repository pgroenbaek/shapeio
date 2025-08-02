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
from shapeio.decoder import _DistanceLevelSelectionParser, BlockFormatError
from shapeio.encoder import _DistanceLevelSelectionSerializer


@pytest.fixture
def serializer():
    return _DistanceLevelSelectionSerializer()


@pytest.fixture
def parser():
    return _DistanceLevelSelectionParser()


def test_serialize_dlevel_selection(serializer):
    result = serializer.serialize(200)
    assert result == "dlevel_selection ( 200 )"


def test_parse_dlevel_selection(parser):
    text = "dlevel_selection ( 200 )"
    value = parser.parse(text)
    assert value == 200


def test_parse_dlevel_selection_with_whitespace(parser):
    text = "   dlevel_selection (   345   )   "
    value = parser.parse(text)
    assert value == 345


@pytest.mark.parametrize("bad_input", [
    "dlevel_selection ()",           # Missing number
    "dlevel_selection ( abc )",      # Not a number
    "dlevel_selection ( 1 2 )",      # Too many numbers
    "dlevelselection ( 123 )",       # Misspelled keyword
    "dlevel_selection 123",          # Missing parentheses
])
def test_parse_invalid_dlevel_selection_raises(parser, bad_input):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_input)


@pytest.mark.parametrize("bad_input", [
    Point(1.0, 2.0, 3.0),
    "not a number",
])
def test_serialize_invalid_type_raises(serializer, bad_input):
    with pytest.raises(TypeError):
        serializer.serialize(bad_input)


def test_serialize_dlevel_selection_with_depth_and_spaces():
    serializer = _DistanceLevelSelectionSerializer(indent=2, use_tabs=False)
    result = serializer.serialize(999, depth=1)
    expected = "  dlevel_selection ( 999 )"
    assert result == expected