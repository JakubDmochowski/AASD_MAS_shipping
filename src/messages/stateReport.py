from typing import Dict
from jsonSerializable import JsonSerializable


class StateReport(JsonSerializable):
    def __init__(self, state: Dict[str, Dict[str, int]]) -> None:
        self.state = state
