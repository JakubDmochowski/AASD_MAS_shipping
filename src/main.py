from agents.dummy import DummyAgent
from spade import quit_spade
import time
from agents.warehouse import WarehouseAgent
from agents.Client import Client
from agents.Shop import Shop

dummy = DummyAgent("ss@localhost", "aa")
warehouse = WarehouseAgent("receiver@localhost", "bb", capacity=15)
x = warehouse.start()
x.result()
future = dummy.start()

content = {"orange":2}
shop=Shop("student2@01337.io", "student2",content, "student3@01337.io")
shop_result = shop.start()
shop_result.result()

order = {"orange":1}
client = Client("student1@01337.io", "student1",order, "student2@01337.io" )
client_result = client.start()
client_result.result()

time.sleep(10)
quit_spade()

