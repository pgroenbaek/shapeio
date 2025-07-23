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

import codecs
import subprocess
from typing import Optional


def _detect_encoding(filepath: str) -> str:
    with open(filepath, 'rb') as f:
        b = f.read(4)
        bstartswith = b.startswith
        if bstartswith((codecs.BOM_UTF32_BE, codecs.BOM_UTF32_LE)):
            return 'utf-32'
        if bstartswith((codecs.BOM_UTF16_BE, codecs.BOM_UTF16_LE)):
            return 'utf-16'
        if bstartswith(codecs.BOM_UTF8):
            return 'utf-8-sig'

        if len(b) >= 4:
            if not b[0]:
                return 'utf-16-be' if b[1] else 'utf-32-be'
            if not b[1]:
                return 'utf-16-le' if b[2] or b[3] else 'utf-32-le'
        elif len(b) == 2:
            if not b[0]:
                return 'utf-16-be'
            if not b[1]:
                return 'utf-16-le'
        return 'utf-8'


def dump(shape: shape.Shape, filepath: str, indent: int = 1, use_tabs: bool = True) -> None:
    encoder = ShapeEncoder(indent=indent, use_tabs=use_tabs)
    text = encoder.encode(shape)
    with open(filepath, 'w', encoding='utf-16-le') as f:
        f.write(text)


def load(filepath: str) -> shape.Shape:
    if is_compressed(filepath):
        raise ValueError("""Cannot load shape while the file is compressed. Please use the 'decompress(ffeditc_path: str)' method or decompress it manually.""")
    encoding = _detect_encoding(filepath)
    with open(filepath, 'r', encoding=encoding) as f:
        text = f.read()
    decoder = ShapeDecoder()
    return decoder.decode(text)


def dumps(shape: shape.Shape, indent: int = 1, use_tabs: bool = True) -> str:
    encoder = ShapeEncoder(indent=indent, use_tabs=use_tabs)
    return encoder.encode(shape)


def loads(shape_string: str) -> shape.Shape:
    decoder = ShapeDecoder()
    return decoder.decode(s)


def is_compressed(filepath: str) -> Optional[bool]:
    with open(filepath, 'r', encoding=_detect_encoding(filepath)) as f:
        try:
            header = f.read(32)
            if header.startswith("SIMISA@@@@@@@@@@JINX0s1t______"):
                return False
            elif header == "":
                return None
        except UnicodeDecodeError:
            pass
        
        return True


def compress(filepath: str, ffeditc_path: str) -> None:
    if not is_compressed():
        subprocess.call([ffeditc_path, filepath, "/o:" + filepath])


def decompress(filepath: str, ffeditc_path: str) -> None:
    if is_compressed():
        subprocess.call([ffeditc_path, filepath, "/u", "/o:" + filepath])

