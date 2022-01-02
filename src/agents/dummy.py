from spade import agent, message
from spade.behaviour import OneShotBehaviour
from spade.template import Template

class DummyAgent(agent.Agent):
	class InformBehav(OneShotBehaviour):
		async def run(self):
			print("InformBehav running")
			msg = message.Message(to="receiver@localhost")
			msg.set_metadata('performative', 'query')

			await self.send(msg)
			print("Message sent!")

	class RecvBehav(OneShotBehaviour):
		async def run(self):
			print("RecvBehav running")

			msg = await self.receive(timeout=10) # wait for a message for 10 seconds
			if msg:
				print("Message received with content: {}".format(msg.body))
			else:
				print("Did not received any message after 10 seconds")

	async def setup(self):
		print("SenderAgent started")
		b = self.InformBehav()
		self.add_behaviour(b)
		self.add_behaviour(self.RecvBehav(), Template())