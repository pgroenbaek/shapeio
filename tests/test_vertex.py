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

from shapeio.shape import Vertex, VertexSet
from shapeio.decoder import _VertexParser, BlockFormatError, BlockNotFoundError
from shapeio.encoder import _VertexSerializer


@pytest.fixture
def serializer():
    return _VertexSerializer()


@pytest.fixture
def parser():
    return _VertexParser()


def test_serialize_vertex(serializer):
    vertex = Vertex("00000000", 3413, 207, "ff969696", "ff808080", [1153])
    result = serializer.serialize(vertex)
    expected = (
        "vertex ( 00000000 3413 207 ff969696 ff808080\n"
        "\tvertex_uvs ( 1 1153 )\n"
        ")"
    )
    assert result == expected


def test_parse_vertex(parser):
    text = (
        "vertex ( 00000000 3413 207 ff969696 ff808080\n"
        "\tvertex_uvs ( 1 1153 )\n"
        ")"
    )
    vertex = parser.parse(text)
    assert vertex.flags == "00000000"
    assert vertex.point_index == 3413
    assert vertex.normal_index == 207
    assert vertex.colour1 == "ff969696"
    assert vertex.colour2 == "ff808080"
    assert vertex.vertex_uvs == [1153]


def test_parse_vertex_with_multiple_uvs(parser):
    text = (
        "vertex ( 00000000 12 34 ffffffff 00000000\n"
        "\tvertex_uvs ( 3 100 200 300 )\n"
        ")"
    )
    vertex = parser.parse(text)
    assert vertex.vertex_uvs == [100, 200, 300]


@pytest.mark.parametrize("bad_input", [
    "vortex ( 00000000 1 2 ffffffff ffffffff\nvertex_uvs ( 1 123 )\n)",  # Wrong keyword
    "vertex ( 000000GG 1 2 ffffffff ffffffff\n vertex_uvs ( 1 123 )\n)", # Bad hex
    "vertex ( 00000000 1 2 ffffffff ffffffff\n vertex_uvs ( )\n)",       # Incomplete vertex_uvs block
])
def test_parse_invalid_vertex_raises(parser, bad_input):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_input)


@pytest.mark.parametrize("bad_input", [
    "vertex ( 00000000 1 2 ffffffff ffffffff )",                         # Missing vertex_uvs block
])
def test_parse_invalid_vertex_raises(parser, bad_input):
    with pytest.raises(BlockNotFoundError):
        parser.parse(bad_input)


@pytest.mark.parametrize("bad_input", [
    VertexSet(0, 0, 0),
])
def test_serialize_invalid_type_raises(serializer, bad_input):
    with pytest.raises(TypeError):
        serializer.serialize(bad_input)


def test_serialize_vertex_with_depth_and_spaces():
    serializer = _VertexSerializer(indent=2, use_tabs=False)
    vertex = Vertex("abcd1234", 1, 2, "ff000000", "00ffffff", [999])
    result = serializer.serialize(vertex, depth=1)
    expected = (
        "  vertex ( abcd1234 1 2 ff000000 00ffffff\n"
        "    vertex_uvs ( 1 999 )\n"
        "  )"
    )
    assert result == expected
