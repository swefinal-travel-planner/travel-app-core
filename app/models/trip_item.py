from app.models.place_with_score import PlaceWithScore
class TripItem:
    def __init__(self, place_id, trip_day, order_in_day, time_in_day):
        self.place_id = place_id
        self.trip_day = trip_day
        self.order_in_day = order_in_day
        self.time_in_day = time_in_day
        
    def to_dict(self):
        return {
            "place_id": self.place_id,
            "trip_day": self.trip_day,
            "order_in_day": self.order_in_day,
            "time_in_day": self.time_in_day
        }
    
class TripItemWithPlace:
    def __init__(self, place: PlaceWithScore, tripItem: TripItem):
        self.place = place
        self.trip_day = tripItem.trip_day
        self.order_in_day = tripItem.order_in_day
        self.time_in_day = tripItem.time_in_day

    def to_dict(self):
        return {
            "place": self.place.to_dict(),
            "trip_day": self.trip_day,
            "order_in_day": self.order_in_day,
            "time_in_day": self.time_in_day
        }