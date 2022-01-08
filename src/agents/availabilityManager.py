from spade import agent
from typing import Dict
from spade.template import Template
from spade.message import Message
from spade.behaviour import CyclicBehaviour
from common import Performative, getPerformative, setPerformative
from messages.stateReport import StateReport

from aioxmpp.xso.types import JSON, Integer


class AvailabilityManagerAgent(agent.Agent):
    def __init__(self, jid: str, password: str):
        super().__init__(jid, password, verify_security=False)
        self.contents: Dict[str, Dict[str, Integer]] = dict()

    async def setup(self) -> None:
        print("Hello World! I'm agent {}".format(str(self.jid)))
        template = Template()
        setPerformative(template, Performative.Query)
        self.add_behaviour(AvailabilityManagerReportRequestReceiverBehaviour(self), template)

        template = Template()
        template.set_metadata('performative', 'receiveDeliveryFromCarrier')
        self.add_behaviour(WarehouseTransportRecieverBehaviour(self), template)


class AvailabilityManagerReportRequestReceiverBehaviour(CyclicBehaviour):
    def __init__(self, parent: AvailabilityManagerAgent):
        super().__init__()
        self._parent = parent

    async def run(self) -> None:
        msg = await self.receive(timeout=100)
        print('AvailabilityManager received message {}, from {}'.format(msg.id, msg.sender))
        if 'performative' in msg.metadata:
            if getPerformative(msg) == Performative.Query:
                await self.send(self.prepareAvailabilityManagerReportMessage(msg))
        else:
            print("Agent {} Error: no performative in message".format(self.agent.jid))

    def prepareAvailabilityManagerReportMessage(self, msg: Message) -> Message:
        response = Message(to=str(msg.sender), sender=str(self.agent.jid), thread=msg.thread)
        setPerformative(response, Performative.Inform)
        response.body = (StateReport(self._parent.contents)).toJSON()
        return response
