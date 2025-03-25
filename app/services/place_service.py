from app.repositories.place_repository import PlaceRepository
from injector import inject

class PlaceService:
    @inject
    def __init__(self, place_repository: PlaceRepository):
        self.place_repository = place_repository