from typing import Dict
from aioxmpp.xso.types import Integer
from spade import agent
from spade.behaviour import CyclicBehaviour
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
from common import Performative, getPerformative, setPerformative
from messages.carrierDeliveryItems import CarrierDeliveryItems
from messages.warehouseStateReport import WarehouseStateReport

class WarehouseAgent(agent.Agent):

    def __init__(self, jid: str, password: str, capacity: Integer, availabilityManJiD,
                 content: Dict[str, Integer]):
        super().__init__(jid, password, verify_security=False)
        self.capacity = capacity
        self.availabilityManJiD = availabilityManJiD
        self.content = content

    async def setup(self) -> None:
        print("WerehouseAgent started: {}".format(str(self.jid)))

        self.add_behaviour(WarehouseInitialStateReportBehaviour(self))

        template = Template()
        template.set_metadata('performative', 'receiveDeliveryFromCarrier')
        self.add_behaviour(WarehouseTransportRecieverBehaviour(self), template)

    def addItems(self, items: Dict[str, Integer]):
        # todo: ensure there is capacity
        for key, value in items.items():
            if key in self.content:
                self.content[key] = 0
            self.content[key] = self.content[key] + value

    def takeItems(self, items: Dict[str, Integer]):
        # todo: ensure there is capacity
        for key, value in items.items():
            if key in self.content:
                self.content[key] = 0
            self.content[key] = self.content[key] - value


class WarehouseInitialStateReportBehaviour(OneShotBehaviour):
    def __init__(self, parent: WarehouseAgent):
        super().__init__()
        self._parent = parent

    async def run(self) -> None:
        await self.send(self.prepareWarehouseReportMessage())

    def prepareWarehouseReportMessage(self) -> Message:
        report = Message(to=self._parent.availabilityManJiD, sender=str(self.agent.jid))
        setPerformative(report, Performative.Inform)
        report.body = (WarehouseStateReport(self._parent.content, self._parent.capacity)).toJSON()
        return report


class WarehouseTransportRecieverBehaviour(CyclicBehaviour):
    def __init__(self, parent: WarehouseAgent):
        super().__init__()
        self._parent = parent

    async def run(self) -> None:
        msg = await self.receive(timeout=100)
        if not msg:
            return
        print('Warehouse: recieved message {}, from {}'.format(msg.id, msg.sender))

        if msg.get_metadata('performative') == 'receiveDeliveryFromCarrier':
            items = CarrierDeliveryItems({})
            items.fromMsg(msg)
            self._parent.addItems(items.content)
            reply = Message(to=str(msg.sender), body='ok')
            setPerformative(reply, Performative.Inform)
            await self.send(msg)
            await self.send(WarehousePickupRecieverBehaviour.prepareWarehouseReportMessage())


class WarehousePickupRecieverBehaviour(CyclicBehaviour):
    def __init__(self, parent: WarehouseAgent):
        super().__init__()
        self._parent = parent

    async def run(self) -> None:
        msg = await self.receive(timeout=100)
        if not msg:
            return
        print('Warehouse: recieved message {}, from {}'.format(msg.id, msg.sender))

        if msg.get_metadata('performative') == 'giveDeliveryToCarrier':
            items = CarrierDeliveryItems({})
            items.fromMsg(msg)
            self._parent.takeItems(items.content)
            await self.send(self.prepareWarehouseReportMessage())

    def prepareWarehouseReportMessage(self) -> Message:
        response = Message(to=str(self._parent.availabilityManJiD), sender=str(self.agent.jid), thread=msg.thread)
        setPerformative(response, Performative.Inform)
        response.body = (WarehouseStateReport(self._parent.content, self._parent.capacity)).toJSON()
        return response
