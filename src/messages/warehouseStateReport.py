from typing import Dict

from aioxmpp.xso.types import Integer


class WarehouseStateReport:
	def __init__(self, contents: Dict, freeCapacity: Integer) -> None:
		self.contents = contents
		self.freeCapacity = freeCapacity
