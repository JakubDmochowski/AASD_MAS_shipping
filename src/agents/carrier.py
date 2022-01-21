import random

from aioxmpp.xso.types import Integer
from spade import agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template
from messages.carrierDeliveryItems import CarrierDeliveryItems

from messages.carrierDetailsReport import CarrierDetailsReport
from messages.deliveryConfirmation import DeliveryConfirmation
from messages.transportConfirmationRequest import TransportConfirmationRequest
from messages.transportContractConfirmation import TransportContractConfirmation
from messages.transportOffer import TransportOffer
from messages.transportProposal import TransportProposal

class CarrierAgent(agent.Agent):
	class RecvDetailsRequestBehav(CyclicBehaviour):
		async def run(self):
			print("Carrier: RecvDetailsRequestBehav running")

			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			if msg:
				print("Carrier: Carrier details request received with content: {}".format(msg.body))
				out = self.agent.generateCarrierDetailsReport(msg)
				await self.send(out)
				print("Carrier: Send carrier details with content: {}".format(out.body))
			else:
				print("Carrier: Did not received any carrier details request after 100 seconds")
	
	class RecvTranspOfferGenerateProposalBehav(CyclicBehaviour):
		async def run(self):
			print("Carrier: RecvTranspOfferGenerateProposalBehav running")

			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			if msg:
				print("Carrier: Transport offer received with content: {}".format(msg.body))
				if msg.body is not None:
					out = self.agent.generateTransportProposal(msg)
					await self.send(out)
					print("Carrier: Send proposal with content: {}".format(out.body))
			else:
				print("Carrier: Did not received any transport offer after 100 seconds")

	class RecvTranspContractGenerateConfirmBehav(CyclicBehaviour):
		async def run(self):
			print("Carrier: RecvTranspContractGenerateConfirmBehav running")

			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			if msg:
				print("Carrier: Transport contract received with content: {}".format(msg.body))
				out = self.agent.generateTransportConfirmation(msg)
				await self.send(out)
				print("Carrier: Send contract confirmation with content: {}".format(out.body))
				self.agent.add_behaviour(self.agent.ReceiveProductBehav())
			else:
				print("Carrier: Did not received any transport contract after 100 seconds")

	class RecvTranspOfferResolved(CyclicBehaviour):
		async def run(self):
			print("Carrier: RecvTranspContractGenerateConfirmBehav running")

			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			if msg:
				print("Carrier: Transport offer resolved msg received with content: {}".format(msg.body))
				await self.send(self.agent.generateACK(msg))
			else:
				print("Carrier: Did not received transport offer resolved after 100 seconds")
	
	class DeliveryConfirmationBehav(OneShotBehaviour):
		async def run(self):
			for manager, proposal in self.agent.handledOffers.items():
				msg = Message(to=manager)
				msg.set_metadata('performative', 'info')
				msg.body = (DeliveryConfirmation(True, proposal)).toJSON()
				await self.send(msg)
				print("Carrier: Product delivered from {} to {}".format(proposal.offer.src, proposal.offer.dst))
				del self.agent.handledOffers[manager]

	class ReceiveProductBehav(OneShotBehaviour):
		async def run(self):
			print("Carrier: ReceiveProductBehav running")

			for _, proposal in self.agent.handledOffers.items():
				msg = Message(to=proposal.offer.src)
				msg.set_metadata('performative', 'confirm')
				msg.set_metadata('protocol', 'giveDeliveryToCarrier')
				msg.body = (CarrierDeliveryItems(proposal.offer.contents)).toJSON()
				await self.send(msg)

				msg = await self.receive(timeout=100) # wait for a message for 100 seconds
				if msg and msg["protocol"] == "orderFromShopToCarrier":
					print("Carrier: Delivery started, product taken from source!: {}".format(msg.body))
					self.agent.add_behaviour(self.agent.DeliverProductBehav())
				else:
					print("Carrier: Did not received delivery products")

	
	class DeliverProductBehav(OneShotBehaviour):
		async def run(self):
			print("Carrier: DeliverProductBehav running")

			for _, proposal in self.agent.handledOffers.items():
				msg = Message(to=proposal.offer.dst)
				msg.set_metadata('performative', 'request')
				msg.set_metadata('protocol', 'receiveDeliveryFromCarrier')
				msg.body = (CarrierDeliveryItems(proposal.offer.contents)).toJSON()
				await self.send(msg)

				msg = await self.receive(timeout=100) # wait for a message for 100 seconds
				if msg and msg["protocol"] == "receiveDeliveryFromCarrier":
					print("Carrier: Delivery ended, product delivered to destination!; {}".format(msg.body))
					self.agent.add_behaviour(self.agent.DeliveryConfirmationBehav())
				else:
					print("Carrier: Did not received delivery products")

	def __init__(self, jid: str, password: str, load_capacity: Integer, availability: bool):
		super().__init__(jid, password, verify_security=False)
		self.handledTransports = dict()
		self.load_capacity = load_capacity
		self.availability = availability
		self.delivery_count = 0
	
	async def setup(self):
		print("CarrierAgent started: {}".format(str(self.jid)))
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
		proposalMsg.body = (TransportProposal(offer, self.delivery_count, random.randint(50, 100))).toJSON()
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
		contract = TransportConfirmationRequest()
		contract.fromJSON(msg.body)
		confirmMsg.body = (TransportContractConfirmation(contract.proposal)).toJSON()

		self.handledTransports[msg.sender] = contract.proposal
		return confirmMsg
	
	def generateACK(self, msg: Message) -> Message:
		ackMsg = Message(to=str(msg.sender), sender=str(self.jid))
		ackMsg.set_metadata("performative", "inform")
		ackMsg.body = "{}"
		return ackMsg
