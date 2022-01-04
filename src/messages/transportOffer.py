from typing import Dict
from jsonSerializable import JsonSerializable

class TransportOffer(JsonSerializable):
	def __init__(self, src, dst, contents: Dict[str, int], capacity: int, threadId: str) -> None:
		self.src = src
		self.dst = dst
		self.contents = contents
		self.capacity = capacity
		self.threadId = threadId
