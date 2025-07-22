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

class ShapeHeader:
    def __init__(self,
        flags1: str,
        flags2: str
    ):
        self.flags1 = flags1
        self.flags2 = flags2

class VolumeSphere:
    def __init__(self,
        vector: Vector,
        radius: float
    ):
        self.vector = vector
        self.radius = radius

class Vector:
    def __init__(self,
        x: float,
        y: float,
        z: float
    ):
        self.x = x
        self.y = y
        self.z = z

class Point:
    def __init__(self,
        x: float,
        y: float,
        z: float
    ):
        self.x = x
        self.y = y
        self.z = z

class UVPoint:
    def __init__(self,
        u: float,
        v: float
    ):
        self.u = u
        self.v = v

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

class Matrix:
    def __init__(self,
        name: str,
        ax: float,
        ay: float,
        az: float,
        bx: float,
        by: float,
        bz: float,
        cx: float,
        cy: float,
        cz: float,
        dx: float,
        dy: float,
        dz: float,
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

class LightModelCfg:
    def __init__(self,
        flags: str,
        uv_ops: List[UVOp]
    ):
        self.flags = flags
        self.uv_ops = uv_ops

class UVOp(ABC):
    def __init__(self,
        texture_address_mode: int
    ):
        self.texture_address_mode = texture_address_mode

class UVOpCopy(UVOp):
    def __init__(self,
        texture_address_mode: int,
        source_uv_index: int
    ):
        super().__init__(texture_address_mode)
        self.source_uv_index = source_uv_index

class UVOpReflectMapFull(UVOp):
    def __init__(self,
        texture_address_mode: int
    ):
        super().__init__(texture_address_mode)

class UVOpReflectMap(UVOp):
    def __init__(self,
        texture_address_mode: int
    ):
        super().__init__(texture_address_mode)

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

class LodControl:
    def __init__(self,
        distance_levels_header: DistanceLevelsHeader,
        distance_levels: List[DistanceLevel]
    ):
        self.distance_levels_header = distance_levels_header
        self.distance_levels = distance_levels

class DistanceLevelsHeader:
    def __init__(self,
        dlevel_bias: int
    ):
        self.dlevel_bias = dlevel_bias

class DistanceLevel:
    def __init__(self,
        distance_level_header: DistanceLevelHeader,
        sub_objects: List[SubObject]
    ):
        self.distance_level_header = distance_level_header
        self.sub_objects = sub_objects

class DistanceLevelHeader:
    def __init__(self,
        dlevel_selection: int,
        hierarchy: List[int]
    ):
        self.dlevel_selection = dlevel_selection
        self.hierarchy = hierarchy

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

class CullablePrims:
    def __init__(self,
        num_prims: int,
        num_flat_sections: int,
        num_prim_indices: int
    ):
        self.num_prims = num_prims
        self.num_flat_sections = num_flat_sections
        self.num_prim_indices = num_prim_indices

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

class VertexSet:
    def __init__(self,
        vtx_state: int,
        vtx_start_index: int,
        vtx_count: int
    ):
        self.vtx_state = vtx_state
        self.vtx_start_index = vtx_start_index
        self.vtx_count = vtx_count

class Primitive:
    def __init__(self,
        prim_state_index: int,
        indexed_trilist: IndexedTrilist
    ):
        self.prim_state_index = prim_state_index
        self.indexed_trilist = indexed_trilist

class IndexedTrilist:
    def __init__(self,
        vertex_indexes: List[VertexIdx],
        normal_indexes: List[NormalIdx],
        flags: List[str]
    ):
        self.vertex_indexes = vertex_indexes
        self.normal_indexes = normal_indexes
        self.flags = flags

class VertexIdx:
    def __init__(self,
        vertex1_index: int,
        vertex2_index: int,
        vertex3_index: int
    ):
        self.vertex1_index = vertex1_index
        self.vertex2_index = vertex2_index
        self.vertex3_index = vertex3_index

class NormalIdx:
    def __init__(self,
        index: int,
        unknown2: int
    ):
        self.index = index
        self.unknown2 = unknown2

class Animation:
    def __init__(self,
        frame_count: int,
        frame_rate: int,
        animation_nodes: List[AnimationNode]
    ):
        self.frame_count = frame_count
        self.frame_rate = frame_rate
        self.animation_nodes = animation_nodes

class AnimationNode:
    def __init__(self,
        name: str,
        controllers: List[Controller]
    ):
        self.name = name
        self.controllers = controllers

class KeyPosition(ABC):
    def __init__(self,
        frame: int,
    ):
        self.frame = frame

class Controller(ABC):
    def __init__(self,
        keyframes: List[KeyPosition]
    ):
        self.keyframes = keyframes

class TCBRot(Controller):
    def __init__(self,
        keyframes: List[KeyPosition]
    ):
        super().__init__(keyframes)

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

class LinearPos(Controller):
    def __init__(self,
        keyframes: List[KeyPosition]
    ):
        super().__init__(keyframes)

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

class TCBPos(Controller):
    def __init__(self,
        keyframes: List[KeyPosition]
    ):
        super().__init__(keyframes)

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