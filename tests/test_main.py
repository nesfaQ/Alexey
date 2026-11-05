from unittest.mock import patch

from src.errors import InvalidDataError
from src.main import main


def test_main_prints_pipeline_result(capsys):
    with patch("src.main.input_matrix_size", return_value=(1, 2)):
        with patch("src.main.input_matrix", return_value=[[1, 2]]):
            with patch("src.main.run_pipeline", return_value="1.0 2.0"):
                main()
    output = capsys.readouterr().out
    assert "Результат:" in output
    assert "1.0 2.0" in output


def test_main_prints_integration_error(capsys):
    with patch("src.main.input_matrix_size", return_value=(1, 1)):
        with patch("src.main.input_matrix", return_value=[[1]]):
            with patch("src.main.run_pipeline", side_effect=InvalidDataError("тест")):
                main()
    assert "Ошибка интеграции: тест" in capsys.readouterr().out
