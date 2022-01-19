import json
from jsonSerializable import JsonSerializable
from messages.transportOffer import TransportOffer

class TransportProposal(JsonSerializable):
	def __init__(self, offer: TransportOffer=None, delivery_no=0, price=0) -> None:
		self.offer = offer
		self.delivery_no = delivery_no
		self.price = price

	@classmethod
	def fromMsg(self, msg):
		msgBody = json.loads(msg.body)
		off = TransportOffer()
		off.fromJSON(msgBody['offer'])
		self.offer = off
		self.delivery_no = msgBody['delivery_no']
		self.price = msgBody['price']
		return self