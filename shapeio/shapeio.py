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

import io
import os
import re
import zlib
import codecs
import shutil
import fnmatch
import tempfile
import subprocess
from typing import Optional, List

from . import shape
from .decoder import ShapeDecoder
from .encoder import ShapeEncoder


def _detect_encoding(filepath: str) -> str:
    """
    Detect the text encoding of a file by inspecting its initial bytes (BOM or heuristics).

    Args:
        filepath (str): Path to the file to check.

    Returns:
        str: The detected encoding string suitable for use in `open()`.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be accessed.
        OSError: For other OS-related errors while reading the file.
    """
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


class ShapeCompressedError(Exception):
    """Raised when attempting to load a shape file that is compressed."""
    pass


def find_directory_files(
    directory: str,
    match_files: List[str],
    ignore_files: Optional[List[str]] = None
) -> List[str]:
    """
    Return a list of filenames in the given directory that match specified patterns,
    excluding those that match ignore patterns.

    Args:
        directory (str): Path to the directory to search.
        match_files (List[str]): List of glob-style patterns to include (e.g., ["*.s", "*.sd"]).
        ignore_files (Optional[List[str]]): List of glob-style patterns to exclude from the results.

    Returns:
        List[str]: Filenames in the directory that match the include patterns but not the exclude patterns.

    Raises:
        FileNotFoundError: If the specified directory does not exist.
        PermissionError: If access to the directory is denied.
        OSError: For other OS-related errors during directory listing.
    """
    files = []

    for file_name in os.listdir(directory):
        if any([fnmatch.fnmatch(file_name, x) for x in match_files]):
            if ignore_files is not None:
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
    """
    Serialize a shape object to a file in a readable text format.

    Args:
        shape (shape.Shape): The shape object to serialize.
        filepath (str): Path to the file where the shape will be saved.
        indent (int, optional): Number of indentation levels for formatting. Defaults to 1.
        use_tabs (bool, optional): Whether to use tabs for indentation instead of spaces. Defaults to True.

    Raises:
        OSError: If the file cannot be opened or written to.
    """
    if not isinstance(shape, shape.Shape):
        raise TypeError(f"Parameter 'shape' must be of type shape.Shape, but got {type(shape).__name__}")

    encoder = ShapeEncoder(indent=indent, use_tabs=use_tabs)
    text = "\ufeff" + encoder.encode(shape)

    with open(filepath, 'w', encoding='utf-16-le') as f:
        f.write(text)


def load(filepath: str) -> shape.Shape:
    """
    Load a shape object from a text file.

    The file must be uncompressed. If the shape file is compressed, a ValueError is raised.

    Args:
        filepath (str): Path to the shape file to load.

    Returns:
        shape.Shape: The deserialized shape object.

    Raises:
        ShapeCompressedError: If the shape file is detected as compressed.
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be accessed.
        OSError: If an I/O error occurs while opening the file.
        BlockNotFoundError: If a required block is missing or malformed in the shape data.
        CountMismatchError: If item counts do not match expectations in the shape data.
        ParenthesisMismatchError: If parentheses in the shape data are unmatched.
        BlockFormatError: If the format in shape data block is malformed.
    """
    if is_compressed(filepath):
        raise ShapeCompressedError("""Cannot load shape while it is compressed.
            First use the 'decompress' function or decompress it using another tool.""")
    
    with open(filepath, 'r', encoding=_detect_encoding(filepath)) as f:
        text = f.read()
    
    decoder = ShapeDecoder()
    return decoder.decode(text)


def dumps(
    shape: shape.Shape,
    indent: int = 1,
    use_tabs: bool = True
) -> str:
    """
    Serialize a shape object to a formatted string.

    Args:
        shape (shape.Shape): The shape object to serialize.
        indent (int, optional): Number of indentation levels for formatting. Defaults to 1.
        use_tabs (bool, optional): Whether to use tabs for indentation instead of spaces. Defaults to True.

    Returns:
        str: The serialized shape as a formatted string.
    """
    if not isinstance(shape, shape.Shape):
        raise TypeError(f"Parameter 'shape' must be of type shape.Shape, but got {type(shape).__name__}")

    encoder = ShapeEncoder(indent=indent, use_tabs=use_tabs)
    return encoder.encode(shape)


def loads(shape_string: str) -> shape.Shape:
    """
    Deserialize a shape object from a string.

    Args:
        shape_string (str): The string containing serialized shape data.

    Returns:
        shape.Shape: The deserialized shape object.

    Raises:
        BlockNotFoundError: If a required block is missing or malformed in the shape data.
        CountMismatchError: If item counts do not match expectations in the shape data.
        ParenthesisMismatchError: If parentheses in the shape data are unmatched.
        BlockFormatError: If the format in shape data block is malformed.
    """
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
    with open(filepath, "rb") as f:
        bom = f.read(2)
        is_unicode = (bom == b"\xFF\xFE")

        if is_unicode:
            buffer = f.read(32)
            header = buffer.decode("utf-16-le")
        else:
            buffer = bom + f.read(14)
            header = buffer.decode("ascii", errors="ignore")

        if header.startswith("SIMISA@F") or header.startswith("\r\nSIMISA@F"):
            return True

        elif header.startswith("SIMISA@@") or header.startswith("\r\nSIMISA@@"):
            return False

        return None


def is_shape(filepath: str) -> bool:
    """
    Checks if the given file is a shape file.

    Args:
        filepath (str): Path to the file to check.

    Returns:
        bool: True if the file is a shape file (compressed or uncompressed),
              False otherwise.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be accessed.
        OSError: If an I/O error occurs while opening the file.
    """
    compressed = is_compressed(filepath)

    if compressed is None:
        return False

    with open(filepath, "rb") as f:
        bom = f.read(2)
        is_unicode = (bom == b"\xFF\xFE")

        if is_unicode:
            header_bytes = f.read(32)
            header = header_bytes[:16].decode("utf-16-le")
        else:
            header_bytes = bom + f.read(14)
            header = header_bytes[:8].decode("ascii", errors="ignore")

        if compressed:
            f.read(2)
            decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
            file_stream = io.BytesIO(decompressor.decompress(f.read()))
        elif header.startswith("\r\n"):
            if is_unicode:
                f.read(4)
            else:
                f.read(2)
            file_stream = f
        else:
            file_stream = f

        if is_unicode:
            subheader_bytes = file_stream.read(32)
            subheader = subheader_bytes[:16].decode("utf-16-le")
        else:
            subheader_bytes = file_stream.read(16)
            subheader = subheader_bytes[:8].decode("ascii", errors="ignore")

        if len(subheader) < 5:
            return False
        
        return subheader[5] == "s"


def copy(old_filepath: str, new_filepath: str) -> None:
    """
    Copy a file from the source path to the destination path.

    Args:
        old_filepath (str): Path to the source file.
        new_filepath (str): Path where the file should be copied.

    Raises:
        FileNotFoundError: If the source file does not exist.
        PermissionError: If the file cannot be accessed or written.
        OSError: For other OS-related errors during copying.
    """
    shutil.copyfile(old_filepath, new_filepath)


def replace(filepath: str, search_exp: str, replace_str: str) -> None:
    """
    Replace occurrences of a regex pattern in a text file with a given string.

    Args:
        filepath (str): Path to the shape file to modify.
        search_exp (str): Regular expression pattern to search for.
        replace_str (str): Replacement string.

    Raises:
        ShapeCompressedError: If the file is a shape file and it is compressed.
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be accessed or written.
        OSError: For other OS-related errors during file operations.
    """
    if is_shape(filepath) and is_compressed(filepath):
        raise ShapeCompressedError("""Cannot replace text in a compressed shape.
            First use the 'decompress' function or decompress it using another tool.""")

    pattern = re.compile(search_exp)
    encoding = _detect_encoding(filepath)

    with open(filepath, 'r', encoding=encoding) as f:
        text = f.read()
    
    new_text = pattern.sub(replace_str, text)
    
    with open(filepath, 'w', encoding=encoding) as f:
        f.write(new_text)


def replace_ignorecase(filepath: str, search_exp: str, replace_str: str) -> None:
    """
    Replace occurrences of a regex pattern (case-insensitive) in a text file with a given string.

    Args:
        filepath (str): Path to the shape file to modify.
        search_exp (str): Regular expression pattern to search for.
        replace_str (str): Replacement string.

    Raises:
        ShapeCompressedError: If the file is a shape file and it is compressed.
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be accessed or written.
        OSError: For other OS-related errors during file operations.
    """
    if is_shape(filepath) and is_compressed(filepath):
        raise ShapeCompressedError("""Cannot replace text in a compressed shape.
            First use the 'decompress' function or decompress it using another tool.""")

    pattern = re.compile(search_exp, re.IGNORECASE)
    encoding = _detect_encoding(filepath)

    with open(filepath, 'r', encoding=encoding) as f:
        text = f.read()
    
    new_text = pattern.sub(replace_str, text)
    
    with open(filepath, 'w', encoding=encoding) as f:
        f.write(new_text)