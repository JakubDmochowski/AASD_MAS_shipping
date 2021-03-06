from jsonSerializable import JsonSerializable
from messages.transportOffer import TransportOffer
from messages.transportProposal import TransportProposal

class TransportConfirmationRequest(JsonSerializable):
	def __init__(self, proposal: TransportProposal = None) -> None:
		self.proposal = proposal
		self.message = "Your transport proposal was accepted. Please confirm the transport contract acceptance."
	