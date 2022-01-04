from typing import Dict
from jsonSerializable import JsonSerializable

class StateReport(JsonSerializable):
	def __init__(self, price: int, src, dst, contents: Dict[str, int], capacity: int) -> None:
		self.price = price
		self.src = src
		self.dst = dst
		self.contents = contents
		self.capacity = capacity