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

from typing import Tuple, List

from shapeio.decoder import CountMismatchError, ShapeParserError
from shapeio.decoder import _Parser


class DummyParser(_Parser):
    def parse(self, text: str) -> str:
        return text.strip()


@pytest.fixture
def parser():
    return DummyParser()


@pytest.fixture
def valid_shape_text():
    return """
    colours ( 0 )
    matrices ( 10
        matrix PNT5D_L01 ( 1 0 0 0 1 0 0 0 1 0 0 0 )
        matrix L450_CWIRE_L1_01 ( 1 0 0 0 1 0 0 0 1 0 6.2 0 )
        matrix L450_CWIRE_L1_02 ( 1 0 0 0 1 0 0 0 1 0 6.2 0 )
        matrix L450_CWIRE_L2_01 ( 1 0 0 0 1 0 0 0 1 0 6.2 0 )
        matrix M200_HEBEL_LR01 ( 0 -1 0 1 0 0 0 0 1 2.097 0.241 18.949 )
        matrix M200_STANGEN_LR01 ( 1 0 0 0 1 0 0 0 1 -0.111 0 18.702 )
        matrix M450_HEBEL_LR01 ( 1 0 0 0 1 0 0 0 1 2.097 0.241 18.884 )
        matrix M700_MSIGL1_M01 ( 1 0 0 0 1 0 0 0 1 2.097 -0.044 19.231 )
        matrix ZL01 ( 1 0 0 0 1 0 0 0 1 -0.828 0 35.076 )
        matrix ZL02 ( 1 0 -0.007 0 1 0 0.007 0 1 0.604 0 35.08 )
    )
    images ( 11
        image ( DB_Track10sw.ACE )
        image ( DB_Track1w.ACE )
        image ( DB_Rails10w.ACE )
        image ( DB_WL4b.ACE )
        image ( DB_Rails10w.ACE )
        image ( DB_Rails10w.ACE )
        image ( DB_WM1c.ACE )
        image ( DK_WM1m.ace )
        image ( DK_WS4a.ace )
        image ( DB_WM1s.ACE )
        image ( DB_Rails10w.ACE )
    )
    textures ( 15
        texture ( 0 1 -1 ff000000 )
        texture ( 1 1 -1 ff000000 )
        texture ( 2 1 0 ff000000 )
        texture ( 2 1 -1 ff000000 )
        texture ( 3 0 0 ff000000 )
        texture ( 4 1 -1 ff000000 )
        texture ( 5 0 -1 ff000000 )
        texture ( 6 1 -1 ff000000 )
        texture ( 7 1 -1 ff000000 )
        texture ( 8 1 0 ff000000 )
        texture ( 8 1 -1 ff000000 )
        texture ( 9 1 0 ff000000 )
        texture ( 10 1 0 ff000000 )
        texture ( 10 1 -1 ff000000 )
        texture ( 0 0 0 ff000000 )
    )
    light_materials ( 0 )
    light_model_cfgs ( 1
        light_model_cfg ( 00000000
            uv_ops ( 1
                uv_op_copy ( 1 0 )
            )
        )
    )
    vtx_states ( 12
        vtx_state ( 00000000 0 -5 0 00000002 )
        vtx_state ( 00000000 0 -12 0 00000002 )
        vtx_state ( 00000000 1 -5 0 00000002 )
        vtx_state ( 00000000 2 -5 0 00000002 )
        vtx_state ( 00000000 3 -5 0 00000002 )
        vtx_state ( 00000000 4 -5 0 00000002 )
        vtx_state ( 00000000 5 -5 0 00000002 )
        vtx_state ( 00000000 6 -5 0 00000002 )
        vtx_state ( 00000000 7 -5 0 00000002 )
        vtx_state ( 00000000 7 -11 0 00000002 )
        vtx_state ( 00000000 8 -5 0 00000002 )
        vtx_state ( 00000000 9 -5 0 00000002 )
    )
    prim_states ( 30
        prim_state Rails ( 00000000 0
            tex_idxs ( 1 3 ) 0 0 0 0 1
        )
        prim_state TClamp01 ( 00000000 1
            tex_idxs ( 1 3 ) 0 0 1 0 1
        )
        prim_state Rails ( 00000000 0
            tex_idxs ( 1 3 ) 0 6 0 0 1
        )
        prim_state Rails ( 00000000 0
            tex_idxs ( 1 3 ) 0 10 0 0 1
        )
        prim_state Rails ( 00000000 0
            tex_idxs ( 1 3 ) 0 11 0 0 1
        )
        prim_state DB_WM1c ( 00000000 0
            tex_idxs ( 1 7 ) 0 0 0 0 1
        )
    )
    """


@pytest.fixture
def invalid_textures_count():
    return """
    textures ( 30
        texture ( 0 1 -1 ff000000 )
        texture ( 1 1 -1 ff000000 )
        texture ( 2 1 0 ff000000 )
        texture ( 2 1 -1 ff000000 )
        texture ( 3 0 0 ff000000 )
        texture ( 4 1 -1 ff000000 )
        texture ( 5 0 -1 ff000000 )
        texture ( 6 1 -1 ff000000 )
        texture ( 7 1 -1 ff000000 )
        texture ( 8 1 0 ff000000 )
        texture ( 8 1 -1 ff000000 )
        texture ( 9 1 0 ff000000 )
        texture ( 10 1 0 ff000000 )
        texture ( 10 1 -1 ff000000 )
        texture ( 0 0 0 ff000000 )
    )
    """


def test_extract_block(parser, valid_shape_text):
    block = parser._extract_block(valid_shape_text, "matrices")
    expected = """    matrices ( 10
        matrix PNT5D_L01 ( 1 0 0 0 1 0 0 0 1 0 0 0 )
        matrix L450_CWIRE_L1_01 ( 1 0 0 0 1 0 0 0 1 0 6.2 0 )
        matrix L450_CWIRE_L1_02 ( 1 0 0 0 1 0 0 0 1 0 6.2 0 )
        matrix L450_CWIRE_L2_01 ( 1 0 0 0 1 0 0 0 1 0 6.2 0 )
        matrix M200_HEBEL_LR01 ( 0 -1 0 1 0 0 0 0 1 2.097 0.241 18.949 )
        matrix M200_STANGEN_LR01 ( 1 0 0 0 1 0 0 0 1 -0.111 0 18.702 )
        matrix M450_HEBEL_LR01 ( 1 0 0 0 1 0 0 0 1 2.097 0.241 18.884 )
        matrix M700_MSIGL1_M01 ( 1 0 0 0 1 0 0 0 1 2.097 -0.044 19.231 )
        matrix ZL01 ( 1 0 0 0 1 0 0 0 1 -0.828 0 35.076 )
        matrix ZL02 ( 1 0 -0.007 0 1 0 0.007 0 1 0.604 0 35.08 )
    )"""
    assert expected == block


def test_extract_block_with_nesting(parser, valid_shape_text):
    block = parser._extract_block(valid_shape_text, "light_model_cfgs")
    expected = """    light_model_cfgs ( 1
        light_model_cfg ( 00000000
            uv_ops ( 1
                uv_op_copy ( 1 0 )
            )
        )
    )"""
    assert expected == block


def test_extract_empty_block(parser, valid_shape_text):
    block = parser._extract_block(valid_shape_text, "colours")
    expected = "\n    colours ( 0 )"
    assert expected == block


def test_parse_items_in_block(parser, valid_shape_text):
    block = parser._extract_block(valid_shape_text, "vtx_states")
    items = parser._parse_items_in_block(block, "vtx_states", "vtx_state", parser)
    assert items.expected_count == 12
    assert len(items.items) == 12
    assert items.items[1] == "vtx_state ( 00000000 0 -12 0 00000002 )"


def test_parse_named_items_in_block(parser, valid_shape_text):
    block = parser._extract_block(valid_shape_text, "matrices")
    items = parser._parse_named_items_in_block(block, "matrices", "matrix", parser)
    assert items.expected_count == 10
    assert len(items.items) == 10
    assert items.items[0] == "matrix PNT5D_L01 ( 1 0 0 0 1 0 0 0 1 0 0 0 )"


def test_parse_items_in_block_with_nesting(parser, valid_shape_text):
    block = parser._extract_block(valid_shape_text, "light_model_cfgs")
    items = parser._parse_items_in_block(block, "light_model_cfgs", "light_model_cfg", parser)
    expected_item = """light_model_cfg ( 00000000
            uv_ops ( 1
                uv_op_copy ( 1 0 )
            )
        )"""
    assert items.expected_count == 1
    assert len(items.items) == 1
    assert items.items[0] == expected_item


def test_parse_values_images(parser, valid_shape_text):
    block = parser._extract_block(valid_shape_text, "images")
    items = parser._extract_items_in_block(block, "images", "image")
    assert items.expected_count == 11
    assert len(items.items) == 11
    assert "DB_Rails10w.ACE" in items.items[-1]


def test_parse_values_textures(parser, valid_shape_text):
    block = parser._extract_block(valid_shape_text, "textures")
    items = parser._extract_items_in_block(block, "textures", "texture")
    assert items.expected_count == 15
    assert len(items.items) == 15


@pytest.mark.parametrize("bad_input", [
    "image ( DB_Track1w.ACE )",  # Keyword not present
    "colours 0.0 0.0 0.0 0.0",   # Missing parentheses
    "colours ( 0",   # Unmatched parentheses
])
def test_extract_block(parser, bad_input):
    with pytest.raises(ShapeParserError):
        parser._extract_block(bad_input, "colours")


def test_parse_values_textures(parser, invalid_textures_count):
    block = parser._extract_block(invalid_textures_count, "textures")
    with pytest.raises(CountMismatchError):
        parser._extract_items_in_block(block, "textures", "texture")


def test_parse_values_textures_verify_count_false(parser, invalid_textures_count):
    block = parser._extract_block(invalid_textures_count, "textures")
    items = parser._extract_items_in_block(block, "textures", "texture", verify_count=False)
    assert items.expected_count == 30
    assert len(items.items) == 15


def test_extract_block_verify_block_false(parser, valid_shape_text):
    block = parser._extract_block(valid_shape_text, "animations", verify_block=False)
    assert block is None