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

from messages.transportProposal import TransportProposal

class OrderManager(agent.Agent):

	class TransportThread:
		def __init__(self, offer: TransportOffer, id: str):
			self.offer = offer
			self.proposals = List[TransportProposal]()
			self.id = id
			self.ended: bool = False
			self.last_update: datetime = None
			self.possible_suppliers = List[str]()

	class RecvTransportRequest(CyclicBehaviour):
		async def run(self) -> None:
			print("OrderManager: Waiting for transport requests")
			ag: OrderManager = self.agent
			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			# TODO: check if that particular message is transportRequest
			if msg:
				newThread = OrderManager.TransportThread(offer = ag.getTransportOffer(msg), id=msg.thread)
				ag.transportThreads.append(newThread)
				self.send(self.agent.generateStateReportRequest())
				print(f"OrderManager requests state report from {ag.availabilityManager}")
			else:
				print("Did not received any transport offers for 100 seconds")

	class RecvTransportOffer(CyclicBehaviour):
		async def run(self) -> None:
			print("OrderManager: Waiting for transport offers")
			ag: OrderManager = self.agent
			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			# TODO: check if that particular message is transportRequest
			if msg:
				newThread = OrderManager.TransportThread(offer = msg, id=msg.thread)
				ag.transportThreads.append(newThread)
				self.send(ag.generateStateReportRequest())
				print(f"OrderManager requests state report from {ag.availabilityManager}")
			else:
				print("Did not received any transport offers for 100 seconds")

	class TryEndAuction(TimeoutBehaviour):
		async def run(self) -> None:
			ag: OrderManager = self.agent
			for thread in ag.transportThreads:
				if not thread.ended and (datetime.now() - thread.last_update) > timedelta(seconds=99):
					thread.ended = True

	class RecvStateReport(OneShotBehaviour):
		async def run(self) -> None:
			print("OrderManager: Waiting for state report")
			ag: OrderManager = self.agent
			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			if msg:
				print(f"OrderManager state report received: {msg.body}")
				print("OrderManager broadcasting transport offers.")
				for thread in ag.transportThreads:
					if len(thread.proposals) < 1:
						thread.possible_suppliers = ag.getPossibleSuppliers(msg)
						thread.last_update = datetime.now()
						for supplier in thread.possible_suppliers:
							offer = deepcopy(thread.offer)
							offer.src = supplier
							for carrier in ag.carriers:
								self.send(ag.generateTransportOffer(to=carrier, offer=offer, threadid=thread.id))

				startAt = datetime.now() + timedelta(seconds=100)
				self.agent.add_behaviour(OrderManager.TryEndAuction(start_at=startAt))
			else:
				print("Did not received any transport offers for 100 seconds")


	class RecvTransportProposals(CyclicBehaviour):
		async def run(self) -> None:
			print("OrderManager: Waiting for transportProposals")
			ag: OrderManager = self.agent
			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			if msg:
				for thread in ag.transportThreads:
					if msg.thread == thread.id:
						thread.proposals.append(TransportProposal(msg.body))
						thread.last_update = datetime.now()
					# thread.proposals.sort(desc=true)
				print(f"OrderManager transport proposal received: {msg.body}")

	class ResolveAuctionBehaviour(PeriodicBehaviour):
		async def run(self) -> None:
			ag: OrderManager = self.agent
			print("OrderManager: Waiting for transportProposals")
			threads : List[OrderManager.TransportThread] = ag.transportThreads
			for thread in threads:
				if thread.ended:
					if len(thread.proposals) < 1:
						thread.ended = False # Fetch proposals and auction again
						continue
				leftProposals, winner = ag.pickBestProposal(thread.proposals)
				thread.proposals = leftProposals
				self.send(ag.generateTransportConfirmationRequest(thread, winner))


	class RecvTransportConfirmation(CyclicBehaviour):
		async def run(self) -> None:
			print("OrderManager: Waiting for TransportConfirmation")

			msg = await self.receive(timeout=100) # wait for a message for 100 seconds
			if msg:
				if msg['metadata']:
					print(f"OrderManager transport proposal received: {msg.body}")


	def __init__(self, jid: str, password: str, capacity: Integer):
		super().__init__(jid, password, verify_security=False)
		self.transportThreads = List[OrderManager.TransportThread]()
		self.carriers = List[str]()


	async def setup(self) -> None:
		print("Initialized OrderManager agent {}".format(str(self.jid)))
		
		recvStateReportTemplate = Template()
		setPerformative(recvStateReportTemplate, Performative.Inform)
		self.add_behaviour(self.RecvStateReport(), recvStateReportTemplate)

		recvTransportRequestTemplate = Template()
		setPerformative(recvTransportRequestTemplate, Performative.Propose)
		self.add_behaviour(self.RecvTransportRequest(), recvTransportRequestTemplate)

		recvTransportOfferTemplate = Template()
		setPerformative(recvTransportOfferTemplate, Performative.Propose)
		self.add_behaviour(self.RecvTransportOffer(), recvTransportOfferTemplate)

		recvTransportProposalTemplate = Template()
		setPerformative(recvTransportProposalTemplate, Performative.Propose)
		self.add_behaviour(self.RecvTransportProposal(), recvTransportProposalTemplate)

		self.add_behaviour(self.RecvTransportConfirmation())

		self.add_behaviour(self.ResolveAuctionBehaviour(period=3))


	def getTransportOffer(self, msg: Message) -> TransportOffer:
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
		setPerformative(msg, Performative.Request)
		return msg

	def generateTransportOffer(self, to: str, offer: TransportOffer, threadid: str) -> Message:
		msg = Message(to = to, thread = threadid, body = offer.toJSON())
		setPerformative(msg, Performative.CFP)
		return msg

	def getPossibleSuppliers(self, msg: Message) -> List[str]:
		msgBody = json.loads(msg.body)
		if msgBody['src']:
			return list(msgBody['src'])
		else:
			# return list(location in msgBody['locations'] if is_close(location, offer.dst))
			return msgBody['locations']

	def pickBestProposal(self, proposals: List[TransportProposal]) -> Tuple[List[TransportProposal], TransportProposal]:
		winner: TransportProposal = None
		for proposal in proposals:
			if not winner:
				winner = proposal
			if proposal.price < winner.price:
				winner = proposal
		leftProposals = [proposal for proposal in proposals if proposal != winner]
		return leftProposals, winner

	def generateTransportConfirmationRequest(self, thread: TransportThread, proposal: Message) -> Message:
		msg = Message()
		msg.to = proposal.sender
		msg.thread = thread.id
		msg.body = TransportConfirmationRequest(thread.offer).toJSON()
		return msg

	class ReceiverBehaviour():
		pass