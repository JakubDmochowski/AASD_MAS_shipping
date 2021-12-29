from jsonSerializable import JsonSerializable


class TransportOffer(JsonSerializable):
	def __init__(self, price: int) -> None:
		self.price = price