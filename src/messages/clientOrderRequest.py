from jsonSerializable import JsonSerializable
from typing import Dict
from aioxmpp.xso.types import Integer

class clientOrderRequest(JsonSerializable):
	def __init__(self, order: Dict[str, int]) -> None:
		self.order = order