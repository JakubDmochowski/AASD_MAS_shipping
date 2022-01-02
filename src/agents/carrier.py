from typing import Dict
from aioxmpp.xso.types import JSON, Integer
from spade import agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
import json
from messages.carrierDetailsReport import CarrierDetailsReport

class CarrierAgent(agent.Agent):
	class RecvDetailsRequestBehav(OneShotBehaviour):
		async def run(self):
			print("RecvDetailsRequestBehav running")

			msg = await self.receive(timeout=100) # wait for a message for 10 seconds
			if msg:
				print("Message received with content: {}".format(msg.body))
				await self.send(self.agent.generateCarrierDetailsReport(msg))
			else:
				print("Did not received any message after 100 seconds")
	
	class RecvTranspOfferGenerateProposalBehav(OneShotBehaviour):
		async def run(self):
			print("RecvTranspOfferGenerateProposalBehav running")

			msg = await self.receive(timeout=100) # wait for a message for 10 seconds
			if msg:
				print("Message received with content: {}".format(msg.body))
				await self.send(self.agent.generateTransportProposal(msg))
			else:
				print("Did not received any message after 100 seconds")

	class RecvTranspContractGenerateConfirmBehav(OneShotBehaviour):
		async def run(self):
			print("RecvTranspContractGenerateConfirmBehav running")

			msg = await self.receive(timeout=100) # wait for a message for 10 seconds
			if msg:
				print("Message received with content: {}".format(msg.body))
				await self.send(self.agent.generateTransportConfirmation(msg))
			else:
				print("Did not received any message after 100 seconds")

	class RecvTranspOfferResolved(OneShotBehaviour):
		async def run(self):
			print("RecvTranspContractGenerateConfirmBehav running")

			msg = await self.receive(timeout=100) # wait for a message for 10 seconds
			if msg:
				print("Message received with content: {}".format(msg.body))
				await self.send(self.agent.generateACK(msg))
			else:
				print("Did not received any message after 100 seconds")
	
	# # TODO: this should be more like a state in FSM than OneShotBehaviour
	# class DeliveryConfirmationBehav(OneShotBehaviour):
    # 	async def run(self):
	# 		print("RecvTranspOfferGenerateProposalBehav running")

	# 		msg = await self.receive(timeout=100) # wait for a message for 10 seconds
	# 		if msg:
	# 			print("Message received with content: {}".format(msg.body))
	# 			await self.send(self.agent.generateTransportProposal(msg))
	# 		else:
	# 			print("Did not received any message after 100 seconds")	


	def __init__(self, jid: str, password: str, load_capacity: Integer, availability: bool):
		super().__init__(jid, password, verify_security=False)
		self.load_capacity = load_capacity
		self.availability = availability
	
	async def setup(self):
		print("CarrierAgent started")
		carrier_details_request = Template()
		carrier_details_request.set_metadata("performative", "query")
		self.add_behaviour(self.RecvBehav(), carrier_details_request)

		transportOffer = Template()
		transportOffer.set_metadata("performative", "cfp") # TODO: set sender to Order manager jid
		self.add_behaviour(self.RecvTranspOfferGenerateProposalBehav, transportOffer)

		transportContract = Template()
		transportContract.set_metadata("performative", "accept-proposal") # TODO: set sender to Order manager jid
		self.add_behaviour(self.RecvTranspContractGenerateConfirmBehav, transportContract)

		offerResolved = Template()
		offerResolved.set_metadata("performative", "refuse-proposal") # TODO: set sender to Order manager jid
		self.add_behaviour(self.RecvTranspOfferResolved, offerResolved)

	def generateCarrierDetailsReport(self, msg: Message) -> Message:
		reportMsg = Message(to=str(msg.sender), sender=str(self.agent.jid))
		reportMsg.set_metadata("performative", "info")
		reportMsg.body = (CarrierDetailsReport(self.load_capacity, self.availability)).toJSON()
		return reportMsg

	def generateTransportProposal(self, msg: Message) -> Message:
		proposalMsg = Message(to=str(msg.sender), sender=str(self.agent.jid))
		proposalMsg.set_metadata("performative", "propose")
		# TODO fill proposal's content based on the received offer
		return proposalMsg

	def generateTransportConfirmation(self, msg: Message) -> Message:
		confirmMsg = Message(to=str(msg.sender), sender=str(self.agent.jid))
		confirmMsg.set_metadata("performative", "confirm")
		# TODO fill confirmation's content based on the received contract
		return confirmMsg
	
	def generateACK(self, msg: Message) -> Message:
		ackMsg = Message(to=str(msg.sender), sender=str(self.agent.jid))
		ackMsg.set_metadata("performative", "inform")
		ackMsg.body = "{}"
		return ackMsg
