from jsonSerializable import JsonSerializable
from typing import Dict
from aioxmpp.xso.types import Integer

class carrierDeliveryItems(JsonSerializable):
	def __init__(self, content: Dict[str, int]) -> None:
		self.content = content