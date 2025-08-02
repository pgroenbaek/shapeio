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

    def _serialize_items_in_block(self,
        items: List[T],
        block_name: str,
        item_serializer: "_Serializer[T]",
        depth: int = 0,
        items_per_line: Optional[int] = 1,
        count_multiplier: int = 1,
        newline_after_header: bool = True,
        newline_before_closing: bool = True
    ) -> str:

        inner_depth = depth + 1
        indent = self.get_indent(depth)
        inner_indent = self.get_indent(inner_depth)

        count = int(len(items) * count_multiplier)
        header = f"{indent}{block_name} ( {count}"

        list_empty = len(items) == 0
        should_newline_after_header = newline_after_header and not list_empty
        should_newline_before_closing = newline_before_closing and not list_empty

        lines = [header]

        serialized_items = [item_serializer.serialize(item, inner_depth).strip() for item in items]
        effective_items_per_line = items_per_line or len(serialized_items)

        current_line = []
        is_first_line = True

        for idx, item_str in enumerate(serialized_items):
            current_line.append(item_str)
            is_last_item = idx == len(serialized_items) - 1
            should_wrap = len(current_line) == effective_items_per_line

            if should_wrap or is_last_item:
                line = " ".join(current_line)

                if not should_newline_after_header and is_first_line:
                    lines[-1] += f" {line}"
                else:
                    if items_per_line is None and not should_newline_before_closing:
                        lines.append(line)
                    else:
                        lines.append(f"{inner_indent}{line}")

                current_line = []
                is_first_line = False
        
        if should_newline_before_closing:
            lines.append(f"{indent})")
        else:
            lines[-1] += " )"

        return "\n".join(lines)


class _IntSerializer(_Serializer[int]):
    def serialize(self, value: int, depth: int = 0) -> str:
        if not isinstance(value, int):
            raise TypeError(f"Parameter 'value' must be of type int, but got {type(value).__name__}")
        
        return str(value)


class _FloatSerializer(_Serializer[float]):
    def serialize(self, value: float, depth: int = 0) -> str:
        if not isinstance(value, float) and not isinstance(value, int):
            raise TypeError(f"Parameter 'value' must be of type float or int, but got {type(value).__name__}")

        return f"{value:.6g}"


class _StrSerializer(_Serializer[str]):
    def serialize(self, value: str, depth: int = 0) -> str:
        if not isinstance(value, str):
            raise TypeError(f"Parameter 'value' must be of type str, but got {type(value).__name__}")

        return value


class _HexSerializer(_Serializer[str]):
    def serialize(self, value: str, depth: int = 0) -> str:
        if not isinstance(value, str):
            raise TypeError(f"Parameter 'value' must be of type str, but got {type(value).__name__}")

        return value.lower()


class _ShapeHeaderSerializer(_Serializer[shape.ShapeHeader]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._hex_serializer = _HexSerializer(indent, use_tabs)

    def serialize(self, shape_header: shape.ShapeHeader, depth: int = 0) -> str:
        if not isinstance(shape_header, shape.ShapeHeader):
            raise TypeError(f"Parameter 'shape_header' must be of type shape.ShapeHeader, but got {type(shape_header).__name__}")

        indent = self.get_indent(depth)
        return (
            f"{indent}shape_header ( "
            f"{self._hex_serializer.serialize(shape_header.flags1)} "
            f"{self._hex_serializer.serialize(shape_header.flags2)} )"
        )


class _VectorSerializer(_Serializer[shape.Vector]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._float_serializer = _FloatSerializer(indent, use_tabs)

    def serialize(self, vector: shape.Vector, depth: int = 0) -> str:
        if not isinstance(vector, shape.Vector):
            raise TypeError(f"Parameter 'vector' must be of type shape.Vector, but got {type(vector).__name__}")

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
        if not isinstance(volume_sphere, shape.VolumeSphere):
            raise TypeError(f"Parameter 'volume_sphere' must be of type shape.VolumeSphere, but got {type(volume_sphere).__name__}")

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
        if not isinstance(point, shape.Point):
            raise TypeError(f"Parameter 'point' must be of type shape.Point, but got {type(point).__name__}")

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
        if not isinstance(uv_point, shape.UVPoint):
            raise TypeError(f"Parameter 'uv_point' must be of type shape.UVPoint, but got {type(uv_point).__name__}")

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
        if not isinstance(colour, shape.Colour):
            raise TypeError(f"Parameter 'colour' must be of type shape.Colour, but got {type(colour).__name__}")

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
        if not isinstance(matrix, shape.Matrix):
            raise TypeError(f"Parameter 'matrix' must be of type shape.Matrix, but got {type(matrix).__name__}")

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
        self._float_serializer = _FloatSerializer(indent, use_tabs)
        self._hex_serializer = _HexSerializer(indent, use_tabs)

    def serialize(self, texture: shape.Texture, depth: int = 0) -> str:
        if not isinstance(texture, shape.Texture):
            raise TypeError(f"Parameter 'texture' must be of type shape.Texture, but got {type(texture).__name__}")

        indent = self.get_indent(depth)
        return (
            f"{indent}texture ( "
            f"{self._int_serializer.serialize(texture.image_index)} "
            f"{self._int_serializer.serialize(texture.filter_mode)} "
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
        if not isinstance(light_material, shape.LightMaterial):
            raise TypeError(f"Parameter 'light_material' must be of type shape.LightMaterial, but got {type(light_material).__name__}")

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
        if not isinstance(uv_op, shape.UVOp):
            raise TypeError(f"Parameter 'uv_op' must be of type shape.UVOp, but got {type(uv_op).__name__}")

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
        self._uv_op_serializer = _UVOpSerializer(indent, use_tabs)

    def serialize(self, light_model_cfg: shape.LightModelCfg, depth: int = 0) -> str:
        if not isinstance(light_model_cfg, shape.LightModelCfg):
            raise TypeError(f"Parameter 'light_model_cfg' must be of type shape.LightModelCfg, but got {type(light_model_cfg).__name__}")

        indent = self.get_indent(depth)
        inner_depth = depth + 1

        flags = self._hex_serializer.serialize(light_model_cfg.flags)
        uv_ops_block = self._serialize_items_in_block(light_model_cfg.uv_ops, "uv_ops", self._uv_op_serializer, inner_depth)

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
        if not isinstance(vtx_state, shape.VtxState):
            raise TypeError(f"Parameter 'vtx_state' must be of type shape.VtxState, but got {type(vtx_state).__name__}")

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

    def serialize(self, prim_state: shape.PrimState, depth: int = 0) -> str:
        if not isinstance(prim_state, shape.PrimState):
            raise TypeError(f"Parameter 'prim_state' must be of type shape.PrimState, but got {type(prim_state).__name__}")

        indent = self.get_indent(depth)
        inner_depth = depth + 1

        tex_idxs_block = self._serialize_items_in_block(
            prim_state.texture_indices,
            "tex_idxs",
            self._int_serializer,
            inner_depth,
            items_per_line=None,
            newline_after_header=False,
            newline_before_closing=False
        )
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


class _DistanceLevelSelectionSerializer(_Serializer[int]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._int_serializer = _IntSerializer(indent, use_tabs)

    def serialize(self, value: int, depth: int = 0) -> str:
        if not isinstance(value, int):
            raise TypeError(f"Parameter 'value' must be of type int, but got {type(value).__name__}")

        indent = self.get_indent(depth)
        return f"{indent}dlevel_selection ( {self._int_serializer.serialize(value)} )"


class _DistanceLevelHeaderSerializer(_Serializer[shape.DistanceLevelHeader]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._distance_level_selection_serializer = _DistanceLevelSelectionSerializer(indent, use_tabs)
        self._int_serializer = _IntSerializer(indent, use_tabs)

    def serialize(self, header: shape.DistanceLevelHeader, depth: int = 0) -> str:
        if not isinstance(header, shape.DistanceLevelHeader):
            raise TypeError(f"Parameter 'header' must be of type shape.DistanceLevelHeader, but got {type(header).__name__}")

        indent = self.get_indent(depth)
        inner_depth = depth + 1

        dlevel_selection_block = self._distance_level_selection_serializer.serialize(header.dlevel_selection, inner_depth)
        hierarchy_block = self._serialize_items_in_block(
            header.hierarchy,
            "hierarchy",
            self._int_serializer,
            inner_depth,
            items_per_line=None,
            newline_after_header=False,
            newline_before_closing=False
        )
        return (
            f"{indent}distance_level_header (\n"
            f"{dlevel_selection_block}\n"
            f"{hierarchy_block}\n"
            f"{indent})"
        )


class _DistanceLevelSerializer(_Serializer[shape.DistanceLevel]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._dlevel_header_serializer = _DistanceLevelHeaderSerializer(indent, use_tabs)
        #self._subobject_list_serializer = _ListSerializer(
        #    list_name="sub_objects",
        #    item_serializer=_SubObjectSerializer(indent, use_tabs),
        #    items_per_line=1,
        #    newline_after_header=False,
        #    newline_before_closing=False
        #)

    def serialize(self, dlevel: shape.DistanceLevel, depth: int = 0) -> str:
        if not isinstance(dlevel, shape.DistanceLevel):
            raise TypeError(f"Parameter 'dlevel' must be of type shape.DistanceLevel, but got {type(dlevel).__name__}")

        indent = self.get_indent(depth)
        inner_depth = depth + 1

        header_block = self._dlevel_header_serializer.serialize(dlevel.distance_level_header, inner_depth)
        subobject_block = ""#self._subobject_list_serializer.serialize(dlevel.sub_objects, inner_depth)

        return (
            f"{indent}distance_level (\n"
            f"{header_block}\n"
            f"{subobject_block}\n"
            f"{indent})"
        )


class _DistanceLevelsHeaderSerializer(_Serializer[shape.DistanceLevelsHeader]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._int_serializer = _IntSerializer(indent, use_tabs)

    def serialize(self, header: shape.DistanceLevelsHeader, depth: int = 0) -> str:
        if not isinstance(header, shape.DistanceLevelsHeader):
            raise TypeError(f"Parameter 'header' must be of type shape.DistanceLevelsHeader, but got {type(header).__name__}")

        indent = self.get_indent(depth)
        return f"{indent}distance_levels_header ( {self._int_serializer.serialize(header.dlevel_bias)} )"


class _LodControlSerializer(_Serializer[shape.LodControl]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._distance_levels_header_serializer = _DistanceLevelsHeaderSerializer(indent, use_tabs)
        self._distance_level_serializer = _DistanceLevelSerializer(indent, use_tabs)

    def serialize(self, lod_control: shape.LodControl, depth: int = 0) -> str:
        if not isinstance(lod_control, shape.LodControl):
            raise TypeError(f"Parameter 'lod_control' must be of type shape.LodControl, but got {type(lod_control).__name__}")

        indent = self.get_indent(depth)
        inner_depth = depth + 1

        dlevels_header_block = self._distance_levels_header_serializer.serialize(lod_control.distance_levels_header, inner_depth)
        dlevels_block = self._serialize_items_in_block(lod_control.distance_levels, "distance_levels", self._distance_level_serializer, inner_depth)

        return (
            f"{indent}lod_control (\n"
            f"{dlevels_header_block}\n"
            f"{dlevels_block}\n"
            f"{indent})"
        )


class _ShapeSerializer(_Serializer[shape.Shape]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._shape_header_serializer = _ShapeHeaderSerializer(indent, use_tabs)
        self._volume_sphere_serializer = _VolumeSphereSerializer(indent, use_tabs)
        self._named_shader_serializer = _NamedShaderSerializer(indent, use_tabs)
        self._named_filter_mode_serializer = _NamedFilterModeSerializer(indent, use_tabs)
        self._point_serializer = _PointSerializer(indent, use_tabs)
        self._uv_point_serializer = _UVPointSerializer(indent, use_tabs)
        self._vector_serializer = _VectorSerializer(indent, use_tabs)
        self._colour_serializer = _ColourSerializer(indent, use_tabs)
        self._matrix_serializer = _MatrixSerializer(indent, use_tabs)
        self._image_serializer = _ImageSerializer(indent, use_tabs)
        self._texture_serializer = _TextureSerializer(indent, use_tabs)
        self._light_material_serializer = _LightMaterialSerializer(indent, use_tabs)
        self._light_model_cfg_serializer = _LightModelCfgSerializer(indent, use_tabs)
        self._vtx_state_serializer = _VtxStateSerializer(indent, use_tabs)
        self._prim_state_serializer = _PrimStateSerializer(indent, use_tabs)
        self._lod_control_serializer = _LodControlSerializer(indent, use_tabs)

    def serialize(self, s: shape.Shape, depth: int = 0) -> str:
        if not isinstance(s, shape.Shape):
            raise TypeError(f"Parameter 's' must be of type shape.Shape, but got {type(s).__name__}")

        indent = self.get_indent(depth)
        inner_depth = depth + 1

        shape_header_block = self._shape_header_serializer.serialize(s.shape_header, inner_depth)
        volumes_block = self._serialize_items_in_block(s.volumes, "volumes", self._volume_sphere_serializer, inner_depth)
        shader_names_block = self._serialize_items_in_block(s.shader_names, "shader_names", self._named_shader_serializer, inner_depth)
        texture_filter_names_block = self._serialize_items_in_block(s.texture_filter_names, "texture_filter_names", self._named_filter_mode_serializer, inner_depth)
        points_block = self._serialize_items_in_block(s.points, "points", self._point_serializer, inner_depth)
        uv_points_block = self._serialize_items_in_block(s.uv_points, "uv_points", self._uv_point_serializer, inner_depth)
        normals_block = self._serialize_items_in_block(s.normals, "normals", self._vector_serializer, inner_depth)
        sort_vectors_block = self._serialize_items_in_block(s.sort_vectors, "sort_vectors", self._vector_serializer, inner_depth)
        colours_block = self._serialize_items_in_block(s.colours, "colours", self._colour_serializer, inner_depth)
        matrices_block = self._serialize_items_in_block(s.matrices, "matrices", self._matrix_serializer, inner_depth)
        images_block = self._serialize_items_in_block(s.images, "images", self._image_serializer, inner_depth)
        textures_block = self._serialize_items_in_block(s.textures, "textures", self._texture_serializer, inner_depth)
        light_materials_block = self._serialize_items_in_block(s.light_materials, "light_materials", self._light_material_serializer, inner_depth)
        light_model_cfgs_block = self._serialize_items_in_block(s.light_model_cfgs, "light_model_cfgs", self._light_model_cfg_serializer, inner_depth)
        vtx_states_block = self._serialize_items_in_block(s.vtx_states, "vtx_states", self._vtx_state_serializer, inner_depth)
        prim_states_block = self._serialize_items_in_block(s.prim_states, "prim_states", self._prim_state_serializer, inner_depth)
        lod_controls_block = self._serialize_items_in_block(s.lod_controls, "lod_controls", self._lod_control_serializer, inner_depth)

        return (
            f"{indent}shape (\n"
            f"{shape_header_block}\n"
            f"{volumes_block}\n"
            f"{shader_names_block}\n"
            f"{texture_filter_names_block}\n"
            f"{points_block}\n"
            f"{uv_points_block}\n"
            f"{normals_block}\n"
            f"{sort_vectors_block}\n"
            f"{colours_block}\n"
            f"{matrices_block}\n"
            f"{images_block}\n"
            f"{textures_block}\n"
            f"{light_materials_block}\n"
            f"{light_model_cfgs_block}\n"
            f"{vtx_states_block}\n"
            f"{prim_states_block}\n"
            f"{lod_controls_block}\n"
            f"{animations_block + '\n' if animations_block else ''}"
            f"{indent})"
        )

