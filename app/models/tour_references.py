from pydantic import BaseModel

class TourReferences(BaseModel):
    city: str
    days: int
    locationsPerDay: int
    location_attributes: list[str]
    food_attributes: list[str]
    special_requirements: list[str]
    medical_conditions: list[str]
    vi_location_attributes_label: list[str]
    en_location_attributes_label: list[str]
    vi_food_attributes_label: list[str]
    en_food_attributes_label: list[str]
    locationPreference: str
    def to_dict(self):
        return {
            "city": self.city,
            "days": self.days,
            "locationsPerDay": self.locationsPerDay,
            "location_attributes": self.location_attributes,
            "food_attributes": self.food_attributes,
            "special_requirements": self.special_requirements,
            "medical_conditions": self.medical_conditions,
            "vi_location_attributes_label": self.vi_location_attributes_label,
            "en_location_attributes_label": self.en_location_attributes_label,
            "vi_food_attributes_label": self.vi_food_attributes_label,
            "en_food_attributes_label": self.en_food_attributes_label,
            "locationPreference": self.locationPreference
        }
    
    def attributes_to_dict(self):
        return {
            "location_attributes": self.location_attributes,
            "food_attributes": self.food_attributes,
            "vi_location_attributes_label": self.vi_location_attributes_label,
            "en_location_attributes_label": self.en_location_attributes_label,
            "vi_food_attributes_label": self.vi_food_attributes_label,
            "en_food_attributes_label": self.en_food_attributes_label
        }
    
    def attriutes_with_special_and_medical_conditions(self):
        return {
            "special_requirements": self.special_requirements,
            "medical_conditions": self.medical_conditions,
            "location_attributes": self.location_attributes,
            "food_attributes": self.food_attributes,
            "vi_location_attributes_label": self.vi_location_attributes_label,
            "en_location_attributes_label": self.en_location_attributes_label,
            "vi_food_attributes_label": self.vi_food_attributes_label,
            "en_food_attributes_label": self.en_food_attributes_label
        }
    
    def from_dict(data):
        return TourReferences(
            city=data["city"],
            days=data["days"],
            locationsPerDay=data["locationsPerDay"],
            location_attributes=data["location_attributes"],
            food_attributes=data["food_attributes"],
            special_requirements=data["special_requirements"],
            medical_conditions=data["medical_conditions"],
            vi_location_attributes_label=data["vi_location_attributes_label"],
            en_location_attributes_label=data["en_location_attributes_label"],
            vi_food_attributes_label=data["vi_food_attributes_label"],
            en_food_attributes_label=data["en_food_attributes_label"],
            locationPreference=data["locationPreference"]
        )
