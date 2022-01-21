from spade import quit_spade
import time
from spade.agent import Agent
from typing import List
from agents.availabilityManager import AvailabilityManagerAgent
from agents.orderManager import OrderManagerAgent
from agents.carrier import CarrierAgent
from agents.shop import ShopAgent
from agents.client import ClientAgent
from agents.warehouse import WarehouseAgent
from common import dumb_password

def prepareAgents() -> List[Agent]:
	return [
		CarrierAgent("carrier1@localhost", dumb_password, 50, True),
		CarrierAgent("carrier2@localhost", dumb_password, 30, True),
		WarehouseAgent("warehouse@localhost", dumb_password, 20, {"orange": 15, "apple": 20}),
		AvailabilityManagerAgent("availability@localhost", dumb_password),
		OrderManagerAgent("order@localhost", dumb_password),
		ShopAgent("shop@localhost", dumb_password, 50, {"orange": 15}, "availability@localhost", "order@localhost"),
		ClientAgent("client@localhost", dumb_password, order={"orange": 10, "apple": 2}, shop_name="shop@localhost" )
	]



def case3():
	agents = prepareAgents()
	for agent in agents:
		agent.start().result()
	time.sleep(15)
	for agent in agents:
		agent.stop().result()
