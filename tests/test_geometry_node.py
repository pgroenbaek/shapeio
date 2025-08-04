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

from shapeio.shape import CullablePrims, GeometryNode, Point
from shapeio.decoder import _GeometryNodeParser, BlockFormatError, BlockNotFoundError
from shapeio.encoder import _GeometryNodeSerializer


@pytest.fixture
def serializer():
    return _GeometryNodeSerializer()


@pytest.fixture
def parser():
    return _GeometryNodeParser()


def test_serialize_geometry_node(serializer):
    cullable_prims = CullablePrims(1, 2, 3)
    geometry_node = GeometryNode(10, 20, 30, 40, 50, cullable_prims)
    expected = (
        "geometry_node ( 10 20 30 40 50\n"
        "\tcullable_prims ( 1 2 3 )\n"
        ")"
    )
    assert serializer.serialize(geometry_node) == expected


def test_parse_geometry_node(parser):
    text = """
        geometry_node ( 10 20 30 40 50
            cullable_prims ( 1 2 3 )
        )
    """
    geometry_node = parser.parse(text)
    assert geometry_node.tx_light_cmds == 10
    assert geometry_node.node_x_tx_light_cmds == 20
    assert geometry_node.trilists == 30
    assert geometry_node.line_lists == 40
    assert geometry_node.pt_lists == 50
    assert geometry_node.cullable_prims.num_prims == 1
    assert geometry_node.cullable_prims.num_flat_sections == 2
    assert geometry_node.cullable_prims.num_prim_indices == 3


def test_parse_geometry_node_with_whitespace(parser):
    text = """
            geometry_node (
                7    8   9  10  11
                cullable_prims ( 5   6   7 )
            )
    """
    geometry_node = parser.parse(text)

    assert geometry_node.tx_light_cmds == 7
    assert geometry_node.node_x_tx_light_cmds == 8
    assert geometry_node.trilists == 9
    assert geometry_node.line_lists == 10
    assert geometry_node.pt_lists == 11
    assert geometry_node.cullable_prims.num_prims == 5
    assert geometry_node.cullable_prims.num_flat_sections == 6
    assert geometry_node.cullable_prims.num_prim_indices == 7


@pytest.mark.parametrize("bad_input", [
    "geometry_node ( 1 2 3 4 )",                   # Too few ints
    "geometrie_node ( 1 2 3 4 5 )",                # Misspelled keyword
    "geometry_node 1 2 3 4 5",                     # Missing parentheses
])
def test_parse_invalid_geometry_node_raises(parser, bad_input):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_input)


@pytest.mark.parametrize("bad_input", [
    "geometry_node ( 1 2 3 4 5 )",               # Nested block not present
    "geometry_node ( 1 2 3 4 5\ncullableprim (1 2 3)\n)",  # Bad nested block
])
def test_parse_invalid_geometry_node_raises(parser, bad_input):
    with pytest.raises(BlockNotFoundError):
        parser.parse(bad_input)


@pytest.mark.parametrize("bad_input", [
    Point(1.0, 2.2, 3.2),  # Invalid type
])
def test_serialize_invalid_type_raises(serializer, bad_input):
    with pytest.raises(TypeError):
        serializer.serialize(bad_input)


def test_serialize_geometry_node_with_depth_and_spaces():
    serializer = _GeometryNodeSerializer(indent=2, use_tabs=False)
    cullable_prims = CullablePrims(4, 5, 6)
    geometry_node = GeometryNode(100, 200, 300, 400, 500, cullable_prims)

    result = serializer.serialize(geometry_node, depth=1)
    expected = (
        "  geometry_node ( 100 200 300 400 500\n"
        "    cullable_prims ( 4 5 6 )\n"
        "  )"
    )
    assert result == expected
