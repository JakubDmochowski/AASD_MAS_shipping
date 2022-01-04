from spade import agent
from spade.template import Template
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from messages.shopInventoryReport import shopInventoryReport
from messages.clientOrderRequest import clientOrderRequest
import json

class Shop(agent.Agent):
    def __init__(self, jid: str, password: str,  content, availabilityManJiD):
        super().__init__(jid, password, verify_security=False)
        self.content = content
        self.availabilityManJiD = availabilityManJiD

    async def setup(self):
        print("Hello World! I'm shop {}".format(str(self.jid)))
        shopInverntorytemplate = Template()
        self.add_behaviour(sendInverntoryReport(self), shopInverntorytemplate)

        recvOrderRequestTemplate = Template()
        recvOrderRequestTemplate.set_metadata("performative", "orderRequest")
        self.add_behaviour(RecvTransportRequest(self),recvOrderRequestTemplate)

    def generateInventoryReport(self, to, order) -> Message:
        shopInventoryMsg = Message(to=str(self.availabilityManJiD), sender=str(self.jid))
        shopInventoryMsg.set_metadata("performative", "inventory")
        shopInventoryMsg.body = (shopInventoryReport(self.content)).toJSON()
        return shopInventoryMsg

    def getClientOrderRequest(self, msg) -> clientOrderRequest:
        msgBody = json.loads(msg.body)
        return clientOrderRequest(
            order=msgBody['order']
        )

class sendInverntoryReport(OneShotBehaviour):
    def __init__(self, parent: Shop):
        super().__init__()
        self._parent = parent

    async def run(self):
        print("Sending inventory")
        await self.send(self._parent.generateInventoryReport(to=self._parent.availabilityManJiD,order=self._parent.content))
        print("inventory sent!")

class RecvTransportRequest(CyclicBehaviour):
    def __init__(self, parent: Shop):
        super().__init__()
        self._parent = parent

    async def run(self):
        print("Shop: Waiting for order Request from client")
        msg = await self.receive(timeout=60)
        if msg:
            print("Shop: Received order from client"+str(msg.to))
            clientOrderRequest=self._parent.getClientOrderRequest(msg)
            print(clientOrderRequest.order)
        else:
            print("Did not received any order Request from client for 60 seconds")