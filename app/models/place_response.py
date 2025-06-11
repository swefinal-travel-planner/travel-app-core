class PlaceResponse:
    def __init__(self, id: str, name: str, address: str, long: float, lat: float, properties: list[str], type: str, images: list[str]):
        self.id = id
        self.name = name
        self.address = address
        self.long = long
        self.lat = lat
        self.properties = properties
        self.type = type
        self.images = images

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "location": {"lat": self.lat, "long": self.long},
            "properties": self.properties,
            "type": self.type,
            "images": self.images
        }
