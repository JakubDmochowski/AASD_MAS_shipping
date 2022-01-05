import datetime
import json
from typing import Dict
from aioxmpp.xso.types import JSON, Integer
from spade import agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour, PeriodicBehaviour
from spade.message import Message
from spade.template import Template

from messages.carrierDetailsReport import CarrierDetailsReport
from messages.deliveryConfirmation import DeliveryConfirmation
from messages.transportOffer import TransportOffer
from messages.transportProposal import TransportProposal

class CarrierAgent(agent.Agent):
	class RecvDetailsRequestBehav(CyclicBehaviour):
		async def run(self):
			print("RecvDetailsRequestBehav running")

			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			if msg:
				print("Carrier details request received with content: {}".format(msg.body))
				out = self.agent.generateCarrierDetailsReport(msg)
				await self.send(out)
				print("Send carrier details with content: {}".format(out.body))
			else:
				print("Did not received any carrier details request after 100 seconds")
	
	class RecvTranspOfferGenerateProposalBehav(CyclicBehaviour):
		async def run(self):
			print("RecvTranspOfferGenerateProposalBehav running")

			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			if msg:
				print("Transport offer received with content: {}".format(msg.body))
				if msg.body is not None:
					out = self.agent.generateTransportProposal(msg)
					await self.send(out)
					print("Send proposal with content: {}".format(out.body))
			else:
				print("Did not received any transport offer after 100 seconds")

	class RecvTranspContractGenerateConfirmBehav(CyclicBehaviour):
		async def run(self):
			print("RecvTranspContractGenerateConfirmBehav running")

			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			if msg:
				print("Transport contract received with content: {}".format(msg.body))
				out = self.agent.generateTransportConfirmation(msg)
				await self.send(out)
				print("Send contract confirmation with content: {}".format(out.body))

				startAt = datetime.datetime.now() + datetime.timedelta(seconds=100)
				self.agent.add_behaviour(self.agent.DeliveryConfirmationBehav(startAt=startAt))
			else:
				print("Did not received any transport contract after 100 seconds")

	class RecvTranspOfferResolved(CyclicBehaviour):
		async def run(self):
			print("RecvTranspContractGenerateConfirmBehav running")

			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			if msg:
				print("Transport offer resolved msg received with content: {}".format(msg.body))
				await self.send(self.agent.generateACK(msg))
			else:
				print("Did not received transport offer resolved after 100 seconds")
	
	class DeliveryConfirmationBehav(PeriodicBehaviour):
		async def run(self):
			print("DeliveryConfirmationBehav running")

			msg = Message(to="receiver@localhost")
			msg.set_metadata('performative', 'info')
			msg.body = (DeliveryConfirmation(True)).toJSON()
			await self.send(msg)
			print("Delivery confirmation sent!")


	def __init__(self, jid: str, password: str, load_capacity: Integer, availability: bool):
		super().__init__(jid, password, verify_security=False)
		self.load_capacity = load_capacity
		self.availability = availability
		self.delivery_count = 0
	
	async def setup(self):
		print("CarrierAgent started")
		carrier_details_request = Template()
		carrier_details_request.set_metadata("performative", "query")
		self.add_behaviour(self.RecvDetailsRequestBehav(), carrier_details_request)

		transportOffer = Template()
		transportOffer.set_metadata("performative", "cfp") # TODO: set sender to Order manager jid
		self.add_behaviour(self.RecvTranspOfferGenerateProposalBehav(), transportOffer)

		transportContract = Template()
		transportContract.set_metadata("performative", "accept-proposal") # TODO: set sender to Order manager jid
		self.add_behaviour(self.RecvTranspContractGenerateConfirmBehav(), transportContract)

		offerResolved = Template()
		offerResolved.set_metadata("performative", "refuse-proposal") # TODO: set sender to Order manager jid
		self.add_behaviour(self.RecvTranspOfferResolved(), offerResolved)

	def generateTransportProposal(self, msg: Message) -> Message:
		proposalMsg = Message(to=str(msg.sender), sender=str(self.jid))
		proposalMsg.set_metadata("performative", "propose")
		offer = TransportOffer()
		offer.fromJSON(msg.body)
		proposalMsg.body = (TransportProposal(offer.src, offer.dst, self.delivery_count, "", offer.price, offer.threadId)).toJSON()
		self.delivery_count += 1
		return proposalMsg

	def generateCarrierDetailsReport(self, msg: Message) -> Message:
		reportMsg = Message(to=str(msg.sender), sender=str(self.jid))
		reportMsg.set_metadata("performative", "info")
		reportMsg.body = (CarrierDetailsReport(self.load_capacity, self.availability)).toJSON()
		return reportMsg

	def generateTransportConfirmation(self, msg: Message) -> Message:
		confirmMsg = Message(to=str(msg.sender), sender=str(self.jid))
		confirmMsg.set_metadata("performative", "confirm")
		# contract = json.loads(msg.body)
		# TODO fill confirmation's content based on the received contract
		return confirmMsg
	
	def generateACK(self, msg: Message) -> Message:
		ackMsg = Message(to=str(msg.sender), sender=str(self.jid))
		ackMsg.set_metadata("performative", "inform")
		ackMsg.body = "{}"
		return ackMsg
