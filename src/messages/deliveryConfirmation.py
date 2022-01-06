from jsonSerializable import JsonSerializable
from messages.transportProposal import TransportProposal

class DeliveryConfirmation(JsonSerializable):
	def __init__(self, delivered: bool, proposal: TransportProposal) -> None:
		self.delivered = delivered
		self.proposal = proposal