from pydantic import BaseModel

class LocationLabelsExtract(BaseModel):
    vi_location_attributes_label: list[str]
    en_location_attributes_label: list[str]