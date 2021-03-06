import time
from spade.agent import Agent
from typing import List
from common import dumb_password
from agents.availabilityManager import AvailabilityManagerAgent
from agents.orderManager import OrderManagerAgent
from agents.carrier import CarrierAgent
from agents.producer import ProducerAgent
from agents.warehouse import WarehouseAgent
from agents.shop import ShopAgent
from agents.client import ClientAgent

def prepareAgents() -> List[Agent]:
	return [
		CarrierAgent("carrier1@localhost", dumb_password, 10, True),
		OrderManagerAgent("order@localhost", dumb_password, "availability@localhost", ["carrier1@localhost"]),
		AvailabilityManagerAgent("availability@localhost", dumb_password, "producer@localhost", "warehouse@localhost",
								 "order@localhost"),
		WarehouseAgent("warehouse@localhost", dumb_password, 10, "availability@localhost", {"orange": 20}),
		ShopAgent("shop@localhost", dumb_password, 15, {"apple": 15}, "availability@localhost", "order@localhost"),
		ClientAgent("client@localhost", dumb_password, order={"orange": 5}, shop_name="shop@localhost")

	]

def case2():
	agents = prepareAgents()
	for agent in agents:
		agent.start().result()
	time.sleep(15)
	for agent in agents:
		agent.stop().result()

