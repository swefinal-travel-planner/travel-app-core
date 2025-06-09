class PlaceResponse:
    def __init__(self, id: str, name: str, long: float, lat: float, properties: list[str], type: str):
        self.id = id
        self.name = name
        self.long = long
        self.lat = lat
        self.properties = properties
        self.type = type

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": {"lat": self.lat, "long": self.long},
            "properties": self.properties,
            "type": self.type
        }
