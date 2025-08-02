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

from shapeio.shape import VolumeSphere, Vector
from shapeio.decoder import _VolumeSphereParser, BlockFormatError
from shapeio.encoder import _VolumeSphereSerializer


@pytest.fixture
def parser():
    return _VolumeSphereParser()


@pytest.fixture
def serializer():
    return _VolumeSphereSerializer()


def test_parse_vol_sphere(parser):
    text = "vol_sphere ( vector ( -1.23867 0.495151 40 ) 40.1839 )"
    vs = parser.parse(text)
    assert isinstance(vs, VolumeSphere)
    assert vs.vector.x == -1.23867
    assert vs.vector.y == 0.495151
    assert vs.vector.z == 40
    assert vs.radius == 40.1839


def test_serialize_vol_sphere(serializer):
    vs = VolumeSphere(Vector(-1.23, 0.49, 40.0), 41.1)
    result = serializer.serialize(vs, depth=1)
    expected = (
        "\tvol_sphere (\n"
        "\t\tvector ( -1.23 0.49 40 ) 41.1\n"
        "\t)"
    )
    assert result == expected


@pytest.mark.parametrize("bad_text", [
    "volsphere ( vector ( 1 2 3 ) 4 )",            # wrong keyword
    "vol_sphere ( vector ( 1 2 ) 3 )",             # missing coordinate
    "vol_sphere ( vector ( 1 2 3 ) )",             # missing radius
    "vol_sphere ( 1 2 3 4 )",                      # no vector keyword
])
def test_parse_invalid_vol_sphere_raises(parser, bad_text):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_text)