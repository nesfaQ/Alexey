from unittest.mock import patch

import pytest

from src.errors import InvalidDataError
from src.input_module import input_matrix, input_matrix_size, validate_matrix


def test_validate_matrix_converts_values_to_float():
    assert validate_matrix([[1, "2.5"]]) == [[1.0, 2.5]]


@pytest.mark.parametrize("matrix", [[], [[]], [[1, 2], [3]], [[1, "x"]]])
def test_validate_matrix_rejects_invalid_data(matrix):
    with pytest.raises(InvalidDataError):
        validate_matrix(matrix)


def test_input_matrix_size_repeats_after_invalid_values():
    with patch("builtins.input", side_effect=["a", "0", "3", "2", "3"]):
        assert input_matrix_size() == (2, 3)


def test_input_matrix_repeats_after_wrong_values():
    answers = ["1 2", "1 x 3", "1 2 3", "4 5 6"]
    with patch("builtins.input", side_effect=answers):
        assert input_matrix(2, 3) == [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
