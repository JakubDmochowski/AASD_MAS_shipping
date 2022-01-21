from spade import quit_spade
import time
from spade.agent import Agent
from typing import List
from agents.producer import Producer
from agents.availabilityManager import AvailabilityManagerAgent
from agents.orderManager import OrderManager
from agents.carrier import CarrierAgent
from agents.shop import Shop
from agents.client import Client
from agents.warehouse import WarehouseAgent
from common import dumb_password

def prepareAgents() -> List[Agent]:
	return [
    WarehouseAgent("warehouse@localhost", dumb_password, 500, {"orange": 200, "apple": 100, "banana": 100, "grapefruit": 100}),
		AvailabilityManagerAgent("availability@localhost", dumb_password),
		OrderManager("order@localhost", dumb_password),
		CarrierAgent("carrier@localhost", dumb_password, 40, True),
    Shop("shop@localhost", dumb_password, 100, {"orange": 50}, "availability@localhost", "order@localhost"),
		Producer("producer@localhost", dumb_password, 40, {"apple": 40}),
	]

def case4():
	agents = prepareAgents()
	for agent in agents:
		agent.start().result()
	time.sleep(5)
	for agent in agents:
		agent.stop().result()
