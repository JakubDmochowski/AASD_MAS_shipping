import time
from spade.agent import Agent
from typing import List
from agents.producer import ProducerAgent
from agents.availabilityManager import AvailabilityManagerAgent
from agents.orderManager import OrderManagerAgent
from agents.carrier import CarrierAgent
from agents.Shop import ShopAgent
from agents.warehouse import WarehouseAgent
from common import dumb_password

def prepareAgents() -> List[Agent]:
	return [
		CarrierAgent("carrier@localhost", dumb_password, 40, True),
		AvailabilityManagerAgent("availability@localhost", dumb_password, "producer@localhost", "warehouse@localhost",
								 "order@localhost"),
		OrderManagerAgent("order@localhost", dumb_password, "availability@localhost", ["carrier@localhost"]),
    	WarehouseAgent("warehouse@localhost", dumb_password, 500, "availability@localhost",
					   {"orange": 200, "apple": 100, "banana": 100, "grapefruit": 100}),
    	ShopAgent("shop@localhost", dumb_password, 100, {"orange": 50}, "availability@localhost", "order@localhost"),
		ProducerAgent("producer@localhost", dumb_password, 40, "availability@localhost"),
	]

def case4():
	agents = prepareAgents()
	for agent in agents:
		agent.start().result()
	time.sleep(15)
	for agent in agents:
		agent.stop().result()
