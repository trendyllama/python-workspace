import json
import xml.etree.ElementTree as ET
from enum import StrEnum
from pathlib import Path
from typing import Protocol

import yaml


class FileType(StrEnum):
    JSON = "json"
    XML = "xml"
    YAML = "yaml"


class File(Protocol):
    def read(self) -> Path: ...

    def write(self, data: str) -> None: ...


class FileParserFactory:
    def _parse_json(self, file: File) -> str:
        data = json.loads(file.read().read_text())

        return data

    def _parse_xml(self, file: File) -> str:
        root = ET.parse(file.read()).getroot()
        return ET.tostring(root, encoding="unicode")

    def _parse_yaml(self, file: File) -> str:
        data = yaml.safe_load(file.read().read_text())
        return data

    def parse(self, file: File, file_type: FileType) -> str:
        match file_type:
            case FileType.JSON:
                return self._parse_json(file)
            case FileType.XML:
                return self._parse_xml(file)
            case FileType.YAML:
                return self._parse_yaml(file)


def file_parser(file: File, file_type: FileType) -> str:
    return FileParserFactory().parse(file, file_type)
