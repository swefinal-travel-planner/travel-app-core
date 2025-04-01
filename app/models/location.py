class Location:
    def __init__(self, id: int, type: str, properties: dict, geometry: dict):
        self.id = id
        self.type = type
        self.properties = str(properties)
        self.geometry = str(geometry)

    def to_dict(self):

        return {
            "id": self.id,
            "type": self.type,
            "properties": self.properties,
            "geometry": self.geometry
        }
