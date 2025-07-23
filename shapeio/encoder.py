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
from typing import List, TypeVar, Generic

from . import shape

T = TypeVar('T')


class ShapeEncoder:
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        self.indent = indent
        self.use_tabs = use_tabs

    def encode(self, obj: shape.Shape) -> str:
        header = "SIMISA@@@@@@@@@@JINX0s1t______\n\n"
        text = _ShapeSerializer(indent=self.indent, use_tabs=self.use_tabs).serialize(obj)

        return header + text


class _Serializer(ABC, Generic[T]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        char = "\t" if use_tabs else " "
        self.indent_unit = char * indent

    def get_indent(self, depth: int = 0) -> str:
        return self.indent_unit * depth

    @abstractmethod
    def serialize(self, obj: T, depth: int = 0) -> str:
        pass


class _VectorSerializer(_Serializer[shape.Vector]):
    def serialize(self, vector: shape.Vector, depth: int = 0) -> str:
        indent = self.get_indent(depth)

        return f"{indent}vector ( {vector.x:.6g} {vector.y:.6g} {vector.z:.6g} )"


class _PointSerializer(_Serializer[shape.Point]):
    def serialize(self, point: shape.Point, depth: int = 0) -> str:
        indent = self.get_indent(depth)

        return f"{indent}point ( {point.x:.6g} {point.y:.6g} {point.z:.6g} )"


class _UVPointSerializer(_Serializer[shape.UVPoint]):
    def serialize(self, uv_point: shape.UVPoint, depth: int = 0) -> str:
        indent = self.get_indent(depth)

        return f"{indent}uv_point ( {uv_point.u:.6g} {uv_point.v:.6g} )"


class _ColourSerializer(_Serializer[shape.Colour]):
    def serialize(self, colour: shape.Colour, depth: int = 0) -> str:
        indent = self.get_indent(depth)

        return f"{indent}colour ( {colour.a:.6g} {colour.r:.6g} {colour.g:.6g} {colour.b:.6g} )"


class _MatrixSerializer(_Serializer[shape.Matrix]):
    def serialize(self, matrix: shape.Matrix, depth: int = 0) -> str:
        indent = self.get_indent(depth)
        values = (
            matrix.ax, matrix.ay, matrix.az,
            matrix.bx, matrix.by, matrix.bz,
            matrix.cx, matrix.cy, matrix.cz,
            matrix.dx, matrix.dy, matrix.dz
        )
        values_str = ' '.join(f"{v:.6g}" for v in values)

        return f"{indent}matrix {matrix.name} ( {values_str} )"


class _ListSerializer(_Serializer[List[T]]):
    def __init__(self,
        list_name: str,
        item_serializer: _Serializer[T],
        indent: int = 1,
        use_tabs: bool = True
    ):
        super().__init__(indent, use_tabs)
        self.list_name = list_name
        self.item_serializer = item_serializer

    def serialize(self, items: List[T], depth: int = 0) -> str:
        indent = self.get_indent(depth)
        inner_depth = depth + 1

        lines = [f"{indent}{self.list_name} ( {len(items)}"]
        for item in items:
            lines.append(f"{self.item_serializer.serialize(item, depth=inner_depth)}")
        lines.append(f"{indent})")

        return "\n".join(lines)


class _ShapeSerializer(_Serializer[shape.Shape]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self.serializers = {
            "points": _ListSerializer(
                list_name="points",
                item_serializer=_PointSerializer(indent, use_tabs),
                indent=indent,
                use_tabs=use_tabs
            ),
        }

    def serialize(self, shape: shape.Shape, depth: int = 0) -> str:
        indent = self.get_indent(depth)
        inner_depth = depth + 1

        lines = [f"{indent}shape ("]
        for name, serializer in self.serializers.items():
            items = getattr(shape, name, [])
            lines.append(serializer.serialize(items, depth=inner_depth))
        lines.append(f"{indent})")

        return "\n".join(lines)

