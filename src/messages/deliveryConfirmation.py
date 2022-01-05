from jsonSerializable import JsonSerializable

class DeliveryConfirmation(JsonSerializable):
	def __init__(self, delivered: bool) -> None:
		self.delivered = delivered