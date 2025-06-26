from dataclasses import dataclass
from typing import Optional

@dataclass
class PlaceWithScore:
    id: str
    en_name: str
    vi_name: str
    en_address: str
    vi_address: str
    long: float
    lat: float
    en_type: str
    vi_type: str
    en_properties: list[str]
    vi_properties: list[str]
    images: list[str]
    score: Optional[float] = None

    def to_dict(self):
        return {
            "id": self.id,
            "en_name": self.en_name,
            "vi_name": self.vi_name,
            "en_address": self.en_address,
            "vi_address": self.vi_address,
            "long": self.long,
            "lat": self.lat,
            "en_type": self.en_type,
            "vi_type": self.vi_type,
            "en_properties": self.en_properties,
            "vi_properties": self.vi_properties,
            "images": self.images
        }
    
    def to_dict_with_score(self):
        return {
            "id": self.id,
            "en_name": self.en_name,
            "vi_name": self.vi_name,
            "en_type": self.en_type,
            "vi_type": self.vi_type,
            "en_properties": self.en_properties,
            "vi_properties": self.vi_properties,
            "score": self.score
        }