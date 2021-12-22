from agents.dummy import DummyAgent
from spade import quit_spade

dummy = DummyAgent("your_jid@your_xmpp_server", "your_password")
future = dummy.start()
future.result()

dummy.stop()
quit_spade()