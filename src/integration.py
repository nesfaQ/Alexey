from collections.abc import Callable
from pathlib import Path
from typing import Optional

from .errors import ModuleUnavailableError
from .input_module import validate_matrix
from .output_module import format_matrix
from .processing_module import swap_extreme_rows
from .xml_transport import read_matrix, write_matrix


MatrixHandler = Callable[[list[list[float]]], list[list[float]]]
OutputHandler = Callable[[list[list[float]]], str]

EXCHANGE_FILES = ("input.xml", "processed.xml", "result.xml")


def clear_exchange(exchange_dir: Path) -> None:
    for name in EXCHANGE_FILES:
        (exchange_dir / name).unlink(missing_ok=True)


def run_pipeline(
    matrix: list[list[float]],
    exchange_dir: Path,
    processor: Optional[MatrixHandler] = swap_extreme_rows,
    formatter: Optional[OutputHandler] = format_matrix,
) -> str:
    clear_exchange(exchange_dir)
    if processor is None:
        raise ModuleUnavailableError("Модуль обработки недоступен.")
    if formatter is None:
        raise ModuleUnavailableError("Модуль вывода недоступен.")
    input_path, processed_path, result_path = (
        exchange_dir / name for name in EXCHANGE_FILES
    )
    try:
        write_matrix(input_path, validate_matrix(matrix), "input")
        input_data = read_matrix(input_path)
        processed_data = processor(input_data)
        write_matrix(processed_path, processed_data, "processing")
        output_data = read_matrix(processed_path)
        write_matrix(result_path, output_data, "output")
        return formatter(read_matrix(result_path))
    except Exception:
        clear_exchange(exchange_dir)
        raise
