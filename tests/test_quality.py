"""Модульные, интеграционные и регрессионные тесты качества (вариант 4).

Основной метод - эквивалентное разбиение входных данных на допустимые
и недопустимые классы. Дополнительно применены методы «белого ящика»:
покрытие решений, условий и комбинаторное покрытие условий.
"""

import threading
import xml.etree.ElementTree as ET

import pytest

from src.errors import (
    IntegrationTimeoutError,
    InvalidDataError,
    ModuleUnavailableError,
    VersionConflictError,
)
from src.input_module import input_matrix, input_matrix_size, validate_matrix
from src.integration import run_pipeline
from src.main import main
from src.output_module import format_matrix, print_matrix
from src.processing_module import swap_extreme_rows
from src.xml_transport import read_matrix, write_matrix


RECTANGULAR_MATRIX = [[4.5, -8.0], [1.0, 12.0], [3.0, 6.0]]
RECTANGULAR_RESULT = [[1.0, 12.0], [4.5, -8.0], [3.0, 6.0]]
POSITIVE_MATRIX = [[1.0, 2.0], [3.0, 4.0]]
ONE_ROW_MATRIX = [[7.5, -3.0, 0.0]]
EXCHANGE_FILES = ("input.xml", "processed.xml", "result.xml")


def _message(rows, columns, body, version="1.0"):
    return (
        f'<matrix-message version="{version}" rows="{rows}" columns="{columns}">'
        f"{body}</matrix-message>"
    )


def _row(*values):
    return "<row>" + "".join(f"<value>{value}</value>" for value in values) + "</row>"


def _write(tmp_path, text, name="message.xml"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


class TestInputModule:
    """Эквивалентное разбиение входных матриц и интерактивного ввода."""

    @pytest.mark.parametrize(
        "matrix, expected",
        [
            ([[1]], [[1.0]]),
            ([[1, 2, 3]], [[1.0, 2.0, 3.0]]),
            ([[1.25, "2"]], [[1.25, 2.0]]),
            ([["-4e2", "+0.5"]], [[-400.0, 0.5]]),
            ([[-1.0, 0.0], [0.0, -0.0]], [[-1.0, 0.0], [0.0, -0.0]]),
        ],
    )
    def test_valid_class_returns_float_matrix(self, matrix, expected):
        result = validate_matrix(matrix)
        assert result == expected
        assert all(isinstance(value, float) for row in result for value in row)

    def test_valid_class_builds_new_object(self):
        source = [[1, 2]]
        result = validate_matrix(source)
        assert result is not source
        assert result[0] is not source[0]

    @pytest.mark.parametrize(
        "matrix",
        [
            None,
            [],
            (),
            "1 2",
            [[]],
            [[], []],
            [[1, 2], [3]],
            [[1, 2], [3, 4, 5]],
            [(1, 2)],
            [[1, 2], (3, 4)],
            [[1, None]],
            [[1, "x"]],
            [[1, [2]]],
            [["", 1]],
            [[float("nan"), 1]],
            [["inf", 1]],
            [[1, "-Infinity"]],
        ],
    )
    def test_invalid_class_raises(self, matrix):
        with pytest.raises(InvalidDataError):
            validate_matrix(matrix)

    @pytest.mark.parametrize(
        "matrix, message",
        [
            ([], "пустой"),
            ([[]], "Строка матрицы"),
            ([[1, 2], [3]], "одинаковой длины"),
            ([["слово"]], "только числа"),
            ([[1e309]], "конечными"),
        ],
    )
    def test_error_messages_match_class(self, matrix, message):
        with pytest.raises(InvalidDataError, match=message):
            validate_matrix(matrix)

    @pytest.mark.parametrize(
        "answers, expected",
        [
            (["1", "1"], (1, 1)),
            (["3", "2"], (3, 2)),
            (["x", "2", "3"], (2, 3)),
            (["2", "1.5", "2", "2"], (2, 2)),
            (["0", "1", "1", "1"], (1, 1)),
            (["1", "-4", "5", "1"], (5, 1)),
        ],
    )
    def test_matrix_size_classes(self, monkeypatch, answers, expected):
        replies = iter(answers)
        monkeypatch.setattr("builtins.input", lambda prompt: next(replies))
        assert input_matrix_size() == expected

    @pytest.mark.parametrize(
        "answers, expected",
        [
            (["1 2"], [[1.0, 2.0]]),
            (["1", "1 2"], [[1.0, 2.0]]),
            (["1 2 3", "4 5"], [[4.0, 5.0]]),
            (["a b", "-1 2e1"], [[-1.0, 20.0]]),
        ],
    )
    def test_matrix_row_classes(self, monkeypatch, answers, expected):
        replies = iter(answers)
        monkeypatch.setattr("builtins.input", lambda prompt: next(replies))
        assert input_matrix(1, 2) == expected


class TestProcessingModule:
    """Покрытие решений и условий алгоритма перестановки строк."""

    def test_rectangular_matrix_swaps_extreme_rows(self):
        assert swap_extreme_rows(RECTANGULAR_MATRIX) == RECTANGULAR_RESULT

    def test_single_row_is_stable(self):
        assert swap_extreme_rows(ONE_ROW_MATRIX) == ONE_ROW_MATRIX

    def test_single_column_swaps_rows(self):
        assert swap_extreme_rows([[3.0], [1.0], [2.0]]) == [[1.0], [3.0], [2.0]]

    def test_single_element(self):
        assert swap_extreme_rows([[42.0]]) == [[42.0]]

    def test_minimum_in_last_row(self):
        assert swap_extreme_rows([[0.0, 2.0], [1.0, 9.0], [-5.0, 4.0]]) == [
            [0.0, 2.0],
            [-5.0, 4.0],
            [1.0, 9.0],
        ]

    def test_maximum_in_last_row(self):
        assert swap_extreme_rows([[1.0, 2.0], [0.0, 3.0], [5.0, 4.0]]) == [
            [1.0, 2.0],
            [5.0, 4.0],
            [0.0, 3.0],
        ]

    def test_both_extremes_in_first_row(self):
        matrix = [[-9.0, 9.0], [0.0, 1.0]]
        assert swap_extreme_rows(matrix) == matrix

    def test_both_extremes_in_last_row(self):
        matrix = [[0.0, 1.0], [-9.0, 9.0]]
        assert swap_extreme_rows(matrix) == matrix

    def test_equal_extremes_keep_first_rows(self):
        matrix = [[-5.0, 10.0], [-5.0, 10.0]]
        assert swap_extreme_rows(matrix) == matrix

    def test_duplicate_minimum_uses_first_occurrence(self):
        assert swap_extreme_rows([[0.0, 1.0], [0.0, 2.0], [5.0, 6.0]]) == [
            [5.0, 6.0],
            [0.0, 2.0],
            [0.0, 1.0],
        ]

    def test_constant_matrix_is_stable(self):
        matrix = [[2.0, 2.0], [2.0, 2.0]]
        assert swap_extreme_rows(matrix) == matrix

    def test_negative_and_float_values(self):
        assert swap_extreme_rows([[-1.5, 2.5], [7.0, -0.5]]) == [[7.0, -0.5], [-1.5, 2.5]]

    def test_source_matrix_is_not_modified(self):
        source = [row[:] for row in RECTANGULAR_MATRIX]
        swap_extreme_rows(source)
        assert source == RECTANGULAR_MATRIX

    def test_result_is_independent_copy(self):
        source = [row[:] for row in RECTANGULAR_MATRIX]
        result = swap_extreme_rows(source)
        result[0][0] = 100.0
        assert source[0][0] == 4.5

    @pytest.mark.parametrize("matrix", [[], [[]], [[1, 2], [3]], [[1, "x"]]])
    def test_invalid_matrix_propagates_error(self, matrix):
        with pytest.raises(InvalidDataError):
            swap_extreme_rows(matrix)


class TestOutputModule:
    """Классы эквивалентности форматирования результата."""

    @pytest.mark.parametrize(
        "matrix, expected",
        [
            ([[1, 2], [3.5, 4]], "1.0 2.0\n3.5 4.0"),
            ([[7]], "7.0"),
            (ONE_ROW_MATRIX, "7.5 -3.0 0.0"),
            ([[1.0], [2.0]], "1.0\n2.0"),
            ([[-1.5, -0.25]], "-1.5 -0.25"),
            ([["3", 1e-3]], "3.0 0.001"),
        ],
    )
    def test_format_classes(self, matrix, expected):
        assert format_matrix(matrix) == expected

    @pytest.mark.parametrize("matrix", [[], [[]], [[1, 2], [3]], [[1, "x"]]])
    def test_invalid_matrix_raises(self, matrix):
        with pytest.raises(InvalidDataError):
            format_matrix(matrix)

    def test_print_matrix_writes_line_by_line(self, capsys):
        assert print_matrix([[1, 2], [3, 4]]) is None
        assert capsys.readouterr().out == "1.0 2.0\n3.0 4.0\n"


class TestXmlTransport:
    """Контракт XML-сообщения: допустимые и недопустимые классы."""

    def test_write_and_read_round_trip(self, tmp_path):
        path = tmp_path / "matrix.xml"
        write_matrix(path, RECTANGULAR_MATRIX, "input")
        assert read_matrix(path) == RECTANGULAR_MATRIX

    def test_header_contains_dimensions_and_attributes(self, tmp_path):
        path = tmp_path / "matrix.xml"
        write_matrix(path, RECTANGULAR_MATRIX, "processing")
        root = ET.parse(path).getroot()
        assert root.tag == "matrix-message"
        assert root.attrib == {
            "version": "1.0",
            "stage": "processing",
            "rows": "3",
            "columns": "2",
        }
        assert [row.get("number") for row in root.findall("row")] == ["1", "2", "3"]

    def test_write_creates_missing_directory(self, tmp_path):
        path = tmp_path / "nested" / "deeper" / "matrix.xml"
        write_matrix(path, [[1.0]], "output")
        assert path.exists()

    def test_write_rejects_invalid_matrix(self, tmp_path):
        path = tmp_path / "matrix.xml"
        with pytest.raises(InvalidDataError):
            write_matrix(path, [[1, "x"]], "input")
        assert not path.exists()

    def test_write_normalises_input_values(self, tmp_path):
        path = tmp_path / "matrix.xml"
        write_matrix(path, [["1", 2]], "input")
        assert read_matrix(path) == [[1.0, 2.0]]

    @pytest.mark.parametrize("timeout", [0.0, 0.02])
    def test_read_missing_file_times_out(self, tmp_path, timeout):
        with pytest.raises(IntegrationTimeoutError, match="absent.xml"):
            read_matrix(tmp_path / "absent.xml", timeout=timeout)

    def test_read_waits_for_late_file(self, tmp_path):
        path = tmp_path / "late.xml"
        draft = tmp_path / "late.draft"

        def writer():
            write_matrix(draft, [[1.0, 2.0]], "input")
            draft.replace(path)

        timer = threading.Timer(0.05, writer)
        timer.start()
        try:
            assert read_matrix(path, timeout=5.0) == [[1.0, 2.0]]
        finally:
            timer.join()

    @pytest.mark.parametrize("text", ["", "<matrix-message", "просто текст"])
    def test_read_rejects_broken_xml(self, tmp_path, text):
        with pytest.raises(InvalidDataError, match="прочитать"):
            read_matrix(_write(tmp_path, text))

    @pytest.mark.parametrize("tag", ["data", "matrix", "root", "matrix-messages"])
    def test_read_rejects_wrong_root_tag(self, tmp_path, tag):
        with pytest.raises(InvalidDataError, match="корневой"):
            read_matrix(_write(tmp_path, f'<{tag} version="1.0"/>'))

    @pytest.mark.parametrize("version", ["0.9", "2.0", "", "1"])
    def test_read_rejects_unsupported_version(self, tmp_path, version):
        text = _message(1, 1, _row(1), version=version)
        with pytest.raises(VersionConflictError):
            read_matrix(_write(tmp_path, text))

    def test_read_rejects_missing_version(self, tmp_path):
        text = f"<matrix-message>{_row(1)}</matrix-message>"
        with pytest.raises(VersionConflictError):
            read_matrix(_write(tmp_path, text))

    @pytest.mark.parametrize(
        "body",
        [
            _row("x"),
            _row(""),
            _row("1", "нет"),
            _row(1) + _row(2, 3),
            _row(1, 2)[:-6],
        ],
    )
    def test_read_rejects_bad_numbers_and_structure(self, tmp_path, body):
        with pytest.raises(InvalidDataError):
            read_matrix(_write(tmp_path, _message(1, 2, body)))

    @pytest.mark.parametrize(
        "rows, columns, body",
        [
            (2, 1, _row(1)),
            (1, 2, _row(1)),
            (0, 0, _row(1)),
            (1, 1, ""),
            (-1, 1, _row(1)),
        ],
    )
    def test_read_rejects_header_mismatch(self, tmp_path, rows, columns, body):
        with pytest.raises(InvalidDataError):
            read_matrix(_write(tmp_path, _message(rows, columns, body)))

    @pytest.mark.parametrize("rows, columns", [("много", "1"), ("1", "два"), ("1.5", "1")])
    def test_read_rejects_non_integer_header(self, tmp_path, rows, columns):
        with pytest.raises(InvalidDataError, match="некорректные"):
            read_matrix(_write(tmp_path, _message(rows, columns, _row(1.0))))

    def test_read_rejects_missing_headers(self, tmp_path):
        text = f'<matrix-message version="1.0">{_row(1)}</matrix-message>'
        with pytest.raises(InvalidDataError):
            read_matrix(_write(tmp_path, text))


class TestIntegration:
    """Интеграция этапов через XML-конвейер: успешные и ошибочные сценарии."""

    def test_pipeline_returns_formatted_result(self, tmp_path):
        assert run_pipeline(RECTANGULAR_MATRIX, tmp_path) == "1.0 12.0\n4.5 -8.0\n3.0 6.0"

    def test_pipeline_creates_three_messages(self, tmp_path):
        run_pipeline(RECTANGULAR_MATRIX, tmp_path)
        assert sorted(path.name for path in tmp_path.glob("*.xml")) == list(EXCHANGE_FILES)

    def test_pipeline_stages_are_recorded(self, tmp_path):
        run_pipeline(RECTANGULAR_MATRIX, tmp_path)
        stages = [ET.parse(tmp_path / name).getroot().get("stage") for name in EXCHANGE_FILES]
        assert stages == ["input", "processing", "output"]

    def test_pipeline_messages_hold_stage_data(self, tmp_path):
        run_pipeline(RECTANGULAR_MATRIX, tmp_path)
        assert read_matrix(tmp_path / "input.xml") == RECTANGULAR_MATRIX
        assert read_matrix(tmp_path / "processed.xml") == RECTANGULAR_RESULT
        assert read_matrix(tmp_path / "result.xml") == RECTANGULAR_RESULT

    @pytest.mark.parametrize(
        "matrix, expected",
        [
            ([[3.0]], "3.0"),
            ([["2"], [1]], "1.0\n2.0"),
            (ONE_ROW_MATRIX, "7.5 -3.0 0.0"),
        ],
    )
    def test_pipeline_valid_classes(self, tmp_path, matrix, expected):
        assert run_pipeline(matrix, tmp_path) == expected

    def test_pipeline_creates_exchange_directory(self, tmp_path):
        exchange = tmp_path / "new" / "folder"
        run_pipeline(POSITIVE_MATRIX, exchange)
        assert (exchange / "result.xml").exists()

    def test_pipeline_is_repeatable(self, tmp_path):
        assert run_pipeline(RECTANGULAR_MATRIX, tmp_path) == run_pipeline(
            RECTANGULAR_MATRIX, tmp_path
        )

    @pytest.mark.parametrize(
        "processor, formatter",
        [(None, format_matrix), (swap_extreme_rows, None), (None, None)],
    )
    def test_unavailable_module_combinations(self, tmp_path, processor, formatter):
        with pytest.raises(ModuleUnavailableError):
            run_pipeline(POSITIVE_MATRIX, tmp_path, processor=processor, formatter=formatter)

    def test_custom_processor_and_formatter(self, tmp_path):
        result = run_pipeline(
            POSITIVE_MATRIX,
            tmp_path,
            processor=lambda matrix: matrix,
            formatter=lambda matrix: f"rows={len(matrix)}",
        )
        assert result == "rows=2"

    def test_processor_contract_violation_is_detected(self, tmp_path):
        with pytest.raises(InvalidDataError):
            run_pipeline(POSITIVE_MATRIX, tmp_path, processor=lambda matrix: [])

    @pytest.mark.parametrize("matrix", [[], [[]], [[1, 2], [3]], [[1, "x"]], None])
    def test_invalid_matrix_stops_pipeline(self, tmp_path, matrix):
        with pytest.raises(InvalidDataError):
            run_pipeline(matrix, tmp_path)
        assert not (tmp_path / "result.xml").exists()

    def test_processor_error_stops_pipeline(self, tmp_path):
        def broken(matrix):
            raise InvalidDataError("сбой обработки")

        with pytest.raises(InvalidDataError, match="сбой обработки"):
            run_pipeline(POSITIVE_MATRIX, tmp_path, processor=broken)
        assert not (tmp_path / "result.xml").exists()

    def test_formatter_error_stops_pipeline(self, tmp_path):
        def broken(matrix):
            raise InvalidDataError("сбой вывода")

        with pytest.raises(InvalidDataError, match="сбой вывода"):
            run_pipeline(POSITIVE_MATRIX, tmp_path, formatter=broken)


class TestMain:
    """Сценарии консольного запуска."""

    @pytest.fixture
    def console(self, monkeypatch):
        monkeypatch.setattr("src.main.input_matrix_size", lambda: (1, 2))
        monkeypatch.setattr("src.main.input_matrix", lambda rows, columns: [[1, 2]])
        return monkeypatch

    def test_main_prints_result(self, console, capsys):
        console.setattr("src.main.run_pipeline", lambda matrix, path: "1.0 2.0")
        main()
        output = capsys.readouterr().out
        assert "Результат:" in output
        assert "1.0 2.0" in output
        assert "integration_data" in output

    def test_main_runs_real_pipeline(self, console, capsys, tmp_path):
        console.chdir(tmp_path)
        main()
        assert "1.0 2.0" in capsys.readouterr().out
        assert (tmp_path / "integration_data" / "result.xml").exists()

    @pytest.mark.parametrize(
        "error",
        [
            InvalidDataError("тест"),
            ModuleUnavailableError("тест"),
            IntegrationTimeoutError("тест"),
            VersionConflictError("тест"),
        ],
    )
    def test_main_reports_integration_errors(self, console, capsys, error):
        def failing(matrix, path):
            raise error

        console.setattr("src.main.run_pipeline", failing)
        main()
        assert "Ошибка интеграции: тест" in capsys.readouterr().out


class TestRegression:
    """Регрессионные тесты на дефекты BR-01 и BR-02."""

    def test_br01_read_matrix_rejects_non_finite_numbers(self, tmp_path):
        """BR-01: значения NaN и Infinity из XML принимались как корректные числа."""
        for values in (("nan", "1"), ("1", "inf"), ("-Infinity", "2")):
            path = _write(tmp_path, _message(1, 2, _row(*values)))
            with pytest.raises(InvalidDataError):
                read_matrix(path)

    def test_br02_stale_result_removed_after_failure(self, tmp_path):
        """BR-02: после сбоя нового запроса оставался устаревший result.xml."""
        assert run_pipeline(RECTANGULAR_MATRIX, tmp_path) == "1.0 12.0\n4.5 -8.0\n3.0 6.0"
        with pytest.raises(InvalidDataError):
            run_pipeline([[1, "x"]], tmp_path)
        assert [name for name in EXCHANGE_FILES if (tmp_path / name).exists()] == []

    def test_br02_unavailable_module_removes_previous_result(self, tmp_path):
        run_pipeline(POSITIVE_MATRIX, tmp_path)
        with pytest.raises(ModuleUnavailableError):
            run_pipeline(POSITIVE_MATRIX, tmp_path, processor=None)
        assert not (tmp_path / "result.xml").exists()

    def test_br02_formatter_failure_removes_messages(self, tmp_path):
        def broken(matrix):
            raise ValueError("сбой вывода")

        with pytest.raises(ValueError):
            run_pipeline(POSITIVE_MATRIX, tmp_path, formatter=broken)
        assert not any((tmp_path / name).exists() for name in EXCHANGE_FILES)
