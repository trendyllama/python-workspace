"""Tests for the file parser factory pattern."""

import json
from pathlib import Path

import pytest

from src.design_patterns.factory import FileParserFactory, FileType, file_parser


class FileStub:
    def __init__(self, path: Path):
        self._path = path

    def read(self) -> Path:
        return self._path

    def write(self, data: str) -> None:
        self._path.write_text(data)


@pytest.mark.parametrize(
    ("file_type", "contents", "expected"),
    [
        (
            FileType.JSON,
            json.dumps({"name": "Ada", "active": True, "score": 12}),
            {"name": "Ada", "active": True, "score": 12},
        ),
        (
            FileType.XML,
            "<person><name>Ada</name><active>true</active><score>12</score></person>",
            "<person><name>Ada</name><active>true</active><score>12</score></person>",
        ),
        (
            FileType.YAML,
            "name: Ada\nactive: true\nscore: 12\n",
            {"name": "Ada", "active": True, "score": 12},
        ),
    ],
)
def test_file_parser_factory_parses_supported_file_types(
    tmp_path: Path,
    file_type: FileType,
    contents: str,
    expected: object,
):
    file_path = tmp_path / f"data.{file_type.value}"
    file_path.write_text(contents)
    file = FileStub(file_path)

    actual = FileParserFactory().parse(file, file_type)

    if file_type is FileType.XML:
        assert actual == expected
    else:
        assert actual == expected


def test_file_parser_function_delegates_to_factory(tmp_path: Path):
    file_path = tmp_path / "config.json"
    file_path.write_text(json.dumps({"enabled": True}))

    actual = file_parser(FileStub(file_path), FileType.JSON)

    assert actual == {"enabled": True}
