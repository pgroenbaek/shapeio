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

from shapeio.shape import (
    TCBRot, LinearPos, TCBPos,
    SlerpRot, LinearKey, TCBKey
)
from shapeio.decoder import _ControllerParser, BlockFormatError
from shapeio.encoder import _ControllerSerializer


@pytest.fixture
def parser():
    return _ControllerParser()


@pytest.fixture
def serializer():
    return _ControllerSerializer()


@pytest.mark.parametrize("controller, expected_text", [
    (
        TCBRot([SlerpRot(0, 0, 0, 0.707107, 0.707107), SlerpRot(1, 0, 0, 0, 1)]),
        "tcb_rot ( 2\n"
        "\tslerp_rot ( 0 0 0 0.707107 0.707107 )\n"
        "\tslerp_rot ( 1 0 0 0 1 )\n"
        ")"
    ),
    (
        LinearPos([LinearKey(0, 1.1, 2.0, 3.0), LinearKey(1, 4.0, 5.0, 6.0)]),
        "linear_pos ( 2\n"
        "\tlinear_key ( 0 1.1 2 3 )\n"
        "\tlinear_key ( 1 4 5 6 )\n"
        ")"
    ),
    (
        TCBPos([TCBKey(0, 0, 0, 0, 1, 0, 0, 0, 0, 0)]),
        "tcb_pos ( 1\n"
        "\ttcb_key ( 0 0 0 0 1 0 0 0 0 0 )\n"
        ")"
    ),
])
def test_serialize_controller(serializer, controller, expected_text):
    result = serializer.serialize(controller, depth=0)
    result_lines = [line.rstrip() for line in result.splitlines()]
    expected_lines = [line.rstrip() for line in expected_text.splitlines()]
    assert result_lines == expected_lines


@pytest.mark.parametrize("text, expected_type, keyframes_values", [
    (
        "tcb_rot ( 2\n"
        "    slerp_rot ( 0 0 0 0.707107 0.707107 )\n"
        "    slerp_rot ( 1 0 0 0 1 )\n"
        ")",
        TCBRot,
        [(0, 0, 0, 0.707107, 0.707107), (1, 0, 0, 0, 1)]
    ),
    (
        "linear_pos ( 2\n"
        "    linear_key ( 0 1.0 2.0 3.0 )\n"
        "    linear_key ( 1 4.0 5.0 6.0 )\n"
        ")",
        LinearPos,
        [(0, 1.0, 2.0, 3.0), (1, 4.0, 5.0, 6.0)]
    ),
    (
        "tcb_pos ( 1\n"
        "    tcb_key ( 0 0 0 0 1 0 0 0 0 0 )\n"
        ")",
        TCBPos,
        [(0, 0, 0, 0, 1, 0, 0, 0, 0, 0)]
    ),
])
def test_parse_controller(parser, text, expected_type, keyframes_values):
    controller = parser.parse(text)
    assert isinstance(controller, expected_type)
    for k, expected in zip(controller.keyframes, keyframes_values):
        values = tuple(vars(k).values())
        assert values == expected


@pytest.mark.parametrize("bad_text", [
    "unknown_controller ( 1\n    slerp_rot ( 0 0 0 0.707107 0.707107 )\n)",
    "tcb_rot 2\n    slerp_rot ( 0 0 0 0.707107 0.707107 )",  # missing parentheses
    "linear_pos ( 1\n    linear_key ( 1 2 3 )\n)",  # too few values
])
def test_parse_invalid_controller_raises(parser, bad_text):
    with pytest.raises(BlockFormatError):
        parser.parse(bad_text)


@pytest.mark.parametrize("bad_input", [
    "not_a_controller",
    123,
])
def test_serialize_invalid_type_raises(serializer, bad_input):
    with pytest.raises(TypeError):
        serializer.serialize(bad_input)
