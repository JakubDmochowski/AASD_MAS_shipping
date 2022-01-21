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
	shop1 = Shop("shop1@localhost", dumb_password, {}, "availability@localhost", "order@localhost")
	shop2 = Shop("shop2@localhost", dumb_password, {}, "availability@localhost", "order@localhost")
	order = {"orange": 10}
	client1 = Client("client1@localhost", dumb_password,order, shop_name="student2@localhost" )
	client2 = Client("client1@localhost", dumb_password,order, shop_name="student2@localhost" )
	return [
		CarrierAgent("carrier1@localhost", dumb_password, 10, True),
		WarehouseAgent("warehouse@localhost", dumb_password, 10, {"orange", 20}),
		AvailabilityManagerAgent("availability@localhost", dumb_password),
		OrderManager("order@localhost", dumb_password),
		shop1,
		shop2,
		client1,
		client2
	]



def case1():
	agents = prepareAgents()
	for agent in agents:
		agent.start().result()
	time.sleep(15)
	for agent in agents:
		agent.stop().result()
