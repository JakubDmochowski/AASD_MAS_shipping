import json
from jsonSerializable import JsonSerializable

class TransportProposal(JsonSerializable):
	def __init__(self, src, dst, delivery_no, delivery_time, price, threadId: str) -> None:
		self.src = src
		self.dst = dst
		self.delivery_no = delivery_no
		self.delivery_time = delivery_time
		self.price = price
		self.threadId = threadId

	@classmethod
	def fromMsg(self, msg):
		msgBody = JSON.loads(msg.body)
		self.src = msgBody['src']
		self.dst = msgBody['dst']
		self.delivery_no = msgBody['delivery_no']
		self.delivery_time = msgBody['delivery_time']
		self.price = msgBody['price']
		self.threadId = msgBody['threadId']
		return self