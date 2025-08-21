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

import re
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, TypeVar, Generic, Pattern

from . import shape

T = TypeVar('T')


class ShapeDecoder:
    """
    Decoder for deserializing MSTS/ORTS shape data from a string into a shape object.

    This class uses an internal parser to interpret structured shape text
    and convert it into a `shape.Shape` instance.

    Methods:
        decode(text: str) -> shape.Shape:
            Parses the given text and returns a shape object.

    Raises:
        BlockNotFoundError: If a required block is missing or malformed in the shape data.
        CountMismatchError: If item counts do not match expectations in the shape data.
        ParenthesisMismatchError: If parentheses in the shape data are unmatched.
        BlockFormatError: If the format in a shape data block is malformed.
    """
    def __init__(self):
        self._parser = _ShapeParser()

    def decode(self, text: str) -> shape.Shape:
        return self._parser.parse(text)


class ShapeParserError(Exception):
    """Base class for parser errors."""
    pass

class BlockNotFoundError(ShapeParserError):
    """Raised when a specified block is not found or malformed."""
    pass

class CountMismatchError(ShapeParserError):
    """Raised when expected and actual item counts mismatch."""
    pass

class ParenthesisMismatchError(ShapeParserError):
    """Raised when parentheses in a block are unmatched."""
    pass

class BlockFormatError(ShapeParserError):
    """Raised when format in a block is malformed."""
    pass


class _Items():
    def __init__(self, items: List[str], expected_count: int):
        self.items = items
        self.expected_count = expected_count


class _ParsedItems(Generic[T]):
    def __init__(self, items: List[T], expected_count: int):
        self.items = items
        self.expected_count = expected_count


class _Parser(ABC, Generic[T]):
    @abstractmethod
    def parse(self, text: str) -> T:
        """
        Abstract method to parse input text and return an object of type T.

        Parameters:
            text (str): The input text to parse.

        Returns:
            T: Parsed representation of the input.
        """
        pass

    def _verify_count(self, expected: int, actual: int, item_type: str, block_name: str):
        """
        Verify that the expected count matches the actual number of items found.

        Parameters:
            expected (int): The expected count of items.
            actual (int): The actual number of items found.
            item_type (str): The name of the item being counted.
            block_name (str): The name of the block containing the items.

        Raises:
            CountMismatchError: If expected and actual counts do not match.
        """
        if expected != actual:
            raise CountMismatchError(
                f"Count mismatch for '{item_type}' in '{block_name}': "
                f"Expected {expected} but found {actual} items"
            )

    def _extract_count_from_header(self, block: str, block_name: str) -> int:
        """
        Extract the count of items from the header of a block.

        Parameters:
            block (str): The block of text containing the header.
            block_name (str): The name of the block to extract the count from.

        Returns:
            int: The count extracted from the block header.

        Raises:
            BlockNotFoundError: If the count cannot be found in the block header.
        """
        pattern = re.compile(rf'^\s*{re.escape(block_name)}\s*\(\s*(\d+)', re.MULTILINE)
        match = pattern.search(block)
        if not match:
            raise BlockNotFoundError(f"Count not found in block header for '{block_name}'")
        return int(match.group(1))

    def _find_block_end(self, text: str, start_idx: int) -> int:
        """
        Finds the matching closing parenthesis for a block starting at start_idx.

        Parameters:
            text (str): The full text to search within.
            start_idx (int): The index of the opening parenthesis '('.

        Returns:
            int: The index one past the matching closing parenthesis ')'.

        Raises:
            ParenthesisMismatchError: If parentheses are unmatched.
            ShapeParserError: If the character at start_idx is not '('.
        """
        if start_idx >= len(text) or text[start_idx] != '(':
            found_char = text[start_idx] if start_idx < len(text) else 'EOF'
            raise ShapeParserError(f"Expected '(' at index {start_idx}, found '{found_char}' instead.")

        depth = 1
        idx = start_idx + 1
        while idx < len(text) and depth > 0:
            if text[idx] == '(':
                depth += 1
            elif text[idx] == ')':
                depth -= 1
            idx += 1

        if depth != 0:
            snippet = text[start_idx:start_idx+30].replace('\n', '\\n')
            raise ParenthesisMismatchError(
                f"Unmatched parenthesis starting at index {start_idx}. Context: '{snippet}...'"
            )

        return idx

    def _extract_block(self, text: str, block_name: str, verify_block: bool = True) -> Optional[str]:
        """
        Extracts a block by name from the text, including its full content.

        Parameters:
            text (str): The text to search within.
            block_name (str): The name of the block to extract.
            verify_block (bool): If True, raises an error when the block is not found; otherwise returns None.

        Returns:
            Optional[str]: The extracted block text if found, otherwise None.

        Raises:
            BlockNotFoundError: If verify_block is True and block is not found or malformed.
            ShapeParserError: If an opening parenthesis is missing.
        """
        pattern = re.compile(rf'^\s*{re.escape(block_name)}\s*\(\s*\d*', re.MULTILINE)
        match = pattern.search(text)

        if not match:
            if verify_block:
                raise BlockNotFoundError(f"Block '{block_name}' not found or malformed")
            return None

        start_idx = match.start()
        open_idx = text.find("(", start_idx)

        if open_idx == -1:
            raise ShapeParserError(f"No opening '(' found for block '{block_name}' starting at index {start_idx}")

        end_idx = self._find_block_end(text, open_idx)
        return text[start_idx:end_idx]

    def _extract_items_in_block(self, text: str, block_name: str, item_type: str, verify_block: bool = True, verify_count: bool = True, escape_regex: bool = False) -> Optional[_Items]:
        """
        Extracts all items matching item_type inside a given block.

        Parameters:
            text (str): The text to search.
            block_name (str): The name of the block for count verification.
            item_type (str): The type name of the items to extract.
            verify_block (bool): If True, raises an error when the block is not found; otherwise returns None.
            verify_count (bool): Whether to verify the number of extracted items matches the block's declared count.
            escape_regex (bool): Whether to escape the item_type used for matching items with regex in the block.

        Returns:
            Optional[_Items]: A tuple containing the list of extracted items and the expected count.

        Raises:
            BlockNotFoundError: If block header count is missing (only if verify_block = True).
            CountMismatchError: If extracted item count doesn't match expected (only if verify_count = True).
        """
        block = self._extract_block(text, block_name, verify_block=verify_block)

        items = []

        if escape_regex:
            pattern = re.compile(rf'^\s*{re.escape(item_type)}\s*\(', re.MULTILINE)
        else:
            pattern = re.compile(rf'^\s*{item_type}\s*\(', re.MULTILINE)

        for match in pattern.finditer(block):
            start_idx = match.end() - 1
            end_idx = self._find_block_end(block, start_idx)
            items.append(block[match.start():end_idx].strip())

        count = self._extract_count_from_header(block, block_name)

        if verify_count:
            self._verify_count(count, len(items), item_type, block_name)

        return _Items(items, count)

    def _extract_values_in_block(self, text: str, block_name: str, verify_block: bool = True, verify_count: bool = True) -> Optional[_Items]:
        """
        Extracts space-separated values inside the parentheses of a block.

        Parameters:
            text (str): The text to extract values from.
            block_name (str): The block's name for count verification.
            verify_block (bool): If True, raises an error when the block is not found; otherwise returns None.
            verify_count (bool): Whether to verify count matches the number of values extracted.

        Returns:
            Optional[_Items]: List of values extracted and expected count.

        Raises:
            BlockNotFoundError: If block header count is missing (only if verify_block = True).
            CountMismatchError: If extracted item count doesn't match expected (only if verify_count = True).
            ShapeParserError: If the first token inside the block is not an integer count.
        """
        pattern = re.compile(rf'^\s*{re.escape(block_name)}\s*\((.*?)\)', re.DOTALL | re.MULTILINE)
        match = pattern.search(text)
        if not match:
            if verify_block:
                raise BlockNotFoundError(f"Block '{block_name}' not found or malformed")
            return None

        content = match.group(1).strip()
        if not content:
            return _Items([], 0)

        tokens = content.split()
        if not tokens:
            return _Items([], 0)

        try:
            count = int(tokens[0])
        except ValueError:
            raise ShapeParserError(f"Expected count as first value inside '{block_name}' block")

        values = tokens[1:]

        if verify_count:
            self._verify_count(count, len(values), "values", block_name)

        return _Items(values, count)

    def _extract_named_items_in_block(self, text: str, block_name: str, item_type: str, verify_block: bool = True, verify_count: bool = True) -> Optional[_Items]:
        """
        Extracts items with a name after the item_type keyword inside a block.

        Parameters:
            text (str): The text to extract from.
            block_name (str): The name of the block for count verification.
            item_type (str): The type keyword that precedes the named items (e.g. "param").
            verify_block (bool): If True, raises an error when the block is not found; otherwise returns None.
            verify_count (bool): Whether to verify count consistency.

        Returns:
            Optional[_Items]: List of extracted named items and expected count.

        Raises:
            BlockNotFoundError: If block header count is missing (only if verify_block = True).
            CountMismatchError: If extracted item count doesn't match expected (only if verify_count = True).
        """
        block = self._extract_block(text, block_name, verify_block=verify_block)

        pattern = re.compile(rf'^\s*{re.escape(item_type)}\s+\S+\s*\(', re.MULTILINE)

        items = []
        for match in pattern.finditer(block):
            start_idx = match.end() - 1
            end_idx = self._find_block_end(block, start_idx)
            items.append(block[match.start():end_idx].strip())

        count = self._extract_count_from_header(block, block_name)

        if verify_count:
            self._verify_count(count, len(items), item_type, block_name)

        return _Items(items, count)

    def _parse_block(self, text: str, block_name: str, parser: "_Parser[T]", verify_block: bool = True) -> Optional[T]:
        """
        Parses an entire block and returns its parsed representation of type T.

        Parameters:
            text (str): The full text to search the block in.
            block_name (str): The name of the block to parse.
            parser (_Parser[T]): The parser instance to use for parsing.
            verify_block (bool): If True, raises an error when the block is not found; otherwise returns None.

        Returns:
            Optional[T]: The parsed block object or None if not found and verify_block is False.

        Raises:
            BlockNotFoundError: If block header count is missing (only if verify_block = True).
        """
        block_str = self._extract_block(text, block_name, verify_block)
        if block_str is None:
            return None
        return parser.parse(block_str)

    def _parse_items_in_block(self, block: str, block_name: str, item_type: str, parser: "_Parser[T]", verify_block: bool = True, verify_count: bool = True, escape_regex: bool = False) -> Optional[_ParsedItems[T]]:
        """
        Parses all items matching item_type inside a block, returning a list of parsed items and expected count.

        Parameters:
            block (str): The block of text containing the items.
            block_name (str): The block name used for count verification.
            item_type (str): The item type name to parse.
            parser (_Parser[T]): The parser instance to use for parsing.
            verify_block (bool): If True, raises an error when the block is not found; otherwise returns None.
            verify_count (bool): Whether to verify the number of extracted items matches the count.
            escape_regex (bool): Whether to escape the item_type used for matching items with regex in the block.

        Returns:
            Optional[_ParsedItems[T]]: Parsed items and expected count.

        Raises:
            BlockNotFoundError: If block header count is missing (only if verify_block = True).
            CountMismatchError: If extracted item count doesn't match expected (only if verify_count = True).
        """
        extracted_items = self._extract_items_in_block(block, block_name, item_type, verify_block, verify_count, escape_regex)
        parsed_items = [parser.parse(item) for item in extracted_items.items]
        return _ParsedItems(parsed_items, extracted_items.expected_count)

    def _parse_values_in_block(self, block: str, block_name: str, parser: "_Parser[T]", verify_block: bool = True, verify_count: bool = True) -> Optional[_ParsedItems[T]]:
        """
        Parses space-separated values inside a block, returning parsed values and expected count.

        Parameters:
            block (str): The block text.
            block_name (str): The block name for verification.
            parser (_Parser[T]): The parser instance to use for parsing.
            verify_block (bool): If True, raises an error when the block is not found; otherwise returns None.
            verify_count (bool): Whether to verify count consistency.

        Returns:
            Optional[_ParsedItems[T]]: Parsed values and expected count.

        Raises:
            BlockNotFoundError: If block header count is missing (only if verify_block = True).
            CountMismatchError: If extracted item count doesn't match expected (only if verify_count = True).
        """
        extracted_values = self._extract_values_in_block(block, block_name, verify_block, verify_count)
        parsed_values = [parser.parse(value) for value in extracted_values.items]
        return _ParsedItems(parsed_values, extracted_values.expected_count)

    def _parse_named_items_in_block(self, block: str, block_name: str, item_type: str, parser: "_Parser[T]", verify_block: bool = True, verify_count: bool = True) -> Optional[_ParsedItems[T]]:
        """
        Parses named items inside a block, returning parsed items and expected count.

        Parameters:
            block (str): The block text.
            block_name (str): The block name for verification.
            item_type (str): The item type keyword preceding the named item.
            parser (_Parser[T]): The parser instance to use for parsing.
            verify_block (bool): If True, raises an error when the block is not found; otherwise returns None.
            verify_count (bool): Whether to verify count consistency.

        Returns:
            Optional[_ParsedItems[T]]: Parsed named items and expected count.

        Raises:
            BlockNotFoundError: If block header count is missing (only if verify_block = True).
            CountMismatchError: If extracted item count doesn't match expected (only if verify_count = True).
        """
        extracted_items = self._extract_named_items_in_block(block, block_name, item_type, verify_block, verify_count)
        parsed_items = [parser.parse(item) for item in extracted_items.items]
        return _ParsedItems(parsed_items, extracted_items.expected_count)


class _IntParser(_Parser[int]):
    PATTERN = re.compile(r'-?\d+')

    def parse(self, text: str) -> int:
        match = self.PATTERN.fullmatch(text.strip())
        if not match:
            raise ValueError(f"Invalid int value: '{text}'")
        
        return int(text.strip())


class _FloatParser(_Parser[float]):
    PATTERN = re.compile(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?')

    def parse(self, text: str) -> float:
        match = self.PATTERN.fullmatch(text.strip())
        if not match:
            raise ValueError(f"Invalid float value: '{text}'")
        
        return float(text.strip())


class _StrParser(_Parser[str]):
    PATTERN = re.compile(r'\w+')

    def parse(self, text: str) -> str:
        match = self.PATTERN.fullmatch(text.strip())
        if not match:
            raise ValueError(f"Invalid string value: '{text}'")
        
        return text.strip()


class _HexParser(_Parser[str]):
    PATTERN = re.compile(r'[0-9a-fA-F]{8}')

    def parse(self, text: str) -> str:
        match = self.PATTERN.fullmatch(text.strip())
        if not match:
            raise ValueError(f"Invalid hex value: '{text}'")
        
        return text.strip().lower()


class _ShapeHeaderParser(_Parser[shape.ShapeHeader]):
    PATTERN = re.compile(r'shape_header\s*\(\s*([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s*\)', re.IGNORECASE)

    def __init__(self):
        self._hex_parser = _HexParser()

    def parse(self, text: str) -> shape.ShapeHeader:
        match = self.PATTERN.search(text)
        if not match:
            raise BlockFormatError(f"Invalid shape_header format: '{text}'")

        flags1 = self._hex_parser.parse(match.group(1))
        flags2 = self._hex_parser.parse(match.group(2))
        return shape.ShapeHeader(flags1, flags2)


class _VectorParser(_Parser[shape.Vector]):
    PATTERN = re.compile(r'vector\s*\(\s*([-+eE\d\.]+)\s+([-+eE\d\.]+)\s+([-+eE\d\.]+)\s*\)')

    def __init__(self):
        self._float_parser = _FloatParser()

    def parse(self, text: str) -> shape.Vector:
        match = self.PATTERN.match(text.strip())
        if not match:
            raise BlockFormatError(f"Invalid vector format: '{text}'")

        x = self._float_parser.parse(match.group(1))
        y = self._float_parser.parse(match.group(2))
        z = self._float_parser.parse(match.group(3))
        return shape.Vector(x, y, z)


class _VolumeSphereParser(_Parser[shape.VolumeSphere]):
    PATTERN = re.compile(r"vol_sphere\s*\(\s*(vector\s*\([^()]*\))\s+(-?\d+(?:\.\d+)?)\s*\)", re.IGNORECASE)

    def __init__(self):
        self._vector_parser = _VectorParser()
        self._float_parser = _FloatParser()

    def parse(self, text: str) -> shape.VolumeSphere:
        match = self.PATTERN.search(text)
        if not match:
            raise BlockFormatError(f"Invalid vol_sphere format: '{text}'")

        vector_text = match.group(1)
        radius = self._float_parser.parse(match.group(2))
        vector = self._vector_parser.parse(vector_text)
        return shape.VolumeSphere(vector, radius)


class _NamedShaderParser(_Parser[str]):
    PATTERN = re.compile(r'named_shader\s*\(\s*(.+?)\s*\)', re.IGNORECASE)

    def parse(self, text: str) -> str:
        match = self.PATTERN.search(text)
        if not match:
            raise BlockFormatError(f"Invalid named_shader format: '{text}'")

        value = match.group(1).strip()
        if not value:
            raise BlockFormatError(f"named_shader cannot be empty: '{text}'")

        return value


class _NamedFilterModeParser(_Parser[str]):
    PATTERN = re.compile(r'named_filter_mode\s*\(\s*(.+?)\s*\)', re.IGNORECASE)

    def parse(self, text: str) -> str:
        match = self.PATTERN.search(text)
        if not match:
            raise BlockFormatError(f"Invalid named_filter_mode format: '{text}'")

        value = match.group(1).strip()
        if not value:
            raise BlockFormatError(f"named_filter_mode cannot be empty: '{text}'")

        return value


class _PointParser(_Parser[shape.Point]):
    PATTERN = re.compile(r'point\s*\(\s*([-+eE\d\.]+)\s+([-+eE\d\.]+)\s+([-+eE\d\.]+)\s*\)')

    def __init__(self):
        self._float_parser = _FloatParser()

    def parse(self, text: str) -> shape.Point:
        match = self.PATTERN.match(text.strip())
        if not match:
            raise BlockFormatError(f"Invalid point format: '{text}'")

        x = self._float_parser.parse(match.group(1))
        y = self._float_parser.parse(match.group(2))
        z = self._float_parser.parse(match.group(3))
        return shape.Point(x, y, z)


class _UVPointParser(_Parser[shape.UVPoint]):
    PATTERN = re.compile(r'uv_point\s*\(\s*([-+eE\d\.]+)\s+([-+eE\d\.]+)\s*\)')

    def __init__(self):
        self._float_parser = _FloatParser()

    def parse(self, text: str) -> shape.UVPoint:
        match = self.PATTERN.match(text.strip())
        if not match:
            raise BlockFormatError(f"Invalid uv_point format: '{text}'")

        u = self._float_parser.parse(match.group(1))
        v = self._float_parser.parse(match.group(2))
        return shape.UVPoint(u, v)


class _ColourParser(_Parser[shape.Colour]):
    PATTERN = re.compile(r'colour\s*\(\s*([-+eE\d\.]+)\s+([-+eE\d\.]+)\s+([-+eE\d\.]+)\s+([-+eE\d\.]+)\s*\)')

    def __init__(self):
        self._float_parser = _FloatParser()

    def parse(self, text: str) -> shape.Colour:
        match = self.PATTERN.match(text.strip())
        if not match:
            raise BlockFormatError(f"Invalid colour format: '{text}'")

        a = self._float_parser.parse(match.group(1))
        r = self._float_parser.parse(match.group(2))
        g = self._float_parser.parse(match.group(3))
        b = self._float_parser.parse(match.group(4))
        return shape.Colour(a, r, g, b)


class _MatrixParser(_Parser[shape.Matrix]):
    PATTERN = re.compile(r'matrix\s+(\S+)\s*\(\s*([-+eE\d\.]+(?:\s+[-+eE\d\.]+){11})\s*\)')

    def __init__(self):
        self._float_parser = _FloatParser()
        self._str_parser = _StrParser()

    def parse(self, text: str) -> shape.Matrix:
        match = self.PATTERN.match(text.strip())
        if not match:
            raise BlockFormatError(f"Invalid matrix format: '{text}'")

        name = self._str_parser.parse(match.group(1))
        values = [self._float_parser.parse(v) for v in match.group(2).split()]
        if len(values) != 12:
            raise BlockFormatError(f"Expected 12 values in matrix, got {len(values)}")

        return shape.Matrix(name, *values)


class _ImageParser(_Parser[str]):
    PATTERN = re.compile(r'image\s*\(\s*(.+?)\s*\)', re.IGNORECASE)

    def parse(self, text: str) -> str:
        match = self.PATTERN.search(text)
        if not match:
            raise BlockFormatError(f"Invalid image format: '{text}'")

        value = match.group(1).strip()
        if not value:
            raise BlockFormatError(f"image cannot be empty: '{text}'")

        return value


class _TextureParser(_Parser[shape.Texture]):
    PATTERN = re.compile(r'texture\s*\(\s*(-?\d+)\s+(-?\d+)\s+(-?\d+(?:\.\d+)?)\s+([a-fA-F0-9]+)\s*\)', re.IGNORECASE)

    def __init__(self):
        self._int_parser = _IntParser()
        self._float_parser = _FloatParser()
        self._hex_parser = _HexParser()

    def parse(self, text: str) -> shape.Texture:
        match = self.PATTERN.search(text)
        if not match:
            raise BlockFormatError(f"Invalid texture format: '{text}'")

        image_index = self._int_parser.parse(match.group(1))
        filter_mode = self._int_parser.parse(match.group(2))
        mipmap_lod_bias = self._float_parser.parse(match.group(3))
        border_colour = self._hex_parser.parse(match.group(4))

        return shape.Texture(
            image_index,
            filter_mode,
            mipmap_lod_bias,
            border_colour
        )


class _LightMaterialParser(_Parser[shape.LightMaterial]):
    PATTERN = re.compile(
        r'light_material\s*\(\s*([a-fA-F0-9]+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+(?:\.\d+)?)\s*\)',
        re.IGNORECASE
    )

    def __init__(self):
        self._hex_parser = _HexParser()
        self._int_parser = _IntParser()
        self._float_parser = _FloatParser()

    def parse(self, text: str) -> shape.LightMaterial:
        match = self.PATTERN.search(text)
        if not match:
            raise BlockFormatError(f"Invalid light_material format: '{text}'")

        flags = self._hex_parser.parse(match.group(1))
        diff_colour_index = self._int_parser.parse(match.group(2))
        amb_colour_index = self._int_parser.parse(match.group(3))
        spec_colour_index = self._int_parser.parse(match.group(4))
        emissive_colour_index = self._int_parser.parse(match.group(5))
        spec_power = self._float_parser.parse(match.group(6))

        return shape.LightMaterial(
            flags,
            diff_colour_index,
            amb_colour_index,
            spec_colour_index,
            emissive_colour_index,
            spec_power
        )


class _UVOpParser(_Parser[shape.UVOp]):
    PATTERN = re.compile(
        r'uv_op_([a-z]+)\s*\(\s*(-?\d+)(?:\s+(-?\d+))?(?:\s+(-?\d+))?(?:\s+(-?\d+))?\s*\)',
        re.IGNORECASE
    )

    def __init__(self):
        self._int_parser = _IntParser()

    def parse(self, text: str) -> shape.UVOp:
        match = self.PATTERN.fullmatch(text.strip())
        if not match:
            raise BlockFormatError(f"Invalid uv_op format: '{text}'")

        op_type = match.group(1).lower()
        values = [g for g in match.groups()[1:] if g is not None]
        int_values = [self._int_parser.parse(value) for value in values]

        if op_type == "copy":
            if len(int_values) != 2:
                raise BlockFormatError(f"uv_op_copy expects 2 values, got {len(int_values)}: {text}")
            return shape.UVOpCopy(*int_values)

        elif op_type == "reflectmapfull":
            if len(int_values) != 1:
                raise BlockFormatError(f"uv_op_reflectmapfull expects 1 value, got {len(int_values)}: {text}")
            return shape.UVOpReflectMapFull(*int_values)

        elif op_type == "reflectmap":
            if len(int_values) != 1:
                raise BlockFormatError(f"uv_op_reflectmap expects 1 value, got {len(int_values)}: {text}")
            return shape.UVOpReflectMap(*int_values)

        elif op_type == "uniformscale":
            if len(int_values) != 4:
                raise BlockFormatError(f"uv_op_uniformscale expects 4 values, got {len(int_values)}: {text}")
            return shape.UVOpUniformScale(*int_values)

        elif op_type == "nonuniformscale":
            if len(int_values) != 4:
                raise BlockFormatError(f"uv_op_nonuniformscale expects 4 values, got {len(int_values)}: {text}")
            return shape.UVOpNonUniformScale(*int_values)

        else:
            raise BlockFormatError(f"Unknown uv_op type: 'uv_op_{op_type}'")


class _LightModelCfgParser(_Parser[shape.LightModelCfg]):
    PATTERN = re.compile(r'light_model_cfg\s*\(\s*([a-fA-F0-9]+)', re.IGNORECASE)

    def __init__(self):
        self._hex_parser = _HexParser()
        self._uv_op_parser = _UVOpParser()

    def parse(self, text: str) -> shape.LightModelCfg:
        match = self.PATTERN.search(text)
        if not match:
            raise BlockFormatError(f"Invalid light_model_cfg format: '{text}'")

        flags = self._hex_parser.parse(match.group(1))
        uv_ops = self._parse_items_in_block(text, "uv_ops", "uv_op_[a-z]+", self._uv_op_parser, escape_regex=False).items

        return shape.LightModelCfg(flags, uv_ops)


class _VtxStateParser(_Parser[shape.VtxState]):
    PATTERN = re.compile(
        r"vtx_state\s*\(\s*([a-fA-F0-9]+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+([a-fA-F0-9]+)(?:\s+(-?\d+))?\s*\)",
        re.IGNORECASE
    )

    def __init__(self):
        self._hex_parser = _HexParser()
        self._int_parser = _IntParser()

    def parse(self, text: str) -> shape.VtxState:
        match = self.PATTERN.search(text)
        if not match:
            raise BlockFormatError(f"Invalid vtx_state format: '{text}'")

        flags = self._hex_parser.parse(match.group(1))
        matrix_index = self._int_parser.parse(match.group(2))
        light_material_index = self._int_parser.parse(match.group(3))
        light_model_cfg_index = self._int_parser.parse(match.group(4))
        light_flags = self._hex_parser.parse(match.group(5))
        matrix2_index = self._int_parser.parse(match.group(6)) if match.group(6) is not None else None

        return shape.VtxState(
            flags,
            matrix_index,
            light_material_index,
            light_model_cfg_index,
            light_flags,
            matrix2_index
        )


class _PrimStateParser(_Parser[shape.PrimState]):
    PATTERN = re.compile(
        r"""prim_state\s+(\w+)\s*\(\s*([a-fA-F0-9]+)\s+(\d+)\s+
            tex_idxs\s*\(\s*(?:-?\d+\s*)*\)\s+
            (-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s*
        \)""",
        re.IGNORECASE | re.VERBOSE
    )

    def __init__(self):
        self._hex_parser = _HexParser()
        self._int_parser = _IntParser()
        self._str_parser = _StrParser()
        self._float_parser = _FloatParser()

    def parse(self, text: str) -> shape.PrimState:
        match = self.PATTERN.search(text)
        if not match:
            raise BlockFormatError(f"Invalid prim_state format: '{text}'")

        name = self._str_parser.parse(match.group(1))
        flags = self._hex_parser.parse(match.group(2))
        shader_index = self._int_parser.parse(match.group(3))
        texture_indices = self._parse_values_in_block(text, "tex_idxs", self._int_parser).items
        z_bias = self._float_parser.parse(match.group(4))
        vtx_state_index = self._int_parser.parse(match.group(5))
        alpha_test_mode = self._int_parser.parse(match.group(6))
        light_cfg_index = self._int_parser.parse(match.group(7))
        z_buffer_mode = self._int_parser.parse(match.group(8))

        return shape.PrimState(
            name,
            flags,
            shader_index,
            texture_indices,
            z_bias,
            vtx_state_index,
            alpha_test_mode,
            light_cfg_index,
            z_buffer_mode
        )


class _VertexParser(_Parser[shape.Vertex]):
    PATTERN = re.compile(
        r'vertex\s*\(\s*([0-9A-Fa-f]{8})\s+(\d+)\s+(\d+)\s+([0-9A-Fa-f]{8})\s+([0-9A-Fa-f]{8})',
        re.IGNORECASE
    )

    def __init__(self):
        self._hex_parser = _HexParser()
        self._int_parser = _IntParser()

    def parse(self, text: str) -> shape.Vertex:
        match = self.PATTERN.search(text)
        if not match:
            raise BlockFormatError(f"Invalid vertex format: '{text}'")

        flags = self._hex_parser.parse(match.group(1))
        point_index = self._int_parser.parse(match.group(2))
        normal_index = self._int_parser.parse(match.group(3))
        colour1 = self._hex_parser.parse(match.group(4))
        colour2 = self._hex_parser.parse(match.group(5))
        vertex_uvs = self._parse_values_in_block(text, "vertex_uvs", self._int_parser).items

        return shape.Vertex(
            flags,
            point_index,
            normal_index,
            colour1,
            colour2,
            vertex_uvs
        )


class _VertexSetParser(_Parser[shape.VertexSet]):
    PATTERN = re.compile(
        r'vertex_set\s*\(\s*(\d+)\s+(\d+)\s+(\d+)\s*\)',
        re.IGNORECASE
    )

    def __init__(self):
        self._int_parser = _IntParser()

    def parse(self, text: str) -> shape.VertexSet:
        match = self.PATTERN.search(text)
        if not match:
            raise BlockFormatError(f"Invalid vertex_set format: '{text}'")

        vtx_state = self._int_parser.parse(match.group(1))
        vtx_start_index = self._int_parser.parse(match.group(2))
        vtx_count = self._int_parser.parse(match.group(3))

        return shape.VertexSet(vtx_state, vtx_start_index, vtx_count)


class _IndexedTrilistParser(_Parser[shape.IndexedTrilist]):
    def __init__(self):
        super().__init__()
        self._int_parser = _IntParser()
        self._hex_parser = _HexParser()

    def parse(self, text: str) -> shape.IndexedTrilist:
        raw_vertex_idxs = self._parse_values_in_block(text, "vertex_idxs", self._int_parser)
        raw_normal_idxs = self._parse_values_in_block(text, "normal_idxs", self._int_parser, verify_count=False)
        flags = self._parse_values_in_block(text, "flags", self._hex_parser).items

        if raw_normal_idxs.expected_count != len(raw_normal_idxs.items) // 2:
            raise CountMismatchError(
                "Count mismatch for 'normal_idxs' in 'IndexedTrilist': "
                f"Expected {raw_normal_idxs.expected_count * 2} values "
                f"(for {raw_normal_idxs.expected_count} index pairs) but found {len(raw_normal_idxs.items)}"
            )

        vertex_idxs = [
            shape.VertexIdx(raw_vertex_idxs.items[i], raw_vertex_idxs.items[i + 1], raw_vertex_idxs.items[i + 2])
            for i in range(0, len(raw_vertex_idxs.items), 3)
        ]
        normal_idxs = [
            shape.NormalIdx(raw_normal_idxs.items[i], raw_normal_idxs.items[i + 1])
            for i in range(0, len(raw_normal_idxs.items), 2)
        ]

        return shape.IndexedTrilist(
            vertex_idxs=vertex_idxs,
            normal_idxs=normal_idxs,
            flags=flags
        )


class _PrimitivesParser(_Parser[List[shape.Primitive]]):
    def __init__(self):
        super().__init__()
        self._int_parser = _IntParser()
        self._trilist_parser = _IndexedTrilistParser()

    def parse(self, text: str) -> List[shape.Primitive]:
        results = []
        current_index = None
        current_group = []

        primitives_block = self._extract_items_in_block(
            text,
            "primitives",
            item_type="(?:prim_state_idx|indexed_trilist)",
            escape_regex=False
        )

        for item in primitives_block.items:
            item = item.strip()
            if item.startswith("prim_state_idx"):
                if current_index is not None:
                    for trilist in current_group:
                        results.append(shape.Primitive(current_index, trilist))
                    current_group = []

                match = re.match(r'^\s*prim_state_idx\s*\(\s*(-?\d+)\s*\)', item)
                if not match:
                    raise BlockFormatError(f"Invalid prim_state_idx format: {item!r}")
                
                current_index = self._int_parser.parse(match.group(1))

            elif item.startswith("indexed_trilist"):
                trilist = self._trilist_parser.parse(item)
                current_group.append(trilist)

        if current_index is not None:
            for trilist in current_group:
                results.append(shape.Primitive(current_index, trilist))

        return results


class _CullablePrimsParser(_Parser[shape.CullablePrims]):
    PATTERN = re.compile(
        r'cullable_prims\s*\(\s*(\d+)\s+(\d+)\s+(\d+)\s*\)',
        re.IGNORECASE
    )

    def __init__(self):
        self._int_parser = _IntParser()

    def parse(self, text: str) -> shape.CullablePrims:
        match = self.PATTERN.search(text)
        if not match:
            raise BlockFormatError(f"Invalid cullable_prims format: '{text}'")

        num_prims = self._int_parser.parse(match.group(1))
        num_flat_sections = self._int_parser.parse(match.group(2))
        num_prim_indices = self._int_parser.parse(match.group(3))

        return shape.CullablePrims(num_prims, num_flat_sections, num_prim_indices)


class _GeometryNodeParser(_Parser[shape.GeometryNode]):
    PATTERN = re.compile(
        r'geometry_node\s*\(\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',
        re.IGNORECASE
    )

    def __init__(self):
        self._int_parser = _IntParser()
        self._cullable_prims_parser = _CullablePrimsParser()

    def parse(self, text: str) -> shape.CullablePrims:
        match = self.PATTERN.search(text)
        if not match:
            raise BlockFormatError(f"Invalid geometry_node format: '{text}'")

        tx_light_cmds = self._int_parser.parse(match.group(1))
        node_x_tx_light_cmds = self._int_parser.parse(match.group(2))
        trilists = self._int_parser.parse(match.group(3))
        line_lists = self._int_parser.parse(match.group(4))
        pt_lists = self._int_parser.parse(match.group(5))
        cullable_prims = self._parse_block(text, "cullable_prims", self._cullable_prims_parser)

        return shape.GeometryNode(
            tx_light_cmds=tx_light_cmds,
            node_x_tx_light_cmds=node_x_tx_light_cmds,
            trilists=trilists,
            line_lists=line_lists,
            pt_lists=pt_lists,
            cullable_prims=cullable_prims
        )


class _GeometryInfoParser(_Parser[shape.GeometryInfo]):
    PATTERN = re.compile(
        r'geometry_info\s*\(\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',
        re.IGNORECASE
    )

    def __init__(self):
        self._int_parser = _IntParser()
        self._geometry_node_parser = _GeometryNodeParser()

    def parse(self, text: str) -> shape.GeometryInfo:
        match = self.PATTERN.search(text)
        if not match:
            raise BlockFormatError(f"Invalid geometry_info format: '{text}'")

        face_normals = self._int_parser.parse(match.group(1))
        tx_light_cmds = self._int_parser.parse(match.group(2))
        node_x_tx_light_cmds = self._int_parser.parse(match.group(3))
        trilist_indices = self._int_parser.parse(match.group(4))
        line_list_indices = self._int_parser.parse(match.group(5))
        node_x_trilist_indices = self._int_parser.parse(match.group(6))
        trilists = self._int_parser.parse(match.group(7))
        line_lists = self._int_parser.parse(match.group(8))
        pt_lists = self._int_parser.parse(match.group(9))
        node_x_trilists = self._int_parser.parse(match.group(10))
        geometry_nodes = self._parse_items_in_block(text, "geometry_nodes", "geometry_node", self._geometry_node_parser).items
        geometry_node_map = self._parse_values_in_block(text, "geometry_node_map", self._int_parser).items

        return shape.GeometryInfo(
            face_normals=face_normals,
            tx_light_cmds=tx_light_cmds,
            node_x_tx_light_cmds=node_x_tx_light_cmds,
            trilist_indices=trilist_indices,
            line_list_indices=line_list_indices,
            node_x_trilist_indices=node_x_trilist_indices,
            trilists=trilists,
            line_lists=line_lists,
            pt_lists=pt_lists,
            node_x_trilists=node_x_trilists,
            geometry_nodes=geometry_nodes,
            geometry_node_map=geometry_node_map
        )


class _SubObjectHeaderParser(_Parser[shape.SubObjectHeader]):
    INITIAL_PATTERN = re.compile(
        r"sub_object_header\s*\(\s*([0-9A-Fa-f]{8})\s+(-?\d+)\s+(-?\d+)\s+([0-9A-Fa-f]{8})\s+([0-9A-Fa-f]{8})",
        re.IGNORECASE
    )
    TRAILING_PATTERN = re.compile(
        r'(\d+)\s*\)\s*$',
        re.DOTALL
    )

    def __init__(self):
        self._int_parser = _IntParser()
        self._hex_parser = _HexParser()
        self._geometry_info_parser = _GeometryInfoParser()

    def parse(self, text: str) -> shape.SubObjectHeader:
        initial_match = self.INITIAL_PATTERN.search(text)
        if not initial_match:
            raise BlockFormatError(f"Invalid sub_object_header format: '{text}'")
        
        trailing_match = self.TRAILING_PATTERN.search(text)
        if not trailing_match:
            raise BlockFormatError(f"Invalid sub_object_header format: '{text}'")
        
        flags = self._hex_parser.parse(initial_match.group(1))
        sort_vector_index = self._int_parser.parse(initial_match.group(2))
        volume_index = self._int_parser.parse(initial_match.group(3))
        source_vtx_fmt_flags = self._hex_parser.parse(initial_match.group(4))
        destination_vtx_fmt_flags = self._hex_parser.parse(initial_match.group(5))
        geometry_info = self._parse_block(text, "geometry_info", self._geometry_info_parser)
        subobject_shaders = self._parse_values_in_block(text, "subobject_shaders", self._int_parser).items
        subobject_light_cfgs = self._parse_values_in_block(text, "subobject_light_cfgs", self._int_parser).items
        subobject_id = self._int_parser.parse(trailing_match.group(1))

        return shape.SubObjectHeader(
            flags=flags,
            sort_vector_index=sort_vector_index,
            volume_index=volume_index,
            source_vtx_fmt_flags=source_vtx_fmt_flags,
            destination_vtx_fmt_flags=destination_vtx_fmt_flags,
            geometry_info=geometry_info,
            subobject_shaders=subobject_shaders,
            subobject_light_cfgs=subobject_light_cfgs,
            subobject_id=subobject_id
        )


class _SubObjectParser(_Parser[shape.SubObject]):
    def __init__(self):
        self._sub_object_header_parser = _SubObjectHeaderParser()
        self._vertex_parser = _VertexParser()
        self._vertex_set_parser = _VertexSetParser()
        self._primitives_parser = _PrimitivesParser()

    def parse(self, text: str) -> shape.SubObject:
        sub_object_header = self._parse_block(text, "sub_object_header", self._sub_object_header_parser)
        vertices = self._parse_items_in_block(text, "vertices", "vertex", self._vertex_parser).items
        vertex_sets = self._parse_items_in_block(text, "vertex_sets", "vertex_set", self._vertex_set_parser).items
        primitives = self._parse_block(text, "primitives", self._primitives_parser)

        return shape.SubObject(
            sub_object_header=sub_object_header,
            vertices=vertices,
            vertex_sets=vertex_sets,
            primitives=primitives
        )


class _DistanceLevelSelectionParser(_Parser[int]):
    PATTERN = re.compile(r'dlevel_selection\s*\(\s*(\d+)\s*\)', re.IGNORECASE)

    def __init__(self):
        self._int_parser = _IntParser()

    def parse(self, text: str) -> int:
        match = self.PATTERN.search(text)
        if not match:
            raise BlockFormatError(f"Invalid dlevel_selection format: '{text}'")

        return self._int_parser.parse(match.group(1))


class _DistanceLevelHeaderParser(_Parser[shape.DistanceLevelHeader]):
    def __init__(self):
        self._distance_level_selection_parser = _DistanceLevelSelectionParser()
        self._int_parser = _IntParser()

    def parse(self, text: str) -> shape.DistanceLevelHeader:
        dlevel_selection = self._parse_block(text, "dlevel_selection", self._distance_level_selection_parser)
        hierarchy = self._parse_values_in_block(text, "hierarchy", self._int_parser).items

        return shape.DistanceLevelHeader(dlevel_selection, hierarchy)


class _DistanceLevelParser(_Parser[shape.DistanceLevel]):
    def __init__(self):
        self._distance_level_header_parser = _DistanceLevelHeaderParser()
        self._sub_object_parser = _SubObjectParser()

    def parse(self, text: str) -> shape.DistanceLevel:
        distance_level_header = self._parse_block(text, "distance_level_header", self._distance_level_header_parser)
        sub_objects = self._parse_items_in_block(text, "sub_objects", "sub_object", self._sub_object_parser).items

        return shape.DistanceLevel(
            distance_level_header=distance_level_header,
            sub_objects=sub_objects
        )


class _DistanceLevelsHeaderParser(_Parser[shape.DistanceLevelsHeader]):
    PATTERN = re.compile(r'distance_levels_header\s*\(\s*(\d+)\s*\)', re.IGNORECASE)

    def __init__(self):
        self._int_parser = _IntParser()

    def parse(self, text: str) -> shape.DistanceLevelsHeader:
        match = self.PATTERN.search(text)
        if not match:
            raise BlockFormatError(f"Invalid distance_levels_header format: '{text}'")

        dlevel_bias = self._int_parser.parse(match.group(1))
        return shape.DistanceLevelsHeader(dlevel_bias)


class _LodControlParser(_Parser[shape.LodControl]):
    def __init__(self):
        self._distance_levels_header_parser = _DistanceLevelsHeaderParser()
        self._distance_level_parser = _DistanceLevelParser()

    def parse(self, text: str) -> shape.LodControl:
        distance_levels_header = self._parse_block(text, "distance_levels_header", self._distance_levels_header_parser)
        distance_levels = self._parse_items_in_block(text, "distance_levels", "distance_level", self._distance_level_parser).items

        return shape.LodControl(
            distance_levels_header=distance_levels_header,
            distance_levels=distance_levels
        )


class _AnimationNodeParser(_Parser[shape.AnimationNode]):
    PATTERN = re.compile(r'anim_node\s+(\w+)\s*\(', re.IGNORECASE)

    def __init__(self):
        self._str_parser = _StrParser()

    def parse(self, text: str) -> shape.AnimationNode:
        match = self.PATTERN.search(text)
        if not match:
            raise BlockFormatError(f"Invalid anim_node format: '{text}'")

        name = self._str_parser.parse(match.group(1))
        controllers = []

        return shape.AnimationNode(
            name=name,
            controllers=controllers
        )


class _AnimationParser(_Parser[shape.Animation]):
    PATTERN = re.compile(r'animation\s*\(\s*(\d+)\s+(\d+)', re.IGNORECASE)

    def __init__(self):
        self._int_parser = _IntParser()
        self._anim_node_perser = _AnimationNodeParser()

    def parse(self, text: str) -> shape.Animation:
        match = self.PATTERN.search(text)
        if not match:
            raise BlockFormatError(f"Invalid animation format: '{text}'")

        frame_count = self._int_parser.parse(match.group(1))
        frame_rate = self._int_parser.parse(match.group(2))
        animation_nodes = self._parse_named_items_in_block(text, "anim_nodes", "anim_node", self._anim_node_perser).items

        return shape.Animation(
            frame_count=frame_count,
            frame_rate=frame_rate,
            animation_nodes=animation_nodes
        )


class _ShapeParser(_Parser[shape.Shape]):
    def __init__(self):
        self._shape_header_parser = _ShapeHeaderParser()
        self._volume_sphere_parser = _VolumeSphereParser()
        self._named_shader_parser = _NamedShaderParser()
        self._named_filter_mode_parser = _NamedFilterModeParser()
        self._point_parser = _PointParser()
        self._uv_point_parser = _UVPointParser()
        self._vector_parser = _VectorParser()
        self._colour_parser = _ColourParser()
        self._matrix_parser = _MatrixParser()
        self._image_parser = _ImageParser()
        self._texture_parser = _TextureParser()
        self._light_material_parser = _LightMaterialParser()
        self._light_model_cfg_parser = _LightModelCfgParser()
        self._vtx_state_parser = _VtxStateParser()
        self._prim_state_parser = _PrimStateParser()
        self._lod_control_parser = _LodControlParser()
        self._animation_parser = _AnimationParser()

    def parse(self, text: str) -> shape.Shape:
        shape_header = self._parse_block(text, "shape_header", self._shape_header_parser)
        volumes = self._parse_items_in_block(text, "volumes", "vol_sphere", self._volume_sphere_parser).items
        shader_names = self._parse_items_in_block(text, "shader_names", "named_shader", self._named_shader_parser).items
        texture_filter_names = self._parse_items_in_block(text, "texture_filter_names", "named_filter_mode", self._named_filter_mode_parser).items
        points = self._parse_items_in_block(text, "points", "point", self._point_parser).items
        uv_points = self._parse_items_in_block(text, "uv_points", "uv_point", self._uv_point_parser).items
        normals = self._parse_items_in_block(text, "normals", "vector", self._vector_parser).items
        sort_vectors = self._parse_items_in_block(text, "sort_vectors", "vector", self._vector_parser).items
        colours = self._parse_items_in_block(text, "colours", "colour", self._colour_parser).items
        matrices = self._parse_named_items_in_block(text, "matrices", "matrix", self._matrix_parser).items
        images = self._parse_items_in_block(text, "images", "image", self._image_parser).items
        textures = self._parse_items_in_block(text, "textures", "texture", self._texture_parser).items
        light_materials = self._parse_items_in_block(text, "light_materials", "light_material", self._light_material_parser).items
        light_model_cfgs = self._parse_items_in_block(text, "light_model_cfgs", "light_model_cfg", self._light_model_cfg_parser).items
        vtx_states = self._parse_items_in_block(text, "vtx_states", "vtx_state", self._vtx_state_parser).items
        prim_states = self._parse_named_items_in_block(text, "prim_states", "prim_state", self._prim_state_parser).items
        lod_controls = self._parse_items_in_block(text, "lod_controls", "lod_control", self._lod_control_parser).items
        animations = self._parse_items_in_block(text, "animations", "animation", self._animation_parser, verify_block=False).items

        return shape.Shape(
            shape_header=shape_header,
            volumes=volumes,
            shader_names=shader_names,
            texture_filter_names=texture_filter_names,
            points=points,
            uv_points=uv_points,
            normals=normals,
            sort_vectors=sort_vectors,
            colours=colours,
            matrices=matrices,
            images=images,
            textures=textures,
            light_materials=light_materials,
            light_model_cfgs=light_model_cfgs,
            vtx_states=vtx_states,
            prim_states=prim_states,
            lod_controls=lod_controls,
            animations=animations or []
        )
