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

from shapeio.decoder import _ImageParser
from shapeio.encoder import _ImageSerializer


@pytest.fixture
def serializer():
    return _ImageSerializer()


@pytest.fixture
def parser():
    return _ImageParser()


def test_serialize_image(serializer):
    image = "DB_Track1w.ACE"
    result = serializer.serialize(image)
    assert result == "image ( DB_Track1w.ACE )"


def test_parse_image(parser):
    text = "image ( DB_Track1w.ACE )"
    mode = parser.parse(text)
    assert mode == "DB_Track1w.ACE"


def test_parse_image_with_whitespace(parser):
    text = "  image (   DB_Track1w.ACE   )  "
    mode = parser.parse(text)
    assert mode == "DB_Track1w.ACE"


@pytest.mark.parametrize("bad_input", [
    "img ( DB_Track1w.ACE )",         # Incorrect keyword
    "image DB_Track1w.ACE",            # Missing parentheses
    "image ( )",                  # Empty value
    "image ()",                   # Also empty
])
def test_parse_image_mode_raises(parser, bad_input):
    with pytest.raises(ValueError):
        parser.parse(bad_input)


def test_serialize_image_with_depth_and_spaces():
    serializer = _ImageSerializer(indent=2, use_tabs=False)
    mode = "DB_Track1w.ACE"
    result = serializer.serialize(mode, depth=2)
    expected = "    image ( DB_Track1w.ACE )"
    assert result == expected

