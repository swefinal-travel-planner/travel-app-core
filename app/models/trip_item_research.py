class TripItemResearch:
    def __init__(self, place_id, score, is_selected):
        self.place_id = place_id
        self.score = score
        self.is_selected = is_selected

    def to_dict(self):
        return {
            "place_id": self.place_id,
            "score": self.score,
            "is_selected": self.is_selected
        }
    
class TripItemResearchList:
    def __init__(self, trip_items=None):
        self.trip_items = trip_items if trip_items is not None else []

    def add(self, item: TripItemResearch):
        self.trip_items.append(item)

    def get_by_id(self, place_id: str) -> TripItemResearch:
        for item in self.trip_items:
            if item.place_id == place_id:
                return item
        return None
    
    def set_is_selected(self, place_id):
        item = self.get_by_id(place_id)
        if item:
            item.is_selected = True
            return True
        else:
            return False

    def to_dict(self):
        return {
            "trip_items": [item.to_dict() for item in self.trip_items]
        }