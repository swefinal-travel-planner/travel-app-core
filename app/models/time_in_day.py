from enum import Enum

class TimeInDay(Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"

    def to_string(self):
        return self.value
    
    @staticmethod
    def from_string(value):
        if value == "morning":
            return TimeInDay.MORNING
        elif value == "afternoon":
            return TimeInDay.AFTERNOON
        elif value == "evening":
            return TimeInDay.EVENING
        else:
            raise ValueError(f"Invalid time in day: {value}")