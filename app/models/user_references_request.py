class UserReferencesRequest:
    def __init__(self, address, days, budget, slots, location_attributes, food_attributes, special_requirements, medical_conditions):
        self.address = address
        self.days = days
        self.budget = budget
        self.slots = slots
        self.location_attributes = location_attributes
        self.food_attributes = food_attributes
        self.special_requirements = special_requirements
        self.medical_conditions = medical_conditions

    def to_dict(self):
        return {
            "address": self.address,
            "days": self.days,
            "budget": self.budget,
            "slots": self.slots,
            "location_attributes": self.location_attributes,
            "food_attributes": self.food_attributes,
            "special_requirements": self.special_requirements,
            "medical_conditions": self.medical_conditions
        }
