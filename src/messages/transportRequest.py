from typing import Dict
from jsonSerializable import JsonSerializable

class TransportRequest(JsonSerializable):
	def __init__(self, dst, capacity: int, contents: Dict[str, int]) -> None:
		self.dst = dst
		self.contents = contents
		self.capacity = capacity