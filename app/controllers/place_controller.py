from app.services.place_service import PlaceService
from injector import inject

class PlaceController:
    @inject
    def __init__(self, place_service: PlaceService):
        self.place_service = place_service

    def get_places(self):
        return "hello"