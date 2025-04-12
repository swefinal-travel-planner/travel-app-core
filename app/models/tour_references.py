from pydantic import BaseModel
from .user_references_request import UserReferencesRequest

class TourReferences(BaseModel):
    address: str
    days: int
    budget: float
    slots: int
    location_attributes: list[str]
    food_attributes: list[str]
    special_requirements: list[str]
    medical_conditions: list[str]
    vi_location_attributes_label: list[str]
    en_location_attributes_label: list[str]
    vi_food_attributes_label: list[str]
    en_food_attributes_label: list[str]
    def to_dict(self):
        return {
            "address": self.address,
            "days": self.days,
            "budget": self.budget,
            "slots": self.slots,
            "location_attributes": self.location_attributes,
            "food_attributes": self.food_attributes,
            "special_requirements": self.special_requirements,
            "medical_conditions": self.medical_conditions,
            "vi_location_attributes_label": self.vi_location_attributes_label,
            "en_location_attributes_label": self.en_location_attributes_label,
            "vi_food_attributes_label": self.vi_food_attributes_label,
            "en_food_attributes_label": self.en_food_attributes_label
        }
