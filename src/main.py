from agents.carrier import CarrierAgent
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

carrier = CarrierAgent("carrier@localhost", "tigase", load_capacity=50, availability=True)
y = carrier.start()
y.result()

future = dummy.start()

content = {"orange":2}
shop=Shop("student2@01337.io", "student2",content, availabilityManJiD="student4@01337.io",orderManJiD="student4@01337.io")
shop_result = shop.start()
shop_result.result()

order = {"orange":3}
client = Client("student1@01337.io", "student1",order, shop_name="student2@01337.io" )
client_result = client.start()
client_result.result()

time.sleep(10)
while warehouse.is_alive() or carrier.is_alive() or shop.is_alive() or client.is_alive():
    try:
         time.sleep(1)
    except KeyboardInterrupt:
        warehouse.stop()
        carrier.stop()
        dummy.stop()
        shop.stop()
        client.stop()
        break
quit_spade()

