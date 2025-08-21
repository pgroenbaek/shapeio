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

from shapeio.shape import AnimationNode
from shapeio.decoder import _AnimationNodeParser, BlockFormatError
from shapeio.encoder import _AnimationNodeSerializer


@pytest.fixture
def serializer():
    return _AnimationNodeSerializer()


@pytest.fixture
def parser():
    return _AnimationNodeParser()


def test_serialize_animation_node(serializer):
    node = AnimationNode(name="PNT5D_L01", controllers=[])
    result = serializer.serialize(node)
    assert result.startswith("anim_node PNT5D_L01 (")
    assert result.strip().endswith(")")


def test_parse_animation_node(parser):
    text = "anim_node PNT5D_L01 (\n controllers ( 0 )\n )"
    node = parser.parse(text)
    assert isinstance(node, AnimationNode)
    assert node.name == "PNT5D_L01"
    assert hasattr(node, "controllers")


def test_parse_animation_node_with_whitespace(parser):
    text = "   anim_node   MyNode_42   ( \n controllers (  0 ) \n )"
    node = parser.parse(text)
    assert node.name == "MyNode_42"


@pytest.mark.parametrize("bad_input", [
    "anim_nodes MyNode ( controllers ( 0 ) )",   # Wrong keyword
    "anim_node (",           # Missing name
    "anim_node",             # Incomplete
])
def test_parse_invalid_animation_node_raises(parser, bad_input):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_input)


@pytest.mark.parametrize("bad_input", [
    "not_an_anim_node",
    123,
    object(),
])
def test_serialize_invalid_type_raises(serializer, bad_input):
    with pytest.raises(TypeError):
        serializer.serialize(bad_input)


def test_serialize_animation_node_with_indent_and_depth():
    serializer = _AnimationNodeSerializer(indent=2, use_tabs=False)
    node = AnimationNode(name="Node01", controllers=[])
    result = serializer.serialize(node, depth=1)
    assert result.startswith("  anim_node Node01 (")
    assert result.strip().endswith("  )")
