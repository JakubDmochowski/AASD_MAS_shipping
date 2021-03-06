from spade import agent
from spade.behaviour import OneShotBehaviour,CyclicBehaviour
from spade.message import Message
from messages.clientOrderRequest import clientOrderRequest
from spade.template import Template

class ClientAgent(agent.Agent):
	def __init__(self, jid: str, password: str,  order, shop_name):
		super().__init__(jid, password, verify_security=False)
		self.order = order
		self.shop_name = shop_name

	async def setup(self):
		print("ClientAgent started: {}".format(str(self.jid)))
		orderRequest = Template()
		self.add_behaviour(SendOrderRequest(self), orderRequest)

		orderReadyToPickTemplate = Template()
		orderReadyToPickTemplate.set_metadata("performative", "inform")
		orderReadyToPickTemplate.set_metadata("protocol", "orderReadyToPick")
		self.add_behaviour(OrderReadyToPickInfo(self), orderReadyToPickTemplate)

	def generateOrderRequest(self, to, order) -> Message:
		OrderRequestMsg = Message(to=str(to), sender=str(self.jid))
		OrderRequestMsg.set_metadata("performative", "request")
		OrderRequestMsg.set_metadata("protocol", "orderRequest")
		OrderRequestMsg.body = (clientOrderRequest(order)).toJSON()
		return OrderRequestMsg

class SendOrderRequest(OneShotBehaviour):
	def __init__(self, parent: ClientAgent):
		super().__init__()
		self._parent = parent
	async def run(self):
		print("Client: Sending order to shop:"+str(self._parent.shop_name))
		await self.send(self._parent.generateOrderRequest(to=self._parent.shop_name,order=self._parent.order))
		print("Client: Order sent!")

class OrderReadyToPickInfo(CyclicBehaviour):
	def __init__(self, parent: ClientAgent):
		super().__init__()
		self._parent = parent
	async def run(self):
		msg = await self.receive()
		if msg:
			print("Client: I picked up my order")
			await self._parent.stop()
