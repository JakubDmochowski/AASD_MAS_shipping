from agents.dummy import DummyAgent
from spade import quit_spade

dummy = DummyAgent("ss@localhost", "aa")
future = dummy.start()
future.result()

dummy.stop()
quit_spade()

