from src.processing_module import swap_extreme_rows


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


def test_first_rows_are_used_when_extremes_repeat():
    matrix = [[-5.0, 10.0], [-5.0, 10.0], [1.0, 2.0]]
    assert swap_extreme_rows(matrix) == matrix


def test_maximum_can_be_in_later_row():
    assert swap_extreme_rows([[0, 2], [1, 9]]) == [[1.0, 9.0], [0.0, 2.0]]
