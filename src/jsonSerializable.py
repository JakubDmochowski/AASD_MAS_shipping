import jsonpickle


class JsonSerializable:
    def toJSON(self) -> str:
        return jsonpickle.encode(self)

    def fromJSON(self, j):
        self.__dict__ = (jsonpickle.decode(j)).__dict__