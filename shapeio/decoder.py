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
        self.parser = _ShapeParser()

    def decode(self, text: str) -> shape.Shape:
        return self.parser.parse(text)


class _Parser(ABC, Generic[T]):
    @abstractmethod
    def parse(self, text: str) -> T:
        pass


class _ShapeHeaderParser(_Parser[shape.ShapeHeader]):
    PATTERN = re.compile(r'shape_header\s*\(\s*([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s*\)', re.IGNORECASE)

    def parse(self, text: str) -> shape.ShapeHeader:
        match = self.PATTERN.search(text)
        if not match:
            raise ValueError(f"Invalid shape_header format: '{text}'")
        
        flags1, flags2 = match.group(1).upper(), match.group(2).upper()
        return shape.ShapeHeader(flags1, flags2)


class _NamedShaderParser(_Parser[str]):
    PATTERN = re.compile(r'named_shader\s*\(\s*(.+?)\s*\)', re.IGNORECASE)

    def parse(self, text: str) -> str:
        match = self.PATTERN.search(text)
        if not match:
            raise ValueError(f"Invalid named_shader format: '{text}'")
        
        value = match.group(1).strip()
        if not value:
            raise ValueError(f"named_shader cannot be empty: '{text}'")
        
        return value


class _NamedFilterModeParser(_Parser[str]):
    PATTERN = re.compile(r'named_filter_mode\s*\(\s*(.+?)\s*\)', re.IGNORECASE)

    def parse(self, text: str) -> str:
        match = self.PATTERN.search(text)
        if not match:
            raise ValueError(f"Invalid named_filter_mode format: '{text}'")

        value = match.group(1).strip()
        if not value:
            raise ValueError(f"named_filter_mode cannot be empty: '{text}'")
        
        return value


class _VectorParser(_Parser[shape.Vector]):
    PATTERN = re.compile(r'vector\s*\(\s*([-+eE\d\.]+)\s+([-+eE\d\.]+)\s+([-+eE\d\.]+)\s*\)')

    def parse(self, text: str) -> shape.Vector:
        match = self.PATTERN.match(text.strip())
        if not match:
            raise ValueError(f"Invalid vector format: '{text}'")

        x, y, z = map(float, match.groups())
        return shape.Vector(x, y, z)


class _PointParser(_Parser[shape.Point]):
    PATTERN = re.compile(r'point\s*\(\s*([-+eE\d\.]+)\s+([-+eE\d\.]+)\s+([-+eE\d\.]+)\s*\)')

    def parse(self, text: str) -> shape.Point:
        match = self.PATTERN.match(text.strip())
        if not match:
            raise ValueError(f"Invalid point format: '{text}'")

        x, y, z = map(float, match.groups())
        return shape.Point(x, y, z)


class _UVPointParser(_Parser[shape.UVPoint]):
    PATTERN = re.compile(r'uv_point\s*\(\s*([-+eE\d\.]+)\s+([-+eE\d\.]+)\s*\)')

    def parse(self, text: str) -> shape.UVPoint:
        match = self.PATTERN.match(text.strip())
        if not match:
            raise ValueError(f"Invalid uv_point format: '{text}'")

        u, v = map(float, match.groups())
        return shape.UVPoint(u, v)


class _ColourParser(_Parser[shape.Colour]):
    PATTERN = re.compile(r'colour\s*\(\s*([-+eE\d\.]+)\s+([-+eE\d\.]+)\s+([-+eE\d\.]+)\s+([-+eE\d\.]+)\s*\)')

    def parse(self, text: str) -> shape.Colour:
        match = self.PATTERN.match(text.strip())
        if not match:
            raise ValueError(f"Invalid colour format: '{text}'")

        a, r, g, b = map(float, match.groups())
        return shape.Colour(a, r, g, b)


class _MatrixParser(_Parser[shape.Matrix]):
    PATTERN = re.compile(r'matrix\s+(\S+)\s*\(\s*([-+eE\d\.]+(?:\s+[-+eE\d\.]+){11})\s*\)')

    def parse(self, text: str) -> shape.Matrix:
        match = self.PATTERN.match(text.strip())
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
            rf'{regex.escape(list_name)}\s*\(\s*(\d+)\s*'
            rf'(?P<items>(?:{regex.escape(item_name)}\s*\((?:[^()]+|(?R))*\)\s*)+)\)'
        )
        self.list_pattern = regex.compile(list_pattern_str, regex.DOTALL)

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


class _ShapeParser(_Parser[shape.Shape]):
    def __init__(self):
        self._shape_header_parser = _ShapeHeaderParser()
        self._named_shader_parser = _NamedShaderParser()
        self._shader_names_parser = _ListParser(
            list_name="shader_names",
            item_name="named_shader",
            item_parser=self._named_shader_parser,
            item_pattern=self._named_shader_parser.PATTERN
        )
        self._named_filter_mode_parser = _NamedFilterModeParser()
        self._named_filter_names_parser = _ListParser(
            list_name="texture_filter_names",
            item_name="named_filter_mode",
            item_parser=self._named_filter_mode_parser,
            item_pattern=self._named_filter_mode_parser.PATTERN
        )
        self._point_parser = _PointParser()
        self._points_parser = _ListParser(
            list_name="points",
            item_name="point",
            item_parser=self._point_parser,
            item_pattern=self._point_parser.PATTERN
        )
        self._uv_point_parser = _UVPointParser()
        self._uv_points_parser = _ListParser(
            list_name="uv_points",
            item_name="uv_point",
            item_parser=self._uv_point_parser,
            item_pattern=self._uv_point_parser.PATTERN
        )
        self._vector_parser = _VectorParser()
        self._normals_parser = _ListParser(
            list_name="normals",
            item_name="vector",
            item_parser=self._vector_parser,
            item_pattern=self._vector_parser.PATTERN
        )
        self._sort_vectors_parser = _ListParser(
            list_name="sort_vectors",
            item_name="vector",
            item_parser=self._vector_parser,
            item_pattern=self._vector_parser.PATTERN
        )

    def parse(self, text: str) -> shape.Shape:
        shape_header = self._parse_shape_header_block(text)
        shader_names = self._parse_shader_names_block(text)
        texture_filter_names = self._parse_texture_filter_names_block(text)
        points = self._parse_points_block(text)
        uv_points = self._parse_uv_points_block(text)
        normals = self._parse_normals_block(text)
        sort_vectors = self._parse_sort_vectors_block(text)

        return shape.Shape(
            shape_header=shape_header,
            volumes=[],
            shader_names=shader_names,
            texture_filter_names=texture_filter_names,
            points=points,
            uv_points=uv_points,
            normals=normals,
            sort_vectors=sort_vectors,
            colours=[],
            matrices=[],
            images=[],
            textures=[],
            light_materials=[],
            light_model_cfgs=[],
            vtx_states=[],
            prim_states=[],
            lod_controls=[],
            animations=[]
        )

    def _compile_list_block_pattern(self, list_name: str, item_name: str) -> Pattern:
        block_pattern_str = (
            rf'{regex.escape(list_name)}\s*\(\s*\d+\s*(?:{regex.escape(item_name)}\s*\((?:[^()]+|(?R))*\)\s*)+\)'
        )
        block_pattern = regex.compile(block_pattern_str, regex.DOTALL)
        return block_pattern

    def _parse_shape_header_block(self, text: str) -> List[str]:
        shape_header_block_pattern = re.compile(
            r"shape_header\s*\(\s*[0-9a-fA-F]{8}\s+[0-9a-fA-F]{8}\s*\)",
            re.IGNORECASE
        )
        match = shape_header_block_pattern.search(text)
        if not match:
            raise ValueError("No valid 'shape_header' block found in shape file.")

        return self._shape_header_parser.parse(match.group(0))

    def _parse_shader_names_block(self, text: str) -> List[str]:
        shader_names_block_pattern = self._compile_list_block_pattern(list_name="shader_names", item_name="named_shader")
        match = shader_names_block_pattern.search(text)
        if not match:
            raise ValueError("No valid 'shader_names' block found in shape file.")

        return self._shader_names_parser.parse(match.group(0))
    
    def _parse_texture_filter_names_block(self, text: str) -> List[str]:
        texture_filter_names_block_pattern = self._compile_list_block_pattern(list_name="texture_filter_names", item_name="named_filter_mode")
        match = texture_filter_names_block_pattern.search(text)
        if not match:
            raise ValueError("No valid 'texture_filter_names' block found in shape file.")

        return self._named_filter_names_parser.parse(match.group(0))

    def _parse_points_block(self, text: str) -> List[shape.Point]:
        points_block_pattern = self._compile_list_block_pattern(list_name="points", item_name="point")
        match = points_block_pattern.search(text)
        if not match:
            raise ValueError("No valid 'points' block found in shape file.")

        return self._points_parser.parse(match.group(0))

    def _parse_points_block(self, text: str) -> List[shape.Point]:
        points_block_pattern = self._compile_list_block_pattern(list_name="points", item_name="point")
        match = points_block_pattern.search(text)
        if not match:
            raise ValueError("No valid 'points' block found in shape file.")

        return self._points_parser.parse(match.group(0))
    
    def _parse_uv_points_block(self, text: str) -> List[shape.UVPoint]:
        uv_points_block_pattern = self._compile_list_block_pattern(list_name="uv_points", item_name="uv_point")
        match = uv_points_block_pattern.search(text)
        if not match:
            raise ValueError("No valid 'uv_points' block found in shape file.")

        return self._uv_points_parser.parse(match.group(0))
    
    def _parse_normals_block(self, text: str) -> List[shape.Vector]:
        normals_block_pattern = self._compile_list_block_pattern(list_name="normals", item_name="vector")
        match = normals_block_pattern.search(text)
        if not match:
            raise ValueError("No valid 'normals' block found in shape file.")

        return self._normals_parser.parse(match.group(0))

    def _parse_sort_vectors_block(self, text: str) -> List[shape.Vector]:
        sort_vectors_block_pattern = self._compile_list_block_pattern(list_name="sort_vectors", item_name="vector")
        match = sort_vectors_block_pattern.search(text)
        if not match:
            raise ValueError("No valid 'sort_vectors' block found in shape file.")

        return self._sort_vectors_parser.parse(match.group(0))