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

from shapeio.shape import Animation
from shapeio.decoder import _AnimationParser, BlockFormatError
from shapeio.encoder import _AnimationSerializer


@pytest.fixture
def serializer():
    return _AnimationSerializer()


@pytest.fixture
def parser():
    return _AnimationParser()


def test_serialize_animation(serializer):
    anim = Animation(frame_count=2, frame_rate=30, animation_nodes=[])
    result = serializer.serialize(anim)
    assert result.startswith("animation ( 2 30")
    assert result.strip().endswith(")")


def test_parse_animation(parser):
    text = "animation ( 2 30\n    anim_nodes ( 0\n   )\n)"
    anim = parser.parse(text)
    assert isinstance(anim, Animation)
    assert anim.frame_count == 2
    assert anim.frame_rate == 30
    assert hasattr(anim, "animation_nodes")


def test_parse_animation_with_whitespace(parser):
    text = "   animation   (   42   15   \n    anim_nodes ( 0\n   )\n)"
    anim = parser.parse(text)
    assert anim.frame_count == 42
    assert anim.frame_rate == 15


@pytest.mark.parametrize("bad_input", [
    "animation ( anim_nodes ( 0 ))",             # No numbers
    "animation ( 10 anim_nodes ( 0 ) )",         # Only one number
    "animations ( 10 20 anim_nodes ( 0 ) )",     # Wrong keyword
    "animation ( a b anim_nodes ( 0 ) )",        # Non-numeric
])
def test_parse_invalid_animation_raises(parser, bad_input):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_input)


@pytest.mark.parametrize("bad_input", [
    "not_an_animation",
    123,
    object(),
])
def test_serialize_invalid_type_raises(serializer, bad_input):
    with pytest.raises(TypeError):
        serializer.serialize(bad_input)


def test_serialize_animation_with_indent_and_depth():
    serializer = _AnimationSerializer(indent=2, use_tabs=False)
    anim = Animation(frame_count=5, frame_rate=60, animation_nodes=[])
    result = serializer.serialize(anim, depth=1)
    assert result.startswith("  animation ( 5 60")
    assert result.strip().endswith("  )")

