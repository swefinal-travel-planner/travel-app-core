from pydantic import BaseModel

class PlaceWithScoreCollapse(BaseModel):
    id: str
    score: float

class PlaceWithScoreCollapseList(BaseModel):
    places: list[PlaceWithScoreCollapse]