"""Tests for the file parser factory pattern."""

import json
from pathlib import Path

import pytest

from src.design_patterns.factory import (
    FileParserFactory,
    FileType,
    JsonFile,
    XmlFile,
    YamlFile,
    file_parser,
)


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
            {
                "person": {
                    "name": {"#text": "Ada"},
                    "active": {"#text": "true"},
                    "score": {"#text": "12"},
                }
            },
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
    file = JsonFile(file_path)

    actual = FileParserFactory().parse(file, file_type)

    assert actual == expected


def test_file_parser_function_delegates_to_factory(tmp_path: Path):
    file_path = tmp_path / "config.json"
    file_path.write_text(json.dumps({"enabled": True}))

    actual = file_parser(JsonFile(file_path), FileType.JSON)

    assert actual == {"enabled": True}


@pytest.mark.parametrize(
    ("file_class", "suffix"),
    [(JsonFile, "json"), (YamlFile, "yaml")],
)
def test_text_file_writers_write_readable_data(
    tmp_path: Path, file_class: type, suffix: str
):
    file_path = tmp_path / f"data.{suffix}"
    file = file_class(file_path)
    contents = "serialized content"

    file.write(contents)

    assert file.read() == contents


def test_xml_writer_serializes_xml(tmp_path: Path):
    file = XmlFile(tmp_path / "data.xml")
    contents = "<person><name>Ada</name></person>"

    file.write(contents)

    assert file.read() == {"person": {"name": {"#text": "Ada"}}}


def test_xml_reader_includes_attributes_and_repeated_children(tmp_path: Path):
    file_path = tmp_path / "people.xml"
    file_path.write_text(
        '<people source="registry">'
        "<person>Ada</person><person>Grace</person><person>Linus</person>"
        "</people>"
    )

    actual = XmlFile(file_path).read()

    assert actual == {
        "people": {
            "@attributes": {"source": "registry"},
            "person": [
                {"#text": "Ada"},
                {"#text": "Grace"},
                {"#text": "Linus"},
            ],
        }
    }
