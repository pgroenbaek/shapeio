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

from shapeio.shape import CullablePrims, GeometryNode, GeometryInfo, Point
from shapeio.decoder import _GeometryInfoParser, BlockFormatError, BlockNotFoundError
from shapeio.encoder import _GeometryInfoSerializer


@pytest.fixture
def serializer():
    return _GeometryInfoSerializer()


@pytest.fixture
def parser():
    return _GeometryInfoParser()


def test_serialize_geometry_info(serializer):
    cullable_prims = CullablePrims(1, 2, 3)
    geometry_node = GeometryNode(10, 20, 30, 40, 50, cullable_prims)
    geometry_info = GeometryInfo(
        face_normals=126,
        tx_light_cmds=2,
        node_x_tx_light_cmds=0,
        trilist_indices=378,
        line_list_indices=0,
        node_x_trilist_indices=0,
        trilists=2,
        line_lists=0,
        pt_lists=0,
        node_x_trilists=0,
        geometry_nodes=[geometry_node],
        geometry_node_map=[0]
    )
    result = serializer.serialize(geometry_info)
    expected = (
        "geometry_info ( 126 2 0 378 0 0 2 0 0 0\n"
        "\tgeometry_nodes ( 1\n"
        "\t\tgeometry_node ( 10 20 30 40 50\n"
        "\t\t\tcullable_prims ( 1 2 3 )\n"
        "\t\t)\n"
        "\t)\n"
        "\tgeometry_node_map ( 1 0 )\n"
        ")"
    )
    assert result == expected


def test_parse_geometry_info(parser):
    text = """
        geometry_info ( 126 2 0 378 0 0 2 0 0 0
            geometry_nodes ( 1
                geometry_node ( 10 20 30 40 50
                    cullable_prims ( 1 2 3 )
                )
            )
            geometry_node_map ( 1 0 )
        )
    """
    geometry_info = parser.parse(text)
    assert geometry_info.face_normals == 126
    assert geometry_info.tx_light_cmds == 2
    assert geometry_info.node_x_tx_light_cmds == 0
    assert geometry_info.trilist_indices == 378
    assert geometry_info.line_list_indices == 0
    assert geometry_info.node_x_trilist_indices == 0
    assert geometry_info.trilists == 2
    assert geometry_info.line_lists == 0
    assert geometry_info.pt_lists == 0
    assert geometry_info.node_x_trilists == 0
    assert len(geometry_info.geometry_nodes) == 1
    node = geometry_info.geometry_nodes[0]
    assert node.tx_light_cmds == 10
    assert node.node_x_tx_light_cmds == 20
    assert node.trilists == 30
    assert node.line_lists == 40
    assert node.pt_lists == 50
    assert node.cullable_prims.num_prims == 1
    assert node.cullable_prims.num_flat_sections == 2
    assert node.cullable_prims.num_prim_indices == 3
    assert geometry_info.geometry_node_map == [0]


def test_parse_geometry_info_with_whitespace(parser):
    text = """
        geometry_info (
            1 2 3 4 5 6 7 8 9 10
            geometry_nodes ( 1
                geometry_node (
                    11 12 13 14 15
                    cullable_prims ( 16 17 18 )
                )
            )
            geometry_node_map ( 2 19 20 )
        )
    """
    geometry_info = parser.parse(text)
    assert geometry_info.face_normals == 1
    assert geometry_info.geometry_nodes[0].tx_light_cmds == 11
    assert geometry_info.geometry_node_map == [19, 20]


@pytest.mark.parametrize("bad_input", [
    "geometry_info ( 1 2 3 4 5 6 7 8 9 )",                    # Too few integers
    "geometry_infot ( 1 2 3 4 5 6 7 8 9 10 )",                # Wrong keyword
    "geometry_info 1 2 3 4 5 6 7 8 9 10",                     # Missing parenthesis
])
def test_parse_invalid_geometry_info_raises(parser, bad_input):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_input)


@pytest.mark.parametrize("bad_input", [
    "geometry_info ( 1 2 3 4 5 6 7 8 9 10 )",              # Too many integers
    "geometry_info ( 1 2 3 4 5 6 7 8 9 10 geometry_nodes () )" # Empty geometry_nodes block
])
def test_parse_invalid_geometry_info_raises(parser, bad_input):
    with pytest.raises(BlockNotFoundError):
        parser.parse(bad_input)


@pytest.mark.parametrize("bad_input", [
    Point(1.0, 2.0, 3.0),  # Wrong type
])
def test_serialize_invalid_type_raises(serializer, bad_input):
    with pytest.raises(TypeError):
        serializer.serialize(bad_input)


def test_serialize_geometry_info_with_depth_and_spaces():
    serializer = _GeometryInfoSerializer(indent=2, use_tabs=False)
    cullable_prims = CullablePrims(1, 1, 1)
    geometry_node = GeometryNode(1, 1, 1, 1, 1, cullable_prims)
    geometry_info = GeometryInfo(
        face_normals=1,
        tx_light_cmds=2,
        node_x_tx_light_cmds=3,
        trilist_indices=4,
        line_list_indices=5,
        node_x_trilist_indices=6,
        trilists=7,
        line_lists=8,
        pt_lists=9,
        node_x_trilists=10,
        geometry_nodes=[geometry_node],
        geometry_node_map=[99]
    )
    result = serializer.serialize(geometry_info, depth=1)
    expected = (
        "  geometry_info ( 1 2 3 4 5 6 7 8 9 10\n"
        "    geometry_nodes ( 1\n"
        "      geometry_node ( 1 1 1 1 1\n"
        "        cullable_prims ( 1 1 1 )\n"
        "      )\n"
        "    )\n"
        "    geometry_node_map ( 1 99 )\n"
        "  )"
    )
    assert result == expected
