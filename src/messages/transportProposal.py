import json
from jsonSerializable import JsonSerializable

class TransportProposal(JsonSerializable):
	@classmethod
	def fromJson(cls, j: str) -> TransportProposal:
		result = TransportProposal(0, '')
		result.__dict__ = json.loads(j)
		return result

	def __init__(self, price: int, threadId: str) -> None:
		self.threadId = threadId
		self.price = price
