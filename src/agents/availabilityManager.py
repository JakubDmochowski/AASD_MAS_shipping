import json

from typing import Dict, List
from aioxmpp.xso.types import Integer
from spade import agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

from agents.warehouse import WarehouseTransportRecieverBehaviour
from common import Performative, getPerformative, setPerformative
from messages.stateReport import StateReport
from messages.transportOffer import TransportOffer


class AvailabilityManagerAgent(agent.Agent):
    def __init__(self, jid: str, password: str, producerJiD, warehouseJiD, orderJiD):
        super().__init__(jid, password, verify_security=False)
        self.producerJiD = producerJiD
        self.warehouseJiD = warehouseJiD
        self.orderJiD = orderJiD
        self.state: Dict[str, Dict[str, Integer]] = dict()

    async def setup(self) -> None:
        print("AvailabilityManagerAgent started: {}".format(str(self.jid)))

        transportRecvTemplate = Template()
        transportRecvTemplate.set_metadata('performative', 'receiveDeliveryFromCarrier')
        self.add_behaviour(WarehouseTransportRecieverBehaviour(self), transportRecvTemplate)

        recvStateReportTemplate = Template()
        setPerformative(recvStateReportTemplate, Performative.Inform)
        self.add_behaviour(AvailabilityManagerHandleStateReportsBehaviour(self), recvStateReportTemplate)


class AvailabilityManagerHandleStateReportsBehaviour(CyclicBehaviour):
    def __init__(self, parent: AvailabilityManagerAgent):
        super().__init__()
        self._parent = parent

    async def run(self) -> None:
        msg = await self.receive(timeout=100)
        print('AvailabilityManager: received message {}, from {} state {}'.format(msg.id, msg.sender,
                                                                                  self._parent.state))
        if msg.sender.__str__() not in self._parent.state or \
                self._parent.state[msg.sender.__str__()] != json.loads(msg.body)['content']:
            self._parent.state[msg.sender.__str__()] = json.loads(msg.body)['content']
            if bool(self._parent.producerJiD and self._parent.warehouseJiD) and \
                    ("producer" in msg.sender.localpart or "warehouse" in msg.sender.localpart):
                products = self.prepareProductsForDelivery()
                if bool(products):
                    await self.send(self.generateTransportOffer(self._parent.orderJiD, self._parent.producerJiD,
                                                                self._parent.warehouseJiD, 1, products))
        await self.send(self.prepareAvailabilityManagerReportMessage(msg))

    def prepareAvailabilityManagerReportMessage(self, msg: Message) -> Message:
        response = Message(to=str(self._parent.orderJiD), sender=str(self.agent.jid), thread=msg.thread)
        setPerformative(response, Performative.Inform)
        response.body = (StateReport(self._parent.state)).toJSON()
        return response

    def prepareProductsForDelivery(self):
        warehouseProducts = self._parent.state.get(self._parent.warehouseJiD)
        producerProducts = self._parent.state.get(self._parent.producerJiD)
        productsToBeDelivered = {}
        if warehouseProducts and producerProducts:
            for product in warehouseProducts:
                if warehouseProducts[product] < 4 and producerProducts[product] > 1:
                    productsToBeDelivered = {product: 1}

        return productsToBeDelivered

    def generateTransportOffer(self, to, src, dst, capacity, order) -> Message:
        supplierTranportOfferMsg = Message(to=str(to), sender=str(self._parent.jid))
        supplierTranportOfferMsg.set_metadata("performative", Performative.Request.value)
        supplierTranportOfferMsg.body = (TransportOffer(src=src, dst=dst,
                                                        capacity=capacity, contents=order)).toJSON()
        return supplierTranportOfferMsg
