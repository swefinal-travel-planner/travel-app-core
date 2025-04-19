class Location:
    def __init__(self, id: str, type: str, properties: dict, geometry: dict):
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

    def to_str(self):
        return f"Location(id={self.id}, type={self.type}, properties={self.properties}, geometry={self.geometry})\n"