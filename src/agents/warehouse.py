from typing import Dict
from aioxmpp.xso.types import Integer
from spade import agent

class WarehouseAgent(agent.Agent):

	def __init__(self, jid: str, password: str, capacity: Integer):
		super().__init__(jid, password, verify_security=False)
		self._capacity = capacity
		self._contents = Dict()

	async def setup(self):
		print("Hello World! I'm agent {}".format(str(self.jid)))

	class RecieverBehaviour():
		pass