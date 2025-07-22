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
from abc import ABC, abstractmethod
from typing import List

from . import shape


class ShapeDecoder:
    def __init__(self):
        pass

    def decode(self, text: str) -> shape.Shape:
        return _ShapeParser().parse(text)


class _Parser(ABC):
    @abstractmethod
    def parse(self, text: str) -> object:
        pass


class _VectorParser(_Parser):
    VECTOR_PATTERN = re.compile(r'vector\s*\(\s*([-+eE\d\.]+)\s+([-+eE\d\.]+)\s+([-+eE\d\.]+)\s*\)')

    def parse(self, text: str) -> shape.Vector:
        match = self.VECTOR_PATTERN.match(text.strip())
        if not match:
            raise ValueError(f"Invalid vector format: '{text}'")

        x, y, z = map(float, match.groups())
        return shape.Vector(x, y, z)


class _PointParser(_Parser):
    POINT_PATTERN = re.compile(r'point\s*\(\s*([-+eE\d\.]+)\s+([-+eE\d\.]+)\s+([-+eE\d\.]+)\s*\)')

    def parse(self, text: str) -> shape.Point:
        match = self.POINT_PATTERN.match(text.strip())
        if not match:
            raise ValueError(f"Invalid point format: '{text}'")

        x, y, z = map(float, match.groups())
        return shape.Point(x, y, z)


class _UVPointParser(_Parser):
    UVPOINT_PATTERN = re.compile(r'uv_point\s*\(\s*([-+eE\d\.]+)\s+([-+eE\d\.]+)\s*\)')

    def parse(self, text: str) -> shape.UVPoint:
        match = self.UVPOINT_PATTERN.match(text.strip())
        if not match:
            raise ValueError(f"Invalid uv_point format: '{text}'")

        u, v = map(float, match.groups())
        return shape.UVPoint(u, v)


class _ColourParser(_Parser):
    COLOUR_PATTERN = re.compile(r'colour\s*\(\s*([-+eE\d\.]+)\s+([-+eE\d\.]+)\s+([-+eE\d\.]+)\s+([-+eE\d\.]+)\s*\)')

    def parse(self, text: str) -> shape.Colour:
        match = self.COLOUR_PATTERN.match(text.strip())
        if not match:
            raise ValueError(f"Invalid colour format: '{text}'")

        a, r, g, b = map(float, match.groups())
        return shape.Colour(a, r, g, b)


class _PointsListParser(_Parser):
    POINT_PARSER = _PointParser()
    POINTS_LIST_PATTERN = re.compile(
        r'points\s*\(\s*(\d+)\s*((?:point\s*\([^)]*\)\s*)+)\)', re.DOTALL
    )
    POINT_BLOCK_PATTERN = _PointParser.POINT_PATTERN

    def parse(self, text: str) -> List[shape.Point]:
        text = text.strip()
        match = self.POINTS_LIST_PATTERN.match(text)
        if not match:
            raise ValueError(f"Invalid points block: '{text}'")

        count = int(match.group(1))
        body = match.group(2)

        matches = list(self.POINT_BLOCK_PATTERN.finditer(body))
        if len(matches) != count:
            raise ValueError(f"Expected {count} points, but found {len(matches)}")

        return [self.POINT_PARSER.parse(m.group(0)) for m in matches]


