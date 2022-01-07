from spade import agent
from spade.template import Template
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from messages.shopInventoryReport import shopInventoryReport
from messages.carrierDeliveryItems import CarrierDeliveryItems
from messages.clientOrderRequest import clientOrderRequest
from messages.transportRequest import TransportRequest
from common import Performative
import json


class Shop(agent.Agent):
    def __init__(self, jid: str, password: str, content, availabilityManJiD, orderManJiD):
        super().__init__(jid, password, verify_security=False)
        self.content = content
        self.availabilityManJiD = availabilityManJiD
        self.orderManJiD = orderManJiD
        self.clients_orders = {}

    async def setup(self):
        print("Hello World! I'm shop {}".format(str(self.jid)))
        shopInverntorytemplate = Template()
        self.add_behaviour(sendInverntoryReport(self), shopInverntorytemplate)

        recvOrderRequestTemplate = Template()
        recvOrderRequestTemplate.set_metadata("performative", "request")
        recvOrderRequestTemplate.set_metadata("protocol", "orderRequest")
        self.add_behaviour(RecvOrderRequest(self), recvOrderRequestTemplate)

        recvDeliveryTemplate = Template()
        recvDeliveryTemplate.set_metadata("performative", "request")
        recvDeliveryTemplate.set_metadata("protocol", "receiveDeliveryFromCarrier")
        self.add_behaviour(RecvDelivery(self), recvDeliveryTemplate)

        giveDeliveryTemplate = Template()
        giveDeliveryTemplate.set_metadata("performative", "confirm")
        giveDeliveryTemplate.set_metadata("protocol", "giveDeliveryToCarrier")
        self.add_behaviour(GiveDelivery(self), giveDeliveryTemplate)

    def generateInventoryReport(self, to, order) -> Message:
        shopInventoryMsg = Message(to=str(to), sender=str(self.jid))
        shopInventoryMsg.set_metadata("performative", "inform")
        shopInventoryMsg.body = (shopInventoryReport(order)).toJSON()
        return shopInventoryMsg

    def generateTransportRequest(self, to, order) -> Message:
        shopTranportRequestMsg = Message(to=str(to), sender=str(self.jid))
        shopTranportRequestMsg.set_metadata("performative", Performative.Request.value)
        shopTranportRequestMsg.body = (TransportRequest(dst=self.jid, capacity=1, contents=order)).toJSON()
        return shopTranportRequestMsg

    def generateOrderReadToPickInfo(self, to) -> Message:
        shopInventoryMsg = Message(to=str(to), sender=str(self.jid))
        shopInventoryMsg.set_metadata("performative", "inform")
        shopInventoryMsg.set_metadata("protocol", "orderReadyToPick")
        shopInventoryMsg.body = "Order ready to pick"
        return shopInventoryMsg

    def generateOrderForCarrier(self, to, content) -> Message:
        OrderForCarrierMsg = Message(to=str(to), sender=str(self.jid))
        OrderForCarrierMsg.set_metadata("performative", "confirm")
        OrderForCarrierMsg.set_metadata("protocol", "orderFromShopToCarrier")
        OrderForCarrierMsg.body = (CarrierDeliveryItems(content)).toJSON()
        return OrderForCarrierMsg

    def generateDeliveryReceiveConfirm(self, to, content) -> Message:
        ReceivedFromCarrierMsg = Message(to=str(to), sender=str(self.jid))
        ReceivedFromCarrierMsg.set_metadata("performative", "confirm")
        ReceivedFromCarrierMsg.set_metadata("protocol", "receiveDeliveryFromCarrier")
        ReceivedFromCarrierMsg.body = (CarrierDeliveryItems(content)).toJSON()
        return ReceivedFromCarrierMsg

    def getDeliveryItems(self, msg) -> CarrierDeliveryItems:
        msgBody = json.loads(msg.body)
        return CarrierDeliveryItems(
            content=msgBody['content']
        )

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
        await self.send(
            self._parent.generateInventoryReport(to=self._parent.availabilityManJiD, order=self._parent.content))
        print("inventory sent!")


class GiveDelivery(CyclicBehaviour):
    def __init__(self, parent: Shop):
        super().__init__()
        self._parent = parent

    async def run(self):
        msg = await self.receive(timeout=1)
        if msg:
            print("Shop is giving delivery to " + str(msg.sender))
            carrierDelivery = self._parent.getDeliveryItems(msg)
            deliveryToGive = {}
            for product_to_give in carrierDelivery.content:
                quantity_to_give = carrierDelivery.content[product_to_give]
                quantity_available = self._parent.content[product_to_give]
                if product_to_give in self._parent.content:
                    if quantity_available >= quantity_to_give:
                        self._parent.content[product_to_give] -= quantity_to_give
                        deliveryToGive[product_to_give] = quantity_to_give
                    else:
                        deliveryToGive[product_to_give] = quantity_available
                        self._parent.content[product_to_give] = 0
            # send delivery
            await self.send(self._parent.generateOrderForCarrier(to=msg.sender, content=deliveryToGive))
            # send inventory
            print("Shop: Sending inventory")
            await self.send(self._parent.generateInventoryReport(to=self._parent.availabilityManJiD,
                                                                 order=self._parent.content))
            print("Shop: inventory sent!")


class RecvDelivery(CyclicBehaviour):
    def __init__(self, parent: Shop):
        super().__init__()
        self._parent = parent

    async def run(self):
        # monitor if there is delivery to pick
        msg = await self.receive(timeout=1)
        if msg:
            print("Shop received delivery from " + str(msg.sender))
            carrierDelivery = self._parent.getDeliveryItems(msg)
            for product_delivered in carrierDelivery.content:
                qty_delivered = carrierDelivery.content[product_delivered]
                if qty_delivered > 0:
                    if product_delivered in self._parent.content:
                        self._parent.content[product_delivered] += qty_delivered
                    else:
                        self._parent.content[product_delivered] = qty_delivered
            print("Shop: Sending confirmation of delivery to carrier")
            await self.send(self._parent.generateDeliveryReceiveConfirm(to=self._parent.msg.sender, content=carrierDelivery.content))
            # check if delivery can close any order
            for client in self._parent.clients_orders:
                product_to_pop_from_order = []
                for product_in_order in self._parent.clients_orders[client]:
                    if product_in_order in self._parent.content and self._parent.content[product_in_order] > 0:
                        qty_avail=self._parent.content[product_in_order]
                        qty_in_order=self._parent.clients_orders[client][product_in_order]
                        if qty_avail >= qty_in_order:
                            # delete this part of order
                            product_to_pop_from_order.append(product_in_order)
                            self._parent.content[product_in_order] = qty_avail - qty_in_order
                        else:
                            self._parent.clients_orders[client][product_in_order][product_in_order] =qty_in_order - qty_avail
                            self._parent.content[product_in_order] = 0
                for product_to_pop in product_to_pop_from_order:
                    del self._parent.clients_orders[client][product_to_pop]
            # close orders and send info to customer
            client_to_pop_list = []
            for client in self._parent.clients_orders:
                if not self._parent.clients_orders[client]:
                    print("Shop: Client's  order is ready to pick up")
                    await self.send(self._parent.generateOrderReadToPickInfo(to=client))
                    client_to_pop_list.append(client)
            for client_to_pop in client_to_pop_list:
                del self._parent.clients_orders[client_to_pop]

            print("Shop: Sending inventory")
            await self.send(self._parent.generateInventoryReport(to=self._parent.availabilityManJiD,
                                                                 order=self._parent.content))
            print("Shop: inventory sent!")


class RecvOrderRequest(CyclicBehaviour):
    def __init__(self, parent: Shop):
        super().__init__()
        self._parent = parent

    async def run(self):
        # print("Shop: Waiting for order Request from client")
        msg = await self.receive(timeout=1)
        if msg:
            change = 0
            print("Shop: Received order from client" + str(msg.sender))
            clientOrderRequest = self._parent.getClientOrderRequest(msg)
            print(clientOrderRequest.order)
            missing_products = {}
            # Check whether shop has all the products
            for product in clientOrderRequest.order:
                if product in self._parent.content:
                    if self._parent.content[product] < clientOrderRequest.order[product]:
                        if self._parent.content[product] != 0:
                            change = 1
                        # jezeli czesc jest na stocku
                        missing_products[product] = clientOrderRequest.order[product] - self._parent.content[product]
                        self._parent.content[product]=0
                    else:
                        self._parent.content[product] = self._parent.content[product] - clientOrderRequest.order[
                            product]
                else:
                    missing_products[product] = clientOrderRequest.order[product]
            # response to client
            if not missing_products:
                # all item already there
                print("Shop: Client's  order is ready to pick up")
                await self.send(self._parent.generateOrderReadToPickInfo(to=msg.sender))
                print("Shop: Sending inventory")
                await self.send(self._parent.generateInventoryReport(to=self._parent.availabilityManJiD,
                                                                     order=self._parent.content))
                print("Shop: inventory sent!")
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

