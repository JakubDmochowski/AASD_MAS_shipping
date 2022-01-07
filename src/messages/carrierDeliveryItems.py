import json
from jsonSerializable import JsonSerializable
from typing import Dict
from aioxmpp.xso.types import Integer

class CarrierDeliveryItems(JsonSerializable):
	def __init__(self, content: Dict[str, int]) -> None:
		self.content = content

	@classmethod
	def fromMsg(self, msg):
		msgBody = json.loads(msg.body)
		self.content = msgBody['content']
		return self
