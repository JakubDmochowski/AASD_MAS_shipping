from jsonSerializable import JsonSerializable

from aioxmpp.xso.types import Integer

class CarrierDetailsReport(JsonSerializable):
	def __init__(self, load_capacity: Integer, availability: bool) -> None:
		self.load_capacity = load_capacity
		self.availability = availability