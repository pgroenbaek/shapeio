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

from shapeio.shape import VertexSet, Point
from shapeio.decoder import _VertexSetParser, BlockFormatError
from shapeio.encoder import _VertexSetSerializer


@pytest.fixture
def serializer():
    return _VertexSetSerializer()


@pytest.fixture
def parser():
    return _VertexSetParser()


def test_serialize_vertex_set(serializer):
    vset = VertexSet(0, 12, 34)
    assert serializer.serialize(vset) == "vertex_set ( 0 12 34 )"


def test_parse_vertex_set(parser):
    text = "vertex_set ( 1 100 250 )"
    vset = parser.parse(text)
    assert vset.vtx_state == 1
    assert vset.vtx_start_index == 100
    assert vset.vtx_count == 250


def test_parse_vertex_set_with_whitespace(parser):
    text = "  vertex_set (  7   8  9 )  "
    vset = parser.parse(text)
    assert vset.vtx_state == 7
    assert vset.vtx_start_index == 8
    assert vset.vtx_count == 9


@pytest.mark.parametrize("bad_input", [
    "vertex_set ( 1 2 )",               # Too few items
    "vertex_set ( 1 2 3 4 )",           # Too many
    "vertex_set 1 2 3",                 # Missing parentheses
    "vertexset ( 1 2 3 )",              # Typo in keyword
])
def test_parse_invalid_vertex_set_raises(parser, bad_input):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_input)


@pytest.mark.parametrize("bad_input", [
    Point(0, 0, 0),
])
def test_serialize_invalid_vertex_set_type_raises(serializer, bad_input):
    with pytest.raises(TypeError):
        serializer.serialize(bad_input)


def test_serialize_vertex_set_with_depth_and_spaces():
    serializer = _VertexSetSerializer(indent=1, use_tabs=False)
    vertex_set = VertexSet(9, 8, 7)
    result = serializer.serialize(vertex_set, depth=2)
    assert result == "  vertex_set ( 9 8 7 )"
