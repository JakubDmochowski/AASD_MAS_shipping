from jsonSerializable import JsonSerializable
from messages.transportProposal import TransportProposal

class TransportConfirmationRequest(JsonSerializable):
	def __init__(self, proposal: TransportProposal) -> None:
		self.proposal = proposal
		self.message = "Your transport proposal was accepted. Please confirm the transport contract acceptance."