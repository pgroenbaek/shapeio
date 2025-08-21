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

from shapeio.shape import SlerpRot, LinearKey, TCBKey, Point
from shapeio.decoder import _KeyPositionParser, BlockFormatError
from shapeio.encoder import _KeyPositionSerializer


@pytest.fixture
def parser():
    return _KeyPositionParser()


@pytest.fixture
def serializer():
    return _KeyPositionSerializer()


@pytest.mark.parametrize("text, expected_type, expected_values", [
    ("slerp_rot ( 0 0 0 0.707107 0.707107 )", SlerpRot, (0, 0, 0, 0.707107, 0.707107)),
    ("linear_key ( 1 2.09668 0.2413 18.9491 )", LinearKey, (1, 2.09668, 0.2413, 18.9491)),
    ("tcb_key ( 0 0 0 0.707107 0.707107 0 0 0 0 0 )", TCBKey, (0, 0, 0, 0.707107, 0.707107, 0, 0, 0, 0, 0)),
])
def test_parse_key_position(parser, text, expected_type, expected_values):
    key = parser.parse(text)
    assert isinstance(key, expected_type)
    assert tuple(vars(key).values()) == expected_values


@pytest.mark.parametrize("key, expected", [
    (SlerpRot(0, 0, 0, 0.707107, 0.707107), "slerp_rot ( 0 0 0 0.707107 0.707107 )"),
    (LinearKey(1, 2.09668, 0.2413, 18.9491), "linear_key ( 1 2.09668 0.2413 18.9491 )"),
    (TCBKey(0, 0, 0, 0.707107, 0.707107, 0, 0, 0, 0, 0),
     "tcb_key ( 0 0 0 0.707107 0.707107 0 0 0 0 0 )"),
])
def test_serialize_key_position(serializer, key, expected):
    result = serializer.serialize(key, depth=0)
    assert result.strip() == expected


@pytest.mark.parametrize("bad_text", [
    "slerp_rot ( 0 0 0 0.707107 )",  # Too few args
    "linear_key ( 1 2 3 )",  # Too few
    "tcb_key ( 0 0 0 0.707107 0.707107 0 0 0 0 )",  # Too few
    "unknown_key ( 0 0 0 )",  # Unknown type
    "linear_key 1 2 3 4",  # Missing parentheses
])
def test_parse_invalid_key_raises(parser, bad_text):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_text)


@pytest.mark.parametrize("bad_input", [
    Point(1.0, 2.2, 3.2),
])
def test_serialize_invalid_type_raises(serializer, bad_input):
    with pytest.raises(TypeError):
        serializer.serialize(bad_input)
