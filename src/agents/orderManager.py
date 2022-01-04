from aioxmpp.xso.types import Integer
from spade import agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from messages.transportOffer import TransportOffer 
import json
from datetime import datetime, timedelta

class OrderManager(agent.Agent):

	class TransportThread:
		def __init__(self, offer: TransportOffer, id: str):
			self.offer = None
			self.proposals = [] # messages
			self.id = id
			self.ended = False
			self.last_update = None

	class RecvTransportRequest(CyclicBehaviour):
		async def run(self):
			print("OrderManager: Waiting for transport requests")

			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			# TODO: check if that particular message is transportRequest
			if msg:
				newThread = TransportThread(offer = self.agent.getTransportOffer(msg), id=msg.thread)
				self.agent.transportThreads.append(newThread)
				self.send(self.agent.generateStateReportRequest())
				print(f"OrderManager requests state report from {self.agent.availabilityManager}"))
			else:
				print("Did not received any transport offers for 100 seconds")

	class RecvTransportOffer(CyclicBehaviour):
		async def run(self):
			print("OrderManager: Waiting for transport offers")

			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			# TODO: check if that particular message is transportRequest
			if msg:
				newThread = TransportThread(offer = msg, id=msg.thread)
				self.agent.transportThreads.append(newThread)
				self.send(self.agent.generateStateReportRequest())
				print(f"OrderManager requests state report from {self.agent.availabilityManager}"))
			else:
				print("Did not received any transport offers for 100 seconds")

	class TryEndAuction(TimeoutBehaviour):
		async def run(self):
			for thread in transportThreads if not thread.ended and datetime.now() - thread.last_update > timedelta(seconds=99)
				thread.ended = True

	class RecvStateReport(OneShotBehaviour):
		async def run(self):
			print("OrderManager: Waiting for state report")

			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			if msg:
				print(f"OrderManager state report received: {msg.body}")
				print("OrderManager broadcasting transport offers.")
				for thread in self.transportThreads if len(thread.proposals) < 1:
					thread.possible_suppliers = self.getPossibleSuppliers(msg)
					thread.last_update = datetime.now()
					for supplier in thread.possible_suppliers:
						offer = clone(thread.offer)
						offer.src = supplier
						for carrier in self.agent.carriers:
							self.send(self.agent.generateTransportOffer(to=carrier, offer=offer, threadid=thread.id))

				startAt = datetime.datetime.now() + datetime.timedelta(seconds=100)
				self.agent.add_behaviour(TryEndAuction(start_at=startAt))
			else:
				print("Did not received any transport offers for 100 seconds")


	class RecvTransportProposals(CyclicBehaviour):
		async def run(self):
			print("OrderManager: Waiting for transportProposals")

			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			if msg:
				for thread in self.transportThreads if msg.thread === thread.id:
					thread.proposals.append(msg)
					thread.last_update = datetime.now()
					# thread.proposals.sort(desc=true)
				print(f"OrderManager transport proposal received: {msg.body}")

	class ResolveAuctionBehaviour(PeriodicBehaviour):
		async def run(self):
			print("OrderManager: Waiting for transportProposals")

			for thread in self.transportThreads if thread.ended is True:
				if len(thread.proposals) < 1:
					thread.ended = False # Fetch proposals and auction again
					continue
				leftProposals, winner = self.agent.pickBestProposal(thread.proposals)
				thread.proposals = leftProposals
				self.send(self.agent.generateTransportConfirmationRequest(thread, winner))


	class RecvTransportConfirmation(CyclicBehaviour):
		async def run(self):
			print("OrderManager: Waiting for TransportConfirmation")

			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			if msg:
				if msg['metadata']
				print(f"OrderManager transport proposal received: {msg.body}")
				

	def __init__(self, jid: str, password: str, capacity: Integer):
		super().__init__(jid, password, verify_security=False)
		self.transportThreads = []


	async def setup(self):
		print("Initialized OrderManager agent {}".format(str(self.jid)))
		
		recvStateReportTemplate = Template()
		recvStateReportTemplate.set_metadata("performative", "inform")
		self.add_behaviour(self.RecvStateReport(), recvStateReportTemplate)

		recvTransportRequestTemplate = Template()
		recvTransportRequestTemplate.set_metadata("performative", "propose")
		self.add_behaviour(self.RecvTransportRequest(), recvTransportRequestTemplate)

		recvTransportOfferTemplate = Template()
		recvTransportOfferTemplate.set_metadata("performative", "propose")
		self.add_behaviour(self.RecvTransportOffer(), recvTransportOfferTemplate)

		recvTransportProposalTemplate = Template()
		recvTransportProposalTemplate.set_metadata("performative", "propose")
		self.add_behaviour(self.RecvTransportProposal(), recvTransportProposalTemplate)

		self.add_behaviour(self.RecvTransportConfirmation())

		self.add_behaviour(self.ResolveAuctionBehaviour(period=3))


	def getTransportOffer(self, msg) -> TransportOffer:
		msgBody = json.loads(msg['body'])
		return TransportOffer(
			dst = msgBody['dst'],
			contents = msgBody['contents'],
			capacity = msgBody['capacity']
		)

	def generateStateReportRequest(self) -> Message:
		msg = Message()
		msg.to = self.agent.availabilityManager
		msg.body = "Request state report"
		msg.set_metadata("performative", "request")
		return msg

	def generateTransportOffer(self, to, offer, threadid) -> Message:
		msg = Message()
		msg.to = to
		msg.body = json.dumps(offer)
		msg.thread = threadid
		msg.set_metadata("performative", "cfp")
		return msg

	def getPossibleSuppliers(self, msg, offer) -> list:
		msgBody = json.loads(msg['body'])
		if msgBody['src']:
			return list(msgBody['src'])
		else:
			# return list(location in msgBody['locations'] if is_close(location, offer.dst))
			return msgBody['locations']

	def pickBestProposal(self, proposals) -> tuple:
		winner = None
		for proposal in proposals:
			if not winner:
				winner = proposal
			if proposal.price < winner.price:
				winner = proposal
		leftProposals = [proposal in proposals if proposal != winner]
		return leftProposals, winner

	def generateTransportConfirmationRequest(self, thread, proposal) -> Message:
		msg = Message()
		msg.to = proposal.sender
		msg.thread = thread.id
		msg.body = json.dumps({
			message: "Your transport proposal was accepted. Please confirm the transport contract acceptance.",
			offer: thread.offer,
		})
		return msg

	class ReceiverBehaviour():
		pass