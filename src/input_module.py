import math

from .errors import InvalidDataError


def validate_matrix(matrix: list[list[float]]) -> list[list[float]]:
    if not isinstance(matrix, list) or not matrix:
        raise InvalidDataError("Матрица не должна быть пустой.")
    columns = len(matrix[0]) if isinstance(matrix[0], list) else 0
    if columns == 0:
        raise InvalidDataError("Строка матрицы не должна быть пустой.")

    result = []
    for row in matrix:
        if not isinstance(row, list) or len(row) != columns:
            raise InvalidDataError("Все строки матрицы должны быть одинаковой длины.")
        try:
            values = [float(value) for value in row]
        except (TypeError, ValueError) as error:
            raise InvalidDataError("В матрице должны быть только числа.") from error
        if not all(math.isfinite(value) for value in values):
            raise InvalidDataError("Элементы матрицы должны быть конечными числами.")
        result.append(values)
    return result


def input_matrix_size() -> tuple[int, int]:
    while True:
        try:
            rows = int(input("Введите количество строк: "))
            columns = int(input("Введите количество столбцов: "))
        except ValueError:
            print("Ошибка: размеры должны быть целыми числами.")
            continue
        if rows > 0 and columns > 0:
            return rows, columns
        print("Ошибка: размеры должны быть натуральными числами.")


def input_matrix(rows: int, columns: int) -> list[list[float]]:
    matrix = []
    for row_number in range(1, rows + 1):
        while True:
            values = input(
                f"Введите строку {row_number} из {columns} чисел: "
            ).split()
            if len(values) != columns:
                print(f"Ошибка: требуется ровно {columns} чисел.")
                continue
            try:
                matrix.append([float(value) for value in values])
                break
            except ValueError:
                print("Ошибка: все элементы должны быть числами.")
    return matrix
