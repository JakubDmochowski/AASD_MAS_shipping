from jsonSerializable import JsonSerializable
from typing import Dict
from aioxmpp.xso.types import Integer

class shopInventoryReport(JsonSerializable):
	def __init__(self, content: Dict) -> None:
		self.content = content