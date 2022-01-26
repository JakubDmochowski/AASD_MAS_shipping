import jsonpickle

class JsonSerializable:
	def toJSON(self) -> str:
		return jsonpickle.encode(self)
	
	def fromJSON(self, j):
		self = jsonpickle.decode(j)