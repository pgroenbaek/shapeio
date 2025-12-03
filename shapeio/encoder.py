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
from collections import defaultdict
from typing import List, Optional, TypeVar, Generic

from . import shape

T = TypeVar('T')


class ShapeEncoder:
    """
    Encoder for serializing MSTS/ORTS shape objects into a formatted string.

    This class produces shape text that includes the expected MSTS header
    and supports indentation customization. It uses an internal serializer
    to convert a `shape.Shape` instance into the structured text format.

    Args:
        indent (int, optional): Number of indentation levels for formatting. Defaults to 1.
        use_tabs (bool, optional): Whether to use tabs instead of spaces for indentation. Defaults to True.

    Methods:
        encode(shape: shape.Shape) -> str:
            Serializes a shape object into a properly formatted shape string,
            including the MSTS shape header.

    Returns:
        str: The complete shape text including the standard header and formatting.
    """
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        self._serializer = _ShapeSerializer(indent=indent, use_tabs=use_tabs)

    def encode(self, shape: shape.Shape) -> str:
        header = "SIMISA@@@@@@@@@@JINX0s1t______\n\n"
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
        disable_inner_indent: bool = False,
        count_multiplier: float = 1,
        newline_after_header: bool = True,
        newline_before_closing: bool = True
    ) -> str:
        """
        Serializes a list of items into a structured text format list block.

        This method produces a structured text format list block with a header line containing
        the block name and item count, followed by serialized representations of the
        items. Supports indentation, line wrapping, and optional newlines for improved
        formatting flexibility.

        Args:
            items (List[T]): The list of items to serialize.
            block_name (str): The name of the list block.
            item_serializer (_Serializer[T]): Serializer instance capable of serializing
                each item to a string, with optional indentation depth.
            depth (int, optional): Indentation depth for the block. Defaults to 0.
            items_per_line (Optional[int], optional): Number of items per output line.
                If None, all items appear on one line. Defaults to 1.
            disable_inner_indent (bool, optional): If True, disables additional inner indentation
                for serialized items. Defaults to False.
            count_multiplier (float, optional): Multiplier applied to the item count displayed
                in the header. Defaults to 1.
            newline_after_header (bool, optional): If True, inserts a newline after the header
                line (before items). Defaults to True.
            newline_before_closing (bool, optional): If True, places the closing parenthesis
                on a new line. Otherwise, it is appended to the last line of items.
                Defaults to True.

        Returns:
            str: The formatted, serialized list block as a string.
        """
        inner_depth = depth if disable_inner_indent else depth + 1
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

        vector = self._vector_serializer.serialize(volume_sphere.vector, depth + 1).strip()
        radius = self._float_serializer.serialize(volume_sphere.radius)

        return (
            f"{indent}vol_sphere (\n"
            f"{inner_indent}{vector} {radius}\n"
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
            f"{indent}prim_state {prim_state.name if prim_state.name is not None else ''} ( "
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


class _VertexSerializer(_Serializer[shape.Vertex]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._hex_serializer = _HexSerializer(indent, use_tabs)
        self._int_serializer = _IntSerializer(indent, use_tabs)

    def serialize(self, vertex: shape.Vertex, depth: int = 0) -> str:
        if not isinstance(vertex, shape.Vertex):
            raise TypeError(f"Parameter 'vertex' must be of type shape.Vertex, but got {type(vertex).__name__}")

        indent = self.get_indent(depth)
        inner_depth = depth + 1

        vertex_uvs_block = self._serialize_items_in_block(
            vertex.vertex_uvs,
            "vertex_uvs",
            self._int_serializer,
            inner_depth,
            items_per_line=None,
            newline_after_header=False,
            newline_before_closing=False
        )

        return (
            f"{indent}vertex ( "
            f"{self._hex_serializer.serialize(vertex.flags)} "
            f"{self._int_serializer.serialize(vertex.point_index)} "
            f"{self._int_serializer.serialize(vertex.normal_index)} "
            f"{self._hex_serializer.serialize(vertex.colour1)} "
            f"{self._hex_serializer.serialize(vertex.colour2)}\n"
            f"{vertex_uvs_block}\n"
            f"{indent})"
        )


class _VertexSetSerializer(_Serializer[shape.VertexSet]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._int_serializer = _IntSerializer(indent, use_tabs)

    def serialize(self, vertex_set: shape.VertexSet, depth: int = 0) -> str:
        if not isinstance(vertex_set, shape.VertexSet):
            raise TypeError(f"Parameter 'vertex_set' must be of type shape.VertexSet, but got {type(vertex_set).__name__}")

        indent = self.get_indent(depth)
        return (
            f"{indent}vertex_set ( "
            f"{self._int_serializer.serialize(vertex_set.vtx_state)} "
            f"{self._int_serializer.serialize(vertex_set.vtx_start_index)} "
            f"{self._int_serializer.serialize(vertex_set.vtx_count)} )"
        )


class _IndexedTrilistSerializer(_Serializer[shape.IndexedTrilist]):
    def __init__(self, indent=1, use_tabs=True):
        super().__init__(indent, use_tabs)
        self._int_serializer = _IntSerializer(indent, use_tabs)
        self._str_serializer = _StrSerializer(indent, use_tabs)
        self._hex_serializer = _HexSerializer(indent, use_tabs)
    
    def serialize(self, indexed_trilist: shape.IndexedTrilist, depth: int = 0) -> str:
        if not isinstance(indexed_trilist, shape.IndexedTrilist):
            raise TypeError(f"Parameter 'indexed_trilist' must be a shape.IndexedTrilist, but got {type(indexed_trilist).__name__}")
        
        indent = self.get_indent(depth)
        inner_depth = depth + 1

        flattened_vertex_idxs = [
            val
            for v in indexed_trilist.vertex_idxs
            for val in (v.vertex1_index, v.vertex2_index, v.vertex3_index)
        ]

        flattened_normal_idxs = [
            f"{n.index} {n.unknown2}"
            for n in indexed_trilist.normal_idxs
        ]

        vertex_idxs_block = self._serialize_items_in_block(
            flattened_vertex_idxs,
            "vertex_idxs",
            self._int_serializer,
            inner_depth,
            disable_inner_indent=True,
            items_per_line=240,
            newline_after_header=False,
            newline_before_closing=False
        )
        normal_idxs_block = self._serialize_items_in_block(
            flattened_normal_idxs,
            "normal_idxs",
            self._str_serializer,
            inner_depth,
            disable_inner_indent=True,
            items_per_line=120,
            newline_after_header=False,
            newline_before_closing=False
        )
        flags_block = self._serialize_items_in_block(
            indexed_trilist.flags,
            "flags",
            self._hex_serializer,
            inner_depth,
            disable_inner_indent=True,
            items_per_line=120,
            newline_after_header=False,
            newline_before_closing=False
        )

        return (
            f"{indent}indexed_trilist (\n"
            f"{vertex_idxs_block}\n"
            f"{normal_idxs_block}\n"
            f"{flags_block}\n"
            f"{indent})"
        )


class _PrimitivesSerializer(_Serializer[List[shape.Primitive]]):
    def __init__(self, indent=1, use_tabs=True):
        super().__init__(indent, use_tabs)
        self._trilist_serializer = _IndexedTrilistSerializer(indent, use_tabs)
        self._int_serializer = _IntSerializer(indent, use_tabs)

    def serialize(self, primitives: List[shape.Primitive], depth: int = 0) -> str:
        if not isinstance(primitives, list):
            raise TypeError(f"Parameter 'primitives' must be a list, but got {type(primitives).__name__}")
        
        for idx, primitive in enumerate(primitives):
            if not isinstance(primitive, shape.Primitive):
                raise TypeError(
                    f"Item at index {idx} in parameter 'primitives' must be of type shape.Primitive, but got {type(primitive).__name__}"
                )

        indent = self.get_indent(depth)
        inner_depth = depth + 1
        inner_indent = self.get_indent(inner_depth)

        grouped = defaultdict(list)
        for prim in primitives:
            grouped[prim.prim_state_index].append(prim.indexed_trilist)

        prim_state_idx_count = len(grouped)
        indexed_trilist_count = sum(len(trilists) for trilists in grouped.values())
        total_count = prim_state_idx_count + indexed_trilist_count

        lines = [f"{indent}primitives ( {total_count}"]

        for prim_state_index, trilists in grouped.items():
            idx_line = f"{inner_indent}prim_state_idx ( {prim_state_index} )"
            lines.append(idx_line)

            for trilist in trilists:
                trilist_block = self._trilist_serializer.serialize(trilist, inner_depth)
                lines.append(trilist_block)

        lines.append(f"{indent})")
        return "\n".join(lines)


class _CullablePrimsSerializer(_Serializer[shape.CullablePrims]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._int_serializer = _IntSerializer(indent, use_tabs)

    def serialize(self, cullable_prims: shape.CullablePrims, depth: int = 0) -> str:
        if not isinstance(cullable_prims, shape.CullablePrims):
            raise TypeError(f"Parameter 'cullable_prims' must be of type shape.CullablePrims, but got {type(cullable_prims).__name__}")

        indent = self.get_indent(depth)
        
        return (
            f"{indent}cullable_prims ( "
            f"{self._int_serializer.serialize(cullable_prims.num_prims)} "
            f"{self._int_serializer.serialize(cullable_prims.num_flat_sections)} "
            f"{self._int_serializer.serialize(cullable_prims.num_prim_indices)} )"
        )


class _GeometryNodeSerializer(_Serializer[shape.GeometryNode]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._int_serializer = _IntSerializer(indent, use_tabs)
        self._cullable_prims_serializer = _CullablePrimsSerializer(indent, use_tabs)

    def serialize(self, geometry_node: shape.GeometryNode, depth: int = 0) -> str:
        if not isinstance(geometry_node, shape.GeometryNode):
            raise TypeError(f"Parameter 'geometry_node' must be of type shape.GeometryNode, but got {type(geometry_node).__name__}")

        indent = self.get_indent(depth)
        inner_depth = depth + 1

        tx_light_cmds = self._int_serializer.serialize(geometry_node.tx_light_cmds)
        node_x_tx_light_cmds = self._int_serializer.serialize(geometry_node.node_x_tx_light_cmds)
        trilists = self._int_serializer.serialize(geometry_node.trilists)
        line_lists = self._int_serializer.serialize(geometry_node.line_lists)
        pt_lists = self._int_serializer.serialize(geometry_node.pt_lists)
        cullable_prims_block = self._cullable_prims_serializer.serialize(geometry_node.cullable_prims, inner_depth)
        
        return (
            f"{indent}geometry_node ( "
            f"{tx_light_cmds} "
            f"{node_x_tx_light_cmds} "
            f"{trilists} "
            f"{line_lists} "
            f"{pt_lists}\n"
            f"{cullable_prims_block}\n"
            f"{indent})"
        )


class _GeometryInfoSerializer(_Serializer[shape.GeometryInfo]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._int_serializer = _IntSerializer(indent, use_tabs)
        self._geometry_node_serializer = _GeometryNodeSerializer(indent, use_tabs)

    def serialize(self, geometry_info: shape.GeometryInfo, depth: int = 0) -> str:
        if not isinstance(geometry_info, shape.GeometryInfo):
            raise TypeError(f"Parameter 'geometry_info' must be of type shape.GeometryInfo, but got {type(geometry_info).__name__}")

        indent = self.get_indent(depth)
        inner_depth = depth + 1

        face_normals = self._int_serializer.serialize(geometry_info.face_normals)
        tx_light_cmds = self._int_serializer.serialize(geometry_info.tx_light_cmds)
        node_x_tx_light_cmds = self._int_serializer.serialize(geometry_info.node_x_tx_light_cmds)
        trilist_indices = self._int_serializer.serialize(geometry_info.trilist_indices)
        line_list_indices = self._int_serializer.serialize(geometry_info.line_list_indices)
        node_x_trilist_indices = self._int_serializer.serialize(geometry_info.node_x_trilist_indices)
        trilists = self._int_serializer.serialize(geometry_info.trilists)
        line_lists = self._int_serializer.serialize(geometry_info.line_lists)
        pt_lists = self._int_serializer.serialize(geometry_info.pt_lists)
        node_x_trilists = self._int_serializer.serialize(geometry_info.node_x_trilists)
        geometry_nodes_block = self._serialize_items_in_block(geometry_info.geometry_nodes, "geometry_nodes", self._geometry_node_serializer, inner_depth)
        geometry_node_map_block = self._serialize_items_in_block(
            geometry_info.geometry_node_map,
            "geometry_node_map",
            self._int_serializer,
            inner_depth,
            items_per_line=None,
            newline_after_header=False,
            newline_before_closing=False
        )

        return (
            f"{indent}geometry_info ( "
            f"{face_normals} "
            f"{tx_light_cmds} "
            f"{node_x_tx_light_cmds} "
            f"{trilist_indices} "
            f"{line_list_indices} "
            f"{node_x_trilist_indices} "
            f"{trilists} "
            f"{line_lists} "
            f"{pt_lists} "
            f"{node_x_trilists}\n"
            f"{geometry_nodes_block}\n"
            f"{geometry_node_map_block}\n"
            f"{indent})"
        )


class _SubObjectHeaderSerializer(_Serializer[shape.SubObjectHeader]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._int_serializer = _IntSerializer(indent, use_tabs)
        self._hex_serializer = _HexSerializer(indent, use_tabs)
        self._geometry_info_serializer = _GeometryInfoSerializer(indent, use_tabs)

    def serialize(self, sub_object_header: shape.SubObjectHeader, depth: int = 0) -> str:
        if not isinstance(sub_object_header, shape.SubObjectHeader):
            raise TypeError(f"Parameter 'sub_object_header' must be of type shape.SubObjectHeader, but got {type(sub_object_header).__name__}")

        indent = self.get_indent(depth)
        inner_depth = depth + 1

        flags = self._hex_serializer.serialize(sub_object_header.flags)
        sort_vector_index = self._int_serializer.serialize(sub_object_header.sort_vector_index)
        volume_index = self._int_serializer.serialize(sub_object_header.volume_index)
        source_vtx_fmt_flags = self._hex_serializer.serialize(sub_object_header.source_vtx_fmt_flags)
        destination_vtx_fmt_flags = self._hex_serializer.serialize(sub_object_header.destination_vtx_fmt_flags)
        geometry_info_block = self._geometry_info_serializer.serialize(sub_object_header.geometry_info, inner_depth)
        subobject_shaders_block = self._serialize_items_in_block(
            sub_object_header.subobject_shaders,
            "subobject_shaders",
            self._int_serializer,
            inner_depth,
            items_per_line=None,
            newline_after_header=False,
            newline_before_closing=False
        )
        subobject_light_cfgs_block = self._serialize_items_in_block(
            sub_object_header.subobject_light_cfgs,
            "subobject_light_cfgs",
            self._int_serializer,
            inner_depth,
            items_per_line=None,
            newline_after_header=False,
            newline_before_closing=False
        )
        subobject_id = self._int_serializer.serialize(sub_object_header.subobject_id)

        return (
            f"{indent}sub_object_header ( "
            f"{flags} "
            f"{sort_vector_index} "
            f"{volume_index} "
            f"{source_vtx_fmt_flags} "
            f"{destination_vtx_fmt_flags}\n"
            f"{geometry_info_block}\n"
            f"{subobject_shaders_block}\n"
            f"{subobject_light_cfgs_block} "
            f"{subobject_id}\n"
            f"{indent})"
        )


class _SubObjectSerializer(_Serializer[shape.SubObject]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._sub_object_header_serializer = _SubObjectHeaderSerializer(indent, use_tabs)
        self._vertex_serializer = _VertexSerializer(indent, use_tabs)
        self._vertex_set_serializer = _VertexSetSerializer(indent, use_tabs)
        self._primitives_serializer = _PrimitivesSerializer(indent, use_tabs)

    def serialize(self, sub_object: shape.SubObject, depth: int = 0) -> str:
        if not isinstance(sub_object, shape.SubObject):
            raise TypeError(f"Parameter 'sub_object' must be of type shape.SubObject, but got {type(sub_object).__name__}")

        indent = self.get_indent(depth)
        inner_depth = depth + 1

        header_block = self._sub_object_header_serializer.serialize(sub_object.sub_object_header, inner_depth)
        vertices_block = self._serialize_items_in_block(sub_object.vertices, "vertices", self._vertex_serializer, inner_depth)
        vertex_sets_block = self._serialize_items_in_block(sub_object.vertex_sets, "vertex_sets", self._vertex_set_serializer, inner_depth)
        primitives_block = self._primitives_serializer.serialize(sub_object.primitives, inner_depth)

        return (
            f"{indent}sub_object (\n"
            f"{header_block}\n"
            f"{vertices_block}\n"
            f"{vertex_sets_block}\n"
            f"{primitives_block}\n"
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
        self._sub_object_serializer = _SubObjectSerializer()

    def serialize(self, dlevel: shape.DistanceLevel, depth: int = 0) -> str:
        if not isinstance(dlevel, shape.DistanceLevel):
            raise TypeError(f"Parameter 'dlevel' must be of type shape.DistanceLevel, but got {type(dlevel).__name__}")

        indent = self.get_indent(depth)
        inner_depth = depth + 1

        header_block = self._dlevel_header_serializer.serialize(dlevel.distance_level_header, inner_depth)
        sub_objects_block = self._serialize_items_in_block(dlevel.sub_objects, "sub_objects", self._sub_object_serializer, inner_depth)

        return (
            f"{indent}distance_level (\n"
            f"{header_block}\n"
            f"{sub_objects_block}\n"
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


class _KeyPositionSerializer(_Serializer[shape.KeyPosition]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._int_serializer = _IntSerializer()
        self._float_serializer = _FloatSerializer()

    def serialize(self, key: shape.KeyPosition, depth: int = 0) -> str:
        if not isinstance(key, shape.KeyPosition):
            raise TypeError(f"Parameter 'key' must be of type shape.KeyPosition, but got {type(key).__name__}")

        indent = self.get_indent(depth)

        s = lambda v: self._float_serializer.serialize(v) if isinstance(v, float) else self._int_serializer.serialize(v)

        if isinstance(key, shape.SlerpRot):
            return f"{indent}slerp_rot ( {s(key.frame)} {s(key.x)} {s(key.y)} {s(key.z)} {s(key.w)} )"

        elif isinstance(key, shape.LinearKey):
            return f"{indent}linear_key ( {s(key.frame)} {s(key.x)} {s(key.y)} {s(key.z)} )"

        elif isinstance(key, shape.TCBKey):
            return (
                f"{indent}tcb_key ( {s(key.frame)} {s(key.x)} {s(key.y)} {s(key.z)} {s(key.w)} "
                f"{s(key.tension)} {s(key.continuity)} {s(key.bias)} {s(key.ease_in)} {s(key.ease_out)} )"
            )
        else:
            raise TypeError(f"Unknown key type: {type(key)}")


class _ControllerSerializer(_Serializer[shape.Controller]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._key_position_serializer = _KeyPositionSerializer()

    def serialize(self, controller: shape.Controller, depth: int = 0) -> str:
        if not isinstance(controller, shape.Controller):
            raise TypeError(f"Parameter 'controller' must be of type shape.Controller, but got {type(controller).__name__}")

        indent = self.get_indent(depth)
        inner_depth = depth + 1

        if isinstance(controller, shape.TCBRot):
            name = "tcb_rot"

        elif isinstance(controller, shape.LinearPos):
            name = "linear_pos"

        elif isinstance(controller, shape.TCBPos):
            name = "tcb_pos"

        else:
            raise TypeError(f"Unknown controller type: {type(controller)}")

        key_frames_block = "\n".join(self._key_position_serializer.serialize(k, inner_depth) for k in controller.keyframes)

        return (
            f"{indent}{name} ( {len(controller.keyframes)}\n"
            f"{key_frames_block}\n"
            f"{indent})"
        )


class _AnimationNodeSerializer(_Serializer[shape.AnimationNode]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._controller_serializer = _ControllerSerializer()

    def serialize(self, animation_node: shape.AnimationNode, depth: int = 0) -> str:
        if not isinstance(animation_node, shape.AnimationNode):
            raise TypeError(f"Parameter 'animation_node' must be of type shape.AnimationNode, but got {type(animation_node).__name__}")

        indent = self.get_indent(depth)
        inner_depth = depth + 1

        controllers_block = self._serialize_items_in_block(animation_node.controllers, "controllers", self._controller_serializer, inner_depth)

        return (
            f"{indent}anim_node {animation_node.name} (\n"
            f"{controllers_block}\n"
            f"{indent})"
        )


class _AnimationSerializer(_Serializer[shape.Animation]):
    def __init__(self, indent: int = 1, use_tabs: bool = True):
        super().__init__(indent, use_tabs)
        self._int_serializer = _IntSerializer(indent, use_tabs)
        self._animation_node_serializer = _AnimationNodeSerializer(indent, use_tabs)

    def serialize(self, animation: shape.Animation, depth: int = 0) -> str:
        if not isinstance(animation, shape.Animation):
            raise TypeError(f"Parameter 'animation' must be of type shape.Animation, but got {type(animation).__name__}")

        indent = self.get_indent(depth)
        inner_depth = depth + 1

        frame_count = self._int_serializer.serialize(animation.frame_count)
        frame_rate = self._int_serializer.serialize(animation.frame_rate)
        animation_node_block = self._serialize_items_in_block(animation.animation_nodes, "anim_nodes", self._animation_node_serializer, inner_depth)

        return (
            f"{indent}animation ( "
            f"{frame_count} "
            f"{frame_rate}\n"
            f"{animation_node_block}\n"
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
        self._animation_serializer = _AnimationSerializer(indent, use_tabs)

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
        if s.animations:
            animations_block = self._serialize_items_in_block(s.animations, "animations", self._animation_serializer, inner_depth)
        else:
            animations_block = None

        animations_block_str = f"{animations_block}\n" if animations_block else ""

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
            f"{animations_block_str}"
            f"{indent})"
        )

