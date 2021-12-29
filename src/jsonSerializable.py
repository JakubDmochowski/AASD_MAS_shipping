import json

class JsonSerializable:
	def toJSON(self) -> str:
		return json.dumps(self, default=lambda o: o.__dict__, 
		sort_keys=True, indent=4)