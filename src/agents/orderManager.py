from aioxmpp.xso.types import Integer
from spade import agent

class OrderManager(agent.Agent):

	async def setup(self):
		print("Hello World! I'm agent {}".format(str(self.jid)))

	class RecieverBehaviour():
		pass