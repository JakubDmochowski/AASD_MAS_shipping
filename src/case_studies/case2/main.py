from spade import quit_spade
import time
from spade.agent import Agent
from typing import List
from agents.availabilityManager import AvailabilityManagerAgent
from agents.orderManager import OrderManager
from agents.carrier import CarrierAgent
from agents.producer import ProducerAgent
from agents.warehouse import WarehouseAgent
from common import dumb_password

def prepareAgents() -> List[Agent]:
	producer = ProducerAgent("producer@localhost", dumb_password, 15)
	return [
		WarehouseAgent("warehouse@localhost", dumb_password, 10, {"orange", 20}),
		AvailabilityManagerAgent("availability@localhost", dumb_password),
		OrderManager("order@localhost", dumb_password),
		CarrierAgent("carrier1@localhost", dumb_password, 10, True),
		producer
	]



def case2():
	agents = prepareAgents()
	for agent in agents:
		agent.start().result()
	time.sleep(5)
	for agent in agents:
		agent.stop().result()

