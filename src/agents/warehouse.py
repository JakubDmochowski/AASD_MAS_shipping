from typing import Dict
from aioxmpp.xso.types import JSON, Integer
from spade import agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
import json
from messages.warehouseStateReport import WarehouseStateReport

class WarehouseAgent(agent.Agent):

	def __init__(self, jid: str, password: str, capacity: Integer):
		super().__init__(jid, password, verify_security=False)
		self.capacity = capacity
		self.contents: Dict[str, Integer] = dict()

	async def setup(self) -> None:
		print("Hello World! I'm agent {}".format(str(self.jid)))
		template = Template()
		template.set_metadata('performative', 'query')
		self.add_behaviour(WarehouseRecieverBehaviour(self), template)


class WarehouseRecieverBehaviour(OneShotBehaviour):
	def __init__(self, parent: WarehouseAgent):
		super().__init__()
		self._parent = parent

	async def run(self) -> None:
		msg = await self.receive(timeout=100)
		print('Warehouse recieved message {}, from {}'.format(msg.id, msg.sender))
		if 'performative' in msg.metadata:
			if msg.metadata['performative'] == 'query':
				await self.send(self.prepareWarehouseReportMessage(msg))
		else:
			print("Agent {} Error: no performative in message".format(self.agent.jid))

	def prepareWarehouseReportMessage(self, msg: Message) -> Message:
		response = Message(to=str(msg.sender), sender=str(self.agent.jid))
		response.set_metadata('performative', 'info')
		response.body = (WarehouseStateReport(self._parent.contents, self._parent.capacity)).toJSON()
		return response



