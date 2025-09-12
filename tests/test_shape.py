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

from shapeio.shape import Shape
from shapeio.decoder import ShapeDecoder
from shapeio.encoder import ShapeEncoder


def load_shape(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-16-le') as f:
        return f.read()


def save_shape(filepath: str, content: str) -> None:
    with open(filepath, 'w', encoding='utf-16-le') as f:
        f.write(content)


@pytest.fixture
def decoder():
    return ShapeDecoder()


@pytest.fixture
def encoder():
    return ShapeEncoder()


def test_round_trip_decode_and_encode(global_storage, decoder, encoder):
    shape = decoder.decode(global_storage["shape"])
    text = encoder.encode(shape)
    save_shape("./tests/data/DK10f_A1tPnt5dLft_serialized.s", text)
    #original_shape = load_shape("./tests/data/DK10f_A1tPnt5dLft.s")
    #serialized_shape = load_shape("./tests/data/DK10f_A1tPnt5dLft_serialized.s")
    #assert original_shape == serialized_shape

