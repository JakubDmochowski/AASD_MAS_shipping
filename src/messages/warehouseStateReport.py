from typing import Dict
from jsonSerializable import JsonSerializable

from aioxmpp.xso.types import Integer


class WarehouseStateReport(JsonSerializable):
	def __init__(self, contents: Dict[str, int], freeCapacity: Integer) -> None:
		self.contents = contents
		self.freeCapacity = freeCapacity
