import json

class DistanceEntry:
    def __init__(self, source_id: str, destination_id: str, distance: float):
        self.source_id = source_id
        self.destination_id = destination_id
        self.distance = distance

    def to_dict(self):
        return {
            "source_id": self.source_id,
            "destination_id": self.destination_id,
            "distance": self.distance
        }

    @staticmethod
    def from_dict(data):
        return DistanceEntry(
            source_id=data["source_id"],
            destination_id=data["destination_id"],
            distance=data["distance"]
        )
