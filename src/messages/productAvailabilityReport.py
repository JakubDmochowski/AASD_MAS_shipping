from jsonSerializable import JsonSerializable
from typing import Dict
from aioxmpp.xso.types import Integer


class productAvailabilityReport(JsonSerializable):
    def __init__(self, content: Dict[str, Integer]) -> None:
        self.content = content
