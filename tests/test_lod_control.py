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

# from shapeio.shape import LodControl, DistanceLevelsHeader, Point
# from shapeio.decoder import _LodControlParser, BlockFormatError
# from shapeio.encoder import _LodControlSerializer


# @pytest.fixture
# def serializer():
#     return _LodControlSerializer()


# @pytest.fixture
# def parser():
#     return _LodControlParser()


# def test_serialize_lod_control_empty(serializer):
#     lod = LodControl(
#         distance_levels_header=DistanceLevelsHeader(dlevel_bias=0),
#         distance_levels=[]
#     )

#     result = serializer.serialize(lod, depth=0)
#     expected = (
#         "lod_control (\n"
#         "\tdistance_levels_header ( 0 )\n"
#         "\tdistance_levels ( 0\n"
#         "\t)\n"
#         ")"
#     )
#     assert result.strip() == expected.strip()


# def test_parse_lod_control_empty(parser):
#     text = """
#     lod_control (
#         distance_levels_header ( 3 )
#         distance_levels ( 0
#         )
#     )
#     """
#     lod = parser.parse(text)
#     assert isinstance(lod, LodControl)
#     assert lod.distance_levels_header.dlevel_bias == 3
#     assert isinstance(lod.distance_levels, list)
#     assert len(lod.distance_levels) == 0


# @pytest.mark.parametrize("bad_input", [
#     "lod_control ( distance_levels_header ( ) distance_levels ( 0 ) )",  # missing int
#     "lod_control ( distance_levels_header ( 1 ) )",  # no distance_levels block
#     "lod_control ( distance_levels ( 1 ) )",  # missing header
#     "lod_control ( )",  # completely empty
# ])
# def test_parse_invalid_lod_control_raises(parser, bad_input):
#     with pytest.raises(BlockFormatError):
#         parser.parse(bad_input)


#@pytest.mark.parametrize("bad_input", [
#    Point(1.0, 2.2, 3.2),
#])
#def test_serialize_invalid_type_raises(serializer, bad_input):
#    with pytest.raises(TypeError):
#        serializer.serialize(bad_input)
