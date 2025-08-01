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

import pytest

from typing import Any, List
from abc import ABC

from shapeio.encoder import _Serializer


class DummySerializer(_Serializer[Any]):
    def serialize(self, obj: Any, depth: int = 0) -> str:
        return f"{self.get_indent(depth)}{obj}"


@pytest.fixture
def dummy_serializer():
    return DummySerializer(indent=1, use_tabs=True)


@pytest.fixture
def dummy_serializer_spaces():
    return DummySerializer(indent=2, use_tabs=False)


def test_get_indent_tabs(dummy_serializer):
    assert dummy_serializer.get_indent(0) == ""
    assert dummy_serializer.get_indent(1) == "\t"
    assert dummy_serializer.get_indent(3) == "\t\t\t"


def test_get_indent_spaces(dummy_serializer_spaces):
    assert dummy_serializer_spaces.get_indent(0) == ""
    assert dummy_serializer_spaces.get_indent(1) == "  "
    assert dummy_serializer_spaces.get_indent(2) == "    "


def test_serialize_single_line(dummy_serializer_spaces):
    items = [1, 2, 3]
    result = dummy_serializer_spaces._serialize_items_in_block(
        items=items,
        block_name="values",
        item_serializer=dummy_serializer_spaces,
        depth=1,
        items_per_line=3,
        newline_after_header=True,
        newline_before_closing=True,
    )
    expected = (
        "  values ( 3\n"
        "    1 2 3\n"
        "  )"
    )
    assert result == expected


def test_serialize_multiple_lines(dummy_serializer):
    items = [1, 2, 3, 4]
    result = dummy_serializer._serialize_items_in_block(
        items=items,
        block_name="values",
        item_serializer=dummy_serializer,
        depth=0,
        items_per_line=2,
        newline_after_header=True,
        newline_before_closing=True,
    )
    expected = (
        "values ( 4\n"
        "\t1 2\n"
        "\t3 4\n"
        ")"
    )
    assert result == expected


def test_serialize_no_newline_after_header(dummy_serializer):
    items = [1, 2]
    result = dummy_serializer._serialize_items_in_block(
        items=items,
        block_name="values",
        item_serializer=dummy_serializer,
        depth=1,
        items_per_line=1,
        newline_after_header=False,
        newline_before_closing=True,
    )
    expected = (
        "\tvalues ( 2 1\n"
        "\t\t2\n"
        "\t)"
    )
    assert result == expected


def test_serialize_no_newline_before_closing(dummy_serializer):
    items = [1, 2]
    result = dummy_serializer._serialize_items_in_block(
        items=items,
        block_name="values",
        item_serializer=dummy_serializer,
        depth=1,
        items_per_line=1,
        newline_after_header=True,
        newline_before_closing=False,
    )
    expected = (
        "\tvalues ( 2\n"
        "\t\t1\n"
        "\t\t2 )"
    )
    assert result == expected


def test_serialize_empty_list(dummy_serializer):
    result = dummy_serializer._serialize_items_in_block(
        items=[],
        block_name="values",
        item_serializer=dummy_serializer,
        depth=0,
        newline_after_header=False,
        newline_before_closing=False
    )
    expected = "values ( 0 )"
    assert result == expected


def test_serialize_empty_list_ignore_after_header_before_closing_flags(dummy_serializer):
    result = dummy_serializer._serialize_items_in_block(
        items=[],
        block_name="values",
        item_serializer=dummy_serializer,
        depth=0,
        newline_after_header=True,
        newline_before_closing=True
    )
    expected = "values ( 0 )"
    assert result == expected


def test_serialize_with_depth(dummy_serializer):
    items = [1, 2]
    result = dummy_serializer._serialize_items_in_block(
        items=items,
        block_name="values",
        item_serializer=dummy_serializer,
        depth=2,
        items_per_line=1
    )
    expected = (
        "\t\tvalues ( 2\n"
        "\t\t\t1\n"
        "\t\t\t2\n"
        "\t\t)"
    )
    assert result == expected


def test_serialize_with_count_multiplier(dummy_serializer):
    items = [1, 2]
    result = dummy_serializer._serialize_items_in_block(
        items=items,
        block_name="values",
        item_serializer=dummy_serializer,
        depth=0,
        count_multiplier=5,
        items_per_line=1,
    )
    expected = (
        "values ( 10\n"
        "\t1\n"
        "\t2\n"
        ")"
    )
    assert result == expected


def test_serialize_with_count_multiplier_below_1(dummy_serializer):
    items = [1, 2]
    result = dummy_serializer._serialize_items_in_block(
        items=items,
        block_name="values",
        item_serializer=dummy_serializer,
        depth=0,
        count_multiplier=0.5,
        items_per_line=1,
    )
    expected = (
        "values ( 1\n"
        "\t1\n"
        "\t2\n"
        ")"
    )
    assert result == expected


def test_serialize_items_per_line_none(dummy_serializer):
    items = [1, 2, 3]
    result = dummy_serializer._serialize_items_in_block(
        items=items,
        block_name="values",
        item_serializer=dummy_serializer,
        items_per_line=None,
        newline_after_header=False,
        newline_before_closing=False
    )
    expected = "values ( 3 1 2 3 )"
    assert result == expected


def test_serialize_items_per_line_none_newline_after_header(dummy_serializer):
    items = [1, 2, 3]
    result = dummy_serializer._serialize_items_in_block(
        items=items,
        block_name="values",
        item_serializer=dummy_serializer,
        items_per_line=None,
        newline_after_header=True,
        newline_before_closing=False
    )
    expected = (
        "values ( 3\n"
        "1 2 3 )"
    )
    assert result == expected


def test_serialize_items_per_line_none_newline_before_closing(dummy_serializer):
    items = [1, 2, 3]
    result = dummy_serializer._serialize_items_in_block(
        items=items,
        block_name="values",
        item_serializer=dummy_serializer,
        items_per_line=None,
        newline_after_header=False,
        newline_before_closing=True
    )
    expected = (
        "values ( 3 1 2 3"
        "\n)"
    )
    assert result == expected


def test_serialize_items_per_line_none_newline_after_header_newline_before_closing(dummy_serializer):
    items = [1, 2, 3]
    result = dummy_serializer._serialize_items_in_block(
        items=items,
        block_name="values",
        item_serializer=dummy_serializer,
        items_per_line=None,
        newline_after_header=True,
        newline_before_closing=True
    )
    expected = (
        "values ( 3\n"
        "\t1 2 3\n"
        ")"
    )
    assert result == expected


def test_serialize_single_item(dummy_serializer):
    result = dummy_serializer._serialize_items_in_block(
        items=[1],
        block_name="values",
        item_serializer=dummy_serializer,
        items_per_line=1,
        newline_after_header=True,
        newline_before_closing=True
    )
    expected = (
        "values ( 1\n"
        "\t1\n"
        ")"
    )
    assert result == expected


def test_serialize_large_list(dummy_serializer):
    items = list(range(10))
    result = dummy_serializer._serialize_items_in_block(
        items=items,
        block_name="values",
        item_serializer=dummy_serializer,
        depth=1,
        items_per_line=3,
    )
    expected = (
        "\tvalues ( 10\n"
        "\t\t0 1 2\n"
        "\t\t3 4 5\n"
        "\t\t6 7 8\n"
        "\t\t9\n"
        "\t)"
    )
    assert result == expected

