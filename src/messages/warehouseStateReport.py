from typing import Dict
from jsonSerializable import JsonSerializable

from aioxmpp.xso.types import Integer


class WarehouseStateReport(JsonSerializable):
	def __init__(self, content: Dict[str, int] = {}, capacity: Integer = 0) -> None:
		self.content = content
		self.capacity = capacity
