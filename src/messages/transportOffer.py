from jsonSerializable import JsonSerializable

class TransportOffer(JsonSerializable):
	def __init__(self, price: int, src, dst, contents: dict, capacity: int) -> None:
		self.price = price
		self.src = src
		self.dst = dst
		self.contents = contents
		self.capacity = capacity