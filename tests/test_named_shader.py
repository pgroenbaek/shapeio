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
from shapeio.decoder import _NamedShaderParser, BlockFormatError
from shapeio.encoder import _NamedShaderSerializer


@pytest.fixture
def serializer():
    return _NamedShaderSerializer()


@pytest.fixture
def parser():
    return _NamedShaderParser()


def test_serialize_named_shader(serializer):
    shader = "TexDiff"
    result = serializer.serialize(shader)
    assert result == "named_shader ( TexDiff )"


def test_parse_named_shader(parser):
    text = "named_shader ( TexDiff )"
    shader = parser.parse(text)
    assert shader == "TexDiff"


def test_parse_named_shader_with_whitespace(parser):
    text = "  named_shader (   BlendATexDiff   )  "
    shader = parser.parse(text)
    assert shader == "BlendATexDiff"


@pytest.mark.parametrize("bad_input", [
    "namedshader ( TexDiff )",             # Incorrect keyword
    "named_shader TexDiff",                # Missing parentheses
    "named_shader ( )",                    # Empty string
    "named_shader ()",                     # Also empty
])
def test_parse_invalid_named_shader_raises(parser, bad_input):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_input)


@pytest.mark.parametrize("bad_input", [
    Point(1.0, 2.2, 3.2),
])
def test_serialize_invalid_type_raises(serializer, bad_input):
    with pytest.raises(TypeError):
        serializer.serialize(bad_input)


def test_serialize_named_shader_with_depth_and_spaces():
    serializer = _NamedShaderSerializer(indent=2, use_tabs=False)
    shader = "BlendATexDiff"
    result = serializer.serialize(shader, depth=1)
    expected = "  named_shader ( BlendATexDiff )"
    assert result == expected

