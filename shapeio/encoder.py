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
        self._serializer = _ShapeSerializer(indent=indent, use_tabs=use_tabs)

    def encode(self, shape: shape.Shape) -> str:
        header = "SIMISA@@@@@@@@@@JINX0s1t______\n\n"
        text = self._serializer.serialize(shape)

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


class _ShapeHeaderSerializer(_Serializer[shape.ShapeHeader]):
    def serialize(self, value: shape.ShapeHeader, depth: int = 0) -> str:
        indent = self.get_indent(depth)
        return f"{indent}shape_header ( {value.flags1.lower()} {value.flags2.lower()} )"


class _NamedShaderSerializer(_Serializer[str]):
    def serialize(self, value: str, depth: int = 0) -> str:
        indent = self.get_indent(depth)

        return f"{indent}named_shader ( {value} )"


class _NamedFilterModeSerializer(_Serializer[str]):
    def serialize(self, value: str, depth: int = 0) -> str:
        indent = self.get_indent(depth)

        return f"{indent}named_filter_mode ( {value} )"


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


class _ImageSerializer(_Serializer[str]):
    def serialize(self, value: str, depth: int = 0) -> str:
        indent = self.get_indent(depth)

        return f"{indent}image ( {value} )"


class _TextureSerializer(_Serializer[shape.Texture]):
    def serialize(self, texture: shape.Texture, depth: int = 0) -> str:
        indent = self.get_indent(depth)

        return (
            f"{indent}texture ( {texture.image_index} "
            f"{texture.filter_mode} {texture.mipmap_lod_bias:.6g} "
            f"{texture.border_colour} )"
        )


class _ListSerializer(_Serializer[List[T]]):
    def __init__(
        self,
        list_name: str,
        item_serializer: _Serializer[T],
        indent: int = 1,
        use_tabs: bool = True,
        items_per_line: int = 1,
        newline_after_header: bool = True,
        newline_before_closing: bool = True,
        newlines_for_empty_list: bool = False,
    ):
        super().__init__(indent, use_tabs)
        self.list_name = list_name
        self.item_serializer = item_serializer
        self.items_per_line = items_per_line
        self.newline_after_header = newline_after_header
        self.newline_before_closing = newline_before_closing
        self.newlines_for_empty_list = newlines_for_empty_list

    def serialize(self, items: List[T], depth: int = 0) -> str:
        indent = self.get_indent(depth)
        inner_indent = self.get_indent(depth + 1)
        header = f"{indent}{self.list_name} ( {len(items)}"

        lines = []

        list_not_empty = len(items) != 0
        newline_after_header_if_not_empty = self.newline_after_header and list_not_empty

        if newline_after_header_if_not_empty or self.newlines_for_empty_list:
            lines.append(header)
        else:
            extra_space_if_not_empty = " " if list_not_empty else ""
            lines.append(header.rstrip() + extra_space_if_not_empty)

        current_line = []
        for i, item in enumerate(items):
            rendered = self.item_serializer.serialize(item, depth=0).strip()
            current_line.append(rendered)

            is_last_item = i == len(items) - 1
            should_wrap = (len(current_line) == self.items_per_line) or is_last_item

            if should_wrap:
                line_str = ' '.join(current_line)
                if self.newline_after_header:
                    lines.append(f"{inner_indent}{line_str}")
                else:
                    lines[-1] += line_str if is_last_item else line_str + " "
                current_line = []

        newline_before_closing_if_not_empty = self.newline_before_closing and list_not_empty

        if newline_before_closing_if_not_empty or self.newlines_for_empty_list:
            lines.append(f"{indent})")
        else:
            lines[-1] += " )"

        return "\n".join(lines)


class _ShapeSerializer(_Serializer[shape.Shape]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self.serializers = {
            "shape_header": _ShapeHeaderSerializer(indent, use_tabs),
            "shader_names": _ListSerializer(
                list_name="shader_names",
                item_serializer=_NamedShaderSerializer(indent, use_tabs),
                indent=indent,
                use_tabs=use_tabs
            ),
            "texture_filter_names": _ListSerializer(
                list_name="texture_filter_names",
                item_serializer=_NamedFilterModeSerializer(indent, use_tabs),
                indent=indent,
                use_tabs=use_tabs
            ),
            "points": _ListSerializer(
                list_name="points",
                item_serializer=_PointSerializer(indent, use_tabs),
                indent=indent,
                use_tabs=use_tabs
            ),
            "uv_points": _ListSerializer(
                list_name="uv_points",
                item_serializer=_UVPointSerializer(indent, use_tabs),
                indent=indent,
                use_tabs=use_tabs
            ),
            "normals": _ListSerializer(
                list_name="normals",
                item_serializer=_VectorSerializer(indent, use_tabs),
                indent=indent,
                use_tabs=use_tabs
            ),
            "sort_vectors": _ListSerializer(
                list_name="sort_vectors",
                item_serializer=_VectorSerializer(indent, use_tabs),
                indent=indent,
                use_tabs=use_tabs
            ),
            "colours": _ListSerializer(
                list_name="colours",
                item_serializer=_ColourSerializer(indent, use_tabs),
                indent=indent,
                use_tabs=use_tabs
            ),
            "matrices": _ListSerializer(
                list_name="matrices",
                item_serializer=_MatrixSerializer(indent, use_tabs),
                indent=indent,
                use_tabs=use_tabs
            ),
            "images": _ListSerializer(
                list_name="images",
                item_serializer=_ImageSerializer(indent, use_tabs),
                indent=indent,
                use_tabs=use_tabs
            ),
            "textures": _ListSerializer(
                list_name="textures",
                item_serializer=_TextureSerializer(indent, use_tabs),
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

