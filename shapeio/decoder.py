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
from typing import List, Optional, TypeVar, Generic, Pattern

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

    def _find_header_start_idx(self, text: str, block_name: str) -> Optional[int]:
        header_pattern = re.compile(
            rf'{re.escape(block_name)}\s*\(\s*\d+',
            re.IGNORECASE
        )
        match = header_pattern.search(text)
        if not match:
            return None

        return match.start()

    def _find_block(self, text: str, block_name: str) -> str:
        start_idx = self._find_header_start_idx(text, block_name)
        if start_idx is None:
            raise ValueError(f"No valid '{block_name}' block header found")

        open_parenthesis_idx = text.find('(', start_idx)
        if open_parenthesis_idx == -1:
            raise ValueError(f"Malformed block: no opening '(' for '{block_name}'")

        depth = 0
        idx = open_parenthesis_idx
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

    def _parse_block(self, text: str, block_name: str, parser: "_Parser[T]") -> T:
        block_text = self._find_block(text, block_name)

        return parser.parse(block_text)

    def _parse_block_optional(self, text: str, block_name: str, parser: "_Parser[T]") -> Optional[T]:
        start_idx = self._find_header_start_idx(text, block_name)
        if start_idx is None:
            return None
        
        return self._parse_block(text, block_name)


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
            raise ValueError(f"Expected {count} items in {self.list_name}, but found {len(matches)}")

        return [self.item_parser.parse(m.group(0)) for m in matches]


class _IntParser(_Parser[int]):
    PATTERN = re.compile(r'-?\d+')

    def parse(self, text: str) -> int:
        match = self.PATTERN.fullmatch(text.strip())
        if not match:
            raise ValueError(f"Invalid int value: '{text}'")
        
        return int(text.strip())


class _FloatParser(_Parser[float]):
    PATTERN = re.compile(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?')

    def parse(self, text: str) -> float:
        match = self.PATTERN.fullmatch(text.strip())
        if not match:
            raise ValueError(f"Invalid float value: '{text}'")
        
        return float(text.strip())


class _StrParser(_Parser[str]):
    PATTERN = re.compile(r'\w+')

    def parse(self, text: str) -> str:
        match = self.PATTERN.fullmatch(text.strip())
        if not match:
            raise ValueError(f"Invalid string value: '{text}'")
        
        return text.strip()


class _HexParser(_Parser[str]):
    PATTERN = re.compile(r'[0-9a-fA-F]{8}')

    def parse(self, text: str) -> str:
        match = self.PATTERN.fullmatch(text.strip())
        if not match:
            raise ValueError(f"Invalid hex value: '{text}'")
        
        return text.strip().lower()


class _ShapeHeaderParser(_Parser[shape.ShapeHeader]):
    PATTERN = re.compile(r'shape_header\s*\(\s*([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s*\)', re.IGNORECASE)

    def __init__(self):
        self._hex_parser = _HexParser()

    def parse(self, text: str) -> shape.ShapeHeader:
        match = self.PATTERN.search(text)
        if not match:
            raise ValueError(f"Invalid shape_header format: '{text}'")

        flags1 = self._hex_parser.parse(match.group(1))
        flags2 = self._hex_parser.parse(match.group(2))
        return shape.ShapeHeader(flags1, flags2)


class _VectorParser(_Parser[shape.Vector]):
    PATTERN = re.compile(r'vector\s*\(\s*([-+eE\d\.]+)\s+([-+eE\d\.]+)\s+([-+eE\d\.]+)\s*\)')

    def __init__(self):
        self._float_parser = _FloatParser()

    def parse(self, text: str) -> shape.Vector:
        match = self.PATTERN.match(text.strip())
        if not match:
            raise ValueError(f"Invalid vector format: '{text}'")

        x = self._float_parser.parse(match.group(1))
        y = self._float_parser.parse(match.group(2))
        z = self._float_parser.parse(match.group(3))
        return shape.Vector(x, y, z)


class _VolumeSphereParser(_Parser[shape.VolumeSphere]):
    PATTERN = re.compile(r"vol_sphere\s*\(\s*(vector\s*\([^()]*\))\s+(-?\d+(?:\.\d+)?)\s*\)", re.IGNORECASE)

    def __init__(self):
        self._vector_parser = _VectorParser()
        self._float_parser = _FloatParser()

    def parse(self, text: str) -> shape.VolumeSphere:
        match = self.PATTERN.search(text)
        if not match:
            raise ValueError(f"Invalid vol_sphere format: '{text}'")

        vector_text = match.group(1)
        radius = self._float_parser.parse(match.group(2))
        vector = self._vector_parser.parse(vector_text)
        return shape.VolumeSphere(vector, radius)


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


class _PointParser(_Parser[shape.Point]):
    PATTERN = re.compile(r'point\s*\(\s*([-+eE\d\.]+)\s+([-+eE\d\.]+)\s+([-+eE\d\.]+)\s*\)')

    def __init__(self):
        self._float_parser = _FloatParser()

    def parse(self, text: str) -> shape.Point:
        match = self.PATTERN.match(text.strip())
        if not match:
            raise ValueError(f"Invalid point format: '{text}'")

        x = self._float_parser.parse(match.group(1))
        y = self._float_parser.parse(match.group(2))
        z = self._float_parser.parse(match.group(3))
        return shape.Point(x, y, z)


class _UVPointParser(_Parser[shape.UVPoint]):
    PATTERN = re.compile(r'uv_point\s*\(\s*([-+eE\d\.]+)\s+([-+eE\d\.]+)\s*\)')

    def __init__(self):
        self._float_parser = _FloatParser()

    def parse(self, text: str) -> shape.UVPoint:
        match = self.PATTERN.match(text.strip())
        if not match:
            raise ValueError(f"Invalid uv_point format: '{text}'")

        u = self._float_parser.parse(match.group(1))
        v = self._float_parser.parse(match.group(2))
        return shape.UVPoint(u, v)


class _ColourParser(_Parser[shape.Colour]):
    PATTERN = re.compile(r'colour\s*\(\s*([-+eE\d\.]+)\s+([-+eE\d\.]+)\s+([-+eE\d\.]+)\s+([-+eE\d\.]+)\s*\)')

    def __init__(self):
        self._float_parser = _FloatParser()

    def parse(self, text: str) -> shape.Colour:
        match = self.PATTERN.match(text.strip())
        if not match:
            raise ValueError(f"Invalid colour format: '{text}'")

        a = self._float_parser.parse(match.group(1))
        r = self._float_parser.parse(match.group(2))
        g = self._float_parser.parse(match.group(3))
        b = self._float_parser.parse(match.group(4))
        return shape.Colour(a, r, g, b)


class _MatrixParser(_Parser[shape.Matrix]):
    PATTERN = re.compile(r'matrix\s+(\S+)\s*\(\s*([-+eE\d\.]+(?:\s+[-+eE\d\.]+){11})\s*\)')

    def __init__(self):
        self._float_parser = _FloatParser()
        self._str_parser = _StrParser()

    def parse(self, text: str) -> shape.Matrix:
        match = self.PATTERN.match(text.strip())
        if not match:
            raise ValueError(f"Invalid matrix format: '{text}'")

        name = self._str_parser.parse(match.group(1))
        values = [self._float_parser.parse(v) for v in match.group(2).split()]
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

    def __init__(self):
        self._int_parser = _IntParser()
        self._float_parser = _FloatParser()
        self._hex_parser = _HexParser()

    def parse(self, text: str) -> shape.Texture:
        match = self.PATTERN.search(text)
        if not match:
            raise ValueError(f"Invalid texture format: '{text}'")

        image_index = self._int_parser.parse(match.group(1))
        filter_mode = self._int_parser.parse(match.group(2))
        mipmap_lod_bias = self._float_parser.parse(match.group(3))
        border_colour = self._hex_parser.parse(match.group(4))

        return shape.Texture(
            image_index,
            filter_mode,
            mipmap_lod_bias,
            border_colour
        )


class _LightMaterialParser(_Parser[shape.LightMaterial]):
    PATTERN = re.compile(
        r'light_material\s*\(\s*([a-fA-F0-9]+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+(?:\.\d+)?)\s*\)',
        re.IGNORECASE
    )

    def __init__(self):
        self._hex_parser = _HexParser()
        self._int_parser = _IntParser()
        self._float_parser = _FloatParser()

    def parse(self, text: str) -> shape.LightMaterial:
        match = self.PATTERN.search(text)
        if not match:
            raise ValueError(f"Invalid light_material format: '{text}'")

        flags = self._hex_parser.parse(match.group(1))
        diff_colour_index = self._int_parser.parse(match.group(2))
        amb_colour_index = self._int_parser.parse(match.group(3))
        spec_colour_index = self._int_parser.parse(match.group(4))
        emissive_colour_index = self._int_parser.parse(match.group(5))
        spec_power = self._float_parser.parse(match.group(6))

        return shape.LightMaterial(
            flags,
            diff_colour_index,
            amb_colour_index,
            spec_colour_index,
            emissive_colour_index,
            spec_power
        )


class _UVOpParser(_Parser[shape.UVOp]):
    PATTERN = re.compile(
        r'uv_op_([a-z]+)\s*\(\s*(-?\d+)(?:\s+(-?\d+))?(?:\s+(-?\d+))?(?:\s+(-?\d+))?\s*\)',
        re.IGNORECASE
    )

    def __init__(self):
        self._int_parser = _IntParser()

    def parse(self, text: str) -> shape.UVOp:
        match = self.PATTERN.fullmatch(text.strip())
        if not match:
            raise ValueError(f"Invalid uv_op format: '{text}'")

        op_type = match.group(1).lower()
        values = [g for g in match.groups()[1:] if g is not None]
        int_values = [self._int_parser.parse(value) for value in values]

        if op_type == "copy":
            if len(int_values) != 2:
                raise ValueError(f"uv_op_copy expects 2 values, got {len(int_values)}: {text}")
            return shape.UVOpCopy(*int_values)

        elif op_type == "reflectmapfull":
            if len(int_values) != 1:
                raise ValueError(f"uv_op_reflectmapfull expects 1 value, got {len(int_values)}: {text}")
            return shape.UVOpReflectMapFull(*int_values)

        elif op_type == "reflectmap":
            if len(int_values) != 1:
                raise ValueError(f"uv_op_reflectmap expects 1 value, got {len(int_values)}: {text}")
            return shape.UVOpReflectMap(*int_values)

        elif op_type == "uniformscale":
            if len(int_values) != 4:
                raise ValueError(f"uv_op_uniformscale expects 4 values, got {len(int_values)}: {text}")
            return shape.UVOpUniformScale(*int_values)

        elif op_type == "nonuniformscale":
            if len(int_values) != 4:
                raise ValueError(f"uv_op_nonuniformscale expects 4 values, got {len(int_values)}: {text}")
            return shape.UVOpNonUniformScale(*int_values)

        else:
            raise ValueError(f"Unknown uv_op type: 'uv_op_{op_type}'")


class _LightModelCfgParser(_Parser[shape.LightModelCfg]):
    PATTERN = re.compile(r"""
        light_model_cfg\s*\(\s*([a-fA-F0-9]+)\s*
        uv_ops\s*\(\s*\d+\s*
        (?:uv_op_[a-z_]+\s*\(\s*-?\d+\s+-?\d+\s*\)\s*)+
        \)\s*
        \)
    """, re.IGNORECASE | re.VERBOSE | re.DOTALL)

    def __init__(self):
        self._hex_parser = _HexParser()
        self._uv_op_parser = _UVOpParser()
        self._uv_op_list_parser = _ListParser(
            list_name="uv_ops",
            item_parser=self._uv_op_parser,
            item_pattern=_UVOpParser.PATTERN
        )

    def parse(self, text: str) -> shape.LightModelCfg:
        match = self.PATTERN.search(text)
        if not match:
            raise ValueError(f"Invalid light_model_cfg format: '{text}'")

        flags = self._hex_parser.parse(match.group(1))
        uv_ops = self._parse_block(text, "uv_ops", self._uv_op_list_parser)

        return shape.LightModelCfg(flags, uv_ops)


class _VtxStateParser(_Parser[shape.VtxState]):
    PATTERN = re.compile(
        r"vtx_state\s*\(\s*([a-fA-F0-9]+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+([a-fA-F0-9]+)(?:\s+(-?\d+))?\s*\)",
        re.IGNORECASE
    )

    def __init__(self):
        self._hex_parser = _HexParser()
        self._int_parser = _IntParser()

    def parse(self, text: str) -> shape.VtxState:
        match = self.PATTERN.search(text)
        if not match:
            raise ValueError(f"Invalid vtx_state format: '{text}'")

        flags = self._hex_parser.parse(match.group(1))
        matrix_index = self._int_parser.parse(match.group(2))
        light_material_index = self._int_parser.parse(match.group(3))
        light_model_cfg_index = self._int_parser.parse(match.group(4))
        light_flags = self._hex_parser.parse(match.group(5))
        matrix2_index = self._int_parser.parse(match.group(6)) if match.group(6) is not None else None

        return shape.VtxState(
            flags,
            matrix_index,
            light_material_index,
            light_model_cfg_index,
            light_flags,
            matrix2_index
        )


class _PrimStateParser(_Parser[shape.PrimState]):
    PATTERN = re.compile(
        r"""prim_state\s+(\w+)\s*\(\s*([a-fA-F0-9]+)\s+(\d+)\s+
            tex_idxs\s*\(.*?\)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s*
        \)""",
        re.IGNORECASE | re.VERBOSE
    )

    def __init__(self):
        self._hex_parser = _HexParser()
        self._int_parser = _IntParser()
        self._str_parser = _StrParser()
        self._float_parser = _FloatParser()
        self._texture_list_parser = _ListParser(
            list_name="tex_idxs",
            item_parser=self._int_parser,
            item_pattern=_IntParser.PATTERN
        )

    def parse(self, text: str) -> shape.PrimState:
        match = self.PATTERN.search(text)
        if not match:
            raise ValueError(f"Invalid prim_state format: '{text}'")

        name = self._str_parser.parse(match.group(1))
        flags = self._hex_parser.parse(match.group(2))
        shader_index = self._int_parser.parse(match.group(3))
        texture_indices = self._parse_block(text, "tex_idxs", self._texture_list_parser)
        z_bias = self._float_parser.parse(match.group(4))
        vtx_state_index = self._int_parser.parse(match.group(5))
        alpha_test_mode = self._int_parser.parse(match.group(6))
        light_cfg_index = self._int_parser.parse(match.group(7))
        z_buffer_mode = self._int_parser.parse(match.group(8))

        return shape.PrimState(
            name,
            flags,
            shader_index,
            texture_indices,
            z_bias,
            vtx_state_index,
            alpha_test_mode,
            light_cfg_index,
            z_buffer_mode
        )


class _ShapeParser(_Parser[shape.Shape]):
    def __init__(self):
        self._shape_header_parser = _ShapeHeaderParser()
        self._volumes_parser = _ListParser(
            list_name="volumes",
            item_parser=_VolumeSphereParser(),
            item_pattern=_VolumeSphereParser.PATTERN
        )
        self._shader_names_parser = _ListParser(
            list_name="shader_names",
            item_parser=_NamedShaderParser(),
            item_pattern=_NamedShaderParser.PATTERN
        )
        self._named_filter_names_parser = _ListParser(
            list_name="texture_filter_names",
            item_parser=_NamedFilterModeParser(),
            item_pattern=_NamedFilterModeParser.PATTERN
        )
        self._points_parser = _ListParser(
            list_name="points",
            item_parser=_PointParser(),
            item_pattern=_PointParser.PATTERN
        )
        self._uv_points_parser = _ListParser(
            list_name="uv_points",
            item_parser=_UVPointParser(),
            item_pattern=_UVPointParser.PATTERN
        )
        self._normals_parser = _ListParser(
            list_name="normals",
            item_parser=_VectorParser(),
            item_pattern=_VectorParser.PATTERN
        )
        self._sort_vectors_parser = _ListParser(
            list_name="sort_vectors",
            item_parser=_VectorParser(),
            item_pattern=_VectorParser.PATTERN
        )
        self._colours_parser = _ListParser(
            list_name="colours",
            item_parser=_ColourParser(),
            item_pattern=_ColourParser.PATTERN
        )
        self._matrices_parser = _ListParser(
            list_name="matrices",
            item_parser=_MatrixParser(),
            item_pattern=_MatrixParser.PATTERN
        )
        self._images_parser = _ListParser(
            list_name="images",
            item_parser=_ImageParser(),
            item_pattern=_ImageParser.PATTERN
        )
        self._textures_parser = _ListParser(
            list_name="textures",
            item_parser=_TextureParser(),
            item_pattern=_TextureParser.PATTERN
        )
        self._light_materials_parser = _ListParser(
            list_name="light_materials",
            item_parser=_LightMaterialParser(),
            item_pattern=_LightMaterialParser.PATTERN
        )
        self._light_model_cfgs_parser = _ListParser(
            list_name="light_model_cfgs",
            item_parser=_LightModelCfgParser(),
            item_pattern=_LightModelCfgParser.PATTERN
        )
        self._vtx_states_parser = _ListParser(
            list_name="vtx_states",
            item_parser=_VtxStateParser(),
            item_pattern=_VtxStateParser.PATTERN
        )
        self._prim_states_parser = _ListParser(
            list_name="prim_states",
            item_parser=_PrimStateParser(),
            item_pattern=_PrimStateParser.PATTERN
        )

    def parse(self, text: str) -> shape.Shape:
        shape_header = self._parse_block(text, "shape_header", self._shape_header_parser)
        volumes = self._parse_block(text, "volumes", self._volumes_parser)
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
        light_materials = self._parse_block(text, "light_materials", self._light_materials_parser)
        light_model_cfgs = self._parse_block(text, "light_model_cfgs", self._light_model_cfgs_parser)
        vtx_states = self._parse_block(text, "vtx_states", self._vtx_states_parser)
        prim_states = self._parse_block(text, "prim_states", self._prim_states_parser)
        animations = None

        return shape.Shape(
            shape_header=shape_header,
            volumes=volumes,
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
            light_materials=light_materials,
            light_model_cfgs=light_model_cfgs,
            vtx_states=vtx_states,
            prim_states=prim_states,
            lod_controls=[],
            animations=animations or []
        )
