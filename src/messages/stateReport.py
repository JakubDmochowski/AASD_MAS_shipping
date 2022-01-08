from typing import Dict
from jsonSerializable import JsonSerializable


class StateReport(JsonSerializable):
    def __init__(self, src, dst, contents: Dict[str, Dict[str, int]]) -> None:
        self.src = src
        self.dst = dst
        self.contents = contents
