from enum import Enum

class LocationPreference(Enum):
    PROXIMITY = ["proximity",0.0002]
    RELEVANCE = ["relevance",0.00001]
    BALANCED = ["balanced",0.00007]

    def to_string(self):
        return self.value[0]
    
    def to_float(self):
        return self.value[1]
    
    def from_string(value):
        if value == "proximity":
            return LocationPreference.PROXIMITY
        elif value == "relevance":
            return LocationPreference.RELEVANCE
        elif value == "balanced":
            return LocationPreference.BALANCED
        else:
            raise ValueError(f"Invalid location preference: {value}")