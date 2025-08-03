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

import os
import re
import codecs
import shutil
import fnmatch
import subprocess
from typing import Optional, List

from . import shape, compression
from .decoder import ShapeDecoder
from .encoder import ShapeEncoder


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


def find_directory_files(
    directory: str,
    match_files: List[str],
    ignore_files: List[str]
) -> List[str]:

    files = []

    for file_name in os.listdir(directory):
        if any([fnmatch.fnmatch(file_name, x) for x in match_files]):
            if any([fnmatch.fnmatch(file_name, x) for x in ignore_files]):
                continue
            files.append(file_name)

    return files


def dump(
    shape: shape.Shape,
    filepath: str,
    indent: int = 1,
    use_tabs: bool = True
) -> None:

    encoder = ShapeEncoder(indent=indent, use_tabs=use_tabs)
    text = encoder.encode(shape)

    with open(filepath, 'w', encoding='utf-16-le') as f:
        f.write(text)


def load(filepath: str) -> shape.Shape:
    if is_compressed(filepath):
        raise ValueError("""Cannot load shape while it is compressed.
            Please use the 'decompress' function or decompress it by hand.""")
    
    with open(filepath, 'r', encoding=_detect_encoding(filepath)) as f:
        text = f.read()
    
    decoder = ShapeDecoder()
    return decoder.decode(text)


def dumps(
    shape: shape.Shape,
    indent: int = 1,
    use_tabs: bool = True
) -> str:

    encoder = ShapeEncoder(indent=indent, use_tabs=use_tabs)
    return encoder.encode(shape)


def loads(shape_string: str) -> shape.Shape:
    decoder = ShapeDecoder()
    return decoder.decode(shape_string)


def is_compressed(filepath: str) -> Optional[bool]:
    """
    Determines whether a shape file is compressed.

    Args:
        filepath (str): Path to the shape file to inspect.

    Returns:
        bool:
            - True if the file appears to be compressed (binary format).
            - False if the file appears to be uncompressed (text format with a known header).
            - None if the file is readable as text but does not match known headers.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be accessed.
        OSError: If an I/O error occurs while opening the file.
    """
    with open(filepath, 'r', encoding=_detect_encoding(filepath)) as f:
        try:
            header = f.read(32)
            if header.startswith("SIMISA@@@@@@@@@@JINX0s1t______"):
                return False
            return None
        except UnicodeDecodeError:
            pass
        
        return True


def compress(
    input_filepath: str,
    output_filepath: Optional[str],
    tkutils_dll_filepath: str
) -> bool:
    """
    Compresses a shape file if it is not already compressed.

    If `output_filepath` is None, the file is compressed in place using a temporary file.
    If the file is already compressed, no changes are made. If an output path is given
    and the file is already compressed, it is simply copied to the destination.

    Args:
        input_filepath (str): Path to the input shape file.
        output_filepath (Optional[str]): Destination path for the compressed file,
                                         or None to compress in place.
        tkutils_dll_filepath (str): Path to the TK.MSTS.Tokens DLL.

    Returns:
        bool: True if compression was performed, False if the file was already compressed
              and was either copied or left unchanged.

    Raises:
        EnvironmentError: If required runtime dependencies (Mono or .NET) are missing.
        FileNotFoundError: If the input file or specified DLL file is not found.
        ImportError: If the DLL fails to load.
        OSError: If file operations fail.
    """
    already_compressed = is_compressed(input_filepath)

    if output_filepath is None:
        if already_compressed:
            return False
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            compression.compress_shape(input_filepath, tmp_path, tkutils_dll_filepath)
            os.replace(tmp_path, input_filepath)
            return True
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    else:
        if already_compressed:
            if input_filepath != output_filepath:
                copy(input_filepath, output_filepath)
            
            return False
        
        return compression.compress_shape(input_filepath, output_filepath, tkutils_dll_filepath)


def decompress(
    input_filepath: str,
    output_filepath: Optional[str],
    tkutils_dll_filepath: str
) -> bool:
    """
    Decompresses a shape file if it is currently compressed.

    If `output_filepath` is None, the file is decompressed in place using a temporary file.
    If the file is already decompressed, no changes are made. If an output path is given
    and the file is already decompressed, it is simply copied to the destination.

    Args:
        input_filepath (str): Path to the input shape file.
        output_filepath (Optional[str]): Destination path for the decompressed file,
                                         or None to decompress in place.
        tkutils_dll_filepath (str): Path to the TK.MSTS.Tokens DLL.

    Returns:
        bool: True if decompression was performed, False if the file was already decompressed
              and was either copied or left unchanged.

    Raises:
        EnvironmentError: If required runtime dependencies (Mono or .NET) are missing.
        FileNotFoundError: If the input file or specified DLL file is not found.
        ImportError: If the DLL fails to load.
        OSError: If file operations fail.
    """
    currently_compressed = is_compressed(input_filepath)

    if output_filepath is None:
        if not currently_compressed:
            return False
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            compression.decompress_shape(input_filepath, tmp_path, tkutils_dll_filepath)
            os.replace(tmp_path, input_filepath)
            return True
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        
    else:
        if not currently_compressed:
            if input_filepath != output_filepath:
                copy(input_filepath, output_filepath)
            
            return False
        
        return compression.decompress_shape(input_filepath, output_filepath, tkutils_dll_filepath)


def is_shape(filepath: str) -> bool:
    """
    Checks if the given file is a shape file.

    Args:
        filepath (str): Path to the file to check.

    Returns:
        bool: True if the file is a shape file (compressed or uncompressed),
              False if it cannot be identified as a shape file.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be accessed.
        OSError: If an I/O error occurs while opening the file.
    """
    return is_compressed(filepath) is not None


def copy(old_filepath: str, new_filepath: str) -> None:
    shutil.copyfile(old_filepath, new_filepath)


def replace(filepath: str, search_exp: str, replace_str: str) -> None:
    if is_shape(filepath) and is_compressed(filepath):
        raise ValueError("""Cannot replace text in a compressed shape.
            Please use the 'decompress' function or decompress it by hand.""")

    pattern = re.compile(search_exp)
    encoding = _detect_encoding(filepath)

    with open(filepath, 'r', encoding=encoding) as f:
        text = f.read()
    
    new_text = pattern.sub(replace_str, text)
    
    with open(filepath, 'w', encoding=encoding) as f:
        f.write(new_text)


def replace_ignorecase(filepath: str, search_exp: str, replace_str: str) -> None:
    if is_shape(filepath) and is_compressed(filepath):
        raise ValueError("""Cannot replace text in a compressed shape.
            Please use the 'decompress' function or decompress it by hand.""")

    pattern = re.compile(search_exp, re.IGNORECASE)
    encoding = _detect_encoding(filepath)

    with open(filepath, 'r', encoding=encoding) as f:
        text = f.read()
    
    new_text = pattern.sub(replace_str, text)
    
    with open(filepath, 'w', encoding=encoding) as f:
        f.write(new_text)