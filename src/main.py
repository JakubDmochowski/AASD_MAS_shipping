from agents.dummy import DummyAgent
from spade import quit_spade
import time
from agents.warehouse import WarehouseAgent

dummy = DummyAgent("ss@localhost", "aa")
warehouse = WarehouseAgent("receiver@localhost", "bb", capacity=15)
x = warehouse.start()
x.result()
future = dummy.start()

time.sleep(10)
quit_spade()

