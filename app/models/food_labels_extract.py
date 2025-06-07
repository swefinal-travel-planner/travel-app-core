from pydantic import BaseModel

class FoodLabelsExtract(BaseModel):
    vi_food_attributes_label: list[str]
    en_food_attributes_label: list[str] 