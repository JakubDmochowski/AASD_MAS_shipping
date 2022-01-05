from spade import agent
from spade.template import Template
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from messages.shopInventoryReport import shopInventoryReport
from messages.clientOrderRequest import clientOrderRequest
from messages.transportRequest import TransportRequest
from common import Performative
import json

class Shop(agent.Agent):
    def __init__(self, jid: str, password: str,  content, availabilityManJiD,orderManJiD):
        super().__init__(jid, password, verify_security=False)
        self.content = content
        self.availabilityManJiD = availabilityManJiD
        self.orderManJiD=orderManJiD
        self.clients_orders = {}

    async def setup(self):
        print("Hello World! I'm shop {}".format(str(self.jid)))
        shopInverntorytemplate = Template()
        self.add_behaviour(sendInverntoryReport(self), shopInverntorytemplate)

        recvOrderRequestTemplate = Template()
        recvOrderRequestTemplate.set_metadata("performative", "orderRequest")
        self.add_behaviour(RecvTransportRequest(self),recvOrderRequestTemplate)

    def generateInventoryReport(self, to, order) -> Message:
        shopInventoryMsg = Message(to=str(to), sender=str(self.jid))
        shopInventoryMsg.set_metadata("performative", "inventory")
        shopInventoryMsg.body = (shopInventoryReport(order)).toJSON()
        return shopInventoryMsg

    def generateTransportRequest(self, to,order) -> Message:
        shopTranportRequestMsg = Message(to=str(to), sender=str(self.jid))
        shopTranportRequestMsg.set_metadata("performative",Performative.Request.value)
        shopTranportRequestMsg.body =(TransportRequest(dst=self.jid, capacity=1, contents=order)).toJSON()
        return shopTranportRequestMsg

    def generateOrderReadToPickInfo(self, to) -> Message:
        shopInventoryMsg = Message(to=str(to), sender=str(self.jid))
        shopInventoryMsg.set_metadata("performative", "orderReadyToPick")
        shopInventoryMsg.body = "Order ready to pick"
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
        #print("Shop: Waiting for order Request from client")
        msg = await self.receive(timeout=1)
        if msg:
            change=0
            print("Shop: Received order from client"+str(msg.sender))
            clientOrderRequest=self._parent.getClientOrderRequest(msg)
            print(clientOrderRequest.order)
            missing_products={}
            #Check whether shop has all the products
            for product in clientOrderRequest.order:
                if product in self._parent.content:
                    if self._parent.content[product]<clientOrderRequest.order[product]:
                        if self._parent.content[product]!=0:
                            change = 1
                        #jezeli czesc jest na stocku
                        missing_products[product] = clientOrderRequest.order[product]-self._parent.content[product]
                    else:
                        self._parent.content[product]=self._parent.content[product]-clientOrderRequest.order[product]
                else:
                    missing_products[product] = clientOrderRequest.order[product]
            #response to client
            if not missing_products:
                # all item already there
                print("Shop: Client's  order is ready to pick up")
                await self.send(self._parent.generateOrderReadToPickInfo(to=msg.sender))
                print("Sending inventory")
                await self.send(self._parent.generateInventoryReport(to=self._parent.availabilityManJiD,
                                                                     order=self._parent.content))
                print("inventory sent!")
            else:
                # some products are mising
                self._parent.clients_orders[msg.sender] = missing_products
                if change:
                    await self.send(self._parent.generateInventoryReport(to=self._parent.availabilityManJiD,
                                                                     order=self._parent.content))
                    print("inventory sent!")
                await self.send(self._parent.generateTransportRequest(to=self._parent.orderManJiD,
                                                                     order=self._parent.clients_orders[msg.sender]))
                print("Shop: transport request sent")
                # TODO monitor deliveries
                #sprawdzenie czy mozna zakonczyc zamówienie klienta
                #jezeli dostawa zmienia stan magazynu send -> inventory report

        #else:
            #print("Did not received any order Request from client for 60 seconds")