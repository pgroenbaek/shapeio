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

from shapeio.shape import LightModelCfg
from shapeio.decoder import _LightModelCfgParser
from shapeio.encoder import _LightModelCfgSerializer


@pytest.fixture
def serializer():
    return _LightModelCfgSerializer()


@pytest.fixture
def parser():
    return _LightModelCfgParser()


def test_serialize_light_model_cfg(serializer):
    cfg = LightModelCfg(
        flags="000000ff",
        uv_ops=[]
    )
    expected = (
        "light_model_cfg ( 000000ff\n"
        "\tuv_ops ( 0 )\n"
        ")"
    )
    assert serializer.serialize(cfg, depth=0) == expected


def test_parse_light_model_cfg(parser):
    text = """
    light_model_cfg ( 000000ab
        uv_ops ( 1
            uv_op_copy ( 1 3 )
        )
    )
    """
    cfg = parser.parse(text)
    assert cfg.flags == "000000ab"
    assert len(cfg.uv_ops) == 1
    op = cfg.uv_ops[0]
    assert op.__class__.__name__ == "UVOpCopy"
    assert op.texture_address_mode == 1
    assert op.source_uv_index == 3


@pytest.mark.parametrize("bad_input", [
    "light_model_cfg ( GARBAGE uv_ops ( 1 uv_op_copy ( 1 2 ) ) )",
    "light_model_cfg ( 000000FF uv_ops ( 1 ) )",  # Missing op
    "light_model_cfg ( 000000FF )",  # No uv_ops
])
def test_parse_invalid_light_model_cfg_raises(parser, bad_input):
    with pytest.raises(ValueError):
        parser.parse(bad_input)
