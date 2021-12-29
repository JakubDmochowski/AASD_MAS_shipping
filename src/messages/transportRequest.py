from jsonSerializable import JsonSerializable

class TransportRequest(JsonSerializable):
	def __init__(self, fr, to) -> None:
		self.fr = fr
		self.to = to