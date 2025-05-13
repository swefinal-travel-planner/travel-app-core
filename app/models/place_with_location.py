from dataclasses import dataclass

@dataclass
class PlaceWithLocation:
    id: str
    long: float
    lat: float
    score: float