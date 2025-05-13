class UserReferencesRequest:
    def __init__(self, city, days, locationsPerDay, location_attributes, food_attributes, special_requirements, medical_conditions, locationPreference):
        self.city = city
        self.days = days
        self.locationsPerDay = locationsPerDay
        self.location_attributes = location_attributes
        self.food_attributes = food_attributes
        self.special_requirements = special_requirements
        self.medical_conditions = medical_conditions
        self.locationPreference = locationPreference

    def to_dict(self):
        return {
            "city": self.city,
            "days": self.days,
            "locationsPerDay": self.locationsPerDay,
            "location_attributes": self.location_attributes,
            "food_attributes": self.food_attributes,
            "special_requirements": self.special_requirements,
            "medical_conditions": self.medical_conditions,
            "locationPreference": self.locationPreference
        }
