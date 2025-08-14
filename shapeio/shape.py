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

import numpy as np
from abc import ABC
from typing import List, Optional


class Vector:
    def __init__(self,
        x: float,
        y: float,
        z: float
    ):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"Vector(x={self.x}, y={self.y}, z={self.z})"

    def to_numpy(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    @classmethod
    def from_numpy(cls, array: np.ndarray):
        if array.shape != (3,):
            raise ValueError("Input array must have shape (3,).")
        return cls(array[0], array[1], array[2])

class Point:
    def __init__(self,
        x: float,
        y: float,
        z: float
    ):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y}, z={self.z})"

    def to_numpy(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    @classmethod
    def from_numpy(cls, array: np.ndarray):
        if array.shape != (3,):
            raise ValueError("Input array must have shape (3,).")
        return cls(array[0], array[1], array[2])

class UVPoint:
    def __init__(self,
        u: float,
        v: float
    ):
        self.u = u
        self.v = v

    def __repr__(self):
        return f"UVPoint(u={self.u}, v={self.v})"

    def to_numpy(self) -> np.ndarray:
        return np.array([self.u, self.v])

    @classmethod
    def from_numpy(cls, array: np.ndarray):
        if array.shape != (2,):
            raise ValueError("Input array must have shape (2,).")
        return cls(array[0], array[1])

class Colour:
    def __init__(self,
        a: float,
        r: float,
        g: float,
        b: float
    ):
        self.a = a
        self.r = r
        self.g = g
        self.b = b

    def __repr__(self):
        return f"Colour(a={self.a}, r={self.r}, g={self.g}, b={self.b})"

class Matrix:
    def __init__(self,
        name: str,
        ax: float, ay: float, az: float,
        bx: float, by: float, bz: float,
        cx: float, cy: float, cz: float,
        dx: float, dy: float, dz: float,
    ):
        self.name = name
        self.ax = ax
        self.ay = ay
        self.az = az
        self.bx = bx
        self.by = by
        self.bz = bz
        self.cx = cx
        self.cy = cy
        self.cz = cz
        self.dx = dx
        self.dy = dy
        self.dz = dz

    def __repr__(self):
        return (
            "Matrix(\n"
            f"  name='{self.name}',\n"
            f"  ax={self.ax}, ay={self.ay}, az={self.az},\n"
            f"  bx={self.bx}, by={self.by}, bz={self.bz},\n"
            f"  cx={self.cx}, cy={self.cy}, cz={self.cz},\n"
            f"  dx={self.dx}, dy={self.dy}, dz={self.dz}\n"
            ")"
        )

    def to_numpy(self) -> np.ndarray:
        """Convert to a 4x3 numpy matrix."""
        return np.array([
            [self.ax, self.ay, self.az],
            [self.bx, self.by, self.bz],
            [self.cx, self.cy, self.cz],
            [self.dx, self.dy, self.dz],
        ], dtype=np.float32)

    @classmethod
    def from_numpy(cls, name: str, array: np.ndarray):
        """Create a Matrix from a 4x3 numpy array."""
        if array.shape != (4, 3):
            raise ValueError("Input array must have shape (4, 3).")
        return cls(
            name,
            *array[0],
            *array[1],
            *array[2],
            *array[3],
        )

class VertexIdx:
    def __init__(self,
        vertex1_index: int,
        vertex2_index: int,
        vertex3_index: int
    ):
        self.vertex1_index = vertex1_index
        self.vertex2_index = vertex2_index
        self.vertex3_index = vertex3_index

    def __repr__(self):
        return (
            f"VertexIdx("
            f"vertex1_index={self.vertex1_index}, "
            f"vertex2_index={self.vertex2_index}, "
            f"vertex3_index={self.vertex3_index})"
        )

class NormalIdx:
    def __init__(self,
        index: int,
        unknown2: int
    ):
        self.index = index
        self.unknown2 = unknown2

    def __repr__(self):
        return (
            f"NormalIdx("
            f"index={self.index}, "
            f"unknown2={self.unknown2})"
        )

class IndexedTrilist:
    def __init__(self,
        vertex_idxs: List[VertexIdx],
        normal_idxs: List[NormalIdx],
        flags: List[str]
    ):
        self.vertex_idxs = vertex_idxs
        self.normal_idxs = normal_idxs
        self.flags = flags

    def __repr__(self):
        return (
            "IndexedTrilist("
            f"vertex_idxs (len={len(self.vertex_idxs)}), "
            f"normal_idxs (len={len(self.normal_idxs)}), "
            f"flags (len={len(self.flags)}))"
        )

class KeyPosition(ABC):
    def __init__(self,
        frame: int,
    ):
        self.frame = frame
    
    def _base_repr(self):
        return f"frame={self.frame}"

    def __repr__(self):
        return f"KeyPosition({self._base_repr()})"

class Controller(ABC):
    def __init__(self,
        keyframes: List[KeyPosition]
    ):
        self.keyframes = keyframes
    
    def _base_repr(self):
        return f"keyframes (len={len(self.keyframes)})"

    def __repr__(self):
        return f"Controller({self._base_repr()})"

class TCBRot(Controller):
    def __init__(self,
        keyframes: List[KeyPosition]
    ):
        super().__init__(keyframes)

    def __repr__(self):
        return f"TCBRot({self._base_repr()})"

class SlerpRot(KeyPosition):
    def __init__(self,
        frame: int,
        x: float,
        y: float,
        z: float,
        w: float
    ):
        super().__init__(frame)
        self.x = x
        self.y = y
        self.z = z
        self.w = w
    
    def __repr__(self):
        return (
            f"SlerpRot({self._base_repr()}, "
            f"x={self.x}, y={self.y}, z={self.z}, w={self.w})"
        )

class LinearPos(Controller):
    def __init__(self,
        keyframes: List[KeyPosition]
    ):
        super().__init__(keyframes)

    def __repr__(self):
        return f"LinearPos({self._base_repr()})"

class LinearKey(KeyPosition):
    def __init__(self,
        frame: int,
        x: float,
        y: float,
        z: float
    ):
        super().__init__(frame)
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return (
            f"LinearKey({self._base_repr()}, "
            f"x={self.x}, y={self.y}, z={self.z})"
        )

class TCBPos(Controller):
    def __init__(self,
        keyframes: List[KeyPosition]
    ):
        super().__init__(keyframes)

    def __repr__(self):
        return f"TCBPos({self._base_repr()})"

class TCBKey(KeyPosition):
    def __init__(self,
        frame: int,
        x: float,
        y: float,
        z: float,
        w: float,
        tension: float,
        continuity: float,
        bias: float,
        ease_in: float,
        ease_out: float
    ):
        super().__init__(frame)
        self.x = x
        self.y = y
        self.z = z
        self.w = w
        self.tension = tension
        self.continuity = continuity
        self.bias = bias
        self.ease_in = ease_in
        self.ease_out = ease_out

    def __repr__(self):
        return (
            f"TCBKey({self._base_repr()}, "
            f"x={self.x}, y={self.y}, z={self.z}, w={self.w}, "
            f"tension={self.tension}, continuity={self.continuity}, bias={self.bias}, "
            f"ease_in={self.ease_in}, ease_out={self.ease_out})"
        )

class AnimationNode:
    def __init__(self,
        name: str,
        controllers: List[Controller]
    ):
        self.name = name
        self.controllers = controllers

    def __repr__(self):
        return (
            f"AnimationNode(name={self.name}, "
            f"controllers (len={len(self.controllers)}))"
        )

class Animation:
    def __init__(self,
        frame_count: int,
        frame_rate: int,
        animation_nodes: List[AnimationNode]
    ):
        self.frame_count = frame_count
        self.frame_rate = frame_rate
        self.animation_nodes = animation_nodes

    def __repr__(self):
        return (
            f"Animation(frame_count={self.frame_count}, "
            f"frame_rate={self.frame_rate}, "
            f"animation_nodes (len={len(self.animation_nodes)}))"
        )

class ShapeHeader:
    def __init__(self,
        flags1: str,
        flags2: str
    ):
        self.flags1 = flags1
        self.flags2 = flags2

    def __repr__(self):
        return f"ShapeHeader(flags1={self.flags1}, flags2={self.flags2})"

class VolumeSphere:
    def __init__(self,
        vector: Vector,
        radius: float
    ):
        self.vector = vector
        self.radius = radius

    def __repr__(self):
        return f"VolumeSphere(vector={self.vector}, radius={self.radius})"

class Texture:
    def __init__(self,
        image_index: int,
        filter_mode: int,
        mipmap_lod_bias: float,
        border_colour: str
    ):
        self.image_index = image_index
        self.filter_mode = filter_mode
        self.mipmap_lod_bias = mipmap_lod_bias
        self.border_colour = border_colour

    def __repr__(self):
        return (
            f"Texture(image_index={self.image_index}, filter_mode={self.filter_mode}, "
            f"mipmap_lod_bias={self.mipmap_lod_bias}, border_colour={self.border_colour})"
        )

class LightMaterial:
    def __init__(self,
        flags: str,
        diff_colour_index: int,
        amb_colour_index: int,
        spec_colour_index: int,
        emissive_colour_index: int,
        spec_power: float
    ):
        self.flags = flags
        self.diff_colour_index = diff_colour_index
        self.amb_colour_index = amb_colour_index
        self.spec_colour_index = spec_colour_index
        self.emissive_colour_index = emissive_colour_index
        self.spec_power = spec_power

    def __repr__(self):
        return (
            f"LightMaterial(flags={self.flags}, "
            f"diff_colour_index={self.diff_colour_index}, amb_colour_index={self.amb_colour_index}, "
            f"spec_colour_index={self.spec_colour_index}, emissive_colour_index={self.emissive_colour_index}, "
            f"spec_power={self.spec_power})"
        )

class UVOp(ABC):
    def __init__(self,
        texture_address_mode: int
    ):
        self.texture_address_mode = texture_address_mode

    def _base_repr(self):
        return f"texture_address_mode={self.texture_address_mode}"

    def __repr__(self):
        return f"UVOp({self._base_repr()})"

class UVOpCopy(UVOp):
    def __init__(self,
        texture_address_mode: int,
        source_uv_index: int
    ):
        super().__init__(texture_address_mode)
        self.source_uv_index = source_uv_index

    def __repr__(self):
        return f"UVOpCopy({self._base_repr()}, source_uv_index={self.source_uv_index})"

class UVOpReflectMapFull(UVOp):
    def __init__(self,
        texture_address_mode: int
    ):
        super().__init__(texture_address_mode)

    def __repr__(self):
        return f"UVOpReflectMapFull({self._base_repr()})"

class UVOpReflectMap(UVOp):
    def __init__(self,
        texture_address_mode: int
    ):
        super().__init__(texture_address_mode)

    def __repr__(self):
        return f"UVOpReflectMap({self._base_repr()})"

class UVOpUniformScale(UVOp):
    def __init__(self,
        texture_address_mode: int,
        source_uv_index: int,
        unknown3: int,
        unknown4: int
    ):
        super().__init__(texture_address_mode)
        self.source_uv_index = source_uv_index
        self.unknown3 = unknown3
        self.unknown4 = unknown4

    def __repr__(self):
        return (
            f"UVOpUniformScale({self._base_repr()}, source_uv_index={self.source_uv_index}, "
            f"unknown3={self.unknown3}, unknown4={self.unknown4})"
        )

class UVOpNonUniformScale(UVOp):
    def __init__(self,
        texture_address_mode: int,
        source_uv_index: int,
        unknown3: int,
        unknown4: int
    ):
        super().__init__(texture_address_mode)
        self.source_uv_index = source_uv_index
        self.unknown3 = unknown3
        self.unknown4 = unknown4

    def __repr__(self):
        return (
            f"UVOpNonUniformScale({self._base_repr()}, source_uv_index={self.source_uv_index}, "
            f"unknown3={self.unknown3}, unknown4={self.unknown4})"
        )

class LightModelCfg:
    def __init__(self,
        flags: str,
        uv_ops: List[UVOp]
    ):
        self.flags = flags
        self.uv_ops = uv_ops

    def __repr__(self):
        return f"LightModelCfg(flags={self.flags}, uv_ops (len={len(self.uv_ops)}))"

class VtxState:
    def __init__(self,
        flags: str,
        matrix_index: int,
        light_material_index: int,
        light_model_cfg_index: int,
        light_flags: str,
        matrix2_index: Optional[int] = None
    ):
        self.flags = flags
        self.matrix_index = matrix_index
        self.light_material_index = light_material_index
        self.light_model_cfg_index = light_model_cfg_index
        self.light_flags = light_flags
        self.matrix2_index = matrix2_index

    def __repr__(self):
        return (
            f"VtxState(flags={self.flags}, matrix_index={self.matrix_index}, "
            f"light_material_index={self.light_material_index}, "
            f"light_model_cfg_index={self.light_model_cfg_index}, "
            f"light_flags={self.light_flags}, matrix2_index={self.matrix2_index})"
        )

class PrimState:
    def __init__(self,
        name: str,
        flags: str,
        shader_index: int,
        texture_indices: List[int],
        z_bias: float,
        vtx_state_index: int,
        alpha_test_mode: int,
        light_cfg_index: int,
        z_buffer_mode: int
    ):
        self.name = name
        self.flags = flags
        self.shader_index = shader_index
        self.texture_indices = texture_indices
        self.z_bias = z_bias
        self.vtx_state_index = vtx_state_index
        self.alpha_test_mode = alpha_test_mode
        self.light_cfg_index = light_cfg_index
        self.z_buffer_mode = z_buffer_mode

    def __repr__(self):
        return (
            f"PrimState(name={self.name}, flags={self.flags}, shader_index={self.shader_index}, "
            f"texture_indices (len={len(self.texture_indices)}), z_bias={self.z_bias}, "
            f"vtx_state_index={self.vtx_state_index}, alpha_test_mode={self.alpha_test_mode}, "
            f"light_cfg_index={self.light_cfg_index}, z_buffer_mode={self.z_buffer_mode})"
        )

class DistanceLevelsHeader:
    def __init__(self,
        dlevel_bias: int
    ):
        self.dlevel_bias = dlevel_bias

    def __repr__(self):
        return f"DistanceLevelsHeader(dlevel_bias={self.dlevel_bias})"

class CullablePrims:
    def __init__(self,
        num_prims: int,
        num_flat_sections: int,
        num_prim_indices: int
    ):
        self.num_prims = num_prims
        self.num_flat_sections = num_flat_sections
        self.num_prim_indices = num_prim_indices

    def __repr__(self):
        return (
            f"CullablePrims(num_prims={self.num_prims}, "
            f"num_flat_sections={self.num_flat_sections}, "
            f"num_prim_indices={self.num_prim_indices})"
        )

class GeometryNode:
    def __init__(self,
        tx_light_cmds: int,
        node_x_tx_light_cmds: int,
        trilists: int,
        line_lists: int,
        pt_lists: int,
        cullable_prims: CullablePrims
    ):
        self.tx_light_cmds = tx_light_cmds
        self.node_x_tx_light_cmds = node_x_tx_light_cmds
        self.trilists = trilists
        self.line_lists = line_lists
        self.pt_lists = pt_lists
        self.cullable_prims = cullable_prims

    def __repr__(self):
        return (
            f"GeometryNode(tx_light_cmds={self.tx_light_cmds}, "
            f"node_x_tx_light_cmds={self.node_x_tx_light_cmds}, "
            f"trilists={self.trilists}, line_lists={self.line_lists}, "
            f"pt_lists={self.pt_lists}, cullable_prims={self.cullable_prims})"
        )

class GeometryInfo:
    def __init__(self,
        face_normals: int,
        tx_light_cmds: int,
        node_x_tx_light_cmds: int,
        trilist_indices: int,
        line_list_indices: int,
        node_x_trilist_indices: int,
        trilists: int,
        line_lists: int,
        pt_lists: int,
        node_x_trilists: int,
        geometry_nodes: List[GeometryNode],
        geometry_node_map: List[int]
    ):
        self.face_normals = face_normals
        self.tx_light_cmds = tx_light_cmds
        self.node_x_tx_light_cmds = node_x_tx_light_cmds
        self.trilist_indices = trilist_indices
        self.line_list_indices = line_list_indices
        self.node_x_trilist_indices = node_x_trilist_indices
        self.trilists = trilists
        self.line_lists = line_lists
        self.pt_lists = pt_lists
        self.node_x_trilists = node_x_trilists
        self.geometry_nodes = geometry_nodes
        self.geometry_node_map = geometry_node_map

    def __repr__(self):
        return (
            f"GeometryInfo(face_normals={self.face_normals}, "
            f"tx_light_cmds={self.tx_light_cmds}, node_x_tx_light_cmds={self.node_x_tx_light_cmds}, "
            f"trilist_indices={self.trilist_indices}, line_list_indices={self.line_list_indices}, "
            f"node_x_trilist_indices={self.node_x_trilist_indices}, trilists={self.trilists}, "
            f"line_lists={self.line_lists}, pt_lists={self.pt_lists}, node_x_trilists={self.node_x_trilists}, "
            f"geometry_nodes (len={len(self.geometry_nodes)}), geometry_node_map (len={len(self.geometry_node_map)}))"
        )

class SubObjectHeader:
    def __init__(self,
        flags: str,
        sort_vector_index: int,
        volume_index: int,
        source_vtx_fmt_flags: str,
        destination_vtx_fmt_flags: str,
        geometry_info: GeometryInfo,
        subobject_shaders: List[int],
        subobject_light_cfgs: List[int],
        subobject_id: int
    ):
        self.flags = flags
        self.sort_vector_index = sort_vector_index
        self.volume_index = volume_index
        self.source_vtx_fmt_flags = source_vtx_fmt_flags
        self.destination_vtx_fmt_flags = destination_vtx_fmt_flags
        self.geometry_info = geometry_info
        self.subobject_shaders = subobject_shaders
        self.subobject_light_cfgs = subobject_light_cfgs
        self.subobject_id = subobject_id

    def __repr__(self):
        return (
            f"SubObjectHeader(flags={self.flags}, sort_vector_index={self.sort_vector_index}, "
            f"volume_index={self.volume_index}, source_vtx_fmt_flags={self.source_vtx_fmt_flags}, "
            f"destination_vtx_fmt_flags={self.destination_vtx_fmt_flags}, geometry_info={self.geometry_info}, "
            f"subobject_shaders (len={len(self.subobject_shaders)}), "
            f"subobject_light_cfgs (len={len(self.subobject_light_cfgs)}), "
            f"subobject_id={self.subobject_id})"
        )

class Vertex:
    def __init__(self,
        flags: str,
        point_index: int,
        normal_index: int,
        colour1: str,
        colour2: str,
        vertex_uvs: List[int]
    ):
        self.flags = flags
        self.point_index = point_index
        self.normal_index = normal_index
        self.colour1 = colour1
        self.colour2 = colour2
        self.vertex_uvs = vertex_uvs

    def __repr__(self):
        return (
            f"Vertex(flags={self.flags}, point_index={self.point_index}, normal_index={self.normal_index}, "
            f"colour1={self.colour1}, colour2={self.colour2}, vertex_uvs (len={len(self.vertex_uvs)}))"
        )

class VertexSet:
    def __init__(self,
        vtx_state: int,
        vtx_start_index: int,
        vtx_count: int
    ):
        self.vtx_state = vtx_state
        self.vtx_start_index = vtx_start_index
        self.vtx_count = vtx_count

    def __repr__(self):
        return (
            f"VertexSet(vtx_state={self.vtx_state}, vtx_start_index={self.vtx_start_index}, vtx_count={self.vtx_count})"
        )

class Primitive:
    def __init__(self,
        prim_state_index: int,
        indexed_trilist: IndexedTrilist
    ):
        self.prim_state_index = prim_state_index
        self.indexed_trilist = indexed_trilist

    def __repr__(self):
        return (
            f"Primitive(prim_state_index={self.prim_state_index}, "
            f"indexed_trilist={self.indexed_trilist})"
        )

class SubObject:
    def __init__(self,
        sub_object_header: SubObjectHeader,
        vertices: List[Vertex],
        vertex_sets: List[VertexSet],
        primitives: List[Primitive]
    ):
        self.sub_object_header = sub_object_header
        self.vertices = vertices
        self.vertex_sets = vertex_sets
        self.primitives = primitives

    def __repr__(self):
        return (
            f"SubObject(sub_object_header={self.sub_object_header}, "
            f"vertices (len={len(self.vertices)}), "
            f"vertex_sets (len={len(self.vertex_sets)}), "
            f"primitives (len={len(self.primitives)}))"
        )

class DistanceLevelHeader:
    def __init__(self,
        dlevel_selection: int,
        hierarchy: List[int]
    ):
        self.dlevel_selection = dlevel_selection
        self.hierarchy = hierarchy
    
    def __repr__(self):
        return (
            f"DistanceLevelHeader(dlevel_selection={self.dlevel_selection}, "
            f"hierarchy (len={len(self.hierarchy)}))"
        )

class DistanceLevel:
    def __init__(self,
        distance_level_header: DistanceLevelHeader,
        sub_objects: List[SubObject]
    ):
        self.distance_level_header = distance_level_header
        self.sub_objects = sub_objects

    def __repr__(self):
        return (
            f"DistanceLevel(distance_level_header={self.distance_level_header}, "
            f"sub_objects (len={len(self.sub_objects)}))"
        )

class LodControl:
    def __init__(self,
        distance_levels_header: DistanceLevelsHeader,
        distance_levels: List[DistanceLevel]
    ):
        self.distance_levels_header = distance_levels_header
        self.distance_levels = distance_levels

    def __repr__(self):
        return (
            f"LodControl(distance_levels_header={self.distance_levels_header}, "
            f"distance_levels (len={len(self.distance_levels)}))"
        )

class Shape:
    def __init__(self,
        shape_header: ShapeHeader,
        volumes: List[VolumeSphere],
        shader_names: List[str],
        texture_filter_names: List[str],
        points: List[Point],
        uv_points: List[UVPoint],
        normals: List[Vector],
        sort_vectors: List[Vector],
        colours: List[Colour],
        matrices: List[Matrix],
        images: List[str],
        textures: List[Texture],
        light_materials: List[LightMaterial],
        light_model_cfgs: List[LightModelCfg],
        vtx_states: List[VtxState],
        prim_states: List[PrimState],
        lod_controls: List[LodControl],
        animations: Optional[List[Animation]] = None
    ):
        self.shape_header = shape_header
        self.volumes = volumes
        self.shader_names = shader_names
        self.texture_filter_names = texture_filter_names
        self.points = points
        self.uv_points = uv_points
        self.normals = normals
        self.sort_vectors = sort_vectors
        self.colours = colours
        self.matrices = matrices
        self.images = images
        self.textures = textures
        self.light_materials = light_materials
        self.light_model_cfgs = light_model_cfgs
        self.vtx_states = vtx_states
        self.prim_states = prim_states
        self.lod_controls = lod_controls
        self.animations = animations or []

    def __repr__(self):
        return (
            f"Shape(shape_header={self.shape_header}, "
            f"volumes (len={len(self.volumes)}), "
            f"shader_names (len={len(self.shader_names)}), "
            f"texture_filter_names (len={len(self.texture_filter_names)}), "
            f"points (len={len(self.points)}), "
            f"uv_points (len={len(self.uv_points)}), "
            f"normals (len={len(self.normals)}), "
            f"sort_vectors (len={len(self.sort_vectors)}), "
            f"colours (len={len(self.colours)}), "
            f"matrices (len={len(self.matrices)}), "
            f"images (len={len(self.images)}), "
            f"textures (len={len(self.textures)}), "
            f"light_materials (len={len(self.light_materials)}), "
            f"light_model_cfgs (len={len(self.light_model_cfgs)}), "
            f"vtx_states (len={len(self.vtx_states)}), "
            f"prim_states (len={len(self.prim_states)}), "
            f"lod_controls (len={len(self.lod_controls)}), "
            f"animations (len={len(self.animations)}))"
        )

