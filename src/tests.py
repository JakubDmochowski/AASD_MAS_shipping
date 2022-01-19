from asyncio.tasks import wait
import time
import unittest
from unittest.case import TestCase
from spade import agent
from spade import message

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
from agents.orderManager import OrderManager

from agents.warehouse import WarehouseAgent
from common import Performative, setPerformative
from messages.warehouseStateReport import WarehouseStateReport

class DummyAgent(agent.Agent):
	class InformBehav(OneShotBehaviour):
		async def run(self) -> None:
			print("InformBehav running")
			msg = Message(to="receiver@localhost")
			setPerformative(msg, Performative.Query)

			await self.send(msg)
			print("Message sent!")

	class RecvBehav(OneShotBehaviour):
		async def run(self) -> None:
			msg = await self.receive(timeout=1000) # wait for a message for 10 seconds
			test: TestCase = self.agent.test
			test.assertTrue(msg)
			body = WarehouseStateReport()
			body.fromJSON(msg.body)
			test.assertTrue(body.freeCapacity == 15)
			test.assertDictEqual(body.contents, {})
			await self.agent.stop()


	async def setup(self) -> None:
		print("SenderAgent started")
		self.add_behaviour(self.RecvBehav(), Template())
		b = self.InformBehav()
		self.add_behaviour(b)
	def __init__(self, jid: str, password: str, test: unittest.TestCase, verify_security: bool = False):
		super().__init__(jid, password, verify_security=verify_security)
		self.test = test

class WarehouseTests(unittest.TestCase):

	def test_WHEN_AskedForStateReportWhileEmpty_THEN_ProducesReport(self):
		warehouse = WarehouseAgent("receiver@localhost", "bb", capacity=15)
		warehouse.start().result()
		dummy = DummyAgent("a@localhost", "b", self)
		
		dummy.start().result()
		while(dummy.is_alive()):
			time.sleep(0.1)
		
		pass

class OrderManagerTests(unittest.TestCase):
	def test_WHEN_RequestedToTransport_THEN_SendsMessagesToCarriers(self):
		orderManager = OrderManager("manager@localhost", "a")
		orderManager.start().result()
		

if __name__ == '__main__':
	unittest.main()
