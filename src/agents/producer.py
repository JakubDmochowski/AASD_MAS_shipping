from spade import agent
from aioxmpp.xso.types import JSON, Integer
from typing import Dict
from spade.template import Template
from spade.message import Message
from spade.behaviour import OneShotBehaviour
from spade.behaviour import PeriodicBehaviour
from common import Performative, getPerformative, setPerformative
from messages.productAvailabilityReport import productAvailabilityReport
from agents.warehouse import WarehousePickupRecieverBehaviour


class ProducerAgent(agent.Agent):

    def __init__(self, jid: str, password: str, capacity: Integer, availabilityManJiD):
        super().__init__(jid, password, verify_security=False)
        self.capacity = capacity
        self.availabilityManJiD = availabilityManJiD
        self.content = {"orange": 5, "apple": 5, "banana": 5, "grapefruit": 5}

    async def setup(self) -> None:
        print("ProducerAgent started {}".format(str(self.jid)))
        template = Template()
        template.set_metadata('performative', 'receiveProductDemand')
        self.add_behaviour(ProducerReceiverBehaviour(self), template)
        self.add_behaviour(ProducerCyclicProductionBehaviour(self, period=0.5))
        self.add_behaviour(ProducerInitialStateReportBehaviour(self))
        transportRecvTemplate = Template()
        transportRecvTemplate.set_metadata('performative', 'receiveDeliveryFromCarrier')
        self.add_behaviour(WarehousePickupRecieverBehaviour(self), transportRecvTemplate)


class ProducerInitialStateReportBehaviour(OneShotBehaviour):
    def __init__(self, parent: ProducerAgent):
        super().__init__()
        self._parent = parent

    async def run(self) -> None:
        await self.send(self.generateProducerAvailabilityReportInitialState())

    def generateProducerAvailabilityReportInitialState(self) -> Message:
        report = Message(to=self._parent.availabilityManJiD, sender=str(self.agent.jid))
        setPerformative(report, Performative.Inform)
        report.body = (productAvailabilityReport(self._parent.content)).toJSON()
        return report


class ProducerCyclicProductionBehaviour(PeriodicBehaviour):
    def __init__(self, parent: ProducerAgent, period: float):
        super().__init__(period=period)
        self._parent = parent

    async def run(self) -> None:
        for key in self._parent.content:
            if self._parent.content[key] < self._parent.capacity:
                self._parent.content[key] += 1
        await self.send(self.generateProducerAvailabilityReportMessage())

    def generateProducerAvailabilityReportMessage(self) -> Message:
        response = Message(to=str(self._parent.availabilityManJiD), sender=str(self.agent.jid))
        setPerformative(response, Performative.Inform)
        response.body = (productAvailabilityReport(self._parent.content)).toJSON()
        return response


class ProducerReceiverBehaviour(OneShotBehaviour):
    def __init__(self, parent: ProducerAgent):
        super().__init__()
        self._parent = parent

    async def run(self) -> None:
        msg = await self.receive(timeout=100)
        if msg:
            print('Producer: message received {}, from {}'.format(msg.id, msg.sender))
            await self.send(self.generateProducerAvailabilityReportMessage(msg))
        else:
            print("Producer: Agent {} Did not received any message".format(self.agent.jid))

    def generateProducerAvailabilityReportMessage(self, msg: Message) -> Message:
        response = Message(to=str(msg.sender), sender=str(self.agent.jid), thread=msg.thread)
        setPerformative(response, Performative.Inform)
        response.body = (productAvailabilityReport(self._parent.content)).toJSON()
        return response
