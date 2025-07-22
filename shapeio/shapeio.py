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


def _detect_encoding(fp: str) -> str:
    with open(fp, 'rb') as f:
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


def dump(obj, fp):
    pass


def dumps(obj):
    pass


def load(fp):
    pass


def loads(s):
    pass


def is_compressed(fp: str) -> Optional[bool]:
    with open(fp, 'r', encoding=_detect_encoding(fp)) as f:
        try:
            header = f.read(32)
            if header.startswith("SIMISA@@@@@@@@@@JINX0s1t______"):
                return False
            elif header == "":
                return None
        except UnicodeDecodeError:
            pass
        
        return True


def compress(fp: str, ffeditc_path: str) -> None:
    if not self.is_compressed():
        subprocess.call([ffeditc_path, fp, "/o:" + fp])


def decompress(fp: str, ffeditc_path: str) -> None:
    if self.is_compressed():
        subprocess.call([ffeditc_path, fp, "/u", "/o:" + fp])

