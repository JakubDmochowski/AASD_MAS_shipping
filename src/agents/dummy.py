from spade import agent, message
from spade.behaviour import OneShotBehaviour
from spade.template import Template

from common import Performative, setPerformative
from messages.transportOffer import TransportOffer

class DummyAgent(agent.Agent):
	class InformBehav(OneShotBehaviour):
		async def run(self) -> None:
			print("InformBehav running")
			msg = message.Message(to="receiver@localhost")
			setPerformative(msg, Performative.Query)

			await self.send(msg)

			offer = message.Message(to="carrier@localhost")
			offer.set_metadata("performative", "cfp")
			offer.body = (TransportOffer(5, "a", "b", {}, 5)).toJSON()

			await self.send(offer)
			await self.send(offer)
			print("Message sent!")

	class RecvBehav(OneShotBehaviour):
		async def run(self) -> None:
			print("RecvBehav running")

			msg = await self.receive(timeout=10) # wait for a message for 10 seconds
			if msg:
				print("Message received with content: {}".format(msg.body))
			else:
				print("Did not received any message after 10 seconds")

	async def setup(self) -> None:
		print("SenderAgent started")
		b = self.InformBehav()
		self.add_behaviour(b)
		self.add_behaviour(self.RecvBehav(), Template())