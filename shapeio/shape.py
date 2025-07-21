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
from typing import List


class Shape:
    def __init__(self,
        shape_header: ShapeHeader,
        volumes: List[VolumeSphere],
        shader_names: List[NamedShader],
        texture_filter_names: List[NamedFilterMode],
        points: List[Point],
        uv_points: List[UVPoint],
        normals: List[Vector],
        sort_vectors: List[Vector],
        colours: int,
        matrices: List[Matrix],
        images: List[Image],
        light_materials: int,
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
        self.light_materials = light_materials

class ShapeHeader:
    def __init__(self,
        flag1: str,
        flag2: str
    ):
        self.flag1 = flag1
        self.flag2 = flag2

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

class NamedShader:
    def __init__(self,
        name: str
    ):
        self.name = name

class NamedFilterMode:
    def __init__(self,
        name: str
    ):
        self.name = name

class Point:
    def __init__(self,
        x: float
        y: float
        z: float
    ):
        self.x = x
        self.y = y
        self.z = z

class UVPoint:
    def __init__(self,
        u: float
        v: float
    ):
        self.u = u
        self.v = v

class Matrix:
    def __init__(self,
        name: str,
        m11: float,
        m12: float,
        m13: float,
        m21: float,
        m22: float,
        m23: float,
        m31: float,
        m32: float,
        m33: float,
        m41: float,
        m42: float,
        m43: float
    ):
        self.name = name
        self.m11 = m11
        self.m12 = m12
        self.m13 = m13
        self.m21 = m21
        self.m22 = m22
        self.m23 = m23
        self.m31 = m31
        self.m32 = m32
        self.m33 = m33
        self.m41 = m41
        self.m42 = m42
        self.m43 = m43

class Image:
    def __init__(self,
        name: str
    ):
        self.name = name

class Texture:
    def __init__(self,
        image_index: int,
        filter_mode: int,
        mipmap_lod_bias: int,
        border_colour: str
    ):
        self.image_index = image_index
        self.filter_mode = filter_mode
        self.mipmap_lod_bias = mipmap_lod_bias
        self.border_colour = border_colour