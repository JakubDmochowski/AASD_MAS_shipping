from jsonSerializable import JsonSerializable
from messages.transportOffer import TransportOffer

class TransportConfirmationRequest(JsonSerializable):
	def __init__(self, offer: TransportOffer) -> None:
		self.offer = offer
		self.message = "Your transport proposal was accepted. Please confirm the transport contract acceptance."