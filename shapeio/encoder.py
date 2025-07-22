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

from abc import ABC, abstractmethod

from . import shape


class ShapeEncoder:
    def __init__(self):
        pass

    def encode(self, obj: shape.Shape) -> str:
        header = "SIMISA@@@@@@@@@@JINX0s1t______\n\n"
        text = _ShapeSerializer().serialize(obj)

        return header + text


class Serializer(ABC):
    @abstractmethod
    def serialize(self, obj) -> str:
        pass


class _VectorSerializer(Serializer):
    def __init__(self, indent: int = 4, use_tabs: bool = False):
        char = "\t" if use_tabs else " "
        self.indent_unit = char * indent

    def serialize(self, vector: shape.Vector, depth: int = 0) -> str:
        indent = self.indent_unit * depth

        return f"{indent}vector ( {vector.x} {vector.y} {vector.z} )"


class _PointSerializer(Serializer):
    def __init__(self, indent: int = 4, use_tabs: bool = False):
        char = "\t" if use_tabs else " "
        self.indent_unit = char * indent

    def serialize(self, point: shape.Point, depth: int = 0) -> str:
        indent = self.indent_unit * depth

        return f"{indent}point ( {point.x} {point.y} {point.z} )"


class _UVPointSerializer(Serializer):
    def __init__(self, indent: int = 4, use_tabs: bool = False):
        char = "\t" if use_tabs else " "
        self.indent_unit = char * indent

    def serialize(self, uv_point: shape.UVPoint, depth: int = 0) -> str:
        indent = self.indent_unit * depth
        
        return f"{indent}uv_point ( {uv_point.u} {uv_point.v} )"


class _PointsListSerializer(Serializer):
    POINT_SERIALIZER = _PointSerializer()

    def __init__(self, indent: int = 4, use_tabs: bool = False):
        char = "\t" if use_tabs else " "
        self.indent_unit = char * indent

    def serialize(self, points: list[shape.Point], depth: int = 0) -> str:
        base_indent = self.indent_unit * depth
        inner_indent = self.indent_unit * (depth + 1)

        lines = [f"{base_indent}points ( {len(points)}"]
        for point in points:
            lines.append(f"{inner_indent}{self.POINT_SERIALIZER.serialize(point)}")
        lines.append(f"{base_indent})")

        return "\n".join(lines)
