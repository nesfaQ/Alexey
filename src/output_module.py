from .input_module import validate_matrix


def format_matrix(matrix: list[list[float]]) -> str:
    checked_matrix = validate_matrix(matrix)
    lines = []
    for row in checked_matrix:
        lines.append(" ".join(str(value) for value in row))
    return "\n".join(lines)


def print_matrix(matrix: list[list[float]]) -> None:
    print(format_matrix(matrix))
