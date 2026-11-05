from collections.abc import Callable
from pathlib import Path

from .errors import ModuleUnavailableError
from .input_module import validate_matrix
from .output_module import format_matrix
from .processing_module import swap_extreme_rows
from .xml_transport import read_matrix, write_matrix


MatrixHandler = Callable[[list[list[float]]], list[list[float]]]
OutputHandler = Callable[[list[list[float]]], str]


def run_pipeline(
    matrix: list[list[float]],
    exchange_dir: Path,
    processor: MatrixHandler | None = swap_extreme_rows,
    formatter: OutputHandler | None = format_matrix,
) -> str:
    if processor is None:
        raise ModuleUnavailableError("Модуль обработки недоступен.")
    if formatter is None:
        raise ModuleUnavailableError("Модуль вывода недоступен.")
    input_path = exchange_dir / "input.xml"
    processed_path = exchange_dir / "processed.xml"
    result_path = exchange_dir / "result.xml"
    write_matrix(input_path, validate_matrix(matrix), "input")
    input_data = read_matrix(input_path)
    processed_data = processor(input_data)
    write_matrix(processed_path, processed_data, "processing")
    output_data = read_matrix(processed_path)
    write_matrix(result_path, output_data, "output")
    return formatter(read_matrix(result_path))
