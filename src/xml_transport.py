import time
import xml.etree.ElementTree as ET
from pathlib import Path

from .errors import IntegrationTimeoutError, InvalidDataError, VersionConflictError
from .input_module import validate_matrix


SCHEMA_VERSION = "1.0"


def write_matrix(path: Path, matrix: list[list[float]], stage: str) -> None:
    checked_matrix = validate_matrix(matrix)
    root = ET.Element("matrix-message", version=SCHEMA_VERSION, stage=stage)
    root.set("rows", str(len(checked_matrix)))
    root.set("columns", str(len(checked_matrix[0])))
    for row_number, row in enumerate(checked_matrix, start=1):
        row_element = ET.SubElement(root, "row", number=str(row_number))
        for value in row:
            ET.SubElement(row_element, "value").text = str(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def read_matrix(path: Path, timeout: float = 1.0) -> list[list[float]]:
    start = time.monotonic()
    while not path.exists():
        if time.monotonic() - start >= timeout:
            raise IntegrationTimeoutError(f"Файл {path.name} не получен вовремя.")
        time.sleep(0.01)
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as error:
        raise InvalidDataError("Не удалось прочитать XML-сообщение.") from error
    if root.tag != "matrix-message":
        raise InvalidDataError("Неверный корневой элемент XML.")
    if root.get("version") != SCHEMA_VERSION:
        raise VersionConflictError("Версия XML-схемы не поддерживается.")
    try:
        expected_rows = int(root.get("rows", "0"))
        expected_columns = int(root.get("columns", "0"))
        matrix = [
            [float(value.text) for value in row.findall("value")]
            for row in root.findall("row")
        ]
    except (TypeError, ValueError) as error:
        raise InvalidDataError("В XML обнаружены некорректные числа.") from error
    checked_matrix = validate_matrix(matrix)
    if len(checked_matrix) != expected_rows:
        raise InvalidDataError("Число строк не совпадает с заголовком XML.")
    if len(checked_matrix[0]) != expected_columns:
        raise InvalidDataError("Число столбцов не совпадает с заголовком XML.")
    return checked_matrix
