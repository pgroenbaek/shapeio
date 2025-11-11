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

from shapeio.shape import PrimState, Point
from shapeio.decoder import _PrimStateParser, BlockFormatError
from shapeio.encoder import _PrimStateSerializer


@pytest.fixture
def parser():
    return _PrimStateParser()


@pytest.fixture
def serializer():
    return _PrimStateSerializer()


def test_parse_prim_state(parser):
    text = """prim_state Rails ( 00000000 0
        tex_idxs ( 2 1 3 ) 0 0 0 0 1
    )"""
    prim_state = parser.parse(text)
    assert prim_state.name == "Rails"
    assert prim_state.flags == "00000000"
    assert prim_state.shader_index == 0
    assert prim_state.texture_indices == [1, 3]
    assert prim_state.z_bias == 0
    assert prim_state.vtx_state_index == 0
    assert prim_state.alpha_test_mode == 0
    assert prim_state.light_cfg_index == 0
    assert prim_state.z_buffer_mode == 1


def test_parse_prim_state_without_name(parser):
    text = """prim_state ( 00000000 0
        tex_idxs ( 2 1 3 ) 0 0 0 0 1
    )"""
    prim_state = parser.parse(text)
    assert prim_state.name == None
    assert prim_state.flags == "00000000"
    assert prim_state.shader_index == 0
    assert prim_state.texture_indices == [1, 3]
    assert prim_state.z_bias == 0
    assert prim_state.vtx_state_index == 0
    assert prim_state.alpha_test_mode == 0
    assert prim_state.light_cfg_index == 0
    assert prim_state.z_buffer_mode == 1


def test_serialize_prim_state(serializer):
    prim_state = PrimState("Rails", "FF00FF00", 2, [1, 5], 0, 3, 1, 0, 1)
    result = serializer.serialize(prim_state)
    expected = (
        "prim_state Rails ( ff00ff00 2\n"
        "\ttex_idxs ( 2 1 5 ) 0 3 1 0 1\n"
        ")"
    )
    assert result == expected


def test_serialize_prim_state_depth_1(serializer):
    prim_state = PrimState("Rails", "FF00FF00", 2, [1, 5], 0, 3, 1, 0, 1)
    result = serializer.serialize(prim_state, depth=1)
    expected = (
        "\tprim_state Rails ( ff00ff00 2\n"
        "\t\ttex_idxs ( 2 1 5 ) 0 3 1 0 1\n"
        "\t)"
    )
    assert result == expected


@pytest.mark.parametrize("bad_input", [
    "prim_state Foo ( 00000000 0 tex_idxs ( 2 1 ) 0 0 0 0 )",  # missing z_buffer_mode
    "prim_state Foo ( ZZZZZZZZ 0 tex_idxs ( 1 2 ) 0 0 0 0 1 )",  # invalid hex
    "prim_state Foo ( 00000000 0 texidxs ( 1 2 ) 0 0 0 0 1 )",  # misspelled tex_idxs
])
def test_parse_invalid_prim_state_raises(parser, bad_input):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_input)


@pytest.mark.parametrize("bad_input", [
    Point(1.0, 2.2, 3.2),
])
def test_serialize_invalid_type_raises(serializer, bad_input):
    with pytest.raises(TypeError):
        serializer.serialize(bad_input)
