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

from shapeio.shape import Point
from shapeio.decoder import _ListParser, _PointParser
from shapeio.encoder import _ListSerializer, _PointSerializer


@pytest.fixture
def parser():
    return _ListParser(
        list_name="points",
        item_name="point",
        item_parser=_PointParser(),
        item_pattern=_PointParser.POINT_PATTERN,
    )

@pytest.fixture
def serializer():
    return _ListSerializer(
        list_name="points",
        item_serializer=_PointSerializer()
    )


def test_serialize_points_list(serializer):
    points = [
        Point(1.2, 2.2, 3.2),
        Point(4.0, 5.4, 6.0)
    ]
    expected = (
        "points ( 2\n"
        "\tpoint ( 1.2 2.2 3.2 )\n"
        "\tpoint ( 4 5.4 6 )\n"
        ")"
    )
    output = serializer.serialize(points, depth=0)
    assert output == expected


def test_parse_points_list(parser):
    text = """
    points ( 2
        point ( 1.0 2.0 3.0 )
        point ( 4.0 5.0 6.0 )
    )
    """
    points = parser.parse(text)
    assert len(points) == 2
    assert points[0].x == 1.0
    assert points[1].z == 6.0


def test_parse_points_list_with_indentation_and_whitespace(parser):
    text = """
        points ( 2
            point ( -1.0   0.0    3.5 )
            point ( 4.0 5.5 6.75 )
        )
    """
    points = parser.parse(text)
    assert len(points) == 2
    assert points[0].x == -1.0
    assert points[1].z == 6.75

@pytest.mark.parametrize("bad_text", [
    "",  # Empty
    "points ()",  # No count
    "points ( 2 )",  # No points
    "points ( 1\n    point ( 1.0 2.0 )\n)",  # Malformed point
    "points ( 2\n    point ( 1.0 2.0 3.0 )\n)",  # Count mismatch
    "pints ( 1\n    point ( 1.0 2.0 3.0 )\n)",  # Misspelled keyword
])
def test_parse_invalid_points_list_raises(parser, bad_text):
    with pytest.raises(ValueError):
        parser.parse(bad_text)


def test_serialize_with_depth_and_spaces():
    serializer = _ListSerializer(
        list_name="points",
        item_serializer=_PointSerializer(indent=2, use_tabs=False),
        indent=2,
        use_tabs=False
    )
    points = [
        Point(1.2, 2.4, 3.6),
        Point(4.8, 5.0, 6.0)
    ]
    result = serializer.serialize(points, depth=2)
    expected = (
        "    points ( 2\n"
        "      point ( 1.2 2.4 3.6 )\n"
        "      point ( 4.8 5 6 )\n"
        "    )"
    )
    assert result == expected


def test_round_trip_parse_and_serialize(parser, serializer):
    input_text = """
    points ( 2
        point ( 10.7 20.7 30.7 )
        point ( -1.0 -2.0 -3.3 )
    )
    """
    points = parser.parse(input_text)
    output = serializer.serialize(points, depth=0)
    assert "points ( 2" in output
    assert "point ( 10.7 20.7 30.7 )" in output
    assert "point ( -1 -2 -3.3 )" in output


def test_serialize_items_per_line_1_no_newline_after_header_no_newline_before_closing():
    serializer = _ListSerializer(
        list_name="points",
        item_serializer=_PointSerializer(),
        items_per_line=1,
        newline_after_header=False,
        newline_before_closing=False,
        indent=1,
        use_tabs=True,
    )
    points = [Point(1, 2, 3), Point(4, 5, 6), Point(7, 8, 9)]
    expected = (
        "points ( 3 point ( 1 2 3 ) point ( 4 5 6 ) point ( 7 8 9 ) )"
    )
    output = serializer.serialize(points)
    assert output == expected


def test_serialize_items_per_line_2_newline_after_header():
    serializer = _ListSerializer(
        list_name="points",
        item_serializer=_PointSerializer(),
        items_per_line=2,
        newline_after_header=True,
        newline_before_closing=True,
    )
    points = [Point(1, 2, 3), Point(4, 5, 6), Point(7, 8, 9), Point(10, 11, 12)]
    expected = (
        "points ( 4\n"
        "\tpoint ( 1 2 3 ) point ( 4 5 6 )\n"
        "\tpoint ( 7 8 9 ) point ( 10 11 12 )\n"
        ")"
    )
    output = serializer.serialize(points)
    assert output == expected


def test_serialize_items_per_line_3_no_newline_after_header_no_newline_before_closing():
    serializer = _ListSerializer(
        list_name="points",
        item_serializer=_PointSerializer(),
        items_per_line=3,
        newline_after_header=False,
        newline_before_closing=False,
        indent=1,
        use_tabs=True,
    )
    points = [
        Point(1, 2, 3), Point(4, 5, 6), Point(7, 8, 9),
        Point(10, 11, 12), Point(13, 14, 15), Point(16, 17, 18),
        Point(19, 20, 21)
    ]
    expected = (
        "points ( 7 "
        "point ( 1 2 3 ) point ( 4 5 6 ) point ( 7 8 9 )\n"
        "\tpoint ( 10 11 12 ) point ( 13 14 15 ) point ( 16 17 18 )\n"
        "\tpoint ( 19 20 21 ) )"
    )
    output = serializer.serialize(points)
    assert output == expected


def test_serialize_newline_after_header_false_newline_before_closing_true():
    serializer = _ListSerializer(
        list_name="points",
        item_serializer=_PointSerializer(),
        items_per_line=1,
        newline_after_header=False,
        newline_before_closing=True,
    )
    points = [Point(1, 2, 3), Point(4, 5, 6)]
    expected = (
        "points ( 2 point ( 1 2 3 )\n"
        "\tpoint ( 4 5 6 )\n"
        ")"
    )
    output = serializer.serialize(points)
    assert output == expected
