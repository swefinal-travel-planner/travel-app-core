from pydantic import BaseModel

class Place(BaseModel):
    id: int
    name: str
    long: float
    lat: float
    type: str
    properties: list[str]
    price: float

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "long": self.long,
            "lat": self.lat,
            "type": self.type,
            "properties": self.properties,
            "price": self.price
        }

        
class Place_list(BaseModel):
    places: list[Place]