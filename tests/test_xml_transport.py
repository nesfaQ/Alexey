import xml.etree.ElementTree as ET

import pytest

from src.errors import IntegrationTimeoutError, InvalidDataError, VersionConflictError
from src.xml_transport import read_matrix, write_matrix


def test_xml_round_trip(tmp_path):
    path = tmp_path / "matrix.xml"
    write_matrix(path, [[1, 2], [3.5, 4]], "input")
    assert read_matrix(path) == [[1.0, 2.0], [3.5, 4.0]]
    root = ET.parse(path).getroot()
    assert root.attrib == {"version": "1.0", "stage": "input", "rows": "2", "columns": "2"}


def test_read_matrix_reports_timeout(tmp_path):
    with pytest.raises(IntegrationTimeoutError):
        read_matrix(tmp_path / "missing.xml", timeout=0.02)


def test_read_matrix_rejects_broken_xml(tmp_path):
    path = tmp_path / "broken.xml"
    path.write_text("<matrix>", encoding="utf-8")
    with pytest.raises(InvalidDataError):
        read_matrix(path)


def test_read_matrix_rejects_wrong_root(tmp_path):
    path = tmp_path / "wrong.xml"
    path.write_text('<data version="1.0"/>', encoding="utf-8")
    with pytest.raises(InvalidDataError):
        read_matrix(path)


def test_read_matrix_rejects_wrong_version(tmp_path):
    path = tmp_path / "version.xml"
    path.write_text('<matrix-message version="2.0"/>', encoding="utf-8")
    with pytest.raises(VersionConflictError):
        read_matrix(path)


@pytest.mark.parametrize(
    "xml",
    [
        '<matrix-message version="1.0" rows="1" columns="1">'
        "<row><value>x</value></row></matrix-message>",
        '<matrix-message version="1.0" rows="2" columns="1">'
        "<row><value>1</value></row></matrix-message>",
        '<matrix-message version="1.0" rows="1" columns="2">'
        "<row><value>1</value></row></matrix-message>",
    ],
)
def test_read_matrix_rejects_inconsistent_data(tmp_path, xml):
    path = tmp_path / "invalid.xml"
    path.write_text(xml, encoding="utf-8")
    with pytest.raises(InvalidDataError):
        read_matrix(path)
