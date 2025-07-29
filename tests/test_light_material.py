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

from shapeio.shape import LightMaterial
from shapeio.decoder import _LightMaterialParser
from shapeio.encoder import _LightMaterialSerializer


@pytest.fixture
def parser():
    return _LightMaterialParser()


@pytest.fixture
def serializer():
    return _LightMaterialSerializer()


def test_parse_light_material(parser):
    text = "light_material ( ff000000 1 2 3 4 2.2 )"
    mat = parser.parse(text)
    assert mat.flags.lower() == "ff000000"
    assert mat.diff_colour_index == 1
    assert mat.amb_colour_index == 2
    assert mat.spec_colour_index == 3
    assert mat.emissive_colour_index == 4
    assert mat.spec_power == 2.2


def test_parse_light_material_with_whitespace(parser):
    text = "  light_material (  deadbeef   0  0  0  0  1.0 )  "
    mat = parser.parse(text)
    assert mat.flags.lower() == "deadbeef"
    assert mat.diff_colour_index == 0
    assert mat.amb_colour_index == 0
    assert mat.spec_colour_index == 0
    assert mat.emissive_colour_index == 0
    assert mat.spec_power == 1.0


def test_serialize_light_material(serializer):
    mat = LightMaterial("ABCDEF12", 1, 2, 3, 4, 5.5)
    result = serializer.serialize(mat)
    assert result == "light_material ( abcdef12 1 2 3 4 5.5 )"


def test_serialize_light_material_with_depth(serializer):
    mat = LightMaterial("FF000000", 0, 1, 2, 3, 4.0)
    result = serializer.serialize(mat, depth=1)
    assert result == "\tlight_material ( ff000000 0 1 2 3 4 )"


@pytest.mark.parametrize("bad_input", [
    "light_material ( ff000000 1 2 3 4 )",         # Too few values
    "light_material ( ff000000 1 2 3 4 5 6 )",     # Too many values
    "light_material ( gg000000 1 2 3 4 1.0 )",     # Invalid hex
    "lightmaterial ( ff000000 1 2 3 4 1.0 )",      # Wrong keyword
    "light_material  ff000000 1 2 3 4 1.0",        # Missing parentheses
])
def test_parse_invalid_light_material_raises(parser, bad_input):
    with pytest.raises(ValueError):
        parser.parse(bad_input)

