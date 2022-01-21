from spade import agent, message
from spade.behaviour import OneShotBehaviour
from spade.template import Template

from common import Performative, setPerformative
from messages.transportOffer import TransportOffer

class DummyAgent(agent.Agent):
	class InformBehav(OneShotBehaviour):
		async def run(self) -> None:
			print("Dummy: InformBehav running")
			msg = message.Message(to="receiver@localhost")
			setPerformative(msg, Performative.Query)

			await self.send(msg)

			offer = message.Message(to="carrier@localhost")
			offer.set_metadata("performative", "cfp")
			offer.body = (TransportOffer("a", "b", {}, 5, "1")).toJSON()

			await self.send(offer)
			print("Dummy: Message sent!")

	class RecvBehav(OneShotBehaviour):
		async def run(self) -> None:
			print("Dummy: RecvBehav running")

			msg = await self.receive(timeout=10) # wait for a message for 10 seconds
			if msg:
				print("Dummy: Message received with content: {}".format(msg.body))
			else:
				print("Dummy: Did not received any message after 10 seconds")

	async def setup(self) -> None:
		print("DummyAgent started: {}".format(str(self.jid)))
		b = self.InformBehav()
		self.add_behaviour(b)
		self.add_behaviour(self.RecvBehav(), Template())