from src.output_module import format_matrix, print_matrix


def test_format_matrix():
    assert format_matrix([[1, 2], [3.5, 4]]) == "1.0 2.0\n3.5 4.0"


def test_print_matrix(capsys):
    print_matrix([[1, 2]])
    assert capsys.readouterr().out == "1.0 2.0\n"
