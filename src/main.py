from pathlib import Path

from src.errors import IntegrationError
from src.input_module import input_matrix, input_matrix_size
from src.integration import run_pipeline


def main() -> None:
    rows, columns = input_matrix_size()
    matrix = input_matrix(rows, columns)
    try:
        result = run_pipeline(matrix, Path("integration_data"))
        print("Результат:")
        print(result)
        print("XML-файлы сохранены в каталоге integration_data.")
    except IntegrationError as error:
        print(f"Ошибка интеграции: {error}")


if __name__ == "__main__":  # pragma: no cover
    main()
