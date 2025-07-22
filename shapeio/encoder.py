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

from abc import ABC

from . import shape


class ShapeEncoder:
    def __init__(self):
        pass

    def encode(self, obj: shape.Shape) -> str:
        return _ShapeSerializer().serialize(obj)


class _Serializer(ABC):
    @abstractmethod
    def serialize(self, obj) -> str:
        pass


class _ShapeSerializer(Serializer):
    def serialize(self, obj: shape.Shape) -> str:
        pass