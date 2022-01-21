import time
from spade.agent import Agent
from typing import List
from agents.availabilityManager import AvailabilityManagerAgent
from agents.orderManager import OrderManagerAgent
from agents.carrier import CarrierAgent
from agents.producer import ProducerAgent
from agents.warehouse import WarehouseAgent
from common import dumb_password

def prepareAgents() -> List[Agent]:
	return [
		CarrierAgent("carrier1@localhost", dumb_password, 10, True),
		WarehouseAgent("warehouse@localhost", dumb_password, 10, {"orange", 20}),
		AvailabilityManagerAgent("availability@localhost", dumb_password),
		OrderManagerAgent("order@localhost", dumb_password),
		ProducerAgent("producer@localhost", dumb_password, 15, {}, "availability@localhost")
	]



def case2():
	agents = prepareAgents()
	for agent in agents:
		agent.start().result()
	time.sleep(15)
	for agent in agents:
		agent.stop().result()

