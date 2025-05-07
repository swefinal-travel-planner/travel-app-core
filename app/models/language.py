from enum import Enum

class Language(Enum):
    VI = "vi"
    EN = "en"

    def to_string(self):
        return self.value