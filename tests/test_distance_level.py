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

# from shapeio.shape import DistanceLevel, DistanceLevelHeader
# from shapeio.decoder import _DistanceLevelParser, BlockFormatError
# from shapeio.encoder import _DistanceLevelSerializer


# @pytest.fixture
# def parser():
#     return _DistanceLevelParser()


# @pytest.fixture
# def serializer():
#     return _DistanceLevelSerializer()


# def test_parse_distance_level_empty(parser):
#     text = """
#     distance_level (
#         distance_level_header (
#             dlevel_selection ( 123 )
#             hierarchy ( 10 -1 0 0 0 0 0 0 0 0 0 )
#         )
#         sub_objects ( 0
#         )
#     )
#     """
#     dlevel = parser.parse(text)
#     assert isinstance(dlevel, DistanceLevel)
#     assert isinstance(dlevel.distance_level_header, DistanceLevelHeader)
#     assert dlevel.distance_level_header.dlevel_selection == 123
#     assert isinstance(dlevel.sub_objects, list)
#     assert len(dlevel.sub_objects) == 0


# def test_serialize_distance_level_empty(serializer):
#     dlevel = DistanceLevel(
#         distance_level_header=DistanceLevelHeader(
#             dlevel_selection=123,
#             hierarchy=[10, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
#         ),
#         sub_objects=[]
#     )
#     result = serializer.serialize(dlevel, depth=0)

#     expected = (
#         "distance_level (\n"
#         "    distance_level_header (\n"
#         "        dlevel_selection ( 123 )\n"
#         "        hierarchy ( 10 -1 0 0 0 0 0 0 0 0 0 )\n"
#         "    )\n"
#         "    sub_objects ( 0\n"
#         "    )\n"
#         ")"
#     )
#     assert result.strip() == expected.strip()


# @pytest.mark.parametrize("bad_input", [
#     "distance_level ( distance_level_header ( ) )",  # Missing sub_objects
#     "distance_level ( sub_objects ( 0 ) )",          # Missing header
#     "distance_level ( )",                            # Empty block
# ])
# def test_parse_invalid_distance_level_raises(parser, bad_input):
#     with pytest.raises(BlockFormatError):
#         parser.parse(bad_input)
