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

from shapeio.shape import SubObjectHeader, Point, GeometryInfo
from shapeio.decoder import _SubObjectHeaderParser, BlockFormatError
from shapeio.encoder import _SubObjectHeaderSerializer


@pytest.fixture
def serializer():
    return _SubObjectHeaderSerializer()


@pytest.fixture
def parser():
    return _SubObjectHeaderParser()


def test_serialize_sub_object_header(serializer):
    header = SubObjectHeader(
        flags="00000400",
        sort_vector_index=6,
        volume_index=7,
        source_vtx_fmt_flags="000001d2",
        destination_vtx_fmt_flags="000001c4",
        geometry_info=GeometryInfo(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, [], []),
        subobject_shaders=[],
        subobject_light_cfgs=[],
        subobject_id=1
    )
    result = serializer.serialize(header, depth=1)
    assert result.startswith(
        "\tsub_object_header ( 00000400 6 7 000001d2 000001c4"
    )
    assert result.strip().endswith("1\n\t)")


def test_parse_sub_object_header(parser):
    text = """
        sub_object_header ( 00000400 6 7 000001d2 000001c4
            geometry_info ( 126 2 0 378 0 0 2 0 0 0
                geometry_nodes ( 1
                    geometry_node ( 2 0 0 0 0
                        cullable_prims ( 2 126 378 )
                    )
                )
                geometry_node_map ( 10 0 -1 -1 -1 -1 -1 -1 -1 -1 -1 )
            )
            subobject_shaders ( 1 1 )
            subobject_light_cfgs ( 1 0 ) 1
        )
    """
    header = parser.parse(text)
    assert header.flags == "00000400"
    assert header.sort_vector_index == 6
    assert header.volume_index == 7
    assert header.source_vtx_fmt_flags == "000001d2"
    assert header.destination_vtx_fmt_flags == "000001c4"
    assert header.subobject_id == 1


@pytest.mark.parametrize("bad_input", [
    "sub_object_header ( 00000400 6 7 )",  # Too few fields
    "subobj_header ( 00000400 6 7 000001d2 000001c4 )",  # Wrong keyword
    "sub_object_header 00000400 6 7 000001d2 000001c4",  # Missing parentheses
])
def test_parse_invalid_sub_object_header_raises(parser, bad_input):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_input)


@pytest.mark.parametrize("bad_input", [
    123,
    "not a SubObjectHeader",
    Point(1.0, 2.0, 3.0)
])
def test_serialize_invalid_type_raises(serializer, bad_input):
    with pytest.raises(TypeError):
        serializer.serialize(bad_input)


def test_serialize_sub_object_header_with_depth_and_spaces():
    serializer = _SubObjectHeaderSerializer(indent=2, use_tabs=False)
    header = SubObjectHeader(
        flags="00000400",
        sort_vector_index=6,
        volume_index=7,
        source_vtx_fmt_flags="000001d2",
        destination_vtx_fmt_flags="000001c4",
        geometry_info=GeometryInfo(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, [], []),
        subobject_shaders=[],
        subobject_light_cfgs=[],
        subobject_id=1
    )
    result = serializer.serialize(header, depth=2)
    assert result.startswith(
        "    sub_object_header ( 00000400 6 7 000001d2 000001c4"
    )
    assert result.strip().endswith("1\n    )")
