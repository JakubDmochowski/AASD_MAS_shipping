from spade import quit_spade
import time
from spade.agent import Agent
from typing import List
from agents.availabilityManager import AvailabilityManagerAgent
from agents.orderManager import OrderManager
from agents.carrier import CarrierAgent
from agents.shop import Shop
from agents.client import Client
from agents.warehouse import WarehouseAgent
from common import dumb_password

def prepareAgents() -> List[Agent]:
	shop = Shop("shop@localhost", dumb_password, {"orange": 15}, "availability@localhost", "order@localhost")
	order = {"orange": 10, "apple": 2}
	client = Client("client@localhost", dumb_password, order, shop_name="shop@localhost" )
	return [
		CarrierAgent("carrier1@localhost", dumb_password, 50, True),
        CarrierAgent("carrier2@localhost", dumb_password, 30, True),
		WarehouseAgent("warehouse@localhost", dumb_password, 20, {"orange": 15, "apple": 20}),
		AvailabilityManagerAgent("availability@localhost", dumb_password),
		OrderManager("order@localhost", dumb_password),
		shop,
		client,
	]



def case3():
	agents = prepareAgents()
	for agent in agents:
		agent.start().result()
	time.sleep(15)
	for agent in agents:
		agent.stop().result()
