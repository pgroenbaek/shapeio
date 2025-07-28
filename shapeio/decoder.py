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
from typing import List, TypeVar, Generic, Pattern

from . import shape

T = TypeVar('T')


class ShapeDecoder:
    def __init__(self):
        self._parser = _ShapeParser()

    def decode(self, text: str) -> shape.Shape:
        return self._parser.parse(text)


class _Parser(ABC, Generic[T]):
    @abstractmethod
    def parse(self, text: str) -> T:
        pass

    def _find_block(self, text: str, block_name: str):
        header_pattern = re.compile(
            rf'{re.escape(block_name)}\s*\(\s*\d+',
            re.IGNORECASE
        )
        match = header_pattern.search(text)
        if not match:
            raise ValueError(f"No valid '{block_name}' block header found")

        start_idx = match.start()

        open_paren_idx = text.find('(', match.start())
        if open_paren_idx == -1:
            raise ValueError(f"Malformed block: no opening '(' for '{block_name}'")

        depth = 0
        idx = open_paren_idx
        while idx < len(text):
            char = text[idx]
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
                if depth == 0:
                    return text[start_idx:idx + 1]
            idx += 1

        raise ValueError(f"Unbalanced parentheses in '{block_name}' block")

    def _parse_block(self, text: str, block_name: str, parser: "_Parser") -> T:
        block_text = self._find_block(text, block_name)
        if block_text is None:
            raise ValueError(f"No valid '{block_name}' block found in shape file.")

        return parser.parse(block_text)


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


class _ImageParser(_Parser[str]):
    PATTERN = re.compile(r'image\s*\(\s*(.+?)\s*\)', re.IGNORECASE)

    def parse(self, text: str) -> str:
        match = self.PATTERN.search(text)
        if not match:
            raise ValueError(f"Invalid image format: '{text}'")
        
        value = match.group(1).strip()
        if not value:
            raise ValueError(f"image cannot be empty: '{text}'")
        
        return value


class _TextureParser(_Parser[shape.Texture]):
    PATTERN = re.compile(r'texture\s*\(\s*(-?\d+)\s+(-?\d+)\s+(-?\d+(?:\.\d+)?)\s+([a-fA-F0-9]+)\s*\)', re.IGNORECASE)

    def parse(self, text: str) -> str:
        match = self.PATTERN.search(text)
        if not match:
            raise ValueError(f"Invalid texture format: '{text}'")
        
        image_index = int(match.group(1))
        filter_mode = int(match.group(2))
        mipmap_lod_bias = float(match.group(3))
        border_colour = match.group(4)

        return shape.Texture(image_index, filter_mode, mipmap_lod_bias, border_colour)


class _ListParser(_Parser[List[T]]):
    def __init__(self,
        list_name: str,
        item_parser: _Parser[T],
        item_pattern: Pattern,
    ):
        self.list_name = list_name
        self.item_parser = item_parser
        self.item_pattern = item_pattern

    def parse(self, text: str) -> List[T]:
        text = text.strip()

        header_match = re.match(
            rf'{re.escape(self.list_name)}\s*\(\s*(\d+)',
            text
        )
        if not header_match:
            raise ValueError(f"Invalid {self.list_name} block header: '{text}'")
        
        count = int(header_match.group(1))
        header_end = header_match.end()

        body_end = text.rfind(')')
        if body_end == -1:
            if count == 0:
                return []
            raise ValueError(f"Malformed block structure in '{self.list_name}'")

        body = text[header_end : body_end].strip()

        matches = list(self.item_pattern.finditer(body))
        if len(matches) != count:
            print(matches)
            raise ValueError(f"Expected {count} {self.list_name}, but found {len(matches)}")

        return [self.item_parser.parse(m.group(0)) for m in matches]


class _ShapeParser(_Parser[shape.Shape]):
    def __init__(self):
        self._shape_header_parser = _ShapeHeaderParser()
        self._named_shader_parser = _NamedShaderParser()
        self._shader_names_parser = _ListParser(
            list_name="shader_names",
            item_parser=self._named_shader_parser,
            item_pattern=self._named_shader_parser.PATTERN
        )
        self._named_filter_mode_parser = _NamedFilterModeParser()
        self._named_filter_names_parser = _ListParser(
            list_name="texture_filter_names",
            item_parser=self._named_filter_mode_parser,
            item_pattern=self._named_filter_mode_parser.PATTERN
        )
        self._point_parser = _PointParser()
        self._points_parser = _ListParser(
            list_name="points",
            item_parser=self._point_parser,
            item_pattern=self._point_parser.PATTERN
        )
        self._uv_point_parser = _UVPointParser()
        self._uv_points_parser = _ListParser(
            list_name="uv_points",
            item_parser=self._uv_point_parser,
            item_pattern=self._uv_point_parser.PATTERN
        )
        self._vector_parser = _VectorParser()
        self._normals_parser = _ListParser(
            list_name="normals",
            item_parser=self._vector_parser,
            item_pattern=self._vector_parser.PATTERN
        )
        self._sort_vectors_parser = _ListParser(
            list_name="sort_vectors",
            item_parser=self._vector_parser,
            item_pattern=self._vector_parser.PATTERN
        )
        self._colour_parser = _ColourParser()
        self._colours_parser = _ListParser(
            list_name="colours",
            item_parser=self._colour_parser,
            item_pattern=self._colour_parser.PATTERN
        )
        self._matrix_parser = _MatrixParser()
        self._matrices_parser = _ListParser(
            list_name="matrices",
            item_parser=self._matrix_parser,
            item_pattern=self._matrix_parser.PATTERN
        )
        self._image_parser = _ImageParser()
        self._images_parser = _ListParser(
            list_name="images",
            item_parser=self._image_parser,
            item_pattern=self._image_parser.PATTERN
        )
        self._texture_parser = _TextureParser()
        self._textures_parser = _ListParser(
            list_name="textures",
            item_parser=self._texture_parser,
            item_pattern=self._texture_parser.PATTERN
        )

    def parse(self, text: str) -> shape.Shape:
        shape_header = self._parse_block(text, "shape_header", self._shape_header_parser)
        shader_names = self._parse_block(text, "shader_names", self._shader_names_parser)
        texture_filter_names = self._parse_block(text, "texture_filter_names", self._named_filter_names_parser)
        points = self._parse_block(text, "points", self._points_parser)
        uv_points = self._parse_block(text, "uv_points", self._uv_points_parser)
        normals = self._parse_block(text, "normals", self._normals_parser)
        sort_vectors = self._parse_block(text, "sort_vectors", self._sort_vectors_parser)
        colours = self._parse_block(text, "colours", self._colours_parser)
        matrices = self._parse_block(text, "matrices", self._matrices_parser)
        images = self._parse_block(text, "images", self._images_parser)
        textures = self._parse_block(text, "textures", self._textures_parser)

        return shape.Shape(
            shape_header=shape_header,
            volumes=[],
            shader_names=shader_names,
            texture_filter_names=texture_filter_names,
            points=points,
            uv_points=uv_points,
            normals=normals,
            sort_vectors=sort_vectors,
            colours=colours,
            matrices=matrices,
            images=images,
            textures=textures,
            light_materials=[],
            light_model_cfgs=[],
            vtx_states=[],
            prim_states=[],
            lod_controls=[],
            animations=[]
        )
