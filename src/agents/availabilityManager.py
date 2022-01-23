import json
from typing import Dict, List

from aioxmpp.xso.types import Integer
from spade import agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
from spade.message import Message
from spade.template import Template

from agents.warehouse import WarehouseTransportRecieverBehaviour
from common import Performative, getPerformative, setPerformative
from messages.stateReport import StateReport
from messages.transportRequest import TransportRequest


class AvailabilityManagerAgent(agent.Agent):
    def __init__(self, jid: str, password: str, producerJiD, warehouseJiD, orderJiD, shopJiDs: List[str] = list()):
        super().__init__(jid, password, verify_security=False)
        self.producerJiD = producerJiD
        self.warehouseJiD = warehouseJiD
        self.orderJiD = orderJiD
        self.shopJiDs = shopJiDs
        self.state: Dict[str, Dict[str, Integer]] = dict()

    async def setup(self) -> None:
        print("AvailabilityManagerAgent started: {}".format(str(self.jid)))

        transportRecvTemplate = Template()
        transportRecvTemplate.set_metadata('performative', 'receiveDeliveryFromCarrier')
        self.add_behaviour(WarehouseTransportRecieverBehaviour(self), transportRecvTemplate)

        recvStateReportTemplate = Template()
        setPerformative(recvStateReportTemplate, Performative.Inform)
        self.add_behaviour(AvailabilityManagerHandleStateReportsBehaviour(self), recvStateReportTemplate)

        self.add_behaviour(OptimizeSuppliersStateBehaviour(self, period=5))


class AvailabilityManagerHandleStateReportsBehaviour(CyclicBehaviour):
    def __init__(self, parent: AvailabilityManagerAgent):
        super().__init__()
        self._parent = parent

    async def run(self) -> None:
        msg = await self.receive(timeout=100)
        self._parent.state[msg.sender.localpart] = json.loads(msg.body)['content']
        await self.send(self.prepareAvailabilityManagerReportMessage(msg))
        print('AvailabilityManager: received message {}, from {} state {}'.format(msg.id, msg.sender,
                                                                                  self._parent.state))

    def prepareAvailabilityManagerReportMessage(self, msg: Message) -> Message:
        response = Message(to=str(self._parent.orderJiD), sender=str(self.agent.jid), thread=msg.thread)
        setPerformative(response, Performative.Inform)
        response.body = (StateReport(self._parent.state)).toJSON()
        return response


class OptimizeSuppliersStateBehaviour(PeriodicBehaviour):
    def __init__(self, parent: AvailabilityManagerAgent, period: float):
        super().__init__(period=period)
        self._parent = parent

    async def run(self) -> None:
        warehouseProducts = self._parent.state.get(self._parent.warehouseJiD)
        producerProducts = self._parent.state.get(self._parent.producerJiD)
        if warehouseProducts and producerProducts:
            for product in warehouseProducts:
                if warehouseProducts[product] < 4 and producerProducts[product] > 1:
                    await self.send(self.generateTransportRequest(self._parent.orderJiD, {product: 1}))

    def generateTransportRequest(self, to, order) -> Message:
        supplierTranportRequestMsg = Message(to=str(to), sender=str(self.jid))
        supplierTranportRequestMsg.set_metadata("performative", Performative.Request.value)
        supplierTranportRequestMsg.body = (TransportRequest(dst=self.jid, capacity=1, contents=order)).toJSON()
        return supplierTranportRequestMsg
