from pydantic import BaseModel

class Place(BaseModel):
    id: str
    en_name: str
    vi_name: str
    long: float
    lat: float
    en_type: str
    vi_type: str
    en_properties: list[str]
    vi_properties: list[str]
    price: float

    def to_dict(self):
        return {
            "id": self.id,
            "en_name": self.en_name,
            "vi_name": self.vi_name,
            "long": self.long,
            "lat": self.lat,
            "en_type": self.en_type,
            "vi_type": self.vi_type,
            "en_properties": self.en_properties,
            "vi_properties": self.vi_properties,
            "price": self.price
        }

        
class Place_list(BaseModel):
    places: list[Place]