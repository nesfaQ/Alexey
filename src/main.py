def input_matrix_size() -> tuple[int, int]:
    """Запросить натуральные размеры матрицы."""
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
    """Считать вещественную матрицу заданного размера."""
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


def swap_extreme_rows(matrix: list[list[float]]) -> list[list[float]]:
    """Поменять строки с глобальными минимумом и максимумом."""
    result = [row.copy() for row in matrix]
    min_row = min(
        range(len(result)),
        key=lambda index: min(result[index]),
    )
    max_row = max(
        range(len(result)),
        key=lambda index: max(result[index]),
    )
    result[min_row], result[max_row] = result[max_row], result[min_row]
    return result


def print_matrix(matrix: list[list[float]]) -> None:
    """Вывести матрицу построчно."""
    for row in matrix:
        print(*row)


def main() -> None:
    """Запустить консольную программу."""
    rows, columns = input_matrix_size()
    matrix = input_matrix(rows, columns)
    result = swap_extreme_rows(matrix)
    print("Результат:")
    print_matrix(result)


if __name__ == "__main__":
    main()
