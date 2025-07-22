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

from shapeio.shape import Vector
from shapeio.decoder import _VectorParser
from shapeio.encoder import _VectorSerializer

serializer = _VectorSerializer()
parser = _VectorParser()

def test_serialize_vector():
    vector = Vector(1.0, 2.0, 3.0)
    assert serializer.serialize(vector) == "vector ( 1.0 2.0 3.0 )"

def test_parse_vector():
    text = "vector ( 1.0 2.0 3.0 )"
    vector = parser.parse(text)
    assert vector.x == 1.0
    assert vector.y == 2.0
    assert vector.z == 3.0

def test_parse_vector_with_whitespace():
    text = "  vector (   -1.5  0.0   42.75 )  "
    vector = parser.parse(text)
    assert vector.x == -1.5
    assert vector.y == 0.0
    assert vector.z == 42.75

@pytest.mark.parametrize("bad_input", [
    "vector ( 1.0 2.0 )",          # Too few components
    "vector ( 1.0 2.0 3.0 4.0 )",  # Too many components
    "vect ( 1.0 2.0 3.0 )",        # Incorrect keyword
    "vector 1.0 2.0 3.0",          # Missing parentheses
])
def test_parse_invalid_vector_raises(bad_input):
    with pytest.raises(ValueError):
        parser.parse(bad_input)
