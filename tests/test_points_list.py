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
from shapeio.decoder import _PointsListParser, _PointParser
from shapeio.encoder import _PointsListSerializer, _PointSerializer


@pytest.fixture
def parser():
    return _PointsListParser()


@pytest.fixture
def serializer():
    return _PointsListSerializer()


def test_serialize_points_list(serializer):
    points = [
        Point(1.0, 2.0, 3.0),
        Point(4.0, 5.0, 6.0)
    ]
    expected = (
        "points ( 2\n"
        "    point ( 1.0 2.0 3.0 )\n"
        "    point ( 4.0 5.0 6.0 )\n"
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


def test_serialize_with_depth_and_tabs():
    serializer = _PointsListSerializer(indent=1, use_tabs=True)
    points = [
        Point(1.0, 2.0, 3.0),
        Point(4.0, 5.0, 6.0)
    ]
    result = serializer.serialize(points, depth=2)
    expected = (
        "\t\tpoints ( 2\n"
        "\t\t\tpoint ( 1.0 2.0 3.0 )\n"
        "\t\t\tpoint ( 4.0 5.0 6.0 )\n"
        "\t\t)"
    )
    assert result == expected


def test_round_trip_parse_and_serialize(parser, serializer):
    input_text = """
    points ( 2
        point ( 10.0 20.0 30.0 )
        point ( -1.0 -2.0 -3.0 )
    )
    """
    points = parser.parse(input_text)
    output = serializer.serialize(points, depth=0)
    assert "points ( 2" in output
    assert "point ( 10.0 20.0 30.0 )" in output
    assert "point ( -1.0 -2.0 -3.0 )" in output
