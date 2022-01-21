from spade import agent
from aioxmpp.xso.types import JSON, Integer
from typing import Dict
from spade.template import Template
from spade.message import Message
from spade.behaviour import OneShotBehaviour
from common import Performative, getPerformative, setPerformative
from messages.productAvailabilityReport import productAvailabilityReport


class ProducerAgent(agent.Agent):

    def __init__(self, jid: str, password: str, capacity: Integer, contents: Dict[str, Integer], availabilityManJiD):
        super().__init__(jid, password, verify_security=False)
        self.capacity = capacity
        self.availabilityManJiD = availabilityManJiD
        if contents:
            self.contents = contents
        else:
            self.contents: Dict[str, Integer] = dict()

    async def setup(self) -> None:
        print("ProducerAgent started {}".format(str(self.jid)))
        template = Template()
        template.set_metadata('performative', 'receiveProductDemand')
        self.add_behaviour(ProducerReceiverBehaviour(self), template)

        self.add_behaviour(ProducerInitialStateReportBehaviour(self))

class ProducerInitialStateReportBehaviour(OneShotBehaviour):
    def __init__(self, parent: ProducerAgent):
        super().__init__()
        self._parent = parent

    async def run(self) -> None:
        self.generateProducerAvailabilityReportInitialState()

    def generateProducerAvailabilityReportInitialState(self) -> Message:
        report = Message(to=self._parent.availabilityManJiD, sender=str(self.agent.jid))
        setPerformative(report, Performative.Inform)
        report.body = (productAvailabilityReport(self._parent.capacity, self._parent.contents))

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
        response.body = (productAvailabilityReport(self._parent.capacity, self._parent.contents)).toJSON()
        return response
