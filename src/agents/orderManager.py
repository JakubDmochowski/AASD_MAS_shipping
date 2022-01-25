from typing import List, Tuple
from aioxmpp.xso.types import JSON, Integer
from spade import agent
from copy import deepcopy
from spade.message import Message
from spade.template import Template
from spade.behaviour import OneShotBehaviour, CyclicBehaviour, PeriodicBehaviour, TimeoutBehaviour
from common import Performative, setPerformative
from messages.transportConfirmationRequest import TransportConfirmationRequest
from messages.transportOffer import TransportOffer 
import json
from datetime import datetime, timedelta
import uuid

from messages.transportProposal import TransportProposal

class OrderManagerAgent(agent.Agent):
	class CarrierTransportProposal:
		def __init__ (self, proposal: TransportProposal, msg: Message):
			self.proposal = proposal
			self.msg = msg

	class TransportThread:
		def __init__(self, offer: TransportOffer, id: str):
			self.offer = offer
			self.proposals: List[CarrierTransportProposal] = list()
			self.id = id
			self.ended: bool = False
			self.last_update: datetime = datetime.now()
			self.possible_suppliers: List[str] = list()

	class RecvTransportRequest(CyclicBehaviour):
		async def run(self) -> None:
			print("OrderManager: Waiting for transport requests")
			ag: OrderManagerAgent = self.agent
			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			# TODO: check if that particular message is transportRequest
			if msg:
				threadId = msg.thread if msg.thread != None else str(uuid.uuid4())
				newThread = OrderManagerAgent.TransportThread(offer = ag.getTransportOffer(msg), id=threadId)
				ag.transportThreads.append(newThread)
				await self.send(ag.generateStateReportRequest(threadId))
				print(f"OrderManager: requests state report from {ag.availabilityManagerJID}")
			else:
				print("OrderManager: Did not received any transport offers for 100 seconds")

	class RecvTransportOffer(CyclicBehaviour):
		async def run(self) -> None:
			print("OrderManager: Waiting for transport offers")
			ag: OrderManagerAgent = self.agent
			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			# TODO: check if that particular message is transportRequest
			if msg:
				newThread = OrderManagerAgent.TransportThread(offer = msg, id=msg.thread)
				ag.transportThreads.append(newThread)
				await self.send(ag.generateStateReportRequest(msg.thread))
				print(f"OrderManager: requests state report from {ag.availabilityManagerJID}")
			else:
				print("Did not received any transport offers for 100 seconds")

	class TryEndAuction(TimeoutBehaviour):
		async def run(self) -> None:
			ag: OrderManagerAgent = self.agent
			print("OrderManager: trying to end auction")
			for thread in ag.transportThreads:
				if not thread.ended and (datetime.now() - thread.last_update) > timedelta(seconds=1):
					thread.ended = True

	class RecvStateReport(OneShotBehaviour):
		async def run(self) -> None:
			print("OrderManager: Waiting for state report")
			ag: OrderManagerAgent = self.agent
			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			if msg:
				print(f"OrderManager: state report received: {msg.body}")
				print("OrderManager: starting auction")
				for thread in ag.transportThreads:
					if len(thread.proposals) < 1:
						thread.possible_suppliers = ag.getPossibleSuppliers(msg)
						print("OrderManager: broadcasting transport offers.")
						thread.last_update = datetime.now()
						for supplier in thread.possible_suppliers:
							offer = deepcopy(thread.offer)
							offer.src = supplier
							print(ag.carriers)
							for carrier in ag.carriers:
								print(f"OrderManager: sending transport offer to {carrier}")
								await self.send(ag.generateTransportOffer(to=carrier, offer=offer, threadid=thread.id))
				startAt = datetime.now() + timedelta(seconds=2)
				print(f"OrderManager: ending auction at {startAt}")
				self.agent.add_behaviour(OrderManagerAgent.TryEndAuction(start_at=startAt))
			else:
				print("OrderManager: Did not received any transport offers for 100 seconds")

	class RecvTransportProposals(CyclicBehaviour):
		async def run(self) -> None:
			print("OrderManager: Waiting for transportProposals")
			ag: OrderManagerAgent = self.agent
			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			if msg:
				for thread in ag.transportThreads:
					if msg.thread == thread.id:
						proposal = TransportProposal()
						proposal.fromJSON(msg.body)
						carrierProposal = OrderManagerAgent.CarrierTransportProposal(proposal, msg)
						thread.proposals.append(carrierProposal)
						print(f"OrderManager: Appending proposal to thread {thread.id}. Count {len(thread.proposals)}")
						thread.last_update = datetime.now()
					# thread.proposals.sort(desc=true)
				print(f"OrderManager: transport proposal received: {msg.body}")

	class ResolveAuctionBehaviour(PeriodicBehaviour):
		async def run(self) -> None:
			ag: OrderManagerAgent = self.agent
			threads: List[OrderManagerAgent.TransportThread] = ag.transportThreads
			for thread in threads:
				if thread.ended is not True:
					continue
				print(f"OrderManager: trying to resolve thread {thread.id}")
				print(thread.proposals)
				if len(thread.proposals) < 1:
					print("OrderManager: thread has not enough proposals; retrying auction")
					thread.ended = False # Fetch proposals and auction again
					continue
				print("OrderManager: resolve auction")
				leftProposals, winner = ag.pickBestProposal(thread.proposals)
				print(f"OrderManager: auction winner: {winner.msg.sender}")
				thread.proposals = leftProposals
				await self.send(ag.generateTransportConfirmationRequest(thread, winner))

	class RecvTransportConfirmation(CyclicBehaviour):
		async def run(self) -> None:
			print("OrderManager: Waiting for TransportConfirmation")

			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			if msg:
				print(f"OrderManager: transport confirmation received: {msg.body}")

	def __init__(self, jid: str, password: str, availabilityManagerJID, carriers: List[TransportThread] = list()):
		super().__init__(jid, password, verify_security=False)
		self.transportThreads: List[OrderManagerAgent.TransportThread] = list()
		self.carriers = carriers
		self.availabilityManagerJID = availabilityManagerJID

	async def setup(self) -> None:
		print("OrderManagerAgent started: {}".format(str(self.jid)))
		
		recvStateReportTemplate = Template()
		setPerformative(recvStateReportTemplate, Performative.Inform)
		self.add_behaviour(self.RecvStateReport(), recvStateReportTemplate)

		recvTransportOfferTemplate = Template()
		setPerformative(recvTransportOfferTemplate, Performative.Request)
		recvTransportOfferTemplate.sender = self.availabilityManagerJID
		self.add_behaviour(self.RecvTransportOffer(), recvTransportOfferTemplate)

		recvTransportRequestTemplate = Template()
		setPerformative(recvTransportRequestTemplate, Performative.Request)
		self.add_behaviour(self.RecvTransportRequest(), recvTransportRequestTemplate & ~recvTransportOfferTemplate)

		recvTransportProposalTemplate = Template()
		setPerformative(recvTransportProposalTemplate, Performative.Propose)
		self.add_behaviour(self.RecvTransportProposals(), recvTransportProposalTemplate)

		transportConfirmationTemplate = Template()
		setPerformative(transportConfirmationTemplate, Performative.Confirm)
		self.add_behaviour(self.RecvTransportConfirmation(), transportConfirmationTemplate)

		self.add_behaviour(self.ResolveAuctionBehaviour(period=3))

	def getTransportOffer(self, msg: Message) -> TransportOffer:
		msgBody = json.loads(msg.body)
		return TransportOffer(
			dst = msgBody['dst'],
			contents = msgBody['contents'],
			capacity = msgBody['capacity']
		)

	def generateStateReportRequest(self, threadId: str) -> Message:
		msg = Message()
		msg.to = self.availabilityManagerJID
		msg.thread = threadId
		msg.body = "Request state report"
		setPerformative(msg, Performative.Request)
		return msg

	def generateTransportOffer(self, to: str, offer: TransportOffer, threadid: str) -> Message:
		msg = Message(to = to, thread = threadid, body = offer.toJSON())
		setPerformative(msg, Performative.CFP)
		return msg

	def getPossibleSuppliers(self, msg: Message) -> List[str]:
		msgBody = json.loads(msg.body)
		if "src" in msgBody.keys():
			return list(msgBody.src)
		else:
			# return list(location in msgBody['locations'] if is_close(location, offer.dst))
			transportThread = next((thread for thread in self.transportThreads if thread.id == msg.thread), None)
			requestSrc = transportThread.offer.dst
			return [location for location in msgBody['state'].keys() if location != requestSrc]

	def pickBestProposal(self, proposals: List[CarrierTransportProposal]) -> Tuple[List[CarrierTransportProposal], CarrierTransportProposal]:
		winner: CarrierTransportProposal = None
		for carrierProposal in proposals:
			if not winner or carrierProposal.proposal.price < winner.proposal.price:
				winner = carrierProposal
		leftProposals = [proposal for proposal in proposals if proposal != winner]
		return leftProposals, winner

	def generateTransportConfirmationRequest(self, thread: TransportThread, carrierProposal: CarrierTransportProposal) -> Message:
		msg = Message()
		msg.to = str(carrierProposal.msg.sender)
		msg.thread = thread.id
		setPerformative(msg, Performative.AcceptProposal)
		msg.body = TransportConfirmationRequest(carrierProposal.proposal).toJSON()
		return msg
