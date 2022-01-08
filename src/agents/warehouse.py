from typing import Dict
from aioxmpp.xso.types import Integer
from spade import agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
from common import Performative, getPerformative, setPerformative
from messages.carrierDeliveryItems import CarrierDeliveryItems
from messages.warehouseStateReport import WarehouseStateReport

class WarehouseAgent(agent.Agent):

	def __init__(self, jid: str, password: str, capacity: Integer):
		super().__init__(jid, password, verify_security=False)
		self.capacity = capacity
		self.contents: Dict[str, Integer] = dict()

	async def setup(self) -> None:
		print("Hello World! I'm agent {}".format(str(self.jid)))
		template = Template()
		setPerformative(template, Performative.Query)
		self.add_behaviour(WarehouseReportRequestRecieverBehaviour(self), template)

		template = Template()
		template.set_metadata('performative', 'receiveDeliveryFromCarrier')
		self.add_behaviour(WarehouseTransportRecieverBehaviour(self), template)

	def addItems(self, items: Dict[str, Integer]):
		#todo: ensure there is capacity
		for key, value in items.items():
			if key in self.contents:
				self.contents[key] = 0
			self.contents[key] = self.contents[key] + value

	def takeItems(self, items: Dict[str, Integer]):
		#todo: ensure there is capacity
		for key, value in items.items():
			if key in self.contents:
				self.contents[key] = 0
			self.contents[key] = self.contents[key] - value


class WarehouseReportRequestRecieverBehaviour(CyclicBehaviour):
	def __init__(self, parent: WarehouseAgent):
		super().__init__()
		self._parent = parent

	async def run(self) -> None:
		msg = await self.receive(timeout=100)
		if not msg:
			return
		print('Warehouse recieved message {}, from {}'.format(msg.id, msg.sender))
		if 'performative' in msg.metadata:
			if getPerformative(msg) == Performative.Query:
				await self.send(self.prepareWarehouseReportMessage(msg))
		else:
			print("Agent {} Error: no performative in message".format(self.agent.jid))

	def prepareWarehouseReportMessage(self, msg: Message) -> Message:
		response = Message(to=str(msg.sender), sender=str(self.agent.jid), thread=msg.thread)
		setPerformative(response, Performative.Inform)
		response.body = (WarehouseStateReport(self._parent.contents, self._parent.capacity)).toJSON()
		return response

class WarehouseTransportRecieverBehaviour(CyclicBehaviour):
	def __init__(self, parent: WarehouseAgent):
		super().__init__()
		self._parent = parent

	async def run(self) -> None:
		msg = await self.receive(timeout=100)
		if not msg:
			return
		print('Warehouse recieved message {}, from {}'.format(msg.id, msg.sender))
		
		if msg.get_metadata('performative') == 'receiveDeliveryFromCarrier':
			items = CarrierDeliveryItems({})
			items.fromMsg(msg)
			self._parent.addItems(items.content)
			reply = Message(to= str(msg.sender), body='ok')
			setPerformative(reply, Performative.Inform)
			await self.send(msg)
		

	def prepareWarehouseReportMessage(self, msg: Message) -> Message:
		response = Message(to=str(msg.sender), sender=str(self.agent.jid), thread=msg.thread)
		setPerformative(response, Performative.Inform)
		response.body = (WarehouseStateReport(self._parent.contents, self._parent.capacity)).toJSON()
		return response

class WarehousePickupRecieverBehaviour(CyclicBehaviour):
	def __init__(self, parent: WarehouseAgent):
		super().__init__()
		self._parent = parent

	async def run(self) -> None:
		msg = await self.receive(timeout=100)
		if not msg:
			return
		print('Warehouse recieved message {}, from {}'.format(msg.id, msg.sender))
		
		if msg.get_metadata('performative') == 'giveDeliveryToCarrier':
			items = CarrierDeliveryItems({})
			items.fromMsg(msg)
			self._parent.takeItems(items.content)
		

	def prepareWarehouseReportMessage(self, msg: Message) -> Message:
		response = Message(to=str(msg.sender), sender=str(self.agent.jid), thread=msg.thread)
		setPerformative(response, Performative.Inform)
		response.body = (WarehouseStateReport(self._parent.contents, self._parent.capacity)).toJSON()
		return response

