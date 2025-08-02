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

from shapeio.shape import Matrix
from shapeio.decoder import _MatrixParser, BlockFormatError
from shapeio.encoder import _MatrixSerializer


@pytest.fixture
def serializer():
    return _MatrixSerializer()


@pytest.fixture
def parser():
    return _MatrixParser()


def test_serialize_matrix(serializer):
    matrix = Matrix(
        "transform",
        1.0, 0.0, 0.0,
        0.0, 1.0, 0.0,
        0.0, 0.0, 1.0,
        10.2, 20.0, 30.6
    )
    expected = (
        "matrix transform ( 1 0 0 "
        "0 1 0 "
        "0 0 1 "
        "10.2 20 30.6 )"
    )
    assert serializer.serialize(matrix) == expected


def test_parse_matrix(parser):
    text = "matrix transform ( 1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0 10.0 20.0 30.0 )"
    matrix = parser.parse(text)
    assert matrix.name == "transform"
    assert matrix.ax == 1.0
    assert matrix.bx == 0.0
    assert matrix.cz == 1.0
    assert matrix.dx == 10.0
    assert matrix.dz == 30.0


def test_parse_matrix_with_whitespace(parser):
    text = "   matrix  move  (  -1.0  0.0 0.0    0.0  -1.0 0.0   0.0 0.0 -1.0   5.5   6.6  7.7 )   "
    matrix = parser.parse(text)
    assert matrix.name == "move"
    assert matrix.ax == -1.0
    assert matrix.by == -1.0
    assert matrix.cz == -1.0
    assert matrix.dx == 5.5
    assert matrix.dz == 7.7


@pytest.mark.parametrize("bad_input", [
    "matrix transform ( 1.0 0.0 )",                         # Too few values
    "matrix transform ( 1.0 0.0 0.0 0.0 1.0 0.0 )",         # Still too few
    "matrix transform ( " + " ".join(["1.0"] * 13) + " )",  # Too many
    "matri transform ( 1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0 10.0 20.0 30.0 )",  # Typo in keyword
    "matrix ( 1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0 10.0 20.0 30.0 )",           # Missing name
    "matrix transform 1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0 10.0 20.0 30.0",     # Missing parentheses
])
def test_parse_invalid_matrix_raises(parser, bad_input):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_input)


def test_serialize_matrix_with_depth_and_spaces():
    serializer = _MatrixSerializer(indent=2, use_tabs=False)
    matrix = Matrix(
        "m", 1, 2, 3,
        4, 5, 6,
        7, 8, 9,
        10, 11, 12
    )
    result = serializer.serialize(matrix, depth=2)
    expected = "    matrix m ( 1 2 3 4 5 6 7 8 9 10 11 12 )"
    assert result == expected