from .input_module import validate_matrix


def swap_extreme_rows(matrix: list[list[float]]) -> list[list[float]]:
    result = validate_matrix(matrix)
    min_row = 0
    max_row = 0
    for row_index, row in enumerate(result):
        if min(row) < min(result[min_row]):
            min_row = row_index
        if max(row) > max(result[max_row]):
            max_row = row_index
    result[min_row], result[max_row] = result[max_row], result[min_row]
    return result
