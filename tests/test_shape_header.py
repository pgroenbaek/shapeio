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

from shapeio.shape import ShapeHeader
from shapeio.decoder import _ShapeHeaderParser, BlockFormatError
from shapeio.encoder import _ShapeHeaderSerializer


@pytest.fixture
def serializer():
    return _ShapeHeaderSerializer()


@pytest.fixture
def parser():
    return _ShapeHeaderParser()


def test_serialize_shape_header(serializer):
    header = ShapeHeader("0000001F", "DEADBEEF")
    result = serializer.serialize(header)
    assert result == "shape_header ( 0000001f deadbeef )"


def test_parse_shape_header(parser):
    text = "shape_header ( 0000001F deadbeef )"
    header = parser.parse(text)
    assert header.flags1 == "0000001f"
    assert header.flags2 == "deadbeef"


def test_parse_shape_header_with_whitespace(parser):
    text = "  shape_header (   00ff00aa    abcd1234  )  "
    header = parser.parse(text)
    assert header.flags1 == "00ff00aa"
    assert header.flags2 == "abcd1234"


@pytest.mark.parametrize("bad_input", [
    "shape_header ( 0000001F )",                  # Too few parts
    "shape_header ( 0000001F DEADBEEF CAFEFEED )", # Too many parts
    "shapeheader ( 0000001F DEADBEEF )",          # Wrong keyword
    "shape_header 0000001F DEADBEEF",             # Missing parentheses
    "shape_header ( 000000G1 DEADBEEF )",         # Invalid hex char
])
def test_parse_invalid_shape_header_raises(parser, bad_input):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_input)


def test_serialize_shape_header_with_depth_and_spaces():
    serializer = _ShapeHeaderSerializer(indent=2, use_tabs=False)
    header = ShapeHeader("abcd1234", "deadbeef")
    result = serializer.serialize(header, depth=1)
    expected = "  shape_header ( abcd1234 deadbeef )"
    assert result == expected

