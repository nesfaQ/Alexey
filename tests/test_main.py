from unittest.mock import patch

from src.main import (
    input_matrix,
    input_matrix_size,
    print_matrix,
    swap_extreme_rows,
)


def test_swap_rows_in_square_matrix():
    matrix = [
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0],
    ]

    result = swap_extreme_rows(matrix)

    assert result == [
        [7.0, 8.0, 9.0],
        [4.0, 5.0, 6.0],
        [1.0, 2.0, 3.0],
    ]


def test_swap_rows_in_rectangular_matrix():
    matrix = [[4.5, -8.0], [1.0, 12.0], [3.0, 6.0]]

    assert swap_extreme_rows(matrix) == [
        [1.0, 12.0],
        [4.5, -8.0],
        [3.0, 6.0],
    ]


def test_matrix_does_not_change_when_extremes_are_in_one_row():
    matrix = [[-10.0, 10.0], [1.0, 2.0]]

    assert swap_extreme_rows(matrix) == matrix


def test_source_matrix_is_not_modified():
    matrix = [[1.0, 2.0], [3.0, 4.0]]

    swap_extreme_rows(matrix)

    assert matrix == [[1.0, 2.0], [3.0, 4.0]]


def test_input_matrix_size_repeats_after_invalid_values():
    answers = ["a", "0", "3", "2", "3"]

    with patch("builtins.input", side_effect=answers):
        assert input_matrix_size() == (2, 3)


def test_input_matrix_repeats_after_wrong_row_length():
    answers = ["1 2", "1 2 3", "4 5 6"]

    with patch("builtins.input", side_effect=answers):
        assert input_matrix(2, 3) == [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]


def test_input_matrix_repeats_after_non_numeric_value():
    answers = ["1 x", "1.5 2.5"]

    with patch("builtins.input", side_effect=answers):
        assert input_matrix(1, 2) == [[1.5, 2.5]]


def test_print_matrix(capsys):
    print_matrix([[1.0, 2.0], [3.0, 4.0]])

    assert capsys.readouterr().out == "1.0 2.0\n3.0 4.0\n"
