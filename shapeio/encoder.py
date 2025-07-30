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
from typing import List, Optional, TypeVar, Generic

from . import shape

T = TypeVar('T')


class ShapeEncoder:
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        self._serializer = _ShapeSerializer(indent=indent, use_tabs=use_tabs)

    def encode(self, shape: shape.Shape) -> str:
        header = "\ufeffSIMISA@@@@@@@@@@JINX0s1t______\n\n"
        text = self._serializer.serialize(shape)

        return header + text + "\n"


class _Serializer(ABC, Generic[T]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        char = "\t" if use_tabs else " "
        self.indent_unit = char * indent

    def get_indent(self, depth: int = 0) -> str:
        return self.indent_unit * depth

    @abstractmethod
    def serialize(self, obj: T, depth: int = 0) -> str:
        pass


class _ListSerializer(_Serializer[List[T]]):
    def __init__(self,
        list_name: str,
        item_serializer: _Serializer[T],
        indent: int = 1,
        use_tabs: bool = True,
        items_per_line: Optional[int] = 1,
        count_multiplier: int = 1,
        newline_after_header: bool = True,
        newline_before_closing: bool = True,
        newlines_for_empty_list: bool = False,
    ):
        super().__init__(indent, use_tabs)
        self.list_name = list_name
        self.item_serializer = item_serializer
        self.items_per_line = items_per_line
        self.count_multiplier = count_multiplier
        self.newline_after_header = newline_after_header
        self.newline_before_closing = newline_before_closing
        self.newlines_for_empty_list = newlines_for_empty_list

    def serialize(self, items: List[T], depth: int = 0) -> str:
        indent = self.get_indent(depth)
        inner_indent = self.get_indent(depth + 1)
        header = f"{indent}{self.list_name} ( {len(items) * self.count_multiplier}"

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
            inner_depth = depth + 1
            rendered = self.item_serializer.serialize(item, depth=inner_depth).strip()
            current_line.append(rendered)

            is_last_item = i == len(items) - 1
            is_max_items = len(current_line) == self.items_per_line
            items_per_line_enabled = self.items_per_line is not None
            should_wrap = (items_per_line_enabled and is_max_items) or is_last_item

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


class _IntSerializer(_Serializer[int]):
    def serialize(self, value: int, depth: int = 0) -> str:
        return str(value)


class _FloatSerializer(_Serializer[float]):
    def serialize(self, value: float, depth: int = 0) -> str:
        return f"{value:.6g}"


class _StrSerializer(_Serializer[str]):
    def serialize(self, value: str, depth: int = 0) -> str:
        return value


class _HexSerializer(_Serializer[str]):
    def serialize(self, value: str, depth: int = 0) -> str:
        return value.lower()


class _ShapeHeaderSerializer(_Serializer[shape.ShapeHeader]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._hex_serializer = _HexSerializer(indent, use_tabs)

    def serialize(self, value: shape.ShapeHeader, depth: int = 0) -> str:
        indent = self.get_indent(depth)
        return (
            f"{indent}shape_header ( "
            f"{self._hex_serializer.serialize(value.flags1)} "
            f"{self._hex_serializer.serialize(value.flags2)} )"
        )


class _VectorSerializer(_Serializer[shape.Vector]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._float_serializer = _FloatSerializer(indent, use_tabs)

    def serialize(self, vector: shape.Vector, depth: int = 0) -> str:
        indent = self.get_indent(depth)
        return (
            f"{indent}vector ( "
            f"{self._float_serializer.serialize(vector.x)} "
            f"{self._float_serializer.serialize(vector.y)} "
            f"{self._float_serializer.serialize(vector.z)} )"
        )


class _VolumeSphereSerializer(_Serializer[shape.VolumeSphere]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._vector_serializer = _VectorSerializer(indent, use_tabs)
        self._float_serializer = _FloatSerializer(indent, use_tabs)

    def serialize(self, volume_sphere: shape.VolumeSphere, depth: int = 0) -> str:
        indent = self.get_indent(depth)
        inner_indent = self.get_indent(depth + 1)
        vector_str = self._vector_serializer.serialize(volume_sphere.vector, depth + 1).strip()
        radius_str = self._float_serializer.serialize(volume_sphere.radius)
        return (
            f"{indent}vol_sphere (\n"
            f"{inner_indent}{vector_str} {radius_str}\n"
            f"{indent})"
        )


class _NamedShaderSerializer(_Serializer[str]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._str_serializer = _StrSerializer(indent, use_tabs)

    def serialize(self, value: str, depth: int = 0) -> str:
        indent = self.get_indent(depth)
        return f"{indent}named_shader ( {self._str_serializer.serialize(value)} )"


class _NamedFilterModeSerializer(_Serializer[str]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._str_serializer = _StrSerializer(indent, use_tabs)

    def serialize(self, value: str, depth: int = 0) -> str:
        indent = self.get_indent(depth)
        return f"{indent}named_filter_mode ( {self._str_serializer.serialize(value)} )"


class _PointSerializer(_Serializer[shape.Point]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._float_serializer = _FloatSerializer(indent, use_tabs)

    def serialize(self, point: shape.Point, depth: int = 0) -> str:
        indent = self.get_indent(depth)
        return (
            f"{indent}point ( "
            f"{self._float_serializer.serialize(point.x)} "
            f"{self._float_serializer.serialize(point.y)} "
            f"{self._float_serializer.serialize(point.z)} )"
        )


class _UVPointSerializer(_Serializer[shape.UVPoint]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._float_serializer = _FloatSerializer(indent, use_tabs)

    def serialize(self, uv_point: shape.UVPoint, depth: int = 0) -> str:
        indent = self.get_indent(depth)
        return (
            f"{indent}uv_point ( "
            f"{self._float_serializer.serialize(uv_point.u)} "
            f"{self._float_serializer.serialize(uv_point.v)} )"
        )


class _ColourSerializer(_Serializer[shape.Colour]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._float_serializer = _FloatSerializer(indent, use_tabs)

    def serialize(self, colour: shape.Colour, depth: int = 0) -> str:
        indent = self.get_indent(depth)
        return (
            f"{indent}colour ( "
            f"{self._float_serializer.serialize(colour.a)} "
            f"{self._float_serializer.serialize(colour.r)} "
            f"{self._float_serializer.serialize(colour.g)} "
            f"{self._float_serializer.serialize(colour.b)} )"
        )


class _MatrixSerializer(_Serializer[shape.Matrix]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._float_serializer = _FloatSerializer(indent, use_tabs)

    def serialize(self, matrix: shape.Matrix, depth: int = 0) -> str:
        indent = self.get_indent(depth)
        values = (
            matrix.ax, matrix.ay, matrix.az,
            matrix.bx, matrix.by, matrix.bz,
            matrix.cx, matrix.cy, matrix.cz,
            matrix.dx, matrix.dy, matrix.dz
        )
        values_str = ' '.join(self._float_serializer.serialize(v) for v in values)
        return f"{indent}matrix {matrix.name} ( {values_str} )"


class _ImageSerializer(_Serializer[str]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._str_serializer = _StrSerializer(indent, use_tabs)

    def serialize(self, value: str, depth: int = 0) -> str:
        indent = self.get_indent(depth)
        return f"{indent}image ( {self._str_serializer.serialize(value)} )"


class _TextureSerializer(_Serializer[shape.Texture]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._int_serializer = _IntSerializer(indent, use_tabs)
        self._str_serializer = _StrSerializer(indent, use_tabs)
        self._float_serializer = _FloatSerializer(indent, use_tabs)
        self._hex_serializer = _HexSerializer(indent, use_tabs)

    def serialize(self, texture: shape.Texture, depth: int = 0) -> str:
        indent = self.get_indent(depth)
        return (
            f"{indent}texture ( "
            f"{self._int_serializer.serialize(texture.image_index)} "
            f"{self._str_serializer.serialize(texture.filter_mode)} "
            f"{self._float_serializer.serialize(texture.mipmap_lod_bias)} "
            f"{self._hex_serializer.serialize(texture.border_colour)} )"
        )


class _LightMaterialSerializer(_Serializer[shape.LightMaterial]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._hex_serializer = _HexSerializer(indent, use_tabs)
        self._int_serializer = _IntSerializer(indent, use_tabs)
        self._float_serializer = _FloatSerializer(indent, use_tabs)

    def serialize(self, light_material: shape.LightMaterial, depth: int = 0) -> str:
        indent = self.get_indent(depth)
        return (
            f"{indent}light_material ( "
            f"{self._hex_serializer.serialize(light_material.flags)} "
            f"{self._int_serializer.serialize(light_material.diff_colour_index)} "
            f"{self._int_serializer.serialize(light_material.amb_colour_index)} "
            f"{self._int_serializer.serialize(light_material.spec_colour_index)} "
            f"{self._int_serializer.serialize(light_material.emissive_colour_index)} "
            f"{self._float_serializer.serialize(light_material.spec_power)} )"
        )


class _UVOpSerializer(_Serializer[shape.UVOp]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._int_serializer = _IntSerializer(indent, use_tabs)

    def serialize(self, uv_op: shape.UVOp, depth: int = 0) -> str:
        indent = self.get_indent(depth)
        s = self._int_serializer.serialize

        if isinstance(uv_op, shape.UVOpCopy):
            return f"{indent}uv_op_copy ( {s(uv_op.texture_address_mode)} {s(uv_op.source_uv_index)} )"

        elif isinstance(uv_op, shape.UVOpReflectMapFull):
            return f"{indent}uv_op_reflectmapfull ( {s(uv_op.texture_address_mode)} )"

        elif isinstance(uv_op, shape.UVOpReflectMap):
            return f"{indent}uv_op_reflectmap ( {s(uv_op.texture_address_mode)} )"

        elif isinstance(uv_op, shape.UVOpUniformScale):
            return (
                f"{indent}uv_op_uniformscale ( "
                f"{s(uv_op.texture_address_mode)} {s(uv_op.source_uv_index)} "
                f"{s(uv_op.unknown3)} {s(uv_op.unknown4)} )"
            )

        elif isinstance(uv_op, shape.UVOpNonUniformScale):
            return (
                f"{indent}uv_op_nonuniformscale ( "
                f"{s(uv_op.texture_address_mode)} {s(uv_op.source_uv_index)} "
                f"{s(uv_op.unknown3)} {s(uv_op.unknown4)} )"
            )

        else:
            raise ValueError(f"Unknown UVOp type: {type(uv_op)}")


class _LightModelCfgSerializer(_Serializer[shape.LightModelCfg]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._hex_serializer = _HexSerializer(indent, use_tabs)
        self._uv_ops_serializer = _ListSerializer(
            list_name="uv_ops",
            item_serializer=_UVOpSerializer(indent, use_tabs),
            items_per_line=1,
            newline_after_header=True,
            newline_before_closing=True
        )

    def serialize(self, light_model_cfg: shape.LightModelCfg, depth: int = 0) -> str:
        indent = self.get_indent(depth)
        inner_depth = depth + 1

        flags = self._hex_serializer.serialize(light_model_cfg.flags)
        uv_ops_block = self._uv_ops_serializer.serialize(light_model_cfg.uv_ops, inner_depth)

        return (
            f"{indent}light_model_cfg ( {flags}\n"
            f"{uv_ops_block}\n"
            f"{indent})"
        )


class _VtxStateSerializer(_Serializer[shape.VtxState]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._hex_serializer = _HexSerializer(indent, use_tabs)
        self._int_serializer = _IntSerializer(indent, use_tabs)

    def serialize(self, vtx_state: shape.VtxState, depth: int = 0) -> str:
        indent = self.get_indent(depth)
        base = (
            f"{indent}vtx_state ( "
            f"{self._hex_serializer.serialize(vtx_state.flags)} "
            f"{self._int_serializer.serialize(vtx_state.matrix_index)} "
            f"{self._int_serializer.serialize(vtx_state.light_material_index)} "
            f"{self._int_serializer.serialize(vtx_state.light_model_cfg_index)} "
            f"{self._hex_serializer.serialize(vtx_state.light_flags)}"
        )
        if vtx_state.matrix2_index is not None:
            base += f" {self._int_serializer.serialize(vtx_state.matrix2_index)}"
        return base + " )"


class _PrimStateSerializer(_Serializer[shape.PrimState]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._hex_serializer = _HexSerializer(indent, use_tabs)
        self._int_serializer = _IntSerializer(indent, use_tabs)
        self._float_serializer = _FloatSerializer(indent, use_tabs)
        self._tex_idxs_serializer = _ListSerializer(
            list_name="tex_idxs",
            item_serializer=_IntSerializer(indent, use_tabs),
            items_per_line=None,
            newline_after_header=False,
            newline_before_closing=False
        )

    def serialize(self, prim_state: shape.PrimState, depth: int = 0) -> str:
        indent = self.get_indent(depth)
        inner_depth = depth + 1

        tex_idxs_block = self._tex_idxs_serializer.serialize(prim_state.texture_indices, inner_depth)
        return (
            f"{indent}prim_state {prim_state.name} ( "
            f"{self._hex_serializer.serialize(prim_state.flags)} "
            f"{self._int_serializer.serialize(prim_state.shader_index)}\n"
            f"{tex_idxs_block} "
            f"{self._float_serializer.serialize(prim_state.z_bias)} "
            f"{self._int_serializer.serialize(prim_state.vtx_state_index)} "
            f"{self._int_serializer.serialize(prim_state.alpha_test_mode)} "
            f"{self._int_serializer.serialize(prim_state.light_cfg_index)} "
            f"{self._int_serializer.serialize(prim_state.z_buffer_mode)}\n"
            f"{indent})"
        )


class _ShapeSerializer(_Serializer[shape.Shape]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._serializers = {
            "shape_header": _ShapeHeaderSerializer(indent, use_tabs),
            "volumes": _ListSerializer(
                list_name="volumes",
                item_serializer=_VolumeSphereSerializer(indent, use_tabs),
                indent=indent,
                use_tabs=use_tabs
            ),
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
            "light_materials": _ListSerializer(
                list_name="light_materials",
                item_serializer=_LightMaterialSerializer(indent, use_tabs),
                indent=indent,
                use_tabs=use_tabs
            ),
            "light_model_cfgs": _ListSerializer(
                list_name="light_model_cfgs",
                item_serializer=_LightModelCfgSerializer(indent, use_tabs),
                indent=indent,
                use_tabs=use_tabs
            ),
            "vtx_states": _ListSerializer(
                list_name="vtx_states",
                item_serializer=_VtxStateSerializer(indent, use_tabs),
                indent=indent,
                use_tabs=use_tabs
            ),
            "prim_states": _ListSerializer(
                list_name="prim_states",
                item_serializer=_PrimStateSerializer(indent, use_tabs),
                indent=indent,
                use_tabs=use_tabs
            ),
        }

    def serialize(self, shape: shape.Shape, depth: int = 0) -> str:
        indent = self.get_indent(depth)
        inner_depth = depth + 1

        lines = [f"{indent}shape ("]

        for name, serializer in self._serializers.items():
            items = getattr(shape, name, [])
            lines.append(serializer.serialize(items, depth=inner_depth))

        if shape.animations:
            # TODO handle optional animations block
            pass
        
        lines.append(f"{indent})")

        return "\n".join(lines)

