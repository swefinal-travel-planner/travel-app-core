class UserReferencesRequest:
    def __init__(self,trip_id, address, days, location_attributes, food_attributes, special_requirements, medical_conditions):
        self.trip_id = trip_id
        self.address = address
        self.days = days
        self.location_attributes = location_attributes
        self.food_attributes = food_attributes
        self.special_requirements = special_requirements
        self.medical_conditions = medical_conditions

    def to_dict(self):
        return {
            "trip_id": self.trip_id,
            "address": self.address,
            "days": self.days,
            "location_attributes": self.location_attributes,
            "food_attributes": self.food_attributes,
            "special_requirements": self.special_requirements,
            "medical_conditions": self.medical_conditions
        }
