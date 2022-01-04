from jsonSerializable import JsonSerializable

class TransportRequest(JsonSerializable):
	def __init__(self, dst, capacity: int, contents: dict) -> None:
		self.dst = dst
		self.contents = contents
		self.capacity = capacity