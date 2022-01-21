from jsonSerializable import JsonSerializable
from typing import Dict
from aioxmpp.xso.types import Integer


class productAvailabilityReport(JsonSerializable):
    def __init__(self, capacity: Integer, contents: Dict[str, Integer]) -> None:
        self.capacity = capacity
        self.contents = contents
