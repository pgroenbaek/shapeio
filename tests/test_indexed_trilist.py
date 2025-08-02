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

from shapeio.shape import VertexIdx, NormalIdx, IndexedTrilist
from shapeio.decoder import _IndexedTrilistParser, CountMismatchError
from shapeio.encoder import _IndexedTrilistSerializer


@pytest.fixture
def parser():
    return _IndexedTrilistParser()


@pytest.fixture
def serializer():
    return _IndexedTrilistSerializer(indent=1, use_tabs=True)


def test_parse_valid_indexed_trilist(parser):
    text = """indexed_trilist (
    \tvertex_idxs ( 24 6882 6884 6883 6884 6882 6885 6886 6888 6887 6888 6886 6889 6890 6892 6891 6892 6890 6893 6894 6896 6895 6896 6894 6891 )
    \tnormal_idxs ( 8 2404 3 2404 3 2467 3 2467 3 2181 3 2181 3 2183 3 2183 3 )
    \tflags ( 8 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 )
    )"""
    trilist = parser.parse(text)
    assert len(trilist.vertex_indexes) == 8
    assert trilist.vertex_indexes[0].vertex1_index == 6882
    assert trilist.vertex_indexes[0].vertex2_index == 6884
    assert trilist.vertex_indexes[0].vertex3_index == 6883
    assert trilist.vertex_indexes[-1].vertex1_index == 6896
    assert trilist.vertex_indexes[-1].vertex2_index == 6894
    assert trilist.vertex_indexes[-1].vertex3_index == 6891
    assert len(trilist.normal_indexes) == 8
    assert trilist.normal_indexes[0].index == 2404
    assert trilist.normal_indexes[0].unknown2 == 3
    assert trilist.normal_indexes[-1].index == 2183
    assert trilist.normal_indexes[-1].unknown2 == 3
    assert len(trilist.flags) == 8
    assert trilist.flags == [
        "00000000", "00000000", "00000000", "00000000",
        "00000000", "00000000", "00000000", "00000000"
    ]


def test_serialize_indexed_trilist(serializer):
    trilist = IndexedTrilist(
        vertex_indexes=[
            VertexIdx(1, 2, 3),
            VertexIdx(4, 5, 6),
        ],
        normal_indexes=[
            NormalIdx(7, 8),
            NormalIdx(9, 10),
        ],
        flags=["00000001", "00000002"]
    )
    expected = (
        "indexed_trilist (\n"
        "\tvertex_idxs ( 6 1 2 3 4 5 6 )\n"
        "\tnormal_idxs ( 2 7 8 9 10 )\n"
        "\tflags ( 2 00000001 00000002 )\n"
        ")"
    )
    result = serializer.serialize(trilist)
    assert expected == result


@pytest.mark.parametrize("bad_input", [
    "indexed_trilist (\n\tnormal_idxs ( 2 1 2 3 )\n\tvertex_idxs ( 1 2 3 )\n\tflags ( 1 00000000 )\n)" # normal_idxs count is 2, but only 3 values
])
def test_parse_invalid_normal_count_raises(parser, bad_input):
    with pytest.raises(CountMismatchError):
        parser.parse(bad_input)


def test_serialize_invalid_type_raises(serializer):
    with pytest.raises(TypeError):
        serializer.serialize("not a trilist")
