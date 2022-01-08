from jsonSerializable import JsonSerializable
from typing import Dict
from aioxmpp.xso.types import Integer


class productAvailabilityReport(JsonSerializable):
    def __init__(self, contents: Dict[str, Integer]) -> None:
        self.contents = contents
