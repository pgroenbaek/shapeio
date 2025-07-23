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

import re
import regex
from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, Pattern

from . import shape

T = TypeVar('T')


class ShapeDecoder:
    def __init__(self):
        pass

    def decode(self, text: str) -> shape.Shape:
        return _ShapeParser().parse(text)


class _Parser(ABC, Generic[T]):
    @abstractmethod
    def parse(self, text: str) -> T:
        pass


class _VectorParser(_Parser[shape.Vector]):
    VECTOR_PATTERN = re.compile(r'vector\s*\(\s*([-+eE\d\.]+)\s+([-+eE\d\.]+)\s+([-+eE\d\.]+)\s*\)')

    def parse(self, text: str) -> shape.Vector:
        match = self.VECTOR_PATTERN.match(text.strip())
        if not match:
            raise ValueError(f"Invalid vector format: '{text}'")

        x, y, z = map(float, match.groups())
        return shape.Vector(x, y, z)


class _PointParser(_Parser[shape.Point]):
    POINT_PATTERN = re.compile(r'point\s*\(\s*([-+eE\d\.]+)\s+([-+eE\d\.]+)\s+([-+eE\d\.]+)\s*\)')

    def parse(self, text: str) -> shape.Point:
        match = self.POINT_PATTERN.match(text.strip())
        if not match:
            raise ValueError(f"Invalid point format: '{text}'")

        x, y, z = map(float, match.groups())
        return shape.Point(x, y, z)


class _UVPointParser(_Parser[shape.UVPoint]):
    UVPOINT_PATTERN = re.compile(r'uv_point\s*\(\s*([-+eE\d\.]+)\s+([-+eE\d\.]+)\s*\)')

    def parse(self, text: str) -> shape.UVPoint:
        match = self.UVPOINT_PATTERN.match(text.strip())
        if not match:
            raise ValueError(f"Invalid uv_point format: '{text}'")

        u, v = map(float, match.groups())
        return shape.UVPoint(u, v)


class _ColourParser(_Parser[shape.Colour]):
    COLOUR_PATTERN = re.compile(r'colour\s*\(\s*([-+eE\d\.]+)\s+([-+eE\d\.]+)\s+([-+eE\d\.]+)\s+([-+eE\d\.]+)\s*\)')

    def parse(self, text: str) -> shape.Colour:
        match = self.COLOUR_PATTERN.match(text.strip())
        if not match:
            raise ValueError(f"Invalid colour format: '{text}'")

        a, r, g, b = map(float, match.groups())
        return shape.Colour(a, r, g, b)


class _MatrixParser(_Parser[shape.Matrix]):
    MATRIX_PATTERN = re.compile(r'matrix\s+(\S+)\s*\(\s*([-+eE\d\.]+(?:\s+[-+eE\d\.]+){11})\s*\)')

    def parse(self, text: str) -> shape.Matrix:
        match = self.MATRIX_PATTERN.match(text.strip())
        if not match:
            raise ValueError(f"Invalid matrix format: '{text}'")

        name = match.group(1)
        values = list(map(float, match.group(2).split()))
        if len(values) != 12:
            raise ValueError(f"Expected 12 values, got {len(values)}")
        
        return shape.Matrix(name, *values)


class _ListParser(_Parser[List[T]]):
    def __init__(self,
        list_name: str,
        item_name: str,
        item_parser: _Parser[T],
        item_pattern: Pattern,
    ):
        self.list_name = list_name
        self.item_name = item_name
        self.item_parser = item_parser
        self.item_pattern = item_pattern

        list_pattern_str = (
            rf'{re.escape(list_name)}\s*\(\s*(\d+)\s*'
            rf'((?:{re.escape(item_name)}\s*\([^)]*\)\s*)+)\)'
        )
        self.list_pattern = re.compile(list_pattern_str, re.DOTALL)

    def parse(self, text: str) -> List[T]:
        text = text.strip()
        match = self.list_pattern.match(text)
        if not match:
            raise ValueError(f"Invalid {self.list_name} block: '{text}'")

        count = int(match.group(1))
        body = match.group(2)

        matches = list(self.item_pattern.finditer(body))
        if len(matches) != count:
            raise ValueError(f"Expected {count} {self.list_name}, but found {len(matches)}")

        return [self.item_parser.parse(m.group(0)) for m in matches]
