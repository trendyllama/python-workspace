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


type Json = dict[str, "Json"] | list["Json"] | str | int | float | bool | None
type FileContents = dict[str, Json]

class File[S: FileContents](Protocol):

    path: Path

    def read(self) -> S: ...

    def write(self, data: str) -> None: ...


class JsonFile[S: FileContents](File[S]):
    def __init__(self, path: Path) -> None:
        self.path = path

    def read(self) -> S:
        with self.path.open("r") as f:
            return json.load(f)

    def write(self, data: str) -> None:
        with self.path.open("w") as f:
            json.dump(data, f)



class XmlFile[S: FileContents](File[S]):
    def __init__(self, path: Path) -> None:
        self.path = path


    def element_to_dict(self, element: ET.Element) -> Json:
        result: Json = {}

        if element.attrib:
            result["@attributes"] = element.attrib.copy()

        text = (element.text or "").strip()
        if text:
            result["#text"] = text

        for child in element:
            child_value = self.element_to_dict(child)

            if child.tag not in result:
                result[child.tag] = child_value
            elif isinstance(result[child.tag], list):
                result[child.tag].append(child_value)
            else:
                result[child.tag] = [result[child.tag], child_value]

        return result

    def read(self) -> S:
        root = ET.parse(self.path).getroot()
        return {root.tag: self.element_to_dict(root)}

    def write(self, data: str) -> None:
        root = ET.fromstring(data)
        tree = ET.ElementTree(root)
        tree.write(self.path)

class YamlFile[S: FileContents](File[S]):
    def __init__(self, path: Path) -> None:
        self.path = path

    def read(self) -> S:
        with self.path.open("r") as f:
            return yaml.safe_load(f)

    def write(self, data: str) -> None:
        with self.path.open("w") as f:
            yaml.safe_dump(data, f)



class FileParserFactory[S: FileContents]:


    @staticmethod
    def parse(file: File, file_type: FileType) -> S:
        match file_type:
            case FileType.JSON:
                return JsonFile[S](file.path).read()
            case FileType.XML:
                return XmlFile[S](file.path).read()
            case FileType.YAML:
                return YamlFile[S](file.path).read()


def file_parser(file: File, file_type: FileType) -> FileContents:
    return FileParserFactory.parse(file, file_type)
