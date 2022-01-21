from spade import agent
from typing import Dict
from spade.template import Template
from spade.message import Message
from spade.behaviour import CyclicBehaviour
from agents.warehouse import WarehouseTransportRecieverBehaviour
from common import Performative, getPerformative, setPerformative
from messages.stateReport import StateReport

from aioxmpp.xso.types import JSON, Integer


class AvailabilityManagerAgent(agent.Agent):
	def __init__(self, jid: str, password: str):
		super().__init__(jid, password, verify_security=False)
		self.state: Dict[str, Dict[str, Integer]] = dict()

	async def setup(self) -> None:
		print("AvailabilityManagerAgent started: {}".format(str(self.jid)))
		reportRequestRecvTemplate = Template()
		setPerformative(reportRequestRecvTemplate, Performative.Query)
		self.add_behaviour(AvailabilityManagerReportRequestReceiverBehaviour(self), reportRequestRecvTemplate)

		transportRecvTemplate = Template()
		transportRecvTemplate.set_metadata('performative', 'receiveDeliveryFromCarrier')
		self.add_behaviour(WarehouseTransportRecieverBehaviour(self), transportRecvTemplate)

		recvStateReportTemplate = Template()
		setPerformative(recvStateReportTemplate, Performative.Inform)
		self.add_behaviour(AvailabilityManagerProducerReportRecvBehaviour(self), recvStateReportTemplate)

class AvailabilityManagerProducerReportRecvBehaviour(CyclicBehaviour):
	def __init__(self, parent: AvailabilityManagerAgent):
		super().__init__()
		self._parent = parent

	async def run(self) -> None:
		msg = await self.receive(timeout=100)
		if not msg:
			return
		print('AvailabilityManager: received message {}, from {}'.format(msg.id, msg.sender))
		# TODO: handle this msg -> should receive ProducerReport 
		# and save its state in the self.states dictionary;
		# create transport of products from producer
		# if msg contents are not empty (products are available to pick up)
		# otherwise do nothing
		

class AvailabilityManagerReportRequestReceiverBehaviour(CyclicBehaviour):
	def __init__(self, parent: AvailabilityManagerAgent):
		super().__init__()
		self._parent = parent

	async def run(self) -> None:
		msg = await self.receive(timeout=100)
		print('AvailabilityManager: received message {}, from {}'.format(msg.id, msg.sender))
		if 'performative' in msg.metadata:
			if getPerformative(msg) == Performative.Query:
				await self.send(self.prepareAvailabilityManagerReportMessage(msg))
		else:
			print("AvailabilityManager {} Error: no performative in message".format(self.agent.jid))

	def prepareAvailabilityManagerReportMessage(self, msg: Message) -> Message:
		response = Message(to=str(msg.sender), sender=str(self.agent.jid), thread=msg.thread)
		setPerformative(response, Performative.Inform)
		response.body = (StateReport(self._parent.state)).toJSON()
		return response
