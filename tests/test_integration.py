import pytest

from src.errors import ModuleUnavailableError
from src.integration import run_pipeline


def test_full_pipeline_creates_xml_files(tmp_path):
    result = run_pipeline([[4.5, -8], [1, 12], [3, 6]], tmp_path)
    assert result == "1.0 12.0\n4.5 -8.0\n3.0 6.0"
    assert sorted(path.name for path in tmp_path.glob("*.xml")) == [
        "input.xml",
        "processed.xml",
        "result.xml",
    ]


@pytest.mark.parametrize("processor, formatter", [(None, str), (list, None)])
def test_full_pipeline_reports_unavailable_module(tmp_path, processor, formatter):
    with pytest.raises(ModuleUnavailableError):
        run_pipeline([[1]], tmp_path, processor=processor, formatter=formatter)
