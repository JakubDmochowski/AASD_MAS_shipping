import time
from spade.agent import Agent
from typing import List
from common import dumb_password
from agents.availabilityManager import AvailabilityManagerAgent
from agents.orderManager import OrderManagerAgent
from agents.carrier import CarrierAgent
from agents.shop import ShopAgent
from agents.client import ClientAgent
from agents.warehouse import WarehouseAgent
from agents.producer import ProducerAgent


def prepareAgents() -> List[Agent]:
	return [
		CarrierAgent("carrier1@localhost", dumb_password, 10, True),
		AvailabilityManagerAgent("availability@localhost", dumb_password, "producer@localhost", "warehouse@localhost",
								 "order@localhost"),
		OrderManagerAgent("order@localhost", dumb_password, "availability@localhost", ["carrier1@localhost"]),
		WarehouseAgent("warehouse@localhost", dumb_password, 10, "availability@localhost", {"orange": 1}),
		ShopAgent("shop1@localhost", dumb_password, 50, {}, "availability@localhost", "order@localhost"),
		ShopAgent("shop2@localhost", dumb_password, 50, {}, "availability@localhost", "order@localhost"),
		ClientAgent("client1@localhost", dumb_password,order={"orange": 10}, shop_name="student2@localhost" ),
		ClientAgent("client2@localhost", dumb_password,order={"orange": 10}, shop_name="student2@localhost" ),
		ProducerAgent("producer@localhost", dumb_password, 40, "availability@localhost")

	]

def case1():
	agents = prepareAgents()
	for agent in agents:
		agent.start().result()
	time.sleep(15)
	for agent in agents:
		agent.stop().result()
