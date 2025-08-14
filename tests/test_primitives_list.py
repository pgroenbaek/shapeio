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

from collections import defaultdict

from shapeio.shape import Primitive, IndexedTrilist
from shapeio.decoder import _PrimitivesParser, BlockNotFoundError, BlockFormatError, CountMismatchError
from shapeio.encoder import _PrimitivesSerializer


@pytest.fixture
def serializer():
    return _PrimitivesSerializer(indent=1, use_tabs=True)


@pytest.fixture
def parser():
    return _PrimitivesParser()


def test_serialize_primitives_basic(serializer):
    primitives = [
        Primitive(1, IndexedTrilist([], [], [])),
        Primitive(2, IndexedTrilist([], [], [])),
        Primitive(1, IndexedTrilist([], [], []))
    ]
    output = serializer.serialize(primitives, depth=0)
    assert output.startswith("primitives ( 5")
    assert output.count("prim_state_idx") == 2
    assert output.count("indexed_trilist") == 3


def test_parse_primitives_basic(parser):
    text = (
        "primitives ( 5\n"
        "  prim_state_idx ( 1 )\n"
        "  indexed_trilist (\n vertex_idxs ( 0 )\n normal_idxs ( 0 )\n flags ( 0 )\n )\n"
        "  indexed_trilist (\n vertex_idxs ( 0 )\n normal_idxs ( 0 )\n flags ( 0 )\n )\n"
        "  prim_state_idx ( 2 )\n"
        "  indexed_trilist (\n vertex_idxs ( 0 )\n normal_idxs ( 0 )\n flags ( 0 )\n )\n"
        ")"
    )
    primitives = parser.parse(text)
    assert isinstance(primitives, list)
    assert len(primitives) == 3
    assert primitives[0].prim_state_index == 1
    assert primitives[1].prim_state_index == 1
    assert primitives[2].prim_state_index == 2
    for prim in primitives:
        assert prim.indexed_trilist.vertex_idxs == []
        assert prim.indexed_trilist.normal_idxs == []
        assert prim.indexed_trilist.flags == []


def test_serialize_then_parse_roundtrip(serializer, parser):
    primitives_in = [
        Primitive(7, IndexedTrilist([], [], [])),
        Primitive(7, IndexedTrilist([], [], [])),
        Primitive(9, IndexedTrilist([], [], []))
    ]
    serialized = serializer.serialize(primitives_in)
    primitives_out = parser.parse(serialized)
    assert len(primitives_out) == len(primitives_in)
    assert all(isinstance(p, Primitive) for p in primitives_out)
    assert [p.prim_state_index for p in primitives_out] == [7, 7, 9]
    for prim in primitives_out:
        assert prim.indexed_trilist.vertex_idxs == []
        assert prim.indexed_trilist.normal_idxs == []
        assert prim.indexed_trilist.flags == []


@pytest.mark.parametrize("bad_input", [
    "",  # Empty string
    "primitives ()",  # Empty primitives block
    "prim_state_idx ( )",  # No primitives block
    "primitive ( 2 prim_state_idx ( 1 ) indexed_trilist ( ) )",  # Wrong block name
])
def test_parse_invalid_input_raises_block_not_found(parser, bad_input):
    with pytest.raises(BlockNotFoundError):
        parser.parse(bad_input)


@pytest.mark.parametrize("bad_input", [
    "primitives ( 1 )",  # Count is 1 without any items
    "primitives ( 1 prim_state_idx ( 1 ) indexed_trilist ( ) )",  # non-int index
    "primitives ( 3 prim_state_idx ( 1 ) indexed_trilist ( ) )",  # malformed block
])
def test_parse_invalid_input_raises_count_mismatch(parser, bad_input):
    with pytest.raises(CountMismatchError):
        parser.parse(bad_input)


@pytest.mark.parametrize("bad_type", [
    123,
    "not a primitive",
    [1, 2, 3]
])
def test_serialize_invalid_type_raises(serializer, bad_type):
    with pytest.raises(TypeError):
        serializer.serialize(bad_type)
