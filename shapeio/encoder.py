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
    def serialize(self, vector: shape.Vector) -> str:
        return f"vector ( {vector.x} {vector.y} {vector.z} )"


class _PointSerializer(Serializer):
    def serialize(self, point: shape.Point) -> str:
        return f"point ( {point.x} {point.y} {point.z} )"


class _UVPointSerializer(Serializer):
    def serialize(self, uv_point: shape.UVPoint) -> str:
        return f"uv_point ( {uv_point.u} {uv_point.v} )"