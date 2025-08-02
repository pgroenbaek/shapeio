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

from shapeio.shape import VtxState
from shapeio.decoder import _VtxStateParser, BlockFormatError
from shapeio.encoder import _VtxStateSerializer


@pytest.fixture
def parser():
    return _VtxStateParser()


@pytest.fixture
def serializer():
    return _VtxStateSerializer()


def test_parse_vtx_state(parser):
    text = "vtx_state ( 00000000 3 -5 0 00000002 )"
    vtx_state = parser.parse(text)
    assert vtx_state.flags == "00000000"
    assert vtx_state.matrix_index == 3
    assert vtx_state.light_material_index == -5
    assert vtx_state.light_model_cfg_index == 0
    assert vtx_state.light_flags == "00000002"
    assert vtx_state.matrix2_index is None


def test_parse_vtx_state_with_extra_int(parser):
    text = "vtx_state ( deadbeef 9 -11 0 cafefeed 4 )"
    vtx_state = parser.parse(text)
    assert vtx_state.flags == "deadbeef"
    assert vtx_state.matrix_index == 9
    assert vtx_state.light_material_index == -11
    assert vtx_state.light_model_cfg_index == 0
    assert vtx_state.light_flags == "cafefeed"
    assert vtx_state.matrix2_index == 4


def test_serialize_vtx_state(serializer):
    vtx_state = VtxState("ABCDEF00", 1, -5, 0, "12345678")
    result = serializer.serialize(vtx_state)
    assert result == "vtx_state ( abcdef00 1 -5 0 12345678 )"


def test_serialize_vtx_state_with_extra_int(serializer):
    vtx_state = VtxState("FF00FF00", 7, -3, 2, "00FF00FF", matrix2_index=8)
    result = serializer.serialize(vtx_state)
    assert result == "vtx_state ( ff00ff00 7 -3 2 00ff00ff 8 )"


def test_serialize_vtx_state_with_depth(serializer):
    vtx_state = VtxState("ABC12300", 0, 1, 2, "00ABCDEF")
    result = serializer.serialize(vtx_state, depth=1)
    assert result == "\tvtx_state ( abc12300 0 1 2 00abcdef )"


@pytest.mark.parametrize("bad_input", [
    "vtx_state ( 00000000 1 -5 0 )",                     # Missing light_flags
    "vtx_state ( 00000000 1 -5 0 00000002 X )",          # Invalid extra int
    "vtx_state ( 00000000 1 -5 0 GARBAGE )",             # Invalid hex
    "vtxstate ( 00000000 1 -5 0 00000002 )",             # Wrong keyword
    "vtx_state 00000000 1 -5 0 00000002",                # Missing parentheses
])
def test_parse_invalid_vtx_state_raises(parser, bad_input):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_input)
