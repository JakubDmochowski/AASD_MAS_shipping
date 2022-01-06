from jsonSerializable import JsonSerializable
from messages.transportProposal import TransportProposal

class TransportContractConfirmation(JsonSerializable):
	def __init__(self, proposal: TransportProposal = None) -> None:
		self.proposal = proposal
		self.message = "Your transport contract was accepted."