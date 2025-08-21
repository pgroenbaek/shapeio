"""
ShapeIO

This module provides functions to decode MSTS/ORTS shape files into Python
objects and to encode them back into the shape file format.

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

__version__ = '0.5.0b0'
__all__ = [
    'shape', 'find_directory_files',
    'load', 'loads', 'dump', 'dumps',
    'is_shape', 'is_compressed'
    'copy', 'replace', 'replace_ignorecase',
    'ShapeCompressedError',
    'ShapeParserError', 'BlockNotFoundError', 'CountMismatchError',
    'ParenthesisMismatchError', 'BlockFormatError',
    'ShapeDecoder', 'ShapeEncoder'
]

__author__ = 'Peter Grønbæk Andersen <peter@grnbk.io>'

from . import shape
from .shapeio import find_directory_files
from .shapeio import load, loads, dump, dumps
from .shapeio import is_shape, is_compressed
from .shapeio import copy, replace, replace_ignorecase
from .shapeio import ShapeCompressedError
from .decoder import ShapeDecoder
from .decoder import ShapeParserError, BlockNotFoundError, CountMismatchError
from .decoder import ParenthesisMismatchError, BlockFormatError
from .encoder import ShapeEncoder
