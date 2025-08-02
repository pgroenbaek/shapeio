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

from shapeio.shape import Texture, Point
from shapeio.decoder import _TextureParser, BlockFormatError
from shapeio.encoder import _TextureSerializer


@pytest.fixture
def parser():
    return _TextureParser()


@pytest.fixture
def serializer():
    return _TextureSerializer()


def test_parse_texture(parser):
    text = "texture ( 2 1 -1.5 ff00ff00 )"
    tex = parser.parse(text)
    assert tex.image_index == 2
    assert tex.filter_mode == 1
    assert tex.mipmap_lod_bias == -1.5
    assert tex.border_colour.lower() == "ff00ff00"


def test_parse_texture_with_whitespace(parser):
    text = "  texture (  0   0   0.0   deadbeef  ) "
    tex = parser.parse(text)
    assert tex.image_index == 0
    assert tex.filter_mode == 0
    assert tex.mipmap_lod_bias == 0.0
    assert tex.border_colour.lower() == "deadbeef"


def test_serialize_texture(serializer):
    tex = Texture(3, 1, 0.25, "FF00FF00")
    result = serializer.serialize(tex)
    assert result == "texture ( 3 1 0.25 ff00ff00 )"


def test_serialize_texture_with_depth(serializer):
    tex = Texture(1, 0, -2.75, "abcdef12")
    result = serializer.serialize(tex, depth=1)
    assert result == "\ttexture ( 1 0 -2.75 abcdef12 )"


@pytest.mark.parametrize("bad_input", [
    "texture ( 1 1 ff00ff00 )",           # Missing mipmap_lod_bias
    "texture ( 1 1 -0.5 )",               # Missing hex
    "texture 1 1 -0.5 ff00ff00",          # Missing parentheses
    "texture ( 1 1 -0.5 GHIJKL )",        # Invalid hex
])
def test_parse_invalid_texture_raises(parser, bad_input):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_input)


@pytest.mark.parametrize("bad_input", [
    Point(1.0, 2.2, 3.2),
])
def test_serialize_invalid_type_raises(serializer, bad_input):
    with pytest.raises(TypeError):
        serializer.serialize(bad_input)
